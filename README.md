# Synthetic Players

**Auditable behavioral experiments with LLM-controlled agents.**

[arXiv:2608.00979](https://arxiv.org/abs/2608.00979) · [Project site](https://yoheinakajima.github.io/synthetic-players/) · [Paper PDF](docs/paper/synthetic-players.pdf) · [Manuscript](docs/paper/paper.md) · [arXiv source package](docs/paper/synthetic-players-arxiv-source.zip) · [Scientific review record](REVIEW.md)

## Paper

**Passing Coarse Marginal Checks Can Be Cheap: Persona Mixtures and Imprecise Treatment-Response Estimates in an LLM Persona Panel**  
Yohei Nakajima · Untapped Capital

The paper asks whether a lightweight panel of persona-conditioned LLM agents preserves response to an experimental treatment, rather than merely producing plausible aggregate levels.

### Main result

A fixed panel of sixteen GPT-4.1 persona prompts met preregistered broad-reference condition-mean criteria in three of four repeated-game cells; the sole miss was **0.011** below its lower reference bound. Variation was strongly prompt-indexed, but its estimated share was prior-sensitive: fixed-panel symmetric-Dirichlet sensitivities produced median between-prompt shares of **63%–71%** under Jeffreys alpha=0.5 and **47%–53%** under alpha=1, while finite-opportunity plug-in estimates were **85%–96%**.

Aggregate continuation-probability contrasts were **+0.083** and **+0.078**, with conservative simultaneous 95% intervals **[-0.171, +0.330]** and **[-0.181, +0.330]**. A separate wording-and-position operation moved cooperation from **0/40 to 37/40** in the bare configuration. Because the repeated-game treatment changed both the continuation process and its textual representation, the paper reports a represented-treatment response rather than a pure incentive effect.

The historical P5-2 verdict is preserved, but its fixed-panel Bayesian proximity to the registered 0.20 boundary is prior-dependent: the alpha=1 posterior median is **0.205** with 95% interval **[0.182, 0.231]**. The prompt-cluster bootstrap **[0.071, 0.189]** is the principal dependence-aware sensitivity.

These results concern one fixed model-prompt panel. Human references are protocol-nonmatched, and the paper does **not** claim human substitutability, equivalence, a null response, or generalization to a persona generator.

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
| [`docs/paper/`](docs/paper/) | Canonical manuscript, PDF, checksum, timestamp proof, arXiv metadata, and source archive |
| [`arxiv/`](arxiv/) | The exact TeX and five PDF figures in the arXiv source package |
| [`capsule/`](capsule/) | One-command zero-credential replay capsule |
| [`docs/analysis/submission/`](docs/analysis/submission/) | Dependence-aware sensitivities, prior sweeps, variance decomposition, family audit, and count reconciliation |
| [`docs/phase3-report.md`](docs/phase3-report.md) | Registered Phase 3 results |
| [`docs/phase4/`](docs/phase4/) | Representation, counterfactual, adversary, and drift experiments |
| [`docs/phase5/`](docs/phase5/) | Persona-panel experiment and historical adjudication |
| [`docs/reviews/`](docs/reviews/) | Independent reviews, corrections, and reviewer-role disclosures |
| [`docs/paper/history/`](docs/paper/history/) | Earlier manuscript snapshots retained for provenance |

## Research-integrity contract

The project records prompt registries, external chronology anchors, event-sourced requests and completions, seeded environment state, mechanical adjudication, failed calls, exact replay, registered refutations, post-adjudication corrections, and independent review.

> A pipeline can enforce a registered predicate exactly; it cannot guarantee that the predicate represents a valid estimand, test family, or construct.

Historical registrations and mechanical verdicts are preserved. Later analyses are additive, explicitly labeled, and reproducible from archived databases without provider calls.

## Release verification

The final release workflow:

1. installs a SHA-256-pinned release payload into a clean checkout;
2. verifies the canonical PDF, source archive, Markdown, figures, and release manifest;
3. compiles the arXiv package independently and checks page count, extracted text, and rendered-page equivalence;
4. runs reference, living-document, sealed-boundary, and site lint;
5. executes the complete zero-call replay capsule;
6. records a checksum timestamp proof and machine-readable workflow provenance; and
7. uploads the complete submission bundle as a GitHub Actions artifact.

See [`ARXIV_SUBMISSION.md`](ARXIV_SUBMISSION.md) for the operator checklist.

## Citation and license

Citation metadata are in [`CITATION.cff`](CITATION.cff). The paper is published as [arXiv:2608.00979](https://arxiv.org/abs/2608.00979) (DOI [10.48550/arXiv.2608.00979](https://doi.org/10.48550/arXiv.2608.00979)); the preferred citation uses the arXiv record.

Code is MIT-licensed under [`LICENSE`](LICENSE). Released paper and research artifacts are CC BY 4.0 unless a file states otherwise.
