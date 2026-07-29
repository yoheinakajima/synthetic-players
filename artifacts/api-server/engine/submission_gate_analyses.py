#!/usr/bin/env python3
"""Zero-subject-call analyses required by the paper submission gate.

This script reads the archived Phase 5 event store and writes paper-facing
sensitivity analyses without changing any sealed predicate, historical verdict,
or source event. It performs four analyses:

1. episode-clustered sensitivity for historical seat-level gates and shares;
2. high-precision familywise audit of the P5-3(a) p13 candidate;
3. finite-opportunity correction of between-prompt dispersion;
4. count reconciliation across episodes, events, decisions, and provider calls.

Primary cluster sensitivity chosen before execution:
- unit: complete episode;
- outcome: episode mean of the two round-one seat choices, in {0, .5, 1};
- interval: exact nonparametric percentile bootstrap distribution induced by
  resampling complete episodes with replacement;
- interior gate: 95% cluster-bootstrap interval wholly inside (0.05, 0.95).

A Jeffreys Dirichlet-multinomial posterior interval is reported as an additional
sensitivity for the observed cells, but it is not used to select the familywise
permutation statistic.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import sqlite3
import sys
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Iterable

import numpy as np
from scipy.stats import beta

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))

from phase5_closeout_adjudicate import (  # noqa: E402
    GATE_HI,
    GATE_LO,
    HUMAN_SD,
    P52_LB,
    P52_UB,
    RHO,
    THETA_1,
    THETA_2,
    TIER_A_CELLS,
    collect,
    gate_cell,
    load_p5_arms,
    load_personas,
    load_runs,
    p52_verdict,
    valid_runs_by,
)

OUT = ROOT / "docs" / "analysis" / "submission"
FIG = OUT / "figure-sources"
DECISIONS = ROOT / "docs" / "phase5-close" / "adjudication-decisions.json"
DB = HERE / "data" / "engine.db"
BUDGET_DB = HERE / "data" / "budget.db"

ALPHA = 0.05
DIRICHLET_DRAWS = int(os.environ.get("SUBMISSION_DIRICHLET_DRAWS", "200000"))
FAMILY_PERMUTATIONS = int(os.environ.get("SUBMISSION_FAMILY_PERMUTATIONS", "200000"))
FAMILY_BATCH = int(os.environ.get("SUBMISSION_FAMILY_BATCH", "5000"))
VAR_BOOTSTRAPS = int(os.environ.get("SUBMISSION_VARIANCE_BOOTSTRAPS", "50000"))
BASE_SEED = 20260729
LEVELS = ("s2a", "s2p")
REP_CELLS = tuple(c for c in TIER_A_CELLS if c.startswith("rep-"))


def stable_seed(label: str, base: int = BASE_SEED) -> int:
    h = hashlib.sha256(label.encode("utf-8")).digest()
    return (int.from_bytes(h[:8], "big") ^ base) % (2**63 - 1)


def category_counts(values: Iterable[float]) -> tuple[int, int, int]:
    c = Counter(round(float(v) * 2) for v in values)
    bad = sorted(k for k in c if k not in (0, 1, 2))
    if bad:
        raise ValueError(f"episode outcomes outside {{0,.5,1}}: {bad}")
    return c.get(0, 0), c.get(1, 0), c.get(2, 0)


def category_mean(counts: tuple[int, int, int]) -> float:
    c0, c1, c2 = counts
    n = c0 + c1 + c2
    return (0.5 * c1 + c2) / n if n else float("nan")


@lru_cache(maxsize=None)
def exact_cluster_bootstrap_support(
    c0: int, c1: int, c2: int
) -> tuple[tuple[float, ...], tuple[float, ...]]:
    """Exact percentile-bootstrap distribution of the episode-level mean.

    The empirical distribution has support {0,.5,1}. A bootstrap sample of n
    complete episodes has multinomial counts. We enumerate every possible count
    triple and aggregate probability at each possible sample mean.
    """
    n = c0 + c1 + c2
    if n <= 0:
        return (0.0,), (1.0,)
    probs = (c0 / n, c1 / n, c2 / n)
    by_mean: dict[float, float] = defaultdict(float)
    fact_n = math.factorial(n)
    for b0 in range(n + 1):
        for b1 in range(n - b0 + 1):
            b2 = n - b0 - b1
            coeff = fact_n / (
                math.factorial(b0) * math.factorial(b1) * math.factorial(b2)
            )
            pr = coeff
            for b, p in zip((b0, b1, b2), probs):
                if b and p == 0:
                    pr = 0.0
                    break
                if b:
                    pr *= p**b
            m = (0.5 * b1 + b2) / n
            by_mean[round(m, 12)] += pr
    xs = sorted(by_mean)
    ps = [by_mean[x] for x in xs]
    total = sum(ps)
    ps = [p / total for p in ps]
    return tuple(xs), tuple(ps)


def discrete_quantile(xs: tuple[float, ...], ps: tuple[float, ...], q: float) -> float:
    acc = 0.0
    for x, p in zip(xs, ps):
        acc += p
        if acc + 1e-15 >= q:
            return x
    return xs[-1]


def cluster_bootstrap_interval(
    values: Iterable[float], alpha: float = ALPHA
) -> tuple[float, float]:
    counts = category_counts(values)
    xs, ps = exact_cluster_bootstrap_support(*counts)
    return (
        discrete_quantile(xs, ps, alpha / 2),
        discrete_quantile(xs, ps, 1 - alpha / 2),
    )


def cluster_bootstrap_lower(
    values: Iterable[float], alpha: float = ALPHA
) -> float:
    counts = category_counts(values)
    xs, ps = exact_cluster_bootstrap_support(*counts)
    return discrete_quantile(xs, ps, alpha)


def cluster_gate(values: Iterable[float]) -> dict:
    vals = [float(v) for v in values]
    lo, hi = cluster_bootstrap_interval(vals)
    return {
        "episodes": len(vals),
        "counts_0_half_1": list(category_counts(vals)),
        "mean": float(np.mean(vals)) if vals else None,
        "interval95": [lo, hi],
        "interior": bool(vals and lo > GATE_LO and hi < GATE_HI),
    }


def dirichlet_interval(values: Iterable[float], label: str) -> tuple[float, float]:
    counts = np.asarray(category_counts(values), dtype=float)
    rng = np.random.default_rng(stable_seed(f"dirichlet:{label}"))
    draws = rng.dirichlet(counts + 0.5, size=DIRICHLET_DRAWS)
    means = 0.5 * draws[:, 1] + draws[:, 2]
    lo, hi = np.quantile(means, [ALPHA / 2, 1 - ALPHA / 2])
    return float(lo), float(hi)


def dirichlet_gate(values: Iterable[float], label: str) -> dict:
    vals = [float(v) for v in values]
    lo, hi = dirichlet_interval(vals, label)
    return {
        "episodes": len(vals),
        "mean": float(np.mean(vals)) if vals else None,
        "interval95": [lo, hi],
        "interior": bool(vals and lo > GATE_LO and hi < GATE_HI),
    }


def cp_bounds(k: int, n: int, alpha: float = ALPHA) -> tuple[float, float]:
    if n <= 0:
        return 0.0, 1.0
    lo = 0.0 if k == 0 else float(beta.ppf(alpha / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - alpha / 2, k + 1, n - k))
    return lo, hi


def fmt(x: float | None, digits: int = 4) -> str:
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return "—"
    return f"{x:.{digits}f}"


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def load_decisions() -> dict:
    return json.loads(DECISIONS.read_text(encoding="utf-8"))


def episode_conflict_series(runs: dict, personas: dict, decisions: dict) -> dict[str, list[float]]:
    groups: dict[str, list[float]] = defaultdict(list)
    for pid, lean in sorted(personas.items()):
        for cell in TIER_A_CELLS:
            code = decisions["p52Coding"].get(f"{lean}|{cell}")
            if code is None:
                continue
            task_dir = code["taskConsistent"]
            key = f"{lean}|{cell}"
            for r in valid_runs_by(runs, pid, cell):
                c_role = r["coopRole"]
                want = c_role if task_dir == "coop-role" else 1 - c_role
                hits = [int(a == want) for a in r["round1"]]
                groups[key].append(sum(hits) / 2)
    groups["__pooled__"] = [v for k, vals in groups.items() if k != "__pooled__" for v in vals]
    return dict(groups)


def episode_refusal_series(runs: dict) -> dict[tuple[str, float], list[float]]:
    arms = load_p5_arms()
    out: dict[tuple[str, float], list[float]] = defaultdict(list)
    for r in runs.values():
        arm = arms.get(r.get("armId"))
        if not arm or arm.get("cell") != "os-swap" or arm.get("personaId") is None:
            continue
        if not arm.get("block", "").startswith(("P5A", "P5B")):
            continue
        if not (r.get("completed") and not r.get("invalid") and r.get("round1")):
            continue
        d_role = 1 - r["coopRole"]
        hits = [int(a == d_role) for a in r["round1"]]
        out[(arm["personaId"], float(arm["temperature"]))].append(sum(hits) / 2)
    return dict(out)


def analysis_episode_cluster(runs: dict, personas: dict, col: dict, decisions: dict) -> dict:
    eps_a = col["epsA"]
    rows: list[dict] = []
    changes_boot: list[str] = []
    changes_dir: list[str] = []
    for pid in sorted(personas):
        for cell in TIER_A_CELLS:
            vals = eps_a[(pid, cell)]
            hist = gate_cell(vals)
            boot = cluster_gate(vals)
            dgate = dirichlet_gate(vals, f"{pid}|{cell}")
            if hist["interior"] != boot["interior"]:
                changes_boot.append(f"{pid}|{cell}")
            if hist["interior"] != dgate["interior"]:
                changes_dir.append(f"{pid}|{cell}")
            rows.append({
                "personaId": pid,
                "cell": cell,
                "episodes": len(vals),
                "episodeCounts0": boot["counts_0_half_1"][0],
                "episodeCountsHalf": boot["counts_0_half_1"][1],
                "episodeCounts1": boot["counts_0_half_1"][2],
                "mean": round(float(np.mean(vals)), 6),
                "historicalSeatInterior": int(hist["interior"]),
                "historicalSeatCPlo": round(hist["cp95"][0], 6),
                "historicalSeatCPhi": round(hist["cp95"][1], 6),
                "clusterBootstrapInterior": int(boot["interior"]),
                "clusterBootstrapLo": round(boot["interval95"][0], 6),
                "clusterBootstrapHi": round(boot["interval95"][1], 6),
                "dirichletJeffreysInterior": int(dgate["interior"]),
                "dirichletJeffreysLo": round(dgate["interval95"][0], 6),
                "dirichletJeffreysHi": round(dgate["interval95"][1], 6),
            })
    write_csv(FIG / "episode-cluster-cells.csv", rows)

    restricted_cells = decisions["p51aRestrictedCells"]
    restricted = [r for r in rows if r["cell"] in restricted_cells]
    summaries = {
        "historical": {
            "restrictedInterior": sum(r["historicalSeatInterior"] for r in restricted),
            "restrictedN": len(restricted),
            "restrictedFraction": sum(r["historicalSeatInterior"] for r in restricted) / len(restricted),
            "unrestrictedInterior": sum(r["historicalSeatInterior"] for r in rows),
            "unrestrictedN": len(rows),
        },
        "clusterBootstrap": {
            "restrictedInterior": sum(r["clusterBootstrapInterior"] for r in restricted),
            "restrictedN": len(restricted),
            "restrictedFraction": sum(r["clusterBootstrapInterior"] for r in restricted) / len(restricted),
            "unrestrictedInterior": sum(r["clusterBootstrapInterior"] for r in rows),
            "unrestrictedN": len(rows),
        },
        "dirichletJeffreys": {
            "restrictedInterior": sum(r["dirichletJeffreysInterior"] for r in restricted),
            "restrictedN": len(restricted),
            "restrictedFraction": sum(r["dirichletJeffreysInterior"] for r in restricted) / len(restricted),
            "unrestrictedInterior": sum(r["dirichletJeffreysInterior"] for r in rows),
            "unrestrictedN": len(rows),
        },
    }
    for v in summaries.values():
        v["historicalPredicateWouldSupport"] = bool(v["restrictedFraction"] < THETA_1)

    # P5-2 episode-level task-consistency intervals.
    conflict = episode_conflict_series(runs, personas, decisions)
    conflict_rows = []
    for key, vals in sorted(conflict.items()):
        ci = cluster_bootstrap_interval(vals)
        share = float(np.mean(vals))
        verdict = "task-dominant" if ci[0] >= P52_LB else "persona-dominant" if ci[1] <= P52_UB else "mixed"
        conflict_rows.append({
            "conflictCell": key,
            "episodes": len(vals),
            "meanTaskConsistentSeatShare": round(share, 6),
            "clusterBootstrapLo": round(ci[0], 6),
            "clusterBootstrapHi": round(ci[1], 6),
            "clusterVerdict": verdict,
        })
    write_csv(FIG / "episode-cluster-p52.csv", conflict_rows)

    # Clause (b), episode-clustered, including familywise one-sided lower bound.
    refusal = episode_refusal_series(runs)
    m = len(refusal)
    refusal_rows = []
    for (pid, temp), vals in sorted(refusal.items()):
        ci = cluster_bootstrap_interval(vals)
        lower_bonf = cluster_bootstrap_lower(vals, alpha=ALPHA / m)
        refusal_rows.append({
            "personaId": pid,
            "temperature": temp,
            "episodes": len(vals),
            "meanRefusalSeatShare": round(float(np.mean(vals)), 6),
            "clusterBootstrapLo": round(ci[0], 6),
            "clusterBootstrapHi": round(ci[1], 6),
            "bonferroniOneSidedLower": round(lower_bonf, 6),
            "passesUnadjusted": int(ci[0] >= THETA_2),
            "passesBonferroni": int(lower_bonf >= THETA_2),
        })
    write_csv(FIG / "episode-cluster-clause-b.csv", refusal_rows)

    md = [
        "# Episode-clustered sensitivity for Phase 5 round-one claims",
        "",
        "> **STATUS: POST-ADJUDICATION SENSITIVITY — ZERO SUBJECT CALLS.** Historical registered verdicts are unchanged. The primary sensitivity resamples complete episodes and uses the exact percentile-bootstrap distribution of the episode mean, where an episode contributes 0, 0.5, or 1. A Jeffreys Dirichlet-multinomial interval is reported as a second sensitivity.",
        "",
        "## Method fixed before execution",
        "",
        "Two seat decisions share an episode. The primary sensitivity therefore defines the episode mean `Y_e=(Y_e1+Y_e2)/2`, constructs the exact nonparametric bootstrap distribution obtained by resampling complete episodes, and applies the historical two-sided gate only when the resulting 95% interval lies wholly inside `(0.05,0.95)`. This is a sensitivity analysis, not a retroactive replacement of the frozen Clopper–Pearson predicate.",
        "",
        "## P5-1a census",
        "",
        "| method | restricted interior / n | restricted fraction | would historical `<0.10` rule support? | all-cell interior / 96 |",
        "|---|---:|---:|---|---:|",
    ]
    for name, label in (("historical", "Historical seat-level CP"), ("clusterBootstrap", "Episode cluster bootstrap"), ("dirichletJeffreys", "Episode Dirichlet–Jeffreys")):
        s = summaries[name]
        md.append(
            f"| {label} | {s['restrictedInterior']}/{s['restrictedN']} | {s['restrictedFraction']:.4f} | {'yes' if s['historicalPredicateWouldSupport'] else 'no'} | {s['unrestrictedInterior']}/{s['unrestrictedN']} |"
        )
    md += [
        "",
        f"Cells changing classification under the cluster bootstrap: **{len(changes_boot)}**. Cells changing under the Dirichlet–Jeffreys sensitivity: **{len(changes_dir)}**. Complete cell table: `figure-sources/episode-cluster-cells.csv`.",
        "",
        "## P5-2 and clause (b)",
        "",
        "The episode-level P5-2 table is in `figure-sources/episode-cluster-p52.csv`. Clause-(b) intervals, including a Bonferroni-adjusted one-sided cluster-bootstrap lower bound over every evaluable lane, are in `figure-sources/episode-cluster-clause-b.csv`.",
        "",
        "## Interpretation rule",
        "",
        "Any classification change is reported as a sensitivity result beside the historical mechanical verdict. It is not entered into the dead-predictions count and does not rewrite sealed reports.",
    ]
    (OUT / "episode-cluster-sensitivity.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return {"rows": rows, "summaries": summaries, "conflict": conflict_rows, "refusal": refusal_rows}


def make_gate_lookup(n: int, kind: str) -> np.ndarray:
    arr = np.zeros((n + 1, n + 1), dtype=bool)
    for c0 in range(n + 1):
        for c1 in range(n - c0 + 1):
            c2 = n - c0 - c1
            if kind == "cluster":
                lo, hi = cluster_bootstrap_interval([0.0] * c0 + [0.5] * c1 + [1.0] * c2)
                arr[c0, c1] = lo > GATE_LO and hi < GATE_HI
            elif kind == "historical":
                k = c1 + 2 * c2
                lo, hi = cp_bounds(k, 2 * n)
                arr[c0, c1] = lo > GATE_LO and hi < GATE_HI
            else:
                raise ValueError(kind)
    return arr


def permutation_ci(r: int, b: int, alpha: float = ALPHA) -> tuple[float, float]:
    lo = 0.0 if r == 0 else float(beta.ppf(alpha / 2, r, b - r + 1))
    hi = 1.0 if r == b else float(beta.ppf(1 - alpha / 2, r + 1, b - r))
    return lo, hi


def analysis_p13_family(personas: dict, col: dict) -> dict:
    eps_a = col["epsA"]
    candidates: dict[tuple[str, str], tuple[np.ndarray, np.ndarray]] = {}
    rows = []
    for pid in sorted(personas):
        for lvl in LEVELS:
            g90 = np.asarray(eps_a[(pid, f"rep-d90-{lvl}")], dtype=float)
            g10 = np.asarray(eps_a[(pid, f"rep-d10-{lvl}")], dtype=float)
            candidates[(pid, lvl)] = (g90, g10)
            h90, h10 = gate_cell(g90.tolist()), gate_cell(g10.tolist())
            c90, c10 = cluster_gate(g90.tolist()), cluster_gate(g10.tolist())
            slope = float(g90.mean() - g10.mean())
            rows.append({
                "personaId": pid,
                "surface": lvl,
                "n90": len(g90),
                "n10": len(g10),
                "mean90": round(float(g90.mean()), 6),
                "mean10": round(float(g10.mean()), 6),
                "slope": round(slope, 6),
                "historicalBothInterior": int(h90["interior"] and h10["interior"]),
                "clusterBothInterior": int(c90["interior"] and c10["interior"]),
                "cluster90Lo": round(c90["interval95"][0], 6),
                "cluster90Hi": round(c90["interval95"][1], 6),
                "cluster10Lo": round(c10["interval95"][0], 6),
                "cluster10Hi": round(c10["interval95"][1], 6),
            })
    write_csv(FIG / "p13-family-candidates-final.csv", rows)

    ns = sorted({len(g) for pair in candidates.values() for g in pair})
    hist_lookup = {n: make_gate_lookup(n, "historical") for n in ns}
    cluster_lookup = {n: make_gate_lookup(n, "cluster") for n in ns}

    def observed(kind: str) -> tuple[float, tuple[str, str] | None, list[tuple[str, str]]]:
        best = -math.inf
        arg = None
        gated = []
        for key, (g90, g10) in candidates.items():
            gate = (gate_cell(g90.tolist())["interior"] and gate_cell(g10.tolist())["interior"]) if kind == "historical" else (cluster_gate(g90.tolist())["interior"] and cluster_gate(g10.tolist())["interior"])
            if gate:
                gated.append(key)
                t = float(g90.mean() - g10.mean())
                if t > best:
                    best, arg = t, key
        return best, arg, gated

    obs_hist, arg_hist, gated_hist = observed("historical")
    obs_cluster, arg_cluster, gated_cluster = observed("cluster")

    rng = np.random.default_rng(BASE_SEED + 53)
    exceed_hist = exceed_cluster = 0
    fire_hist = fire_cluster = 0
    any_gate_hist = any_gate_cluster = 0
    tmax_hist_values: list[float] = []
    tmax_cluster_values: list[float] = []

    done = 0
    while done < FAMILY_PERMUTATIONS:
        b = min(FAMILY_BATCH, FAMILY_PERMUTATIONS - done)
        tmax_h = np.full(b, -np.inf)
        tmax_c = np.full(b, -np.inf)
        for _key, (g90, g10) in candidates.items():
            pool_codes = np.rint(np.concatenate([g90, g10]) * 2).astype(np.int8)
            n90, n10 = len(g90), len(g10)
            total_counts = np.bincount(pool_codes, minlength=3)
            keys = rng.random((b, len(pool_codes)))
            selected_idx = np.argpartition(keys, n90 - 1, axis=1)[:, :n90]
            selected = pool_codes[selected_idx]
            c1_90 = np.sum(selected == 1, axis=1)
            c2_90 = np.sum(selected == 2, axis=1)
            c0_90 = n90 - c1_90 - c2_90
            c0_10 = total_counts[0] - c0_90
            c1_10 = total_counts[1] - c1_90
            c2_10 = total_counts[2] - c2_90
            mean90 = (0.5 * c1_90 + c2_90) / n90
            mean10 = (0.5 * c1_10 + c2_10) / n10
            slope = mean90 - mean10
            gh = hist_lookup[n90][c0_90, c1_90] & hist_lookup[n10][c0_10, c1_10]
            gc = cluster_lookup[n90][c0_90, c1_90] & cluster_lookup[n10][c0_10, c1_10]
            tmax_h = np.maximum(tmax_h, np.where(gh, slope, -np.inf))
            tmax_c = np.maximum(tmax_c, np.where(gc, slope, -np.inf))
        exceed_hist += int(np.sum(tmax_h >= obs_hist))
        exceed_cluster += int(np.sum(tmax_c >= obs_cluster))
        fire_hist += int(np.sum(tmax_h > 0))
        fire_cluster += int(np.sum(tmax_c > 0))
        any_gate_hist += int(np.sum(np.isfinite(tmax_h)))
        any_gate_cluster += int(np.sum(np.isfinite(tmax_c)))
        tmax_hist_values.extend(tmax_h[np.isfinite(tmax_h)].tolist())
        tmax_cluster_values.extend(tmax_c[np.isfinite(tmax_c)].tolist())
        done += b

    def summarize(r: int, obs: float, arg, gated, fire: int, any_gate: int, vals: list[float]) -> dict:
        p = (r + 1) / (FAMILY_PERMUTATIONS + 1)
        ci = permutation_ci(r, FAMILY_PERMUTATIONS)
        q = np.quantile(vals, [0.5, 0.9, 0.95, 0.99]).tolist() if vals else [None] * 4
        return {
            "observedTmaxRawSlope": obs,
            "argmax": list(arg) if arg else None,
            "observedGatePassing": [list(x) for x in gated],
            "permutations": FAMILY_PERMUTATIONS,
            "exceedances": r,
            "pAddOne": p,
            "mcClopperPearson95": list(ci),
            "nullAnyGateRate": any_gate / FAMILY_PERMUTATIONS,
            "nullFalseFireRate": fire / FAMILY_PERMUTATIONS,
            "finiteTmaxQuantiles": {"q50": q[0], "q90": q[1], "q95": q[2], "q99": q[3]},
        }

    result = {
        "historicalSeatGate_rawSlopeMax": summarize(exceed_hist, obs_hist, arg_hist, gated_hist, fire_hist, any_gate_hist, tmax_hist_values),
        "episodeClusterBootstrapGate_rawSlopeMax": summarize(exceed_cluster, obs_cluster, arg_cluster, gated_cluster, fire_cluster, any_gate_cluster, tmax_cluster_values),
        "family": {"registeredEligibleClauseA": 96, "evaluableClauseA": 32, "clauseBAnalyzedSeparately": True},
        "seed": BASE_SEED + 53,
    }
    (FIG / "p13-family-audit-final.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    md = [
        "# Final high-precision P5-3(a) family audit",
        "",
        "> **STATUS: POST-ADJUDICATION SENSITIVITY — ZERO SUBJECT CALLS.** The historical mechanical verdict is unchanged. This audit uses the same raw-slope statistic for the observed data and every permutation and reruns the full gate-plus-maximum-selection procedure over all 32 evaluable clause-(a) candidates.",
        "",
        "## Design",
        "",
        f"- Permutations: **{FAMILY_PERMUTATIONS:,}**, seed `{BASE_SEED + 53}`.",
        "- Randomization: episode outcomes are permuted between δ=.90 and δ=.10 within each persona × wording candidate, preserving arm sizes.",
        "- Statistic: maximum positive raw difference in episode-mean round-one cooperation among candidates passing both condition gates.",
        "- Two gate sensitivities are reported: the historical seat-level Clopper–Pearson gate and the episode-level exact cluster-bootstrap gate.",
        "- Monte Carlo p-values use `(r+1)/(B+1)` and the table reports a Clopper–Pearson interval for simulation uncertainty.",
        "",
        "## Results",
        "",
        "| gate | observed max slope | argmax | passing candidates | exceedances / B | p | MC 95% interval | null false-fire rate |",
        "|---|---:|---|---|---:|---:|---|---:|",
    ]
    for key, label in (("historicalSeatGate_rawSlopeMax", "Historical seat CP"), ("episodeClusterBootstrapGate_rawSlopeMax", "Episode cluster bootstrap")):
        s = result[key]
        arg = "/".join(s["argmax"]) if s["argmax"] else "none"
        passing = ", ".join("/".join(x) for x in s["observedGatePassing"]) or "none"
        md.append(
            f"| {label} | {s['observedTmaxRawSlope']:+.4f} | {arg} | {passing} | {s['exceedances']:,}/{s['permutations']:,} | {s['pAddOne']:.6f} | [{s['mcClopperPearson95'][0]:.6f}, {s['mcClopperPearson95'][1]:.6f}] | {s['nullFalseFireRate']:.3%} |"
        )
    md += [
        "",
        "## Status rule",
        "",
        "This is a post-adjudication sensitivity selected after external review identified the family-error omission. Regardless of its numerical outcome, it does not retroactively convert p13 into a prospectively family-controlled confirmatory result. p13 remains a preregistered replication target; the audit determines how strongly the archived data support that target after selection is accounted for.",
        "",
        "Complete candidate table: `figure-sources/p13-family-candidates-final.csv`. Machine-readable summary: `figure-sources/p13-family-audit-final.json`.",
    ]
    (OUT / "p13-family-audit-final.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return result


def corrected_variance(data: np.ndarray) -> tuple[float, float, float, float, float]:
    means = data.mean(axis=1)
    raw_b = float(np.var(means, ddof=1))
    within = np.var(data, axis=1, ddof=1)
    noise = float(np.mean(within / data.shape[1]))
    b = max(0.0, raw_b - noise)
    w = float(np.mean(within))
    ratio = b / (b + w) if b + w > 0 else float("nan")
    return raw_b, noise, b, w, ratio


def hierarchical_variance_bootstrap(data: np.ndarray, seed: int) -> dict:
    n_persona, n_ep = data.shape
    rng = np.random.default_rng(seed)
    vals = {k: [] for k in ("rawB", "noise", "B", "W", "ratio", "correctedSD")}
    batch = 1000
    done = 0
    while done < VAR_BOOTSTRAPS:
        b = min(batch, VAR_BOOTSTRAPS - done)
        pidx = rng.integers(0, n_persona, size=(b, n_persona))
        selected = data[pidx]
        eidx = rng.integers(0, n_ep, size=(b, n_persona, n_ep))
        sampled = np.take_along_axis(selected, eidx, axis=2)
        means = sampled.mean(axis=2)
        raw = np.var(means, axis=1, ddof=1)
        within = np.var(sampled, axis=2, ddof=1)
        noise = np.mean(within / n_ep, axis=1)
        bcorr = np.maximum(raw - noise, 0)
        w = np.mean(within, axis=1)
        ratio = np.divide(bcorr, bcorr + w, out=np.full_like(bcorr, np.nan), where=(bcorr + w) > 0)
        for key, arr in (("rawB", raw), ("noise", noise), ("B", bcorr), ("W", w), ("ratio", ratio), ("correctedSD", np.sqrt(bcorr))):
            vals[key].extend(arr.tolist())
        done += b
    out = {}
    for key, arr in vals.items():
        a = np.asarray(arr, dtype=float)
        a = a[np.isfinite(a)]
        out[key] = {
            "median": float(np.median(a)),
            "lo95": float(np.quantile(a, 0.025)),
            "hi95": float(np.quantile(a, 0.975)),
        }
    return out


def analysis_variance(personas: dict, col: dict, cluster_result: dict) -> dict:
    eps_a = col["epsA"]
    rows = []
    detail = {}
    for cell in REP_CELLS:
        series = [np.asarray(eps_a[(pid, cell)], dtype=float) for pid in sorted(personas)]
        lengths = sorted({len(x) for x in series})
        if len(lengths) != 1:
            raise RuntimeError(f"unequal episode counts in {cell}: {lengths}")
        data = np.vstack(series)
        raw_b, noise, b, w, ratio = corrected_variance(data)
        boot = hierarchical_variance_bootstrap(data, stable_seed(f"variance:{cell}"))
        key = "d90" if "d90" in cell else "d10"
        threshold = RHO * HUMAN_SD[key]
        corrected_sd = math.sqrt(b)
        means = data.mean(axis=1)
        observed_corner_mass = float(np.mean((means <= GATE_LO) | (means >= GATE_HI)))
        cluster_rows = [r for r in cluster_result["rows"] if r["cell"] == cell]
        cluster_corner_mass = 1 - sum(r["clusterBootstrapInterior"] for r in cluster_rows) / len(cluster_rows)
        row = {
            "cell": cell,
            "personas": data.shape[0],
            "episodesPerPersona": data.shape[1],
            "poolMean": round(float(data.mean()), 6),
            "rawBetweenVarianceOfEstimatedMeans": round(raw_b, 8),
            "estimatedMeanMeasurementNoise": round(noise, 8),
            "correctedBetweenVariance": round(b, 8),
            "rawBetweenSD": round(math.sqrt(raw_b), 6),
            "correctedBetweenSD": round(corrected_sd, 6),
            "averageWithinEpisodeVariance": round(w, 8),
            "betweenShare": round(ratio, 6) if math.isfinite(ratio) else "",
            "historicalRhoThresholdSD": round(threshold, 6),
            "correctedPointMeetsHistoricalThreshold": int(corrected_sd >= threshold),
            "observedPointCornerMass": round(observed_corner_mass, 6),
            "clusterGateCornerMass": round(cluster_corner_mass, 6),
            "bootstrapCorrectedSDlo": round(boot["correctedSD"]["lo95"], 6),
            "bootstrapCorrectedSDmedian": round(boot["correctedSD"]["median"], 6),
            "bootstrapCorrectedSDhi": round(boot["correctedSD"]["hi95"], 6),
            "bootstrapBetweenShareLo": round(boot["ratio"]["lo95"], 6),
            "bootstrapBetweenShareMedian": round(boot["ratio"]["median"], 6),
            "bootstrapBetweenShareHi": round(boot["ratio"]["hi95"], 6),
        }
        rows.append(row)
        detail[cell] = {"point": row, "bootstrap": boot}
    write_csv(FIG / "variance-correction.csv", rows)
    (FIG / "variance-correction.json").write_text(json.dumps(detail, indent=2) + "\n", encoding="utf-8")

    md = [
        "# Finite-opportunity correction for between-prompt dispersion",
        "",
        "> **STATUS: POST-ADJUDICATION SENSITIVITY — ZERO SUBJECT CALLS.** Historical P5-1b point comparisons are unchanged. This analysis treats complete episodes as repeated measurements, subtracts the estimated sampling contribution from the variance of persona means, and uses a hierarchical bootstrap over personas and episodes.",
        "",
        "## Estimator",
        "",
        "For each repeated-game cell, the raw variance of estimated persona means is decomposed as `Var_i(p_hat_i) ≈ B + mean(s_i²/n_i)`. The corrected between-prompt component is `max(0, raw variance − estimated measurement noise)`. `W` is the average within-prompt variance of the episode-level outcome. The bootstrap resamples personas and then episodes within persona.",
        "",
        f"Bootstrap replicates: **{VAR_BOOTSTRAPS:,}**.",
        "",
        "| cell | raw SD | corrected SD | bootstrap corrected SD 95% | within variance W | between share B/(B+W) | historical 0.75×human-SD threshold | point meets? |",
        "|---|---:|---:|---|---:|---|---:|---|",
    ]
    for r in rows:
        md.append(
            f"| {r['cell']} | {r['rawBetweenSD']:.4f} | {r['correctedBetweenSD']:.4f} | [{r['bootstrapCorrectedSDlo']:.4f}, {r['bootstrapCorrectedSDhi']:.4f}] | {r['averageWithinEpisodeVariance']:.4f} | {r['betweenShare'] if r['betweenShare'] != '' else '—'} | {r['historicalRhoThresholdSD']:.4f} | {'yes' if r['correctedPointMeetsHistoricalThreshold'] else 'no'} |"
        )
    md += [
        "",
        "## Interpretation",
        "",
        "The corrected quantities estimate heterogeneity among these fixed prompt configurations at the episode-outcome level. They are not protocol-matched human latent variances, do not justify a persona-population claim, and do not remove the need to label the Dal Bó–Fréchette comparator as nonmatched.",
        "",
        "Machine-readable results: `figure-sources/variance-correction.csv` and `.json`.",
    ]
    (OUT / "variance-correction.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return detail


def table_columns(db: sqlite3.Connection, table: str) -> list[str]:
    return [r[1] for r in db.execute(f"PRAGMA table_info({table})")]


def classify_phase(block: str | None, arm: str | None) -> str:
    b = (block or "").lower()
    a = (arm or "").lower()
    if a.startswith("p5") or b.startswith("p5"):
        return "phase5"
    if a.startswith("p4") or b in {"d1", "d2", "d3", "e", "f", "x2"}:
        return "phase4"
    if "sent" in a or b == "sentinel":
        return "sentinel_or_monitoring"
    if a.startswith("t3") or b.startswith("p3") or "phase3" in b:
        return "phase3"
    if a:
        return "legacy_or_other"
    return "unattributed"


def analysis_counts() -> dict:
    db = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    event_counts = {t: n for t, n in db.execute("SELECT type, COUNT(*) FROM events GROUP BY type ORDER BY type")}
    distinct_runs = db.execute("SELECT COUNT(DISTINCT run_id) FROM events WHERE run_id IS NOT NULL").fetchone()[0]
    completed_runs = db.execute("SELECT COUNT(DISTINCT run_id) FROM events WHERE type='run.completed'").fetchone()[0]
    invalid_runs = db.execute("SELECT COUNT(DISTINCT run_id) FROM events WHERE type='trial.invalidated'").fetchone()[0]
    round_events = event_counts.get("round.played", 0)
    llm_requests = event_counts.get("llm.requested", 0)

    run_meta: dict[str, dict] = {}
    request_rows = []
    for rid, payload in db.execute("SELECT run_id, payload FROM events WHERE type='llm.requested' ORDER BY rowid"):
        d = json.loads(payload)
        arm = d.get("armId")
        block = d.get("block")
        model = d.get("model") or "unknown"
        meta = run_meta.setdefault(rid, {"arm": arm, "block": block, "model": model})
        if meta.get("arm") is None and arm is not None:
            meta.update(arm=arm, block=block, model=model)
        request_rows.append((rid, arm, block, model, classify_phase(block, arm)))

    completed_ids = {r[0] for r in db.execute("SELECT DISTINCT run_id FROM events WHERE type='run.completed'")}
    invalid_ids = {r[0] for r in db.execute("SELECT DISTINCT run_id FROM events WHERE type='trial.invalidated'")}
    phase_requests = Counter(r[4] for r in request_rows)
    block_requests = Counter((r[2] or "(none)", r[3], r[4]) for r in request_rows)
    completed_by_phase = Counter()
    completed_by_block = Counter()
    for rid in completed_ids:
        meta = run_meta.get(rid, {})
        phase = classify_phase(meta.get("block"), meta.get("arm"))
        completed_by_phase[phase] += 1
        completed_by_block[(meta.get("block") or "(none)", meta.get("model") or "unknown", phase)] += 1

    block_rows = []
    keys = sorted(set(block_requests) | set(completed_by_block))
    for block, model, phase in keys:
        block_rows.append({
            "phase": phase,
            "block": block,
            "model": model,
            "llmRequestedEvents": block_requests[(block, model, phase)],
            "completedRuns": completed_by_block[(block, model, phase)],
        })
    write_csv(FIG / "count-reconciliation-by-block.csv", block_rows)

    budget = {}
    if BUDGET_DB.exists():
        bdb = sqlite3.connect(f"file:{BUDGET_DB}?mode=ro", uri=True)
        tables = [r[0] for r in bdb.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        budget["tables"] = {}
        for table in tables:
            cols = table_columns(bdb, table)
            budget["tables"][table] = {"columns": cols, "rows": bdb.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]}
        if "spend" in tables:
            cols = table_columns(bdb, "spend")
            numeric_totals = {}
            for col in ("calls", "input_tokens", "output_tokens", "tokens_in", "tokens_out", "cost", "usd"):
                if col in cols:
                    numeric_totals[col] = bdb.execute(f"SELECT COALESCE(SUM({col}),0) FROM spend").fetchone()[0]
            budget["spendTotals"] = numeric_totals
            dims = [c for c in ("block", "model") if c in cols]
            if dims and "calls" in cols:
                group_sql = ", ".join(dims)
                budget_rows = []
                for row in bdb.execute(f"SELECT {group_sql}, SUM(calls) FROM spend GROUP BY {group_sql} ORDER BY {group_sql}"):
                    rec = {dims[i]: row[i] for i in range(len(dims))}
                    rec["calls"] = row[-1]
                    budget_rows.append(rec)
                write_csv(FIG / "count-reconciliation-budget.csv", budget_rows)
        bdb.close()
    db.close()

    summary = {
        "engineDb": {
            "distinctRunIdsAnyEvent": distinct_runs,
            "completedDistinctRuns_replayObservations": completed_runs,
            "invalidatedDistinctRuns": invalid_runs,
            "roundPlayedEvents": round_events,
            "seatRoundDecisions": 2 * round_events,
            "llmRequestedEvents": llm_requests,
            "eventCounts": event_counts,
            "llmRequestsByPhaseHeuristic": dict(sorted(phase_requests.items())),
            "completedRunsByPhaseHeuristic": dict(sorted(completed_by_phase.items())),
        },
        "budgetDb": budget,
        "definitions": {
            "replayObservation": "one distinct completed run in the public replay contract",
            "roundPlayedEvent": "one simultaneous move pair",
            "seatRoundDecision": "one player action; two per round.played event",
            "llmRequestedEvent": "one archived provider request, including requests within multi-round episodes",
        },
    }
    (FIG / "count-reconciliation.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    md = [
        "# Count reconciliation",
        "",
        "> **STATUS: GENERATED FROM THE ARCHIVED EVENT AND BUDGET STORES — ZERO SUBJECT CALLS.** Counts use different nouns and scopes; none should be described generically as the number of subjects.",
        "",
        "## Full archived event store",
        "",
        "| unit | count | definition |",
        "|---|---:|---|",
        f"| distinct run IDs with any event | {distinct_runs:,} | any run identifier appearing in the event table |",
        f"| completed runs / replay observations | {completed_runs:,} | distinct run IDs with `run.completed` |",
        f"| invalidated runs | {invalid_runs:,} | distinct run IDs with `trial.invalidated` |",
        f"| round events | {round_events:,} | simultaneous move pairs recorded as `round.played` |",
        f"| seat-round decisions | {2 * round_events:,} | two player actions per round event |",
        f"| archived provider requests | {llm_requests:,} | `llm.requested` events; multi-round episodes contain many requests |",
        "",
        "## By phase heuristic",
        "",
        "| phase label | provider requests | completed runs |",
        "|---|---:|---:|",
    ]
    for phase in sorted(set(phase_requests) | set(completed_by_phase)):
        md.append(f"| {phase} | {phase_requests[phase]:,} | {completed_by_phase[phase]:,} |")
    md += [
        "",
        "Detailed block × model counts: `figure-sources/count-reconciliation-by-block.csv`. Budget-ledger totals, when present, are in `figure-sources/count-reconciliation-budget.csv`. Machine-readable summary: `figure-sources/count-reconciliation.json`.",
        "",
        "## Reporting rule",
        "",
        "Use `episodes/runs`, `round events`, `seat-round decisions`, `provider requests`, and `replay observations` only with their exact definitions and scope. The full-store provider-request count is not interchangeable with the Phase 4 transactional ledger or the Phase 5 episode count.",
    ]
    (OUT / "count-reconciliation.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return summary


def write_summary(results: dict) -> None:
    summary = {
        "generatedAt": "2026-07-29",
        "status": "post-adjudication zero-call submission sensitivities",
        "parameters": {
            "dirichletDrawsPerObservedCell": DIRICHLET_DRAWS,
            "familyPermutations": FAMILY_PERMUTATIONS,
            "varianceBootstraps": VAR_BOOTSTRAPS,
            "baseSeed": BASE_SEED,
        },
        "results": results,
    }
    (OUT / "submission-analysis-summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    if not DB.exists():
        raise SystemExit(f"missing staged event store: {DB}")
    runs = load_runs()
    personas = load_personas()
    col = collect(runs, personas)
    decisions = load_decisions()

    clustered = analysis_episode_cluster(runs, personas, col, decisions)
    p13 = analysis_p13_family(personas, col)
    variance = analysis_variance(personas, col, clustered)
    counts = analysis_counts()
    write_summary({
        "episodeCluster": clustered["summaries"],
        "p13Family": p13,
        "variance": variance,
        "counts": counts,
    })
    print(json.dumps({
        "episodeCluster": clustered["summaries"],
        "p13HistoricalGate": p13["historicalSeatGate_rawSlopeMax"],
        "p13ClusterGate": p13["episodeClusterBootstrapGate_rawSlopeMax"],
        "countHeadline": counts["engineDb"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
