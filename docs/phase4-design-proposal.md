> **SUPERSEDED (2026-07-24):** this proposal was reviewed and amended by the Phase 4 sign-off response; the binding design is `docs/phase4/freeze-packet.md` and its linked documents. Kept for history.

# Phase 4 Design Proposal — FOR SIGN-OFF (nothing here runs before approval)

**Status:** PROPOSAL. Per the Phase 4 gate: predicates, thresholds, cell counts, and total
call estimates require sign-off before any run. Predicates freeze first (registry + claims),
then runs. Phase 3 stays untouched except the labeled two-layer additions (done).

Subjects: primary `gpt-4.1` (revision-pinned in provenance) **plus at least one cross-vendor
model** — see Decision 2. All new arms use new prompt templates appended to the registry
(v3, append-only, per-arm sha pinning as in Extension X1).

---

## Experiment D — representation-robustness battery

### D1. PD presentation cross

Factors:
- **M** — payoff matrix: canonical (3,0,5,1) · affine (×3+2) · novel-A (4,1,6,2) · novel-B (7,2,9,3)
  (novels are same-class: T>R>P>S, 2R>T+S; different numerals, no memorized (3,0,5,1) shape)
- **L** — action labels: semantic ("Cooperate"/"Defect") · neutral symbols ("J"/"F")
- **O** — option order in prompt: cooperative-first · defect-first
- **P** — payoff-row presentation order: as-defined · permuted

Full cross: 4 × 2 × 2 × 2 = **32 cells**. One-shot self-play, round-1 cooperation as outcome.

**Fractional proposal (recommended):** half fraction, **16 cells**, aliasing O×P and all
3-factor interactions into the block structure. Sacrificed: O×P interaction and higher-order
terms (untestable); retained clean: all four main effects + M×L (the theoretically loaded
interaction — does label sensitivity depend on matrix familiarity?). O and P become
counterbalanced nuisance factors. If the half fraction shows |O| or |P| main effects
> 10pp, a targeted follow-up cell set resolves the aliasing before interpretation.

- Full cross @ 10 episodes/cell: 32 × 10 × 2 calls = **640 calls/model**
- Half fraction @ 20 episodes/cell: 16 × 20 × 2 = **640 calls/model** (same spend, double
  per-cell precision — this is the recommended trade)

### D2. Counterfactual games (follows the numbers or the story?)

Keep PD story and semantic labels; change payoffs:
- **CF-dominant:** cooperation strictly dominant (e.g. R=5,S=4,T=3,P=1 with T<R, P<S)
- **CF-flipped:** unique equilibrium moves to mutual cooperation (defect becomes dominated)

2 cells × 20 episodes × 2 calls = **80 calls/model**.

Draft predicate (freeze at sign-off): in each counterfactual cell, the dominant action is
chosen in ≥ 80% of round-1 decisions (run-level CP bound if a corner). Prior work predicts
failure (canonical-strategy carryover); either outcome is diagnostic.

### D3. RPS counterbalancing (is 80% rock strategic or presentational?)

Neutral symbols {X, Y, Z} mapped to the three roles with per-episode randomized mapping AND
independently randomized display order, mapping archived in run meta. 40 episodes × 2 seats
× 1 round = **80 calls/model** (+ Phase 3 canonical arm reused as the labeled control).

Decomposition (registered method): per-decision log-linear attribution of choice to
role (rock-role) vs display position (first-listed) vs token identity (X/Y/Z), clustered by
episode. Draft predicate: |P(first-listed) − ⅓| ≥ |P(rock-role) − ⅓| (surface dominates
role — the X1-informed direction). Refutation (role survives counterbalancing) would be
evidence of a genuine strategic prior.

**D total: 800 calls/model.**

## Experiment E — δ off the floor (paper-critical)

Phase 3's δ null has no assay sensitivity (floor everywhere). Test δ where cooperation is
measurable:

Arms: δ ∈ {0.10, 0.90} × presentation ∈ {Community-framed repeated PD, best-of-D
representation}. 4 cells × 20 episodes, horizons geometric (registered draw, cap 120),
self-play.

Call estimate (from Phase 3 actuals: mean 7.95 rounds/episode at δ=.90, ~1.1 at δ=.10):
≈ 20×(2×7.95) + 20×(2×1.1) ≈ 362 per presentation → **≈ 725 calls/model**.

Registered predicates (freeze at sign-off):
1. **Assay-sensitivity gate (per presentation):** round-1 cooperation in the δ=0.10 cell
   ≥ 0.05 or in the δ=0.90 cell ≥ 0.05 (off floor somewhere). If the gate fails, the
   δ-slope test for that presentation is declared floor-confounded — registered conditional
   logic, not post-hoc.
2. **δ slope:** within each presentation passing the gate, round-1 coop(δ=.90) −
   round-1 coop(δ=.10) > 0 (run-level, 95% CI; permutation if either arm has zero variance).

Interpretation is pre-committed: off-floor + δ-flat ⇒ incentive-insensitivity with assay
sensitivity (strongest form); slope ⇒ Phase 3's null was a floor artifact. Either is the
paper's central figure.

## Experiment F — adversary suite

Resolves whether the Phase 3 tracker reversal was structural or strategic. All results
reported as "performance against adversary X" — never unbranded "exploitability".

Opponents (all engine-side; no prompt changes):
1. order-2 n-gram tracker
2. order-3 n-gram tracker
3. **WSLS-targeter** — best-responds to the subject's outcome-conditioned signature
4. mid-episode policy switcher (n-gram → WSLS-targeter at round 26)
5. shuffled-history control (tracker fed a permuted copy of history — sequential info
   destroyed, marginals preserved)

Registered central prediction (freeze at sign-off): the WSLS-targeter's per-round payoff vs
the LLM exceeds the first-order tracker's (Phase 3 arm) AND exceeds 0 (absolute
exploitation), run-level 95% CI. Rationale: P(shift|lose)=0.974 is nearly deterministic. If
it holds while the LLM beats first-order trackers, the Phase 3 reversal was structural.

Budget options:
- 5 opponents × 20 episodes × 50 rounds = **5,000 calls/model** (full, matches Phase 3 C
  round count)
- 30-round episodes: **3,000 calls/model** (conditionals from Phase 3 stabilized well
  before round 30 — checkable from stored trajectories before choosing)
- Drop order-3 tracker: −1,000 (order-2 vs order-3 contrast is the least loaded)

## Budget summary (per subject model)

| Block | Calls |
|---|---|
| D (recommended fraction) | 800 |
| E | 725 |
| F (full / reduced) | 5,000 / 3,000 |
| **Total (full / reduced)** | **6,525 / 4,525** |

Two models (primary + one cross-vendor): **13,050 / 9,050 calls** — 2.2× / 1.6× the entire
Phase 3 spend (5,820). Cost scales with prompt length; F dominates (long histories).
Reduced-F for the cross-vendor model only (full-F primary) lands at **11,050**.

## Engine/pipeline work entailed (after sign-off, before runs)

- Registry v3 (append-only): D1 matrix/label/order/permutation templates, D2 counterfactual
  payoffs, D3 symbol-RPS template, E community-repeated template. Per-arm sha pinning as in X1.
- Five new engine opponent policies (F) + seat-mapping metadata for D3; deterministic,
  event-sourced, replay-verified like existing strategies.
- Provider response-ID capture into `provider_meta` (Phase 3 gap, disclosed) + per-run
  `codeCommit`/`parserVersion` stamps in run meta.
- Cross-vendor provider path (Decision 2) through the same event-sourced engine loop.

## Decisions needed (sign-off gate)

1. **D1 design:** half fraction @ 20 eps (recommended) vs full cross @ 10 eps — same spend.
2. **Cross-vendor subject:** which second model, and via which route (OpenRouter-style
   OpenAI-compatible proxy keeps the engine provider path identical).
3. **F size:** full 50-round / 30-round / drop order-3.
4. **ε** for the substitution estimand registration (see
   `substitution-estimand-preregistration.md` §4) — can be deferred, blocks only that
   registration's completeness, not Phase 4 runs.
5. **Drift sentinel cadence:** weekly scheduled run (needs a scheduled deployment) vs
   manual-only for now (script ships either way; 30 calls/week).
6. **External anchoring:** GitHub release + timestamp of the registry/prereg shas needs a
   connected GitHub repo — connect one, or defer.

After sign-off: predicates freeze (claims registered pre-data, as always) → registry v3
seals → runs → verify → adjudicate → report. Same discipline as Phase 3/X1.
