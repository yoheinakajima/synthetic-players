# Round 5 response plan — Explore Science review

> **STATUS: IMPLEMENTED AND VALIDATED, 2026-07-30.** All thirteen Explore Science minor issues have a recorded disposition. The zero-call analyses, v7 manuscript, figures, PDF, lint, sealed-boundary check, and 4,576-run replay have passed. This plan did not reopen the sealed experimental program, authorize new model calls, or modify historical mechanical verdicts. Final validation: [`round-5-validation-record.md`](round-5-validation-record.md).

## Response principles

1. **Correct rather than defend imprecise language.** Several critiques identify real overstatement or missing explanation; adopt them directly.
2. **Separate invalid original confirmation from post hoc disconfirmation.** The original p13 rule lacked family/dependence control. The current archive also lacks enough information to provide a powerful conservative rejection. Both facts can be true.
3. **Keep all computed variants visible.** No result is removed because it is favorable or unfavorable.
4. **Do not manufacture controls after the scope seal.** Missing format controls and numeric/semantic de-confounding become explicit limitations and prospective designs.
5. **Make the paper self-contained.** A diligent reader should understand phase chronology, protocol IDs, gates, and the X2 localization procedure without opening the repository.

## Priority 0 — complete the review record

- [x] Archive a faithful Round 5 synthesis and the source PDF hash.
- [x] Obtain the three online-only Explore Science issues omitted from the standard PDF: B8, B9, C2.
- [x] Append all thirteen issues and dispositions to the response matrix.
- [x] Add Round 5 to `docs/reviews/README.md` and the canonical reviewer entry point.

## Priority 1 — analytical corrections before v7

### 1. Dynamic permutation gate documentation — B1

**Verified result:** the complete gate is dynamically reapplied to each candidate in each permutation. The implementation precomputes gate outcomes for all possible three-valued episode compositions and applies the corresponding lookup independently to both permuted conditions.

- [x] State this explicitly in §4.4.
- [x] Report 25,600,000 condition-gate lookup applications at B=200,000 across 32 candidates, two conditions, and two gate constructions.
- [x] Add lookup/direct parity checks: 56 cases, zero failures.
- [x] Add a dynamic-vs-intentionally-static regression: 718/5,000 draws differ.
- [x] Publish code and machine-readable output under `docs/analysis/submission/round5/`.

**Disposition:** resolved by documentation and test; no statistical result changed.

### 2. Exact-gate attainability and power audit — B3

- [x] Enumerate every possible n=6 three-valued episode composition.
- [x] Report gate-passing means and the maximum eligible slope.
- [x] Estimate the archived 32-candidate null tail at the maximum eligible slope.
- [x] Simulate illustrative prospective power over episode counts and family sizes.
- [x] Replace disconfirmatory p13 language.

**Verified result:** at n=6, exact-gate-eligible cell means range from 0.333 to 0.667 and the maximum eligible slope is 0.333. Under the archived family, that maximum has estimated null tail probability 0.075040 (15,007/200,000). The conservative exact procedure therefore cannot achieve conventional familywise rejection in the archived n=6 design.

**Disposition:** p13 was not prospectively family-confirmed and is not decisively disconfirmed by the underpowered conservative post-adjudication procedure; it remains a replication target.

### 3. Bootstrap rationale correction — B5

- [x] Remove the incorrect claim that a degenerate exact-corner percentile interval can falsely pass the strict interiority gate.
- [x] Use the correct rationale: the exact projection supplies finite-sample coverage for the discrete episode mean; the percentile bootstrap is retained as a small-sample sensitivity without a comparable coverage guarantee at n=6.
- [x] Continue to report `p=0.043455` symmetrically.
- [x] Use “conservative exact sensitivity” and “percentile-bootstrap sensitivity” rather than implying prospective primary-method selection.

**Disposition:** accepted and corrected; numerical results unchanged.

## Priority 2 — construct and provenance boundaries

### 4. Persona-prefix format confound — B2

- [x] Replace semantic “persona presence” language with the observed effect of adding the registered persona-format prefix.
- [x] State that the contrast bundles semantic content, length, position, punctuation, and generic token-sequence changes.
- [x] Clarify that leaning differences remain contrasts among complete prompt bundles rather than trait-causal estimates.
- [x] Add a limitation and prospective neutral-prefix control.

**Disposition:** construct qualified; no post-seal cell added.

### 5. Continuation treatment mixes incentive and representation — B7

- [x] Use “represented continuation-probability treatment.”
- [x] State that the treatment changes both the environment and the text used to communicate it.
- [x] Interpret `+0.083/+0.078` as undecomposed represented-treatment contrasts.
- [x] Add a prospective continuation-probability × wording factorial.

**Disposition:** terminology and construct-validity correction; point estimates unchanged.

### 6. Raw completion tamper-evidence boundary — A2

- [x] Audit request hashes, response IDs, raw text, event-store schema, snapshot manifests, and timestamp proofs.
- [x] Publish a provenance matrix and field-coverage CSV.
- [x] State the boundary plainly: replay verifies the released snapshot, not receipt-time provider authenticity.
- [x] Add future receipt-time response hashing/provider attestation as a protocol improvement.

**Verified coverage:** 30,421/30,421 Phase 4–5 requests contain rendered prompts, bundle/request hashes, engine commit, and provider route. 30,397/30,397 response events contain raw completion text and provider response IDs. Individual response payloads were not separately hash-chained or provider-attested at receipt. `capsule/SHA256SUMS.capsule` covers `data/engine.db.xz`.

**Disposition:** evidence guarantee narrowed precisely.

## Priority 3 — self-contained reporting

### 7. Phase architecture table — A1

- [x] Add a five-stage table in §3 with primary question, unit, registration status, and role.
- [x] Distinguish Phase 4 representation/robustness work from Phase 5 persona-panel work.

### 8. Protocol glossary — B4

- [x] Define `S2-absent`, `S2-present`, `P5-1a`, `P5-1b`, `P5-2`, `P5-3(a)`, `P5-3(b)`, and historical verdict versus post-adjudication sensitivity.

### 9. Span ladder definition — B6

- [x] Define the mechanical six-span decomposition, forward/reverse ladders, ten screening rungs, `|Δ|≥0.50` selection rule, deterministic tie-break, and held-out confirmation.
- [x] State 20 fresh episodes per side, seeds 2953–2972, temperature 0.7, with 0/40 versus 37/40 held-out decisions.
- [x] Avoid claiming that all positional/context interactions were eliminated.

### 10. Gemini pointer — B8

- [x] Add one descriptive-results sentence and direct repository pointer.
- [x] Preserve exclusion from confirmatory inference because of endpoint non-stationarity.

### 11. Probability grounding — B9

- [x] Ground Proposition B in the law of total variance and classical Fréchet–Hoeffding/Sklar coupling results.
- [x] Limit novelty to the LLM-validation application and empirical decomposition.

## Priority 4 — figure and machine-readable corrections

### 12. Figure 5 attribution — C1

- [x] Retitle Figure 5 as **Post-adjudication family-audit constructions**.
- [x] Attribute historical and percentile points to p13/s2a.
- [x] Mark p13 gate-ineligible under the exact construction and attribute `p=0.773206` to p05/s2a.
- [x] Correct the caption and source figure.

### 13. Figure 1 aggregate marker — C2

- [x] Render fixed-panel aggregate estimates as diamonds, consistent with the caption.

## Priority 5 — v7 package and response matrix

- [x] Create the point-by-point disposition matrix.
- [x] Regenerate Markdown, figures, machine-readable summary, and line-numbered PDF as v7.
- [x] Run paper lint, link checks, sealed-boundary checks, all zero-call analyses, and the full capsule replay.
- [x] Render all 19 PDF pages and visually inspect the complete document plus every figure/table-heavy page.
- [x] Publish `round-5-validation-record.md`.

## Final claim language after Round 5

### Core result

> In this fixed sixteen-prompt panel, broad marginal criteria coexist with corrected estimates assigning most episode-level variation to differences among prompt configurations. The observed represented continuation-treatment point contrasts are small on the unit scale but too imprecise to establish equivalence, a null response, or a narrow upper bound.

### p13

> p13 passed the frozen per-candidate rule, but that rule lacked prospective family and dependence control. Post-adjudication procedures yield materially different answers, and the conservative exact procedure is underpowered at the archived sample size. The record therefore supplies neither prospectively controlled confirmation nor decisive disconfirmation; p13 is a replication target.

### Persona-prefix effect

> Adding a persona-format prefix reverses the bare swap-cell choice, but the contrast is not semantically isolated from length, position, punctuation, and token-sequence changes. Differences among persona prompts remain substantial under a common template.

### Continuation treatment

> The registered contrast is a response to a represented continuation-probability treatment, combining the formal environment parameter with the wording used to communicate it.

## Future prospectively registered work

- format-matched filler persona-prefix controls;
- numeric continuation probability × wording factorial;
- p13 or small-family replication with adequate episode-level power;
- receipt-time payload hash chain/provider attestation for new calls.

## Release gate — passed

- [x] all thirteen issues have a documented disposition;
- [x] all three online-only issues are archived;
- [x] the exact-gate power audit is reproducible;
- [x] bootstrap rationale and p13 language agree across paper, figures, review docs, and generated summaries;
- [x] Figure 5 correctly attributes the exact-gate result;
- [x] the v7 PDF build, lint, sealed-boundary check, and 4,576-run replay pass.

No known scientific-review blocker remains. Venue-specific formatting and a fresh independent review of v7 are appropriate next steps, not prerequisites for preserving or evaluating this response package.
