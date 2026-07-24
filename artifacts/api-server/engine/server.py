"""HTTP layer for the ActiveGraph game engine sidecar.

Internal service: bound to localhost only, reached exclusively by the
Express API server. No public proxy path is registered for it.
"""
from __future__ import annotations

import os
import sys
import threading

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from typing import Any, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from engine import Engine
from llm_runner import replay_llm, run_llm
from llm_subject import load_registry
from phase4 import (
    ArmStore,
    BudgetLedger,
    PHASE4_PROTOCOL,
    RESOLUTION_KEYS,
    self_check,
    validate_run_request,
)
from phase4_runner import dry_run_p4, replay_llm_p4, run_llm_p4, write_resolution
from strategies import STRATEGIES

DB_PATH = os.environ.get(
    "ENGINE_DB_PATH",
    os.path.join(os.path.dirname(__file__), "data", "engine.db"),
)
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

app = FastAPI(title="ActiveGraph Game Engine", version="1.0.0")
engine = Engine(DB_PATH)
# Runs mutate a shared SQLite store; serialize engine operations.
_lock = threading.Lock()


# ── Phase 4 bootstrap (freeze packet §F.3) ──────────────────────────────────
# The startup self-check recomputes every template sha named by the sealed
# arms manifest with the Python canonical serializer and compares against the
# Node-computed values. Any mismatch DISABLES Phase 4 endpoints (503) while
# leaving sealed Phase 3 endpoints untouched.

def _p4_bootstrap() -> dict[str, Any]:
    try:
        registry, _sha = load_registry()
        store = ArmStore()
        ledger = BudgetLedger()
        check = self_check(registry, store)
        return {"store": store, "ledger": ledger, "check": check}
    except Exception as e:  # disclosed via /phase4/status, never silent
        return {
            "store": None, "ledger": None,
            "check": {"ok": False, "templatesChecked": 0,
                      "mismatches": [f"bootstrap failure: {type(e).__name__}: {e}"]},
        }


P4 = _p4_bootstrap()
print(
    f"[phase4] startup self-check ok={P4['check']['ok']} "
    f"templatesChecked={P4['check'].get('templatesChecked', 0)} "
    f"mismatches={len(P4['check'].get('mismatches', []))}",
    flush=True,
)


def _p4_ready() -> None:
    if P4["store"] is None or not P4["check"]["ok"]:
        raise HTTPException(status_code=503, detail={
            "error": "Phase 4 endpoints disabled: startup self-check failed",
            "selfCheck": P4["check"],
        })


class GameDefModel(BaseModel):
    slug: str
    numActions: int = Field(ge=2)
    actionLabels: list[str]
    payoffMatrix: list[list[list[float]]]
    nashEquilibria: list[list[int]]


class ScriptedMove(BaseModel):
    """One externally decided move for a 'scripted' seat (LLM event-sourcing)."""

    action: int = Field(ge=0)
    reasoning: Optional[str] = None


class RunRequest(BaseModel):
    game: GameDefModel
    strategy1Slug: str
    strategy2Slug: str
    numRounds: int = Field(ge=1, le=10000)
    seed: int = Field(ge=0, le=0xFFFFFFFF)
    scripted1: Optional[list[ScriptedMove]] = None
    scripted2: Optional[list[ScriptedMove]] = None


class ForkRequest(BaseModel):
    forkRound: int = Field(ge=1)
    strategy1Slug: Optional[str] = None
    strategy2Slug: Optional[str] = None
    scripted1: Optional[list[ScriptedMove]] = None
    scripted2: Optional[list[ScriptedMove]] = None


class LlmConfigModel(BaseModel):
    """Subject-protocol parameters, stored verbatim on the run for provenance."""

    model: str
    temperature: float = Field(ge=0.0, le=2.0)
    maxTokens: int = Field(default=16, ge=1, le=64)
    promptId: str
    framing: Optional[str] = None
    deltaPct: Optional[float] = Field(default=None, ge=0, le=100)
    horizonRule: Optional[str] = None


class LlmRunRequest(BaseModel):
    game: GameDefModel
    strategy1Slug: str
    strategy2Slug: str
    numRounds: int = Field(ge=1, le=200)
    seed: int = Field(ge=0, le=0xFFFFFFFF)
    llm: LlmConfigModel


def _moves(items: Optional[list[ScriptedMove]]) -> Optional[list[dict]]:
    return [m.model_dump() for m in items] if items is not None else None


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


def _guard(fn, *args, **kwargs) -> Any:
    with _lock:
        try:
            return fn(*args, **kwargs)
        except KeyError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except RuntimeError as e:
            # Structured mid-run failures (e.g. partial LLM spend payloads)
            # must reach the caller as JSON detail, not an opaque 500.
            raise HTTPException(status_code=500, detail=str(e))


@app.post("/runs")
def create_run(body: RunRequest) -> dict[str, Any]:
    return _guard(
        engine.run,
        game_def=body.game.model_dump(),
        strategy1_slug=body.strategy1Slug,
        strategy2_slug=body.strategy2Slug,
        num_rounds=body.numRounds,
        seed=body.seed,
        scripted1=_moves(body.scripted1),
        scripted2=_moves(body.scripted2),
    )


@app.post("/runs/{run_id}/fork")
def fork_run(run_id: str, body: ForkRequest) -> dict[str, Any]:
    return _guard(
        engine.fork,
        parent_run_id=run_id,
        fork_round=body.forkRound,
        strategy1_slug=body.strategy1Slug,
        strategy2_slug=body.strategy2Slug,
        scripted1=_moves(body.scripted1),
        scripted2=_moves(body.scripted2),
    )


@app.get("/runs/{run_id}/trace")
def get_trace(run_id: str) -> dict[str, Any]:
    return _guard(engine.trace, run_id)


@app.get("/runs/{parent_run_id}/diff/{fork_run_id}")
def get_diff(parent_run_id: str, fork_run_id: str) -> dict[str, Any]:
    return _guard(engine.diff, parent_run_id, fork_run_id)


@app.get("/llm-registry")
def llm_registry() -> dict[str, Any]:
    """Current prompt registry identity — runners assert this before batches."""
    reg, sha = load_registry()
    return {
        "registryVersion": reg.get("registryVersion"),
        "sha256": sha,
        "promptIds": sorted(reg["prompts"].keys()),
    }


@app.post("/llm-runs")
def create_llm_run(body: LlmRunRequest) -> dict[str, Any]:
    """Live LLM behavioral run. Holds the engine lock for the whole run —
    Phase 3 runs are executed sequentially by design (budget enforcement)."""
    return _guard(
        run_llm,
        engine,
        game_def=body.game.model_dump(),
        strategy1_slug=body.strategy1Slug,
        strategy2_slug=body.strategy2Slug,
        num_rounds=body.numRounds,
        seed=body.seed,
        llm=body.llm.model_dump(exclude_none=True),
    )


@app.post("/llm-runs/{run_id}/replay")
def replay_llm_run(run_id: str) -> dict[str, Any]:
    """Pure replay verification: zero live calls, structural."""
    return _guard(replay_llm, engine, run_id)


# ── Phase 4 endpoints (§F.3: enforcement, capture, replay) ──────────────────


class P4RunRequest(BaseModel):
    armId: str
    game: GameDefModel
    strategy1Slug: str
    strategy2Slug: str
    numRounds: int = Field(ge=1, le=200)
    seed: int = Field(ge=0, le=0xFFFFFFFF)
    model: str
    # Protocol constants: clients state them explicitly, the server verifies
    # against the frozen pins (defaults are the pins for convenience).
    temperature: float = PHASE4_PROTOCOL["temperature"]
    maxTokens: int = PHASE4_PROTOCOL["maxTokens"]
    episodeIndex: Optional[int] = Field(default=None, ge=1)
    sentinelCheckIndex: Optional[int] = Field(default=None, ge=0)
    dryRun: bool = False


class P4ResolutionRequest(BaseModel):
    key: str
    templateId: str
    note: str = ""


@app.get("/phase4/status")
def phase4_status() -> dict[str, Any]:
    reg, sha = load_registry()
    out: dict[str, Any] = {
        "selfCheck": P4["check"],
        "registryVersion": reg.get("registryVersion"),
        "registrySha256": sha,
        "sealed": not str(reg.get("registryVersion", "")).endswith("-proposed"),
        "protocol": PHASE4_PROTOCOL,
    }
    if P4["ledger"] is not None:
        out["budget"] = P4["ledger"].totals()
        out["resolutions"] = {k: P4["ledger"].get_resolution(k) for k in RESOLUTION_KEYS}
    if P4["store"] is not None:
        out["armsManifestSha256"] = P4["store"].manifest_sha
        out["arms"] = len(P4["store"].arms)
    return out


@app.post("/phase4/llm-runs")
def create_phase4_run(body: P4RunRequest) -> dict[str, Any]:
    """Phase 4 run against a sealed arm. Everything is enforcement-first:
    the arm pins template, seeds, model, protocol, and game definition; the
    request must match or is refused. Live runs additionally require the
    registry to be sealed (step 3); dryRun renders + hashes with zero events,
    zero spend, zero provider calls."""
    _p4_ready()
    reg, _sha = load_registry()
    version = str(reg.get("registryVersion", ""))
    if version.endswith("-proposed") and not body.dryRun:
        raise HTTPException(
            status_code=403,
            detail=(
                f"registry {version} is not sealed; live Phase 4 runs are refused "
                "until the step-3 sealing record exists (dryRun is allowed)"
            ),
        )

    def _do() -> dict[str, Any]:
        arm = P4["store"].get(body.armId)
        pinned = validate_run_request(
            arm=arm, registry=reg, store=P4["store"], ledger=P4["ledger"],
            game_def=body.game.model_dump(),
            strategy1_slug=body.strategy1Slug, strategy2_slug=body.strategy2Slug,
            num_rounds=body.numRounds, seed=body.seed, model=body.model,
            temperature=body.temperature, max_tokens=body.maxTokens,
            episode_index=body.episodeIndex,
            sentinel_check_index=body.sentinelCheckIndex,
            known_strategies=set(STRATEGIES),
        )
        if body.dryRun:
            return dry_run_p4(
                arm=arm, pinned=pinned, game_def=body.game.model_dump(),
                num_rounds=body.numRounds, seed=body.seed, model=body.model,
                store=P4["store"],
            )
        return run_llm_p4(
            engine, arm=arm, pinned=pinned, game_def=body.game.model_dump(),
            strategy1_slug=body.strategy1Slug, strategy2_slug=body.strategy2Slug,
            num_rounds=body.numRounds, seed=body.seed, model=body.model,
            episode_index=body.episodeIndex,
            sentinel_check_index=body.sentinelCheckIndex,
            store=P4["store"], ledger=P4["ledger"],
        )

    return _guard(_do)


@app.post("/phase4/llm-runs/{run_id}/replay")
def replay_phase4_run(run_id: str) -> dict[str, Any]:
    """Extended §F.3 replay: bundle-sha byte-compare, request-body-sha
    recompute, parsed-action re-derivation. Zero live calls, structurally."""
    _p4_ready()
    return _guard(replay_llm_p4, engine, run_id, store=P4["store"])


@app.post("/phase4/resolutions")
def create_phase4_resolution(body: P4ResolutionRequest) -> dict[str, Any]:
    """Write-once resolution of a RESOLVED-BY-* placeholder (event-sourced
    first, then the enforcement record). Re-resolution is refused — changing
    a written resolution is an amendment, not an update."""
    _p4_ready()
    return _guard(
        write_resolution, engine,
        key=body.key, template_id=body.templateId, note=body.note,
        ledger=P4["ledger"], store=P4["store"],
    )


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("ENGINE_PORT") or os.environ.get("PORT") or "8090")
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")
