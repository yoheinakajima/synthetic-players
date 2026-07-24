# Metric Definitions (Analysis Version 2)

Every completed experiment gets an analysis row with `analysisVersion: 2` and a
`metricsJson` payload computed by `artifacts/api-server/src/lib/metrics.ts`.
Metrics are **per game class** — a statistic is only reported where it is
meaningful, and is `null` elsewhere.

## Conventions

- Actions are integer indices into the game's `actionLabels`. By convention,
  index 0 is the "cooperative" action in social dilemmas (Cooperate, Stag, Swerve).
- All rates are fractions in [0, 1]. All payoff metrics are **per round** unless
  explicitly labeled as totals.
- `n` denotes number of rounds within one experiment; seed-level statistics
  aggregate across experiments (see Aggregation).

## Universal metrics (all classes)

| Metric | Definition |
|---|---|
| `avgPayoffPerRoundP1/P2` | Total payoff ÷ number of rounds. |
| `jointPayoffPerRound` | Sum of both players' per-round averages. |
| `eqOutcomeRate` | Fraction of rounds whose outcome cell is a **pure** Nash equilibrium. `null` for games with no pure NE (Matching Pennies, RPS) — a per-round equilibrium rate is meaningless under mixed equilibria. |
| `cellRate:i,j` | Fraction of rounds landing in outcome cell (i, j). |
| `cellShareOfEq:i,j` | Among pure-NE-outcome rounds only, the share in NE cell (i, j). Used for equilibrium-selection questions. |

## Social dilemmas (Prisoner's Dilemma, Public Goods)

| Metric | Definition |
|---|---|
| `actionCooperationRateP1/P2` | Fraction of rounds the player chose action 0. **Action-level** — counts unilateral cooperation. |
| `actionCooperationRateOverall` | Mean of the two players' action-level rates. |
| `mutualCooperationRate` | Fraction of rounds where **both** chose action 0. This is the stricter statistic; v1's `cooperationRate` was implicitly this and was mislabeled. |
| `welfareRatio` | `jointPayoffPerRound ÷ max joint payoff cell in the matrix`. 1.0 = Pareto-optimal play every round. |

## Coordination games (Stag Hunt, Battle of the Sexes, Pure Coordination)

| Metric | Definition |
|---|---|
| `coordinationRate` | Fraction of rounds where both players chose the same action index. |
| `eqOutcomeRate` + `cellShareOfEq` | Which equilibrium was selected, how often. |
| `welfareRatio`, cooperation rates | Defined as above (action 0 = the payoff-dominant/safe convention). |

Note: **Chicken** is categorized `social_dilemma` in the DB, so it receives the
dilemma metric suite (action 0 = Swerve as the "cooperative" action). Its
asymmetric pure equilibria (Swerve/Dare, Dare/Swerve) are still captured by the
universal `eqOutcomeRate` and `cellShareOfEq`, which is what the Chicken
anti-coordination claim is adjudicated on.

## Zero-sum games (Matching Pennies, Rock-Paper-Scissors)

Cooperation metrics are **null** — "cooperate" does not exist in these games.
The game value is computed as the expected payoff under uniform mixed play
(correct for symmetric MP/RPS matrices used here: value = 0).

| Metric | Definition |
|---|---|
| `marginalExploitabilityP1/P2` | Opponent's best-response expected payoff against this player's **empirical marginal** action distribution, minus game value. Measures static bias (e.g. favoring Rock). |
| `conditionalExploitabilityP1/P2` | Average payoff an **online first-order pattern tracker** would have earned against the player's actual action sequence, minus game value. The tracker predicts action *t* from Laplace-smoothed (α=1) first-order transition counts accumulated strictly over rounds < *t* (no look-ahead), best-responds each round, with a 10-round burn-in. Measures sequential predictability — this is the honest "could a tracker have beaten this player" number. |
| `tvFromUniformP1/P2` | Total-variation distance between the empirical marginal and the uniform Nash mixed strategy. |
| `lag1RepeatDeviationP1/P2` | \|P(aₜ = aₜ₋₁) − Σₐ pₐ²\| — lag-1 serial dependence beyond what the marginal alone implies. |
| `gTestPValue` | G-test (likelihood-ratio χ², df = k²−1) of joint outcome counts against the Nash-mixed prediction (uniform over cells). Small p ⇒ observed play distribution deviates from equilibrium prediction. This **replaces** the per-round "Nash rate" for mixed-equilibrium games. |

## Aggregation (across seeds)

`GET /api/analyses/aggregate?gameId=&player1StrategyId=&player2StrategyId=&batchLabel=`
returns, per metric: `n`, `mean`, sample `sd`, and a 95% t-interval
(`ciLow`, `ciHigh`; `null` when n < 2). Null metrics are excluded from a
metric's sample rather than counted as zero.

## Claim adjudication rules

A claim predicate is a conjunction of items `{metric, op, threshold, scope}`
(`op ∈ {>, >=, <, <=, between, approx}`); scopes select evidence by game,
strategy slugs (exact seats, either order, any-of, pair-from), and batch label.
Metric names ending in `Focus`/`Opponent` resolve to the seat occupied by
`focusStrategySlug`.

Per item:
- **n = 0** → `untested`.
- **Deterministic evidence** (n = 1, or sd < 1e-12 across replicates — float
  accumulation residue from identical runs counts as zero) → exact point
  comparison: `supported` or `refuted`, never inconclusive.
- **Sampled evidence** (n ≥ 2, sd > 0) → 95% t-interval vs threshold:
  `supported` iff the whole CI satisfies the comparison, `refuted` iff the whole
  CI violates it, otherwise `inconclusive`.

Effect size: one-sample Cohen's d `(mean − threshold)/sd` where sd > 0;
otherwise the raw margin `mean − threshold` is reported.

Claim verdict: `refuted` if any item is refuted; else `untested` if any item
lacks evidence; else `inconclusive` if any item is inconclusive; else
`supported`. Claims without a structured predicate are `untested` by
definition — an uncheckable claim never gets called supported.

## Fork exclusion rule

Fork-lineage experiments (`parentExperimentId` set) are **exploratory, never
evidence**. A fork's history is a hybrid — parent prefix plus post-fork suffix,
possibly with a swapped strategy — so its whole-run metrics are not a clean
sample of the labeled matchup. Enforced in four places: forks cannot receive
analysis rows, the adjudicator's evidence loader skips them, the aggregate
endpoint excludes them, and the strategy leaderboard ignores them. Forks are
studied through the engine's parent-vs-fork diff view instead.

## Fork-comparison metrics (`postFork.*`)

The one principled exception to the fork exclusion rule: a fork IS evidence
when a claim explicitly compares it against its **own parent** over the shared
**post-fork window** — rounds `forkRound+1 … N` on both branches (equal length
enforced). Same seed, same history up to the branch point, one controlled
change: a paired counterfactual, clean where whole-run fork metrics are not.

Computed from stored rounds and flattened under the `postFork.` namespace:

- `postFork.{p1Payoff,p2Payoff,welfare}PerRound{Parent,Fork,Delta}` — per-round
  payoffs over the window; `Delta` = fork − parent.
- `postFork.coopRate{Parent,Fork,Delta}`, `postFork.mutualCoopRate…` — omitted
  entirely (not 0) for zero-sum games, per the "undefined ≠ zero" rule.
- `postFork.eqRate{Parent,Fork,Delta}` — fraction of window rounds in a
  pure-equilibrium cell.
- `postFork.welfareRecoveryFrac` — fraction of the parent's per-round welfare
  gap (to the matrix max joint payoff) closed by the fork:
  `(forkWelfare − parentWelfare) / (maxWelfare − parentWelfare)`. Null when the
  parent is already within 1e-9 of max or the game is zero-sum; clamped at 1.
- `postFork.windowRounds` — window length.

Predicate scoping: a fork item sets
`scope.fork = { forkRound, player1StrategySlug?, player2StrategySlug?, batchLabel? }`.
The **outer** scope matches the **parent** (matchup slugs, batch label);
`eitherOrder` is forced off because seats matter when one seat is swapped.
An omitted fork slug means "seat unchanged". Only completed first-order forks
qualify (a fork of a fork is never evidence), and when several forks of the
same parent match a scope, the newest wins — re-running a fork batch cannot
double-count.

## LLM runs: event-sourced reproducibility

Strategies of type `ai_model` (e.g. `llm-gpt-5-mini`) decide each round via a
live model call (Replit AI Integrations; prompt version pinned in
`llmMetaJson`, finite horizon disclosed, full history in context). These runs
are **not seed-reproducible** — the provider fixes sampling for the gpt-5
family, so behavior is a sample, not a function of the stored seed.

Reproducibility instead comes from **event sourcing**:

- The live loop records every LLM decision (action + stated reasoning).
- The run is then materialized on the ActiveGraph engine with the LLM seat
  played by the special `scripted` pseudo-strategy, which replays the recorded
  decisions as ordinary engine events. Scripted seats consume zero RNG draws;
  classic seats keep their usual seed-derived stream.
- The engine result must match the live loop **exactly** (every action and
  payoff, both seats). Any divergence fails the experiment rather than
  persisting a near-match — the same drift discipline as seeded runs.
- Re-materialization (`POST /experiments/:id/engine-run`) rebuilds scripted
  seats from stored rounds, so the engine run is recoverable from the
  database alone.

Consequences for claims and experiment design:

- Single LLM runs are anecdotes. Claims about LLM behavior aggregate replicate
  batches (n ≥ 6 here) and are adjudicated on means with 95% CIs. Observed
  behavior is legitimately **bimodal** — in the Track 2 corpus some replicates
  sustain ~95% mutual cooperation with Tit-for-Tat while others defect from
  round 1 — so wide CIs and inconclusive verdicts are expected, honest
  outcomes, not failures.
- Live-loop opponents are restricted to zero-RNG deterministic strategies
  (always-cooperate, always-defect, tit-for-tat, grim-trigger,
  win-stay-lose-shift) or another LLM. RNG-consuming opponents would require
  duplicating the engine's seed-stream bookkeeping outside the engine.
- Forks may not leave an LLM seat in place: replaying recorded decisions
  against a changed history would fabricate choices the model never made for
  that context. Every LLM seat must be swapped to a classic strategy when
  forking (live mid-fork LLM decisions are Track 3 scope).
- LLM matchups are excluded from `POST /experiments/batch` (one request would
  stay open for many minutes); replicates run individually via
  `POST /experiments` + `POST /experiments/:id/run`, which also computes the
  v2 analysis.
