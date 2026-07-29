# Final high-precision P5-3(a) family audit

> **STATUS: POST-ADJUDICATION SENSITIVITY — ZERO SUBJECT CALLS.** Historical mechanical verdicts are unchanged. The audit uses the same raw-slope statistic for observed and permuted data and reruns the full gate-plus-maximum-selection procedure over all 32 evaluable clause-(a) candidates.

## Design

- Permutations: **200,000**, seed `20260783`.
- Episode outcomes are permuted between δ=.90 and δ=.10 within each persona × wording candidate, preserving arm sizes.
- Statistic: maximum raw difference in episode-mean round-one cooperation among candidates passing both condition gates.
- Gates: the historical seat-level Clopper–Pearson rule and the primary episode-exact CP projection.
- Monte Carlo p-values use `(r+1)/(B+1)` with an exact interval for Monte Carlo uncertainty.

## Results

| gate | observed max slope | argmax | passing candidates | exceedances / B | p | MC 95% interval | null 95th percentile |
|---|---:|---|---|---:|---:|---|---:|
| Historical seat CP | +0.4167 | p13/s2a | p04/s2p, p05/s2a, p13/s2a | 11,845/200,000 | 0.059230 | [0.058194, 0.060268] | 0.4167 |
| Episode exact CP projection | +0.0833 | p05/s2a | p04/s2p, p05/s2a | 154,641/200,000 | 0.773206 | [0.771363, 0.775039] | 0.3333 |

## Status

This family analysis was specified after external review identified the frozen rule's multiplicity defect. It cannot retroactively create a prospectively family-controlled result. Its purpose is to quantify how much support remains in the archived data under explicit cluster-level inference. p13 remains a replication target regardless of the numerical result.

Machine-readable summary: `figure-sources/p13-family-audit-final.json`.
