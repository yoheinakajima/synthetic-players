/**
 * Canonical structured predicates for the v1 (pre-adjudication) claims,
 * keyed by exact claim title. Applied idempotently at startup: a claim gets
 * its predicate filled only when predicateJson is null.
 *
 * These encode the claims AS ORIGINALLY STATED — including the ones the data
 * refutes. The adjudicator's job is to catch that; ours is not to quietly
 * rewrite history. See docs/POSTMORTEM.md.
 */

import { eq, isNull, and } from "drizzle-orm";
import { db, claimsTable } from "@workspace/db";
import { logger } from "./logger";
import type { ClaimPredicate } from "./adjudicator";

export const V1_CLAIM_PREDICATES: Record<string, ClaimPredicate> = {
  // Original statement: "cooperation rate exceeding 50% when paired against Always Defect".
  // Encoded faithfully. The data shows TFT cooperates once (round 1) then mirrors
  // defection forever — this predicate is expected to be REFUTED.
  "TFT achieves higher cooperation than Always Defect in iterated PD": {
    scope: {
      gameId: 1,
      player1StrategySlug: "tit-for-tat",
      player2StrategySlug: "always-defect",
      eitherOrder: true,
      focusStrategySlug: "tit-for-tat",
    },
    all: [
      {
        label: "TFT action-level cooperation rate > 50% vs Always Defect",
        metric: "actionCooperationRateFocus",
        op: ">",
        threshold: 0.5,
      },
    ],
  },

  "Always Cooperate is exploited to minimum payoff against Always Defect in PD": {
    scope: {
      gameId: 1,
      player1StrategySlug: "always-cooperate",
      player2StrategySlug: "always-defect",
      eitherOrder: true,
      focusStrategySlug: "always-cooperate",
    },
    all: [
      {
        label: "AC per-round payoff ≈ 0 (sucker's payoff every round)",
        metric: "avgPayoffPerRoundFocus",
        op: "approx",
        threshold: 0,
        tolerance: 0.001,
      },
      {
        label: "AD per-round payoff ≈ 5 (temptation payoff every round)",
        metric: "avgPayoffPerRoundOpponent",
        op: "approx",
        threshold: 5,
        tolerance: 0.001,
      },
    ],
  },

  "Mutual TFT achieves near-optimal joint payoff in Prisoner's Dilemma": {
    scope: {
      gameId: 1,
      player1StrategySlug: "tit-for-tat",
      player2StrategySlug: "tit-for-tat",
    },
    all: [
      {
        label: "Joint welfare ratio ≥ 0.99 of Pareto optimum",
        metric: "welfareRatio",
        op: ">=",
        threshold: 0.99,
      },
      {
        label: "Mutual cooperation rate ≥ 98%",
        metric: "mutualCooperationRate",
        op: ">=",
        threshold: 0.98,
      },
    ],
  },

  "Nash equilibrium prediction fails as a behavioral model for iterated PD": {
    scope: {
      gameId: 1,
      anyStrategySlugs: ["tit-for-tat", "grim-trigger", "generous-tit-for-tat", "win-stay-lose-shift"],
    },
    all: [
      {
        label: "Mean cooperation across conditional-strategy PD experiments > 5% (Nash predicts 0%)",
        metric: "actionCooperationRateOverall",
        op: ">",
        threshold: 0.05,
      },
    ],
  },

  "Stag Hunt exhibits equilibrium selection problem: risk vs Pareto dominance": {
    scope: {
      gameId: 2,
      pairFromSlugs: ["random", "nash-mixed"],
    },
    all: [
      {
        label: "Among equilibrium outcomes under uncertainty, risk-dominant (Hare,Hare) share > 50%",
        metric: "cellShareOfEq:1,1",
        op: ">",
        threshold: 0.5,
      },
    ],
  },

  "Random play fails to coordinate on either Nash equilibrium in Stag Hunt": {
    scope: {
      gameId: 2,
      player1StrategySlug: "random",
      player2StrategySlug: "random",
    },
    all: [
      {
        label: "Equilibrium-outcome rate < 50% under random play",
        metric: "eqOutcomeRate",
        op: "<",
        threshold: 0.5,
      },
    ],
  },

  "Anti-coordination equilibria emerge in Chicken when players avoid symmetric outcomes": {
    scope: {
      gameId: 3,
    },
    all: [
      {
        label: "Mean equilibrium-outcome rate across all Chicken experiments > 50%",
        metric: "eqOutcomeRate",
        op: ">",
        threshold: 0.5,
      },
    ],
  },

  "Nash mixed strategy prevents exploitation in zero-sum games": {
    scope: {
      gameId: 5,
      anyStrategySlugs: ["nash-mixed"],
      focusStrategySlug: "nash-mixed",
    },
    all: [
      {
        label: "Conditional (pattern-tracker) exploitability of Nash Mixed < 0.15",
        metric: "conditionalExploitabilityFocus",
        op: "<",
        threshold: 0.15,
      },
      {
        label: "Marginal exploitability of Nash Mixed < 0.15",
        metric: "marginalExploitabilityFocus",
        op: "<",
        threshold: 0.15,
      },
    ],
  },

  "Deterministic strategies are exploitable in zero-sum games": {
    scope: {
      gameId: 5,
      anyStrategySlugs: ["always-cooperate", "always-defect", "tit-for-tat"],
    },
    all: [
      {
        label: "Pattern-tracker exploitability of deterministic play > 0.5 per round",
        metric: "conditionalExploitabilityFocus",
        op: ">",
        threshold: 0.5,
        scope: { focusStrategySlug: "always-cooperate" },
      },
      {
        label: "Same for Always Defect seat",
        metric: "conditionalExploitabilityFocus",
        op: ">",
        threshold: 0.5,
        scope: { focusStrategySlug: "always-defect" },
      },
    ],
  },

  "Pure coordination games trivially achieve optimal outcome with deterministic strategies": {
    scope: {
      gameId: 6,
    },
    all: [
      {
        label: "AC–AC achieves 100% equilibrium outcomes",
        metric: "eqOutcomeRate",
        op: ">=",
        threshold: 1.0,
        scope: { pairFromSlugs: ["always-cooperate"] },
      },
      {
        label: "AD–AD achieves 100% equilibrium outcomes",
        metric: "eqOutcomeRate",
        op: ">=",
        threshold: 1.0,
        scope: { pairFromSlugs: ["always-defect"] },
      },
      {
        label: "Random–Random coordinates ≈ 50% (35–65%)",
        metric: "eqOutcomeRate",
        op: "between",
        threshold: 0.35,
        thresholdHigh: 0.65,
        scope: { player1StrategySlug: "random", player2StrategySlug: "random" },
      },
    ],
  },

  "Cooperation rate systematically exceeds Nash prediction in social dilemmas under repeated play": {
    scope: {
      gameId: 1,
      pairFromSlugs: ["tit-for-tat", "grim-trigger", "generous-tit-for-tat", "win-stay-lose-shift"],
    },
    all: [
      {
        label: "Mean cooperation rate among conditional-vs-conditional PD pairs > 30% (Nash predicts 0%)",
        metric: "actionCooperationRateOverall",
        op: ">",
        threshold: 0.3,
      },
    ],
  },
};

/**
 * Fill predicateJson for known v1 claims that don't have one yet. Idempotent.
 */
export async function backfillClaimPredicates(): Promise<void> {
  const pending = await db
    .select()
    .from(claimsTable)
    .where(isNull(claimsTable.predicateJson));

  let filled = 0;
  for (const claim of pending) {
    const predicate = V1_CLAIM_PREDICATES[claim.title];
    if (!predicate) continue;
    await db
      .update(claimsTable)
      .set({ predicateJson: JSON.stringify(predicate) })
      .where(and(eq(claimsTable.id, claim.id), isNull(claimsTable.predicateJson)));
    filled++;
  }
  if (filled > 0) {
    logger.info(`Backfilled structured predicates for ${filled} claims.`);
  }
}
