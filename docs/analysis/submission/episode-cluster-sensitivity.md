# Episode-clustered sensitivity for Phase 5 round-one claims

> **STATUS: POST-ADJUDICATION SENSITIVITY — ZERO SUBJECT CALLS.** Historical registered verdicts are unchanged. The primary episode-level interval is an exact conservative projection: for the three-valued episode outcome Y∈{0,.5,1}, write Y=(1[Y≥.5]+1[Y=1])/2, construct simultaneous Clopper–Pearson intervals for both binary components, and project them onto E[Y].

## Why the percentile bootstrap is retained only as a sensitivity

The exact Clopper–Pearson projection is the conservative reference because it supplies finite-sample coverage for the discrete episode mean. The percentile cluster bootstrap is retained because it was computed, but with six three-valued episodes per cell it has no comparable finite-sample coverage guarantee and can understate uncertainty. A degenerate [0,0] or [1,1] interval correctly fails this strict interiority gate, so exact-corner degeneracy is **not** itself a false-positive mechanism.

## P5-1a census

| method | restricted interior / n | restricted fraction | would historical `<0.10` rule support? | all-cell interior / 96 |
|---|---:|---:|---|---:|
| Historical seat-level CP | 3/32 | 0.0938 | yes | 14/96 |
| Episode exact CP projection | 2/32 | 0.0625 | yes | 11/96 |
| Percentile cluster bootstrap sensitivity | 3/32 | 0.0938 | yes | 13/96 |
| Episode Dirichlet–Jeffreys sensitivity | 5/32 | 0.1562 | no | 19/96 |

Cells changing classification between the historical seat-level rule and the exact episode interval: **3**. Complete cell table: `figure-sources/episode-cluster-cells.csv`.

## P5-2 and clause (b)

Episode-exact P5-2 results are in `figure-sources/episode-exact-p52.csv`. Clause-(b) intervals, including a simultaneous one-sided lower bound across all evaluable persona × temperature lanes, are in `figure-sources/episode-exact-clause-b.csv`.

## Interpretation rule

The exact episode sensitivity is reported beside the historical mechanical verdict. It is not entered into the dead-predictions count and does not rewrite sealed reports. Any disagreement among defensible interval constructions is treated as method sensitivity, not resolved by choosing the favorable method.
