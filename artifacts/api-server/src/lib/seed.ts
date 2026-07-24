import { db, gamesTable, strategiesTable } from "@workspace/db";
import { logger } from "./logger";

export async function seedIfEmpty(): Promise<void> {
  const existing = await db.select().from(gamesTable).limit(1);
  if (existing.length > 0) {
    logger.info("Seed data already present, skipping.");
    return;
  }

  logger.info("Seeding games and strategies...");

  // ── Games ─────────────────────────────────────────────────────────────────
  await db.insert(gamesTable).values([
    {
      slug: "prisoners-dilemma",
      name: "Prisoner's Dilemma",
      description:
        "Two suspects are interrogated separately. Each can cooperate (stay silent) or defect (betray). If both cooperate they get a moderate sentence; if both defect both get a harsh sentence; if one defects while the other cooperates, the defector goes free while the cooperator gets the harshest sentence.",
      numActions: 2,
      actionLabels: JSON.stringify(["Cooperate", "Defect"]),
      payoffMatrix: JSON.stringify([
        [[3, 3], [0, 5]],
        [[5, 0], [1, 1]],
      ]),
      nashEquilibria: JSON.stringify([[1, 1]]),
      nashDescription:
        "Mutual Defection (D,D) is the unique Nash equilibrium. Defecting is a dominant strategy for both players, even though mutual cooperation (C,C) would give both higher payoffs.",
      theoreticalCooperationRate: 0.0,
      category: "social_dilemma",
    },
    {
      slug: "stag-hunt",
      name: "Stag Hunt",
      description:
        "Two hunters decide independently whether to hunt a stag (requires both) or a hare (can be done alone). Mutual cooperation on the stag yields the highest reward; hunting hare alone is safe but suboptimal. Captures the tension between social cooperation and individual safety.",
      numActions: 2,
      actionLabels: JSON.stringify(["Stag", "Hare"]),
      payoffMatrix: JSON.stringify([
        [[5, 5], [0, 3]],
        [[3, 0], [3, 3]],
      ]),
      nashEquilibria: JSON.stringify([[0, 0], [1, 1]]),
      nashDescription:
        "Two pure Nash equilibria exist: (Stag, Stag) and (Hare, Hare). (Stag, Stag) Pareto-dominates but is risk-dominated. (Hare, Hare) is safer but yields lower payoffs. This captures the coordination problem between risk and reward.",
      theoreticalCooperationRate: 0.5,
      category: "coordination",
    },
    {
      slug: "chicken",
      name: "Chicken Game",
      description:
        "Two drivers race toward each other. If one swerves (cooperates) and the other continues (defects), the one who swerves loses face but survives. If both swerve, both lose equally. If neither swerves, catastrophe. Also known as Hawk-Dove. Models brinkmanship and conflict escalation.",
      numActions: 2,
      actionLabels: JSON.stringify(["Swerve", "Straight"]),
      payoffMatrix: JSON.stringify([
        [[3, 3], [1, 4]],
        [[4, 1], [0, 0]],
      ]),
      nashEquilibria: JSON.stringify([[0, 1], [1, 0]]),
      nashDescription:
        "Two pure Nash equilibria: (Swerve, Straight) and (Straight, Swerve). These are anti-coordination equilibria — players want to do the opposite of each other. There is also a mixed Nash where each player swerves with probability 3/4.",
      theoreticalCooperationRate: 0.5,
      category: "social_dilemma",
    },
    {
      slug: "battle-of-the-sexes",
      name: "Battle of the Sexes",
      description:
        "Two partners want to spend the evening together but prefer different activities (Opera vs Football). Both prefer coordination over going alone, but each prefers their own activity when coordinating. A classic coordination game with conflicting preferences.",
      numActions: 2,
      actionLabels: JSON.stringify(["Opera", "Football"]),
      payoffMatrix: JSON.stringify([
        [[3, 2], [0, 0]],
        [[0, 0], [2, 3]],
      ]),
      nashEquilibria: JSON.stringify([[0, 0], [1, 1]]),
      nashDescription:
        "Two pure Nash equilibria: (Opera, Opera) where Player 1 gets 3 and Player 2 gets 2, and (Football, Football) where Player 1 gets 2 and Player 2 gets 3. Also a mixed Nash at p=3/5 for Player 1 playing Opera and p=2/5 for Player 2 playing Opera.",
      theoreticalCooperationRate: 0.5,
      category: "coordination",
    },
    {
      slug: "matching-pennies",
      name: "Matching Pennies",
      description:
        "Each player secretly places a penny heads or tails up. If the pennies match, Player 1 wins; if they differ, Player 2 wins. A zero-sum game with no pure strategy Nash equilibrium — the only equilibrium is to randomize 50/50.",
      numActions: 2,
      actionLabels: JSON.stringify(["Heads", "Tails"]),
      payoffMatrix: JSON.stringify([
        [[1, -1], [-1, 1]],
        [[-1, 1], [1, -1]],
      ]),
      nashEquilibria: JSON.stringify([]),
      nashDescription:
        "No pure Nash equilibrium exists. The unique Nash equilibrium is mixed: each player randomizes 50/50 between Heads and Tails, yielding expected payoff of 0 for both. Any predictable strategy can be exploited.",
      theoreticalCooperationRate: 0.5,
      category: "zero_sum",
    },
    {
      slug: "coordination-game",
      name: "Pure Coordination Game",
      description:
        "Two players independently choose Left or Right. Both are rewarded only if they choose the same action. No conflicting interests — pure coordination failure can prevent reaching the optimal outcome. Models standards wars, driving conventions, and network effects.",
      numActions: 2,
      actionLabels: JSON.stringify(["Left", "Right"]),
      payoffMatrix: JSON.stringify([
        [[4, 4], [0, 0]],
        [[0, 0], [4, 4]],
      ]),
      nashEquilibria: JSON.stringify([[0, 0], [1, 1]]),
      nashDescription:
        "Two symmetric pure Nash equilibria: (Left, Left) and (Right, Right), both yielding (4, 4). A mixed Nash at 50/50 exists but yields lower expected payoffs. The challenge is coordination without communication.",
      theoreticalCooperationRate: 0.5,
      category: "coordination",
    },
    {
      slug: "rock-paper-scissors",
      name: "Rock-Paper-Scissors",
      description:
        "A symmetric three-action zero-sum game. Rock beats Scissors, Scissors beats Paper, Paper beats Rock. No pure strategy dominates. The unique Nash equilibrium is a fully mixed strategy where each action is played with probability 1/3.",
      numActions: 3,
      actionLabels: JSON.stringify(["Rock", "Paper", "Scissors"]),
      payoffMatrix: JSON.stringify([
        [[0, 0], [-1, 1], [1, -1]],
        [[1, -1], [0, 0], [-1, 1]],
        [[-1, 1], [1, -1], [0, 0]],
      ]),
      nashEquilibria: JSON.stringify([]),
      nashDescription:
        "No pure Nash equilibrium exists. The unique Nash equilibrium is mixed: each player randomizes uniformly over Rock, Paper, and Scissors (probability 1/3 each), yielding expected payoff of 0 for both players. Any pure or biased strategy can be exploited.",
      theoreticalCooperationRate: 0.33,
      category: "zero_sum",
    },
  ]);

  // ── Strategies ────────────────────────────────────────────────────────────
  await db.insert(strategiesTable).values([
    {
      slug: "always-cooperate",
      name: "Always Cooperate",
      description:
        "Always plays action 0 (the cooperative action), regardless of opponent behavior. Maximizes joint welfare but is exploitable by defectors.",
      type: "deterministic",
    },
    {
      slug: "always-defect",
      name: "Always Defect",
      description:
        "Always plays the last action (the defecting action). Dominant strategy in Prisoner's Dilemma, but performs poorly in coordination games and when facing Tit-for-Tat.",
      type: "deterministic",
    },
    {
      slug: "tit-for-tat",
      name: "Tit-for-Tat",
      description:
        "Cooperates on the first round, then mirrors the opponent's previous action. Proposed by Anatol Rapoport and famously won Axelrod's 1980 computer tournament. Encourages cooperation while punishing defection.",
      type: "deterministic",
    },
    {
      slug: "grim-trigger",
      name: "Grim Trigger",
      description:
        "Cooperates until the opponent defects once, then permanently defects for all future rounds. The harshest possible punishment — credible deterrence but unforgiving.",
      type: "deterministic",
    },
    {
      slug: "random",
      name: "Random",
      description:
        "Chooses each action with equal probability at each round. Provides a baseline for comparison. Implements the mixed Nash equilibrium for zero-sum games and approximates it for others.",
      type: "probabilistic",
    },
    {
      slug: "win-stay-lose-shift",
      name: "Win-Stay Lose-Shift (Pavlov)",
      description:
        "Repeats the previous action if it yielded above-average payoff; switches to the next action otherwise. Also known as Pavlov. More forgiving than Grim Trigger and can recover from mistakes.",
      type: "deterministic",
    },
    {
      slug: "nash-mixed",
      name: "Nash Mixed Strategy",
      description:
        "Plays actions according to the Nash mixed strategy equilibrium of the game. For zero-sum games like Matching Pennies and RPS, this is the theoretically optimal strategy. Represents what a perfectly rational game theorist would play.",
      type: "human_optimal",
    },
    {
      slug: "generous-tit-for-tat",
      name: "Generous Tit-for-Tat",
      description:
        "Like Tit-for-Tat but cooperates with 10% probability even after the opponent defects. Avoids the cooperation death-spiral that can occur with standard TFT. More forgiving and robust to noise.",
      type: "deterministic",
    },
  ]);

  logger.info("Seed complete: 7 games, 8 strategies.");
}
