# Phase 3 — Layer 2: Estimand-Aware Statistical Companion

> **Machine-generated** by `scripts/phase3-layer2.mjs` v1.0.0 — do not hand-edit; rerun the script.
> Generated 2026-07-24T13:47:56.280Z at code commit `19f571e`. RNG: mulberry32, bootstrap seed 424242
> (10,000 reps), permutation seed 20260724 (100,000 reps).
>
> **Status: post-hoc, additive, labeled.** Added 2026-07-24 in response to external methods
> review. Registered verdicts in the claims registry are immutable and are not restated here;
> this layer gives each claim the statistical interpretation appropriate to its **estimand** —
> distinguishing the exact **corpus statement** ("in these runs, X happened") from the
> **policy-rate statement** ("the deployed model-policy's rate is bounded by…").

## 1. All-zero / all-one cells — exact Clopper-Pearson intervals

An observed 0-of-20 does **not** establish a zero policy rate; it bounds it. Run-level rows
treat each episode as one Bernoulli observation ("did the run exhibit any round-1
cooperation" / "was it fully cooperative"); seat-level rows are shown for completeness but
seats within a run are **not** independent (self-play), so run-level bounds are authoritative.

| Cell | Pattern | Runs | 95% one-sided bound (run) | 95% two-sided bound (run) | Seat decisions | two-sided (seat, dependence caveat) |
|---|---|---|---|---|---|---|
| prisoners-dilemma:llm41-selfplay:d10:t3 | all-zero | 20 | ≤ 13.9% | ≤ 16.8% | 40 | ≤ 8.8% |
| prisoners-dilemma-iso:llm41-selfplay:d10:t3 | all-zero | 20 | ≤ 13.9% | ≤ 16.8% | 40 | ≤ 8.8% |
| prisoners-dilemma:llm41-selfplay:d50:t3 | all-zero | 20 | ≤ 13.9% | ≤ 16.8% | 40 | ≤ 8.8% |
| prisoners-dilemma-iso:llm41-selfplay:d50:t3 | all-zero | 20 | ≤ 13.9% | ≤ 16.8% | 40 | ≤ 8.8% |
| prisoners-dilemma:llm41-selfplay:d75:t3 | all-zero | 20 | ≤ 13.9% | ≤ 16.8% | 40 | ≤ 8.8% |
| prisoners-dilemma-iso:llm41-selfplay:d75:t3 | all-zero | 20 | ≤ 13.9% | ≤ 16.8% | 40 | ≤ 8.8% |
| prisoners-dilemma:llm41-selfplay:d90:t3 | all-zero | 20 | ≤ 13.9% | ≤ 16.8% | 40 | ≤ 8.8% |
| prisoners-dilemma-iso:llm41-selfplay:d90:t3 | all-zero | 20 | ≤ 13.9% | ≤ 16.8% | 40 | ≤ 8.8% |
| prisoners-dilemma:llm41-oneshot:wallstreet:t3 | all-zero | 20 | ≤ 13.9% | ≤ 16.8% | 40 | ≤ 8.8% |
| prisoners-dilemma:llm41-oneshot:neutral:t3 | all-zero | 20 | ≤ 13.9% | ≤ 16.8% | 40 | ≤ 8.8% |
| prisoners-dilemma:llm41-para-v2a:d90:t3x | all-one | 20 | ≥ 86.1% | ≥ 83.2% | 40 | ≥ 91.2% |
| prisoners-dilemma:llm41-para-v2b:d90:t3x | all-one | 20 | ≥ 86.1% | ≥ 83.2% | 40 | ≥ 91.2% |
| pooled canonical high-δ (A3 cell) | all-zero | 40 | ≤ 7.2% | ≤ 8.8% | 80 | ≤ 4.5% |

**Reading:** "zero round-1 cooperation in 20 episodes" is consistent with a true policy rate
as high as ~16.8% (two-sided) per cell; pooling the canonical high-δ cells
(A3, 40 runs) tightens the bound to ~8.8%. The corpus statements remain
exact; the policy statements carry these intervals.

## 2. Unit-of-analysis accounting (every registered claim item)

| Claim item | Raw decisions | Run-seats | Independent runs | Cluster level in registered test | Registered CI method | Layer-2 supplement |
|---|---|---|---|---|---|---|
| A1 δ=.90 vs δ=.10 | 80 | 80 | 40 | run-seat | exact point (sd=0 both arms) | run-level Clopper-Pearson per cell |
| A2 pooled high vs low δ | 160 | 160 | 80 | run-seat | exact point (sd=0) | run-level CP per pooled cell |
| A3 human-range membership | 80 | 80 | 40 | run-seat | point vs interval | run-level CP (0/40 runs) |
| A4(a)+(b) isomorph | 160 | 160 | 80 | run-seat | exact point (sd=0) | run-level CP; (b) flagged non-diagnostic at floor |
| B1 community − wallstreet | 80 | 80 | 40 | run (Welch on run-seat means) | Welch 95% (df 19) | run-level permutation + bootstrap CI |
| B2 ratio edge rule | 80 | 80 | 40 | run | pre-registered point edge rule | unchanged (rule fired as registered) |
| B3 neutral interior | 120 | 120 | 60 | run | point ordering, ties allowed | wallstreet/neutral CP bounds shown |
| C1 rock share | 120 | 120 | 60 | seat decision (round 1) | point vs [0.33,0.40] band | run-level cluster bootstrap CI |
| C2 P(stay|win), P(shift|lose) | 1470 | 120 | 60 | run-seat summary, null denominators excluded | 95% normal CI across run-seat values | pooled decisions + run-level cluster bootstrap |
| C3 tracker per-round diff | 40 | 80 | 40 | run | Welch 95% (df 37.4) | run-level permutation (two-sided) |
| X1 v2a/v2b round-1 coop | 80 | 80 | 40 | run-seat | exact point (sd=0) | run-level CP (all-one cells) |

## 3. C2 resolved — what n=61 was, and cluster-robust recomputation

The registered test aggregated **per-run-seat conditional summaries** (never pooled raw
decisions): each LLM seat trajectory yields one P(stay|win) and one P(shift|lose), with the
seat excluded from a conditional when its denominator is zero (locked pre-study). From raw
rounds: **80 LLM run-seats** → 61 non-null for stay|win and
61 non-null for shift|lose. Null-denominator composition by arm
(seats with no wins / no losses — dominated by mirror-tie self-play trajectories):

| Arm | LLM seats | null stay\|win | null shift\|lose |
|---|---|---|---|
| llm41-vs-pattern-tracker | 20 | 0 | 0 |
| llm41-vs-nash-mixed | 20 | 0 | 0 |
| llm41-selfplay | 40 | 19 | 19 |

This resolves the registered n: **61 = 80 LLM seats − 19 all-tie
self-play mirror trajectories** (a seat that ties every round has zero wins *and* zero
losses, so it is excluded from both conditionals). The registered unit was the run-seat
summary, **not** nested raw decisions.

Decision-level exposure: **778 win-transitions** (682 stays) and
**692 lose-transitions** (665 shifts) — these are the raw decisions
nested inside the 80 seat summaries.

| Quantity | Registered-style (seat-summary mean) | Pooled decisions | Run-level cluster bootstrap 95% CI | Null |
|---|---|---|---|---|
| P(stay\|win) | 0.6834 | 0.8766 | [0.8331, 0.9132] | > 1/3 |
| P(shift\|lose) | 0.9744 | 0.9610 | [0.9360, 0.9819] | > 2/3 |

**Result:** both cluster-robust CIs lie entirely on the same side of their nulls as the
registered test — the C2 verdict is insensitive to the clustering correction.

**Estimand note (disclosed, not a correction):** the seat-summary mean and the pooled
estimate answer different questions and differ materially for stay|win
(0.6834 vs 0.8766): the former weights every seat equally, the
latter weights by transition exposure, and seats with many win-transitions (e.g. seats
that repeatedly beat the deterministic tracker) have higher stay rates. The registered
predicate used the seat-summary aggregation; both estimands exceed the null, so nothing
turns on the choice here — but Phase 4 predicates will name the aggregation explicitly.

## 4. B1 — permutation and bootstrap supplements (zero-variance arm)

Welch's t assumes both arms contribute a variance estimate; the Wall Street arm cannot
(all zeros). Run-level supplements (unit = one episode's mean round-1 cooperation):

- Observed difference (community − wallstreet): **0.1750**
- Run-level permutation test (one-sided, 100,000 seeded reps): **p = 4.18e-3**
- Community mean, run-level bootstrap 95% CI: **[0.0750, 0.2750]**

The registered SUPPORTED verdict survives the variance-assumption-free test.

## 5. C1 — rock share with cluster-aware uncertainty

80 round-1 seat decisions across 60 runs (self-play contributes two
dependent seats). Rock share **0.8000**; run-level cluster bootstrap 95% CI
**[0.7349, 0.8701]** — still entirely above the human band upper edge
(0.40), so the registered refutation of the band membership is clustering-robust.

## 6. C3 — permutation supplement

Tracker per-round payoff, 20 runs vs LLM against 20 baseline runs
(vs nash-mixed). Observed difference **-0.0800** per round; two-sided run-level
permutation **p = 5.03e-3**. The registered refutation (sign reversal) is
not a Welch artifact.

## 7. Language and framing corrections adopted (mirror of report edits)

- "exploitability" → **"performance against the registered first-order tracker"** (no
  unbranded exploitability claims).
- "20 seeded replicates" → **"20 environment-seeded episodes with archived model draws"**
  (environment RNG is seeded; provider-side sampling is not, and is archived, not seeded).
- A4(b) → **non-diagnostic at the behavioral floor** (cannot separate scale-invariance from
  incentive blindness at 0−0).
- "no shadow of the future — at all" → **"no round-1 cooperation observed under any tested
  δ in this configuration"** (corpus-exact, policy-bounded).
