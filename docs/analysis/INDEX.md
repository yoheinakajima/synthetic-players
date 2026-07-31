# Analysis and verification index

> **STATUS: PUBLIC RESEARCH RECORD.** Historical registrations and mechanical verdicts are preserved. Later analyses are explicitly labeled post-adjudication, sensitivity, or exploratory.

## Start here

| file | contents |
|---|---|
| [`../paper/synthetic-players.pdf`](../paper/synthetic-players.pdf) | Canonical paper PDF |
| [`../paper/paper.md`](../paper/paper.md) | Canonical Markdown manuscript |
| [`../../REVIEW.md`](../../REVIEW.md) | Claim summary, corrections, and reproduction entry point |
| [`submission/submission-analysis-summary.json`](submission/submission-analysis-summary.json) | Machine-readable analysis summary |
| [`novelty-relationships.md`](novelty-relationships.md) | Occupied territory, precise differentiation, and claims to avoid |
| [`literature-map.md`](literature-map.md) | Synthetic participants, strategic behavior, personas, causal surrogacy, validity, and metascience |
| [`hierarchy.md`](hierarchy.md) | Counting units, dependence clusters, fixed-panel and persona-population estimands |
| [`propositions.md`](propositions.md) | Partial identification, microstructure, and cross-condition coupling |
| [`persona-table.md`](persona-table.md) | All sixteen sealed persona sentences, construction rule, leaning labels, and hashes |
| [`../reviews/`](../reviews/) | Independent reviews, dispositions, role disclosure, and verification history |

## Submission analyses

| file | result |
|---|---|
| [`submission/final/composition-prior-sensitivity.md`](submission/final/composition-prior-sensitivity.md) | Symmetric-Dirichlet alpha sweep showing substantial composition but prior-sensitive dominance |
| [`submission/variance-uncertainty-v11.md`](submission/variance-uncertainty-v11.md) | Fixed-panel Jeffreys latent-propensity variance sensitivity |
| [`submission/variance-correction.md`](submission/variance-correction.md) | Finite-opportunity plug-in between-prompt SD and share estimates |
| [`submission/episode-cluster-sensitivity.md`](submission/episode-cluster-sensitivity.md) | Historical/exact/Jeffreys interior counts: 14/11/19 of 96 and 3/2/5 of 32 |
| [`submission/p13-family-audit-final.md`](submission/p13-family-audit-final.md) | Historical, bootstrap, and exact familywise constructions for p13 |
| [`submission/v13/p52-dependence-audit.md`](submission/v13/p52-dependence-audit.md) | Prompt-cluster and fixed-panel latent-propensity sensitivities for P5-2 |
| [`submission/round5/round5-review-audit.md`](submission/round5/round5-review-audit.md) | Dynamic-gate parity, attainability, power, and provenance audit |
| [`submission/count-reconciliation.md`](submission/count-reconciliation.md) | Reconciles event-store, replay, request, token, and ledger counts |
| [`submission/figure-sources/`](submission/figure-sources/) | Cell-level CSV/JSON inputs for the paper figures and sensitivity analyses |

## Reproduction

The public capsule verifies 4,916 confirmatory Phase 3-5 runs and three legacy diagnostics without credentials or live model calls:

```bash
git clone https://github.com/yoheinakajima/synthetic-players
cd synthetic-players/capsule
bash verify.sh
```

Primary scripts:

- `artifacts/api-server/engine/submission_gate_analyses.py`
- `artifacts/api-server/engine/submission_gate_exact_cluster.py`
- `artifacts/api-server/engine/submission_gate_variance_fixed.py`
- `scripts/explore_v11_variance.py`
- `scripts/final_prior_sensitivity.py`
- `scripts/v13_p52_audit.py`
- `scripts/build_arxiv_release.py`

## Historical and contextual material

- `claims-ledger.md` / `claims-ledger.csv` - registered claims and historical verdicts;
- `dead-predictions-final.md` - twelve author predictions refuted by data;
- `human-anchor-scorecard.md` - protocol-nonmatched human references;
- `corner-map.md` - historical seat-level boundary map;
- `post-verdict/` - exploratory clause-(b), p13, interior-census, P5-2, and entropy analyses;
- `paper/history/` - exact earlier manuscript snapshots retained for provenance.
