# arXiv submission checklist

> **STATUS (2026-08-02): SUBMITTED — [arXiv:2608.00979](https://arxiv.org/abs/2608.00979), DOI 10.48550/arXiv.2608.00979.** Operator steps 1–9 are complete; the step-10 metadata patch (CITATION.cff, README, project site, arxiv-metadata.txt) is applied in this repository. Operational note for any future replacement: arXiv's processor auto-detection selected **xelatex**, which fails on this package at `\pdfoutput=1`; explicitly select **pdflatex** on the Process page and reprocess.

The repository produces a canonical 19-page PDF and a minimal source archive containing `main.tex` and five PDF figures.

## Upload files

- Source archive: [`docs/paper/synthetic-players-arxiv-source.zip`](docs/paper/synthetic-players-arxiv-source.zip)
- Reference PDF: [`docs/paper/synthetic-players.pdf`](docs/paper/synthetic-players.pdf)
- Metadata: [`docs/paper/arxiv-metadata.txt`](docs/paper/arxiv-metadata.txt)
- PDF checksum: [`docs/paper/synthetic-players.sha256`](docs/paper/synthetic-players.sha256)
- Timestamp proof: [`docs/paper/synthetic-players.sha256.ots`](docs/paper/synthetic-players.sha256.ots)
- Artifact manifest: [`docs/paper/synthetic-players-artifact.json`](docs/paper/synthetic-players-artifact.json)

Upload the source archive, not the PDF alone. The release workflow extracts it into a clean directory, compiles it with PDFLaTeX, verifies 19 pages and five figure assets, compares extracted text and rendered pages with the canonical PDF, and uploads the complete bundle as a workflow artifact.

## Recommended arXiv fields

**Title**  
Passing Coarse Marginal Checks Can Be Cheap: Persona Mixtures and Imprecise Treatment-Response Estimates in an LLM Persona Panel

**Author**  
Yohei Nakajima

**Primary category**  
`cs.CL` — the paper's central object is the empirical behavior and validation of large language models.

**Cross-list**  
`cs.CY` — the paper concerns LLMs as synthetic participants in social-science research and the governance of auditable computational evidence.

`stat.AP` is a plausible additional cross-list only if the submission interface and moderators consider the applied-statistical contribution within scope. `cs.AI` is a reasonable fallback primary if category moderation redirects the paper.

**License**  
CC BY 4.0 is recommended for the paper, consistent with the repository's released research artifacts. Confirm that you control all included material before selecting it; arXiv licenses cannot ordinarily be changed after public announcement.

**Comments**  
`19 pages, 5 figures. Code, data, registrations, review record, and zero-call replay capsule: https://github.com/yoheinakajima/synthetic-players`

Use the exact abstract in [`docs/paper/arxiv-metadata.txt`](docs/paper/arxiv-metadata.txt).

## Operator sequence

1. Confirm PR #13 is merged, the release tag exists, the final release workflow is green, and the Pages deployment serves the canonical PDF.
2. Log in to arXiv and start a new submission.
3. Upload `synthetic-players-arxiv-source.zip`.
4. Confirm arXiv selects `main.tex` and compiles with PDFLaTeX.
5. Compare arXiv's generated PDF with `synthetic-players.pdf`, especially all five figures, tables, references, Appendix A.2, and the Phase 6 paragraph.
6. Paste the title, author, comments, and exact abstract from `arxiv-metadata.txt`.
7. Select the primary category, cross-list, and license.
8. Preview metadata carefully; verify the repository and project-site links.
9. Submit and record the assigned arXiv identifier.
10. Update `CITATION.cff`, README, the project site, and `arxiv-metadata.txt` with the stable arXiv URL and DOI, then issue a metadata-only patch release.

## Scientific freeze

The experiment is closed. The arXiv package may receive typographic, metadata, or clearly labeled correction updates, but historical registrations, event data, and mechanical verdicts must not be rewritten. New empirical claims require a new registration and release lineage.
