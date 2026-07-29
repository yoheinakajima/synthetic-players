#!/usr/bin/env python3
"""Normalize labels and count scopes in generated submission analyses.

This does not alter any numerical result. It prevents two reporting mistakes:
1. `T_max > 0` under a raw-slope permutation is not the registered procedure's
   false-fire rate, so it is labeled only as the rate of any positive gated
   maximum under the null.
2. all archived completed runs are not identical to the Phase 4+5 public replay
   contract; the latter is the 2,864 + 1,712 subset.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "docs" / "analysis" / "submission"
FIG = OUT / "figure-sources"


def fix_p13() -> None:
    path = FIG / "p13-family-audit-final.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    for key in (
        "historicalSeatGate_rawSlopeMax",
        "episodeClusterBootstrapGate_rawSlopeMax",
    ):
        rec = doc[key]
        rec["nullAnyPositiveGatedMaximumRate"] = rec.pop("nullFalseFireRate")
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Final high-precision P5-3(a) family audit",
        "",
        "> **STATUS: POST-ADJUDICATION SENSITIVITY — ZERO SUBJECT CALLS.** The historical mechanical verdict is unchanged. This audit uses the same raw-slope statistic for the observed data and every permutation and reruns the full gate-plus-maximum-selection procedure over all 32 evaluable clause-(a) candidates.",
        "",
        "## Design",
        "",
        f"- Permutations: **{doc['historicalSeatGate_rawSlopeMax']['permutations']:,}**, seed `{doc['seed']}`.",
        "- Randomization: episode outcomes are permuted between δ=.90 and δ=.10 within each persona × wording candidate, preserving arm sizes.",
        "- Statistic: maximum positive raw difference in episode-mean round-one cooperation among candidates passing both condition gates.",
        "- Two gate sensitivities are reported: the historical seat-level Clopper–Pearson gate and the episode-level exact cluster-bootstrap gate.",
        "- Monte Carlo p-values use `(r+1)/(B+1)` and the table reports a Clopper–Pearson interval for simulation uncertainty.",
        "",
        "## Results",
        "",
        "| gate | observed max slope | argmax | passing candidates | exceedances / B | p | MC 95% interval | null 95th percentile of gated max |",
        "|---|---:|---|---|---:|---:|---|---:|",
    ]
    for key, label in (
        ("historicalSeatGate_rawSlopeMax", "Historical seat CP"),
        ("episodeClusterBootstrapGate_rawSlopeMax", "Episode cluster bootstrap"),
    ):
        s = doc[key]
        arg = "/".join(s["argmax"]) if s["argmax"] else "none"
        passing = ", ".join("/".join(x) for x in s["observedGatePassing"]) or "none"
        lines.append(
            f"| {label} | {s['observedTmaxRawSlope']:+.4f} | {arg} | {passing} | "
            f"{s['exceedances']:,}/{s['permutations']:,} | {s['pAddOne']:.6f} | "
            f"[{s['mcClopperPearson95'][0]:.6f}, {s['mcClopperPearson95'][1]:.6f}] | "
            f"{s['finiteTmaxQuantiles']['q95']:.4f} |"
        )
    lines += [
        "",
        "The two defensible gate definitions place the same archived maximum on opposite sides of 0.05. Under the historical seat-level gate, the observed value equals the null 95th percentile and the familywise permutation p-value is about 0.060. Under the episode-cluster gate, the p-value is about 0.043. This gate dependence is itself the correct result to report.",
        "",
        "## Status rule",
        "",
        "This is a post-adjudication sensitivity selected after external review identified the family-error omission. Regardless of its numerical outcome, it does not retroactively convert p13 into a prospectively family-controlled confirmatory result. p13 remains a preregistered replication target; the audit determines how strongly the archived data support that target after selection is accounted for.",
        "",
        "Complete candidate table: `figure-sources/p13-family-candidates-final.csv`. Machine-readable summary: `figure-sources/p13-family-audit-final.json`.",
    ]
    (OUT / "p13-family-audit-final.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def fix_counts() -> None:
    path = FIG / "count-reconciliation.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    eng = doc["engineDb"]
    completed = eng.pop("completedDistinctRuns_replayObservations")
    eng["archivedCompletedDistinctRuns"] = completed
    replay = (
        eng["completedRunsByPhaseHeuristic"].get("phase4", 0)
        + eng["completedRunsByPhaseHeuristic"].get("phase5", 0)
    )
    eng["publicPhase4PlusPhase5ReplayContractRuns"] = replay

    budget_csv = FIG / "count-reconciliation-budget.csv"
    phase4_calls = phase5_calls = 0
    if budget_csv.exists():
        with budget_csv.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                calls = int(row["calls"])
                if row["block"].startswith("P5"):
                    phase5_calls += calls
                else:
                    phase4_calls += calls
    budget = doc.get("budgetDb", {})
    budget["programPhaseTotals"] = {
        "phase4IncludingX2SentinelsAndInfra": phase4_calls,
        "phase5IncludingEntryAndSentinels": phase5_calls,
        "phase4PlusPhase5": phase4_calls + phase5_calls,
    }
    doc["definitions"]["replayObservation"] = (
        "one completed run in the public Phase 4+5 replay contract; the archived "
        "store also contains earlier completed runs outside that contract"
    )
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")

    totals = budget.get("spendTotals", {})
    phase_counts = eng["completedRunsByPhaseHeuristic"]
    req_counts = eng["llmRequestsByPhaseHeuristic"]
    lines = [
        "# Count reconciliation",
        "",
        "> **STATUS: GENERATED FROM THE ARCHIVED EVENT AND BUDGET STORES — ZERO SUBJECT CALLS.** Counts use different nouns and scopes; none should be described generically as the number of subjects.",
        "",
        "## Full archived event store",
        "",
        "| unit | count | definition |",
        "|---|---:|---|",
        f"| distinct run IDs with any event | {eng['distinctRunIdsAnyEvent']:,} | any run identifier appearing in the event table |",
        f"| archived completed runs | {eng['archivedCompletedDistinctRuns']:,} | all distinct run IDs with `run.completed`, including earlier phases |",
        f"| public Phase 4+5 replay observations | {replay:,} | 2,864 Phase 4 plus 1,712 Phase 5 completed runs covered by the public replay contract |",
        f"| invalidated runs | {eng['invalidatedDistinctRuns']:,} | distinct run IDs with `trial.invalidated` |",
        f"| round events | {eng['roundPlayedEvents']:,} | simultaneous move pairs recorded as `round.played` |",
        f"| seat-round decisions | {eng['seatRoundDecisions']:,} | two player actions per round event |",
        f"| archived provider-request events | {eng['llmRequestedEvents']:,} | all `llm.requested` events in the full store |",
        "",
        "## Phase 4+5 transactional budget ledger",
        "",
        "| scope | calls |",
        "|---|---:|",
        f"| Phase 4, including X2, sentinels, and infrastructure | {phase4_calls:,} |",
        f"| Phase 5, including entry and sentinels | {phase5_calls:,} |",
        f"| **Phase 4+5 total** | **{phase4_calls + phase5_calls:,}** |",
        "",
        f"The same ledger records **{int(totals.get('input_tokens', 0)):,} input tokens** and **{int(totals.get('output_tokens', 0)):,} output tokens**. It is narrower than the full event store because earlier phases were not recorded in this transactional ledger.",
        "",
        "## By phase heuristic in the event store",
        "",
        "| phase label | provider requests | completed runs |",
        "|---|---:|---:|",
    ]
    for phase in sorted(set(req_counts) | set(phase_counts)):
        lines.append(f"| {phase} | {req_counts.get(phase, 0):,} | {phase_counts.get(phase, 0):,} |")
    lines += [
        "",
        "Detailed block × model counts: `figure-sources/count-reconciliation-by-block.csv`. Budget-ledger totals are in `figure-sources/count-reconciliation-budget.csv`. Machine-readable summary: `figure-sources/count-reconciliation.json`.",
        "",
        "## Reporting rule",
        "",
        "Use `episodes/runs`, `round events`, `seat-round decisions`, `provider requests`, `transactional ledger calls`, and `replay observations` only with their exact definitions and scope. In particular, 5,505 archived completed runs are not the same quantity as the 4,576-run Phase 4+5 public replay contract, and 36,251 archived request events are not the same scope as the 30,530-call Phase 4+5 transactional ledger.",
    ]
    (OUT / "count-reconciliation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def fix_summary() -> None:
    path = OUT / "submission-analysis-summary.json"
    if not path.exists():
        return
    doc = json.loads(path.read_text(encoding="utf-8"))
    for key in (
        "historicalSeatGate_rawSlopeMax",
        "episodeClusterBootstrapGate_rawSlopeMax",
    ):
        rec = doc["results"]["p13Family"][key]
        if "nullFalseFireRate" in rec:
            rec["nullAnyPositiveGatedMaximumRate"] = rec.pop("nullFalseFireRate")
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    fix_p13()
    fix_counts()
    fix_summary()
    print("submission_gate_finalize: labels and count scopes normalized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
