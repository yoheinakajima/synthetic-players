# Round 5 gate-power and provenance audit

> **STATUS: POST-ADJUDICATION ZERO-CALL AUDIT.** This document answers Explore Science issues B1, B3, and A2. It changes no sealed artifact or historical verdict. The prospective power table is explicitly model-dependent planning evidence, not a preregistered result.

## B1 — dynamic gate reapplication

**PASS.** The familywise permutation implementation dynamically reapplies the complete condition-level gate inside every permutation. It does not freeze the observed-data candidate mask.

- Lookup/direct parity cases checked: **56**, failures: **0**.
- The implementation precomputes **56** possible-composition gate values and then performs **25,600,000** Boolean condition-gate lookup applications at B=200,000 across 32 candidates, two conditions, and two gate constructions.
- A deterministic regression over 5,000 null draws found dynamic and intentionally static-mask maxima differed in **718** draws (14.4%).
- Concrete witness: `p07/s2a` has observed exact-mask status `False` but a valid permuted assignment with dynamic status `True`.

This regression test would fail if the implementation were changed to use a static observed-data mask.

## B3 — exact-gate attainability at six episodes per arm

The exact episode-level gate admits **12** of the 28 possible three-category outcome compositions at n=6. Its admissible sample means are `[0.333333333333, 0.416666666667, 0.5, 0.583333333333, 0.666666666667]`. Therefore two gate-passing cells can differ by at most **0.3333** at this sample size.

Under the archived 32-candidate null structure, the estimated tail probability at this maximum attainable slope is **p=0.075040** (15,007/200,000 permutations; seed `20260792`). Thus no exact-gate result in the archived n=6 family can reach a conventional 0.05 familywise threshold. The exact-gate audit is therefore informative about dependence and gate eligibility, but it is not a powered disconfirmation of a persona-level response.

The correct p13 status is: **not prospectively confirmed by the frozen rule, and not decisively disconfirmed by the conservative post-adjudication exact procedure; replication target.**

### Illustrative prospective power

The following table assumes independent seat decisions, so an episode outcome is `Binomial(2,p)/2`; one target has p=.333 versus p=.750 and all other candidates are null at p=.5. It is a planning sensitivity only. A Phase 6 registration should simulate its own dependence model and exact decision rule.

| family | episodes/arm | exact critical slope | target gate pass | target passes gate+threshold | family rejection |
|---:|---:|---:|---:|---:|---:|
| 16 | 6 | none | 12.0% | 0.0% | 0.0% |
| 16 | 12 | 0.417 | 59.5% | 22.1% | 24.3% |
| 16 | 20 | 0.325 | 92.5% | 78.1% | 78.9% |
| 16 | 30 | 0.267 | 98.2% | 95.5% | 95.6% |
| 16 | 50 | 0.200 | 99.9% | 99.9% | 99.9% |
| 16 | 75 | 0.160 | 100.0% | 100.0% | 100.0% |
| 16 | 100 | 0.140 | 100.0% | 100.0% | 100.0% |

Complete family-size and sample-size grid: `figure-sources/prospective-power.csv`.

## A2 — completion provenance and tamper-evidence boundary

Phase 4–5 records store the complete rendered system/user bundle, a bundle SHA-256, a deterministic request-body SHA-256, engine commit, provider route, and requested model. The live runner asserts the provider adapter's request-body SHA equals the recorded mirror.

The archive stores raw completion text and, for Phase 4–5 provider adapters, response IDs and selected provider metadata. It does not store a provider-signed response object or a separate receipt-time hash of each raw completion payload.

Published archive snapshots are covered by checksum manifests and external timestamp proofs. This detects changes relative to the released snapshot but does not prove that no edit occurred between provider receipt and snapshot sealing.

Accordingly, byte-exact replay proves reproducibility from the released archive. The checksum and timestamp record makes the released archive tamper-evident relative to its published snapshot. It is **not** provider attestation and does not independently prove immutability of every completion from the instant of receipt.

Machine-readable audit: `round5-review-audit.json`. Field coverage: `figure-sources/provenance-field-coverage.csv`.
