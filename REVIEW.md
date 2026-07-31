# Scientific review and verification entry point

Everything needed to assess the paper's claims, analyses, chronology, corrections, and reproduction contract is public in this repository.

## Start here

1. [Paper PDF](docs/paper/synthetic-players.pdf)
2. [Canonical manuscript](docs/paper/paper.md)
3. [arXiv source package](docs/paper/synthetic-players-arxiv-source.zip)
4. [Machine-readable analysis summary](docs/analysis/submission/submission-analysis-summary.json)
5. [Novelty boundary](docs/analysis/novelty-relationships.md)
6. [Literature map](docs/analysis/literature-map.md)
7. [Units and estimands](docs/analysis/hierarchy.md)
8. [Identification propositions](docs/analysis/propositions.md)
9. [Review and correction archive](docs/reviews/)
10. [Exact manuscript history](docs/paper/history/)

## What the paper claims

A fixed panel of sixteen lightweight persona prompts passed preregistered coarse marginal checks. A fixed-panel latent-propensity sensitivity places median between-prompt shares at 63%-71% with 95% intervals spanning 49%-81%; finite-opportunity plug-in estimates are 85%-96%. Aggregate continuation-probability contrasts are +0.083 and +0.078, with conservative exact intervals [-0.171, +0.330] and [-0.181, +0.330].

The paper does **not** claim equivalence, a null response, incentive insensitivity, human substitutability, or generalization beyond the fixed model-prompt panel. The continuation treatment changed both the environment and the wording communicating it.

## Corrections reviewers should know

- The historical P5-1a boundary census is interval-method-sensitive: 3/32 under the frozen seat rule, 2/32 under the conservative exact-episode sensitivity, and 5/32 under a Dirichlet-Jeffreys sensitivity.
- The favored p13 interpretation is withdrawn. Post-review familywise constructions are disclosed symmetrically; none was prospectively registered, and the conservative exact family is underpowered at six episodes per condition.
- P5-2 remains below its registered boundary under prompt-cluster and fixed-panel Bayesian sensitivities, but the pooled classification is carried by a mechanism-confounded swap cell.
- The between-prompt composition claim is shown through three distinct uncertainty views rather than one thresholded label.
- Human references are protocol-nonmatched and contextual.
- External reviewers first diagnosed defects; one later helped specify post-adjudication analyses. That role transition and all dispositions are archived under [`docs/reviews/`](docs/reviews/).

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
3. Are the treatment-response point estimates presented as imprecise estimates rather than equivalence or null findings?
4. Are the plug-in, fixed-panel latent-propensity, and persona-generator uncertainty views matched to the claims made from them?
5. Are all post-adjudication corrections characterized fairly, including favorable and unfavorable sensitivity results?
6. Does the public replay and provenance record support the auditability claims actually made?

Open a GitHub issue for new scientific criticism. Please distinguish a proposed change to the living interpretation from a requested alteration of a sealed historical artifact; sealed records are preserved rather than silently rewritten.
