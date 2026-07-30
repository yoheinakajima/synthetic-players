# Round 5 Explore Science disposition matrix

> **STATUS: LIVING RESPONSE RECORD.** This matrix maps all thirteen minor issues in the Explore Science review to a disposition, implementation, and evidence location. It does not modify any sealed artifact or historical mechanical verdict. Zero-call audit outputs are generated under `docs/analysis/submission/round5/`.

| ID | Disposition | v7 action | Evidence / future work boundary |
|---|---|---|---|
| A1 | **Adopted** | Add a five-stage architecture table to §3 with question, unit, and registration status. | `docs/paper/paper-draft.md` §3.1. |
| A2 | **Adopted with audited boundary** | State request hashes, raw-response and response-ID coverage, archive checksum/timestamp coverage, and the absence of receipt-time provider attestation or per-response hash chaining. | `docs/analysis/submission/round5/round5-review-audit.md`; future calls should add receipt-time response hashing or provider attestation. |
| B1 | **Verified; reporting omission corrected** | Document that both condition gates are dynamically reapplied for every candidate inside every permutation; add lookup/direct parity and dynamic-vs-static regression checks. | `round5-review-audit.{md,json}` and `artifacts/api-server/engine/round5_review_audit.py`. |
| B2 | **Concede construct confound** | Replace a semantic “persona presence” claim with the observed effect of adding the registered persona-format prefix; disclose missing format/length-matched neutral controls. | Main text §4.3 and §6; neutral-prefix controls are future registered work. |
| B3 | **Adopted and tested** | Exhaustively enumerate n=6 exact-gate attainability, estimate the archived-family tail at the maximum eligible slope, and add model-dependent prospective planning simulations. Reframe p13 as neither prospectively confirmed nor decisively disconfirmed. | `round5-review-audit.md`; `figure-sources/exact-gate-attainability.csv`; `prospective-power.csv`. |
| B4 | **Adopted** | Define S2-absent/present, P5-1a/1b, P5-2, and P5-3 clauses (a)/(b) inline. | Main text §3 protocol glossary. |
| B5 | **Adopted; rationale corrected** | Remove the false-positive-at-corners rationale. Treat the exact projection as the conservative finite-sample coverage reference and the percentile bootstrap as a reported small-sample sensitivity without a comparable coverage guarantee. | §3, §4.4, Figure 5, `episode-cluster-sensitivity.md`, and `p13-family-audit-final.md`. |
| B6 | **Adopted** | Define six rendered spans, forward/reverse ladders, screening criterion, deterministic tie-break, and held-out confirmation with disjoint seeds. | Main text §4.3; sealed source packet `docs/phase4/x2-diff-packet.md`. |
| B7 | **Adopted** | Reframe δ as a represented continuation-probability treatment that changes both the environment and the language communicating it; do not call the contrast a pure numeric incentive effect. | Main text §4.1, §5.1, and §6; a probability × wording factorial is future registered work. |
| B8 | **Adopted** | Add a concise descriptive Gemini result and direct repository pointer; retain exclusion from confirmatory inference because of endpoint non-stationarity. | Main text §4.1; `docs/analysis/figure-sources/p5-tierC-gemini.csv`. |
| B9 | **Adopted** | Ground Proposition B in the law of total variance and classical Fréchet–Hoeffding/Sklar coupling results; retain novelty only in the LLM-validation application and empirical decomposition. | Main text §4.2 and references. |
| C1 | **Corrected** | Rename Figure 5 as a family-audit comparison and explicitly attribute the exact-gate point to p05/s2a while marking p13 gate-ineligible. | `scripts/generate_review_figures.py`; Figure 5 and caption. |
| C2 | **Corrected** | Render fixed-panel aggregate markers as diamonds, consistent with the caption. | Figure 1 generator and output. |

## Release rule

The v7 reviewer package is acceptable only after:

1. the Round 5 audit regenerates successfully from the archived databases;
2. the manuscript, generated audit documents, summary JSON, and figures agree;
3. paper assertion/link/sealed-boundary lint passes;
4. the formatted PDF builds and passes text/page preflight; and
5. all 4,576 Phase 4–5 runs replay byte-exact with zero credentials and zero live provider calls.
