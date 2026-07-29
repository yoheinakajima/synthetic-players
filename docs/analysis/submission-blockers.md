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

A method-of-moments correction subtracts estimated finite-opportunity noise from the variance of prompt means. The primary 50,000-replicate bootstrap retains all sixteen fixed prompts and resamples episodes within each prompt. A separate two-stage bootstrap also resamples prompts and is labeled exploratory persona-population uncertainty.

| cell | corrected SD | fixed-panel episode-bootstrap 95% | between share | fixed-panel share 95% | exploratory persona-population SD 95% |
|---|---:|---|---:|---|---|
| rep-d10-s2a | 0.4182 | [0.4122, 0.4391] | 85.5% | [82.0%, 93.8%] | [0.2724, 0.4879] |
| rep-d10-s2p | 0.4784 | [0.4696, 0.4916] | 96.1% | [94.6%, 98.9%] | [0.3696, 0.5123] |
| rep-d90-s2a | 0.4408 | [0.4279, 0.4654] | 88.8% | [86.7%, 94.6%] | [0.3457, 0.4890] |
| rep-d90-s2p | 0.4323 | [0.4269, 0.4496] | 90.2% | [87.9%, 95.5%] | [0.3345, 0.4847] |

All four fixed-panel corrected-SD lower bounds exceed the historical `0.75 × human SD` threshold. Three of four exploratory persona-population lower bounds do. Neither result is a protocol-matched estimate of human latent heterogeneity.

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

### C3. Retired-language scan — **COMPLETE**

`scripts/paper_submission_lint.py` scans current assertion-bearing prose for retired claims while excluding sealed quotations, correction ledgers, and literature “claims to avoid.” It also checks every paper-facing relative link and enforces the sealed/data-file boundary against `main`. The final integrated workflow passed all three checks.

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

### D2. Reproduction capsule and sealed boundary — **COMPLETE**

The final integrated workflow:

- passed the capsule checksum integrity check;
- staged the archived databases with no provider variables;
- replayed all 4,576 Phase 4–5 runs byte-exact with zero live model calls;
- passed the paper relative-link check;
- passed the sealed/data-boundary check;
- committed only generated post-adjudication analyses and living paper-facing updates.

The living manuscript is not inserted into the immutable historical capsule; the capsule continues to certify the sealed experimental record it was designed to reproduce.

## E. Literature and bibliography

### E1. Final metadata pass — **BLOCKING**

Verify current versions, author lists, titles, and venues for the recent works listed in `literature-map.md`, especially Li–Ji, Persson et al., Lin et al., Harry et al., Xiao et al., Pal et al., Georgousis et al., Same Game/Different Story, SSDataBench, and Whose Personae?.

### E2. Formatted bibliography — **BLOCKING**

Replace bracketed shorthand and remaining placeholders with a final reference list. Cite primary empirical sources for empirical findings rather than attributing them secondhand through a theory paper.

## F. Paper architecture and public navigation

### F1. Main-text scope — **COMPLETE**

The v4 paper retains one claim, one mechanism, and one credibility layer. p13 is now an inferential-correction case, not a positive result.

### F2. Public navigation and relative links — **COMPLETE**

README and the analysis index link the paper, novelty map, literature map, propositions, hierarchy, completed submission analyses, and this checklist. Automated relative-link validation passed on the final integrated working tree.

## Remaining submission blockers

1. Final citation metadata verification.
2. Formatted bibliography.
3. Human author approval of the title, target venue, final attribution statement, and whether any quantitative protocol-nonmatched human comparator remains in the submitted version.
