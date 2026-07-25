# Sentinel alert — check 5, decision memo (frozen rule: freeze → disclose → memo → operator decision before resuming)

**Status: FROZEN at the X2-confirmation → E boundary.** No E-resolution write, no
block E dispatch, no further subject calls until the operator records a decision
in §Decision below. Written 2026-07-24, before any resumption.

## The alert (frozen rule c)

Check 5 (after X2-confirmation / before E, pre-resolution): cell
`p4-sent-v2a × gemini-2.5-flash` modal-action (cooperate, index 0) count **7/10**
vs sealed baseline **10/10** — Δ = 3 ≥ 3. All other cells at baseline
(gpt-4.1: 10/10 in all three cells; gemini v1 and fallback: 10/10). No rule (a)
alerts (returned model identifier unchanged) and no rule (b) alerts (all
finish_reason=stop, zero retries, zero invalid trials) — in check 5 or any
earlier check.

## Trajectory (retrospective; each prior check individually passed the frozen Δ≥3 rule)

| check | boundary | v2a×gemini seat-1 cooperate |
|---|---|---|
| 0 | baseline (sealed) | 10/10 |
| 1 | post-X2-screening | 9/10 |
| 2 | post-D1 | 9/10 |
| 3 | post-D2 | 8/10 |
| 4 | post-D3 | 8/10 |
| 5 | post-X2-confirmation | **7/10 → ALERT** |

Monotone erosion, ~1 episode per two checks — a gradual behavioral drift, not a
step change. The three check-5 deviants (seeds 9052, 9054, 9060) are clean,
valid, single-token defect choices (raw text `F`, parsed valid, displayedOption
consistent, seat 2 cooperative in all three) — not parse artifacts, not decoding
anomalies. Because the Gemini endpoint is **unversioned**, rule (a) cannot see a
silent provider-side update; the behavioral fingerprint is the only detector,
and it behaved exactly as designed.

## Contamination analysis

- **Completed blocks stand.** Checks 0–4 all passed the frozen rule; the D
  battery (D1/D2/D3 + cvx mirrors), X2 screening, and X2 confirmation closed
  under clean gates. Within-block contrasts are internally randomized and
  single-epoch; their interim verdicts are unaffected.
- **Cross-check comparability for cvx is now qualified.** The cvx subject was
  not one fixed provider state across the phase; final reporting (step 8) must
  carry this trajectory descriptively wherever cvx results are compared across
  blocks or to Phase 3. gpt-4.1 shows zero drift on any cell.
- **Pending blocks are exposed.** E contains 80 gemini episodes (of 160), F
  contains 100 (of 220). Dispatching cvx arms now samples a subject that is
  measurably not the D-battery-era subject. Within-block internal validity of
  E/F cvx contrasts is preserved by design (randomization within a single
  epoch); cross-block cvx narratives require the caveat regardless.
- **The E-resolution (Rule INTERIOR) is unaffected**: it reads only D1 gpt-4.1
  M=can cell means, and gpt-4.1 is drift-free on every sentinel cell.

## Options

1. **Resume in full, re-baselined (recommended).** Write the E-resolution and
   dispatch E per the sealed schedule, both models. Before the first post-freeze
   check, register a re-baseline record fixing the check-5 fingerprint
   (7/10) as the new reference for `p4-sent-v2a × gemini-2.5-flash` (frozen Δ≥3
   rule then applies against the new reference for E/F monitoring; the original
   trajectory continues to be reported descriptively at every subsequent check).
   Register a standing caveat: all cross-block cvx comparisons in interim and
   final reports disclose the drift trajectory. Rationale: within-block validity
   is the confirmatory unit everywhere in the registration; halting cvx would
   discard the sealed secondary-subject mirrors to protect a comparability the
   registration never claims.
2. **Resume gpt-only.** Dispatch only the gpt-4.1 episodes of E/F; the sealed
   cvx episodes are abandoned (a substantially larger deviation from the sealed
   schedule than option 1's caveat, and it forfeits the E/F secondary mirrors).
3. **Extend the freeze.** Spend additional sentinel budget re-checking the cell
   before deciding. The drift is monotone across five checks; further checks
   characterize the slope but cannot restore the earlier provider state, and E/F
   grow no more comparable by waiting.

## Decision

**Recorded 2026-07-24 (operator sign-off, verbatim):**

> Option 1, with four riders. (1) Take a fresh fingerprint of the drifted cell
> immediately before E dispatch and re-baseline on that reading rather than the
> check-5 snapshot; the extra sentinel spend is approved. (2) Double sentinel
> cadence on all gemini cells through E and F, with rule (c) armed against the
> new baseline; a second fire means the same freeze. (3) At step 8, report
> gemini results regime-indexed (pre-drift vs post-rebaseline) instead of under
> one blanket caveat; within-regime contrasts stand on their own, cross-regime
> comparisons carry the qualification. (4) Write the sentinel catch up as a
> first-class result: monotone erosion of an unversioned endpoint across six
> checks, invisible to version pinning, caught by the behavioral fingerprint
> with the study frozen before any contaminated spend. This is the mechanism
> the protocol exists to demonstrate. Also noting for the record: the
> schedule-block and driver gaps are the third and fourth instances of sealed
> text promising what the implementation lacked; the freeze-time completeness
> linter stays on the list.

**Adopted implementation (registered before any post-freeze dispatch):**

- Rider 1 → the pre-E full check (sentinel:6, the standing boundary check) is
  the baseline-setting read: `p4-sent-v2a × gemini-2.5-flash` re-baselines on
  its check-6 fingerprint, not the check-5 snapshot. The third cell
  (`p4-sent-fallback`, both models) also takes its fresh baseline at check 6 —
  its template switches to the D-selected representation at the E-resolution
  write, as pre-committed in the sealed sentinel spec. Baseline-setting reads
  take no rule-(c) comparison (rules (a)/(b) apply unchanged); all other cells
  compare to the sealed check-0 baseline as always. The re-baseline record is
  write-once: `docs/phase4/sentinel-rebaseline.json`, written by `--sentinel 6`
  only on a zero-alert check.
- Rider 2 → doubled gemini cadence = gemini-only mid-block checks (3 cells ×
  10 episodes) at the midpoint of E and of F. Full checks: 6 (pre-E),
  8 (post-E/pre-F), 10 (post-F). Gemini-only checks: 7 (mid-E), 9 (mid-F).
  Gemini cells are observed at 6,7,8,9,10 vs gpt-4.1 at 6,8,10. Rule (c) arms
  against the check-6 re-baseline from check 7 onward; a fire anywhere means
  the same boundary freeze. The driver holds after every check until it is
  adjudicated; no block dispatch proceeds past an unadjudicated check.
- Rider 3 → regime indexing pre-committed BEFORE any E/F outcome exists:
  regime R1 = all gemini data through the check-5 era (D battery, X2);
  regime R2 = post-re-baseline (E, F). Step-8 reporting presents gemini
  results per regime; within-regime contrasts stand alone; cross-regime
  comparisons carry the qualification. The drifted cell's original-baseline
  trajectory continues to be reported descriptively at every check.
- Rider 4 → `docs/phase4/sentinel-drift-result.md`, registered at resumption
  as a first-class descriptive result.
- Record note: the operator's instance count is transcribed verbatim above. A
  **fifth instance** surfaced while implementing this decision: the sealed
  sentinel spec's third-cell switch ("D-selected once written; sealed fallback
  before") existed in neither the engine's enforcement nor the driver's
  dispatch — either side would have refused or mis-dispatched check 6. Fixed
  on both sides (engine remains the enforcement point), ledgered in
  provenance-notes.md. The freeze-time completeness linter stays on the
  backlog.

The freeze lifts at the first post-decision dispatch (sentinel:6), and only
after this memo section, the tooling changes, and the E-resolution write are
committed and disclosed.

## Recovery (check 6, fresh pre-E read — recorded 2026-07-25)

Check 6 read the drifted cell (v2a × gemini-2.5-flash) at **10/10** on the
fresh fingerprint — full reversion from check 5's 7/10. The recovery framing
is part of the finding, not an all-clear:

- The endpoint is **non-stationary with reversion**. That upgrades the drift
  catch: a one-time validation check would either have missed the drift
  entirely (sampled at check 6) or overreacted to it (sampled at check 5,
  concluding durable degradation). Continuous fingerprinting is the only
  design that observes both the erosion and the recovery.
- **One clean check is not evidence of stability.** The operative claim is
  "non-stationary with reversion," and it is carried by the densified cadence
  (checks 7–10, rider 2) adjudicated against the re-baseline
  (sentinel-rebaseline.json) under rule (c) — not by check 6 alone.
- Per rider 4, the final report presents the full trajectory (10 → 7 → 10,
  per-check fingerprints) as a first-class result, regime-indexed per rider 3
  (R1 pre-drift baseline, R2 post-re-baseline).

## Second reversion (check 7, mid-E — recorded 2026-07-25)

Check 7 (gemini-only, densified cadence) read v2a × gemini-2.5-flash at
**6/10** against the check-6 re-baseline of 10/10 — Δ=4, a rule (c) fire on
the first armed use of the re-baseline. Companion cells were in band (v1:
10/10 modal 1; fallback: 9/10 modal 0). Adjudicator exit 2; the driver was
already at the registered hold and nothing has been dispatched past the
fired check, per rider 2 ("a fire anywhere means the same boundary freeze").

- The cell's trajectory now reads **10 → 7 → 10 → 6** (original-baseline
  descriptive series; per-check fingerprints in the store). This is
  oscillation, not a one-time step: §Recovery's reading ("one clean check is
  not evidence of stability") is borne out at the first armed check after it
  was written.
- Consequence for rider 3: R2 ("post-re-baseline") is **not internally
  stationary** for this cell. For the oscillating cell, regime indexing must
  be **per dispatch window**, not merely per era: window W(k,k+1) = episodes
  whose store rows fall between the last run.completed of check k and the
  first llm.requested of check k+1. By construction all E:h1 episodes lie in
  W(6,7) — dispatched after a clean check, closed by a fired one; exact
  counts are derivable from the sealed schedule and store timestamps.
  Non-oscillating cells keep the two-regime presentation, with the window
  table as disclosure.
- No gate, threshold, exclusion, or analysis surface is touched by this
  entry. E adjudication mechanics are unchanged; gpt-side cells are outside
  the alert's scope.
- **Decision pending.** Per the alert-5 precedent the boundary freeze lifts
  only on an operator decision recorded here. Options put to the operator:
  (a) dispatch E:h2 per cadence — check 8 (full) closes W(7,8) immediately
  after h2 and cvx results carry per-window indexing; (b) registered
  amendment deferring or shedding E cvx arms; (c) extended hold.
  Recommendation on record: (a) — riders 2/3 built exactly this instrument,
  and pausing cvx arms would modify a sealed schedule to avoid data the
  indexing already handles honestly.

### Decision (operator, recorded 2026-07-25)

Option (a): dispatch E:h2 per cadence. Operator reasoning, transcribed:
10 → 7 → 10 → 6 is oscillation, so there is no clean regime to wait for;
deferring the cvx arms would delete the demonstration rather than protect
it; per-window indexing under riders 2/3 is the honest instrument for a
moving target; gpt-4.1 shows zero drift, so the primary is untouched.

Two riders attach to the decision, continuing the memo's numbering:

- **Rider 5 (adjudication ordering — pre-committed before any h2 gemini
  adjudication):** sealed gemini E predicates adjudicate exactly as written
  on their defined samples; window indexing layers on as interpretation
  only. No pooling choice is made after window contrasts become visible —
  the sealed sample is the unit of adjudication, and per-window splits are
  disclosure, never decision surfaces.
- **Rider 6 (stability reading):** the stability section states the
  upgraded reading — an unversioned endpoint is an uncontrolled mixture
  rather than a single stable subject; continuous fingerprinting is what
  makes that visible; the full oscillation trajectory is the figure.
  Recorded in sentinel-drift-result.md.

SHED-2 (`p4-f-shuffled-history-cvx`) approved as proposed in the same
decision; the gpt twin keeps the control (shedding-order.md).

The freeze lifts at the first post-decision dispatch (the E:h2 preflight),
per the alert-5 pattern: only after this entry, the drift-result addendum,
and the shedding-order approval are committed and disclosed.
