# Phase 4 Registered Predicates (freeze packet §A)

Every confirmatory claim below is frozen with: estimand, unit of analysis, contrast &
direction, threshold, interval/test method (with RNG seed), α and sidedness,
multiplicity family and correction, gating/conditional policy, degenerate-data rule,
subject configuration, sealed arm IDs, and verdict rule with all branches. Global rules
(sign-off §3, binding for all items):

- **Independent unit = episode.** One-shot self-play episodes yield Y_ep ∈ {0, .5, 1}
  (mean of the two seats' indicators); the two seats of an episode are never treated as
  independent. Repeated-game episodes yield one episode-level summary per registered
  metric. No within-trajectory round pooling in any confirmatory test.
- **Two-layer verdicts.** Layer 1: the registered predicate, mechanically adjudicated.
  Layer 2: estimand-aware companion (bounds/intervals) published with every verdict;
  layer 2 never alters layer 1.
- **No Welch-CI defaults on corner data.** Degenerate-data rule (applies everywhere):
  if a cell is constant, binary summaries use exact Clopper-Pearson; differences of
  constant cells use exact comparison plus CP bounds per cell; bootstrap methods are
  replaced by their registered exact fallback stated per claim.
- **Interval methods.** "BCa(seed)" = bias-corrected accelerated bootstrap, 10,000
  resamples over episodes, mulberry32 seed **20260801**; "CP" = two-sided 95%
  Clopper-Pearson. All tests two-sided α=.05 unless stated.
- **Holm** within each confirmatory family; cross-vendor mirrors are separate
  secondary families (replication tier), Holm within each, never pooled with primary.
- **No pooling with Phase 3.** No Phase 3 row enters any Phase 4 confirmatory test.
- **Configuration pin.** Primary subject `gpt-4.1` (expected returned revision
  `gpt-4.1-2025-04-14`; a revision change triggers the sentinel alert rule, §Provider
  packet). Cross-vendor subject `gemini-2.5-flash` (amendment A1, 2026-07-24). Temperature 0.7, maxTokens 16,
  single attempt + one registered retry; replacement policy per arms.json.
- **Arm IDs** refer to `docs/phase4/arms.json` (sealed); seeds and schedules there.

## Family D1 — representation × incentive factorial (one-shot PD, confirmatory m=4)

Design: 64 cells = M(can, aff, nva, nvb) × W(w1, w2a) × L(neu, sem) × O(cf, df) ×
P(ad, pm), 10 episodes/cell, primary model; arms `p4-d1-*-gpt`. Y_ep = episode
cooperation-ROLE share at round 1 ∈ {0,.5,1} (role derived from bindings; in D1 all
maps are aligned so displayed word = role). Analysis model (frozen): episode-level OLS
of Y on all five factor main effects plus the interactions named below, HC3 robust
covariance; planned M contrasts: c1 = can vs aff; c2 = can vs ½(nva+nvb);
c3 = nva vs nvb. O and P are diagnostics (reported, never confirmatory).

| ID | Estimand (episode-level, equal-weight cell means) | Test | Verdict rule |
|---|---|---|---|
| P4-D1-W | E[Y\|W=w2a] − E[Y\|W=w1], marginal over M,L,O,P | HC3 t, 2-sided | supported iff Holm-p < .05; direction reported with 95% CI |
| P4-D1-WM | W-effect heterogeneity across M: joint Wald on (c1,c2,c3)×W | HC3 Wald (3 df) | supported iff Holm-p < .05; per-contrast CIs published |
| P4-D1-WL | (W-effect at L=sem) − (W-effect at L=neu) | HC3 t (1 df) | supported iff Holm-p < .05 |
| P4-D1-ML | M-contrast heterogeneity across L: joint Wald on (c1,c2,c3)×L | HC3 Wald (3 df) | supported iff Holm-p < .05 |

Degenerate branch: if the full design is at a corner (all Y identical), all four report
"non-diagnostic at floor/ceiling" with per-cell CP bounds — registered as a possible
outcome, not a failure. Cross-vendor mirror: same four on `p4-d1-*-cvx`, secondary
family, Holm m=4.

## Family D2 — payoff-word decoupling (one-shot PD, semantic labels, confirmatory m=4)

Design: W(w1,w2a) × G(can, cfd) × S(aligned, swapped), 20 episodes/cell, arms
`p4-d2-*`. The engine stores the DISPLAYED word chosen (parser maps to displayed
option); strategic role derived in analysis from the arm's labelRoleMap. Notation:
word_ep = episode share of seats choosing displayed word COOPERATE; role_ep = episode
share choosing cooperation-ROLE. Conflict cell = (G=cfd, S=swapped): the strictly
dominant cooperation-role displays as the word DEFECT.

| ID | Estimand | Method | Verdict rule |
|---|---|---|---|
| P4-D2-1 | E[role_ep\|cfd,al] − E[role_ep\|can,al] (incentive effect, aligned; marginal over W) | BCa(seed) diff CI; exact fallback | supported iff 95% CI > 0 (Holm) |
| P4-D2-2 | E[role_ep\|cfd,sw] − E[role_ep\|can,sw] (incentive effect, swapped) | BCa(seed); exact fallback | supported iff 95% CI > 0 (Holm) |
| P4-D2-3 | word-following under conflict: P(B_ep=1), B_ep = 1 iff **both** seats chose word COOPERATE in (cfd,sw), marginal over W (n=40 episodes) | **CP exact** | "label-dominant" iff CP **lower bound ≥ 0.80** (point estimate alone never suffices); "payoff-dominant" iff CP upper bound ≤ 0.20; else "mixed" |
| P4-D2-4 | E[word_ep\|cfd,al] − E[word_ep\|cfd,sw] (does flipping the map flip word choice?) | BCa(seed); exact fallback | supported iff 95% CI excludes 0 (Holm; sign reported) |

Cross-vendor mirror on `p4-d2-*-cvx`, secondary, Holm m=4.

## Family D3 — positional vs role attraction (neutral-symbol RPS, single primary)

Design: exact balance, 6 roleMappings × 6 displayOrders × 2 replicates = 72 episodes
(primary model; arms `p4-d3-*-gpt`), one round, self-play. Per episode:
D_ep = (share of the 2 seats choosing the FIRST-LISTED symbol) − (share choosing the
ROCK-mapped symbol). By exact balance the two attractors are orthogonal across cells.

- **P4-D3-1**: E[D_ep] > 0 (position beats rock-role). Method: BCa(seed) over 72
  episodes; exact sign-test fallback if degenerate. **Supported iff one-sided 95%
  lower bound > 0** (α=.05 one-sided; single primary claim, no correction).
- Support-only (never confirmatory): penalized multinomial logit of symbol choice on
  {position, role} features; seeded Bayesian multinomial with Dirichlet(1) prior,
  posterior P(position weight > role weight) reported.
- Cross-vendor mirror `p4-d3-*-cvx`: secondary single claim.

## Family E — δ-sensitivity revisited (repeated PD, gate + slope)

Design: presentations {community (`pd-rep-community-w1`), D-selected (resolved by the
sealed rule from D1 primary-model data; written to the event store before any E run)}
× δ ∈ {.10, .90}, 20 episodes/cell, both models; arms `p4-e-*`. Y_ep = episode round-1
cooperation-role share.

- **Assay gate (per presentation × model, adjudicated before slopes):** the assay is
  *valid* iff at least one of its two δ cells has an episode-level 95% interval wholly
  inside (0.05, 0.95). Frozen interval method: CP on the episode-majority binary
  M_ep = 1{Y_ep ≥ .5} (n=20); disclosed sensitivity check: BCa(seed) on mean Y_ep.
- **P4-E-1 (primary, single):** GPT-4.1, D-selected presentation:
  E[Y_ep|δ=.90] − E[Y_ep|δ=.10] > 0. Method: BCa(seed) diff CI; exact fallback.
  Verdict branches (all registered): (i) gate fails → **corner-confounded: assay
  invalid for slope inference** — explicitly NOT evidence of δ-insensitivity;
  (ii) gate passes & one-sided 95% LB > 0 → **supported (positive slope)**;
  (iii) gate passes & interval includes 0 → **inconclusive** — a δ-flat *claim* would
  require an equivalence margin registered and approved separately; none is, so
  flatness is never asserted.
- Secondary family (Holm m=3): the same slope for {GPT-community, cross-D-selected,
  cross-community}, each with the same gate-first branching.

## Family X2 — wording-switch localization (repeated PD δ=.90, GPT-4.1 only)

Span decomposition (k=6 rendered spans + inert retrySuffix) is sealed in registry v3
with byte-verified endpoints. Screening (exploratory, never confirmatory): 10 rungs
(`p4-x2-f1..f5`, `p4-x2-r1..r5`), 10 episodes each, X1 seeds 1–10 with matched horizon
draws; compute episode-level round-1 cooperation per rung; adjacent gaps along each
ladder (F: v1=F0 → F5 → v2a=F6; R: mirrored). **Candidate rule (frozen):** a candidate
exists iff some adjacent |Δ| ≥ 0.50; select the largest |Δ|; ties → lowest span index;
forward ladder before reverse. Selection written to the event store before
confirmation.

- **P4-X2-1 (confirmatory; runs only if a candidate exists):** minimal pair around the
  selected span (`p4-x2-conf-lo/hi`, 20 fresh-seed episodes/side, seeds **2953–2972**
  as sealed in `arms.json` — the authoritative seed source for every claim):
  signed gap in the screened direction, Δ = E[Y_ep|hi] − E[Y_ep|lo] (orientation fixed
  at selection). Method: BCa(seed); exact fallback (CP per side + exact comparison if
  both sides constant). **Supported iff the one-sided 95% lower bound of the screened-
  direction gap > 0.50 AND sign matches screening.** If no candidate: registered
  outcome "no single dominant span at the 0.50 criterion — effect distributed";
  confirmation budget unspent.

## Family F — adversarial exploitability (RPS, 50 rounds; gate failed → 50-round design)

Stabilization gate result (sealed, `docs/phase4/f-stabilization.md`): 30-round windows
FAILED the pre-set |Δstay| ≤ 0.05 criterion (0.0512) → **50 rounds, switcher at round
26**, per the registered reversion rule. Opponents (primary, arms `p4-f-*-gpt`):
fo-tracker (contemporaneous re-run control), ngram2, ngram3, wsls-targeter,
switcher-r26, shuffled-history (causal: prefix-only, seed-recorded permutation
re-drawn every decision, shuffled prefix archived per decision). Cross-vendor drops
ngram3. **Sign convention (frozen): Ū_X = adversary X's mean per-round payoff against
the subject** (adversary win = +1); positive Ū_X = X exploits the subject. Unit =
episode (adversary per-round mean over 50 rounds → one number per episode; n=20).

- **P4-F-1 (primary, conjunction, single):** Ū_wsls-targeter − Ū_fo-tracker > 0 **and**
  Ū_wsls-targeter > 0; both one-sided 95% lower bounds > 0 (BCa(seed) each; exact
  fallback). Supported iff both hold; partial outcomes reported as registered branches
  (only-first / only-second / neither).
- Secondary family (Holm m=6): each opponent's Ū_X vs 0 (two-sided).
- Secondary directional: Ū_shuffled-history < Ū_fo-tracker (sequence order carries
  exploitable signal beyond marginals).
- Cross-vendor mirrors (m=5 profile + conjunction) — secondary replication tier.

WSLS-targeter full specification (frozen before runs): round 1 uniform-random from the
seeded adversary RNG; thereafter predict subject repeats last action after a subject
win or tie-with-stay pattern (WSLS prediction: repeat after win, shift to the
cyclically next action after loss; ties predict repeat), and play the counter to the
prediction; invalid/missing history (round 1 only) → uniform; all RNG draws from the
episode's seeded adversary stream, archived.

## Sentinel monitoring (not claims; never pooled)

30 calls per model per check: 10 × v1 δ=.90 horizon-1, 10 × v2a δ=.90 horizon-1,
10 × third cell (D-selected once written; sealed fallback `pd-os-w1-neu-cf-ad` before
that). Cadence: immediately before and after every block in the sealed schedule, plus
weekly during any block spanning >7 days. **Frozen alert rule:** alert iff (a) any
returned model identifier differs from the sealed expected string; or (b) any
finish_reason ≠ stop, invalid completion, or retry occurs; or (c) a cell's 10-episode
modal-action count differs from its sealed baseline fingerprint by ≥ 3 episodes
(baseline = the first post-approval check, sealed on write). On alert: block boundary
freeze, disclosure, and a decision memo before resuming — never silent continuation.
