# Round 13 — Claude review of the canonical preprint and arXiv readiness

**Reviewer-supplied review, 2026-07-31.** The reviewer verified the repository at `main` and distinguished a superseded uploaded PDF from the canonical build committed in the repository.

## Findings

The reviewer judged the scientific content preprint-grade and found no remaining scientific analysis blocker. Three release-engineering items were identified:

1. a Phase 6 sentence appeared twice in the generated PDF and living Markdown;
2. the final public paper needed an unversioned, arXiv-facing identity and checksum chain;
3. the final submission package should include timestamped checksum, current Park citation metadata, preferred citation metadata, and a short arXiv abstract.

The reviewer also confirmed that the corrected bibliography, reference-integrity lint, and one-command replay capsule were functioning, and recommended ending the review lineage after the release build.

## Disposition

- **Duplicate sentence:** removed from the canonical source; the PDF and source preflight now require exactly one occurrence.
- **Paper identity:** the canonical manuscript and PDF are unversioned (`paper.md`, `synthetic-players.pdf`) and contain no working-draft or review-candidate labels.
- **arXiv source:** a minimal PDFLaTeX archive containing `main.tex` and five PDF figures is compiled in a fresh directory during CI.
- **Timestamp:** the canonical PDF checksum is stamped with OpenTimestamps and committed beside the paper.
- **Park citation:** updated to the current arXiv v3 title and author list while preserving the original 2024 submission year and noting the 2026 revision.
- **Reference guard:** Park and Akata are included in the identifier-title lint, alongside every previously regressed entry.
- **Metadata:** `CITATION.cff`, `arxiv-metadata.txt`, and `ARXIV_SUBMISSION.md` are publication-facing and contain no internal version label.
- **Public surface:** README, reviewer entry point, and GitHub Pages site now point to the canonical paper, source package, analyses, review archive, and replay capsule.

No new statistical analysis was added. The optional posterior probability that each between-prompt share exceeds one-half was not introduced because the existing median-and-interval presentation already states the uncertainty directly and the review judged it non-blocking.
