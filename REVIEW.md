# Scientific review and verification entry point

Everything needed to assess the paper's claims, analyses, chronology, corrections, and reproduction contract is public in this repository.

## Start here

1. [Paper PDF](docs/paper/synthetic-players.pdf)
2. [Canonical manuscript](docs/paper/paper.md)
3. [arXiv source package](docs/paper/synthetic-players-arxiv-source.zip)
4. [Machine-readable analysis summary](docs/analysis/submission/submission-analysis-summary.json)
5. [P5-2 prior-sensitivity record](docs/analysis/submission/p52-prior-sensitivity.md)
6. [Novelty boundary](docs/analysis/novelty-relationships.md)
7. [Literature map](docs/analysis/literature-map.md)
8. [Units and estimands](docs/analysis/hierarchy.md)
9. [Identification propositions](docs/analysis/propositions.md)
10. [Review and correction archive](docs/reviews/)
11. [Exact manuscript history](docs/paper/history/)

## What the paper claims

A fixed panel of sixteen lightweight persona prompts passed preregistered coarse marginal checks in three of four repeated-game cells. Fixed-panel symmetric-Dirichlet sensitivities place median between-prompt shares at 63%–71% under Jeffreys alpha=0.5 and 47%–53% under alpha=1; finite-opportunity plug-in estimates are 85%–96%. Aggregate continuation-probability contrasts are +0.083 and +0.078, with conservative simultaneous intervals [-0.171, +0.330] and [-0.181, +0.330].

The paper does **not** claim equivalence, a null response, incentive insensitivity, human substitutability, or generalization beyond the fixed model-prompt panel. The continuation treatment changed both the environment and the wording communicating it.

## Corrections reviewers should know

- **P5-1a is method-sensitive.** The restricted census is 3/32 under the frozen seat-level rule, 2/32 under the conservative exact-episode interval, and 5/32 under the Dirichlet-Jeffreys sensitivity. The continuous composition estimates are primary.
- **P5-2 is not prior-robust Bayesian corroboration.** The empirical episode mean is 45/352 = 0.128 and the prompt-cluster bootstrap is [0.071, 0.189]. Across symmetric fixed-panel priors, the posterior median rises from 0.138 at alpha=.10 to 0.205 at alpha=1; the alpha=1 interval [0.182, 0.231] crosses the registered 0.20 boundary. The historical mechanical verdict remains visible.
- **The favored p13 interpretation is withdrawn.** The frozen search lacked prospective family control. Post-adjudication familywise constructions are disclosed symmetrically; the conservative exact family is structurally underpowered at six episodes per condition. p13 is a replication target rather than a finding.
- **Representation sensitivity is specific, not universal.** Ordinary one-shot wording had a registered main effect of only +0.0063 (Holm-adjusted p=1.00), while announcing and implementing repeated interaction and the S2 wording operation produced much larger shifts. Ceiling cells do not identify the continuation-probability slope.
- **Appendix A.2 preserves mixed-status secondary findings.** The adversary result is registered and Holm-controlled; the RPS test sign-reversed and is interpreted descriptively; GPT label-payoff cells are registered while Gemini figures are descriptive under endpoint nonstationarity; endpoint drift is a procedural monitoring record.
- **Human references are protocol-nonmatched and contextual.** No matched human substitution study is claimed in this paper.
- **Reviewer roles are disclosed.** External reviewers first diagnosed defects; one later helped specify post-adjudication analyses. Dispositions and role transitions are archived under [`docs/reviews/`](docs/reviews/).

## Reproduce the confirmatory record

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

No credentials, API keys, or live model calls are used.

## High-value review questions

1. Is the mechanism-level differentiation from statistical-realism, causal-surrogacy, latent-user-drift, persona-collapse, and strategic-game work sufficiently sharp?
2. Are fixed-panel, persona-generator, prompt-indexed, and human-substitution estimands distinguished correctly?
3. Are treatment-response point estimates presented as imprecise estimates rather than equivalence or null findings?
4. Are plug-in, fixed-panel latent-propensity, and persona-generator uncertainty views matched to the claims made from them?
5. Are all post-adjudication corrections characterized fairly, including favorable and unfavorable sensitivity results?
6. Does the public replay and provenance record support the auditability claims actually made?
7. Are registered, descriptive, post-adjudication, and procedural findings kept in distinct evidentiary tiers?

Open a GitHub issue for new scientific criticism. Please distinguish a proposed change to the living interpretation from a requested alteration of a sealed historical artifact; sealed records are preserved rather than silently rewritten.
