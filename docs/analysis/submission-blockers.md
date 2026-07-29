# Paper review and submission gate — current status

> **STATUS: READY FOR FULL SCIENTIFIC REVIEW, 2026-07-29.** The sealed experimental program remains closed. All executable zero-subject-call analyses required by the statistical review are complete and committed. Remaining work is editorial/submission work or explicitly deferred external-data contextualization.

## Gate rule

A task is complete only when its generated artifacts, paper interpretation, and provenance statement agree. Historical mechanical verdicts remain immutable; post-adjudication analyses are labeled separately and cannot retroactively create prospective confirmation.

## A. Statistical inference — complete

### A1. Episode-level sensitivity — **COMPLETE**

Historical predicates counted seat-level binary trials even though two seats share an episode. The committed primary sensitivity defines the episode outcome as 0, 0.5, or 1 and uses a conservative exact projection of simultaneous Clopper–Pearson intervals for `1[Y≥0.5]` and `1[Y=1]`.

Results:

- historical P5-1a restricted count: 3/32 = 0.0938;
- primary exact-episode count: 2/32 = 0.0625;
- historical all-cell count: 14/96;
- primary exact-episode count: 11/96;
- Dirichlet–Jeffreys sensitivity: 5/32 and 19/96, which would fail the historical restricted threshold;
- three cells change classification between the historical and exact-episode rules.

The percentile cluster bootstrap is retained in the audit trail but rejected as the primary interval because it becomes degenerate when every observed episode agrees. Disagreement among the methods is reported as method sensitivity rather than resolved by selecting the favorable verdict.

P5-2 and clause (b) were also recomputed at the episode level:

- pooled P5-2 remains persona-dominant: mean 0.1278, exact interval [0.0918, 0.1721];
- every repeated-game conflict subcell is mixed under the exact episode interval;
- only the word/payoff-confounded swap cell is individually persona-dominant;
- all 24 clause-(b) lanes retain simultaneous familywise lower bounds above 0.20; the minimum is 0.4618.

Artifacts: `submission/episode-cluster-sensitivity.md` and its `figure-sources/` tables.

### A2. p13 family audit — **COMPLETE; ALL COMPUTED VARIANTS REPORTED**

A 200,000-permutation audit applies a maximum raw-slope statistic over all 32 evaluable clause-(a) candidates and reruns each gate within every permutation.

| gate construction | maximum | familywise p | MC 95% interval | interpretation |
|---|---:|---:|---|---|
| Historical seat-level CP | p13, +0.4167 | 0.059230 | [0.058194, 0.060268] | Reproduces the frozen gate structure but adds post hoc family control. |
| Episode-cluster percentile bootstrap | p13, +0.4167 | 0.043455 | [0.042561, 0.044353] | Reported because computed; non-primary because percentile intervals degenerate at exact corners. |
| Conservative exact-episode CP (**primary sensitivity**) | p05/s2a, +0.0833 | 0.773206 | [0.771363, 0.775039] | p13 fails the episode-level interiority gate; only p04/s2p and p05/s2a survive. |

Chronology is load-bearing: no familywise variant was registered at the original freeze, and no seal-before-compute record exists for the post-adjudication analyses. They were specified and executed after external review, run in GitHub Actions against archived databases with fixed seeds, and committed regardless of direction. The favorable `p=0.043455` construction therefore cannot rescue the claim. p13 remains a replication target under every variant.

Artifact: `submission/p13-family-audit-final.md`.

### A3. Between-prompt variance correction — **COMPLETE**

A method-of-moments correction subtracts estimated finite-opportunity noise from the variance of prompt means. The primary 50,000-replicate bootstrap retains all sixteen fixed prompts and resamples episodes within each prompt. A separate two-stage bootstrap also resamples prompts and is labeled exploratory persona-population uncertainty.

| cell | corrected SD | fixed-panel episode-bootstrap 95% | between share | fixed-panel share 95% | exploratory persona-population SD 95% |
|---|---:|---|---:|---|---|
| rep-d10-s2a | 0.4182 | [0.4122, 0.4391] | 85.5% | [82.0%, 93.8%] | [0.2724, 0.4879] |
| rep-d10-s2p | 0.4784 | [0.4696, 0.4916] | 96.1% | [94.6%, 98.9%] | [0.3696, 0.5123] |
| rep-d90-s2a | 0.4408 | [0.4279, 0.4654] | 88.8% | [86.7%, 94.6%] | [0.3457, 0.4890] |
| rep-d90-s2p | 0.4323 | [0.4269, 0.4496] | 90.2% | [87.9%, 95.5%] | [0.3345, 0.4847] |

All four fixed-panel corrected-SD lower bounds exceed the historical `0.75 × published human SD` threshold. Three of four exploratory persona-population lower bounds do. Neither result is a protocol-matched estimate of human latent heterogeneity.

Artifact: `submission/variance-correction.md`.
## B. Human comparator

### B1. Dal Bó–Fréchette microdata contextualization — **DEFERRED EXTERNAL DATA; NOT BLOCKING**

The official replication package remains login-gated. The fixture-tested script is ready at `engine/r2_df_reanalysis.py`, and the operator action is documented in `df-microdata-PENDING.md`.

The statistical review gate is complete with this Q5 task deferred. The current draft uses no matched-magnitude, N-fold, human-interiority, or individual-human-response claim. Every published human comparison is labeled protocol-nonmatched. Q5 becomes blocking only if such claims are restored.

### B2. Matched human arm — **NOT A BLOCKER FOR THE NARROW PAPER**

A matched human arm is required for human–LLM equivalence or substitution claims. The current draft makes neither.

## C. Theory, terminology, and literature

### C1. Identification propositions — **COMPLETE**

`propositions.md` distinguishes:

- partial identification of aggregate response under broad bands;
- nonidentification of between/within decomposition from mean and total variance;
- nonidentification of complete propensity shape from finite moments;
- nonidentification of cross-condition coupling from condition-specific marginals;
- explicit prompt identity from latent-person identity.

### C2. Lin et al. relationship — **COMPLETE**

Living documents state that explicit assignment and execution are controlled, while latent-person invariance is untested and Lin-style drift may coexist with the observed composition pattern.

### C3. Retired-language scan — **COMPLETE**

Automated lint scans assertion-bearing living prose for retired claims, validates paper-facing relative links, and enforces the sealed/data-file boundary against `main`.

### C4. Citation metadata and formatted bibliography — **EDITORIAL, STILL OPEN**

The literature set and novelty boundary are ready for scientific review. Before formal submission, recent-preprint versions, authors, titles, and venues must receive a final metadata pass and the shorthand citations must be converted to the target venue's bibliography format. This does not block reviewer evaluation of novelty or framing.

## D. Counts, reproducibility, and chronology

### D1. Count reconciliation — **COMPLETE**

- 5,540 distinct run IDs with any event;
- 5,505 archived completed runs;
- 4,576 completed Phase 4–5 runs in the replay contract;
- 54,276 round events;
- 108,552 seat-round decisions;
- 36,251 provider-request events in the full store;
- 30,530 Phase 4–5 calls in the transactional ledger;
- 13,141,675 input tokens and 45,247 output tokens in that ledger.

Artifact: `submission/count-reconciliation.md`.

### D2. Reproduction capsule and sealed boundary — **COMPLETE**

The integrated workflow passed capsule checksums, replayed all 4,576 Phase 4–5 runs with zero credentials and zero live model calls, validated paper-facing links, and verified that sealed/data files did not change.

### D3. Scope-seal header ambiguity — **COMPLETE BY ADDENDUM**

`docs/paper/scope-seal.md` remains byte-identical because its hash is pinned in the Phase 5 seal, even though its pre-seal header says “PROPOSED — UNSEALED.” `docs/paper/scope-seal-status.md` documents the sealing event and operative stopping rule.

### D4. Review chronology — **COMPLETE**

`docs/reviews/` records the round-2 methods review, reviewer role expansion, automated execution/integration boundary, and independent round-3 anonymous-clone verification.

## E. Paper architecture and public review surface

### E1. Main-text scope — **COMPLETE**

The v5 paper has three contributions: empirical result, mechanism/identification, and auditability. p13 is an inferential-correction case, not a positive result. Lucas and equifinality are organizing analogies in Discussion rather than novelty claims in the Introduction.

### E2. Public navigation — **COMPLETE**

`REVIEW.md` is the canonical reviewer entry point. README and the analysis index link the manuscript, review records, novelty map, literature map, propositions, completed analyses, reproduction instructions, and this status file.

### E3. Draft history — **INTEGRATION TASK**

Draft v2 and v3 were supplied as exact manuscripts and should be committed under `docs/paper/history/` so correction-ledger version references resolve to public files. This task is editorial provenance, not scientific analysis.

## Remaining before formal submission

1. Commit the exact v2/v3 manuscripts under `docs/paper/history/`.
2. Complete the final metadata/bibliography pass for the chosen venue.
3. Human author sign-off on final title, target venue, and venue-specific AI-assistance statement.

None of these prevents full scientific review of the current GitHub surface.
