/**
 * Fork-comparison metrics — paired parent-vs-fork evaluation over the
 * post-fork window.
 *
 * A fork shares its parent's history through round F (the fork round) and may
 * diverge from round F+1 on. The only honest comparison is therefore over the
 * shared window F+1..N for BOTH runs — identical round counts, identical
 * starting history. Whole-run fork metrics are banned from evidence (hybrid
 * histories); these window metrics are the paired replacement.
 *
 * welfareRecoveryFrac answers "how much of the gap between the parent's
 * post-fork welfare and the best available welfare did the fork close?":
 *
 *   (forkWelfare − parentWelfare) / (maxWelfare − parentWelfare)
 *
 * where all three are per-round joint payoffs over the window and maxWelfare
 * is the best joint payoff any cell of the matrix offers. Null when the
 * parent already sits at max welfare (no gap to close) or for zero-sum games
 * (joint payoff is constant — recovery is undefined there, so it is null,
 * never 0). Negative values mean the switch made things worse; values can
 * exceed 1 only by float noise (clamped).
 *
 * Definitions documented in docs/METRICS.md ("Fork-comparison metrics").
 */

import type { GameDef } from "./game-engine";

export interface WindowRound {
  roundNumber: number;
  player1Action: number;
  player2Action: number;
  player1Payoff: number;
  player2Payoff: number;
  isNashOutcome: boolean | null;
}

export interface WindowMetrics {
  p1PayoffPerRound: number;
  p2PayoffPerRound: number;
  welfarePerRound: number;
  /** Action-level cooperation rate (fraction of actions = index 0). Null for zero-sum. */
  coopRate: number | null;
  /** Fraction of rounds where both players played action 0. Null for zero-sum. */
  mutualCoopRate: number | null;
  /** Fraction of window rounds landing in a pure-NE cell (per stored flags). Null if no flags. */
  eqRate: number | null;
}

export interface ForkWindowComparison {
  forkRound: number;
  windowRounds: number;
  parent: WindowMetrics;
  fork: WindowMetrics;
  /** fork − parent, per field (null where either side is null). */
  delta: {
    p1PayoffPerRound: number;
    p2PayoffPerRound: number;
    welfarePerRound: number;
    coopRate: number | null;
    mutualCoopRate: number | null;
    eqRate: number | null;
  };
  /** Fraction of the parent's welfare gap to the matrix maximum that the fork closed. */
  welfareRecoveryFrac: number | null;
}

const EPS = 1e-9;

export function maxJointPayoffPerRound(gameDef: GameDef): number {
  let max = -Infinity;
  for (const row of gameDef.payoffMatrix) {
    for (const [a, b] of row) {
      if (a + b > max) max = a + b;
    }
  }
  return max;
}

export function computeWindowMetrics(
  gameDef: GameDef & { category: string },
  rounds: WindowRound[]
): WindowMetrics {
  const n = rounds.length;
  if (n === 0) throw new Error("computeWindowMetrics: empty window");
  const isZeroSum = gameDef.category === "zero_sum";

  const p1Total = rounds.reduce((s, r) => s + r.player1Payoff, 0);
  const p2Total = rounds.reduce((s, r) => s + r.player2Payoff, 0);

  let coopActions = 0;
  let mutualCoop = 0;
  let eqKnown = 0;
  let eqCount = 0;
  for (const r of rounds) {
    if (r.player1Action === 0) coopActions++;
    if (r.player2Action === 0) coopActions++;
    if (r.player1Action === 0 && r.player2Action === 0) mutualCoop++;
    if (r.isNashOutcome != null) {
      eqKnown++;
      if (r.isNashOutcome) eqCount++;
    }
  }

  return {
    p1PayoffPerRound: p1Total / n,
    p2PayoffPerRound: p2Total / n,
    welfarePerRound: (p1Total + p2Total) / n,
    coopRate: isZeroSum ? null : coopActions / (2 * n),
    mutualCoopRate: isZeroSum ? null : mutualCoop / n,
    eqRate: eqKnown === n ? eqCount / n : null,
  };
}

/**
 * Compare parent vs fork over the shared post-fork window (rounds > forkRound).
 * Throws if either run lacks the full window — a comparison over unequal
 * windows would be meaningless.
 */
export function computeForkComparison(
  gameDef: GameDef & { category: string },
  parentRounds: WindowRound[],
  forkRounds: WindowRound[],
  forkRound: number
): ForkWindowComparison {
  const parentWindow = parentRounds
    .filter((r) => r.roundNumber > forkRound)
    .sort((a, b) => a.roundNumber - b.roundNumber);
  const forkWindow = forkRounds
    .filter((r) => r.roundNumber > forkRound)
    .sort((a, b) => a.roundNumber - b.roundNumber);

  if (parentWindow.length === 0 || forkWindow.length === 0) {
    throw new Error(
      `Fork comparison needs a non-empty post-fork window (forkRound=${forkRound})`
    );
  }
  if (parentWindow.length !== forkWindow.length) {
    throw new Error(
      `Post-fork windows differ in length (parent ${parentWindow.length}, fork ${forkWindow.length})`
    );
  }

  const parent = computeWindowMetrics(gameDef, parentWindow);
  const fork = computeWindowMetrics(gameDef, forkWindow);

  const sub = (a: number | null, b: number | null): number | null =>
    a == null || b == null ? null : a - b;

  let welfareRecoveryFrac: number | null = null;
  if (gameDef.category !== "zero_sum") {
    const maxWelfare = maxJointPayoffPerRound(gameDef);
    const gap = maxWelfare - parent.welfarePerRound;
    if (gap > EPS) {
      welfareRecoveryFrac = Math.min(
        1,
        (fork.welfarePerRound - parent.welfarePerRound) / gap
      );
    }
  }

  return {
    forkRound,
    windowRounds: forkWindow.length,
    parent,
    fork,
    delta: {
      p1PayoffPerRound: fork.p1PayoffPerRound - parent.p1PayoffPerRound,
      p2PayoffPerRound: fork.p2PayoffPerRound - parent.p2PayoffPerRound,
      welfarePerRound: fork.welfarePerRound - parent.welfarePerRound,
      coopRate: sub(fork.coopRate, parent.coopRate),
      mutualCoopRate: sub(fork.mutualCoopRate, parent.mutualCoopRate),
      eqRate: sub(fork.eqRate, parent.eqRate),
    },
    welfareRecoveryFrac,
  };
}

/**
 * Flatten a comparison into the `postFork.*` metric namespace used by
 * fork-comparison claim predicates. Null metrics are omitted — a predicate on
 * an undefined metric must come back "untested", never see a fake 0.
 */
export function flattenForkComparison(c: ForkWindowComparison): Record<string, number> {
  const out: Record<string, number> = {
    "postFork.windowRounds": c.windowRounds,
    "postFork.p1PayoffPerRoundParent": c.parent.p1PayoffPerRound,
    "postFork.p2PayoffPerRoundParent": c.parent.p2PayoffPerRound,
    "postFork.welfarePerRoundParent": c.parent.welfarePerRound,
    "postFork.p1PayoffPerRoundFork": c.fork.p1PayoffPerRound,
    "postFork.p2PayoffPerRoundFork": c.fork.p2PayoffPerRound,
    "postFork.welfarePerRoundFork": c.fork.welfarePerRound,
    "postFork.p1PayoffPerRoundDelta": c.delta.p1PayoffPerRound,
    "postFork.p2PayoffPerRoundDelta": c.delta.p2PayoffPerRound,
    "postFork.welfarePerRoundDelta": c.delta.welfarePerRound,
  };
  const put = (key: string, v: number | null) => {
    if (v != null) out[key] = v;
  };
  put("postFork.coopRateParent", c.parent.coopRate);
  put("postFork.coopRateFork", c.fork.coopRate);
  put("postFork.coopRateDelta", c.delta.coopRate);
  put("postFork.mutualCoopRateParent", c.parent.mutualCoopRate);
  put("postFork.mutualCoopRateFork", c.fork.mutualCoopRate);
  put("postFork.mutualCoopRateDelta", c.delta.mutualCoopRate);
  put("postFork.eqRateParent", c.parent.eqRate);
  put("postFork.eqRateFork", c.fork.eqRate);
  put("postFork.eqRateDelta", c.delta.eqRate);
  put("postFork.welfareRecoveryFrac", c.welfareRecoveryFrac);
  return out;
}
