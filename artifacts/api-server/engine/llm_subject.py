"""Phase 3 LLM-subject layer: prompt registry, rendering, parsing, provider.

The registry (prompts/registry.json) is the versioned, SHA-256-hashed source
of every behavioral prompt. Prompts are assembled here as plain
`AssembledPrompt` values (NOT via @llm_behavior — the framework's assembled
system prompt would leak non-registry text into the subject's context).

Determinism contract:
- rendering is a pure function of (registry, promptId, seat, round, history,
  game payoffs, protocol params, retry text);
- the parser is exact-match after strip+uppercase, no fuzzy repair;
- the seat tag in the system prompt makes every (seat, round, attempt)
  prompt hash unique within a run, so LLMCache replay lookups can never
  cross-contaminate between the two seats of a self-play run.
"""
from __future__ import annotations

import hashlib
import json
import os
from typing import Any, Optional

from activegraph.llm.prompt import AssembledPrompt
from activegraph.llm.types import LLMMessage

REGISTRY_PATH = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "prompts", "registry.json")
)


class InvalidTrialError(Exception):
    """Subject reply unparseable after the single permitted retry."""

    def __init__(self, seat: int, round_number: int, raw_text: str):
        self.seat = seat
        self.round_number = round_number
        self.raw_text = raw_text
        super().__init__(
            f"invalid trial: seat {seat} round {round_number} reply unparseable after retry"
        )


def load_registry() -> tuple[dict[str, Any], str]:
    """Load the prompt registry and its SHA-256 (over exact file bytes)."""
    with open(REGISTRY_PATH, "rb") as f:
        raw = f.read()
    return json.loads(raw), hashlib.sha256(raw).hexdigest()


def _pts(x: float) -> Any:
    """Render 3.0 as 3 in prompt text (points are integers in all our games)."""
    return int(x) if float(x) == int(x) else x


def _pd_payoff_params(game_def: dict) -> dict[str, Any]:
    """Derive J/F payoff placeholders straight from the game matrix.

    Index 0 = J, index 1 = F. Reading from the matrix (not from protocol
    params) makes prompt/DB payoff drift structurally impossible.
    """
    m = game_def["payoffMatrix"]
    return {
        "rr": _pts(m[0][0][0]),  # both J
        "rs": _pts(m[0][1][0]),  # I J, other F (my points)
        "rt": _pts(m[1][0][0]),  # I F, other J (my points)
        "rp": _pts(m[1][1][0]),  # both F
    }


def _render_history(spec: dict, seat: int, history: list[dict], game_def: dict) -> str:
    if not history:
        return spec["firstRound"]
    lines = [spec["historyHeader"]]
    options = spec["options"]
    zero_sum = "outcomes" in spec
    for i, r in enumerate(history):
        mine = r["p1Action"] if seat == 1 else r["p2Action"]
        theirs = r["p2Action"] if seat == 1 else r["p1Action"]
        my_pay = r["p1Payoff"] if seat == 1 else r["p2Payoff"]
        their_pay = r["p2Payoff"] if seat == 1 else r["p1Payoff"]
        if zero_sum:
            outcome_key = "win" if my_pay > 0 else ("lose" if my_pay < 0 else "tie")
            lines.append(
                spec["historyLine"].format(
                    n=i + 1,
                    you=options[mine],
                    them=options[theirs],
                    outcome=spec["outcomes"][outcome_key],
                )
            )
        else:
            lines.append(
                spec["historyLine"].format(
                    n=i + 1,
                    you=options[mine],
                    them=options[theirs],
                    youPts=_pts(my_pay),
                    themPts=_pts(their_pay),
                )
            )
    return "\n".join(lines)


def render_prompt(
    registry: dict,
    prompt_id: str,
    *,
    seat: int,
    round_number: int,
    history: list[dict],
    game_def: dict,
    num_rounds: int,
    protocol: dict,
    retry_raw: Optional[str] = None,
) -> tuple[str, str]:
    """Render (system, user) text for one decision. Raises ValueError on any
    missing template/param so drift fails loudly instead of shipping a
    malformed prompt to the subject."""
    spec = registry["prompts"].get(prompt_id)
    if spec is None:
        raise ValueError(f"unknown promptId: {prompt_id}")

    system = spec["system"].format(seat=seat)
    kwargs: dict[str, Any] = {"round": round_number, "seat": seat}

    if prompt_id.startswith("pd-"):
        kwargs.update(_pd_payoff_params(game_def))
    if prompt_id.startswith("pd-repeated-"):
        delta_pct = protocol.get("deltaPct")
        if delta_pct is None:
            raise ValueError(f"{prompt_id} requires protocol.deltaPct")
        kwargs["deltaPct"] = _pts(delta_pct)
        kwargs["history"] = _render_history(spec, seat, history, game_def)
    elif prompt_id == "pd-oneshot-v1":
        framing = protocol.get("framing")
        framings = spec["framings"]
        if framing not in framings:
            raise ValueError(f"pd-oneshot-v1 requires framing in {sorted(framings)}")
        kwargs["framingLine"] = framings[framing]
    elif prompt_id.startswith("pd-os-"):
        # Phase 4 one-shot factorial family: payoff placeholders only (no
        # history, no horizon). Values come from the gameDef matrix, which the
        # enforcement layer has already verified against the arm's bindings.
        pass
    elif prompt_id.startswith("pd-rep-") or prompt_id.startswith("pd-x2-"):
        # Phase 4 repeated families (E candidates, community, X2 rungs):
        # same dynamic surface as the sealed pd-repeated-* templates.
        delta_pct = protocol.get("deltaPct")
        if delta_pct is None:
            raise ValueError(f"{prompt_id} requires protocol.deltaPct")
        kwargs["deltaPct"] = _pts(delta_pct)
        kwargs["history"] = _render_history(spec, seat, history, game_def)
    elif prompt_id == "rps-v1":
        kwargs["numRounds"] = num_rounds
        kwargs["history"] = _render_history(spec, seat, history, game_def)
    elif prompt_id == "rps-sym-v1":
        # D3 neutral-symbol RPS: optList/beatsLine are pinned per-arm
        # substitutions derived by the enforcement layer from roleMapping /
        # displayOrder (never client-supplied text).
        opt_list = protocol.get("optList")
        beats_line = protocol.get("beatsLine")
        if not opt_list or not beats_line:
            raise ValueError("rps-sym-v1 requires pinned optList and beatsLine substitutions")
        kwargs["optList"] = opt_list
        kwargs["beatsLine"] = beats_line
        kwargs["numRounds"] = num_rounds
        kwargs["history"] = _render_history(spec, seat, history, game_def)
    else:
        raise ValueError(f"promptId {prompt_id} has no renderer")

    try:
        user = spec["user"].format(**kwargs)
    except (KeyError, IndexError) as e:
        raise ValueError(f"template/param mismatch for {prompt_id}: {e}")

    if retry_raw is not None:
        # Suffixes may carry placeholders (e.g. rps-sym-v1's {optList});
        # formatting is identity for the sealed Phase 3 suffixes (no braces),
        # so recorded Phase 3 runs replay byte-identically.
        try:
            user = user + spec["retrySuffix"].format(**kwargs)
        except (KeyError, IndexError) as e:
            raise ValueError(f"retrySuffix/param mismatch for {prompt_id}: {e}")
    return system, user


# Parser identity, stamped on every Phase 4 call record (§F.3 field 9) and
# re-checked in replay. Bump on ANY change to parse_action semantics.
PARSER_VERSION = "strip-upper-exact-v1.p4.2026-07-24"


def parse_action(registry: dict, prompt_id: str, raw_text: str) -> Optional[int]:
    """Deterministic parser: strip whitespace, uppercase, exact match.
    Returns the action index or None (never guesses)."""
    spec = registry["prompts"][prompt_id]
    cleaned = (raw_text or "").strip().upper()
    options = [o.upper() for o in spec["options"]]
    if cleaned in options:
        return options.index(cleaned)
    return None


def build_prompt(
    system: str, user: str, *, model: str, temperature: float, max_tokens: int
) -> AssembledPrompt:
    return AssembledPrompt(
        system=system,
        messages=[LLMMessage(role="user", content=user)],
        model=model,
        max_tokens=int(max_tokens),
        temperature=float(temperature),
        top_p=1.0,
        output_schema_name=None,
        output_schema_json=None,
        deterministic=False,
        structured_output_mode="prompt",
    )


def make_provider():
    """OpenAI provider wired to the Replit AI Integrations proxy.

    Fails loudly if the env vars are missing — a silent fallback to the
    public API would bill the wrong account and break provenance.
    """
    from openai import OpenAI
    from activegraph.llm.openai import OpenAIProvider

    api_key = os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY")
    base_url = os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL")
    if not api_key or not base_url:
        raise RuntimeError(
            "AI_INTEGRATIONS_OPENAI_API_KEY / AI_INTEGRATIONS_OPENAI_BASE_URL not set"
        )
    client = OpenAI(api_key=api_key, base_url=base_url)
    return OpenAIProvider(client=client)
