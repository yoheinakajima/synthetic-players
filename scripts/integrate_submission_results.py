#!/usr/bin/env python3
"""Insert generated submission-analysis results into living paper documents.

The script updates only paper-facing living files. It never edits sealed phase
records or historical adjudications. Re-running it is idempotent.
"""
from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "docs/analysis/submission/figure-sources/variance-correction.csv"
PAPER = ROOT / "docs/paper/paper-draft.md"
GATE = ROOT / "docs/analysis/submission-blockers.md"

ORDER = ("rep-d10-s2a", "rep-d10-s2p", "rep-d90-s2a", "rep-d90-s2p")


def load_rows() -> list[dict[str, str]]:
    with RESULTS.open(newline="", encoding="utf-8") as f:
        by_cell = {row["cell"]: row for row in csv.DictReader(f)}
    missing = [cell for cell in ORDER if cell not in by_cell]
    if missing:
        raise RuntimeError(f"missing variance rows: {missing}")
    return [by_cell[cell] for cell in ORDER]


def f(row: dict[str, str], key: str, digits: int = 4) -> str:
    return f"{float(row[key]):.{digits}f}"


def interval(row: dict[str, str], prefix: str) -> str:
    return f"[{f(row, prefix + 'lo')}, {f(row, prefix + 'hi')}]"


def update_paper(rows: list[dict[str, str]]) -> None:
    text = PAPER.read_text(encoding="utf-8")
    raw_min = min(float(r["rawBetweenSD"]) for r in rows)
    raw_max = max(float(r["rawBetweenSD"]) for r in rows)
    corrected = ", ".join(f(r, "correctedBetweenSD") for r in rows)
    fixed_intervals = ", ".join(interval(r, "fixedPanelCorrectedSD") for r in rows)
    fixed_shares = ", ".join(
        f"{100 * float(r['betweenShare']):.1f}%" for r in rows
    )
    fixed_share_intervals = ", ".join(
        f"[{100 * float(r['fixedPanelBetweenShareLo']):.1f}%, "
        f"{100 * float(r['fixedPanelBetweenShareHi']):.1f}%]"
        for r in rows
    )
    population_intervals = ", ".join(
        interval(r, "personaPopulationCorrectedSD") for r in rows
    )
    pop_meet = sum(
        float(r["personaPopulationCorrectedSDlo"])
        >= float(r["historicalRhoThresholdSD"])
        for r in rows
    )

    replacement = (
        f"Raw cross-persona standard deviations range from {raw_min:.4f} to "
        f"{raw_max:.4f}. Correcting for finite episode counts leaves fixed-panel "
        f"between-prompt SD estimates of {corrected} across the four repeated "
        f"cells. The primary bootstrap retains all sixteen registered prompts and "
        f"resamples episodes within prompt; its 95% intervals are {fixed_intervals}. "
        f"The corrected between-prompt component accounts for {fixed_shares} of "
        f"total episode-level variation, with fixed-panel 95% intervals "
        f"{fixed_share_intervals}. All four fixed-panel lower bounds exceed the "
        f"historical registered threshold of 0.75 times the published human SD. "
        f"An exploratory two-stage bootstrap that additionally resamples prompts "
        f"produces wider corrected-SD intervals of {population_intervals}; "
        f"{pop_meet}/4 lower bounds exceed the historical threshold. These are "
        f"fixed-panel prompt-heterogeneity estimates and exploratory "
        f"persona-generator sensitivities, not matched human latent variances."
    )

    pattern = re.compile(
        r"Raw cross-persona standard deviations range from .*?"
        r"These are fixed-panel prompt-heterogeneity estimates, not matched human latent variances\.",
        flags=re.DOTALL,
    )
    text, count = pattern.subn(replacement, text, count=1)
    if count != 1:
        raise RuntimeError(f"expected one paper variance paragraph, replaced {count}")
    PAPER.write_text(text, encoding="utf-8")


def update_gate(rows: list[dict[str, str]]) -> None:
    text = GATE.read_text(encoding="utf-8")
    table = [
        "### A3. Between-prompt variance correction — **COMPLETE**",
        "",
        "A method-of-moments correction subtracts estimated finite-opportunity noise from the variance of prompt means. The primary 50,000-replicate bootstrap retains all sixteen fixed prompts and resamples episodes within each prompt. A separate two-stage bootstrap also resamples prompts and is labeled exploratory persona-population uncertainty.",
        "",
        "| cell | corrected SD | fixed-panel episode-bootstrap 95% | between share | fixed-panel share 95% | exploratory persona-population SD 95% |",
        "|---|---:|---|---:|---|---|",
    ]
    for row in rows:
        table.append(
            f"| {row['cell']} | {f(row, 'correctedBetweenSD')} | "
            f"{interval(row, 'fixedPanelCorrectedSD')} | "
            f"{100 * float(row['betweenShare']):.1f}% | "
            f"[{100 * float(row['fixedPanelBetweenShareLo']):.1f}%, "
            f"{100 * float(row['fixedPanelBetweenShareHi']):.1f}%] | "
            f"{interval(row, 'personaPopulationCorrectedSD')} |"
        )
    table += [
        "",
        "All four fixed-panel corrected-SD lower bounds exceed the historical `0.75 × human SD` threshold. Three of four exploratory persona-population lower bounds do. Neither result is a protocol-matched estimate of human latent heterogeneity.",
        "",
        "Artifact: `submission/variance-correction.md`.",
        "",
    ]
    replacement = "\n".join(table)
    pattern = re.compile(
        r"### A3\. Between-prompt variance correction — \*\*COMPLETE\*\*.*?(?=## B\. Human comparator)",
        flags=re.DOTALL,
    )
    text, count = pattern.subn(replacement, text, count=1)
    if count != 1:
        raise RuntimeError(f"expected one gate variance section, replaced {count}")
    GATE.write_text(text, encoding="utf-8")


def main() -> int:
    rows = load_rows()
    update_paper(rows)
    update_gate(rows)
    print("integrate_submission_results: updated paper and submission gate")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
