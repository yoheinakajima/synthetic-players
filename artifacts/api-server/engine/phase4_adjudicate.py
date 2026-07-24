"""Phase 4 per-block adjudication + integrity scan — read-only, zero LLM calls.

Reads the engine event store (sqlite, mode=ro) and the sealed docs. Never
writes to any engine database; outputs go to docs/phase4/ (reports) and
stdout. Verdict-grade adjudication for the paper happens again in the step-8
full replay pass; these are the registered interim per-block reports.

Modes:
  --scan BLOCK       integrity scan: returned model identifiers vs sealed
                     expectation, finish_reason == stop (case-insensitive;
                     Gemini reports the enum name 'STOP'), retries, invalid
                     trials (both escalated to ALERT b inside sentinel cells),
                     episode coverage vs schedule, X2 horizon parity.
  --sentinel K       per-cell fingerprints for check K. K=0 writes the sealed
                     baseline (docs/phase4/sentinel-baseline.json + .md);
                     K>0 evaluates frozen alert rule (c) against the baseline.
  --x2-screening     rung means (interior rungs from Phase 4 events, ladder
                     endpoints from the sealed Phase 3 X1 runs), adjacent
                     gaps, frozen candidate rule, minimal-pair selection.
                     Writes docs/phase4/x2-screening-report.{json,md}.

Run:  cd artifacts/api-server && uv run python engine/phase4_adjudicate.py --scan X2-screening
"""
from __future__ import annotations

import json
import os
import sqlite3
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from strategies import mulberry32  # noqa: E402

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.normpath(os.path.join(_HERE, "..", "..", ".."))
DB_PATH = os.path.join(_HERE, "data", "engine.db")
DOCS = os.path.join(REPO_ROOT, "docs", "phase4")
ARMS_PATH = os.path.join(DOCS, "arms.json")
SCHEDULE_PATH = os.path.join(DOCS, "execution-schedule.json")
BASELINE_JSON = os.path.join(DOCS, "sentinel-baseline.json")
API = "http://localhost:80/api"

# Sealed expected returned-model identifiers (predicates §subjects; provider packet)
EXPECTED_MODEL = {
    "gpt-4.1": "gpt-4.1-2025-04-14",
    "gemini-2.5-flash": "gemini-2.5-flash",
}
SENTINEL_ARMS = ["p4-sent-v1", "p4-sent-v2a", "p4-sent-fallback"]
SUBJECT_MODELS = ["gpt-4.1", "gemini-2.5-flash"]

# X1 ladder endpoints (sealed Phase 3 batches; d90, seeds 1–10 subset)
# Sealed Phase 3 X1 endpoint arms (x2-diff-packet.md: F0 ≡ v1, F6 ≡ v2a;
# δ=.90, gpt-4.1 self-play, X1 environment seeds 1–10). Identified in the
# event store by game-object attributes — the store carries no batch labels.
X1_V1_TEMPLATE = "pd-repeated-v1"
X1_V2A_TEMPLATE = "pd-repeated-v2a"


def draw_horizon(seed: int, delta_pct: int) -> tuple[int, bool]:
    rng = mulberry32((seed ^ 0x54524D) & 0xFFFFFFFF)
    delta = delta_pct / 100
    rounds = 1
    while rng() < delta:
        rounds += 1
        if rounds >= 120:
            return 120, True
    return rounds, False


# ── event-store loading ──────────────────────────────────────────────────────

def load_phase4_runs() -> dict[str, dict]:
    """run_id → {armId, block, episodeIndex, sentinelCheckIndex, model,
    seed, rounds {n: (a1, a2)}, responded [...], invalid, completed}."""
    db = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    runs: dict[str, dict] = {}
    q = ("SELECT run_id, type, payload FROM events WHERE type IN ("
         "'llm.requested','llm.responded','round.played','trial.invalidated','run.completed')")
    for run_id, typ, payload in db.execute(q):
        p = json.loads(payload)
        r = runs.setdefault(run_id, {"rounds": {}, "responded": [],
                                     "invalid": False, "completed": False})
        if typ == "llm.requested" and "armId" in p:
            r.update(armId=p["armId"], block=p.get("block"),
                     episodeIndex=p.get("episodeIndex"),
                     sentinelCheckIndex=p.get("sentinelCheckIndex"),
                     model=p.get("model"), engineCommit=p.get("engineCommit"))
            if p.get("seed") is not None:
                r["seed"] = p["seed"]  # authoritative scheduled seed (requested-side)
        elif typ == "llm.responded":
            if r.get("seed") is None:
                r["seed"] = p.get("seed")  # legacy fallback (phase-3 event shape)
            r["responded"].append({
                "seat": p.get("seat"), "round": p.get("roundNumber"),
                "attempt": p.get("attempt"), "model": p.get("model"),
                "finish": p.get("finish_reason"),
            })
        elif typ == "round.played":
            r["rounds"][p["roundNumber"]] = (p["player1Action"], p["player2Action"])
        elif typ == "trial.invalidated":
            r["invalid"] = True
        elif typ == "run.completed":
            r["completed"] = True
    db.close()
    return {rid: r for rid, r in runs.items() if "armId" in r}


def arms() -> dict[str, dict]:
    return {a["armId"]: a for a in json.load(open(ARMS_PATH))["arms"]}


# ── integrity scan ───────────────────────────────────────────────────────────

def scan(block: str) -> int:
    runs = load_phase4_runs()
    store = arms()
    sel = {rid: r for rid, r in runs.items()
           if (r.get("block") == block if block != "sentinel" else r.get("sentinelCheckIndex") is not None)}
    anomalies: list[str] = []
    retried = invalid = 0
    for rid, r in sel.items():
        exp = EXPECTED_MODEL.get(r["model"])
        in_sentinel = r.get("sentinelCheckIndex") is not None
        for resp in r["responded"]:
            if resp["model"] != exp:
                anomalies.append(f"{rid}: returned model {resp['model']!r} != sealed {exp!r} (ALERT a)")
            # case-insensitive: OpenAI reports 'stop', Gemini the enum name 'STOP'
            if (resp["finish"] or "").lower() != "stop":
                anomalies.append(f"{rid}: finish_reason {resp['finish']!r} != stop"
                                 + (" (ALERT b: sentinel cell)" if in_sentinel else ""))
            if resp["attempt"]:  # attempt is 0-based; >0 means a retry fired
                retried += 1
                if in_sentinel:
                    anomalies.append(f"{rid}: retry (attempt {resp['attempt']}) in sentinel cell (ALERT b)")
        if r["invalid"]:
            invalid += 1
            if in_sentinel:
                anomalies.append(f"{rid}: invalidated trial in sentinel cell (ALERT b)")
        ec = r.get("engineCommit") or {}
        if ec.get("dirty") is not False:
            anomalies.append(f"{rid}: engineCommit dirty flag {ec}")
        arm = store.get(r["armId"])
        if arm and r.get("block") == "X2-screening":
            want, trunc = draw_horizon(r["seed"], int(arm["deltaPct"]))
            got = len(r["rounds"]) if r["completed"] else None
            if not r["invalid"] and got != want:
                anomalies.append(f"{rid}: realized rounds {got} != drawn horizon {want} (seed {r['seed']})")
        if arm and r.get("block") in ("D1", "D2", "D3") and not r["invalid"] and len(r["rounds"]) != 1:
            anomalies.append(f"{rid}: one-shot block with {len(r['rounds'])} rounds")

    # coverage vs the sealed schedule
    if block in ("X2-screening", "D1", "D2", "D3", "E", "F"):
        sched = json.load(open(SCHEDULE_PATH))
        eps = next(b for b in sched["blocks"] if b["block"] == block)["episodes"]
        seen = {(r["armId"], r.get("episodeIndex")) for r in sel.values()}
        missing = [(e["armId"], e["ep"]) for e in eps if (e["armId"], e["ep"]) not in seen]
        dupes = len(sel) - len(seen)
        if missing:
            anomalies.append(f"coverage: {len(missing)} scheduled episodes missing (first: {missing[:4]})")
        if dupes:
            anomalies.append(f"coverage: {dupes} duplicate (armId, episode) run records")

    print(json.dumps({
        "block": block, "runs": len(sel), "retriedCalls": retried,
        "invalidTrials": invalid, "anomalies": anomalies,
    }, indent=1))
    return 1 if anomalies else 0


# ── sentinel fingerprints (frozen alert rule c) ──────────────────────────────

FINGERPRINT_DEF = (
    "cell = sentinel arm × subject model; episode value = seat-1 round-1 action "
    "index; modal action = most frequent episode value across the cell's 10 "
    "episodes (tie → lower action index); fingerprint = (modalAction, count of "
    "episodes whose value equals it). Rule (c) compares counts: alert iff "
    "|count_K − count_baseline| ≥ 3. Modal-action flips at similar counts are "
    "disclosed as observations (the frozen rule is count-based). Seat-2 "
    "distributions are archived alongside for context."
)


def sentinel(k: int) -> int:
    runs = load_phase4_runs()
    cells: dict[str, dict] = {}
    for rid, r in runs.items():
        if r.get("sentinelCheckIndex") != k or r["invalid"]:
            continue
        key = f"{r['armId']}|{r['model']}"
        c = cells.setdefault(key, {"seat1": [], "seat2": [], "runIds": []})
        a1, a2 = r["rounds"].get(1, (None, None))
        c["seat1"].append(a1)
        c["seat2"].append(a2)
        c["runIds"].append(rid)

    fp: dict[str, dict] = {}
    for arm_id in SENTINEL_ARMS:
        for model in SUBJECT_MODELS:
            key = f"{arm_id}|{model}"
            c = cells.get(key)
            if c is None or len(c["seat1"]) != 10 or any(a is None for a in c["seat1"]):
                print(f"INCOMPLETE cell {key}: {0 if c is None else len(c['seat1'])}/10 episodes")
                return 1
            counts: dict[int, int] = {}
            for a in c["seat1"]:
                counts[a] = counts.get(a, 0) + 1
            modal = min([a for a in counts if counts[a] == max(counts.values())])
            fp[key] = {
                "modalAction": modal, "count": counts[modal],
                "seat1Counts": counts,
                "seat2Counts": {str(a): c["seat2"].count(a) for a in set(c["seat2"])},
                "runIds": c["runIds"],
            }

    if k == 0:
        if os.path.exists(BASELINE_JSON):
            print(f"REFUSING to overwrite sealed baseline {BASELINE_JSON} — "
                  "the check-0 baseline is write-once; changing it requires a "
                  "registered amendment (delete the file only under one)")
            return 1
        doc = {
            "definition": FINGERPRINT_DEF, "checkIndex": 0,
            "sealedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "cells": fp,
        }
        with open(BASELINE_JSON, "w") as f:
            json.dump(doc, f, indent=1)
        lines = ["# Phase 4 sentinel baseline (check 0) — sealed on write", "",
                 f"Sealed at {doc['sealedAt']}. {FINGERPRINT_DEF}", "",
                 "| cell | modal action | count/10 | seat-1 distribution |", "|---|---|---|---|"]
        for key, v in fp.items():
            lines.append(f"| {key} | {v['modalAction']} | {v['count']} | {v['seat1Counts']} |")
        with open(os.path.join(DOCS, "sentinel-baseline.md"), "w") as f:
            f.write("\n".join(lines) + "\n")
        print(json.dumps({"baselineSealed": True, "cells": {k2: {"modal": v["modalAction"], "count": v["count"]} for k2, v in fp.items()}}, indent=1))
        return 0

    base = json.load(open(BASELINE_JSON))["cells"]
    alerts, notes = [], []
    for key, v in fp.items():
        b = base[key]
        if abs(v["count"] - b["count"]) >= 3:
            alerts.append(f"{key}: count {v['count']} vs baseline {b['count']} (Δ≥3 — ALERT c)")
        if v["modalAction"] != b["modalAction"]:
            notes.append(f"{key}: modal action flipped {b['modalAction']} → {v['modalAction']} "
                         f"(counts {b['count']} → {v['count']}; disclosed, not an alert under the frozen rule)")
    print(json.dumps({"checkIndex": k, "alerts": alerts, "notes": notes,
                      "cells": {k2: {"modal": v["modalAction"], "count": v["count"]} for k2, v in fp.items()}}, indent=1))
    return 2 if alerts else 0


# ── X2 screening (frozen candidate rule) ─────────────────────────────────────

def _x1_endpoint_eps(template_id: str) -> tuple[dict[int, float], dict[int, int], dict[int, list[str]]]:
    """Per-seed (1–10) round-1 cooperation share for a sealed Phase 3 X1
    endpoint, re-derived from the event store ALONE: runs identified by
    game-object attributes (promptId, deltaPct=90, gpt-4.1, llm-subject
    self-play, seed 1–10) — the store carries no batch labels. Phase 3
    contains duplicate batches for some endpoint seeds; a duplicate is
    accepted ONLY if every copy agrees exactly on horizon and round-1
    actions (agreement is checked, never assumed, and disclosed); any
    disagreement refuses adjudication — no discretionary pick.
    Returns (eps, horizons, duplicates)."""
    db = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    games = list(db.execute(
        """SELECT run_id, CAST(json_extract(payload,'$.object.data.seed') AS INTEGER),
                  CAST(json_extract(payload,'$.object.data.numRounds') AS INTEGER)
           FROM events WHERE type='object.created'
             AND json_extract(payload,'$.object.type')='game'
             AND json_extract(payload,'$.object.data.llm.promptId')=?
             AND json_extract(payload,'$.object.data.llm.deltaPct')=90.0
             AND json_extract(payload,'$.object.data.llm.model')='gpt-4.1'
             AND json_extract(payload,'$.object.data.strategy1Slug')='llm-subject'
             AND json_extract(payload,'$.object.data.strategy2Slug')='llm-subject'
             AND json_extract(payload,'$.object.data.seed') BETWEEN 1 AND 10""",
        (template_id,)))
    per_seed: dict[int, list[tuple[str, int, int, int]]] = {}
    for rid, seed, nr in games:
        if not list(db.execute(
                "SELECT 1 FROM events WHERE run_id=? AND type='run.completed' LIMIT 1", (rid,))):
            raise SystemExit(f"X1 endpoint {template_id} seed {seed}: run {rid} "
                             f"has no run.completed — refusing")
        r1 = list(db.execute(
            """SELECT CAST(json_extract(payload,'$.player1Action') AS INTEGER),
                      CAST(json_extract(payload,'$.player2Action') AS INTEGER)
               FROM events WHERE run_id=? AND type='round.played'
                 AND json_extract(payload,'$.roundNumber')=1""", (rid,)))
        if len(r1) != 1:
            raise SystemExit(f"X1 endpoint {template_id} seed {seed}: run {rid} "
                             f"has {len(r1)} round-1 records — refusing")
        per_seed.setdefault(int(seed), []).append((rid, int(nr), r1[0][0], r1[0][1]))
    db.close()
    eps: dict[int, float] = {}
    horizons: dict[int, int] = {}
    dupes: dict[int, list[str]] = {}
    for seed, copies in sorted(per_seed.items()):
        if len({(nr, a1, a2) for _, nr, a1, a2 in copies}) != 1:
            raise SystemExit(f"X1 endpoint {template_id} seed {seed}: duplicate "
                             f"phase-3 runs DISAGREE ({copies}) — refusing")
        if len(copies) > 1:
            dupes[seed] = sorted(c[0] for c in copies)
        _, nr, a1, a2 = copies[0]
        eps[seed] = ((a1 == 0) + (a2 == 0)) / 2
        horizons[seed] = nr
    if sorted(eps) != list(range(1, 11)):
        raise SystemExit(f"X1 endpoint {template_id}: found {len(eps)}/10 seeds "
                         f"{sorted(eps)} — refusing")
    return eps, horizons, dupes


def x2_screening() -> int:
    runs = load_phase4_runs()
    rung_eps: dict[str, dict[int, float]] = {}
    excluded: list[str] = []
    for rid, r in runs.items():
        if r.get("block") != "X2-screening":
            continue
        if r["invalid"]:
            excluded.append(f"{r['armId']} seed {r['seed']}: invalid trial")
            continue
        a1, a2 = r["rounds"].get(1, (None, None))
        if a1 is None:
            excluded.append(f"{r['armId']} seed {r['seed']}: no round-1 record")
            continue
        rung_eps.setdefault(r["armId"], {})[r["seed"]] = ((a1 == 0) + (a2 == 0)) / 2

    v1, v1_h, v1_dup = _x1_endpoint_eps(X1_V1_TEMPLATE)
    v2a, v2a_h, v2a_dup = _x1_endpoint_eps(X1_V2A_TEMPLATE)
    if v1_h != v2a_h:
        raise SystemExit(f"endpoint horizon mismatch v1={v1_h} v2a={v2a_h} — "
                         f"matched-draw premise broken, refusing")

    def mean(d: dict[int, float]) -> float:
        return sum(d.values()) / len(d)

    means = {"v1": mean(v1), "v2a": mean(v2a)}
    ns = {"v1": len(v1), "v2a": len(v2a)}
    for rung, eps in sorted(rung_eps.items()):
        means[rung] = mean(eps)
        ns[rung] = len(eps)

    ladders = {
        "forward": ["v1"] + [f"p4-x2-f{i}" for i in range(1, 6)] + ["v2a"],
        "reverse": ["v2a"] + [f"p4-x2-r{i}" for i in range(1, 6)] + ["v1"],
    }
    gaps = []
    for ladder, order in ladders.items():
        for pos in range(1, 7):
            lo_r, hi_r = order[pos - 1], order[pos]
            if lo_r not in means or hi_r not in means:
                raise SystemExit(f"missing rung mean for {lo_r} or {hi_r}")
            delta = means[hi_r] - means[lo_r]
            # Sealed rung definitions (x2-diff-packet.md): Forward F_i = spans
            # 1..i applied; Reverse R_i = spans 1..i reverted. In BOTH ladders
            # the adjacent gap at position i therefore isolates span i.
            span = pos
            gaps.append({"ladder": ladder, "position": pos, "spanIndex": span,
                         "pair": [lo_r, hi_r], "delta": round(delta, 4), "absDelta": round(abs(delta), 4)})

    candidates = [g for g in gaps if g["absDelta"] >= 0.50]
    selection = None
    if candidates:
        # frozen: largest |Δ|; ties → lowest span index; forward before reverse
        best = sorted(candidates,
                      key=lambda g: (-g["absDelta"], g["spanIndex"], 0 if g["ladder"] == "forward" else 1))[0]
        pair = best["pair"]
        tmpl = {"v1": X1_V1_TEMPLATE, "v2a": X1_V2A_TEMPLATE}
        lo_t = tmpl.get(pair[0], pair[0].replace("p4-x2-", "pd-x2-"))
        hi_t = tmpl.get(pair[1], pair[1].replace("p4-x2-", "pd-x2-"))
        amendment = not (lo_t.startswith("pd-x2-") and hi_t.startswith("pd-x2-"))
        selection = {
            "gap": best, "confLoTemplate": lo_t, "confHiTemplate": hi_t,
            "orientation": "positive" if best["delta"] > 0 else "negative",
            "screenedDirection": f"E[Y|{pair[1]}] - E[Y|{pair[0]}] {'>' if best['delta'] > 0 else '<'} 0",
            "amendmentRequiredForResolution": amendment,
        }

    report = {
        "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "rule": "candidate iff some adjacent |Δ| ≥ 0.50; largest |Δ|; ties → lowest span index; forward before reverse (frozen, predicates.md)",
        "endpointSource": {
            "v1": X1_V1_TEMPLATE, "v2a": X1_V2A_TEMPLATE,
            "method": "re-derived from the event store alone via game-object attributes "
                      "(promptId, deltaPct=90, gpt-4.1, llm-subject self-play, seeds 1–10); "
                      "the store carries no batch labels",
            "matchedHorizons": {str(k): v for k, v in sorted(v1_h.items())},
            "duplicateEndpointRuns": {
                "v1": {str(k): v for k, v in sorted(v1_dup.items())},
                "v2a": {str(k): v for k, v in sorted(v2a_dup.items())},
                "rule": "duplicates accepted only on exact agreement of horizon + "
                        "round-1 actions; any disagreement refuses adjudication"}},
        "perSeed": {"v1": v1, "v2a": v2a,
                    **{r: dict(sorted(e.items())) for r, e in sorted(rung_eps.items())}},
        "rungMeans": {k: round(v, 4) for k, v in means.items()},
        "rungN": ns,
        "gaps": gaps,
        "excludedEpisodes": excluded,
        "candidate": bool(candidates),
        "selection": selection,
        "registeredNoCandidateOutcome": None if candidates else
            "no single dominant span at the 0.50 criterion — effect distributed (registered outcome; confirmation budget unspent)",
    }
    with open(os.path.join(DOCS, "x2-screening-report.json"), "w") as f:
        json.dump(report, f, indent=1)

    lines = ["# X2 screening report (interim, per registered rider: final verdicts in step 8)", "",
             f"Generated {report['generatedAt']}. {report['rule']}", "",
             "| rung | mean Y_ep | n |", "|---|---|---|"]
    for k in ladders["forward"] + [r for r in ladders["reverse"] if r not in ladders["forward"]]:
        if k in means:
            lines.append(f"| {k} | {means[k]:.4f} | {ns[k]} |")
    lines += ["", "| ladder | pos | span | pair | Δ |", "|---|---|---|---|---|"]
    for g in gaps:
        lines.append(f"| {g['ladder']} | {g['position']} | S{g['spanIndex']} | {g['pair'][0]} → {g['pair'][1]} | {g['delta']:+.4f} |")
    lines += ["", f"**Candidate:** {report['candidate']}"]
    if selection:
        lines += [f"Selected span S{selection['gap']['spanIndex']} ({selection['gap']['ladder']} ladder, "
                  f"|Δ| = {selection['gap']['absDelta']}); minimal pair {selection['confLoTemplate']} / "
                  f"{selection['confHiTemplate']}; screened direction: {selection['screenedDirection']}."]
        if selection["amendmentRequiredForResolution"]:
            lines += ["", "**NOTE:** selected pair includes a sealed Phase 3 endpoint template — the "
                          "pd-x2-* resolution family constraint requires a registered amendment before "
                          "confirmation can be dispatched."]
    else:
        lines += [report["registeredNoCandidateOutcome"]]
    if excluded:
        lines += ["", "Excluded episodes: " + "; ".join(excluded)]
    with open(os.path.join(DOCS, "x2-screening-report.md"), "w") as f:
        f.write("\n".join(lines) + "\n")

    print(json.dumps({k: report[k] for k in ("rungMeans", "candidate", "selection", "excludedEpisodes")}, indent=1))
    return 0


# ── Shared BCa machinery (frozen: predicates.md "Interval methods") ──────────
#
# BCa(seed) = bias-corrected accelerated bootstrap, 10,000 resamples over
# episodes, mulberry32 seed 20260801 (bit-identical engine PRNG). Procedural
# pins made BEFORE any D2/D3 data existed (disclosed in provenance-notes.md):
#   draw order    — per resample: groups in argument order, n index draws per
#                   group in position order; index = floor(u·n).
#   z0            — Φ⁻¹(#{θ*_b < θ̂}/B), strict inequality.
#   acceleration  — delete-one jackknife across all observations of all groups.
#   quantile rule — k = clamp(floor(α_adj·(B+1)), 1, B); k-th order statistic.
#   degenerate    — constant bootstrap distribution or infinite z0 → the claim's
#                   registered exact fallback (constant cells: exact comparison
#                   + CP bounds per cell, seat-level trials).
#   p for Holm    — CI inversion: smallest α at which the (1−α) BCa interval
#                   excludes 0 (bisection); under exact fallback, inversion of
#                   the conservative CP-difference interval (per-cell CP at
#                   1−α/2 each, Bonferroni).

BCA_SEED = 20260801
BCA_B = 10000


def _bca_fit(groups: list[list[float]], stat, seed: int = BCA_SEED, B: int = BCA_B):
    """One bootstrap pass. Returns (theta, sorted_boots, z0, a, degen|None).
    The fit is computed ONCE per claim; every endpoint/inversion reuses it, so
    the pinned mulberry32 stream is consumed exactly once per claim."""
    from scipy.stats import norm
    rng = mulberry32(seed & 0xFFFFFFFF)
    theta = stat(groups)
    boots = []
    for _ in range(B):
        res = [[g[int(rng() * len(g))] for _ in range(len(g))] for g in groups]
        boots.append(stat(res))
    sb = sorted(boots)
    if sb[0] == sb[-1]:
        return theta, sb, None, None, "degenerate bootstrap distribution"
    less = sum(1 for b in boots if b < theta)
    if less == 0 or less == B:
        return theta, sb, None, None, "z0 infinite (all resamples on one side)"
    z0 = float(norm.ppf(less / B))
    jk = []
    for gi, g in enumerate(groups):
        for i in range(len(g)):
            jg = [gg if gj != gi else g[:i] + g[i + 1:] for gj, gg in enumerate(groups)]
            jk.append(stat(jg))
    jbar = sum(jk) / len(jk)
    num = sum((jbar - v) ** 3 for v in jk)
    den = 6.0 * (sum((jbar - v) ** 2 for v in jk)) ** 1.5
    a = 0.0 if den == 0 else num / den
    return theta, sb, z0, a, None


def _bca_endpoint(sb: list[float], z0: float, a: float, al: float) -> float:
    from scipy.stats import norm
    z = float(norm.ppf(al))
    adj = float(norm.cdf(z0 + (z0 + z) / (1 - a * (z0 + z))))
    k = min(max(int(adj * (len(sb) + 1)), 1), len(sb))
    return sb[k - 1]


def _invert_p(excludes, floor: float = 0.0) -> float:
    """Smallest α at which the (1−α) interval excludes 0 (monotone; bisection).
    `floor` prevents overstating precision: bootstrap-based p is floored at
    1/(B+1) — the finest resolution 10k resamples can support."""
    if not excludes(0.9999):
        return 1.0
    lo_a, hi_a = 1e-9, 0.9999
    for _ in range(60):
        mid = (lo_a + hi_a) / 2
        if excludes(mid):
            hi_a = mid
        else:
            lo_a = mid
    return max(hi_a, floor)


def _bca_diff_claim(g_hi: list[float], g_lo: list[float], two_sided: bool) -> dict:
    """Difference-of-means claim: BCa CI + inversion p; registered exact
    fallback when either cell is constant (predicates.md 'Degenerate designs')."""
    stat = lambda gs: sum(gs[0]) / len(gs[0]) - sum(gs[1]) / len(gs[1])
    const_hi, const_lo = len(set(g_hi)) == 1, len(set(g_lo)) == 1
    est = stat([g_hi, g_lo])
    if const_hi or const_lo:
        from scipy.stats import beta

        def cp(g, cell_alpha):
            k = int(round(sum(g) * 2)); n = 2 * len(g)   # 2 seat trials/episode
            lo = 0.0 if k == 0 else float(beta.ppf(cell_alpha / 2, k, n - k + 1))
            hi = 1.0 if k == n else float(beta.ppf(1 - cell_alpha / 2, k + 1, n - k))
            return lo, hi

        def cons_interval(alpha):                        # Bonferroni: α/2 per cell
            (l1, h1), (l2, h2) = cp(g_hi, alpha / 2), cp(g_lo, alpha / 2)
            return l1 - h2, h1 - l2

        def excludes(alpha):
            l, h = cons_interval(alpha)
            return ((l > 0) or (h < 0)) if two_sided else (l > 0)

        lo95, hi95 = cons_interval(0.05)
        return {"method": "exact fallback (constant cell): exact diff + "
                          "CP-conservative interval (seat-level trials)",
                "estimate": est, "ci95": [lo95, hi95],
                "cellCP95": {"hi": cp(g_hi, 0.05), "lo": cp(g_lo, 0.05)},
                "constantCells": {"hi": const_hi, "lo": const_lo},
                "p": _invert_p(excludes)}
    theta, sb, z0, a, degen = _bca_fit([g_hi, g_lo], stat)
    if degen:
        raise SystemExit(f"BCa degenerate ({degen}) with non-constant cells — "
                         f"unregistered condition, refusing")

    def excludes(alpha):
        l = _bca_endpoint(sb, z0, a, alpha / 2)
        h = _bca_endpoint(sb, z0, a, 1 - alpha / 2)
        return ((l > 0) or (h < 0)) if two_sided else (l > 0)

    return {"method": "BCa(20260801), 10000 resamples", "estimate": theta,
            "ci95": [_bca_endpoint(sb, z0, a, 0.025), _bca_endpoint(sb, z0, a, 0.975)],
            "p": _invert_p(excludes, floor=1.0 / (BCA_B + 1))}


# ── D1 confirmatory analysis (frozen: predicates.md §Family D1) ──────────────
#
# Episode-level OLS of Y on all five factor main effects plus the registered
# interactions (M×W, W×L, M×L), HC3 robust covariance. Estimands are
# EQUAL-WEIGHT CELL-MEAN contrasts built mechanically from design rows —
# never hand-derived coefficient readings — so factor coding cannot bias them.
# Requires numpy+scipy at adjudication time only:
#   uv run --with numpy --with scipy python engine/phase4_adjudicate.py --d1

D1_M = ("can", "aff", "nva", "nvb")
D1_W = ("w1", "w2a")
D1_L = ("neu", "sem")
D1_O = ("cf", "df")
D1_P = ("ad", "pm")
# planned M contrasts (frozen): c1 = can vs aff; c2 = can vs ½(nva+nvb); c3 = nva vs nvb
D1_CONTRASTS = {
    "c1": {"can": 1.0, "aff": -1.0, "nva": 0.0, "nvb": 0.0},
    "c2": {"can": 1.0, "aff": 0.0, "nva": -0.5, "nvb": -0.5},
    "c3": {"can": 0.0, "aff": 0.0, "nva": 1.0, "nvb": -1.0},
}
_HALF = {"w1": -0.5, "w2a": 0.5, "neu": -0.5, "sem": 0.5,
         "cf": -0.5, "df": 0.5, "ad": -0.5, "pm": 0.5}


def d1_row(m: str, w: str, l: str, o: str, p: str) -> list[float]:
    """Design row: [1, c1, c2, c3, W, L, O, P, c1W, c2W, c3W, WL, c1L, c2L, c3L]."""
    c = [D1_CONTRASTS[k][m] for k in ("c1", "c2", "c3")]
    W, L, O, P = _HALF[w], _HALF[l], _HALF[o], _HALF[p]
    return [1.0, c[0], c[1], c[2], W, L, O, P,
            c[0] * W, c[1] * W, c[2] * W, W * L, c[0] * L, c[1] * L, c[2] * L]


def d1_parse_arm(arm_id: str) -> tuple[str, str, str, str, str, str] | None:
    """p4-d1-{M}-{W}-{L}-{O}-{P}-{gpt|cvx} → factors + family."""
    parts = arm_id.split("-")
    if len(parts) != 8 or parts[:2] != ["p4", "d1"]:
        return None
    _, _, m, w, l, o, p, fam = parts
    if (m in D1_M and w in D1_W and l in D1_L and o in D1_O and p in D1_P
            and fam in ("gpt", "cvx")):
        return m, w, l, o, p, fam
    return None


def _d1_estimand_rows():
    """Mechanical equal-weight cell-mean contrast vectors (frozen estimands)."""
    import itertools
    import numpy as np

    def mean_rows(cells):
        return np.mean([d1_row(*c) for c in cells], axis=0)

    rest = list(itertools.product(D1_L, D1_O, D1_P))
    # P4-D1-W: E[Y|w2a] − E[Y|w1], marginal over M,L,O,P
    l_w = (mean_rows([(m, "w2a", l, o, p) for m in D1_M for (l, o, p) in rest])
           - mean_rows([(m, "w1", l, o, p) for m in D1_M for (l, o, p) in rest]))
    # per-M W-effects (equal weight over L,O,P)
    w_eff = {m: (mean_rows([(m, "w2a", l, o, p) for (l, o, p) in rest])
                 - mean_rows([(m, "w1", l, o, p) for (l, o, p) in rest])) for m in D1_M}
    L_wm = np.array([sum(D1_CONTRASTS[c][m] * w_eff[m] for m in D1_M)
                     for c in ("c1", "c2", "c3")])
    # W-effect at L=sem minus at L=neu (equal weight over M,O,P)
    def w_eff_at(l):
        return (mean_rows([(m, "w2a", l, o, p) for m in D1_M for o in D1_O for p in D1_P])
                - mean_rows([(m, "w1", l, o, p) for m in D1_M for o in D1_O for p in D1_P]))
    l_wl = w_eff_at("sem") - w_eff_at("neu")
    # per-M L-effects (equal weight over W,O,P)
    def l_eff(m):
        return (mean_rows([(m, w, "sem", o, p) for w in D1_W for o in D1_O for p in D1_P])
                - mean_rows([(m, w, "neu", o, p) for w in D1_W for o in D1_O for p in D1_P]))
    L_ml = np.array([sum(D1_CONTRASTS[c][m] * l_eff(m) for m in D1_M)
                     for c in ("c1", "c2", "c3")])
    return {"P4-D1-W": l_w, "P4-D1-WM": L_wm, "P4-D1-WL": l_wl, "P4-D1-ML": L_ml}


def holm(pvals: dict[str, float]) -> dict[str, float]:
    """Holm step-down over the family; monotone, capped at 1."""
    m = len(pvals)
    order = sorted(pvals, key=lambda k: pvals[k])
    out, running = {}, 0.0
    for i, k in enumerate(order):
        running = max(running, (m - i) * pvals[k])
        out[k] = min(1.0, running)
    return out


def _cp_bounds(k: int, n: int) -> tuple[float, float]:
    from scipy.stats import beta
    lo = 0.0 if k == 0 else float(beta.ppf(0.025, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(0.975, k + 1, n - k))
    return lo, hi


def d1() -> int:
    import numpy as np
    from scipy import stats as sps
    import scipy

    runs = load_phase4_runs()
    fams: dict[str, dict] = {"gpt": {"rows": [], "y": [], "cells": {}, "invalid": [],
                                     "cellCoop": {}},
                             "cvx": {"rows": [], "y": [], "cells": {}, "invalid": [],
                                     "cellCoop": {}}}
    for rid, r in runs.items():
        if r.get("block") != "D1":
            continue
        parsed = d1_parse_arm(r.get("armId", ""))
        if parsed is None:
            print(f"UNPARSEABLE D1 armId {r.get('armId')!r} ({rid}) — refusing to adjudicate")
            return 1
        m, w, l, o, p, fam = parsed
        F = fams[fam]
        cell = f"{m}-{w}-{l}-{o}-{p}"
        if r["invalid"]:
            F["invalid"].append(f"{cell} seed {r.get('seed')}")
            continue
        if not r["completed"] or 1 not in r["rounds"]:
            F["invalid"].append(f"{cell} seed {r.get('seed')} (incomplete run)")
            continue
        a1, a2 = r["rounds"][1]
        y = ((a1 == 0) + (a2 == 0)) / 2.0  # action index 0 = cooperate ROLE (aligned maps in D1)
        F["rows"].append(d1_row(m, w, l, o, p))
        F["y"].append(y)
        F["cells"].setdefault(cell, []).append(y)
        cc = F["cellCoop"].setdefault(cell, [0, 0])
        cc[0] += int(a1 == 0) + int(a2 == 0)
        cc[1] += 2

    est_rows = _d1_estimand_rows()
    report: dict = {
        "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "frozenSpec": "predicates.md §Family D1 — episode-level OLS, five main effects + M×W, W×L, M×L; HC3; equal-weight cell-mean estimands; Holm m=4 per family",
        "versions": {"numpy": np.__version__, "scipy": scipy.__version__},
        "families": {},
    }
    md = ["# D1 interim adjudication (final verdicts in step 8)", "",
          f"Generated {report['generatedAt']}. numpy {np.__version__}, scipy {scipy.__version__}.", ""]

    for fam, role in (("gpt", "primary"), ("cvx", "secondary (cross-vendor mirror)")):
        F = fams[fam]
        n = len(F["y"])
        fr: dict = {"role": role, "episodes": n, "cells": len(F["cells"]),
                    "invalidOrIncomplete": F["invalid"]}
        if n == 0:
            fr["status"] = "no data"
            report["families"][fam] = fr
            continue
        X = np.array(F["rows"]); y = np.array(F["y"])
        if float(np.var(y)) == 0.0:
            # registered degenerate branch: corner design
            fr["status"] = "non-diagnostic at floor/ceiling (registered outcome)"
            fr["constantY"] = float(y[0])
            fr["perCellCP"] = {c: {"coop": k, "n": ntr, "cp95": _cp_bounds(k, ntr)}
                               for c, (k, ntr) in sorted(F["cellCoop"].items())}
            report["families"][fam] = fr
            md += [f"## {fam} ({role}) — non-diagnostic at floor/ceiling",
                   f"All {n} episodes identical (Y = {y[0]}); per-cell Clopper–Pearson bounds in the JSON report.", ""]
            continue
        p_ = X.shape[1]
        XtX_inv = np.linalg.inv(X.T @ X)
        beta_hat = XtX_inv @ X.T @ y
        resid = y - X @ beta_hat
        h = np.einsum("ij,jk,ik->i", X, XtX_inv, X)
        w_hc3 = (resid / (1.0 - h)) ** 2
        V = XtX_inv @ (X.T * w_hc3) @ X @ XtX_inv
        df = n - p_

        claims: dict[str, dict] = {}
        pvals: dict[str, float] = {}
        for cid, ell in est_rows.items():
            ell = np.atleast_2d(ell)
            est = ell @ beta_hat
            cov = ell @ V @ ell.T
            if ell.shape[0] == 1:
                se = float(np.sqrt(cov[0, 0]))
                t = float(est[0] / se) if se > 0 else float("nan")
                pv = float(2 * sps.t.sf(abs(t), df)) if se > 0 else float("nan")
                tcrit = float(sps.t.ppf(0.975, df))
                claims[cid] = {"estimate": float(est[0]), "se": se, "t": t, "df": df,
                               "p": pv, "ci95": [float(est[0] - tcrit * se), float(est[0] + tcrit * se)]}
            else:
                try:
                    wald = float(est @ np.linalg.solve(cov, est))
                    pv = float(sps.chi2.sf(wald, ell.shape[0]))
                except np.linalg.LinAlgError:
                    wald, pv = float("nan"), float("nan")
                percontrast = []
                tcrit = float(sps.t.ppf(0.975, df))
                for i, cname in enumerate(("c1", "c2", "c3")):
                    se_i = float(np.sqrt(cov[i, i]))
                    percontrast.append({"contrast": cname, "estimate": float(est[i]), "se": se_i,
                                        "ci95": [float(est[i] - tcrit * se_i), float(est[i] + tcrit * se_i)]})
                claims[cid] = {"wald": wald, "dfNum": int(ell.shape[0]), "p": pv,
                               "perContrast": percontrast}
            pvals[cid] = claims[cid]["p"]
        hp = holm(pvals)
        for cid in claims:
            claims[cid]["holmP"] = hp[cid]
            claims[cid]["interimVerdict"] = ("supported" if hp[cid] < 0.05 else "not supported")
        # O and P main effects — diagnostics only, never confirmatory (frozen)
        diag = {}
        import itertools as _it
        for fac, lo_v, hi_v in (("O", "cf", "df"), ("P", "ad", "pm")):
            cells_hi = [(m, w, l, hi_v, p2) if fac == "O" else (m, w, l, o2, hi_v)
                        for m in D1_M for w in D1_W for l in D1_L
                        for (o2, p2) in _it.product(D1_O, D1_P) if True]
            # equal-weight diagnostic via design rows (marginal over the other four factors)
            if fac == "O":
                ell = (np.mean([d1_row(m, w, l, hi_v, p2) for m in D1_M for w in D1_W
                                for l in D1_L for p2 in D1_P], axis=0)
                       - np.mean([d1_row(m, w, l, lo_v, p2) for m in D1_M for w in D1_W
                                  for l in D1_L for p2 in D1_P], axis=0))
            else:
                ell = (np.mean([d1_row(m, w, l, o2, hi_v) for m in D1_M for w in D1_W
                                for l in D1_L for o2 in D1_O], axis=0)
                       - np.mean([d1_row(m, w, l, o2, lo_v) for m in D1_M for w in D1_W
                                  for l in D1_L for o2 in D1_O], axis=0))
            e = float(ell @ beta_hat); se = float(np.sqrt(ell @ V @ ell))
            diag[fac] = {"estimate": e, "se": se}
        fr["status"] = "adjudicated"
        fr["grandMeanY"] = float(np.mean(y))
        fr["claims"] = claims
        fr["diagnosticsOP"] = diag
        report["families"][fam] = fr

        md += [f"## {fam} ({role}) — {n} episodes, {len(F['cells'])} cells, "
               f"{len(F['invalid'])} invalid/incomplete excluded",
               f"Grand mean Y = {np.mean(y):.4f}", "",
               "| claim | estimate / Wald | p | Holm-p | interim verdict |", "|---|---|---|---|---|"]
        for cid, c in claims.items():
            stat = (f"{c['estimate']:+.4f} (se {c['se']:.4f})" if "estimate" in c
                    else f"Wald {c['wald']:.3f} ({c['dfNum']} df)")
            md += [f"| {cid} | {stat} | {c['p']:.2e} | {c['holmP']:.2e} | {c['interimVerdict']} |"]
        md += [""]

    with open(os.path.join(DOCS, "d1-report.json"), "w") as f:
        json.dump(report, f, indent=1)
    with open(os.path.join(DOCS, "d1-report.md"), "w") as f:
        f.write("\n".join(md) + "\n")
    print(json.dumps({fam: {k: v for k, v in fr.items() if k in ("status", "episodes", "grandMeanY")}
                      for fam, fr in report["families"].items()}, indent=1))
    print(f"reports written: docs/phase4/d1-report.json, .md")
    return 0


# ── D2 confirmatory analysis (frozen: predicates.md §Family D2) ──────────────
#
# Pinned pre-data (disclosed in provenance-notes.md): Holm step-down uses
# m = 4 (the registered family size) applied over the three CI-based claims
# D2-1/2/4 — strictly conservative; D2-3 is adjudicated solely by its
# registered CP thresholds. p for directional claims (D2-1/2: "CI > 0") is
# the one-sided inversion; D2-4 ("CI excludes 0") two-sided.

def _d2_word_idx(db, rid: str, template_hint: str) -> int:
    rows = list(db.execute(
        """SELECT json_extract(payload,'$.object.data.gameDef.actionLabels')
           FROM events WHERE run_id=? AND type='object.created'
             AND json_extract(payload,'$.object.type')='game'""", (rid,)))
    if len(rows) != 1:
        raise SystemExit(f"D2 run {rid}: {len(rows)} game objects — refusing")
    labels = json.loads(rows[0][0])
    hits = [i for i, lab in enumerate(labels) if "cooperate" in lab.lower()]
    if len(hits) != 1:
        raise SystemExit(f"D2 run {rid}: actionLabels {labels} do not contain exactly "
                         f"one COOPERATE-word option — refusing ({template_hint})")
    return hits[0]


def d2() -> int:
    runs = load_phase4_runs()
    db = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    fams: dict[str, dict] = {f: {"role": {}, "word": {}, "B": [], "invalid": []}
                             for f in ("gpt", "cvx")}
    for rid, r in runs.items():
        if r.get("block") != "D2":
            continue
        parts = r.get("armId", "").split("-")     # p4-d2-{w}-{g}-{s}-{fam}
        if len(parts) != 6 or parts[:2] != ["p4", "d2"]:
            raise SystemExit(f"UNPARSEABLE D2 armId {r.get('armId')!r} — refusing")
        _, _, w, g, s_, fam = parts
        F = fams[fam]
        cell = (g, s_)
        if r["invalid"] or not r["completed"] or 1 not in r["rounds"]:
            F["invalid"].append(f"{r['armId']} seed {r.get('seed')}")
            continue
        cw = _d2_word_idx(db, rid, r["armId"])
        a1, a2 = r["rounds"][1]
        word_ep = ((a1 == cw) + (a2 == cw)) / 2
        role_idx = cw if s_ == "al" else 1 - cw
        role_ep = ((a1 == role_idx) + (a2 == role_idx)) / 2
        F["role"].setdefault(cell, []).append(role_ep)
        F["word"].setdefault(cell, []).append(word_ep)
        if cell == ("cfd", "sw"):
            F["B"].append(1.0 if (a1 == cw and a2 == cw) else 0.0)
    db.close()

    report = {"generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "frozenSpec": "predicates.md §Family D2; BCa(20260801) 10k; exact fallback on "
                            "constant cells; Holm m=4 over the three CI claims (pinned pre-data)",
              "families": {}}
    md = ["# D2 interim adjudication (final verdicts in step 8)", "",
          f"Generated {report['generatedAt']}.", ""]
    for fam, role_name in (("gpt", "primary"), ("cvx", "secondary (cross-vendor mirror)")):
        F = fams[fam]
        n_eps = sum(len(v) for v in F["role"].values())
        fr: dict = {"role": role_name, "episodes": n_eps,
                    "invalidOrIncomplete": F["invalid"]}
        if n_eps == 0:
            fr["status"] = "no data"
            report["families"][fam] = fr
            continue
        claims = {
            "P4-D2-1": _bca_diff_claim(F["role"].get(("cfd", "al"), []),
                                       F["role"].get(("can", "al"), []), two_sided=False),
            "P4-D2-2": _bca_diff_claim(F["role"].get(("cfd", "sw"), []),
                                       F["role"].get(("can", "sw"), []), two_sided=False),
            "P4-D2-4": _bca_diff_claim(F["word"].get(("cfd", "al"), []),
                                       F["word"].get(("cfd", "sw"), []), two_sided=True),
        }
        m_reg = 4                    # registered family size (conservative over 3 CI claims)
        running = 0.0
        for i, (k, _) in enumerate(sorted(claims.items(), key=lambda kv: kv[1]["p"])):
            running = max(running, claims[k]["p"] * (m_reg - i))
            claims[k]["holmP"] = min(1.0, running)
        for k in claims:
            claims[k]["interimVerdict"] = ("supported" if claims[k]["holmP"] < 0.05
                                           else "not supported")
        nb = len(F["B"])
        kb = int(round(sum(F["B"])))
        cp_lo, cp_hi = _cp_bounds(kb, nb) if nb else (float("nan"), float("nan"))
        d23 = {"bothCoopWordEpisodes": kb, "n": nb, "pointEstimate": (kb / nb) if nb else None,
               "cp95": [cp_lo, cp_hi],
               "classification": ("label-dominant" if cp_lo >= 0.80 else
                                  "payoff-dominant" if cp_hi <= 0.20 else "mixed")}
        fr["status"] = "adjudicated"
        fr["claims"] = claims
        fr["P4-D2-3"] = d23
        fr["cellMeans"] = {"role": {f"{g}-{s_}": round(sum(v) / len(v), 4)
                                    for (g, s_), v in sorted(F["role"].items())},
                           "word": {f"{g}-{s_}": round(sum(v) / len(v), 4)
                                    for (g, s_), v in sorted(F["word"].items())}}
        report["families"][fam] = fr
        md += [f"## {fam} ({role_name}) — {n_eps} episodes, "
               f"{len(F['invalid'])} invalid/incomplete excluded",
               f"Cell means (role): {fr['cellMeans']['role']}",
               f"Cell means (word): {fr['cellMeans']['word']}", "",
               "| claim | estimate | 95% CI | p | Holm-p (m=4) | interim verdict |",
               "|---|---|---|---|---|---|"]
        for k, c in claims.items():
            md += [f"| {k} | {c['estimate']:+.4f} | [{c['ci95'][0]:+.4f}, {c['ci95'][1]:+.4f}] "
                   f"| {c['p']:.2e} | {c['holmP']:.2e} | {c['interimVerdict']} |"]
        md += [f"| P4-D2-3 | {d23['pointEstimate']} | CP [{cp_lo:.4f}, {cp_hi:.4f}] | — | — | "
               f"{d23['classification']} |", ""]
    with open(os.path.join(DOCS, "d2-report.json"), "w") as f:
        json.dump(report, f, indent=1)
    with open(os.path.join(DOCS, "d2-report.md"), "w") as f:
        f.write("\n".join(md) + "\n")
    print(json.dumps({f_: {k: v for k, v in fr.items() if k in ("status", "episodes")}
                      for f_, fr in report["families"].items()}, indent=1))
    return 0


# ── D3 confirmatory analysis (frozen: predicates.md §Family D3) ──────────────

def d3() -> int:
    arms = {a["armId"]: a for a in json.load(open(os.path.join(DOCS, "arms.json")))["arms"]}
    runs = load_phase4_runs()
    db = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    fams: dict[str, dict] = {f: {"D": [], "cats": [0, 0, 0, 0], "invalid": []}
                             for f in ("gpt", "cvx")}   # cats: first-only, rock-only, both, neither
    for rid, r in runs.items():
        if r.get("block") != "D3":
            continue
        parts = r.get("armId", "").split("-")          # p4-d3-map{i}-ord{j}-{fam}
        if len(parts) != 5 or parts[:2] != ["p4", "d3"]:
            raise SystemExit(f"UNPARSEABLE D3 armId {r.get('armId')!r} — refusing")
        fam = parts[4]
        F = fams[fam]
        if r["invalid"] or not r["completed"] or 1 not in r["rounds"]:
            F["invalid"].append(f"{r['armId']} seed {r.get('seed')}")
            continue
        binding = arms[r["armId"]]["bindings"]
        rows = list(db.execute(
            """SELECT json_extract(payload,'$.object.data.gameDef.actionLabels')
               FROM events WHERE run_id=? AND type='object.created'
                 AND json_extract(payload,'$.object.type')='game'""", (rid,)))
        if len(rows) != 1:
            raise SystemExit(f"D3 run {rid}: {len(rows)} game objects — refusing")
        labels = json.loads(rows[0][0])
        if labels != binding["displayOrder"]:
            raise SystemExit(f"D3 run {rid}: actionLabels {labels} != sealed displayOrder "
                             f"{binding['displayOrder']} — refusing")
        rock_sym = next(k for k, v in binding["roleMapping"].items() if v == "rock")
        rock_idx = labels.index(rock_sym)
        a1, a2 = r["rounds"][1]
        first_share = ((a1 == 0) + (a2 == 0)) / 2
        rock_share = ((a1 == rock_idx) + (a2 == rock_idx)) / 2
        F["D"].append(first_share - rock_share)
        for a in (a1, a2):
            fi, ro = a == 0, a == rock_idx
            F["cats"][2 if (fi and ro) else 0 if fi else 1 if ro else 3] += 1
    db.close()

    report = {"generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
              "frozenSpec": "predicates.md §Family D3; BCa(20260801) one-sided 95% lower "
                            "bound (α=.05 endpoint); exact sign-test fallback if constant; "
                            "support-only Dirichlet(1) posterior (never confirmatory); "
                            "penalized multinomial logit deferred to step 8 (disclosed)",
              "families": {}}
    md = ["# D3 interim adjudication (final verdicts in step 8)", "",
          f"Generated {report['generatedAt']}.", ""]
    for fam, role_name in (("gpt", "primary"), ("cvx", "secondary (cross-vendor mirror)")):
        F = fams[fam]
        D = F["D"]
        fr: dict = {"role": role_name, "episodes": len(D),
                    "invalidOrIncomplete": F["invalid"]}
        if not D:
            fr["status"] = "no data"
            report["families"][fam] = fr
            continue
        mean_d = sum(D) / len(D)
        if len(set(D)) == 1:
            from scipy.stats import binomtest
            npos, nneg = sum(1 for d in D if d > 0), sum(1 for d in D if d < 0)
            if npos + nneg == 0:
                fr["P4-D3-1"] = {"method": "sign-test fallback", "estimate": mean_d,
                                 "verdict": "non-diagnostic (all D_ep = 0)"}
            else:
                bt = binomtest(npos, npos + nneg, 0.5, alternative="greater")
                fr["P4-D3-1"] = {"method": "exact sign-test fallback (constant sample)",
                                 "estimate": mean_d, "p": float(bt.pvalue),
                                 "verdict": ("supported" if bt.pvalue < 0.05 and mean_d > 0
                                             else "not supported")}
        else:
            theta, sb, z0, a, degen = _bca_fit([D], lambda gs: sum(gs[0]) / len(gs[0]))
            if degen:
                raise SystemExit(f"D3 BCa degenerate ({degen}) with non-constant sample — refusing")
            lb = _bca_endpoint(sb, z0, a, 0.05)
            fr["P4-D3-1"] = {"method": "BCa(20260801) one-sided 95% lower bound",
                             "estimate": theta, "lowerBound95": lb,
                             "verdict": "supported" if lb > 0 else "not supported"}
        import numpy as np
        rng = np.random.default_rng(BCA_SEED)          # support-only; pinned + disclosed
        post = rng.dirichlet([1 + c for c in F["cats"]], size=100000)
        p_pos = float((post[:, 0] > post[:, 1]).mean())
        fr["supportOnly"] = {"seatCategoryCounts": {"firstOnly": F["cats"][0],
                                                    "rockOnly": F["cats"][1],
                                                    "both": F["cats"][2],
                                                    "neither": F["cats"][3]},
                             "dirichletPosteriorP_firstOnly_gt_rockOnly": p_pos,
                             "penalizedLogit": "deferred to step 8 (support-only, disclosed)"}
        fr["status"] = "adjudicated"
        report["families"][fam] = fr
        v = fr["P4-D3-1"]
        md += [f"## {fam} ({role_name}) — {len(D)} episodes, "
               f"{len(F['invalid'])} invalid/incomplete excluded",
               f"mean D_ep = {mean_d:+.4f}; P4-D3-1: {v['verdict']} "
               f"({v['method']}; " +
               (f"lower bound {v['lowerBound95']:+.4f}" if "lowerBound95" in v
                else f"p={v.get('p')}") + ")",
               f"Support-only Dirichlet: P(first-only > rock-only) = {p_pos:.4f} "
               f"(counts {fr['supportOnly']['seatCategoryCounts']})", ""]
    with open(os.path.join(DOCS, "d3-report.json"), "w") as f:
        json.dump(report, f, indent=1)
    with open(os.path.join(DOCS, "d3-report.md"), "w") as f:
        f.write("\n".join(md) + "\n")
    print(json.dumps({f_: {k: v for k, v in fr.items() if k in ("status", "episodes", "P4-D3-1")}
                      for f_, fr in report["families"].items()}, indent=1, default=str))
    return 0


def main() -> None:
    if "--scan" in sys.argv:
        raise SystemExit(scan(sys.argv[sys.argv.index("--scan") + 1]))
    if "--sentinel" in sys.argv:
        raise SystemExit(sentinel(int(sys.argv[sys.argv.index("--sentinel") + 1])))
    if "--x2-screening" in sys.argv:
        raise SystemExit(x2_screening())
    if "--d1" in sys.argv:
        raise SystemExit(d1())
    if "--d2" in sys.argv:
        raise SystemExit(d2())
    if "--d3" in sys.argv:
        raise SystemExit(d3())
    print(__doc__)


if __name__ == "__main__":
    main()
