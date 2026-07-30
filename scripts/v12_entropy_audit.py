#!/usr/bin/env python3
"""Exact event-store audit of the registered Phase 5 choice-entropy secondary.

The first v12 draft attempted to reconstruct entropy from an aggregated curve
CSV and omitted bare lanes. This script instead repeats the adjudicator's event-
store calculation exactly, then adds a matched-lattice mean-within-unit entropy
that the registered pooled secondary did not report. It overwrites only the
post-adjudication v12 audit section and leaves every historical artifact intact.
"""
from __future__ import annotations

import csv
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "artifacts" / "api-server" / "engine"
sys.path.insert(0, str(ENGINE))

import phase5_closeout_adjudicate as adj  # noqa: E402

OUT = ROOT / "docs" / "analysis" / "submission" / "v12"
AUDIT_JSON = OUT / "v12-audits.json"
AUDIT_MD = OUT / "v12-audits.md"
CSV_OUT = OUT / "temperature-entropy.csv"
SUMMARY = ROOT / "docs" / "analysis" / "submission" / "submission-analysis-summary.json"
TEMPS = (0.7, 1.0, 1.3)


def h(counts: Counter) -> float:
    n = sum(counts.values())
    if not n:
        return 0.0
    value = 0.0
    for count in counts.values():
        if count:
            p = count / n
            value -= p * math.log2(p)
    return value


def main() -> int:
    runs = adj.load_runs()
    arms = adj.load_p5_arms()
    all_counts: dict[float, Counter] = defaultdict(Counter)
    unit_counts: dict[tuple[float, tuple[str, str, str | None]], Counter] = defaultdict(Counter)
    units_by_t: dict[float, set] = defaultdict(set)

    for run in runs.values():
        arm = arms.get(run["armId"])
        if not arm or not (run["completed"] and not run["invalid"] and run["round1"]):
            continue
        temperature = float(arm["temperature"])
        if temperature not in TEMPS:
            continue
        lane = "bare" if arm.get("personaId") is None else "persona"
        unit = (lane, arm["cell"], arm.get("personaId"))
        units_by_t[temperature].add(unit)
        for action in run["round1"]:
            all_counts[temperature][action] += 1
            unit_counts[(temperature, unit)][action] += 1

    matched_units = set.intersection(*(units_by_t[t] for t in TEMPS))
    records = []
    for temperature in TEMPS:
        matched_counts = Counter()
        matched_unit_entropies = []
        for unit in sorted(matched_units, key=str):
            counts = unit_counts[(temperature, unit)]
            matched_counts.update(counts)
            matched_unit_entropies.append(h(counts))
        records.append(
            {
                "temperature": temperature,
                "allUnits": len(units_by_t[temperature]),
                "allSeats": sum(all_counts[temperature].values()),
                "allPooledShannonBits": h(all_counts[temperature]),
                "matchedUnits": len(matched_units),
                "matchedSeats": sum(matched_counts.values()),
                "matchedPooledShannonBits": h(matched_counts),
                "matchedMeanUnitShannonBits": sum(matched_unit_entropies) / len(matched_unit_entropies),
                "matchedMedianUnitShannonBits": sorted(matched_unit_entropies)[len(matched_unit_entropies) // 2],
            }
        )

    expected = {
        0.7: (0.9057, 0.8310),
        1.0: (0.7868, 0.7822),
        1.3: (0.7766, 0.7698),
    }
    for row in records:
        pooled, matched = expected[row["temperature"]]
        if abs(row["allPooledShannonBits"] - pooled) > 0.00015:
            raise AssertionError(f"historical pooled entropy mismatch: {row}")
        if abs(row["matchedPooledShannonBits"] - matched) > 0.00015:
            raise AssertionError(f"historical matched entropy mismatch: {row}")

    result = {
        "status": "exact event-store recomputation",
        "definition": (
            "base-2 Shannon entropy H=-sum_a p(a)log2 p(a) over round-one recorded action indices; "
            "the registered secondary pooled all valid seat actions at each temperature"
        ),
        "matchedUnitDefinition": "intersection of (bare/persona lane, cell, personaId) units present at T=0.7, 1.0, and 1.3",
        "matchedUnits": [list(x) for x in sorted(matched_units, key=str)],
        "records": records,
        "registeredPooledDecline": True,
        "declineSurvivesMatchedComposition": True,
        "interpretation": (
            "The registered pooled entropy decline is partly composition-confounded but its direction survives on the "
            "identical sweep lattice. Mean within-unit entropy is reported separately because pooled entropy can remain "
            "high when different prompt-cell units occupy opposite boundaries. The observation remains exploratory and "
            "does not identify a temperature mechanism."
        ),
    }

    OUT.mkdir(parents=True, exist_ok=True)
    audit = json.loads(AUDIT_JSON.read_text(encoding="utf-8"))
    audit["entropy"] = result
    AUDIT_JSON.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    with CSV_OUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)

    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    summary.setdefault("results", {}).setdefault("v12IndependentAudits", {})["entropy"] = result
    SUMMARY.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    lines = AUDIT_MD.read_text(encoding="utf-8").split("## Temperature and choice entropy", 1)[0]
    table = [
        "## Temperature and choice entropy",
        "",
        result["definition"] + ".",
        "",
        "| T | all pooled entropy | all seats | matched pooled entropy | matched seats | mean within-unit entropy |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for row in records:
        table.append(
            f"| {row['temperature']:.1f} | {row['allPooledShannonBits']:.4f} | {row['allSeats']} | "
            f"{row['matchedPooledShannonBits']:.4f} | {row['matchedSeats']} | "
            f"{row['matchedMeanUnitShannonBits']:.4f} |"
        )
    table += ["", result["interpretation"], ""]
    AUDIT_MD.write_text(lines.rstrip() + "\n\n" + "\n".join(table), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
