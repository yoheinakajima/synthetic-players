# arXiv submission checklist

The repository produces a canonical PDF and a minimal source archive that recompiles to the same paper with standard PDFLaTeX.

## Upload files

- Source archive: [`docs/paper/synthetic-players-arxiv-source.zip`](docs/paper/synthetic-players-arxiv-source.zip)
- Reference PDF: [`docs/paper/synthetic-players.pdf`](docs/paper/synthetic-players.pdf)
- Metadata: [`docs/paper/arxiv-metadata.txt`](docs/paper/arxiv-metadata.txt)
- PDF checksum: [`docs/paper/synthetic-players.sha256`](docs/paper/synthetic-players.sha256)
- Timestamp proof: [`docs/paper/synthetic-players.sha256.ots`](docs/paper/synthetic-players.sha256.ots)

The upload archive contains only `main.tex` and five PDF figures. CI extracts it into a fresh directory and recompiles it before publication.

## Suggested arXiv fields

**Title**  
Passing Coarse Marginal Checks Can Be Cheap: Persona Mixtures and Imprecise Treatment-Response Estimates in an LLM Persona Panel

**Author**  
Yohei Nakajima

**Suggested primary category**  
`cs.AI`

**Suggested cross-list**  
`cs.HC`

**Comments**  
Use the generated page and figure count from `arxiv-metadata.txt`, followed by: “Code, data, registrations, review record, and zero-call replay capsule: https://github.com/yoheinakajima/synthetic-players”.

The generated abstract is ASCII-only and remains below arXiv's metadata length limit.

## Operator sequence

1. Log in to arXiv and start a new submission.
2. Upload `synthetic-players-arxiv-source.zip`, not the PDF alone.
3. Confirm that arXiv selects `main.tex` and compiles with PDFLaTeX.
4. Compare arXiv's generated PDF with `synthetic-players.pdf`, especially all five figures, tables, references, and the Phase 6 paragraph.
5. Paste the generated metadata from `arxiv-metadata.txt`.
6. Select the submission license in the arXiv interface.
7. Submit and record the assigned arXiv identifier.
8. Update `CITATION.cff`, the project site, and README with the stable arXiv URL and DOI.

## Scientific freeze

The experiment is closed. The arXiv package may receive typographic, metadata, or clearly labeled correction updates, but historical registrations, event data, and mechanical verdicts must not be rewritten. New empirical claims require a new registration and release lineage.
