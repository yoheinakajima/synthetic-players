# Round 5 — Explore Science review of v6

> **SOURCE STATUS: EXTERNAL REVIEW, 2026-07-29.** Explore Science reviewed the 14-page v6 manuscript PDF, *Passing Coarse Marginal Checks Can Be Cheap: Persona Mixtures and Imprecise Incentive-Response Estimates in an LLM Persona Panel*. This record summarizes the PDF supplied by the author. It is a living review artifact, not sealed experimental evidence, and changes no historical verdict.
>
> Source PDF SHA-256: `bc2e021e69b3011a95b05f52ba13eeae2b76fd2cb8d8601aa15025450f086f09`.

## Overall assessment

Explore Science assigned the manuscript **92/100 (95% CI [91, 93]), Platinum tier**, with **0 major and 13 minor issues** and **42 merits**. The report describes the work as substantially exceeding prevailing norms in LLM behavioral research, especially in analytical approach, research design, ethical conduct, and transparency.

The review's three highlighted merits were:

1. cryptographically anchored preservation of precommitted discussion text with additive correction rather than silent rewriting;
2. a zero-credential, single-command pipeline that replays the archived Phase 4–5 record byte-exact without live provider access;
3. closed-form identification bounds showing precisely what coarse marginal validation does and does not identify.

The review's central diagnosis is not that the paper's core result is wrong. It is that several load-bearing procedures and identifiers remain insufficiently self-contained in the manuscript, and that the post-adjudication exact gate is being interpreted more strongly than its power permits.

## Highest-priority issues

The PDF details ten of the thirteen minor issues. Three additional issues are available only through Explore Science's online surface and are not present in the supplied PDF; they must be captured before the response round is closed.

| ID | Issue | Initial disposition |
|---|---|---|
| A1 | **Phase architecture is not summarized in the main text.** Readers cannot evaluate the chronology and registration logic without consulting the repository. | **Accept.** Add a compact phase table in Methods covering sequence, primary question, unit, and registration status. |
| A2 | **Cryptographic anchoring is described too broadly.** Replay proves determinism from the current archive, but the paper does not state whether raw completion payloads were independently hashed at receipt or provider-attested. | **Verify, then narrow precisely.** Document whether event/payload hashes or provider response IDs exist. If not, state that registries/freeze packets and later archive snapshots are anchored, while individual payloads lack receipt-time provider attestation. |
| B1 | **Dynamic interiority filtering inside permutations is ambiguous.** Proper familywise inference requires reapplying the complete gate within every permutation. | **Clarification, not a new analysis.** The code dynamically reapplies both condition gates for every candidate in every permutation via precomputed lookup tables. State this explicitly, quantify the operations, and add a regression test/documentation pointer. |
| B2 | **No format-matched dummy control for the persona-prefix contrast.** The bare-versus-persona reversal cannot isolate persona semantics from token count, position, or generic prefix disruption. | **Accept as a construct limitation.** Replace “persona presence” with “adding an explicit persona-format prefix.” Retain the within-template direction contrast, but do not claim semantic presence is isolated. Register a length/format-matched filler control in a future phase. |
| B3 | **The conservative exact episode-level family gate is severely underpowered at six episodes per arm.** Failure to confirm p13 is not disconfirmation. | **Accept; highest-priority analytical response.** Add an exact attainability/power audit. Reframe p13 as not prospectively established and not adjudicable under the current family-controlled design, rather than overturned by a powerful contrary test. |
| B4 | **Protocol labels are undefined in the main text.** `S2-absent`, `S2-present`, `P5-1a`, `P5-2`, `P5-3`, clause (a), and clause (b) are load-bearing but unexplained. | **Accept.** Add a compact protocol glossary/table and define each label at first use. |
| B5 | **The reason given for rejecting the percentile bootstrap is logically incorrect.** A degenerate `[0,0]` interval does not falsely pass an interiority gate requiring bounds inside `(0.05,0.95)`. | **Accept and correct everywhere.** Prefer the exact projection for finite-sample coverage and explicit policy uncertainty, not because exact-corner degeneracy creates false-positive interiority. Keep all post-review variants reported symmetrically. |
| B6 | **The span-ladder localization procedure is not operationally defined.** | **Accept.** Summarize the sealed six-span decomposition, forward/reverse ladders, screening rule, selection rule, and fresh-seed 20+20 confirmation in the main text. |
| B7 | **The continuation-probability treatment is not a semantically neutral economic lever.** Changing `10%` to `90%` changes both the formal continuation parameter and its linguistic representation. | **Accept.** Use “continuation-probability treatment under a specified representation” and state that the point contrast combines numerical-incentive and framing channels. A future factorial should separate them. |
| C1 | **Figure 5 misattributes the exact-gate `p=0.773206` to p13.** Under that gate, p13 is excluded and the p-value belongs to the maximum surviving candidate. | **Accept immediately.** Relabel the figure as a family-audit comparison; show p13 as gate-ineligible for the exact construction and label `p05/s2a` as the exact-gate argmax. |

## Important synthesis

### What survives unchanged

- The paper's strongest result remains the fixed-panel composition finding: coarse marginal criteria can coexist with 85%–96% estimated between-prompt variation and small but imprecise aggregate continuation-treatment point estimates.
- The representation results remain strong, subject to more self-contained description.
- The public correction architecture remains a major methodological contribution.
- No human-substitution, equivalence, or narrow-null claim is supported or needed.

### What should change in interpretation

The current language occasionally treats the conservative exact gate as if it *overturned* p13. The correct synthesis is narrower:

> The frozen per-candidate rule did not control multiplicity or episode dependence, so p13 was never prospectively established at the family level. The archived sample is too small for the conservative exact family gate to confirm or refute a persona-level response of the relevant form. p13 remains a prospectively testable replication target.

This distinction preserves the core correction while avoiding absence-of-evidence language.

### Preliminary power/attainability observation to formalize

At `n=6` complete episodes per condition, enumeration of the exact episode-interiority rule admits condition means only between `1/3` and `2/3`; the largest possible difference between two gate-passing condition means is therefore `1/3`. In the archived 32-candidate family audit, the exact-gate null 95th percentile is also `1/3`. This strongly suggests that the present exact-gate/max-slope procedure cannot deliver a conventional positive familywise result at the current sample size. A committed zero-call script should verify and report this formally rather than leaving it as an informal calculation.

## Missing material

The Explore Science cover reports **13 minor issues**, but the supplied standard PDF details only the ten issues above and notes three additional online-only items. Obtain and archive the full online issue export before declaring Round 5 fully dispositioned.
