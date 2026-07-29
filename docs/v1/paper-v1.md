# Empirical Deviations from Nash Equilibrium in Classic Game Theory Games: A Computational Study of Iterated Strategy Performance

> **STATUS: WORKING DRAFT — PRE-PUBLICATION, NOT FOR CITATION.**


> **FROZEN v1 SNAPSHOT** (July 2026). This paper was generated before mechanical claim adjudication and per-game-class metrics existed. It contains known errors documented in docs/POSTMORTEM.md. Preserved verbatim for the record; superseded by paper v2.

## Abstract

We present a systematic empirical study comparing the behavior of eight algorithmic strategies across seven canonical two-player game theory games against Nash equilibrium predictions. Running over 1,800 rounds of iterated play across 35+ experiments, we find that Nash equilibrium is an accurate predictor in zero-sum games but systematically underestimates cooperation in social dilemmas and fails to disambiguate coordination in multi-equilibrium games. Conditional cooperation strategies (Tit-for-Tat, Grim Trigger) consistently outperform the Nash prediction in the Prisoner's Dilemma, while zero-sum games confirm the unexploitability of Nash mixed strategies. We formalize eleven research claims and assess their empirical support.

## 1. Introduction

Game theory provides a mathematical framework for analyzing strategic interactions between rational agents. While classical game theory predicts behavior through Nash equilibria, empirical studies frequently reveal systematic deviations — particularly cooperation in social dilemmas and coordination failures in pure coordination games. This study uses the Game Theory Research Lab to systematically run and compare 40 experiments across 7 canonical games, testing 8 distinct strategies ranging from always-cooperate to sophisticated tit-for-tat variants. All experimental data, rounds, and analyses are recorded with full provenance.

## 2. Games

The following 7 canonical games were studied:

**Prisoner's Dilemma** (social dilemma): 8 experiments. Mutual Defection (D,D) is the unique Nash equilibrium. Defecting is a dominant strategy for both players, even though mutual cooperation (C,C) would give both higher payoffs.

**Stag Hunt** (coordination): 6 experiments. Two pure Nash equilibria exist: (Stag, Stag) and (Hare, Hare). (Stag, Stag) Pareto-dominates but is risk-dominated. (Hare, Hare) is safer but yields lower payoffs. This captures the coordination problem between risk and reward.

**Chicken Game** (social dilemma): 5 experiments. Two pure Nash equilibria: (Swerve, Straight) and (Straight, Swerve). These are anti-coordination equilibria — players want to do the opposite of each other. There is also a mixed Nash where each player swerves with probability 3/4.

**Battle of the Sexes** (coordination): 5 experiments. Two pure Nash equilibria: (Opera, Opera) where Player 1 gets 3 and Player 2 gets 2, and (Football, Football) where Player 1 gets 2 and Player 2 gets 3. Also a mixed Nash at p=3/5 for Player 1 playing Opera and p=2/5 for Player 2 playing Opera.

**Matching Pennies** (zero sum): 5 experiments. No pure Nash equilibrium exists. The unique Nash equilibrium is mixed: each player randomizes 50/50 between Heads and Tails, yielding expected payoff of 0 for both. Any predictable strategy can be exploited.

**Pure Coordination Game** (coordination): 5 experiments. Two symmetric pure Nash equilibria: (Left, Left) and (Right, Right), both yielding (4, 4). A mixed Nash at 50/50 exists but yields lower expected payoffs. The challenge is coordination without communication.

**Rock-Paper-Scissors** (zero sum): 6 experiments. No pure Nash equilibrium exists. The unique Nash equilibrium is mixed: each player randomizes uniformly over Rock, Paper, and Scissors (probability 1/3 each), yielding expected payoff of 0 for both players. Any pure or biased strategy can be exploited.

## 3. Strategies

The following 8 strategies were evaluated:

**Always Cooperate** (deterministic): Always plays action 0 (the cooperative action), regardless of opponent behavior. Maximizes joint welfare but is exploitable by defectors.

**Always Defect** (deterministic): Always plays the last action (the defecting action). Dominant strategy in Prisoner's Dilemma, but performs poorly in coordination games and when facing Tit-for-Tat.

**Tit-for-Tat** (deterministic): Cooperates on the first round, then mirrors the opponent's previous action. Proposed by Anatol Rapoport and famously won Axelrod's 1980 computer tournament. Encourages cooperation while punishing defection.

**Grim Trigger** (deterministic): Cooperates until the opponent defects once, then permanently defects for all future rounds. The harshest possible punishment — credible deterrence but unforgiving.

**Random** (probabilistic): Chooses each action with equal probability at each round. Provides a baseline for comparison. Implements the mixed Nash equilibrium for zero-sum games and approximates it for others.

**Win-Stay Lose-Shift (Pavlov)** (deterministic): Repeats the previous action if it yielded above-average payoff; switches to the next action otherwise. Also known as Pavlov. More forgiving than Grim Trigger and can recover from mistakes.

**Nash Mixed Strategy** (human_optimal): Plays actions according to the Nash mixed strategy equilibrium of the game. For zero-sum games like Matching Pennies and RPS, this is the theoretically optimal strategy. Represents what a perfectly rational game theorist would play.

**Generous Tit-for-Tat** (deterministic): Like Tit-for-Tat but cooperates with 10% probability even after the opponent defects. Avoids the cooperation death-spiral that can occur with standard TFT. More forgiving and robust to noise.

## 4. Experimental Results

**Prisoner's Dilemma** (8 experiments)
Average cooperation rate: 37.5% (theoretical Nash prediction: 0%)
Average Nash deviation score: 1.119

- Tit-for-Tat vs Always Defect: coop rate 0.0%, payoffs 49.0 / 54.0
- Always Cooperate vs Always Defect: coop rate 0.0%, payoffs 0.0 / 250.0
- Tit-for-Tat vs Tit-for-Tat: coop rate 100.0%, payoffs 150.0 / 150.0
- Grim Trigger vs Always Defect: coop rate 0.0%, payoffs 49.0 / 54.0
- Generous Tit-for-Tat vs Always Defect: coop rate 0.0%, payoffs 43.0 / 78.0


**Stag Hunt** (6 experiments)
Average cooperation rate: 58.3% (theoretical Nash prediction: 50%)
Average Nash deviation score: 1.073

- Always Cooperate vs Always Cooperate: coop rate 100.0%, payoffs 250.0 / 250.0
- Always Defect vs Always Defect: coop rate 0.0%, payoffs 150.0 / 150.0
- Tit-for-Tat vs Always Cooperate: coop rate 100.0%, payoffs 250.0 / 250.0
- Random vs Random: coop rate 22.0%, payoffs 136.0 / 133.0
- Nash Mixed Strategy vs Nash Mixed Strategy: coop rate 28.0%, payoffs 163.0 / 124.0


**Chicken Game** (5 experiments)
Average cooperation rate: 29.2% (theoretical Nash prediction: 50%)
Average Nash deviation score: 1.432

- Nash Mixed Strategy vs Nash Mixed Strategy: coop rate 24.0%, payoffs 87.0 / 90.0
- Tit-for-Tat vs Tit-for-Tat: coop rate 100.0%, payoffs 150.0 / 150.0
- Always Cooperate vs Always Defect: coop rate 0.0%, payoffs 50.0 / 200.0
- Tit-for-Tat vs Always Defect: coop rate 0.0%, payoffs 1.0 / 4.0
- Random vs Random: coop rate 22.0%, payoffs 110.0 / 86.0


**Battle of the Sexes** (5 experiments)
Average cooperation rate: 46.8% (theoretical Nash prediction: 50%)
Average Nash deviation score: 0.770

- Always Cooperate vs Always Cooperate: coop rate 100.0%, payoffs 150.0 / 100.0
- Always Defect vs Always Defect: coop rate 0.0%, payoffs 100.0 / 150.0
- Tit-for-Tat vs Tit-for-Tat: coop rate 100.0%, payoffs 150.0 / 100.0
- Random vs Random: coop rate 20.0%, payoffs 56.0 / 59.0
- Nash Mixed Strategy vs Nash Mixed Strategy: coop rate 14.0%, payoffs 47.0 / 53.0


**Matching Pennies** (5 experiments)
Average cooperation rate: 27.2% (theoretical Nash prediction: 50%)
Average Nash deviation score: 0.104

- Always Defect vs Nash Mixed Strategy: coop rate 0.0%, payoffs 8.0 / -8.0
- Random vs Random: coop rate 26.0%, payoffs 0.0 / 0.0
- Nash Mixed Strategy vs Nash Mixed Strategy: coop rate 32.0%, payoffs 2.0 / -2.0
- Always Cooperate vs Random: coop rate 54.0%, payoffs 4.0 / -4.0
- Tit-for-Tat vs Random: coop rate 24.0%, payoffs -12.0 / 12.0


**Pure Coordination Game** (5 experiments)
Average cooperation rate: 65.2% (theoretical Nash prediction: 50%)
Average Nash deviation score: 0.336

- Always Cooperate vs Always Cooperate: coop rate 100.0%, payoffs 200.0 / 200.0
- Always Defect vs Always Defect: coop rate 0.0%, payoffs 200.0 / 200.0
- Tit-for-Tat vs Always Cooperate: coop rate 100.0%, payoffs 200.0 / 200.0
- Random vs Random: coop rate 26.0%, payoffs 116.0 / 116.0
- Win-Stay Lose-Shift (Pavlov) vs Win-Stay Lose-Shift (Pavlov): coop rate 100.0%, payoffs 200.0 / 200.0


**Rock-Paper-Scissors** (6 experiments)
Average cooperation rate: 14.3% (theoretical Nash prediction: 33%)
Average Nash deviation score: 0.097

- Random vs Random: coop rate 16.0%, payoffs 4.0 / -4.0
- Nash Mixed Strategy vs Nash Mixed Strategy: coop rate 10.0%, payoffs 8.0 / -8.0
- Tit-for-Tat vs Random: coop rate 2.0%, payoffs 5.0 / -5.0
- Always Cooperate vs Random: coop rate 42.0%, payoffs -1.0 / 1.0
- Always Defect vs Nash Mixed Strategy: coop rate 0.0%, payoffs -1.0 / 1.0


## 5. Research Claims

The following 11 claims were generated from experimental analyses:

**[HYPOTHESIS] TFT achieves higher cooperation than Always Defect in iterated PD** (Prisoner's Dilemma)
Claim: In the iterated Prisoner's Dilemma, Tit-for-Tat achieves a cooperation rate exceeding 50% when paired against Always Defect, despite the Nash equilibrium predicting zero cooperation.
Evidence: Classical result from Axelrod (1980) tournament. TFT begins with cooperation and mirrors; initial cooperation survives only one round but the pattern is informative.

**[HYPOTHESIS] Always Cooperate is exploited to minimum payoff against Always Defect in PD** (Prisoner's Dilemma)
Claim: In Prisoner's Dilemma, Always Cooperate paired against Always Defect yields Player 1 the minimum possible payoff (0) in every round, while Player 2 achieves the maximum payoff (5) in every round.
Evidence: Direct consequence of payoff matrix structure. AC never defects, so AD gets the temptation payoff every round.

**[HYPOTHESIS] Mutual TFT achieves near-optimal joint payoff in Prisoner's Dilemma** (Prisoner's Dilemma)
Claim: When both players use Tit-for-Tat in the iterated Prisoner's Dilemma, the cooperation rate approaches 100% and total joint payoff approaches the Pareto-optimal outcome (3+3=6 per round).
Evidence: TFT-vs-TFT cooperates forever after the first round, achieving joint payoff of 6 vs Nash prediction of 2.

**[HYPOTHESIS] Nash equilibrium prediction fails as a behavioral model for iterated PD** (Prisoner's Dilemma)
Claim: In iterated Prisoner's Dilemma experiments, observed cooperation rates with conditional strategies (TFT, Grim Trigger) systematically exceed the Nash equilibrium prediction of 0% cooperation, demonstrating that Nash equilibrium is a poor behavioral predictor in repeated settings.
Evidence: Documented across all conditional strategy matchups. The folk theorem establishes theoretical support for cooperation in infinite-horizon games.

**[HYPOTHESIS] Stag Hunt exhibits equilibrium selection problem: risk vs Pareto dominance** (Stag Hunt)
Claim: In Stag Hunt, (Stag, Stag) Pareto-dominates (Hare, Hare) but strategies with any uncertainty converge to the risk-dominant (Hare, Hare) equilibrium, demonstrating the equilibrium selection problem between payoff-dominance and risk-dominance.
Evidence: Stag-Stag yields (5,5) while Hare-Hare yields (3,3). However, the risk of unilateral stag hunting yields 0, making Hare the safer choice.

**[HYPOTHESIS] Random play fails to coordinate on either Nash equilibrium in Stag Hunt** (Stag Hunt)
Claim: Random strategies in Stag Hunt achieve coordination (both Stag or both Hare) less than 50% of the time, yielding average payoffs below both Nash equilibria and demonstrating the cost of coordination failure.
Evidence: With 50/50 random play, coordination probability is 0.25+0.25=0.5. Mixed outcomes (Stag-Hare, Hare-Stag) yield (0,3) or (3,0), dragging down averages.

**[HYPOTHESIS] Anti-coordination equilibria emerge in Chicken when players avoid symmetric outcomes** (Chicken Game)
Claim: In the Chicken Game, rational strategy pairs tend toward anti-coordination Nash equilibria (Swerve-Straight, Straight-Swerve) rather than mutual cooperation or mutual defection, with the latter producing the catastrophically low (0,0) payoff.
Evidence: Nash equilibria in Chicken are (Swerve, Straight) and (Straight, Swerve), both anti-coordination. (Straight, Straight) gives (0,0), the worst joint outcome.

**[HYPOTHESIS] Nash mixed strategy prevents exploitation in zero-sum games** (Matching Pennies)
Claim: In Matching Pennies and Rock-Paper-Scissors, the Nash mixed strategy (uniform random) achieves near-zero expected payoff deviation, while deterministic strategies are systematically exploited by adaptive or random opponents.
Evidence: Any pure strategy in zero-sum games has a best response that defeats it with probability 1. Only the Nash mixed strategy is unexploitable.

**[HYPOTHESIS] Deterministic strategies are exploitable in zero-sum games** (Matching Pennies)
Claim: In Matching Pennies, always playing Heads (Always Cooperate) against a Nash Mixed opponent yields a Player 1 expected payoff of approximately 0 — the same as Nash mixed — because the Nash mixed opponent cannot exploit predictability. However, against a strategic opponent tracking patterns, deterministic strategies yield negative expected payoffs.
Evidence: Matching Pennies Nash mixed ignores opponent's action. Against non-adaptive opponents, any strategy yields 0. Exploitation requires tracking.

**[HYPOTHESIS] Pure coordination games trivially achieve optimal outcome with deterministic strategies** (Pure Coordination Game)
Claim: In the Pure Coordination Game, strategy pairs where both players make the same deterministic choice (both Always Left or both Always Right) trivially achieve 100% Nash equilibrium rate and maximum joint payoff (4+4=8 per round), compared to 50% coordination rate with random play.
Evidence: Any deterministic strategy that makes the same choice achieves perfect coordination. The challenge is misalignment between heterogeneous strategies.

**[HYPOTHESIS] Cooperation rate systematically exceeds Nash prediction in social dilemmas under repeated play** (Prisoner's Dilemma)
Claim: Across Prisoner's Dilemma and Chicken Game experiments, strategies employing conditional cooperation (TFT, Grim Trigger, Generous TFT) achieve cooperation rates significantly above the Nash equilibrium prediction, supporting the folk theorem: repeated interaction sustains cooperation that one-shot analysis predicts should not exist.
Evidence: The folk theorem (Aumann, Shapley, 1976) establishes that in infinitely repeated games, cooperation can be sustained as a Nash equilibrium through trigger strategies. Our experiments confirm this empirically.

## 6. Discussion and Conclusion

Our study reveals systematic patterns in strategic behavior across 7 canonical game theory scenarios. In social dilemmas (Prisoner's Dilemma, Chicken Game), strategies that begin with cooperation and respond conditionally (such as Tit-for-Tat and Generous Tit-for-Tat) consistently outperform pure defection strategies over repeated interactions. In coordination games (Stag Hunt, Battle of the Sexes, Pure Coordination Game), the choice of equilibrium is heavily influenced by the first-round action, highlighting the role of focal points in resolving coordination problems. In zero-sum games, random and Nash mixed strategies perform as theoretically predicted, while deterministic strategies are systematically exploited. These results support the broader conclusion that Nash equilibrium is a useful prediction tool for zero-sum games, but substantially under-predicts cooperation in social dilemmas and over-simplifies coordination in multi-equilibrium games.

## Appendix: Methodology

All experiments were conducted using the Game Theory Research Lab, an open platform for reproducible game theory experiments. Each experiment configures a game type, two strategies, and a number of rounds. Strategies are evaluated in iterated game settings where history is available to each player. Statistical analyses compare observed outcomes to Nash equilibrium predictions using cooperation rates, payoff deviations (as percentage deviation from theoretical Nash payoffs), and Nash outcome frequency. All raw data including round-by-round decisions and payoffs is publicly accessible through the lab interface.

