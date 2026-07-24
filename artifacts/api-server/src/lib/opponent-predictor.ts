/**
 * TS-side action predictors for DETERMINISTIC classic strategies, used only
 * inside the live LLM game loop (the LLM needs the opponent's move each round
 * before the run can be materialized on the engine).
 *
 * These are predictions, not the record: after the live loop, the run is
 * re-executed on the ActiveGraph engine with the real strategy slug and the
 * result is verified round-by-round against the live loop. Any divergence
 * fails the experiment — a predictor bug can never silently enter the data.
 *
 * RNG-consuming strategies (random, nash-mixed, generous-tit-for-tat) are
 * deliberately absent: predicting them would require duplicating seed-stream
 * bookkeeping here. LLM matchups against them are rejected upstream.
 */

import type { GameDef } from "./game-engine";

export interface LiveRound {
  p1Action: number;
  p2Action: number;
  p1Payoff: number;
  p2Payoff: number;
}

/** Slugs the live loop can predict (all consume zero RNG draws). */
export const PREDICTABLE_OPPONENTS: ReadonlySet<string> = new Set([
  "always-cooperate",
  "always-defect",
  "tit-for-tat",
  "grim-trigger",
  "win-stay-lose-shift",
]);

export function predictOpponentAction(
  slug: string,
  history: LiveRound[],
  playerNum: 1 | 2,
  game: Pick<GameDef, "numActions">
): number {
  const defect = game.numActions - 1;
  const oppLast = (): number => {
    const last = history[history.length - 1];
    return playerNum === 1 ? last.p2Action : last.p1Action;
  };

  switch (slug) {
    case "always-cooperate":
      return 0;
    case "always-defect":
      return defect;
    case "tit-for-tat":
      return history.length === 0 ? 0 : oppLast();
    case "grim-trigger": {
      const everDefected = history.some(
        (r) => (playerNum === 1 ? r.p2Action : r.p1Action) === defect
      );
      return everDefected ? defect : 0;
    }
    case "win-stay-lose-shift": {
      if (history.length === 0) return 0;
      const last = history[history.length - 1];
      const myAction = playerNum === 1 ? last.p1Action : last.p2Action;
      const myPayoff = playerNum === 1 ? last.p1Payoff : last.p2Payoff;
      let sum = 0;
      for (const r of history) sum += playerNum === 1 ? r.p1Payoff : r.p2Payoff;
      const avg = sum / history.length;
      return myPayoff >= avg ? myAction : (myAction + 1) % game.numActions;
    }
    default:
      throw new Error(
        `Cannot predict actions for strategy "${slug}" — not a supported deterministic opponent`
      );
  }
}
