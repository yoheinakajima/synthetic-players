#!/usr/bin/env python3
"""Apply the Round 8 micro-fixes and preserve the v10 text freeze.

This script runs after earlier reviewer-integration scripts. It edits only living
manuscript/navigation/support files and is idempotent. It never modifies sealed
registrations, historical adjudications, raw event data, or precommitted text.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "docs/paper/paper-draft.md"
README = ROOT / "README.md"
REVIEW = ROOT / "REVIEW.md"
INDEX = ROOT / "docs/analysis/INDEX.md"
STATUS = ROOT / "docs/analysis/submission-blockers.md"
PDF_README = ROOT / "docs/paper/PDF-README.md"
REVIEWS = ROOT / "docs/reviews/README.md"
COUNT = ROOT / "docs/analysis/submission/count-reconciliation.md"
CITATION = ROOT / "CITATION.cff"
HEADER = ROOT / "docs/paper/review-draft-header.tex"


def replace_all(path: Path, replacements: list[tuple[str, str]]) -> None:
    text = path.read_text(encoding="utf-8")
    for old, new in replacements:
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")


def update_paper() -> None:
    text = PAPER.read_text(encoding="utf-8")
    text = text.replace(
        "WORKING DRAFT v8 — INDEPENDENT REPOSITORY REVIEW DRAFT, NOT FOR CITATION.",
        "TEXT FREEZE v10 — EXPLORE SCIENCE REVIEW COPY, NOT FOR CITATION.",
    )
    text = text.replace(
        "WORKING DRAFT v9 — TEXT-FREEZE CANDIDATE, NOT FOR CITATION.",
        "TEXT FREEZE v10 — EXPLORE SCIENCE REVIEW COPY, NOT FOR CITATION.",
    )
    text = text.replace("We report a five-stage research program.", "We report a five-phase research program.")
    text = text.replace(
        "the registered criteria could be satisfied through composition",
        "the broad-reference marginal criteria could be satisfied through composition",
    )
    text = text.replace(
        "the registered checks could be passed without estimating",
        "the broad-reference marginal checks could be passed without estimating",
    )
    text = text.replace(
        "all permutation p-values use the add-one convention, \\(r+1\\)/(B+1), with exact Monte Carlo intervals.",
        "all permutation p-values use the add-one convention, \\(\\widehat p=(r+1)/(B+1)\\), with exact Monte Carlo intervals.",
    )
    text = text.replace(
        "all permutation p-values use the add-one convention, \\(r+1)/(B+1)\\), with exact Monte Carlo intervals.",
        "all permutation p-values use the add-one convention, \\(\\widehat p=(r+1)/(B+1)\\), with exact Monte Carlo intervals.",
    )

    cheap = (
        "Here, “cheap” denotes evidentiary economy rather than only low API cost: "
        "the broad-reference marginal checks could be passed without estimating the "
        "treatment-response object they might be taken to validate."
    )
    if cheap not in text:
        marker = "\n**Contributions.**"
        if marker not in text:
            raise RuntimeError("missing Contributions marker")
        text = text.replace(marker, "\n" + cheap + "\n" + marker, 1)

    two_readings = (
        "These numbers have two distinct readings. For the finite archived panel, the contrasts "
        "+0.083 and +0.078 are exact descriptive arithmetic and require no sampling interval. "
        "For inference about the latent cooperation propensities of these sixteen configurations "
        "under repeated sampling, the conservative exact intervals span roughly [−0.17, +0.33]. "
        "A plug-in or asymptotic clustered interval that treats zero observed within-cell variation "
        "as zero latent variance can be much narrower by construction; we do not use that as the "
        "primary uncertainty model because six agreeing episodes do not establish a deterministic "
        "boundary policy."
    )
    if two_readings not in text:
        marker = "\nDal Bó and Fréchette [2011] remain useful"
        if marker not in text:
            raise RuntimeError("missing human-comparator marker")
        text = text.replace(marker, "\n" + two_readings + "\n" + marker, 1)

    old_attainability = (
        "An exhaustive attainability audit shows that with six episodes per condition, the exact gate "
        "admits sample means only from 0.333 to 0.667, so two eligible cells can differ by at most 0.333. "
        "Under the archived 32-candidate null structure, the estimated familywise tail probability at "
        "that maximum attainable slope is 0.075040; no exact-gate result in this archived family can reach 0.05."
    )
    new_attainability = (
        "An exhaustive attainability audit shows that, with six episodes per condition, 12 of the 28 "
        "possible episode-value compositions pass the exact gate. Their sample means range from 0.333 "
        "to 0.667, but eligibility depends on the full \\({0,0.5,1}\\) composition rather than on the "
        "mean alone. Two eligible cells can therefore differ by at most 0.333. Under the archived "
        "32-candidate null structure, the add-one familywise tail probability at that maximum attainable "
        "slope is 0.075040, with Monte Carlo 95% interval [0.073884, 0.076198]; no exact-gate result in "
        "this archived family can reach 0.05."
    )
    text = text.replace(old_attainability, new_attainability)

    old_counts = (
        "For Phase 4–5, the event record contains complete rendered prompts, bundle and request-body "
        "SHA-256 values, engine commit and provider route, raw completion text, and provider response IDs "
        "for 30,397 of 30,397 recorded response events."
    )
    new_counts = (
        "For Phase 4–5, the event record contains 30,421 normal `llm.requested` events and 30,397 "
        "`llm.responded` events; the 24-event difference is the disclosed set of provider-failure partials. "
        "The response records contain complete rendered prompts, bundle and request-body SHA-256 values, "
        "engine commit and provider route, raw completion text, and provider response IDs for all 30,397 "
        "responses. The separate budget ledger records 30,530 call attempts, including Phase 4 "
        "infrastructure and spend-accounting entries outside the standard request-event stream, so it is "
        "not row-identical to either event count."
    )
    text = text.replace(old_counts, new_counts)

    old_a4 = (
        "At n=6, exhaustive enumeration limits exact-gate-eligible cell means to [0.333, 0.667] and the "
        "largest eligible slope to 0.333; under the archived family, even that maximum has estimated null "
        "tail probability 0.075040."
    )
    new_a4 = (
        "At n=6, 12 of the 28 possible episode-value compositions pass the exact gate; their means span "
        "[0.333, 0.667], but eligibility depends on the full {0, 0.5, 1} composition rather than the mean "
        "alone. The largest eligible slope is 0.333; under the archived family, even that maximum has "
        "add-one tail probability 0.075040 with Monte Carlo 95% interval [0.073884, 0.076198]."
    )
    text = text.replace(old_a4, new_a4)

    text = text.replace("*End of working draft v8.*", "*End of text-freeze review copy v10.*")
    text = text.replace("*End of working draft v9.*", "*End of text-freeze review copy v10.*")
    PAPER.write_text(text, encoding="utf-8")


def update_count_glossary() -> None:
    text = COUNT.read_text(encoding="utf-8")
    block = """## Phase 4+5 request, response, and spending counts

| unit | count | definition |
|---|---:|---|
| Phase 4+5 normal request events | 30,421 | `llm.requested` events assigned to Phase 4 or Phase 5 in the event store |
| Phase 4+5 response events | 30,397 | `llm.responded` events with archived raw completion text and provider response IDs |
| provider-failure partials | 24 | request events without a normal response event; disclosed and excluded from completed-run replay |
| Phase 4+5 transactional ledger calls | 30,530 | spending-accounting call attempts, including Phase 4 infrastructure entries outside the standard request-event stream |

These totals answer different questions. Request and response events describe the event stream; ledger calls describe budget accounting. They are related but not row-identical.

"""
    if "## Phase 4+5 request, response, and spending counts" not in text:
        marker = "## Phase 4+5 transactional budget ledger"
        if marker not in text:
            raise RuntimeError("missing count-glossary insertion marker")
        text = text.replace(marker, block + marker, 1)
    text = text.replace(
        "Use `episodes/runs`, `round events`, `seat-round decisions`, `provider requests`, `transactional ledger calls`, and `replay observations` only with their exact definitions and scope.",
        "Use `episodes/runs`, `round events`, `seat-round decisions`, `provider requests`, `response events`, `provider-failure partials`, `transactional ledger calls`, and `replay observations` only with their exact definitions and scope.",
    )
    COUNT.write_text(text, encoding="utf-8")


def update_navigation() -> None:
    for path in (README, REVIEW, INDEX, STATUS, PDF_README, CITATION):
        text = path.read_text(encoding="utf-8")
        text = text.replace("synthetic-players-review-draft-v8.pdf", "synthetic-players-review-v10.pdf")
        text = text.replace("synthetic-players-review-draft-v9.pdf", "synthetic-players-review-v10.pdf")
        text = text.replace("Current v8 Markdown manuscript", "Current v10 frozen Markdown manuscript")
        text = text.replace("Current v9 Markdown manuscript", "Current v10 frozen Markdown manuscript")
        text = text.replace("v8 Markdown manuscript", "v10 frozen Markdown manuscript")
        text = text.replace("v9 Markdown manuscript", "v10 frozen Markdown manuscript")
        text = text.replace("phase5-review-v8", "phase5-review-v10")
        text = text.replace("phase5-review-v9", "phase5-review-v10")
        text = text.replace("The v8 paper has three contributions", "The v10 frozen paper has three contributions")
        text = text.replace("The v9 paper has three contributions", "The v10 frozen paper has three contributions")
        path.write_text(text, encoding="utf-8")

    review = REVIEW.read_text(encoding="utf-8")
    round8 = "- **Claude v9 freeze review:** [`docs/reviews/round-8-claude-v9-freeze-review.md`](docs/reviews/round-8-claude-v9-freeze-review.md) mechanically verifies the v8→v9 delta, closes two citation checks, and recommends freezing scientific text after three micro-fixes integrated into v10.\n"
    marker = "## Corrections reviewers should know before reading\n\n"
    if round8 not in review:
        review = review.replace(marker, marker + round8, 1)
    review = review.replace(
        "Round 4 reproduced this end-to-end on an outside machine rather than relying only on Actions evidence. Round 4 reproduced this end-to-end on an outside machine rather than relying only on Actions evidence.",
        "Round 4 reproduced this end-to-end on an outside machine rather than relying only on Actions evidence.",
    )
    REVIEW.write_text(review, encoding="utf-8")

    header = HEADER.read_text(encoding="utf-8")
    header = header.replace("Working Draft v8 - Not for Citation", "Text Freeze v10 - Review Copy")
    header = header.replace("Working Draft v9 - Not for Citation", "Text Freeze v10 - Review Copy")
    header = header.replace(
        "Working Draft v8 - Independent Repository Review - Not for Citation",
        "Text Freeze v10 - Explore Science Review Copy - Not for Citation",
    )
    header = header.replace(
        "Working Draft v9 - Text-Freeze Candidate - Not for Citation",
        "Text Freeze v10 - Explore Science Review Copy - Not for Citation",
    )
    HEADER.write_text(header, encoding="utf-8")


def main() -> int:
    update_paper()
    update_count_glossary()
    update_navigation()
    print("apply_round8_v10: preserved the v10 text freeze and final micro-fixes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
