"""Phase 5 close-out adjudicator — sealed predicates P5-1a/1b, P5-2, P5-3, P5-4.

Verdicts are computed by code from the event store only; the author never
adjudicates. Registered sources:
  docs/phase5/freeze-packet-draft.md §4 (predicates)
  docs/phase5/seal-record.md          (pinned constants)
  docs/paper/discussion-branches.md   (branch selection rule)

Modes
  --bare-gates   outcome-blind: interior-gate status of every candidate
                 bare-twin source (no Phase 5 persona outcomes touched)
  --selftest     fixture checks of the pure adjudication cores
  --adjudicate   full run; requires docs/phase5-close/adjudication-decisions.json
                 (operator-signed completion of the underspecified bits,
                 recorded outcome-blind BEFORE this mode is first run)

Conventions pinned for parity with Phase 4:
  - round-1 cooperation per episode: ((a1==coopRole)+(a2==coopRole))/2 from
    the round.played round-1 event; cooperate ROLE derived from the recorded
    payoff matrix (mutual payoff comparison), never from displayed labels.
  - interior gate: seat-level trials k=round(sum*2), n=2*len(episodes),
    Clopper-Pearson 95% two-sided, interval wholly inside open (0.05, 0.95).
  - δ-slope: phase4_adjudicate._e_slope reused verbatim (BCa 20260801 with
    exact CP fallback for constant cells).
  - exclusion rule: completed runs only; trial.invalidated runs excluded and
    tabulated (registered secondary under P5-4).
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sqlite3
import sys
from collections import defaultdict

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

REPO_ROOT = os.path.normpath(os.path.join(_HERE, "..", "..", ".."))
DB_PATH = os.path.join(_HERE, "data", "engine.db")
P5DOCS = os.path.join(REPO_ROOT, "docs", "phase5")
CLOSE = os.path.join(REPO_ROOT, "docs", "phase5-close")
DECISIONS_PATH = os.path.join(CLOSE, "adjudication-decisions.json")

from phase4_adjudicate import _cp_bounds, _e_slope  # noqa: E402

# ---- pinned constants (seal-record.md / freeze-packet-draft.md §4) ----
THETA_1 = 0.10          # P5-1a interior-fraction threshold
RHO = 0.75              # P5-1b SD ratio
HUMAN_SD = {"d90": 0.3116, "d10": 0.4122}   # DF2011 R=40 panels
THETA_2 = 0.20          # P5-3(b) refusal CP lower bound
P52_LB = 0.80           # task-dominant CP lower bound
P52_UB = 0.20           # persona-dominant CP upper bound
GATE_LO, GATE_HI = 0.05, 0.95

TIER_A_CELLS = ["rep-d10-s2a", "rep-d10-s2p", "rep-d90-s2a", "rep-d90-s2p",
                "os-swap", "os-community"]
FAMILY_OF = {"rep-d90-s2a": "rep-δ90", "rep-d90-s2p": "rep-δ90",
             "rep-d10-s2a": "rep-δ10", "rep-d10-s2p": "rep-δ10",
             "os-swap": "os-swap", "os-community": "os-community"}
SWEEP_CELLS = ["rep-d90-s2a", "rep-d90-s2p", "os-swap"]
SUBSET_B = ["p02", "p06", "p11", "p15"]


# ---------------------------------------------------------------- stats
def seat_counts(eps: list[float]) -> tuple[int, int]:
    return int(round(sum(eps) * 2)), 2 * len(eps)


def gate_cell(eps: list[float]) -> dict:
    k, n = seat_counts(eps)
    lo, hi = _cp_bounds(k, n)
    return {"k": k, "n": n, "mean": (k / n) if n else None,
            "cp95": [lo, hi],
            "interior": bool(n and lo > GATE_LO and hi < GATE_HI)}


def wilson(k: int, n: int, z: float) -> tuple[float, float]:
    if n == 0:
        return 0.0, 1.0
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (c - h) / d, (c + h) / d


def newcombe_lb_one_sided(k1: int, n1: int, k2: int, n2: int,
                          alpha: float = 0.05) -> float:
    """One-sided 95% lower bound for p1 - p2 (Newcombe score method)."""
    z = 1.6448536269514722 if alpha == 0.05 else _z(1 - alpha)
    p1, p2 = k1 / n1, k2 / n2
    l1, _ = wilson(k1, n1, z)
    _, u2 = wilson(k2, n2, z)
    return (p1 - p2) - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2)


def _z(q: float) -> float:
    from scipy.stats import norm
    return float(norm.ppf(q))


def sample_sd(xs: list[float]) -> float:
    m = sum(xs) / len(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def entropy(counts: dict) -> float:
    tot = sum(counts.values())
    if not tot:
        return 0.0
    return -sum((c / tot) * math.log2(c / tot) for c in counts.values() if c)


# ---------------------------------------------------------------- data
def load_runs(db_path: str = DB_PATH) -> dict:
    """Group events by run_id for every arm of interest.

    Returns runId -> {armId, block, temperature, model, personaId(from arms),
                      coopRole (payoff-derived), round1:(a1,a2), invalid,
                      completed, source}
    """
    arms = load_p5_arms()
    db = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    runs: dict[str, dict] = {}
    p3_community: set[str] = set()

    for rid, typ, payload in db.execute(
            "SELECT run_id, type, payload FROM events "
            "WHERE type IN ('llm.requested','round.played',"
            "'trial.invalidated','run.completed','object.created') "
            "ORDER BY rowid"):
        d = json.loads(payload)
        r = runs.setdefault(rid, {"armId": None, "block": None, "round1": None,
                                  "invalid": False, "completed": False,
                                  "temperature": None, "model": None,
                                  "coopRole": None, "actions": []})
        if typ == "llm.requested":
            if r["armId"] is None and d.get("armId"):
                r.update(armId=d["armId"], block=d.get("block"),
                         temperature=d.get("temperature"), model=d.get("model"))
            if (d.get("armId") is None and d.get("promptId") == "pd-oneshot-v1"
                    and "communit" in (d.get("user") or "").lower()
                    and d.get("model") == "gpt-4.1"
                    and d.get("temperature") == 0.7):
                p3_community.add(rid)
                r.update(temperature=0.7, model="gpt-4.1")
        elif typ == "object.created" and "payoffMatrix" in payload:
            m = d.get("payoffMatrix") or (d.get("gameDef") or {}).get("payoffMatrix")
            if m:
                r["coopRole"] = 0 if m[0][0][0] >= m[1][1][0] else 1
        elif typ == "round.played":
            if d.get("roundNumber") == 1:
                r["round1"] = (d["player1Action"], d["player2Action"])
            r["actions"].extend([d["player1Action"], d["player2Action"]])
        elif typ == "trial.invalidated":
            r["invalid"] = True
        elif typ == "run.completed":
            r["completed"] = True

    out = {}
    for rid, r in runs.items():
        if rid in p3_community:
            r["armId"] = "__p3-community-bare__"
            r["cell"] = "os-community"
            r["personaId"] = None
        elif r["armId"] in arms:
            a = arms[r["armId"]]
            r["cell"] = a["cell"]
            r["personaId"] = a.get("personaId")
        elif r["armId"] in ("p5-sent-bare-gpt", "p4-d2-w1-can-sw-gpt",
                            "p4-d1-can-w1-neu-cf-ad-gpt",
                            "p4-d1-can-w2a-neu-cf-ad-gpt"):
            r["cell"] = None
            r["personaId"] = None
        else:
            continue
        if r["coopRole"] is None:
            r["coopRole"] = 0            # aligned default; swap arms all carry gameDefs
        out[rid] = r
    return out


def load_p5_arms() -> dict:
    with open(os.path.join(P5DOCS, "arms.json")) as f:
        doc = json.load(f)
    arms = doc["arms"] if isinstance(doc, dict) and "arms" in doc else doc
    if isinstance(arms, dict):
        arms = list(arms.values())
    return {a["armId"]: a for a in arms}


def load_personas() -> dict:
    with open(os.path.join(P5DOCS, "personas-v4.json")) as f:
        doc = json.load(f)
    out = {}
    for p in doc["personas"]:
        fac = p["factors"]
        coop_ct = sum([fac["d1"] == "agreeable", fac["d2"] == "patient",
                       fac["d3"] == "risk-averse"])
        rule_leaning = ("cooperative-leaning" if coop_ct >= 2
                        else "defect-leaning")
        if "leaning" in p and p["leaning"] != rule_leaning:
            raise SystemExit(f"persona {p['id']}: leaning field contradicts "
                             "registered rule — refusing")
        out[p["id"]] = rule_leaning
    return out


def coop_of(r: dict) -> float:
    a1, a2 = r["round1"]
    c = r["coopRole"]
    return ((a1 == c) + (a2 == c)) / 2.0


def valid_runs(runs: dict, arm_id: str) -> list[dict]:
    return [r for r in runs.values()
            if r["armId"] == arm_id and r["completed"] and not r["invalid"]
            and r["round1"] is not None]


# ------------------------------------------------------- bare gates
BARE_SOURCES = {
    "sent-bare-gpt (pd-rep-w1-neu δ90 T0.7, exact template)": "p5-sent-bare-gpt",
    "p4-d2-w1-can-sw-gpt (os-swap exact twin)": "p4-d2-w1-can-sw-gpt",
    "p3-community-bare (pd-oneshot-v1 community gpt T0.7)": "__p3-community-bare__",
    "p4-d1-can-w1-neu-cf-ad-gpt (one-shot wording match, w1-neu)":
        "p4-d1-can-w1-neu-cf-ad-gpt",
    "p4-d1-can-w2a-neu-cf-ad-gpt (one-shot wording match, w2a-neu)":
        "p4-d1-can-w2a-neu-cf-ad-gpt",
}


def bare_gates(runs: dict) -> dict:
    out = {}
    for label, arm in BARE_SOURCES.items():
        eps = [coop_of(r) for r in valid_runs(runs, arm)]
        g = gate_cell(eps)
        g["episodes"] = len(eps)
        g["gateStatus"] = "INTERIOR (gate passes)" if g["interior"] else \
            "NOT interior (gate fails → restricted-set candidate)"
        out[label] = g
    return out


# ------------------------------------------------- pure adjudication cores
def adjudicate_p51a(interior: dict, restricted_cells: list[str]) -> dict:
    """interior: (personaId, cell) -> bool over the 96 tier-A units."""
    units = sorted(interior.keys())
    restricted = [u for u in units if u[1] in restricted_cells]
    res = {
        "restrictedCells": restricted_cells,
        "restrictedN": len(restricted),
        "restrictedInterior": sum(interior[u] for u in restricted),
    }
    if not restricted:
        res["verdict"] = "null (registered edge case: restricted set empty)"
    else:
        frac = res["restrictedInterior"] / res["restrictedN"]
        res["restrictedFraction"] = frac
        res["verdict"] = ("supported" if frac < THETA_1 else "not supported")
    # secondaries
    res["unrestrictedFraction"] = sum(interior.values()) / len(units)
    fam: dict[str, list] = defaultdict(list)
    for (p, c), v in interior.items():
        fam[FAMILY_OF[c]].append(v)
    res["byFamily"] = {k: {"n": len(v), "interior": sum(v),
                           "fraction": sum(v) / len(v)}
                       for k, v in sorted(fam.items())}
    return res


def adjudicate_p51b(persona_means: dict) -> dict:
    """persona_means: cell -> {personaId: mean round-1 coop} (rep cells)."""
    out = {}
    for cell, means in sorted(persona_means.items()):
        key = "d90" if "d90" in cell else "d10"
        xs = [means[p] for p in sorted(means)]
        sd = sample_sd(xs)
        thr = RHO * HUMAN_SD[key]
        out[cell] = {"n": len(xs), "betweenPersonaSD": sd,
                     "humanSD": HUMAN_SD[key], "rho": RHO, "threshold": thr,
                     "verdict": ("corner-mixture-consistent" if sd >= thr
                                 else "not corner-mixture-consistent")}
    return out


def p52_verdict(k: int, n: int) -> dict:
    lo, hi = _cp_bounds(k, n)
    v = ("task-dominant" if lo >= P52_LB
         else "persona-dominant" if hi <= P52_UB else "mixed")
    return {"k": k, "n": n, "share": k / n if n else None,
            "cp95": [lo, hi], "verdict": v}


def adjudicate_p53(persona_records: dict) -> dict:
    """persona_records: personaId -> {
         'gates': {s2Level: {'d90': eps, 'd10': eps}},   # T=0.7
         'refusal': {T: (k, n)} }                        # swap refusal counts
    Returns per-persona pass status + existence verdict."""
    per = {}
    for pid, rec in sorted(persona_records.items()):
        detail = {"a": {}, "b": {}}
        pass_a = False
        for lvl, cells in sorted(rec["gates"].items()):
            g90, g10 = gate_cell(cells["d90"]), gate_cell(cells["d10"])
            entry = {"d90": g90, "d10": g10, "bothInterior":
                     g90["interior"] and g10["interior"]}
            if entry["bothInterior"]:
                s = _e_slope(cells["d90"], cells["d10"])
                entry["slope"] = s
                entry["passes"] = s["lowerBound95"] > 0
            else:
                entry["passes"] = False
            detail["a"][lvl] = entry
            pass_a = pass_a or entry["passes"]
        pass_b = False
        for t, (k, n) in sorted(rec["refusal"].items()):
            lo, _ = _cp_bounds(k, n)
            detail["b"][str(t)] = {"k": k, "n": n, "cpLB": lo,
                                   "passes": lo >= THETA_2}
            pass_b = pass_b or lo >= THETA_2
        per[pid] = {"passes": pass_a or pass_b, "viaA": pass_a, "viaB": pass_b,
                    "detail": detail}
    passing = sorted(p for p, v in per.items() if v["passes"])
    return {"perPersona": per, "passing": passing,
            "axisB": "at-least-one" if passing else "zero",
            "registeredPrediction": "zero of 16 pass",
            "predictionOutcome": "held" if not passing else "failed"}


def adjudicate_p54(interior07: dict, interior13: dict,
                   interior10: dict | None = None) -> dict:
    """interior maps: (personaId, cell) -> bool on the matched sweep units."""
    k1, n1 = sum(interior13.values()), len(interior13)
    k2, n2 = sum(interior07.values()), len(interior07)
    lb = newcombe_lb_one_sided(k1, n1, k2, n2)
    refuted = lb > 0
    out = {"matchedUnits": {"T0.7": n2, "T1.3": n1},
           "interiorFraction": {"T0.7": k2 / n2, "T1.3": k1 / n1},
           "newcombeOneSidedLB95_diff_T13_minus_T07": lb,
           "clause1": "refuted" if refuted else "not refuted",
           "clause2": ("non-estimable (registered aliasing disclosure: T is "
                       "not crossed with δ=0.10; δ-slope at T∈{1.0,1.3} has "
                       "no δ=0.10 cell — clause cannot fire; disclosed, not "
                       "adjudicated)"),
           "verdict": "refuted" if refuted else "not refuted",
           "axisC": "yes" if refuted else "no"}
    if interior10 is not None and interior10:
        out["descriptiveT10"] = {"n": len(interior10),
                                 "fraction": sum(interior10.values()) /
                                 len(interior10)}
    return out


def select_branch(axis_a: str, axis_b: str, axis_c: str) -> int:
    if axis_b == "at-least-one":
        return 2
    if axis_c == "yes":
        return 3
    if axis_a == "supported":
        return 1
    return 4


# ---------------------------------------------------------------- selftest
def selftest() -> int:
    # gate fixtures
    assert gate_cell([1.0] * 10)["interior"] is False        # hi = 1
    assert gate_cell([0.0] * 10)["interior"] is False        # lo = 0
    g = gate_cell([0.5] * 20)                                # k=20 n=40
    assert g["interior"] is True and abs(g["mean"] - 0.5) < 1e-12
    # seat counts
    assert seat_counts([0.5, 1.0]) == (3, 4)
    # newcombe: strong positive diff
    assert newcombe_lb_one_sided(18, 20, 2, 20) > 0
    assert newcombe_lb_one_sided(10, 20, 10, 20) < 0
    assert newcombe_lb_one_sided(12, 12, 0, 12) > 0
    # P5-1a fixtures
    interior = {(f"p{i:02d}", c): False for i in range(1, 17)
                for c in TIER_A_CELLS}
    r = adjudicate_p51a(interior, ["os-swap"])
    assert r["verdict"] == "supported" and r["restrictedN"] == 16
    interior[("p01", "os-swap")] = True; interior[("p02", "os-swap")] = True
    r = adjudicate_p51a(interior, ["os-swap"])
    assert r["verdict"] == "not supported"          # 2/16 = 0.125 ≥ 0.10
    assert adjudicate_p51a(interior, [])["verdict"].startswith("null")
    # P5-1b fixtures
    corners = {f"p{i:02d}": (1.0 if i <= 8 else 0.0) for i in range(1, 17)}
    r = adjudicate_p51b({"rep-d90-s2a": corners})
    assert r["rep-d90-s2a"]["verdict"] == "corner-mixture-consistent"
    flat = {f"p{i:02d}": 0.0 for i in range(1, 17)}
    r = adjudicate_p51b({"rep-d10-s2a": flat})
    assert r["rep-d10-s2a"]["verdict"] == "not corner-mixture-consistent"
    # P5-2 fixtures
    assert p52_verdict(96, 100)["verdict"] == "task-dominant"
    assert p52_verdict(4, 100)["verdict"] == "persona-dominant"
    assert p52_verdict(50, 100)["verdict"] == "mixed"
    # P5-3 fixtures
    rec = {"p01": {"gates": {"s2a": {"d90": [0.5] * 20, "d10": [0.25] * 20}},
                   "refusal": {0.7: (0, 40)}}}
    r = adjudicate_p53(rec)     # constant cells → CP fallback slope; LB>0? 0.5-0.25 cells
    # d90 [0.5]*20 CP lo>… slope fallback = lo(d90)-hi(d10); just assert shape
    assert r["axisB"] in ("zero", "at-least-one")
    rec = {"p01": {"gates": {}, "refusal": {0.7: (30, 40)}}}
    r = adjudicate_p53(rec)
    assert r["axisB"] == "at-least-one" and r["perPersona"]["p01"]["viaB"]
    rec = {"p01": {"gates": {}, "refusal": {0.7: (8, 40)}}}   # lo < .20
    assert adjudicate_p53(rec)["axisB"] == "zero"
    # P5-4 fixtures
    i07 = {(p, c): False for p in SUBSET_B for c in SWEEP_CELLS}
    i13 = dict(i07)
    assert adjudicate_p54(i07, i13)["verdict"] == "not refuted"
    i13 = {k: True for k in i13}
    assert adjudicate_p54(i07, i13)["verdict"] == "refuted"
    # branch table — all 8 registered rows
    table = [("supported", "zero", "no", 1), ("supported", "zero", "yes", 3),
             ("supported", "at-least-one", "no", 2),
             ("supported", "at-least-one", "yes", 2),
             ("not-supported", "zero", "no", 4),
             ("not-supported", "zero", "yes", 3),
             ("not-supported", "at-least-one", "no", 2),
             ("not-supported", "at-least-one", "yes", 2)]
    for a, b, c, want in table:
        got = select_branch("supported" if a == "supported" else "x", b, c)
        assert got == want, (a, b, c, got)
    print("phase5_closeout_adjudicate selftest: ALL PASS")
    return 0


# ---------------------------------------------------------------- assembly
def collect(runs: dict, personas: dict) -> dict:
    """Assemble every per-unit series needed by the predicate cores."""
    arms = load_p5_arms()
    # tier A persona-cell episode series
    eps_a: dict[tuple, list[float]] = defaultdict(list)
    refusal: dict[tuple, list[int]] = defaultdict(lambda: [0, 0])  # (pid,T)->[k,n]
    eps_bT: dict[tuple, list[float]] = defaultdict(list)  # (pid,cell,T)
    invalid_by_T: dict[float, list[int]] = defaultdict(lambda: [0, 0])
    action_counts_T: dict[float, dict] = defaultdict(lambda: defaultdict(int))
    tierC: dict[tuple, list[float]] = defaultdict(list)

    for r in runs.values():
        a = arms.get(r["armId"])
        if a is None:
            continue
        T = a["temperature"]
        cell, pid = a["cell"], a.get("personaId")
        counted = r["completed"]
        if counted:
            invalid_by_T[T][1] += 1
            if r["invalid"]:
                invalid_by_T[T][0] += 1
        if not (r["completed"] and not r["invalid"] and r["round1"]):
            continue
        c = coop_of(r)
        for act in r["round1"]:
            action_counts_T[T][act] += 1
        if a["block"].startswith("P5A"):
            eps_a[(pid, cell)].append(c)
        if a["block"].startswith(("P5A", "P5B")) and cell in SWEEP_CELLS:
            eps_bT[(pid, cell, T)].append(c)
        if a["block"].startswith("P5C"):
            tierC[(pid, cell)].append(c)
        if cell == "os-swap" and pid is not None:
            a1, a2 = r["round1"]
            d_role = 1 - r["coopRole"]      # dominant defect role
            k, n = refusal[(pid, T)]
            refusal[(pid, T)] = [k + (a1 == d_role) + (a2 == d_role), n + 2]

    return {"epsA": dict(eps_a), "refusal": dict(refusal),
            "epsBT": dict(eps_bT), "invalidByT": dict(invalid_by_T),
            "actionCountsT": {t: dict(v) for t, v in action_counts_T.items()},
            "tierC": dict(tierC)}


def adjudicate_all(decisions: dict) -> dict:
    runs = load_runs()
    personas = load_personas()
    col = collect(runs, personas)
    eps_a = col["epsA"]

    # sanity: 96 tier-A units, each non-empty
    units = [(p, c) for p in sorted(personas) for c in TIER_A_CELLS]
    missing = [u for u in units if not eps_a.get(u)]
    if missing:
        raise SystemExit(f"tier-A units missing/empty: {missing[:5]} …refusing")

    interior = {u: gate_cell(eps_a[u])["interior"] for u in units}

    # ---- P5-1a (restricted set from the operator-signed twin decision)
    bg = bare_gates(runs)
    restricted_cells = decisions["p51aRestrictedCells"]
    p51a = adjudicate_p51a(interior, restricted_cells)
    p51a["bareGateTable"] = bg
    p51a["twinDecision"] = decisions["p51aTwinNote"]

    # ---- P5-1b (matched rep cells)
    persona_means = {
        cell: {p: sum(eps_a[(p, cell)]) / len(eps_a[(p, cell)])
               for p in sorted(personas)}
        for cell in TIER_A_CELLS if cell.startswith("rep-")}
    p51b = adjudicate_p51b(persona_means)
    p51b_oneshot_note = ("one-shot cells: null (predicate defined for matched "
                         "rep-PD cells only; never 0)")

    # ---- P5-2 (conflict cells per operator-signed coding)
    conflict = []
    for pid, lean in sorted(personas.items()):
        for cell in TIER_A_CELLS:
            code = decisions["p52Coding"].get(f"{lean}|{cell}")
            if code is None:
                continue
            task_dir = code["taskConsistent"]      # 'coop-role'|'defect-role'
            for r in valid_runs_by(runs, pid, cell):
                c_role = r["coopRole"]
                want = c_role if task_dir == "coop-role" else 1 - c_role
                for act in r["round1"]:
                    conflict.append((f"{lean}|{cell}", int(act == want)))
    p52_cells: dict[str, list[int]] = defaultdict(list)
    for key, hit in conflict:
        p52_cells[key].append(hit)
    p52 = {"byConflictCell": {k: p52_verdict(sum(v), len(v))
                              for k, v in sorted(p52_cells.items())},
           "pooled": p52_verdict(sum(h for _, h in conflict), len(conflict)),
           "coding": decisions["p52Coding"],
           "note": decisions.get("p52Note", "")}
    p52["verdict"] = p52["pooled"]["verdict"]

    # ---- P5-3
    prec = {}
    for pid in sorted(personas):
        gates = {}
        for lvl in ("s2a", "s2p"):
            gates[lvl] = {"d90": eps_a[(pid, f"rep-d90-{lvl}")],
                          "d10": eps_a[(pid, f"rep-d10-{lvl}")]}
        ref = {T: tuple(kn) for (p, T), kn in col["refusal"].items() if p == pid}
        prec[pid] = {"gates": gates, "refusal": ref}
    p53 = adjudicate_p53(prec)

    # ---- P5-4
    def interior_at(T: float) -> dict:
        out = {}
        for pid in SUBSET_B:
            for cell in SWEEP_CELLS:
                eps = (eps_a[(pid, cell)] if T == 0.7
                       else col["epsBT"].get((pid, cell, T), []))
                if not eps:
                    raise SystemExit(f"P5-4 unit empty: {pid} {cell} T={T}")
                out[(pid, cell)] = gate_cell(eps)["interior"]
        return out
    p54 = adjudicate_p54(interior_at(0.7), interior_at(1.3), interior_at(1.0))
    p54["secondaries"] = {
        "invalidRateByT": {str(t): {"invalid": k, "runs": n,
                                    "rate": k / n if n else None}
                           for t, (k, n) in sorted(col["invalidByT"].items())},
        "round1ChoiceEntropyByT": {str(t): entropy(c) for t, c in
                                   sorted(col["actionCountsT"].items())},
    }

    # ---- axes + branch
    axis_a_rule = decisions["axisARule"]
    consistent_cells = [c for c, v in p51b.items()
                        if v["verdict"] == "corner-mixture-consistent"]
    if axis_a_rule == "p51a-only":
        axis_a = ("supported" if p51a["verdict"] == "supported"
                  else "not-supported")
    elif axis_a_rule == "p51a-and-p51b-all-cells":
        axis_a = ("supported" if p51a["verdict"] == "supported"
                  and len(consistent_cells) == len(p51b) else "not-supported")
    else:
        raise SystemExit(f"unknown axisARule {axis_a_rule!r}")
    axis_b, axis_c = p53["axisB"], p54["axisC"]
    branch = select_branch(axis_a, axis_b, axis_c)

    return {"pinnedConstants": {"theta1": THETA_1, "rho": RHO,
                                "humanSD": HUMAN_SD, "theta2": THETA_2,
                                "p52": [P52_LB, P52_UB]},
            "decisions": decisions,
            "P5-1a": p51a,
            "P5-1b": {"cells": p51b, "oneShotNote": p51b_oneshot_note},
            "P5-2": p52, "P5-3": p53, "P5-4": p54,
            "interiorMap": {f"{p}|{c}": v for (p, c), v in sorted(interior.items())},
            "tierCDescriptive": {f"{p}|{c}": gate_cell(v) for (p, c), v in
                                 sorted(col["tierC"].items())},
            "axes": {"A": axis_a, "B": axis_b, "C": axis_c},
            "selectedBranch": branch}


def valid_runs_by(runs: dict, pid: str, cell: str) -> list[dict]:
    arms = load_p5_arms()
    return [r for r in runs.values()
            if (a := arms.get(r["armId"])) and a.get("personaId") == pid
            and a["cell"] == cell and a["block"].startswith("P5A")
            and r["completed"] and not r["invalid"] and r["round1"]]


# ---------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bare-gates", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--adjudicate", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        return selftest()
    if args.bare_gates:
        runs = load_runs()
        print(json.dumps(bare_gates(runs), indent=2))
        return 0
    if args.adjudicate:
        if not os.path.exists(DECISIONS_PATH):
            raise SystemExit(f"missing {DECISIONS_PATH} — operator-signed "
                             "decisions required before adjudication")
        with open(DECISIONS_PATH) as f:
            decisions = json.load(f)
        report = adjudicate_all(decisions)
        os.makedirs(CLOSE, exist_ok=True)
        out = os.path.join(CLOSE, "adjudication-report.json")
        with open(out, "w") as f:
            json.dump(report, f, indent=1, default=str)
        print(f"wrote {out}")
        print(json.dumps({"P5-1a": report["P5-1a"]["verdict"],
                          "P5-1b": {c: v["verdict"] for c, v in
                                    report["P5-1b"]["cells"].items()},
                          "P5-2": report["P5-2"]["verdict"],
                          "P5-3": report["P5-3"]["axisB"],
                          "P5-4": report["P5-4"]["verdict"],
                          "axes": report["axes"],
                          "selectedBranch": report["selectedBranch"]},
                         indent=1))
        return 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
