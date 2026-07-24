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
- **Deterministic evidence** (n = 1, or sd = 0 across replicates) → exact point
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
