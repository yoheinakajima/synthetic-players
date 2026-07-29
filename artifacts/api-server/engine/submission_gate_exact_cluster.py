#!/usr/bin/env python3
"""Exact episode-level sensitivity for Phase 5 round-one outcomes.

Why this file exists: an ordinary percentile cluster bootstrap can be degenerate
when all observed episodes in a cell agree. That reproduces the original error
of treating zero observed variation as zero policy uncertainty. This script
therefore makes the primary cluster sensitivity an exact, conservative
confidence interval for the mean of the three-valued episode outcome.

For Y in {0, .5, 1}, define A=1[Y>=.5] and B=1[Y=1]. Then
E[Y]=(E[A]+E[B])/2. We construct simultaneous Clopper-Pearson intervals for
E[A] and E[B] and project them onto E[Y]. Bonferroni guarantees at least the
stated coverage without assuming independence between the two seat decisions.

Historical registered verdicts are never changed.
"""
from __future__ import annotations

import csv
import json
import math
import os
import sys
from collections import Counter, defaultdict
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
    P52_LB,
    P52_UB,
    THETA_1,
    THETA_2,
    TIER_A_CELLS,
    collect,
    gate_cell,
    load_p5_arms,
    load_personas,
    load_runs,
    valid_runs_by,
)

OUT = ROOT / "docs" / "analysis" / "submission"
FIG = OUT / "figure-sources"
DECISIONS = ROOT / "docs" / "phase5-close" / "adjudication-decisions.json"
ALPHA = 0.05
B = int(os.environ.get("SUBMISSION_FAMILY_PERMUTATIONS", "200000"))
BATCH = int(os.environ.get("SUBMISSION_FAMILY_BATCH", "5000"))
SEED = 20260783
LEVELS = ("s2a", "s2p")


def cp_two_sided(k: int, n: int, alpha: float) -> tuple[float, float]:
    if n <= 0:
        return 0.0, 1.0
    lo = 0.0 if k == 0 else float(beta.ppf(alpha / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - alpha / 2, k + 1, n - k))
    return lo, hi


def cp_one_sided_lower(k: int, n: int, alpha: float) -> float:
    if n <= 0 or k == 0:
        return 0.0
    return float(beta.ppf(alpha, k, n - k + 1))


def episode_counts(values: Iterable[float]) -> tuple[int, int, int]:
    c = Counter(round(float(v) * 2) for v in values)
    bad = sorted(x for x in c if x not in (0, 1, 2))
    if bad:
        raise ValueError(f"unexpected episode outcomes: {bad}")
    return c.get(0, 0), c.get(1, 0), c.get(2, 0)


def exact_mean_interval(values: Iterable[float], alpha: float = ALPHA) -> tuple[float, float]:
    """At-least-(1-alpha) interval for E[Y] with Y in {0,.5,1}.

    A=1[Y>=.5], B=1[Y=1], E[Y]=(E[A]+E[B])/2. Each component gets alpha/2
    family error, and each component interval is two-sided CP.
    """
    c0, c1, c2 = episode_counts(values)
    n = c0 + c1 + c2
    component_alpha = alpha / 2
    a_lo, a_hi = cp_two_sided(c1 + c2, n, component_alpha)
    b_lo, b_hi = cp_two_sided(c2, n, component_alpha)
    return (a_lo + b_lo) / 2, (a_hi + b_hi) / 2


def exact_mean_lower(values: Iterable[float], alpha: float) -> float:
    """One-sided lower bound with Bonferroni over the A/B components."""
    c0, c1, c2 = episode_counts(values)
    n = c0 + c1 + c2
    component_alpha = alpha / 2
    return (
        cp_one_sided_lower(c1 + c2, n, component_alpha)
        + cp_one_sided_lower(c2, n, component_alpha)
    ) / 2


def exact_gate(values: Iterable[float]) -> dict:
    vals = [float(v) for v in values]
    lo, hi = exact_mean_interval(vals)
    c0, c1, c2 = episode_counts(vals)
    return {
        "episodes": len(vals),
        "counts_0_half_1": [c0, c1, c2],
        "mean": float(np.mean(vals)) if vals else None,
        "interval95": [lo, hi],
        "interior": bool(vals and lo > GATE_LO and hi < GATE_HI),
    }


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
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
    groups["__pooled__"] = [v for key, vals in groups.items() if key != "__pooled__" for v in vals]
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


def update_episode_report(runs: dict, personas: dict, col: dict, decisions: dict) -> dict:
    eps_a = col["epsA"]
    generated = FIG / "episode-cluster-cells.csv"
    prior_rows = {}
    if generated.exists():
        with generated.open(newline="", encoding="utf-8") as f:
            prior_rows = {(r["personaId"], r["cell"]): r for r in csv.DictReader(f)}

    rows = []
    changes_exact = []
    for pid in sorted(personas):
        for cell in TIER_A_CELLS:
            vals = eps_a[(pid, cell)]
            hist = gate_cell(vals)
            exact = exact_gate(vals)
            old = prior_rows.get((pid, cell), {})
            if hist["interior"] != exact["interior"]:
                changes_exact.append(f"{pid}|{cell}")
            row = dict(old)
            row.update({
                "personaId": pid,
                "cell": cell,
                "episodes": len(vals),
                "episodeCounts0": exact["counts_0_half_1"][0],
                "episodeCountsHalf": exact["counts_0_half_1"][1],
                "episodeCounts1": exact["counts_0_half_1"][2],
                "mean": round(float(np.mean(vals)), 6),
                "historicalSeatInterior": int(hist["interior"]),
                "historicalSeatCPlo": round(hist["cp95"][0], 6),
                "historicalSeatCPhi": round(hist["cp95"][1], 6),
                "episodeExactInterior": int(exact["interior"]),
                "episodeExactLo": round(exact["interval95"][0], 6),
                "episodeExactHi": round(exact["interval95"][1], 6),
            })
            rows.append(row)
    write_csv(generated, rows)

    restricted_cells = decisions["p51aRestrictedCells"]
    restricted = [r for r in rows if r["cell"] in restricted_cells]

    def sum_method(field: str) -> dict:
        ri = sum(int(r[field]) for r in restricted)
        ui = sum(int(r[field]) for r in rows)
        return {
            "restrictedInterior": ri,
            "restrictedN": len(restricted),
            "restrictedFraction": ri / len(restricted),
            "unrestrictedInterior": ui,
            "unrestrictedN": len(rows),
            "historicalPredicateWouldSupport": ri / len(restricted) < THETA_1,
        }

    summaries = {
        "historical": sum_method("historicalSeatInterior"),
        "episodeExact": sum_method("episodeExactInterior"),
    }
    if rows and "clusterBootstrapInterior" in rows[0]:
        summaries["discardedPercentileBootstrap"] = sum_method("clusterBootstrapInterior")
    if rows and "dirichletJeffreysInterior" in rows[0]:
        summaries["dirichletJeffreys"] = sum_method("dirichletJeffreysInterior")

    conflict = episode_conflict_series(runs, personas, decisions)
    conflict_rows = []
    for key, vals in sorted(conflict.items()):
        lo, hi = exact_mean_interval(vals)
        verdict = "task-dominant" if lo >= P52_LB else "persona-dominant" if hi <= P52_UB else "mixed"
        conflict_rows.append({
            "conflictCell": key,
            "episodes": len(vals),
            "meanTaskConsistentSeatShare": round(float(np.mean(vals)), 6),
            "episodeExactLo": round(lo, 6),
            "episodeExactHi": round(hi, 6),
            "episodeExactVerdict": verdict,
        })
    write_csv(FIG / "episode-exact-p52.csv", conflict_rows)

    refusal = episode_refusal_series(runs)
    m = len(refusal)
    refusal_rows = []
    for (pid, temp), vals in sorted(refusal.items()):
        lo, hi = exact_mean_interval(vals)
        family_lower = exact_mean_lower(vals, ALPHA / m)
        refusal_rows.append({
            "personaId": pid,
            "temperature": temp,
            "episodes": len(vals),
            "meanRefusalSeatShare": round(float(np.mean(vals)), 6),
            "episodeExactLo": round(lo, 6),
            "episodeExactHi": round(hi, 6),
            "familywiseOneSidedLower": round(family_lower, 6),
            "passesUnadjusted": int(lo >= THETA_2),
            "passesFamilywise": int(family_lower >= THETA_2),
        })
    write_csv(FIG / "episode-exact-clause-b.csv", refusal_rows)

    labels = [
        ("historical", "Historical seat-level CP"),
        ("episodeExact", "Episode exact CP projection"),
    ]
    if "discardedPercentileBootstrap" in summaries:
        labels.append(("discardedPercentileBootstrap", "Percentile cluster bootstrap (discarded as primary)"))
    if "dirichletJeffreys" in summaries:
        labels.append(("dirichletJeffreys", "Episode Dirichlet–Jeffreys sensitivity"))

    lines = [
        "# Episode-clustered sensitivity for Phase 5 round-one claims",
        "",
        "> **STATUS: POST-ADJUDICATION SENSITIVITY — ZERO SUBJECT CALLS.** Historical registered verdicts are unchanged. The primary episode-level interval is an exact conservative projection: for the three-valued episode outcome Y∈{0,.5,1}, write Y=(1[Y≥.5]+1[Y=1])/2, construct simultaneous Clopper–Pearson intervals for both binary components, and project them onto E[Y].",
        "",
        "## Why the initially generated percentile bootstrap is not primary",
        "",
        "An ordinary nonparametric percentile bootstrap becomes degenerate when every sampled episode has the same outcome. It therefore does not quantify policy uncertainty at the exact corners and was rejected before integration into the paper. Its output is retained in the table as an audit trail, not used as the submission inference.",
        "",
        "## P5-1a census",
        "",
        "| method | restricted interior / n | restricted fraction | would historical `<0.10` rule support? | all-cell interior / 96 |",
        "|---|---:|---:|---|---:|",
    ]
    for key, label in labels:
        s = summaries[key]
        lines.append(
            f"| {label} | {s['restrictedInterior']}/{s['restrictedN']} | {s['restrictedFraction']:.4f} | {'yes' if s['historicalPredicateWouldSupport'] else 'no'} | {s['unrestrictedInterior']}/{s['unrestrictedN']} |"
        )
    lines += [
        "",
        f"Cells changing classification between the historical seat-level rule and the exact episode interval: **{len(changes_exact)}**. Complete cell table: `figure-sources/episode-cluster-cells.csv`.",
        "",
        "## P5-2 and clause (b)",
        "",
        "Episode-exact P5-2 results are in `figure-sources/episode-exact-p52.csv`. Clause-(b) intervals, including a simultaneous one-sided lower bound across all evaluable persona × temperature lanes, are in `figure-sources/episode-exact-clause-b.csv`.",
        "",
        "## Interpretation rule",
        "",
        "The exact episode sensitivity is reported beside the historical mechanical verdict. It is not entered into the dead-predictions count and does not rewrite sealed reports. Any disagreement among defensible interval constructions is treated as method sensitivity, not resolved by choosing the favorable method.",
    ]
    (OUT / "episode-cluster-sensitivity.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"rows": rows, "summaries": summaries, "changesExact": changes_exact, "conflict": conflict_rows, "refusal": refusal_rows}


def gate_lookup(n: int, kind: str) -> np.ndarray:
    arr = np.zeros((n + 1, n + 1), dtype=bool)
    for c0 in range(n + 1):
        for c1 in range(n - c0 + 1):
            c2 = n - c0 - c1
            vals = [0.0] * c0 + [0.5] * c1 + [1.0] * c2
            if kind == "historical":
                arr[c0, c1] = gate_cell(vals)["interior"]
            elif kind == "exact":
                arr[c0, c1] = exact_gate(vals)["interior"]
            else:
                raise ValueError(kind)
    return arr


def mc_interval(r: int, b: int, alpha: float = ALPHA) -> tuple[float, float]:
    lo = 0.0 if r == 0 else float(beta.ppf(alpha / 2, r, b - r + 1))
    hi = 1.0 if r == b else float(beta.ppf(1 - alpha / 2, r + 1, b - r))
    return lo, hi


def final_family_audit(personas: dict, col: dict) -> dict:
    eps_a = col["epsA"]
    candidates: dict[tuple[str, str], tuple[np.ndarray, np.ndarray]] = {}
    for pid in sorted(personas):
        for lvl in LEVELS:
            candidates[(pid, lvl)] = (
                np.asarray(eps_a[(pid, f"rep-d90-{lvl}")], dtype=float),
                np.asarray(eps_a[(pid, f"rep-d10-{lvl}")], dtype=float),
            )
    ns = sorted({len(x) for pair in candidates.values() for x in pair})
    lookups = {kind: {n: gate_lookup(n, kind) for n in ns} for kind in ("historical", "exact")}

    def observed(kind: str):
        best, arg, gated = -math.inf, None, []
        for key, (g90, g10) in candidates.items():
            gate = (
                gate_cell(g90.tolist())["interior"] and gate_cell(g10.tolist())["interior"]
                if kind == "historical"
                else exact_gate(g90.tolist())["interior"] and exact_gate(g10.tolist())["interior"]
            )
            if gate:
                gated.append(key)
                slope = float(g90.mean() - g10.mean())
                if slope > best:
                    best, arg = slope, key
        return best, arg, gated

    observed_results = {kind: observed(kind) for kind in ("historical", "exact")}
    rng = np.random.default_rng(SEED)
    exceed = {kind: 0 for kind in observed_results}
    finite_values = {kind: [] for kind in observed_results}
    done = 0
    while done < B:
        b = min(BATCH, B - done)
        tmax = {kind: np.full(b, -np.inf) for kind in observed_results}
        for _key, (g90, g10) in candidates.items():
            pool = np.rint(np.concatenate([g90, g10]) * 2).astype(np.int8)
            n90, n10 = len(g90), len(g10)
            total = np.bincount(pool, minlength=3)
            random_keys = rng.random((b, len(pool)))
            idx = np.argpartition(random_keys, n90 - 1, axis=1)[:, :n90]
            selected = pool[idx]
            c1_90 = np.sum(selected == 1, axis=1)
            c2_90 = np.sum(selected == 2, axis=1)
            c0_90 = n90 - c1_90 - c2_90
            c0_10 = total[0] - c0_90
            c1_10 = total[1] - c1_90
            c2_10 = total[2] - c2_90
            slope = (0.5 * c1_90 + c2_90) / n90 - (0.5 * c1_10 + c2_10) / n10
            for kind in observed_results:
                gate = lookups[kind][n90][c0_90, c1_90] & lookups[kind][n10][c0_10, c1_10]
                tmax[kind] = np.maximum(tmax[kind], np.where(gate, slope, -np.inf))
        for kind, vals in tmax.items():
            obs = observed_results[kind][0]
            if math.isfinite(obs):
                exceed[kind] += int(np.sum(vals >= obs))
            finite_values[kind].extend(vals[np.isfinite(vals)].tolist())
        done += b

    result = {
        "family": {"registeredEligibleClauseA": 96, "evaluableClauseA": 32, "clauseBAnalyzedSeparately": True},
        "permutations": B,
        "seed": SEED,
    }
    for kind, out_key in (("historical", "historicalSeatGate_rawSlopeMax"), ("exact", "episodeExactCPGate_rawSlopeMax")):
        obs, arg, gated = observed_results[kind]
        r = exceed[kind]
        p = (r + 1) / (B + 1) if math.isfinite(obs) else None
        ci = mc_interval(r, B) if math.isfinite(obs) else (None, None)
        vals = np.asarray(finite_values[kind], dtype=float)
        result[out_key] = {
            "observedTmaxRawSlope": obs if math.isfinite(obs) else None,
            "argmax": list(arg) if arg else None,
            "observedGatePassing": [list(x) for x in gated],
            "exceedances": r if math.isfinite(obs) else None,
            "pAddOne": p,
            "mcClopperPearson95": list(ci),
            "nullAnyGateRate": len(vals) / B,
            "finiteTmaxQuantiles": ({q: float(v) for q, v in zip(("q50", "q90", "q95", "q99"), np.quantile(vals, [.5, .9, .95, .99]))} if len(vals) else {}),
        }
    (FIG / "p13-family-audit-final.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Final high-precision P5-3(a) family audit",
        "",
        "> **STATUS: POST-ADJUDICATION SENSITIVITY — ZERO SUBJECT CALLS.** Historical mechanical verdicts are unchanged. The audit uses the same raw-slope statistic for observed and permuted data and reruns the full gate-plus-maximum-selection procedure over all 32 evaluable clause-(a) candidates.",
        "",
        "## Design",
        "",
        f"- Permutations: **{B:,}**, seed `{SEED}`.",
        "- Episode outcomes are permuted between δ=.90 and δ=.10 within each persona × wording candidate, preserving arm sizes.",
        "- Statistic: maximum raw difference in episode-mean round-one cooperation among candidates passing both condition gates.",
        "- Gates: the historical seat-level Clopper–Pearson rule and the primary episode-exact CP projection.",
        "- Monte Carlo p-values use `(r+1)/(B+1)` with an exact interval for Monte Carlo uncertainty.",
        "",
        "## Results",
        "",
        "| gate | observed max slope | argmax | passing candidates | exceedances / B | p | MC 95% interval | null 95th percentile |",
        "|---|---:|---|---|---:|---:|---|---:|",
    ]
    for key, label in (("historicalSeatGate_rawSlopeMax", "Historical seat CP"), ("episodeExactCPGate_rawSlopeMax", "Episode exact CP projection")):
        rec = result[key]
        if rec["observedTmaxRawSlope"] is None:
            lines.append(f"| {label} | — | none | none | — | — | — | — |")
            continue
        arg = "/".join(rec["argmax"])
        passing = ", ".join("/".join(x) for x in rec["observedGatePassing"]) or "none"
        lines.append(
            f"| {label} | {rec['observedTmaxRawSlope']:+.4f} | {arg} | {passing} | {rec['exceedances']:,}/{B:,} | {rec['pAddOne']:.6f} | [{rec['mcClopperPearson95'][0]:.6f}, {rec['mcClopperPearson95'][1]:.6f}] | {rec['finiteTmaxQuantiles'].get('q95', float('nan')):.4f} |"
        )
    lines += [
        "",
        "## Status",
        "",
        "This family analysis was specified after external review identified the frozen rule's multiplicity defect. It cannot retroactively create a prospectively family-controlled result. Its purpose is to quantify how much support remains in the archived data under explicit cluster-level inference. p13 remains a replication target regardless of the numerical result.",
        "",
        "Machine-readable summary: `figure-sources/p13-family-audit-final.json`.",
    ]
    (OUT / "p13-family-audit-final.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return result


def update_summary(exact: dict, p13: dict) -> None:
    path = OUT / "submission-analysis-summary.json"
    doc = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    doc.setdefault("results", {})["episodeExact"] = exact["summaries"]
    doc["results"]["p13FamilyFinalExact"] = p13
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    runs = load_runs()
    personas = load_personas()
    col = collect(runs, personas)
    decisions = load_decisions()
    exact = update_episode_report(runs, personas, col, decisions)
    p13 = final_family_audit(personas, col)
    update_summary(exact, p13)
    print(json.dumps({"episodeExact": exact["summaries"], "p13": p13}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
