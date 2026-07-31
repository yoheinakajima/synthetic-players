#!/usr/bin/env python3
"""Synchronize repository navigation with the near-arXiv v12 manuscript."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def update(path: Path, transform) -> None:
    if not path.exists():
        return
    before = path.read_text(encoding="utf-8")
    after = transform(before)
    path.write_text(after, encoding="utf-8")


def main() -> int:
    index = ROOT / "docs" / "analysis" / "INDEX.md"
    update(
        index,
        lambda t: t.replace("synthetic-players-review-v11.pdf", "synthetic-players-preprint-v12.pdf")
        .replace("Current v11 review-revision Markdown manuscript", "Current v12 preprint Markdown manuscript")
        .replace("Current full paper draft, revised through the submission-gate audit", "Current near-arXiv v12 preprint manuscript"),
    )

    reviews = ROOT / "docs" / "reviews" / "README.md"
    def review_transform(t: str) -> str:
        entry = "- [`round-10-explore-science-v11-review.md`](round-10-explore-science-v11-review.md) and [`round-10-disposition-matrix.md`](round-10-disposition-matrix.md): final Explore Science review and v12 disposition.\n"
        if entry not in t:
            marker = "## Review records\n"
            if marker in t:
                t = t.replace(marker, marker + "\n" + entry, 1)
            else:
                t += "\n" + entry
        return t
    update(reviews, review_transform)

    pdfreadme = ROOT / "docs" / "paper" / "PDF-README.md"
    update(
        pdfreadme,
        lambda _t: """# Preprint PDF build

The current manuscript is `paper-draft.md`. The near-arXiv review artifact is
`synthetic-players-preprint-v12.pdf`, built by `scripts/build_preprint_pdf_v12.py`
with Pandoc and XeLaTeX. Its SHA-256 and build manifest are committed beside it.

The v12 PDF is a clean preprint surface: no margin line numbers, no reviewer-only
status language, and five vector figures. Historical review PDFs remain preserved
under their versioned names.
""",
    )

    synthesis = ROOT / "docs" / "analysis" / "program-synthesis-DRAFT.md"
    def synthesis_transform(t: str) -> str:
        t = t.replace("current manuscript is [`../paper/paper-draft.md`](../paper/paper-draft.md)", "current near-arXiv manuscript is [`../paper/paper-draft.md`](../paper/paper-draft.md)")
        t = t.replace("4,576", "4,916")
        t = t.replace("Phase 4–5", "Phase 3–5")
        if "63%–71% posterior medians (85%–96% conditional plug-in estimates)" not in t:
            t = t.replace("85%–96%", "63%–71% posterior medians (85%–96% conditional plug-in estimates)")
        return t
    update(synthesis, synthesis_transform)

    capsule_analysis = ROOT / "docs" / "analysis" / "r2" / "capsule-verification.md"
    def capsule_transform(t: str) -> str:
        t = t.replace("4,576/4,576", "4,916/4,916")
        t = t.replace("Phase 4 and Phase 5", "Phase 3, Phase 4, and Phase 5")
        t = t.replace("Phase 4–5", "Phase 3–5")
        return t
    update(capsule_analysis, capsule_transform)

    status = ROOT / "docs" / "analysis" / "submission-blockers.md"
    def status_transform(t: str) -> str:
        t = re.sub(r"^# .*", "# Preprint v12 status — scientific revision complete", t, count=1)
        t = re.sub(
            r"> \*\*STATUS:.*?\n",
            "> **STATUS: COMPLETE FOR NEAR-ARXIV REVIEW.** The v11 issues are verified and dispositioned; remaining changes are venue metadata and formatting only.\n",
            t,
            count=1,
        )
        return t
    update(status, status_transform)

    print("polish_repo_v12: repository navigation synchronized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
