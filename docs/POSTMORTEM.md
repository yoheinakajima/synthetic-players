# Postmortem: What v1 Got Wrong

Version 1 of this lab ran 40 experiments, wrote 11 claims, and generated a
2,149-word paper. Several of its outputs were wrong or unfounded. This document
is the honest record. The frozen v1 artifacts are in `docs/v1/` — unmodified.

## E1. A literature result was transplanted into a claim the data refutes

**The error.** Claim #1 stated *"TFT achieves higher cooperation than Always
Defect in iterated PD … cooperation rate exceeding 50% when paired against
Always Defect."* The experiment that claim cites shows TFT cooperating in
exactly **1 of 50 rounds (2%)**: TFT cooperates in round 1, gets defected on,
and mirrors defection forever. The >50% number is an Axelrod-style **tournament
aggregate** (TFT across a population containing cooperators) — not a property
of the TFT-vs-AD dyad that was actually run.

**Root cause.** The claim was written by recalling what the literature says
about TFT rather than by reading the rounds table. Nothing in the v1 pipeline
forced the claim text to be compared against the linked data.

**The fix.** Claims now carry structured predicates and are adjudicated
mechanically. Claim #1's faithful encoding (`actionCooperationRateFocus > 0.5`,
TFT seat, vs Always Defect, PD) is now **REFUTED** (observed 0.02, margin
−0.48). The refutation stands on the record; the claim was not reworded to
dodge it.

## E2. Payoff totals were presented where per-round averages were required

**The error.** Surfaces (UI, paper) showed cumulative totals like "1.0 / 4.0"
(Chicken, TFT vs AD, 50 rounds) in contexts inviting per-round or cross-game
comparison. Investigation confirmed the stored numbers were **correct totals**
— TFT vs AD in Chicken really does produce total payoffs 1.0/4.0 over 50 rounds
((1,4) in round 1, then (0,0) × 49 — mutual "Dare" lock-in) — but nothing
labeled them as totals, and nothing offered the per-round view where such
outcomes look sane.

**The fix.** `player1AvgPayoffPerRound`/`player2AvgPayoffPerRound` are computed
API-side on every experiment; the UI leads with per-round values and labels
totals as totals; the paper reports per-round payoffs exclusively.

## E3. Metrics were applied to game classes where they are undefined

**The errors.**
- "Cooperation rate" was reported for zero-sum games (Matching Pennies, RPS),
  where cooperation does not exist. It measured "how often players picked
  action 0", which is noise.
- A per-round "Nash equilibrium rate" was reported for games whose only
  equilibria are mixed. Under a mixed equilibrium no single round can "be" the
  equilibrium — the statistic reads 0% for optimal play and was reported as if
  it were a behavioral deviation.
- `cooperationRate` on experiments was implicitly **mutual**-cooperation-only
  (EXP-1 stored 0.0 despite one cooperative action by TFT) with nothing
  documenting that definition.

**The fix.** Analysis v2 computes a per-class metric suite (see
`docs/METRICS.md`): welfare ratio and explicit action-level vs mutual
cooperation rates for dilemmas; equilibrium-outcome and coordination rates for
coordination games; exploitability (marginal + pattern-tracker) and
distribution tests (G-test vs Nash mixed) for zero-sum games. Cooperation
metrics are `null` for zero-sum games and the UI displays exploitability panels
there instead.

## E4. Single unseeded runs of stochastic processes were treated as facts

**The error.** Every v1 experiment ran once with `Math.random()` — no seeds, no
replication. Claims about Random/Nash-Mixed behavior (e.g. "Random play fails
to coordinate", observed 42% one time) rested on a single draw whose 95%
interval spans the threshold either way.

**The fix.** The engine now uses a seeded mulberry32 PRNG; the seed is stored
on every experiment and identical seeds reproduce identical runs bit-for-bit
(verified). Every matchup involving a probabilistic strategy was re-run as a
20-seed batch (400 new experiments). Aggregates carry 95% t-intervals, and
adjudication happens against those intervals.

**The honest consequence.** Three v1 claims that sounded crisp are now
**INCONCLUSIVE**, because 20 seeds show their statistics straddling their
thresholds — e.g. Stag Hunt random-play equilibrium rate is 49.4% (CI
[45.3%, 53.6%]) against a "< 50%" claim. That is the correct verdict: the
original claims were sharper than the data permits. They stay inconclusive
rather than being re-thresholded after the fact (that would be HARKing).

## Verdict summary after v2 re-adjudication

| # | Claim (short) | v1 status | v2 verdict |
|---|---|---|---|
| 1 | TFT >50% cooperation vs AD | supported | **refuted** (0.02 observed) |
| 2 | AC exploited to minimum by AD | supported | supported (exact) |
| 3 | TFT–TFT near-optimal welfare | supported | supported (exact) |
| 4 | Nash fails as behavioral model in IPD | supported | **inconclusive** (CI [0.03, 0.24] vs >0.05) |
| 5 | Stag Hunt equilibrium selection (risk-dom.) | supported | **inconclusive** (share 50.9%, CI straddles 50%) |
| 6 | Random fails to coordinate in Stag Hunt | supported | **inconclusive** (49.4%, CI straddles 50%) |
| 7 | Chicken anti-coordination >50% | supported | **inconclusive** (49.3%, CI straddles 50%) |
| 8 | Nash mixed prevents exploitation | supported | supported (tracker exploit. ≈ 0.007) |
| 9 | Deterministic strategies exploitable | supported | supported (tracker exploit. = 1.0) |
| 10 | Pure coordination trivial for deterministic | supported | supported |
| 11 | Cooperation exceeds Nash prediction in IPD | supported | supported (conditional pairs, 100%) |

v1 called 11/11 of its adjudicated claims supported. Mechanical adjudication
sustains 6, refutes 1, and finds 4 not decidable at n=20 seeds. That delta is
the measure of v1's optimism bias.

## Process changes carried forward

1. **Claims are predicates.** No claim without a machine-checkable predicate;
   predicateless claims display as `untested`.
2. **The author doesn't adjudicate.** Verdicts come from the adjudicator
   endpoint, which never reads the claim's prose — only its predicate.
3. **Stochastic ⇒ replicated.** Any matchup with a probabilistic strategy gets
   seeded replicates and CI-based reporting.
4. **Per-class metrics only.** No metric is reported for a game class where it
   is undefined.
5. **Errors stay on the record.** Refuted claims remain visible with their
   adjudication data; v1 artifacts are frozen in `docs/v1/`, and the v2 paper
   carries a mandatory errata section.
