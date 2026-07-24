# Phase 4 provenance notes (running; feeds the step-8 provenance appendix)

Working disclosures recorded at the moment they arise so the final appendix
cannot omit them. Interim per-block reports are working documents; **final
verdicts issue only from the step-8 full replay + adjudication pass.**

1. **"for 1 rounds" grammar (registered rider, 2026-07-24).** The sealed
   one-shot templates render the literal string "for 1 rounds". The template
   bytes are frozen; the oddity is disclosed rather than repaired. No
   evidence of differential effect; any reader can byte-verify against the
   sealed registry.

2. **Sentinel cadence reading.** The sealed schedule notes say "sentinel
   immediately before and after this block" per block. At adjacent block
   boundaries one check serves both notes (the check *after* block N *is*
   the check *before* block N+1). Check indices: 0 = before X2-screening,
   1 = X2/D1 boundary, 2 = D1/D2, 3 = D2/D3, 4 = D3/E, 5 = E/F, 6 = after F.
   Arithmetic: a full check = 3 arms × 2 models × 10 episodes × 2 self-play
   calls = 120 calls; 7 checks = 840, plus 15 Gate-0 calls and 18 planned
   rating calls = 873 of the 900 overhead cap. Any additional check (e.g.
   the weekly rule during a block spanning >7 days) would exceed the cap and
   therefore requires a decision memo first, per the registered cap-breach
   process. The budget document's "60 calls/week" idle line corresponds to a
   half-check; the enforced seat rule (self-play, both seats live) makes a
   full check 120 calls — disclosed here as a budget-note discrepancy.

3. **Sentinel fingerprint definition (sealed with the check-0 baseline).**
   Cell = arm × model. Episode value = seat-1 round-1 action index. Modal
   action = most frequent episode value (tie → lower index). Fingerprint =
   modal count out of 10. Frozen rule (c) compares counts (alert iff Δ ≥ 3
   episodes vs baseline). Modal-action *flips* at similar counts are outside
   the frozen rule's letter and are disclosed as observations. Seat-2
   distributions are archived alongside.

4. **X2 ladder endpoints are the sealed Phase 3 X1 arms** (pd-repeated-v1 /
   v2a, δ=.90, seeds 1–10, matched horizon draws) — reused evidence, no new
   calls. Consequence: if screening selects span 1 or span 6, the minimal
   pair includes a Phase 3 endpoint template, and the write-once resolution
   layer (which requires `pd-x2-*` templates for X2-conf-lo/hi) would refuse
   it. Confirmation in that case requires a registered amendment before
   dispatch. Interior spans (2–5) resolve without amendment.

5. **Horizon rule.** numRounds for E / X2 blocks is drawn client-side by the
   registered Phase 3 rule: geometric(δ) via mulberry32(seed ^ 0x54524D),
   cap 120; a truncated draw excludes the supergame (zero calls, disclosed).
   The driver imports the engine's mulberry32 port; realized-rounds ==
   drawn-horizon parity is machine-checked per episode by the adjudicator's
   integrity scan.

6. **engineCommit discipline (registered rider 2).** The dispatch driver
   refuses to run unless the worktree is clean and HEAD equals the recorded
   preflight commit; the first live run of every driver process asserts the
   engine-stamped commit is {sha: HEAD, dirty: false} and freezes otherwise.
   Driver and adjudicator are committed before first dispatch; their commit
   is the one stamped on every run they dispatch.

7. **Request-construction parity.** The driver builds game definitions with
   the engine's own derivation functions (`_pd_expected_matrix`,
   `_rps_sym_expected_matrix`, `_pure_nash`, registry `options`) rather than
   a reimplementation, and every scheduled step-4 request was validated
   against the enforcement layer via zero-spend dry runs before any live
   dispatch ("dry-all" pass).

8. **Anchoring.** The step-3 seal is externally anchored (GitHub release
   `phase4-v3-seal`, published 2026-07-24T19:04:16Z); the annotated tag is
   NOT GPG-signed (no signing key in the environment) — disclosed deviation,
   see `seal-record.md`. A second, independent timestamp (OpenTimestamps on
   the release's SHA256SUMS.txt) is planned; its outcome (or network
   failure) will be recorded here.

9. **Per-block reporting (registered rider 3).** Blocks are dispatched in
   the sealed order with adjudication + a report to the researcher at each
   block boundary. These interim reports never substitute for the step-8
   full pass.

## OpenTimestamps second anchor (2026-07-24)
- Stamped: `SHA256SUMS.txt` asset of release `phase4-v3-seal`, fetched from GitHub and verified sha256 `082942c06faf6df88dc5cc74960f0d9eaeb53a8485731ffdae924d02a0706fb9`.
- Calendars accepting the digest: a.pool.opentimestamps.org, b.pool.opentimestamps.org, a.pool.eternitywall.com, ots.btc.catallaxy.com.
- Proof committed at `docs/phase4/SHA256SUMS.txt.ots` and attached to the release as an additional asset (addition only; no sealed asset modified). Status: **pending** Bitcoin attestation — run `ots upgrade docs/phase4/SHA256SUMS.txt.ots` after ~24h, then `ots verify` against the release asset. Tooling note: client run with an OpenSSL-3 `LD_PRELOAD` workaround (does not affect proof bytes).

## Pre-dispatch code review (2026-07-24, before any live call)
An independent reviewer audited the dispatch driver and adjudicator against the
frozen predicates before first live dispatch. Findings fixed (no live data
existed yet, so no result is affected): (1) anomaly freezes now always persist
the frozen flag; (2) at-most-once dispatch guard — an inflight marker is
persisted before every live POST and must be resolved via event-store
reconciliation after any ambiguous interruption; (3) finish_reason comparison
made case-insensitive (Gemini reports the enum name `STOP`; OpenAI `stop`);
(4) reverse-ladder span indexing corrected to the sealed definition (R_i =
spans 1..i reverted ⇒ the gap at position i isolates span i in both ladders —
the earlier draft inverted reverse indices; screening had not yet run);
(5) sentinel check-0 baseline made write-once on disk. Dry-all re-validated
after these fixes.

## Event-schema addition: `seed` on `llm.requested` (2026-07-24, before any live call)
Follow-up review round found that phase-4 `llm.responded` events carry
`seed=None` by design (providers run unseeded sampling per protocol), so
event-store recovery keyed sentinel runs on a null seed and could not
guarantee at-most-once redispatch after an ambiguous interruption; the
per-seed X2 analyses would have collapsed for the same reason. Fix: the
scheduled environment seed is now recorded on every `llm.requested` payload
(additive field; passed explicitly, prompt-render inputs untouched so
template byte-parity is unaffected). Driver reconciliation and the
adjudicator read the requested-side seed as authoritative, with the phase-3
event shape as fallback. No live phase-4 events existed before this change.

## X1-endpoint identification fix + X2 screening adjudication (2026-07-24)
The adjudicator's X1 endpoint loader originally resolved phase-3 runs through
the API server's experiments table by batch label; no such labels exist in
either store, so it refused (correctly, loudly). Rewritten to re-derive the
sealed endpoints from the event store alone, identifying runs by game-object
attributes (promptId, δ=90, gpt-4.1, llm-subject self-play, environment seeds
1–10). No sealed rule changed; only the lookup mechanism. Two findings, both
disclosed in x2-screening-report.json: (1) phase 3 contains two complete v1
endpoint batches (every seed duplicated); the mechanical rule accepts
duplicates only when all copies agree exactly on horizon and round-1 actions —
they do — and refuses on any disagreement. v2a has exactly 10 runs, no
duplicates. (2) The matched-horizon premise was verified directly: v1 and v2a
per-seed horizons are identical (90 rounds per rung).

Screening outcome (100/100 episodes; zero retries, invalid trials, and scan
anomalies): forward-ladder span S2 (continuation sentence) carries ΔY = +0.85
(f1 mean 0.00 → f2 mean 0.85), the only gap ≥ 0.50 besides reverse S1 (0.55);
frozen rule selects S2. Minimal pair pd-x2-f1 / pd-x2-f2 — interior rungs, no
amendment required. Resolutions X2-conf-lo / X2-conf-hi written write-once to
the event store (run_1784926714_684aa1fd / run_1784926714_21adc5ac) before any
confirmation dispatch, per the sealed packet. Sentinel check 1 at the X2/D1
boundary: zero alerts against the sealed baseline. Confirmation itself remains
step 5 of the frozen order (after D1→D2→D3).

## D2/D3 adjudication pins (2026-07-24, written during block D1 dispatch — pre-data for D2/D3)

The registered interval spec ("BCa(seed) = bias-corrected accelerated
bootstrap, 10,000 resamples over episodes, mulberry32 seed 20260801"; constant
cells → exact comparison + CP bounds per cell) leaves implementation details
open. They are pinned here BEFORE any D2/D3 episode exists, and the code was
committed and pushed before any D2/D3 dispatch:

- BCa resampler runs on the engine's bit-identical mulberry32; one stream per
  claim, seed 20260801. Draw order: per resample, groups in estimand order
  (minuend first), n index draws per group in position order, index =
  floor(u·n). z0 = Φ⁻¹(#{θ* < θ̂}/B) with strict inequality; acceleration from
  delete-one jackknife across all observations of all groups; endpoint
  quantile k = clamp(floor(α_adj·(B+1)), 1, B), k-th order statistic.
- Exact fallback fires iff either contributing cell is constant: exact
  difference, per-cell CP on seat-level trials (2 per episode), and a
  conservative Bonferroni difference interval (each cell at 1−α/2).
- Verdict p-values by interval inversion (smallest α whose (1−α) interval
  excludes 0), floored at 1/(B+1) so bootstrap precision is never overstated.
  Directional claims (P4-D2-1/2) invert one-sided exclusion; P4-D2-4
  two-sided. Holm step-down at the registered family size m=4 over the three
  CI claims (strictly conservative); P4-D2-3 is adjudicated solely by its
  registered CP thresholds (≥.80 / ≤.20) and consumes no Holm slot.
- D3: one-sided 95% lower bound = the α=.05 BCa endpoint; exact sign-test
  fallback (binomial, H1: median > 0) iff the D_ep sample is constant. The
  support-only Dirichlet(1) posterior (never confirmatory) uses numpy
  default_rng(20260801), 100k draws, seat-level categories {first-only,
  rock-only, both, neither}; the support-only penalized multinomial logit is
  deferred to step 8. Every D3 run's rendered actionLabels are checked against
  the sealed displayOrder binding; any mismatch refuses adjudication.
- Machinery validated on synthetic data (determinism under stream restart,
  known-separation recovery, constant-cell fallback trigger, Holm
  monotonicity, one-sided bound, sign-test path) plus no-data smokes against a
  temporary docs dir so no report file was written before data existed.

Worktree disclosure: these additions were edited into phase4_adjudicate.py
(analysis tooling only — never imported by engine, server, or runner) while
block D1 was dispatching. Engine-process stamps for D1 therefore reflect the
running engine code exactly; the D1 block's dispatch code is byte-identical to
its preflight HEAD.

## Registration gap: E-dselected selection rule (found 2026-07-24, during block D1 dispatch, BEFORE D1 adjudication)

predicates.md §Family E and registry-v3-manifest.md both reference the
D-selected presentation as "resolved by the sealed rule from D1 primary-model
data" / "RESOLVED-BY-D1-SELECTION(pd-rep-*)" — but no document in the sealed
packet states the rule itself (verified: predicates.md incl. full git history,
freeze-packet.md, registry-v3-manifest.md, seal-record.md, x2-diff-packet.md,
provider-packet.md, budget.md). The engine constrains the resolution only to
prefix `pd-rep-` (16 sealed e-repeated-candidate templates,
`pd-rep-{W}-{L}-{O}-{P}`, all M=can as in the community comparator).

Two complete candidate rules are drafted here. Timing, stated exactly: both
rules were drafted while block D1 was still dispatching, before the D1
adjudication mode was run; they are committed at the D1 boundary in the same
push as the D1 report, so commit order alone cannot prove drafting precedence.
The externally checkable pre-commitment is the one that matters mechanically:
both rules are committed and pushed BEFORE the operator's choice between them,
before any resolution write, and before any step-6 dispatch. The operator
(user) picks ONE by name — a choice between two fully specified mechanical
rules, not a free selection informed by cell means. The resolution note will
cite this ledger entry, the chosen rule, and the D1 cell means that
mechanically determine the selection.

- **Rule INTERIOR (recommended):** select the candidate (W,L,O,P) whose D1
  primary-model M=can cell mean Ȳ (10 episodes, cooperation-role share at
  round 1) is closest to 0.5; ties → the earlier template in
  registry-v3-manifest.md line order. Rationale: §E's assay gate requires an
  episode-level 95% interval wholly inside (0.05, 0.95) in at least one δ
  cell; the most interior one-shot presentation maximizes the probability the
  δ-slope assay is valid at all, and refers to no δ quantity (outcome-blind
  for P4-E-1).
- **Rule MAXCOOP:** select the candidate whose D1 primary-model M=can cell
  mean Ȳ is largest; ties → earlier manifest line order. Rationale: probes
  δ-sensitivity where one-shot cooperation is already elevated; higher corner
  risk (gate may fail → registered "corner-confounded" outcome).

Neither rule may be exchanged for the other after D1 cell means are known
outside this pre-commitment; choosing between them is the operator's call and
is disclosed either way. Sentinel third-cell note: per the sealed sentinel
spec, checks continue on the fallback `pd-os-w1-neu-cf-ad` until the
resolution is written; the switch (and its fresh third-cell baseline, first
check after resolution) will be disclosed when it happens.

## E-dselected: operator rule choice (2026-07-24, recorded at the D2 boundary)

At the D1/D2 boundary the operator selected **Rule INTERIOR by name**, from
family-level aggregates only (interim report #3 disclosed grand means and
claim-level marginal effects; the 64-cell table, the 16 candidate cell means,
and the implied winner were not shown). Operator-imposed embargo, honored in
all interim reports: per-cell means and the implied template identity remain
undisclosed to the operator until after the step-6 resolution write.

Operator direction, quoted from the choice response: INTERIOR "matches the
selection rule specified verbatim in the Phase 4 sign-off response ('the D
cell whose round-1 cooperation is nearest 0.5, most interior')" — so the
registration gap documented above was a transcription failure of documented
pre-data intent, and the resolution note must quote and cite that sign-off
language. The operator further directed that the resolution disclosure state
the choice was made from family-level aggregates only.

Mechanical selection is pre-committed as `engine/phase4_select_e.py` at this
boundary, UNRUN against real data: it recomputes the 16 M=can primary-family
cell means from the event store, applies INTERIOR (|mean − 0.5| minimized,
ties by manifest line order in arms.json), refuses on any count/parse
anomaly, POSTs the write-once resolution, and writes
e-selection-report.{json,md}. Its --dry replay mode refuses to run until the
resolution exists, so the script cannot leak the winner ahead of the write.
It runs at step 6 (after X2 confirmation), per the frozen order. Sentinel
third cell switches to the resolved template after the write; fresh
third-cell baseline at the first post-resolution check, as pre-committed.

## Execution-schedule packaging gap #2 — X2-confirmation block (2026-07-24)

Staging step 5, the driver crashed at `act_block("X2-confirmation")` with
StopIteration: the sealed execution-schedule.json contains no block of that
name. The crash preceded any dispatch — zero X2-confirmation calls were made,
no freeze, X2 group spend still 1800/2700. Root cause: the schedule generator
materialized only unconditional blocks; X2 confirmation was registered as
conditional ("runs only if a candidate exists"), and when screening produced
a candidate the generated schedule was never revisited. The design itself is
fully sealed: arms.json carries `p4-x2-conf-lo/hi` (block X2-confirmation,
gpt-4.1, authoritative seeds 2953–2972, matched pairs), predicates.md §X2
fixes 20 episodes/side and the confirm predicate, and the engine resolves the
RESOLVED-BY-SCREENING templates via the sealed write-once X2-conf-lo/hi
resolutions (pd-x2-f1/f2, span S2, orientation fixed at selection).

Remedy — sealed bytes untouched: seal-record.md pins execution-schedule.json
sha256 `139c1b6d…` "(unchanged)", so the block is materialized into a
SEPARATE amendments file (`execution-schedule-amendments.json`) by
`engine/phase4_amend_schedule_x2conf.py`, mechanically, from arms.json alone:
arms in manifest order (lo, hi), seeds ascending as sealed, ep = 1..20 per
arm, model from the arm record, dispatch order arm-major — no constructed
randomness; every registered X2-confirmation analysis is episode-level and
dispatch-order-invariant. The generator refuses unless the sealed schedule
matches its pinned sha and the arms/seeds match the sealed design exactly.
The driver's block lookup is extended (tooling edit, disclosed): sealed
schedule first, then the amendments file, refusing if a block is in neither.
This mirrors the packet's existing additive pattern (sealed placeholders +
post-seal write-once additions), keeping every sealed artifact byte-exact
against its external anchor.

Follow-up (same boundary, before any X2-confirmation dispatch): the driver's
request builder was also step-4-scoped — it froze on any RESOLVED-BY-*
template ("outside current scope"; zero calls dispatched). Tooling edit #2,
disclosed: for RESOLVED-BY arms the driver now substitutes the concrete
template from the engine's sealed write-once resolutions (same key rule as
the engine's own resolve_template_id), and freezes if the resolution is not
yet written. Enforcement is unchanged — the engine independently re-resolves
and sha-rechecks the template on every request, so the driver substitution
cannot introduce anything the ledger has not sealed.

## D3 adjudicator amendment — pre-outcome, schema-grounded (2026-07-24)

`--d3` as pinned at commit 1424fd5 REFUSED block D3 at its fail-closed
presentation check (`actionLabels ≡ sealed displayOrder`): the game object
carries canonical template order ['X','Y','Z'], not the permuted display
order. The refusal fired before any D_ep was computed; no outcome statistic
was seen before or during the investigation and amendment below.

Investigation, decided ONLY on representation ground truth: (a) the sealed
renderRule in arms.json places the presentation permutation in the RENDERED
PROMPT (optList + beats-line from displayOrder); (b) the engine enforces the
game object against the template's canonical `spec["options"]` — dispatch
worked exactly as sealed (spot check: all 6 display orders match their
prompts byte-wise); (c) the parser (`strip-upper-exact-v1`) indexes into the
canonical label list — certified over the whole block via
`decision.parsed.displayedOption`: 197 informative trials canonical-indexed,
0 display-indexed, 0 contradicting both, 0 unreadable (288 trials total).

The pinned check encoded a wrong schema assumption, and the same assumption
made the pinned first-listed mapping (`action == 0`) measure share-of-X
instead of share-of-first-listed. Both are amended to the schema-true form;
the amendment REPLACES one equality check with four STRICTLY STRONGER ones:
(i) block-uniform canonical actionLabels, label-set-equal to displayOrder
and roleMapping domain; (ii) rendered option order ≡ sealed displayOrder at
both prompt sites, both seats, every episode; (iii) per-trial canonical-index
certification (`actionLabels[action] ≡ displayedOption`) plus run-loader
consistency; (iv) first-listed index = labels.index(displayOrder[0]), rock
index = labels.index(rock-role symbol). The D_ep ESTIMAND (first-listed share
− rock-mapped share) is unchanged; only its index realization is corrected.
Had the original mapping silently run, D_ep would have been wrong for 4 of 6
display orders — the fail-closed design did its job.

## Step-8 exploratory rider (operator-directed, recorded 2026-07-24 during D3 dispatch)

For the step-8 exploratory layer ONLY (no confirmatory status, no design
change): the D2 swap-cell role-share swing in the primary family (0.0625
aligned → 1.0 swapped, canonical M) admits at least three readings —
(i) defect-token attachment (the model tracks the defect-flavored word
wherever it sits), (ii) incongruence-inversion (label/role mismatch flips
the decision policy), (iii) residual presentation effects. Step 8 must
include a decomposition across the sealed O/P counterbalance and the D2
cell structure that distinguishes these, clearly labeled exploratory.
Recorded before block D3 completed dispatch; D2 language in all drafts
stays strictly at the estimand level until step 8.

## D1 block + D1/D2 boundary (2026-07-24)

Block D1 completed 1280/1280 episodes (640 primary, 640 cross-vendor), zero
retried calls, zero invalid trials, zero scan anomalies; every llm.requested
stamp is the preflight HEAD, dirty:false. Adjudication (--d1): primary family
(gpt-4.1) all four claims not supported at interim — the design is far from
degenerate (grand mean Y 0.2547), so this is a measured near-zero wording
effect in one-shot (P4-D1-W +0.0063, se 0.0210), not a floor/ceiling artifact.
Cross-vendor family (gemini-2.5-flash): P4-D1-W supported, negative direction
(−0.0500, Holm-p 2.49e-03), P4-D1-WL (+0.0875, Holm-p 8.18e-03) and P4-D1-ML
(Wald 13.16, 3 df, Holm-p 8.60e-03) supported; P4-D1-WM not supported.
Interpretation deferred to step 8 per the frozen order. Sentinel check 2
(post-D1/pre-D2): zero alerts; all six cell modal fingerprints within the
sealed ±2 drift tolerance of baseline (rule (c) threshold is ≥3). Block D2
staged and dispatched on the same verified-clean HEAD.
