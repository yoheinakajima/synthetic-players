# X2 screening report (interim, per registered rider: final verdicts in step 8)

Generated 2026-07-24T20:57:49Z. candidate iff some adjacent |Δ| ≥ 0.50; largest |Δ|; ties → lowest span index; forward before reverse (frozen, predicates.md)

| rung | mean Y_ep | n |
|---|---|---|
| v1 | 0.0000 | 10 |
| p4-x2-f1 | 0.0000 | 10 |
| p4-x2-f2 | 0.8500 | 10 |
| p4-x2-f3 | 0.7000 | 10 |
| p4-x2-f4 | 1.0000 | 10 |
| p4-x2-f5 | 1.0000 | 10 |
| v2a | 1.0000 | 10 |
| p4-x2-r1 | 0.4500 | 10 |
| p4-x2-r2 | 0.0000 | 10 |
| p4-x2-r3 | 0.0000 | 10 |
| p4-x2-r4 | 0.0000 | 10 |
| p4-x2-r5 | 0.0000 | 10 |

| ladder | pos | span | pair | Δ |
|---|---|---|---|---|
| forward | 1 | S1 | v1 → p4-x2-f1 | +0.0000 |
| forward | 2 | S2 | p4-x2-f1 → p4-x2-f2 | +0.8500 |
| forward | 3 | S3 | p4-x2-f2 → p4-x2-f3 | -0.1500 |
| forward | 4 | S4 | p4-x2-f3 → p4-x2-f4 | +0.3000 |
| forward | 5 | S5 | p4-x2-f4 → p4-x2-f5 | +0.0000 |
| forward | 6 | S6 | p4-x2-f5 → v2a | +0.0000 |
| reverse | 1 | S1 | v2a → p4-x2-r1 | -0.5500 |
| reverse | 2 | S2 | p4-x2-r1 → p4-x2-r2 | -0.4500 |
| reverse | 3 | S3 | p4-x2-r2 → p4-x2-r3 | +0.0000 |
| reverse | 4 | S4 | p4-x2-r3 → p4-x2-r4 | +0.0000 |
| reverse | 5 | S5 | p4-x2-r4 → p4-x2-r5 | +0.0000 |
| reverse | 6 | S6 | p4-x2-r5 → v1 | +0.0000 |

**Candidate:** True
Selected span S2 (forward ladder, |Δ| = 0.85); minimal pair pd-x2-f1 / pd-x2-f2; screened direction: E[Y|p4-x2-f2] - E[Y|p4-x2-f1] > 0.
