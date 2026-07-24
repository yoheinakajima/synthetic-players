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

// ── Analysis ──────────────────────────────────────────────────────────────
// Simulation itself now runs on the ActiveGraph engine sidecar
// (artifacts/api-server/engine); only round analysis remains in TypeScript.

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
