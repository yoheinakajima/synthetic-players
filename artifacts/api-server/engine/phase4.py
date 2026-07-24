"""Phase 4 server-side enforcement + transactional budget ledger (§F.3).

Enforcement is rejection, not convention: a Phase 4 run request must name a
sealed arm ID; the engine resolves template + bindings from the sealed arms
manifest, derives the expected game definition and the FULL substitution map
itself (client-supplied values are verified, never trusted), recomputes the
template sha at run start, and refuses anything outside the arm's pins.

Budget: every provider call reserves a ledger row transactionally BEFORE
dispatch (sqlite BEGIN IMMEDIATE). Caps are the frozen budget.md values —
breach refuses the call and aborts the run; spend rows for failed dispatches
stay on the record (burned calls are never invisible).

Live Phase 4 runs are refused while the registry is `*-proposed` (sealing is
step 3); dry runs (render + enforcement, zero provider calls, zero events)
are allowed pre-seal for infrastructure verification.
"""
from __future__ import annotations

import json
import os
import sqlite3
import threading
import time
from typing import Any, Optional

from provenance import canonical_json, sha256_hex, template_sha

ENGINE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.normpath(os.path.join(ENGINE_DIR, "..", "..", ".."))
ARMS_PATH = os.environ.get("ARMS_PATH", os.path.join(REPO_ROOT, "docs", "phase4", "arms.json"))
BUDGET_DB_PATH = os.environ.get("BUDGET_DB_PATH", os.path.join(ENGINE_DIR, "data", "budget.db"))

# Frozen protocol constants (predicates.md / freeze packet §F): the subject
# protocol is not a request parameter, it is a pin.
PHASE4_PROTOCOL = {"temperature": 0.7, "maxTokens": 16, "topP": 1.0}
SUBJECT_MODELS = ("gpt-4.1", "gemini-2.5-flash")  # primary, cross (amendment A1)

# Frozen kill-switch caps (budget.md — engine-enforced, sign-off §10).
# Overhead cap amended 900 → 1_000 on 2026-07-24 (docs/phase4/
# budget-amendments.md A-OVH-1): operator-approved doubled sentinel cadence
# after alert 5 ("the extra sentinel spend is approved" — sentinel-alert-5-
# memo.md §Decision). budget.md itself is sealed and byte-untouched; the
# global cap is unchanged.
GLOBAL_CAP = 21_000
CAP_GROUPS = {"D": 4_300, "E": 1_800, "X2": 2_700, "F": 11_600, "overhead": 1_000}
BLOCK_TO_GROUP = {
    "D1": "D", "D2": "D", "D3": "D",
    "E": "E",
    "X2-screening": "X2", "X2-confirmation": "X2",
    "F": "F",
    "sentinel": "overhead", "infra": "overhead", "ratings": "overhead",
}
EPISODE_RUNAWAY_CAP = 260  # single-episode guard (2 × cap-120 horizon + retries)

RPS_ROLES = ("rock", "paper", "scissors")
RPS_BEATS = {"rock": "scissors", "scissors": "paper", "paper": "rock"}


class BudgetExceededError(RuntimeError):
    """Cap breach: hard stop, disclosure, decision memo — never a silent trim."""


class EnforcementError(ValueError):
    """Request violates the sealed arm's pins. Mapped to HTTP 400."""


# ── arms manifest ───────────────────────────────────────────────────────────

class ArmStore:
    def __init__(self, path: str = ARMS_PATH):
        with open(path, "rb") as f:
            raw = f.read()
        self.manifest_sha = sha256_hex(raw)
        data = json.loads(raw)
        self.models = data["models"]
        self.template_shas: dict[str, str] = dict(data["templateShas"])
        self.template_shas.update(data["sealedPhase3Shas"])  # sealed Phase 3 ids
        self.arms: dict[str, dict] = {a["armId"]: a for a in data["arms"]}

    def get(self, arm_id: str) -> dict:
        arm = self.arms.get(arm_id)
        if arm is None:
            raise EnforcementError(f"unknown sealed arm ID: {arm_id}")
        return arm


def self_check(registry: dict, store: ArmStore) -> dict:
    """Startup parity check: recompute EVERY template sha named by the arms
    manifest from the current registry with the Python canonical serializer
    and compare byte-for-byte with the Node-computed values. Any mismatch
    disables Phase 4 traffic — parity is verified, not assumed."""
    mismatches = []
    for tid, expected in store.template_shas.items():
        spec = registry["prompts"].get(tid)
        if spec is None:
            mismatches.append(f"template {tid} in arms manifest but not in registry")
            continue
        got = template_sha(spec)
        if got != expected:
            mismatches.append(f"template {tid}: recomputed sha {got[:16]}… != manifest {expected[:16]}…")
    return {
        "ok": not mismatches,
        "templatesChecked": len(store.template_shas),
        "mismatches": mismatches,
        "armsManifestSha256": store.manifest_sha,
    }


# ── resolutions (E D-selected template, X2 confirmation pair) ───────────────

RESOLUTION_KEYS = {
    "E-dselected": "pd-rep-",
    "X2-conf-lo": "pd-x2-",
    "X2-conf-hi": "pd-x2-",
}


# ── budget ledger ───────────────────────────────────────────────────────────

_GATE0_BACKFILL = [
    # (run_id, calls, input_tokens, output_tokens) — exact values recomputed
    # from the event store (infra.gate0.call events), 2026-07-24.
    ("gate0_1784906629_0933fb21", 7, 1436, 55),   # round 1 (gpt-4.1 + claude, incl. 64-tok diagnostic)
    ("gate0_1784908582_1a0189ea", 2, 384, 2),     # aborted round-2 attempt (gpt calls before gemini endpoint fix)
    ("gate0_1784908630_49d774e7", 6, 1152, 6),    # round 2 PASS (gpt-4.1 + gemini-2.5-flash)
]


class BudgetLedger:
    """Transactional call ledger. One row per provider call attempt,
    reserved BEFORE dispatch; token counts updated after the response."""

    def __init__(self, path: str = BUDGET_DB_PATH):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.path = path
        self._lock = threading.Lock()
        with self._conn() as c:
            c.execute(
                """CREATE TABLE IF NOT EXISTS spend (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ts TEXT NOT NULL,
                    run_id TEXT NOT NULL,
                    arm_id TEXT NOT NULL,
                    block TEXT NOT NULL,
                    cap_group TEXT NOT NULL,
                    model TEXT NOT NULL,
                    calls INTEGER NOT NULL,
                    input_tokens INTEGER NOT NULL DEFAULT 0,
                    output_tokens INTEGER NOT NULL DEFAULT 0,
                    note TEXT
                )"""
            )
            c.execute(
                """CREATE TABLE IF NOT EXISTS resolutions (
                    key TEXT PRIMARY KEY,
                    template_id TEXT NOT NULL,
                    ts TEXT NOT NULL,
                    event_run_id TEXT NOT NULL,
                    note TEXT
                )"""
            )
            # idempotent Gate-0 backfill (both rounds + aborted attempt)
            for run_id, calls, ti, to in _GATE0_BACKFILL:
                note = f"gate0-backfill:{run_id}"
                row = c.execute("SELECT id FROM spend WHERE note = ?", (note,)).fetchone()
                if row is None:
                    c.execute(
                        "INSERT INTO spend (ts, run_id, arm_id, block, cap_group, model, calls, input_tokens, output_tokens, note) "
                        "VALUES (?,?,?,?,?,?,?,?,?,?)",
                        (_now(), run_id, "infra-gate0", "infra", "overhead", "mixed(gate0)", calls, ti, to, note),
                    )

    def _conn(self) -> sqlite3.Connection:
        c = sqlite3.connect(self.path, timeout=30)
        c.isolation_level = None  # explicit transactions
        return c

    def totals(self) -> dict:
        with self._conn() as c:
            rows = c.execute(
                "SELECT cap_group, SUM(calls), SUM(input_tokens), SUM(output_tokens) FROM spend GROUP BY cap_group"
            ).fetchall()
        by_group = {g: {"calls": int(n), "inputTokens": int(ti), "outputTokens": int(to)} for g, n, ti, to in rows}
        total = sum(v["calls"] for v in by_group.values())
        return {
            "globalCalls": total, "globalCap": GLOBAL_CAP,
            "byGroup": {
                g: {**by_group.get(g, {"calls": 0, "inputTokens": 0, "outputTokens": 0}), "cap": cap}
                for g, cap in CAP_GROUPS.items()
            },
        }

    def check_caps(self, block: str) -> None:
        """Refuse-at-run-start check (also implied by every reserve)."""
        group = BLOCK_TO_GROUP.get(block)
        if group is None:
            raise EnforcementError(f"block {block} has no registered cap group")
        t = self.totals()
        if t["globalCalls"] >= GLOBAL_CAP:
            raise BudgetExceededError(f"global kill-switch at cap: {t['globalCalls']} >= {GLOBAL_CAP}")
        g = t["byGroup"][group]
        if g["calls"] >= g["cap"]:
            raise BudgetExceededError(f"block kill-switch at cap for group {group}: {g['calls']} >= {g['cap']}")

    def reserve_call(self, *, run_id: str, arm_id: str, block: str, model: str,
                     run_call_index: int, note: Optional[str] = None) -> int:
        """Transactionally increment BEFORE dispatch. Returns the spend row id.
        Raises BudgetExceededError at any cap — the call must not be made."""
        group = BLOCK_TO_GROUP.get(block)
        if group is None:
            raise EnforcementError(f"block {block} has no registered cap group")
        if run_call_index > EPISODE_RUNAWAY_CAP:
            raise BudgetExceededError(
                f"single-episode runaway guard: call {run_call_index} > {EPISODE_RUNAWAY_CAP}"
            )
        with self._lock:
            c = self._conn()
            try:
                c.execute("BEGIN IMMEDIATE")
                total = int(c.execute("SELECT COALESCE(SUM(calls),0) FROM spend").fetchone()[0])
                if total >= GLOBAL_CAP:
                    raise BudgetExceededError(f"global kill-switch at cap: {total} >= {GLOBAL_CAP}")
                gtotal = int(c.execute(
                    "SELECT COALESCE(SUM(calls),0) FROM spend WHERE cap_group = ?", (group,)
                ).fetchone()[0])
                if gtotal >= CAP_GROUPS[group]:
                    raise BudgetExceededError(
                        f"block kill-switch at cap for group {group}: {gtotal} >= {CAP_GROUPS[group]}"
                    )
                cur = c.execute(
                    "INSERT INTO spend (ts, run_id, arm_id, block, cap_group, model, calls, note) "
                    "VALUES (?,?,?,?,?,?,1,?)",
                    (_now(), run_id, arm_id, block, group, model, note),
                )
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

    def record_tokens(self, row_id: int, input_tokens: int, output_tokens: int,
                      note: Optional[str] = None) -> None:
        with self._lock, self._conn() as c:
            if note is None:
                c.execute(
                    "UPDATE spend SET input_tokens = ?, output_tokens = ? WHERE id = ?",
                    (int(input_tokens), int(output_tokens), row_id),
                )
            else:
                c.execute(
                    "UPDATE spend SET input_tokens = ?, output_tokens = ?, note = ? WHERE id = ?",
                    (int(input_tokens), int(output_tokens), note, row_id),
                )

    def run_rows(self, run_id: str) -> list[dict]:
        with self._conn() as c:
            rows = c.execute(
                "SELECT id, arm_id, block, model, calls, input_tokens, output_tokens, note FROM spend WHERE run_id = ? ORDER BY id",
                (run_id,),
            ).fetchall()
        return [
            {"id": r[0], "armId": r[1], "block": r[2], "model": r[3], "calls": r[4],
             "inputTokens": r[5], "outputTokens": r[6], "note": r[7]}
            for r in rows
        ]

    # resolutions are write-once; changing one is an amendment, not an update
    def get_resolution(self, key: str) -> Optional[dict]:
        with self._conn() as c:
            r = c.execute(
                "SELECT key, template_id, ts, event_run_id, note FROM resolutions WHERE key = ?", (key,)
            ).fetchone()
        return None if r is None else {
            "key": r[0], "templateId": r[1], "ts": r[2], "eventRunId": r[3], "note": r[4]
        }

    def put_resolution(self, key: str, template_id: str, event_run_id: str, note: str) -> None:
        with self._lock:
            c = self._conn()
            try:
                c.execute("BEGIN IMMEDIATE")
                exists = c.execute("SELECT template_id FROM resolutions WHERE key = ?", (key,)).fetchone()
                if exists is not None:
                    raise EnforcementError(
                        f"resolution {key} already written ({exists[0]}); changing it requires a registered amendment"
                    )
                c.execute(
                    "INSERT INTO resolutions (key, template_id, ts, event_run_id, note) VALUES (?,?,?,?,?)",
                    (key, template_id, _now(), event_run_id, note),
                )
                c.execute("COMMIT")
            except Exception:
                try:
                    c.execute("ROLLBACK")
                except sqlite3.OperationalError:
                    pass
                raise
            finally:
                c.close()


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


# ── expected game definition + substitutions (derived, never trusted) ───────

def _pure_nash(matrix: list[list[list[float]]]) -> list[list[int]]:
    """Generic pure-strategy NE cells of a 2-player bimatrix (weak best response)."""
    n = len(matrix)
    m = len(matrix[0])
    out = []
    for i in range(n):
        for j in range(m):
            p1 = matrix[i][j][0]
            p2 = matrix[i][j][1]
            if all(matrix[k][j][0] <= p1 for k in range(n)) and all(matrix[i][l][1] <= p2 for l in range(m)):
                out.append([i, j])
    return out


def _pd_expected_matrix(bindings: dict) -> list[list[list[float]]]:
    rr, rs, rt, rp = bindings["rr"], bindings["rs"], bindings["rt"], bindings["rp"]
    aligned = [[[rr, rr], [rs, rt]], [[rt, rs], [rp, rp]]]
    if bindings.get("labelRoleMap", "aligned") == "aligned":
        return aligned
    # swapped (D2): displayed option 0 carries the DEFECTION role
    return [[[rp, rp], [rt, rs]], [[rs, rt], [rr, rr]]]


def _rps_sym_expected_matrix(role_mapping: dict) -> list[list[list[float]]]:
    """3×3 win/tie/loss matrix over displayed symbols [X, Y, Z] given their
    hidden rock/paper/scissors roles."""
    syms = ["X", "Y", "Z"]
    out = []
    for a in syms:
        row = []
        for b in syms:
            ra, rb = role_mapping[a], role_mapping[b]
            if ra == rb:
                row.append([0, 0])
            elif RPS_BEATS[ra] == rb:
                row.append([1, -1])
            else:
                row.append([-1, 1])
        out.append(row)
    return out


def _rps_standard_matrix() -> list[list[list[float]]]:
    """Sealed rps-v1 game: options [rock, paper, scissors] in canonical order."""
    return _rps_sym_expected_matrix({"X": "rock", "Y": "paper", "Z": "scissors"})


def _pts(x: Any) -> Any:
    return int(x) if float(x) == int(x) else x


def render_substitutions(arm: dict, template_id: str, registry: dict) -> dict:
    """The FULL dynamic substitution map (§F.3 field 3), derived from the
    arm's pinned bindings only. rps-sym optList/beatsLine rendering is pinned
    HERE (render rule from arms.json, exact join engine-pinned; captured
    per call and re-rendered byte-identically in replay)."""
    b = arm["bindings"]
    block = arm["block"]
    if template_id.startswith(("pd-os-", "pd-rep-", "pd-x2-", "pd-repeated-")):
        m = _pd_expected_matrix(b)
        subs = {
            "rr": _pts(m[0][0][0]), "rs": _pts(m[0][1][0]),
            "rt": _pts(m[1][0][0]), "rp": _pts(m[1][1][0]),
        }
        if arm.get("deltaPct") is not None:
            subs["deltaPct"] = _pts(arm["deltaPct"])
        if block in ("D2",):
            subs["labelRoleMap"] = b["labelRoleMap"]
        return subs
    if template_id == "rps-sym-v1":
        role_mapping = b["roleMapping"]
        display_order = b["displayOrder"]
        opt_list = ", ".join(display_order[:-1]) + " or " + display_order[-1]
        beats = {s: next(t for t in role_mapping if RPS_BEATS[role_mapping[s]] == role_mapping[t])
                 for s in role_mapping}
        beats_line = " ".join(f"{s} beats {beats[s]}." for s in display_order)
        return {
            "roleMapping": role_mapping, "displayOrder": display_order,
            "optList": opt_list, "beatsLine": beats_line,
        }
    if template_id == "rps-v1":
        # Sealed Phase 3 template (F block): the only static placeholder is
        # the horizon; opponent identity is archived for the analysis join.
        return {"numRounds": b["rounds"], "opponent": b["opponent"]}
    raise EnforcementError(f"no substitution rule for template {template_id}")


def resolve_template_id(arm: dict, ledger: BudgetLedger) -> tuple[str, Optional[str]]:
    """Concrete template for an arm; RESOLVED-BY-* placeholders require a
    write-once resolution record (written to the event store first)."""
    tid = arm["templateId"]
    if not tid.startswith("RESOLVED-BY"):
        if arm["block"] == "sentinel" and arm["armId"] == "p4-sent-fallback":
            # Sealed sentinel spec (arms.json bindings note; predicates.md
            # §sentinel): the third cell "switches to the D-selected
            # representation once written to the event store; sealed fallback
            # before". Ledger-state-driven — never request-driven. Implemented
            # 2026-07-24 under sentinel-alert-5-memo.md §Decision (the switch
            # was pre-committed in sealed text but present in neither
            # enforcement nor dispatch — provenance-notes.md, instance 5).
            res = ledger.get_resolution("E-dselected")
            if res is not None:
                return res["templateId"], "E-dselected"
        return tid, None
    if arm["block"] == "E":
        key = "E-dselected"
    elif arm["block"] == "X2-confirmation":
        key = "X2-conf-lo" if arm["armId"].endswith("-lo") else "X2-conf-hi"
    else:
        raise EnforcementError(f"arm {arm['armId']} has unresolvable template {tid}")
    res = ledger.get_resolution(key)
    if res is None:
        raise EnforcementError(
            f"arm {arm['armId']} requires resolution '{key}' — not yet written to the event store"
        )
    return res["templateId"], key


def _sentinel_switch_delta(store: "ArmStore") -> int:
    """The sealed third-cell switch text pins no deltaPct, and no sealed
    dispatch of the selected pd-rep sibling exists to mirror (D1 arms carry
    pd-os-* templates; block E manipulates δ as its treatment variable).
    Registered rule: the switched cell adopts the sentinel battery's own
    repeated-cell continuation probability — the unique deltaPct shared by
    every other sentinel arm that carries one (v1/v2a: 90). Sentinel-internal,
    no cross-block inference; fail-closed if the battery's repeated cells ever
    disagree. Registered under sentinel-alert-5-memo.md §Decision (provenance
    instance 5 follow-up)."""
    deltas = {a.get("deltaPct") for a in store.arms.values()
              if a.get("block") == "sentinel" and a.get("deltaPct") is not None}
    if len(deltas) != 1:
        raise EnforcementError(
            f"sentinel third-cell switch: expected one shared repeated-cell deltaPct "
            f"across sentinel arms, found {sorted(deltas)} — fail-closed")
    return deltas.pop()


def validate_run_request(
    *,
    arm: dict,
    registry: dict,
    store: ArmStore,
    ledger: BudgetLedger,
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
    known_strategies: set[str],
) -> dict:
    """Full §F.3 enforcement. Returns the pinned run context (template id +
    sha, substitutions, expected gameDef) or raises EnforcementError."""
    block = arm["block"]

    # protocol pins
    if temperature != PHASE4_PROTOCOL["temperature"]:
        raise EnforcementError(f"temperature {temperature} != pinned {PHASE4_PROTOCOL['temperature']}")
    if max_tokens != PHASE4_PROTOCOL["maxTokens"]:
        raise EnforcementError(f"maxTokens {max_tokens} != pinned {PHASE4_PROTOCOL['maxTokens']}")

    # model pin
    if block == "sentinel":
        if model not in SUBJECT_MODELS:
            raise EnforcementError(f"sentinel model {model} not in {SUBJECT_MODELS}")
    elif model != arm["model"]:
        raise EnforcementError(f"model {model} != arm pin {arm['model']}")

    # seed pin
    seeds = arm["seeds"]
    if block == "sentinel":
        # Registered pool: seeds 9001 + checkIndex*10 … +9, one window per
        # sentinel check. The check index is part of the record, not optional.
        if sentinel_check_index is None:
            raise EnforcementError("sentinel runs require sentinelCheckIndex")
        lo = 9001 + sentinel_check_index * 10
        hi = lo + 9
        if hi > 9999:
            raise EnforcementError(f"sentinelCheckIndex {sentinel_check_index} exhausts the 9001–9999 pool")
        if not (lo <= seed <= hi):
            raise EnforcementError(
                f"sentinel seed {seed} outside check-{sentinel_check_index} window {lo}–{hi}"
            )
    elif isinstance(seeds, list):
        if sentinel_check_index is not None:
            raise EnforcementError(f"sentinelCheckIndex is sentinel-only, got it on block {block}")
        if seed not in seeds:
            raise EnforcementError(f"seed {seed} not in arm seed list {seeds[0]}–{seeds[-1]}")
        if episode_index is not None and seeds[episode_index - 1] != seed:
            raise EnforcementError(
                f"episodeIndex {episode_index} pins seed {seeds[episode_index - 1]}, got {seed}"
            )
    else:
        raise EnforcementError(f"arm {arm['armId']} has non-list seeds and is not sentinel")

    # template resolution + sha recheck
    template_id, resolution_key = resolve_template_id(arm, ledger)
    if resolution_key == "E-dselected" and block == "sentinel":
        # Sealed third-cell switch (see _sentinel_switch_delta): the effective
        # arm renders the D-selected pd-rep representation at the sentinel
        # battery's own repeated-cell δ (v1/v2a: 90) — the same
        # representation×δ the E δ=.90 D-selected cells use; horizon stays
        # forced to 1 by the sentinel numRounds pin below.
        arm = {**arm, "deltaPct": _sentinel_switch_delta(store)}

    # deltaPct pin (after any sentinel-switch donor substitution)
    delta = arm.get("deltaPct")
    spec = registry["prompts"].get(template_id)
    if spec is None:
        raise EnforcementError(f"template {template_id} not in registry")
    expected_sha = store.template_shas.get(template_id)
    if expected_sha is None:
        raise EnforcementError(f"template {template_id} has no sealed sha in arms manifest")
    got_sha = template_sha(spec)
    if got_sha != expected_sha:
        raise EnforcementError(
            f"template sha mismatch for {template_id}: {got_sha[:16]}… != sealed {expected_sha[:16]}…"
        )

    # numRounds pins per block
    if block in ("D1", "D2"):
        if num_rounds != 1:
            raise EnforcementError(f"{block} is one-shot: numRounds must be 1, got {num_rounds}")
    elif block == "D3":
        if num_rounds != 1:
            raise EnforcementError(f"D3 is 1-round: numRounds must be 1, got {num_rounds}")
    elif block == "F":
        if num_rounds != arm["bindings"]["rounds"]:
            raise EnforcementError(f"F pins numRounds {arm['bindings']['rounds']}, got {num_rounds}")
    elif block == "sentinel":
        if num_rounds != 1:
            raise EnforcementError(f"sentinel horizon is forced to 1, got {num_rounds}")
    else:  # E, X2-*: geometric horizon drawn by the runner, cap 120
        if not (1 <= num_rounds <= 120):
            raise EnforcementError(f"{block} numRounds {num_rounds} outside 1–120 horizon cap")

    # seats
    if block == "F":
        if strategy1_slug != "llm-subject":
            raise EnforcementError("F block: seat 1 must be llm-subject")
        opp = arm["bindings"]["opponent"]
        if strategy2_slug != opp:
            raise EnforcementError(f"F block: seat 2 must be the pinned opponent {opp}, got {strategy2_slug}")
        if opp not in known_strategies:
            raise EnforcementError(
                f"F opponent strategy '{opp}' is not implemented in the engine yet (step-4 work) — refusing"
            )
    else:
        if strategy1_slug != "llm-subject" or strategy2_slug != "llm-subject":
            raise EnforcementError(f"{block} is self-play: both seats must be llm-subject")

    # expected game definition (derived from bindings; request must match EXACTLY)
    subs = render_substitutions(arm, template_id, registry)
    if template_id.startswith(("pd-os-", "pd-rep-", "pd-x2-", "pd-repeated-")):
        expected_matrix = _pd_expected_matrix(arm["bindings"])
        options = spec["options"]
    elif template_id == "rps-sym-v1":
        expected_matrix = _rps_sym_expected_matrix(arm["bindings"]["roleMapping"])
        options = spec["options"]
    elif template_id == "rps-v1":
        expected_matrix = _rps_standard_matrix()
        options = spec["options"]
    else:
        raise EnforcementError(f"no game-definition rule for template {template_id}")

    expected_game = {
        "numActions": len(options),
        "actionLabels": list(options),
        "payoffMatrix": expected_matrix,
        "nashEquilibria": _pure_nash(expected_matrix),
    }

    def _num_norm(v: Any) -> Any:
        # HTTP models coerce ints to floats (3 → 3.0); the comparison is over
        # VALUES, not float formatting. Integral floats normalize to ints on
        # both sides before canonical serialization.
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
                f"(expected {canonical_json(expected_game[key])[:120]}…)"
            )

    return {
        "templateId": template_id,
        "templateSha256": expected_sha,
        "resolutionKey": resolution_key,
        "substitutions": subs,
        "deltaPct": delta,
        "block": block,
        "expectedGame": expected_game,
    }
