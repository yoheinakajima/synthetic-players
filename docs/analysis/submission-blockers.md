# Submission status — arXiv package ready

> **STATUS: READY FOR OPERATOR SUBMISSION.** The scientific interpretation is frozen. The canonical PDF, PDFLaTeX source archive, metadata, checksum, timestamp proof, public replay capsule, and project site are generated and validated in GitHub Actions.

## Canonical artifacts

- Manuscript: `docs/paper/paper.md`
- PDF: `docs/paper/synthetic-players.pdf`
- PDF SHA-256: `docs/paper/synthetic-players.sha256`
- OpenTimestamps proof: `docs/paper/synthetic-players.sha256.ots`
- arXiv upload archive: `docs/paper/synthetic-players-arxiv-source.zip`
- arXiv metadata: `docs/paper/arxiv-metadata.txt`
- Artifact identity record: `docs/paper/synthetic-players-artifact.json`
- Operator checklist: `ARXIV_SUBMISSION.md`

The upload archive contains `main.tex` and five PDF figures. CI extracts the archive into a fresh directory, compiles it twice with PDFLaTeX, and compares its page count to the canonical PDF.

## Scientific status

The experiment is closed. Historical registrations and mechanical verdicts are immutable. Post-adjudication analyses are labeled and reproducible from the archived databases without provider calls.

The paper's bounded claims are:

- a fixed panel of sixteen persona prompts passes coarse marginal checks;
- uncertainty-propagating analysis places median between-prompt shares at 63%-71%, with one interval extending below one-half;
- aggregate continuation-probability contrasts are small point estimates with wide intervals;
- representation changes can produce large local behavioral shifts;
- the results do not identify human substitutability, a pure incentive effect, or generalization beyond the fixed deployment.

No new empirical claim is authorized without a new registration and release lineage.

## Reproducibility status

A fresh anonymous clone can run:

```bash
cd capsule
bash verify.sh
```

Expected result:

```text
CAPSULE VERIFICATION PASS — 4,919 archived Phase 3-5 runs verified
(4,916 confirmatory + 3 legacy diagnostics)
```

The capsule uses no credentials and makes no live model calls.

## Remaining operator actions

1. Upload `synthetic-players-arxiv-source.zip` to arXiv.
2. Confirm arXiv's generated PDF against the canonical PDF.
3. Select category and license in the arXiv interface.
4. Submit and record the assigned arXiv identifier.
5. Add the stable arXiv URL and DOI to `CITATION.cff`, README, and the project site.

These are publication mechanics rather than scientific blockers.
