# Manuscript text freeze — v10

> **STATUS: SCIENTIFIC TEXT FREEZE FOR EXTERNAL REVIEW.** This record applies to the manuscript and figure interpretations designated by the `paper-text-freeze-v10` tag. It does not alter any earlier experimental seal, registration, adjudication, or raw record.

## Frozen scope

The following are frozen as the scientific content of the v10 Explore Science review submission:

- title, abstract, contribution statement, methods narrative, results, discussion, limitations, and substantive appendix text in `docs/paper/paper-draft.md`;
- all numerical claims and interpretive captions attached to Figures 1–5;
- the machine-readable analyses supporting those claims;
- the correction ledger and review-history interpretation through Round 8.

## Changes permitted after this freeze without reopening scientific review

Venue-driven changes may be made provided they do not change the scientific meaning or numerical claims:

- page layout, fonts, line numbering, section numbering, reference style, and citation formatting;
- title-page metadata, affiliations, acknowledgments, funding statements, and venue-specific AI-assistance language;
- movement of unchanged material between main text, appendix, and supplement;
- accessibility improvements, figure sizing, and purely cosmetic copyediting;
- addition of a `preferred-citation` record once venue or arXiv metadata are fixed.

## Changes that require a new manuscript version and explicit addendum

- changes to an estimand, result, uncertainty statement, statistical method, or interpretation;
- addition or removal of an empirical claim;
- changes to the novelty boundary or human-substitution implications;
- new analyses or experiments;
- correction of a scientific error discovered after the freeze.

Any such change must preserve v10, identify the reason, and receive a new version identifier. The experimental scope seal remains unchanged: no new provider calls are authorized by this manuscript freeze.

## Freeze artifacts

The generated freeze package includes:

- the source commit recorded in `text-freeze-v10.json`;
- the line-numbered PDF and its in-tree SHA-256 file;
- an OpenTimestamps proof over the PDF checksum file;
- a machine-readable artifact manifest;
- the generic tag `paper-text-freeze-v10` pointing to the committed freeze package.
