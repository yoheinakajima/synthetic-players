# Paper submission gate — current status

> **STATUS: ACTIVE PAPER CHECKLIST — 2026-07-29.** This file governs submission readiness only. It does not reopen the sealed research program, authorize new subject calls, or change historical mechanical verdicts. The principal zero-call statistical analyses are now complete and committed under `docs/analysis/submission/`.

## Gate rule

The paper is submission-ready only when every remaining **blocking** item is completed, removed with its dependent claim, or explicitly accepted as a limitation with corresponding language downgraded.

## A. Statistical inference

### A1. Episode-level sensitivity — **COMPLETE**

Historical predicates counted seat-level binary trials even though two seats share an episode. The committed sensitivity defines the episode outcome as 0, 0.5, or 1 and uses a conservative exact projection of simultaneous Clopper–Pearson intervals for `1[Y≥0.5]` and `1[Y=1]`.

Results:

- historical P5-1a restricted count: 3/32 = 0.0938;
- exact episode count: 2/32 = 0.0625;
- historical all-cell count: 14/96;
- exact episode count: 11/96;
- Dirichlet–Jeffreys sensitivity: 5/32 and 19/96, which would fail the historical restricted threshold;
- three cells change between the historical and exact episode rules.

The initially generated percentile cluster bootstrap is retained but rejected as primary because it becomes degenerate when every observed episode agrees. This correction is documented in `submission/episode-cluster-sensitivity.md`.

P5-2 and clause (b) were also recomputed at the episode level:

- pooled P5-2 remains persona-dominant: mean 0.1278, exact interval [0.0918, 0.1721];
- every repeated-game conflict subcell is mixed under the exact episode interval;
- only the word/payoff-confounded swap cell is individually persona-dominant;
- all 24 clause-(b) lanes retain simultaneous familywise lower bounds above 0.20; the minimum is 0.4618.

Artifacts:

- `submission/episode-cluster-sensitivity.md`
- `submission/figure-sources/episode-cluster-cells.csv`
- `submission/figure-sources/episode-exact-p52.csv`
- `submission/figure-sources/episode-exact-clause-b.csv`

### A2. p13 family audit — **COMPLETE; p13 DOES NOT SURVIVE EPISODE-LEVEL INFERENCE**

A 200,000-permutation audit uses the same raw-slope statistic for observed and permuted data and reruns the full gate-plus-maximum-selection procedure across all 32 evaluable clause-(a) candidates.

Results:

- historical seat gate: p13 is the maximum at +0.4167, familywise p = 0.059230, Monte Carlo 95% interval [0.058194, 0.060268];
- exact episode gate: p13 fails the two-sided interiority requirement;
- only p04/s2p and p05/s2a pass both exact episode gates;
- maximum surviving slope = +0.0833 at p05/s2a, familywise p = 0.773206.

Status: historical mechanical P5-3 remains unchanged, but clause-(a) no longer supports an unconfounded existence interpretation. p13 is a replication target only and has been removed from the abstract and contributions.

Artifact: `submission/p13-family-audit-final.md`.

### A3. Between-prompt variance correction — **COMPLETE**

A method-of-moments correction subtracts estimated finite-opportunity noise from the variance of persona means. A 50,000-replicate hierarchical bootstrap resamples personas and episodes.

Corrected between-prompt SDs:

| cell | corrected SD | bootstrap 95% interval | between share of total episode-level variance |
|---|---:|---|---:|
| rep-d10-s2a | 0.4182 | [0.2703, 0.4876] | 0.855 |
| rep-d10-s2p | 0.4784 | [0.3643, 0.5123] | 0.961 |
| rep-d90-s2a | 0.4408 | [0.3466, 0.4892] | 0.888 |
| rep-d90-s2p | 0.4323 | [0.3358, 0.4854] | 0.902 |

All point estimates meet the historical `0.75 × human SD` threshold; three of four bootstrap lower bounds do. These remain fixed-panel prompt-heterogeneity estimates, not matched human latent variances.

Artifact: `submission/variance-correction.md`.

## B. Human comparator

### B1. Dal Bó–Fréchette microdata contextualization — **EXTERNAL-DATA PENDING; NOT BLOCKING UNDER CURRENT CLAIM SCOPE**

The official replication package remains login-gated. The fixture-tested script is ready at `engine/r2_df_reanalysis.py` and the exact operator action is documented in `df-microdata-PENDING.md`.

The current draft does not use a matched-magnitude or N-fold claim and treats the published values only as protocol-nonmatched context. Under that scope, the microdata reanalysis is desirable but not submission-blocking. It becomes blocking if the paper restores:

- a human–LLM effect-size ratio;
- a claim that human subject distributions are more interior;
- matched human variance language;
- a human distribution of individual response `Δ_i`.

### B2. Matched human arm — **NOT A BLOCKER FOR THE NARROW PAPER**

A matched arm is required for human–LLM equivalence or substitution claims. The current draft makes neither.

## C. Theory and terminology

### C1. Identification propositions — **COMPLETE**

`propositions.md` now distinguishes:

- partial identification of the aggregate contrast under broad bands;
- nonidentification of between/within decomposition from mean and total variance;
- nonidentification of full propensity shape from finite moments;
- nonidentification of cross-condition coupling from condition-specific marginals;
- prompt identity from latent-person identity.

### C2. Lin et al. relationship — **COMPLETE**

Living paper-facing documents now state that explicit assignment and execution drift are controlled, while latent-person invariance is untested and Lin-style drift may coexist with the observed composition pattern.

### C3. Retired-language scan — **PENDING FINAL AUTOMATED CHECK**

The paper, README, novelty map, literature map, propositions, hierarchy, and program synthesis have been rewritten. Before submission, run a branch-wide scan of living documents for:

- “not payoff-determined”;
- “fixed, drift-free population”;
- “δ-matched”;
- “fivefold” / “one-fifth human response”;
- “human interior heterogeneity”;
- “deterministic persona” as a policy claim;
- “no game-relevant instruction” outside quoted sealed text;
- p13 as a confirmatory existence result;
- exact moment-matching language.

Sealed historical records are excluded from replacement and retain adjacent corrections when quoted.

## D. Counts and reproducibility

### D1. Count reconciliation — **COMPLETE**

Generated counts:

- 5,540 distinct run IDs with any event;
- 5,505 archived completed runs;
- 4,576 completed Phase 4–5 runs in the public replay contract;
- 54,276 round events;
- 108,552 seat-round decisions;
- 36,251 archived provider-request events in the full store;
- 30,530 Phase 4–5 calls in the transactional budget ledger;
- 13,141,675 input tokens and 45,247 output tokens in that ledger.

The paper and README now distinguish every noun and scope. Artifact: `submission/count-reconciliation.md`.

### D2. Reproduction capsule — **COMPLETE FOR SEALED RECORD; FINAL PAPER-LINK CHECK PENDING**

The current capsule replays 4,576/4,576 Phase 4–5 runs anonymously with zero live calls. After the final editorial patch:

- run relative-link validation;
- decide whether the living paper-facing documents belong inside the immutable capsule;
- verify no sealed artifact hash changed;
- update any release manifest only through the declared process.

## E. Literature and bibliography

### E1. Final metadata pass — **BLOCKING**

Verify current versions, author lists, titles, and venues for the recent works listed in `literature-map.md`, especially Li–Ji, Persson et al., Lin et al., Harry et al., Xiao et al., Pal et al., Georgousis et al., Same Game/Different Story, SSDataBench, and Whose Personae?.

### E2. Formatted bibliography — **BLOCKING**

Replace bracketed shorthand and remaining placeholders with a final reference list. Cite primary empirical sources for empirical findings rather than attributing them secondhand through a theory paper.

## F. Paper architecture and public navigation

### F1. Main-text scope — **COMPLETE**

The v4 paper retains one claim, one mechanism, and one credibility layer. p13 is now an inferential-correction case, not a positive result.

### F2. Public navigation — **MOSTLY COMPLETE; LINK CHECK BLOCKING**

README and analysis index link the paper, novelty map, literature map, propositions, hierarchy, submission analyses, and this checklist. A final automated relative-link check remains.

## Remaining submission blockers

1. Branch-wide retired-language scan over living documents.
2. Final citation metadata verification.
3. Formatted bibliography.
4. Relative-link validation and final capsule/hash check.
5. Human author approval of title, target venue, final attribution statement, and whether any quantitative nonmatched human comparator remains.
