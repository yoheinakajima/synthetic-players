# Synthetic Players

**Auditable behavioral experiments with LLM-controlled agents.**

[Project site](https://yoheinakajima.github.io/synthetic-players/) · [Paper PDF](docs/paper/synthetic-players.pdf) · [Manuscript](docs/paper/paper.md) · [arXiv source package](docs/paper/synthetic-players-arxiv-source.zip) · [Scientific review record](REVIEW.md)

## Paper

**Passing Coarse Marginal Checks Can Be Cheap: Persona Mixtures and Imprecise Treatment-Response Estimates in an LLM Persona Panel**  
Yohei Nakajima · Untapped Capital

The paper studies whether a lightweight panel of persona-conditioned LLM agents preserves response to an experimental treatment rather than merely producing plausible aggregate levels.

### Main result

A fixed panel of sixteen GPT-4.1 persona prompts met preregistered broad-reference condition-mean criteria in three of four repeated-game cells; the sole miss was **0.011** below the lower bound. Composition is substantial but the stronger dominance reading is prior-sensitive: median between-prompt shares are **63%-71%** under the Jeffreys prior and **47%-53%** under a symmetric uniform prior, while finite-opportunity plug-in estimates are **85%-96%**. Aggregate continuation-probability contrasts are **+0.083** and **+0.078**, with conservative simultaneous 95% intervals **[-0.171, +0.330]** and **[-0.181, +0.330]**.

Separate representation experiments found that replacing and repositioning one sentence moved cooperation from **0/40 to 37/40** in a bare configuration. The treatment changed both continuation probability and its textual representation, so incentive and framing channels remain undecomposed. The historical p13 result was not prospectively family-controlled and remains a replication target rather than a finding.

These results concern one fixed model-prompt panel. Human references are protocol-nonmatched, and the paper does **not** claim human substitutability.

## Reproduce the confirmatory record

Anonymous clone, zero credentials, zero live model calls:

```bash
git clone https://github.com/yoheinakajima/synthetic-players
cd synthetic-players/capsule
bash verify.sh
```

Expected result:

```text
CAPSULE VERIFICATION PASS — 4,919 archived Phase 3-5 runs verified
(4,916 confirmatory + 3 legacy diagnostics)
```

The verifier replays 4,896 archived LLM runs byte-exact and independently recomputes 20 deterministic baselines.

## What is in this repository

| Path | Contents |
|---|---|
| [`docs/paper/`](docs/paper/) | Canonical manuscript, PDF, checksum, arXiv metadata, and uploadable source archive |
| [`arxiv/`](arxiv/) | The exact TeX and figure files contained in the arXiv source package |
| [`capsule/`](capsule/) | One-command zero-credential replay capsule |
| [`docs/analysis/submission/`](docs/analysis/submission/) | Dependence-aware sensitivities, variance decomposition, prior sensitivity, family audit, and count reconciliation |
| [`docs/phase3-report.md`](docs/phase3-report.md) | Registered Phase 3 results |
| [`docs/phase4/`](docs/phase4/) | Representation, counterfactual, adversary, and drift experiments |
| [`docs/phase5/`](docs/phase5/) | Persona-panel experiment and historical adjudication |
| [`docs/reviews/`](docs/reviews/) | Independent reviews, corrections, and reviewer-role disclosures |
| [`docs/paper/history/`](docs/paper/history/) | Earlier manuscript snapshots retained for provenance |

## Research-integrity contract

The project records prompt registries, external chronology anchors, event-sourced requests and completions, seeded environment state, mechanical adjudication, failed calls, exact replay, registered refutations, post-adjudication corrections, and independent review.

The central boundary is explicit:

> A pipeline can enforce a registered predicate exactly; it cannot guarantee that the predicate represents a valid estimand, test family, or construct.

Historical registrations and mechanical verdicts are preserved. Later analyses are additive, labeled, and reproducible from the archived databases without provider calls.

## Build and submission artifacts

The canonical paper is built from [`docs/paper/paper.md`](docs/paper/paper.md) using standard PDFLaTeX-compatible source. The CI pipeline:

1. regenerates zero-call analyses and figures;
2. runs reference-integrity and sealed-boundary lint;
3. verifies the complete replay capsule;
4. compiles the exact arXiv source package;
5. checks PDF text, figure count, font embedding, and source-package recompilation;
6. records SHA-256 and OpenTimestamps proof files.

See [`ARXIV_SUBMISSION.md`](ARXIV_SUBMISSION.md) for the operator checklist.

## Citation and license

Citation metadata are in [`CITATION.cff`](CITATION.cff). After arXiv assigns an identifier, the preferred citation will be updated with that stable URL and DOI.

Code is MIT-licensed under [`LICENSE`](LICENSE). Released data artifacts and generated research records are CC BY 4.0 unless a file states otherwise.
