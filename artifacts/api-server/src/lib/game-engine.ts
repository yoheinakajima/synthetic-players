/**
 * Game Theory Engine
 * Implements strategy logic and game execution for classic game theory games.
 */

export interface GameDef {
  id: number;
  slug: string;
  numActions: number;
  actionLabels: string[];
  payoffMatrix: number[][][]; // [p1action][p2action] = [p1payoff, p2payoff]
  nashEquilibria: number[][]; // [[p1action, p2action], ...]
}

export interface RoundHistory {
  p1Action: number;
  p2Action: number;
  p1Payoff: number;
  p2Payoff: number;
}

// ── Strategy implementations ──────────────────────────────────────────────────

type StrategyFn = (
  history: RoundHistory[],
  playerNum: 1 | 2,
  game: GameDef
) => { action: number; reasoning: string };

const strategies: Record<string, StrategyFn> = {
  "always-cooperate": (_history, _playerNum, _game) => ({
    action: 0,
    reasoning: "Always play action 0 (cooperate/low/first option).",
  }),

  "always-defect": (_history, _playerNum, game) => ({
    action: game.numActions - 1,
    reasoning: "Always play the last action (defect/high/last option).",
  }),

  "tit-for-tat": (history, playerNum, _game) => {
    if (history.length === 0) {
      return { action: 0, reasoning: "First round: cooperate." };
    }
    const lastRound = history[history.length - 1];
    const opponentLastAction = playerNum === 1 ? lastRound.p2Action : lastRound.p1Action;
    return {
      action: opponentLastAction,
      reasoning: `Mirror opponent's last action: ${opponentLastAction}.`,
    };
  },

  "grim-trigger": (history, playerNum, game) => {
    const opponentEverDefected = history.some((r) => {
      const opponentAction = playerNum === 1 ? r.p2Action : r.p1Action;
      return opponentAction === game.numActions - 1;
    });
    if (opponentEverDefected) {
      return {
        action: game.numActions - 1,
        reasoning: "Opponent defected previously; permanently defecting.",
      };
    }
    return { action: 0, reasoning: "Opponent has always cooperated; cooperating." };
  },

  "random": (_history, _playerNum, game) => {
    const action = Math.floor(Math.random() * game.numActions);
    return { action, reasoning: `Randomly selected action ${action}.` };
  },

  "win-stay-lose-shift": (history, playerNum, game) => {
    if (history.length === 0) {
      return { action: 0, reasoning: "First round: start cooperating." };
    }
    const lastRound = history[history.length - 1];
    const myLastAction = playerNum === 1 ? lastRound.p1Action : lastRound.p2Action;
    const myLastPayoff = playerNum === 1 ? lastRound.p1Payoff : lastRound.p2Payoff;
    // Compute average payoff to determine "win" threshold
    const avgPayoff = history.reduce((s, r) =>
      s + (playerNum === 1 ? r.p1Payoff : r.p2Payoff), 0) / history.length;
    if (myLastPayoff >= avgPayoff) {
      return { action: myLastAction, reasoning: `Won last round (payoff ${myLastPayoff.toFixed(2)} >= avg ${avgPayoff.toFixed(2)}); staying with action ${myLastAction}.` };
    }
    const newAction = (myLastAction + 1) % game.numActions;
    return { action: newAction, reasoning: `Lost last round (payoff ${myLastPayoff.toFixed(2)} < avg ${avgPayoff.toFixed(2)}); shifting to action ${newAction}.` };
  },

  "nash-mixed": (_history, _playerNum, game) => {
    // Play a uniformly random Nash equilibrium action, or uniform random over actions
    // For games with pure Nash, pick one randomly; otherwise uniform random
    if (game.nashEquilibria.length > 0) {
      const ne = game.nashEquilibria[Math.floor(Math.random() * game.nashEquilibria.length)];
      // p1 is index 0, p2 is index 1 in nashEquilibria - but we'll just use the p1 action for both
      const action = ne[0];
      return { action, reasoning: `Playing action from Nash equilibrium: ${action}.` };
    }
    // Matching Pennies / RPS: uniform random (Nash mixed strategy)
    const action = Math.floor(Math.random() * game.numActions);
    return { action, reasoning: `Nash mixed strategy: uniform random action ${action}.` };
  },

  "generous-tit-for-tat": (history, playerNum, game) => {
    if (history.length === 0) {
      return { action: 0, reasoning: "First round: cooperate." };
    }
    const lastRound = history[history.length - 1];
    const opponentLastAction = playerNum === 1 ? lastRound.p2Action : lastRound.p1Action;
    // 10% chance to cooperate even after opponent defects
    if (opponentLastAction === game.numActions - 1 && Math.random() < 0.1) {
      return { action: 0, reasoning: "Opponent defected but forgiving with 10% probability." };
    }
    return { action: opponentLastAction, reasoning: `Mirror opponent: ${opponentLastAction}.` };
  },
};

export function getActionForStrategy(
  strategySlug: string,
  history: RoundHistory[],
  playerNum: 1 | 2,
  game: GameDef
): { action: number; reasoning: string } {
  const fn = strategies[strategySlug] ?? strategies["random"];
  return fn(history, playerNum, game);
}

// ── Game execution ────────────────────────────────────────────────────────────

export interface RunResult {
  rounds: Array<{
    roundNumber: number;
    player1Action: number;
    player2Action: number;
    player1Payoff: number;
    player2Payoff: number;
    player1Reasoning: string;
    player2Reasoning: string;
    isNashOutcome: boolean;
  }>;
  player1TotalPayoff: number;
  player2TotalPayoff: number;
  cooperationRate: number;
  nashDeviationScore: number;
}

export function runGame(
  game: GameDef,
  strategy1Slug: string,
  strategy2Slug: string,
  numRounds: number
): RunResult {
  const history: RoundHistory[] = [];
  const rounds: RunResult["rounds"] = [];

  let p1Total = 0;
  let p2Total = 0;
  let cooperativeRounds = 0;
  let nashRounds = 0;

  // Build Nash equilibrium set for quick lookup
  const nashSet = new Set(game.nashEquilibria.map(([a, b]) => `${a},${b}`));

  for (let i = 1; i <= numRounds; i++) {
    const p1Result = getActionForStrategy(strategy1Slug, history, 1, game);
    const p2Result = getActionForStrategy(strategy2Slug, history, 2, game);

    const p1Action = p1Result.action;
    const p2Action = p2Result.action;

    const [p1Payoff, p2Payoff] = game.payoffMatrix[p1Action][p2Action];
    const isNash = nashSet.has(`${p1Action},${p2Action}`);

    if (p1Action === 0 && p2Action === 0) cooperativeRounds++;
    if (isNash) nashRounds++;

    history.push({ p1Action, p2Action, p1Payoff, p2Payoff });
    p1Total += p1Payoff;
    p2Total += p2Payoff;

    rounds.push({
      roundNumber: i,
      player1Action: p1Action,
      player2Action: p2Action,
      player1Payoff: p1Payoff,
      player2Payoff: p2Payoff,
      player1Reasoning: p1Result.reasoning,
      player2Reasoning: p2Result.reasoning,
      isNashOutcome: isNash,
    });
  }

  // Nash deviation score: how far average payoffs are from Nash payoff
  // (lower is closer to Nash prediction)
  let nashP1Payoff = 0;
  let nashP2Payoff = 0;
  if (game.nashEquilibria.length > 0) {
    const ne = game.nashEquilibria[0];
    [nashP1Payoff, nashP2Payoff] = game.payoffMatrix[ne[0]][ne[1]];
  }
  const avgP1 = p1Total / numRounds;
  const avgP2 = p2Total / numRounds;
  const nashDeviationScore =
    (Math.abs(avgP1 - nashP1Payoff) + Math.abs(avgP2 - nashP2Payoff)) / 2;

  return {
    rounds,
    player1TotalPayoff: p1Total,
    player2TotalPayoff: p2Total,
    cooperationRate: cooperativeRounds / numRounds,
    nashDeviationScore,
  };
}

// ── Analysis computation ──────────────────────────────────────────────────────

export interface AnalysisResult {
  nashEquilibriumRate: number;
  player1CooperationRate: number;
  player2CooperationRate: number;
  player1AvgPayoff: number;
  player2AvgPayoff: number;
  theoreticalPlayer1Payoff: number;
  theoreticalPlayer2Payoff: number;
  player1PayoffDeviation: number;
  player2PayoffDeviation: number;
  mutualCooperationRate: number;
  mutualDefectionRate: number;
  mixedOutcomeRate: number;
  roundByRoundJson: string;
  summary: string;
}

export function computeAnalysis(
  rounds: Array<{
    player1Action: number;
    player2Action: number;
    player1Payoff: number;
    player2Payoff: number;
    isNashOutcome: boolean;
  }>,
  game: GameDef,
  strategy1Name: string,
  strategy2Name: string
): AnalysisResult {
  const n = rounds.length;
  if (n === 0) throw new Error("No rounds to analyze");

  const nashSet = new Set(game.nashEquilibria.map(([a, b]) => `${a},${b}`));

  let nashCount = 0;
  let p1CoopCount = 0;
  let p2CoopCount = 0;
  let mutualCoop = 0;
  let mutualDef = 0;
  let p1TotalPayoff = 0;
  let p2TotalPayoff = 0;

  const roundByRound: Array<{
    round: number;
    p1CumPayoff: number;
    p2CumPayoff: number;
    nashRate: number;
    coopRate: number;
  }> = [];

  for (let i = 0; i < rounds.length; i++) {
    const r = rounds[i];
    if (r.isNashOutcome) nashCount++;
    if (r.player1Action === 0) p1CoopCount++;
    if (r.player2Action === 0) p2CoopCount++;
    if (r.player1Action === 0 && r.player2Action === 0) mutualCoop++;
    if (r.player1Action === game.numActions - 1 && r.player2Action === game.numActions - 1) mutualDef++;
    p1TotalPayoff += r.player1Payoff;
    p2TotalPayoff += r.player2Payoff;

    roundByRound.push({
      round: i + 1,
      p1CumPayoff: p1TotalPayoff,
      p2CumPayoff: p2TotalPayoff,
      nashRate: nashCount / (i + 1),
      coopRate: (p1CoopCount + p2CoopCount) / (2 * (i + 1)),
    });
  }

  const nashEquilibriumRate = nashCount / n;
  const player1CooperationRate = p1CoopCount / n;
  const player2CooperationRate = p2CoopCount / n;
  const player1AvgPayoff = p1TotalPayoff / n;
  const player2AvgPayoff = p2TotalPayoff / n;
  const mutualCooperationRate = mutualCoop / n;
  const mutualDefectionRate = mutualDef / n;
  const mixedOutcomeRate = 1 - mutualCooperationRate - mutualDefectionRate;

  // Theoretical: if both played Nash each round
  let theoreticalPlayer1Payoff = 0;
  let theoreticalPlayer2Payoff = 0;
  if (game.nashEquilibria.length > 0) {
    const ne = game.nashEquilibria[0];
    [theoreticalPlayer1Payoff, theoreticalPlayer2Payoff] = game.payoffMatrix[ne[0]][ne[1]];
  }

  const player1PayoffDeviation =
    theoreticalPlayer1Payoff !== 0
      ? ((player1AvgPayoff - theoreticalPlayer1Payoff) / Math.abs(theoreticalPlayer1Payoff)) * 100
      : 0;
  const player2PayoffDeviation =
    theoreticalPlayer2Payoff !== 0
      ? ((player2AvgPayoff - theoreticalPlayer2Payoff) / Math.abs(theoreticalPlayer2Payoff)) * 100
      : 0;

  // Generate human-readable summary
  const nashPct = (nashEquilibriumRate * 100).toFixed(1);
  const coopPct = ((player1CooperationRate + player2CooperationRate) / 2 * 100).toFixed(1);
  const p1Dev = player1PayoffDeviation.toFixed(1);
  const p2Dev = player2PayoffDeviation.toFixed(1);

  let deviationDescription = "";
  if (Math.abs(player1PayoffDeviation) < 5 && Math.abs(player2PayoffDeviation) < 5) {
    deviationDescription = "Observed payoffs closely track Nash equilibrium predictions.";
  } else if (player1AvgPayoff > theoreticalPlayer1Payoff && player2AvgPayoff > theoreticalPlayer2Payoff) {
    deviationDescription = "Both players exceeded Nash equilibrium payoffs, suggesting cooperative over-performance.";
  } else if (player1AvgPayoff < theoreticalPlayer1Payoff || player2AvgPayoff < theoreticalPlayer2Payoff) {
    deviationDescription = "Players under-performed relative to Nash equilibrium predictions.";
  } else {
    deviationDescription = "Mixed deviation from Nash equilibrium across players.";
  }

  const summary =
    `In ${n} rounds of ${game.slug} between ${strategy1Name} and ${strategy2Name}, ` +
    `Nash equilibrium outcomes occurred in ${nashPct}% of rounds. ` +
    `Average cooperation rate was ${coopPct}%. ` +
    `Player 1 averaged ${player1AvgPayoff.toFixed(2)} per round (${p1Dev > "0" ? "+" : ""}${p1Dev}% vs Nash); ` +
    `Player 2 averaged ${player2AvgPayoff.toFixed(2)} per round (${p2Dev > "0" ? "+" : ""}${p2Dev}% vs Nash). ` +
    deviationDescription;

  return {
    nashEquilibriumRate,
    player1CooperationRate,
    player2CooperationRate,
    player1AvgPayoff,
    player2AvgPayoff,
    theoreticalPlayer1Payoff,
    theoreticalPlayer2Payoff,
    player1PayoffDeviation,
    player2PayoffDeviation,
    mutualCooperationRate,
    mutualDefectionRate,
    mixedOutcomeRate,
    roundByRoundJson: JSON.stringify(roundByRound),
    summary,
  };
}
