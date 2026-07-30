# Final high-precision P5-3(a) family audit

> **STATUS: POST-ADJUDICATION SENSITIVITY — ZERO SUBJECT CALLS.** Historical mechanical verdicts are unchanged. No familywise gate was registered at the original freeze. After external review identified the multiplicity and dependence defects, the variants below were specified and executed against the archived databases with fixed seeds; generated outputs were committed regardless of direction.

## Design and reporting rule

- Permutations: **200,000** for each construction.
- Episode outcomes are permuted between δ=.90 and δ=.10 within each persona × wording candidate, preserving arm sizes.
- Statistic: maximum raw difference in episode-mean round-one cooperation among candidates passing both condition gates.
- The complete data-dependent gate is dynamically reapplied to every candidate within every permutation; no observed-data mask is frozen.
- Monte Carlo p-values use `(r+1)/(B+1)` with exact intervals for Monte Carlo uncertainty.
- **Conservative exact sensitivity:** the exact-episode CP projection treats the episode as the unit and supplies finite-sample coverage for the discrete episode mean.
- **Percentile-bootstrap sensitivity:** reported because it was computed. With six discrete episodes per arm it has no comparable finite-sample coverage guarantee and can understate uncertainty; exact-corner degeneracy is not itself a false-positive mechanism for the strict interiority gate.
- These analyses were not sealed before computation and cannot retroactively create a prospectively family-controlled result. p13 remains a replication target under every numerical outcome.

## Results

| gate construction | observed max slope | argmax | passing candidates | exceedances / B | p | MC 95% interval | null 95th percentile |
|---|---:|---|---|---:|---:|---|---:|
| Historical seat-level CP gate | +0.4167 | p13/s2a | p04/s2p, p05/s2a, p13/s2a | 11,845/200,000 | 0.059230 | [0.058194, 0.060268] | 0.4167 |
| Episode-cluster percentile-bootstrap sensitivity | +0.4167 | p13/s2a | p04/s2p, p05/s2a, p13/s2a | 8,690/200,000 | 0.043455 | [0.042561, 0.044353] | 0.3333 |
| Episode-exact CP projection (conservative sensitivity) | +0.0833 | p05/s2a | p04/s2p, p05/s2a | 154,641/200,000 | 0.773206 | [0.771363, 0.775039] | 0.3333 |

The percentile-bootstrap construction is the only variant below 0.05 (`p=0.043455`, MC 95% `[0.042561, 0.044353]`). That result does not rescue the historical claim: the construction was specified after the inferential defect was found and no familywise procedure was registered at freeze. Under the conservative exact-episode gate, p13 is excluded; the maximum eligible slope belongs to p05/s2a (+0.0833) with `p=0.773206`. The separate Round 5 attainability audit shows that the n=6 exact-gate family is not powered for conventional familywise rejection, so this result is not decisive evidence against a p13-sized response.

## Status

The archived data do not supply a prospectively controlled persona-level incentive-response existence result. They also do not decisively disconfirm p13 under an adequately powered conservative family procedure. The historical mechanical verdict remains visible; the scientific interpretation is a replication target plus an auditable example of where exact procedural enforcement stopped short of valid family-level inference.

Machine-readable summary: `figure-sources/p13-family-audit-final.json`. Round 5 gate-power audit: `round5/round5-review-audit.md`.
