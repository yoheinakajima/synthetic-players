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

DB_PATH = os.environ.get(
    "ENGINE_DB_PATH",
    os.path.join(os.path.dirname(__file__), "data", "engine.db"),
)
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

app = FastAPI(title="ActiveGraph Game Engine", version="1.0.0")
engine = Engine(DB_PATH)
# Runs mutate a shared SQLite store; serialize engine operations.
_lock = threading.Lock()


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


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("ENGINE_PORT") or os.environ.get("PORT") or "8090")
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")
