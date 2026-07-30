# Round 10 — Explore Science review of v11

> **SOURCE STATUS:** External review dated 2026-07-30. Reviewed artifact: `synthetic-players-review-v11.pdf`. Source PDF SHA-256: `3c210460ea80813ab70ad938135a1a34937ed2551b03c48a07c3e2a44f59d698`.

## Verdict

Explore Science scored v11 **96/100, Platinum tier**, with **12 minor issues and no major issues**. The synopsis called the manuscript “in strong overall condition” and characterized the remaining needs as modest, concentrated in reporting completeness and interpretive precision.

## Highest-priority issues

1. **B1 — bootstrap/reference coincidence:** independently verify why the conditional episode-bootstrap lower bound for `rep-d10-s2a` rounds to the same four-decimal value as the Dal Bó–Fréchette human SD.
2. **B2 — label-conflict mechanism:** explicitly consider learned game-theoretic prior knowledge as a competing explanation for the “Defect”-label result.
3. **B3 — leaning strata:** publish the cooperative-leaning and defect-leaning condition means supporting the claimed 0.5–0.7 gaps.

## Complete issue set

| ID | Area | Request |
|---|---|---|
| A1 | replay coverage | extend or precisely scope the capsule’s Phase 3 boundary |
| A2 | terminology | define “switch-bearing” at first use |
| A3 | decoding | state top-p, penalties, and logit-bias handling |
| B1 | numerical audit | independently reproduce the 0.4122 bootstrap bound |
| B2 | construct validity | add game-theoretic prior/memorization as competing mechanism |
| B3 | reporting | publish leaning-stratum means and gaps |
| B4 | interval interpretation | connect width to n=6 and exact corner-retaining inference |
| B5 | protocol transparency | define P3-A3 and the historical corner-mixture predicate |
| B6 | multiplicity | preregister the candidate family and exact FWER rule in replication |
| B7 | binary census | attribute method sensitivity jointly to interval width and n=6 discreteness |
| B8 | emphasis | lead with uncertainty-propagating composition estimates rather than plug-in values |
| C1 | entropy | define choice entropy and aggregation level |

## Authors’ response rule

Every numerical concern is tested independently before prose changes. The v12 branch adds a complete Phase 3 zero-call replay audit, an independently implemented bootstrap verification, a full leaning-strata table, a matched temperature-entropy reanalysis, and an archived decoding-parameter inspection. Manuscript edits are generated only after those checks pass.
