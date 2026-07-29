# Final high-precision P5-3(a) family audit

> **STATUS: POST-ADJUDICATION SENSITIVITY — ZERO SUBJECT CALLS.** Historical mechanical verdicts are unchanged. No familywise gate was registered at the original freeze. After external review identified the multiplicity and dependence defects, the variants below were specified and executed against the archived databases with fixed seeds; generated outputs were committed regardless of direction.

## Design and reporting rule

- Permutations: **200,000** for each construction.
- Episode outcomes are permuted between δ=.90 and δ=.10 within each persona × wording candidate, preserving arm sizes.
- Statistic: maximum raw difference in episode-mean round-one cooperation among candidates passing both condition gates.
- Monte Carlo p-values use `(r+1)/(B+1)` with exact intervals for Monte Carlo uncertainty.
- **Primary sensitivity:** the conservative exact-episode CP projection, because it treats the episode as the unit and does not collapse to zero uncertainty at exact corners.
- **Retained sensitivity:** the episode-cluster percentile-bootstrap gate. It is reported because it was computed, but rejected as primary because percentile intervals become degenerate when every observed episode agrees.
- These analyses were not sealed before computation and cannot retroactively create a prospectively family-controlled result. p13 remains a replication target under every numerical outcome.

## Results

| gate construction | observed max slope | argmax | passing candidates | exceedances / B | p | MC 95% interval | null 95th percentile |
|---|---:|---|---|---:|---:|---|---:|
| Historical seat-level CP gate | +0.4167 | p13/s2a | p04/s2p, p05/s2a, p13/s2a | 11,845/200,000 | 0.059230 | [0.058194, 0.060268] | 0.4167 |
| Episode-cluster percentile-bootstrap gate (retained, non-primary) | +0.4167 | p13/s2a | p04/s2p, p05/s2a, p13/s2a | 8,690/200,000 | 0.043455 | [0.042561, 0.044353] | 0.3333 |
| Episode-exact CP projection (**primary sensitivity**) | +0.0833 | p05/s2a | p04/s2p, p05/s2a | 154,641/200,000 | 0.773206 | [0.771363, 0.775039] | 0.3333 |

The percentile-bootstrap construction is the only variant below 0.05 (`p=0.043455`, MC 95% `[0.042561, 0.044353]`). That result does not rescue the historical claim: the construction was selected after the inferential defect was found, its corner behavior is unsuitable for the assay's purpose, and no familywise procedure was registered at freeze. Under the primary exact-episode gate, p13 is excluded and the maximum surviving slope is +0.0833 with `p=0.773206`.

## Status

The archived data do not supply a prospectively controlled persona-level incentive-response existence result. The historical mechanical verdict remains visible; the scientific interpretation is a replication target plus an auditable example of where exact procedural enforcement stopped short of valid family-level inference.

Machine-readable summary: `figure-sources/p13-family-audit-final.json`.
