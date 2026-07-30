#!/usr/bin/env python3
"""Finalize v11 support surfaces after generated analyses are refreshed."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COUNT = ROOT / "docs/analysis/submission/count-reconciliation.md"
EPISODE = ROOT / "docs/analysis/submission/episode-cluster-sensitivity.md"
SUMMARY = ROOT / "docs/analysis/submission/submission-analysis-summary.json"
V11 = ROOT / "docs/analysis/submission/figure-sources/variance-uncertainty-v11.json"
README = ROOT / "README.md"
REVIEW = ROOT / "REVIEW.md"
INDEX = ROOT / "docs/analysis/INDEX.md"
STATUS = ROOT / "docs/analysis/submission-blockers.md"
PDFREADME = ROOT / "docs/paper/PDF-README.md"
CITATION = ROOT / "CITATION.cff"
REVIEWS = ROOT / "docs/reviews/README.md"

COUNT_BLOCK = """## Phase 4+5 request, response, and spending counts

| unit | count | definition |
|---|---:|---|
| Phase 4+5 normal request events | 30,421 | `llm.requested` events assigned to Phase 4 or Phase 5 in the event store |
| Phase 4+5 response events | 30,397 | `llm.responded` events with archived raw completion text and provider response IDs |
| provider-failure partials | 24 | request events without a normal response event; disclosed and excluded from completed-run replay |
| Phase 4+5 transactional ledger calls | 30,530 | spending-accounting call attempts, including Phase 4 infrastructure entries outside the standard request-event stream |

These totals answer different questions. Request and response events describe the event stream; ledger calls describe budget accounting. They are related but not row-identical.

"""


def finalize_count() -> None:
    text = COUNT.read_text(encoding="utf-8")
    marker = "## Phase 4+5 transactional budget ledger"
    if "## Phase 4+5 request, response, and spending counts" not in text:
        if marker not in text:
            raise RuntimeError("count-reconciliation insertion marker missing")
        text = text.replace(marker, COUNT_BLOCK + marker, 1)
    text = text.replace(
        "Use `episodes/runs`, `round events`, `seat-round decisions`, `provider requests`, `transactional ledger calls`, and `replay observations` only with their exact definitions and scope.",
        "Use `episodes/runs`, `round events`, `seat-round decisions`, `provider requests`, `response events`, `provider-failure partials`, `transactional ledger calls`, and `replay observations` only with their exact definitions and scope.",
    )
    COUNT.write_text(text, encoding="utf-8")


def finalize_episode() -> None:
    text = EPISODE.read_text(encoding="utf-8")
    start = "## Why the initially generated percentile bootstrap is not primary\n\n"
    end = "\n## P5-1a census"
    if start not in text or end not in text:
        raise RuntimeError("episode-sensitivity rationale markers missing")
    before, rest = text.split(start, 1)
    _old, after = rest.split(end, 1)
    rationale = (
        "## Why the percentile bootstrap is retained only as a sensitivity\n\n"
        "The exact Clopper–Pearson projection is the conservative reference because it supplies finite-sample coverage for the discrete episode mean. The percentile cluster bootstrap is retained because it was computed, but with six three-valued episodes per cell it has no comparable finite-sample coverage guarantee and can understate uncertainty. A degenerate [0,0] or [1,1] interval correctly fails this strict interiority gate, so exact-corner degeneracy is **not** itself a false-positive mechanism.\n"
    )
    text = before + rationale + end + after
    text = text.replace(
        "Percentile cluster bootstrap (discarded as primary)",
        "Percentile cluster bootstrap sensitivity",
    )
    EPISODE.write_text(text, encoding="utf-8")


def finalize_summary() -> None:
    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    v11 = json.loads(V11.read_text(encoding="utf-8"))
    summary["v11VarianceUncertainty"] = {
        "status": "post-v10 post-adjudication fixed-panel sensitivity",
        "estimand": "latent propensities of the exact sixteen registered persona prompts",
        "prior": v11["prior"],
        "draws": v11["draws"],
        "rows": v11["rows"],
        "interpretation": (
            "85%–96% are finite-opportunity-corrected plug-in point estimates; "
            "fixed-panel latent-propensity posterior medians are 63%–71%, with "
            "95% intervals spanning approximately 49%–81%."
        ),
    }
    SUMMARY.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def finalize_navigation() -> None:
    readme = README.read_text(encoding="utf-8")
    readme = readme.replace(
        "The sealed experimental program and the scientific review gate are complete. Round 4 independently cloned the repository, passed lint, and replayed all 4,576 runs with zero credentials. Remaining formal-submission work is venue formatting and human sign-off on the final title and venue-specific AI-assistance statement.",
        "The sealed experimental program is complete. v11 is an explicit post-v10 review addendum; its zero-call analyses, figures, PDF, lint, and 4,576-run replay are generated in GitHub Actions.",
    )
    readme = readme.replace(
        "Corrected estimates assign approximately 85%–96% of episode-level variation to differences between prompt configurations. The observed aggregate continuation-probability contrasts are +0.083 and +0.078, with conservative exact intervals of approximately [−0.171, +0.330] and [−0.181, +0.330].",
        "Finite-opportunity-corrected plug-in estimates assign 85%–96% of observed episode-level variation between prompts; a fixed-panel latent-propensity sensitivity yields posterior median shares of 63%–71% with 95% intervals spanning 49%–81%. The observed aggregate continuation-probability contrasts are +0.083 and +0.078, with conservative exact intervals [−0.171, +0.330] and [−0.181, +0.330] (rounded to three decimals).",
    )
    readme = readme.replace(
        "Line-numbered Explore Science review PDF with five vector figures",
        "Clean review PDF with five vector figures",
    )
    README.write_text(readme, encoding="utf-8")

    review = REVIEW.read_text(encoding="utf-8")
    review = review.replace(
        "Corrected variance estimates attribute approximately 85%–96% of episode-level variation to differences between prompt configurations. The two observed aggregate continuation-probability contrasts are +0.083 and +0.078, with conservative exact intervals of approximately [−0.171, +0.330] and [−0.181, +0.330].",
        "Finite-opportunity-corrected plug-in estimates assign 85%–96% of observed episode-level variation between prompts; a fixed-panel latent-propensity sensitivity yields posterior median shares of 63%–71% with 95% intervals spanning 49%–81%. The two observed aggregate continuation-probability contrasts are +0.083 and +0.078, with conservative exact intervals [−0.171, +0.330] and [−0.181, +0.330] (rounded to three decimals).",
    )
    review = review.replace(
        "> Coarse marginal checks can be satisfied largely through composition across prompt-conditioned policies that are highly concentrated within recorded cells, while the observed response to the experimental lever has small point estimates and remains imprecisely estimated.",
        "> Coarse marginal checks can be satisfied through substantial between-prompt composition without requiring the represented-treatment response to be estimated; plug-in concentration estimates are reduced and widened when latent boundary-policy uncertainty is propagated.",
    )
    review = review.replace(
        "4. **Composition claim:** Is the corrected between-prompt share an appropriate primary description given the interval sensitivity of the binary boundary census?",
        "4. **Composition claim:** Is the three-view uncertainty presentation—plug-in/conditional bootstrap, fixed-panel latent-propensity posterior, and persona-generator bootstrap—appropriately matched to its estimands?",
    )
    REVIEW.write_text(review, encoding="utf-8")

    for path in (INDEX, STATUS, PDFREADME):
        text = path.read_text(encoding="utf-8")
        text = text.replace("Line-numbered Explore Science review PDF", "Clean review PDF")
        text = text.replace("line-numbered reviewer PDF", "clean reviewer PDF")
        path.write_text(text, encoding="utf-8")

    citation = CITATION.read_text(encoding="utf-8")
    citation = citation.replace(
        "checks while producing small continuation-probability point estimates with\n  wide dependence-aware intervals. Corrected estimates assign most episode-level variation to\n  differences between prompt configurations.",
        "checks while producing small continuation-probability point estimates with\n  wide dependence-aware intervals. Plug-in estimates assign most observed variation\n  between prompts, while a fixed-panel latent-propensity sensitivity lowers and widens\n  that composition estimate.",
    )
    CITATION.write_text(citation, encoding="utf-8")

    reviews = REVIEWS.read_text(encoding="utf-8")
    reviews = reviews.replace(
        "The Round 5 source PDF reported 13 minor issues but included details for only ten; three online-only issues remain to be obtained and appended before that round is considered fully dispositioned.",
        "The Round 5 source PDF reported ten issues in-document and three online-only issues; all thirteen are now archived in the disposition record. Round 9 supplied twenty additional minor issues against v10.",
    )
    REVIEWS.write_text(reviews, encoding="utf-8")


def main() -> int:
    finalize_count()
    finalize_episode()
    finalize_summary()
    finalize_navigation()
    print("finalize_explore_v11: support surfaces synchronized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
