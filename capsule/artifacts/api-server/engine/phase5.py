"""Phase 5 enforcement layer — persona × temperature extension of Phase 4.

Sealed Phase 4 modules (phase4.py, phase4_runner.py, phase4_driver.py) are
byte-untouched; Phase 5 is a parallel module set that IMPORTS the Phase 4
derivation functions (matrix/nash/substitutions) so parity is by
construction, not reimplementation.

Sealed conditional rules (three-layer anchors; freeze-lint check C4):
  R1-persona-composition: persona_system = preamble + "\n\n" + sealed bare
      system text, byte-identical; the persona sha256(preamble) is pinned in
      the arms manifest and re-verified on every request.
  R2-per-T-echo: the provider request body's temperature field must equal
      the arm's pinned temperature on every call (mirror asserted == wire).
  R3-revision-pin: the returned model revision string must equal the arm
      model's pinned revision; any provider-side change freezes, never a
      silent substitution.

Blocks and caps (call-table.json, sealed): tiers A/B/C + P5-sentinel; global
Phase 5 kill-switch 8,984 reserved calls (subtotal + 7.5% headroom) inside
the operator's 15,000 authorization. Shedding never removes personas or
sentinels — episodes only, in the registered order.
"""
from __future__ import annotations

import json
import os
from typing import Any, Optional

from provenance import sha256_hex
from phase4 import (
    ArmStore as _P4ArmStore,
    BudgetLedger,
    EnforcementError,
    PHASE4_PROTOCOL,
    _pd_expected_matrix,
    _pts,
    _pure_nash,
    canonical_json,
    template_sha,
)

ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.normpath(os.path.join(ENGINE_DIR, "..", "..", ".."))
P5_DIR = os.path.join(REPO_ROOT, "docs", "phase5")
ARMS_PATH_P5 = os.environ.get("P5_ARMS_PATH", os.path.join(P5_DIR, "arms.json"))
PERSONAS_PATH = os.environ.get("P5_PERSONAS_PATH", os.path.join(P5_DIR, "personas-v4.json"))

# Frozen Phase 5 protocol: maxTokens/topP inherited from the Phase 4 pin;
# temperature is PER-ARM (sealed in arms.json), from the registered set.
PHASE5_PROTOCOL = {"maxTokens": PHASE4_PROTOCOL["maxTokens"], "topP": PHASE4_PROTOCOL["topP"]}
ALLOWED_TEMPERATURES = (0.7, 1.0, 1.3)

# R3-revision-pin registered values (freeze packet §5).
PINNED_REVISIONS = {"gpt-4.1": "gpt-4.1-2025-04-14", "gemini-2.5-flash": "gemini-2.5-flash"}

# Kill-switch caps — AMENDMENT 1 (operator-approved 2026-07-28, pre-data).
# Original sealed values (call-table.json estimates + 7.5% headroom):
#   global 8,984; {"P5-A": 4,866, "P5-B": 2,347, "P5-C": 1,316, "P5-overhead": 456}.
# Root cause of the bind: the call table priced rep-PD episodes from Phase 4
# ledger per-episode AVERAGES (~7.4 rounds mean at δ=0.90), but the Phase 5
# seed lanes deterministically draw longer games (exact seeded need:
# A 5,168 / B 3,374 / C 1,438 + 424 overhead = 10,404 > 8,984). Horizons are a
# pure function of the sealed seeds, computed before any dispatch — zero
# outcome bits observed at amendment time. Amended caps = exact seeded need
# + 7.5% headroom per tier; global 11,185 ≤ operator standing cap 15,000.
# Registered rule going forward: sealed call tables for seeded designs are
# computed from EXACT seeded horizons at freeze, and the linter checks it.
# See docs/phase5/amendment-1-caps.md.
GLOBAL_CAP_P5 = 11_185
CAP_GROUPS_P5 = {"P5-A": 5_556, "P5-B": 3_627, "P5-C": 1_546, "P5-overhead": 456}
BLOCK_TO_GROUP_P5 = {
    "P5A-rep": "P5-A", "P5A-os": "P5-A",
    "P5B-rep": "P5-B", "P5B-os": "P5-B",
    "P5C-rep": "P5-C", "P5C-os": "P5-C",
    "P5-sentinel": "P5-overhead", "P5-entry": "P5-overhead",
}
# Registered sentinel seed pool: 46001 + checkIndex*10 … +9 (disjoint from
# the Phase 4 pool 9001–9999 so per-window indexing never collides).
SENTINEL_SEED_BASE_P5 = 46_001


class PersonaStore:
    """Sealed persona registry. Every preamble's sha256 is re-verified
    against the sealed file's own per-persona pins at load — a persona whose
    text drifted from its sha is a seal failure, not a warning."""

    def __init__(self, path: str = PERSONAS_PATH):
        with open(path, "rb") as f:
            raw = f.read()
        self.file_sha = sha256_hex(raw)
        data = json.loads(raw)
        self.personas: dict[str, dict] = {}
        for p in data["personas"]:
            got = sha256_hex(p["preamble"].encode("utf-8"))
            if got != p["sha256"]:
                raise EnforcementError(
                    f"persona {p['id']} preamble sha {got[:16]}… != sealed {p['sha256'][:16]}… "
                    "(R1-persona-composition: drifted persona text fails closed)")
            self.personas[p["id"]] = p

    def get(self, persona_id: str) -> dict:
        p = self.personas.get(persona_id)
        if p is None:
            raise EnforcementError(f"unknown sealed persona ID: {persona_id}")
        return p


class ArmStoreP5(_P4ArmStore):
    def __init__(self, path: str = ARMS_PATH_P5):
        super().__init__(path)


class BudgetLedgerP5(BudgetLedger):
    """Same transactional ledger DB (one continuous spend record across
    phases); Phase 5 cap groups and Phase 5 global kill-switch. Both
    check_caps and reserve_call are overridden — the Phase 4 versions read
    the Phase 4 cap tables and would fail closed on P5 blocks."""

    def _p5_counts(self, c) -> tuple[int, dict[str, int]]:
        groups = tuple(CAP_GROUPS_P5)
        rows = c.execute(
            f"SELECT cap_group, COALESCE(SUM(calls),0) FROM spend "
            f"WHERE cap_group IN ({','.join('?' * len(groups))}) GROUP BY cap_group",
            groups).fetchall()
        by_group = {g: int(n) for g, n in rows}
        return sum(by_group.values()), by_group

    def totals_p5(self) -> dict:
        with self._conn() as c:
            total, by_group = self._p5_counts(c)
        return {
            "globalCalls": total, "globalCap": GLOBAL_CAP_P5,
            "byGroup": {g: {"calls": by_group.get(g, 0), "cap": cap}
                        for g, cap in CAP_GROUPS_P5.items()},
        }

    def check_caps(self, block: str) -> None:
        from phase4 import BudgetExceededError
        group = BLOCK_TO_GROUP_P5.get(block)
        if group is None:
            raise EnforcementError(f"block {block} has no Phase 5 cap group")
        t = self.totals_p5()
        if t["globalCalls"] >= GLOBAL_CAP_P5:
            raise BudgetExceededError(
                f"Phase 5 global kill-switch at cap: {t['globalCalls']} >= {GLOBAL_CAP_P5}")
        g = t["byGroup"][group]
        if g["calls"] >= g["cap"]:
            raise BudgetExceededError(
                f"Phase 5 kill-switch at cap for group {group}: {g['calls']} >= {g['cap']}")

    def reserve_call(self, *, run_id: str, arm_id: str, block: str, model: str,
                     run_call_index: int, note: Optional[str] = None) -> int:
        """Transactionally increment BEFORE dispatch, against the PHASE 5
        caps. Same at-most-once row semantics as Phase 4."""
        import sqlite3
        from phase4 import BudgetExceededError, EPISODE_RUNAWAY_CAP, _now
        group = BLOCK_TO_GROUP_P5.get(block)
        if group is None:
            raise EnforcementError(f"block {block} has no Phase 5 cap group")
        if run_call_index > EPISODE_RUNAWAY_CAP:
            raise BudgetExceededError(
                f"single-episode runaway guard: call {run_call_index} > {EPISODE_RUNAWAY_CAP}")
        with self._lock:
            c = self._conn()
            try:
                c.execute("BEGIN IMMEDIATE")
                total, by_group = self._p5_counts(c)
                if total >= GLOBAL_CAP_P5:
                    raise BudgetExceededError(
                        f"Phase 5 global kill-switch at cap: {total} >= {GLOBAL_CAP_P5}")
                if by_group.get(group, 0) >= CAP_GROUPS_P5[group]:
                    raise BudgetExceededError(
                        f"Phase 5 kill-switch at cap for group {group}: "
                        f"{by_group.get(group, 0)} >= {CAP_GROUPS_P5[group]}")
                cur = c.execute(
                    "INSERT INTO spend (ts, run_id, arm_id, block, cap_group, model, calls, note) "
                    "VALUES (?,?,?,?,?,?,1,?)",
                    (_now(), run_id, arm_id, block, group, model, note))
                c.execute("COMMIT")
                return int(cur.lastrowid)
            except Exception:
                try:
                    c.execute("ROLLBACK")
                except sqlite3.OperationalError:
                    pass
                raise
            finally:
                c.close()


def compose_persona_system(preamble: str, bare_system: str) -> str:
    """R1-persona-composition (sealed rule, enforcement layer): the persona
    system layer is EXACTLY preamble + "\n\n" + the sealed bare system text,
    byte-identical — never a rewrite, never a merge."""
    return preamble + "\n\n" + bare_system


def render_substitutions_p5(arm: dict, template_id: str, registry: dict) -> dict:
    """Phase 5 substitution map. pd-os-*/pd-rep-* reuse the Phase 4 rule via
    the same payoff derivation; pd-oneshot-v1 (community cell) pins the
    framing KEY — the framing line itself comes from the sealed template's
    own framings map, never from the request."""
    b = arm["bindings"]
    m = _pd_expected_matrix(b)
    subs = {
        "rr": _pts(m[0][0][0]), "rs": _pts(m[0][1][0]),
        "rt": _pts(m[1][0][0]), "rp": _pts(m[1][1][0]),
    }
    if template_id == "pd-oneshot-v1":
        framing = b.get("framing")
        spec = registry["prompts"][template_id]
        if framing not in spec.get("framings", {}):
            raise EnforcementError(
                f"pd-oneshot-v1 framing {framing!r} not in sealed framings "
                f"{sorted(spec.get('framings', {}))}")
        subs["framing"] = framing
        return subs
    if template_id.startswith(("pd-os-", "pd-rep-")):
        if arm.get("deltaPct") is not None:
            subs["deltaPct"] = _pts(arm["deltaPct"])
        if b.get("labelRoleMap", "aligned") != "aligned":
            subs["labelRoleMap"] = b["labelRoleMap"]
        return subs
    raise EnforcementError(f"no Phase 5 substitution rule for template {template_id}")


def validate_run_request_p5(
    *,
    arm: dict,
    registry: dict,
    store: ArmStoreP5,
    personas: PersonaStore,
    game_def: dict,
    strategy1_slug: str,
    strategy2_slug: str,
    num_rounds: int,
    seed: int,
    model: str,
    temperature: float,
    max_tokens: int,
    episode_index: Optional[int],
    sentinel_check_index: Optional[int],
) -> dict:
    """Full Phase 5 enforcement. Returns the pinned run context or raises
    EnforcementError. Enforcement by rejection, exactly as Phase 4."""
    block = arm["block"]
    if block not in BLOCK_TO_GROUP_P5:
        raise EnforcementError(f"block {block} is not a sealed Phase 5 block")

    # protocol pins — temperature is per-arm (sealed), from the registered set
    arm_t = float(arm["temperature"])
    if arm_t not in ALLOWED_TEMPERATURES:
        raise EnforcementError(
            f"arm {arm['armId']} temperature {arm_t} outside registered set {ALLOWED_TEMPERATURES}")
    if float(temperature) != arm_t:
        raise EnforcementError(
            f"R2-per-T-echo: request temperature {temperature} != arm pin {arm_t}")
    if max_tokens != PHASE5_PROTOCOL["maxTokens"]:
        raise EnforcementError(f"maxTokens {max_tokens} != pinned {PHASE5_PROTOCOL['maxTokens']}")

    # model pin (sentinels too: each sentinel arm pins its model explicitly)
    if model != arm["model"]:
        raise EnforcementError(f"model {model} != arm pin {arm['model']}")
    if model not in PINNED_REVISIONS:
        raise EnforcementError(f"model {model} has no registered revision pin (R3)")

    # persona pin: armId ↔ personaId ↔ sealed preamble sha (R1)
    persona = None
    if arm.get("personaId") is not None:
        persona = personas.get(arm["personaId"])
        if persona["sha256"] != arm.get("personaSha256"):
            raise EnforcementError(
                f"R1-persona-composition: arm {arm['armId']} pins persona sha "
                f"{str(arm.get('personaSha256'))[:16]}… but sealed persona "
                f"{persona['id']} has {persona['sha256'][:16]}…")

    # seed pin
    seeds = arm["seeds"]
    if block != "P5-sentinel" and sentinel_check_index is not None:
        raise EnforcementError(f"sentinelCheckIndex is sentinel-only, got it on block {block}")
    if block == "P5-sentinel":
        if sentinel_check_index is None:
            raise EnforcementError("sentinel runs require sentinelCheckIndex")
        lo = SENTINEL_SEED_BASE_P5 + sentinel_check_index * 10
        hi = lo + 9
        if not (lo <= seed <= hi):
            raise EnforcementError(
                f"sentinel seed {seed} outside check-{sentinel_check_index} window {lo}–{hi}")
    elif isinstance(seeds, list):
        if seed not in seeds:
            raise EnforcementError(f"seed {seed} not in arm seed list {seeds[0]}–{seeds[-1]}")
        if episode_index is not None and seeds[episode_index - 1] != seed:
            raise EnforcementError(
                f"episodeIndex {episode_index} pins seed {seeds[episode_index - 1]}, got {seed}")
    else:
        raise EnforcementError(f"arm {arm['armId']} has non-list seeds and is not sentinel")

    # template sha recheck (no RESOLVED-BY placeholders exist in Phase 5)
    template_id = arm["templateId"]
    spec = registry["prompts"].get(template_id)
    if spec is None:
        raise EnforcementError(f"template {template_id} not in registry")
    expected_sha = store.template_shas.get(template_id)
    if expected_sha is None:
        raise EnforcementError(f"template {template_id} has no sealed sha in arms manifest")
    got_sha = template_sha(spec)
    if got_sha != expected_sha:
        raise EnforcementError(
            f"template sha mismatch for {template_id}: {got_sha[:16]}… != sealed {expected_sha[:16]}…")

    # horizon pins
    if block.endswith("-os") or block in ("P5-sentinel", "P5-entry"):
        if num_rounds != 1:
            raise EnforcementError(f"{block} is one-shot/forced-1: numRounds must be 1, got {num_rounds}")
    else:  # *-rep: geometric horizon drawn by the driver, cap 120 (X1 rule)
        if not (1 <= num_rounds <= 120):
            raise EnforcementError(f"{block} numRounds {num_rounds} outside 1–120 horizon cap")

    # seats: Phase 5 is self-play throughout (same persona both seats)
    if strategy1_slug != "llm-subject" or strategy2_slug != "llm-subject":
        raise EnforcementError(f"{block} is self-play: both seats must be llm-subject")

    # expected game definition
    subs = render_substitutions_p5(arm, template_id, registry)
    expected_matrix = _pd_expected_matrix(arm["bindings"])
    options = spec["options"]
    expected_game = {
        "numActions": len(options),
        "actionLabels": list(options),
        "payoffMatrix": expected_matrix,
        "nashEquilibria": _pure_nash(expected_matrix),
    }

    def _num_norm(v: Any) -> Any:
        if isinstance(v, bool):
            return v
        if isinstance(v, float) and v.is_integer():
            return int(v)
        if isinstance(v, list):
            return [_num_norm(x) for x in v]
        if isinstance(v, dict):
            return {k: _num_norm(x) for k, x in v.items()}
        return v

    for key in ("numActions", "actionLabels", "payoffMatrix", "nashEquilibria"):
        if canonical_json(_num_norm(game_def.get(key))) != canonical_json(_num_norm(expected_game[key])):
            raise EnforcementError(
                f"gameDef.{key} does not match the arm's pinned bindings "
                f"(expected {canonical_json(expected_game[key])[:120]}…)")

    return {
        "templateId": template_id,
        "templateSha256": expected_sha,
        "substitutions": subs,
        "deltaPct": arm.get("deltaPct"),
        "block": block,
        "temperature": arm_t,
        "personaId": persona["id"] if persona else None,
        "personaSha256": persona["sha256"] if persona else None,
        "personaPreamble": persona["preamble"] if persona else None,
        "expectedGame": expected_game,
    }


def assert_revision_pin(model: str, returned_model: Optional[str]) -> None:
    """R3-revision-pin (sealed rule, enforcement layer): the revision string
    the provider returns must equal the registered pin exactly. Missing or
    different ⇒ hard abort (response archived, spend kept) — a provider-side
    model change is a disclosed event, never a silent substitution."""
    pin = PINNED_REVISIONS[model]
    if returned_model != pin:
        raise RuntimeError(
            f"R3-revision-pin violation: provider returned model {returned_model!r}, "
            f"registered pin {pin!r} (aborting; response archived, spend kept)")


def assert_temperature_echo(mirror_body: dict, model: str, expected_t: float) -> None:
    """R2-per-T-echo (sealed rule, enforcement layer): the temperature field
    inside the ACTUAL provider request body (mirror-asserted == wire by the
    runner) must equal the arm's pinned temperature, per call, per T."""
    if model.startswith("gpt-"):
        got = mirror_body.get("temperature")
    elif model.startswith("gemini-"):
        got = (mirror_body.get("generation_config") or {}).get("temperature")
    else:
        raise RuntimeError(f"R2-per-T-echo: no temperature field rule for model {model}")
    if got is None or float(got) != float(expected_t):
        raise RuntimeError(
            f"R2-per-T-echo violation: request body temperature {got!r} != pinned {expected_t} "
            f"(aborting before dispatch)")
