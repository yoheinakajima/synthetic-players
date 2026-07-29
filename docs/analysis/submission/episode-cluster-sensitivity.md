# Episode-clustered sensitivity for Phase 5 round-one claims

> **STATUS: POST-ADJUDICATION SENSITIVITY — ZERO SUBJECT CALLS.** Historical registered verdicts are unchanged. The primary sensitivity resamples complete episodes and uses the exact percentile-bootstrap distribution of the episode mean, where an episode contributes 0, 0.5, or 1. A Jeffreys Dirichlet-multinomial interval is reported as a second sensitivity.

## Method fixed before execution

Two seat decisions share an episode. The primary sensitivity therefore defines the episode mean `Y_e=(Y_e1+Y_e2)/2`, constructs the exact nonparametric bootstrap distribution obtained by resampling complete episodes, and applies the historical two-sided gate only when the resulting 95% interval lies wholly inside `(0.05,0.95)`. This is a sensitivity analysis, not a retroactive replacement of the frozen Clopper–Pearson predicate.

## P5-1a census

| method | restricted interior / n | restricted fraction | would historical `<0.10` rule support? | all-cell interior / 96 |
|---|---:|---:|---|---:|
| Historical seat-level CP | 3/32 | 0.0938 | yes | 14/96 |
| Episode cluster bootstrap | 3/32 | 0.0938 | yes | 13/96 |
| Episode Dirichlet–Jeffreys | 5/32 | 0.1562 | no | 19/96 |

Cells changing classification under the cluster bootstrap: **1**. Cells changing under the Dirichlet–Jeffreys sensitivity: **5**. Complete cell table: `figure-sources/episode-cluster-cells.csv`.

## P5-2 and clause (b)

The episode-level P5-2 table is in `figure-sources/episode-cluster-p52.csv`. Clause-(b) intervals, including a Bonferroni-adjusted one-sided cluster-bootstrap lower bound over every evaluable lane, are in `figure-sources/episode-cluster-clause-b.csv`.

## Interpretation rule

Any classification change is reported as a sensitivity result beside the historical mechanical verdict. It is not entered into the dead-predictions count and does not rewrite sealed reports.
