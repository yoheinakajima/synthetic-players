# Final high-precision P5-3(a) family audit

> **STATUS: POST-ADJUDICATION SENSITIVITY — ZERO SUBJECT CALLS.** The historical mechanical verdict is unchanged. This audit uses the same raw-slope statistic for the observed data and every permutation and reruns the full gate-plus-maximum-selection procedure over all 32 evaluable clause-(a) candidates.

## Design

- Permutations: **200,000**, seed `20260782`.
- Randomization: episode outcomes are permuted between δ=.90 and δ=.10 within each persona × wording candidate, preserving arm sizes.
- Statistic: maximum positive raw difference in episode-mean round-one cooperation among candidates passing both condition gates.
- Two gate sensitivities are reported: the historical seat-level Clopper–Pearson gate and the episode-level exact cluster-bootstrap gate.
- Monte Carlo p-values use `(r+1)/(B+1)` and the table reports a Clopper–Pearson interval for simulation uncertainty.

## Results

| gate | observed max slope | argmax | passing candidates | exceedances / B | p | MC 95% interval | null 95th percentile of gated max |
|---|---:|---|---|---:|---:|---|---:|
| Historical seat CP | +0.4167 | p13/s2a | p04/s2p, p05/s2a, p13/s2a | 11,988/200,000 | 0.059945 | [0.058904, 0.060989] | 0.4167 |
| Episode cluster bootstrap | +0.4167 | p13/s2a | p04/s2p, p05/s2a, p13/s2a | 8,690/200,000 | 0.043455 | [0.042561, 0.044353] | 0.3333 |

The two defensible gate definitions place the same archived maximum on opposite sides of 0.05. Under the historical seat-level gate, the observed value equals the null 95th percentile and the familywise permutation p-value is about 0.060. Under the episode-cluster gate, the p-value is about 0.043. This gate dependence is itself the correct result to report.

## Status rule

This is a post-adjudication sensitivity selected after external review identified the family-error omission. Regardless of its numerical outcome, it does not retroactively convert p13 into a prospectively family-controlled confirmatory result. p13 remains a preregistered replication target; the audit determines how strongly the archived data support that target after selection is accounted for.

Complete candidate table: `figure-sources/p13-family-candidates-final.csv`. Machine-readable summary: `figure-sources/p13-family-audit-final.json`.
