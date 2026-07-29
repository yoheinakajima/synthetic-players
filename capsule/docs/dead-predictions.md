# Dead predictions: author expectations the machinery refuted

Every entry below was a pre-registered author prediction — direction stated
before data — that the adjudication machinery refuted on the record. This
list is enumerated from the registries and reports, not from memory. Count:
**ten affirmative refutations** (reconciliation of near-misses below).

| # | Claim | The author predicted | Registration | Verdict (key number) | Record |
|---|---|---|---|---|---|
| 1 | v1 Claim 1 | TFT achieves >50% cooperation vs Always Defect | v1 claims registry (`docs/v1/claims-v1.json`) | **REFUTED** — observed 0.02 (margin −0.48) | `docs/POSTMORTEM.md` §E1, verdict table |
| 2 | P3-A1 | Shadow of the future: round-1 cooperation higher at δ=.90 than δ=.10 | `docs/phase3-preregistration.md` | **REFUTED** — 0.000 at both δ levels (n=20 each, sd=0) | `docs/phase3-report.md` |
| 3 | P3-A2 | Risk-dominance separation across δ | `docs/phase3-preregistration.md` | **REFUTED** — pooled 0.000 vs 0.000 | `docs/phase3-report.md` |
| 4 | P3-A3 | LLM round-1 cooperation in the human band [36%, 63%] | `docs/phase3-preregistration.md` | **REFUTED** — 0.000 vs band [0.36, 0.63] | `docs/phase3-report.md` |
| 5 | P3-A4 | Isomorph invariance (payoff-equivalent games behave alike) | `docs/phase3-preregistration.md` | **REFUTED** — fails on separation limb; equality limb vacuous at the 0–0 floor | `docs/phase3-report.md` |
| 6 | P3-C1 | Round-1 RPS distribution matches the human paper (rock in [33%, 40%]) | `docs/phase3-preregistration.md` | **REFUTED** — rock 0.80 (modal ✓ but far outside the band) | `docs/phase3-report.md` |
| 7 | P3-C3 | First-order tracker exploits the LLM beyond the Nash baseline | `docs/phase3-preregistration.md` | **REFUTED, sign reversed** — tracker per-round −0.103 vs LLM; CI [−0.133, −0.027] entirely negative | `docs/phase3-report.md` |
| 8 | P3-X1 | Paraphrase robustness of the A-corner (the 0.000 corner survives rewording) | post-result registration, `docs/phase3-report.md` §6 | **REFUTED** — round-1 cooperation 1.000 (sd=0) under each of two rewordings, same seeds; full corner flip | `docs/phase3-report.md` §6 |
| 9 | P4-D3-1 | Labeled-option bias toward the first-listed option | `docs/phase4/predicates.md` | **NOT SUPPORTED, sign reversed** (primary tier) — mean D_ep −0.1806; P(first-only > rock-only) = 0.0001; bias runs toward rock-only | `docs/phase4/d3-report.md`, `docs/phase4/final-report.md` |
| 10 | P4-F directional | Shuffled-history opponent underperforms the first-order tracker (order carries exploitable signal beyond marginals) | `docs/phase4/predicates.md` §F | **NOT SUPPORTED, nominal sign reversed** — Δ(fo−shuffled) −0.083, LB −0.116 | `docs/phase4/f-report.md`, `docs/phase4/final-report.md` |

## Reconciliation: not-supported ≠ refuted

The following registered claims failed to reach support but are **non-
detections, not refutations** — no registered direction was affirmatively
reversed, or the registered branch explicitly covers the outcome. They are
listed so the count of ten cannot be mistaken for a cherry-pick:

- **P4-D1-W / -WM / -WL / -ML (gpt primary)** — all four presentation
  main-effects null (Holm-p ≥ 0.766). A predicted-effect-absent result; the
  cross-vendor mirror finding structure here is part of the thesis, not a
  refutation of it.
- **P4-D2-2 (gpt)** — word-channel effect null on the primary tier (+0.000);
  supported on the mirror.
- **P4-E-1..4** — corner-confounded (registered branch i): the assay's
  occupancy gates were violated at ceiling/floor. Explicitly NOT evidence of
  δ-insensitivity; the registered branch existed for exactly this outcome.
- **P4-F-1 Ū_wsls limb** — the only-first registered branch: wsls out-
  exploits fo (supported limb) but does not itself profit (LB straddles 0).
  Registered as a branch, not a directional refutation.
- **v1 claims 4–7** — went **inconclusive** (not refuted) under v2
  re-adjudication: the original claims were sharper than the data permits.

Supported claims, for the full picture: v1 #2, #3, #8, #9 (v2-exact);
P3-B1, P3-B3, P3-C2; P4-X2-1, P4-D2-1, P4-D2-4 (both tiers), P4-D2-2 (mirror
only), P4-F wsls-vs-fo limb and ngram2 secondary; plus the F fo-tracker
*negative* finding (the subject beats first-order tracking — a supported
claim nobody predicted, adjacent to dead prediction #7's Phase 3 twin).
