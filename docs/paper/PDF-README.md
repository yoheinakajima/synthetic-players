# Reviewer PDF build

> **STATUS: WORKING REVIEW ARTIFACT — NOT FOR CITATION.**

The first formatted reviewer PDF is:

- [`synthetic-players-review-draft-v6.pdf`](synthetic-players-review-draft-v6.pdf)

It is generated from [`paper-draft.md`](paper-draft.md) plus the vector figures under [`figures/`](figures/) by:

```bash
python scripts/build_review_pdf.py
```

The build uses Pandoc and XeLaTeX, adds line numbers every five lines, and preserves the Markdown manuscript as the living paper source. The current PDF is a review layout, not a venue-formatted submission.

## Required local tools

- Python 3.11+
- Pandoc
- XeLaTeX with `fontspec`, `unicode-math`, `lineno`, `titlesec`, `fancyhdr`, `lastpage`, and related LaTeX packages
- Linux Libertine, Lato, DejaVu Sans Mono, and STIX Math fonts

The GitHub Actions review workflow installs these dependencies, regenerates the figures and machine-readable response estimates, builds the PDF, validates links and the sealed boundary, and reruns the 4,576-run reproduction capsule.
