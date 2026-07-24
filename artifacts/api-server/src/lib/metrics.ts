/**
 * Metrics v2 — per-game-class metric suite.
 *
 * Game classes and their headline metrics:
 *   social_dilemma  → joint welfare ratio, cooperation rates (action-level AND mutual)
 *   coordination    → equilibrium-outcome frequency, coordination rate, per-cell breakdown
 *   zero_sum        → exploitability (marginal + conditional), distribution tests vs Nash mixed
 *
 * Cooperation metrics are NULL for zero-sum games: "cooperate" has no meaning there.
 *
 * All formal definitions are documented in docs/METRICS.md.
 */

import type { GameDef } from "./game-engine";

export interface RoundData {
  player1Action: number;
  player2Action: number;
  player1Payoff: number;
  player2Payoff: number;
}

export type GameClass = "social_dilemma" | "coordination" | "zero_sum";

export interface MetricsV2 {
  gameClass: GameClass;

  // ── Universal ──────────────────────────────────────────────────────────
  numRounds: number;
  avgPayoffPerRoundP1: number;
  avgPayoffPerRoundP2: number;
  jointPayoffPerRound: number;
  /** Fraction of rounds landing in a pure Nash equilibrium cell. Null when the game has no pure NE (MP, RPS). */
  eqOutcomeRate: number | null;
  /** Per-cell outcome rates, keyed "cellRate:i,j" — merged into the flat metric map. */
  cellRates: Record<string, number>;
  /** Among rounds that were pure-NE outcomes, the share in each NE cell, keyed "cellShareOfEq:i,j". */
  cellSharesOfEq: Record<string, number>;

  // ── Dilemma + coordination only (null for zero-sum) ────────────────────
  actionCooperationRateP1: number | null;
  actionCooperationRateP2: number | null;
  actionCooperationRateOverall: number | null;
  mutualCooperationRate: number | null;
  /** Realized joint payoff / maximum joint payoff available in the matrix. */
  welfareRatio: number | null;
  /** First-round cooperation indicator (action 0) per seat: 1 or 0. Null for zero-sum. */
  round1CoopP1: number | null;
  round1CoopP2: number | null;

  // ── Coordination only ───────────────────────────────────────────────────
  /** Fraction of rounds where both players chose the same action index. */
  coordinationRate: number | null;

  // ── Zero-sum only ───────────────────────────────────────────────────────
  /** Best-response payoff against the player's empirical marginal action distribution, minus game value. */
  marginalExploitabilityP1: number | null;
  marginalExploitabilityP2: number | null;
  /**
   * Payoff an online first-order pattern tracker (Laplace-smoothed conditional
   * frequencies, 10-round burn-in) would have earned against this player's
   * actual action sequence, minus game value. The honest "could a tracker have
   * beaten this player" number.
   */
  conditionalExploitabilityP1: number | null;
  conditionalExploitabilityP2: number | null;
  /** Total variation distance of the empirical marginal from the uniform Nash mixed strategy. */
  tvFromUniformP1: number | null;
  tvFromUniformP2: number | null;
  /** |P(a_t = a_{t-1}) − Σ p_a²|: lag-1 serial dependence beyond what the marginal implies. */
  lag1RepeatDeviationP1: number | null;
  lag1RepeatDeviationP2: number | null;
  /** G-test p-value of observed joint outcomes vs the uniform Nash mixed outcome distribution. */
  gTestPValue: number | null;
  /** First-round action indicators for 3-action zero-sum games (null otherwise). */
  round1RockP1: number | null;
  round1RockP2: number | null;
  round1PaperP1: number | null;
  round1PaperP2: number | null;
  round1ScissorsP1: number | null;
  round1ScissorsP2: number | null;
  /** P(repeat previous action | previous round won). Win = payoff > 0; ties excluded. Null when no wins. */
  wslsStayGivenWinP1: number | null;
  wslsStayGivenWinP2: number | null;
  /** P(change action | previous round lost). Loss = payoff < 0; ties excluded. Null when no losses. */
  wslsShiftGivenLoseP1: number | null;
  wslsShiftGivenLoseP2: number | null;
  /**
   * EXPLORATORY ONLY: lag-1 transition counts keyed "prev,next". Deliberately
   * an object field so flattenMetrics never exposes it to the adjudicator
   * (pre-registration lock: transition heatmaps are never adjudicated).
   */
  lag1TransitionsP1: Record<string, number> | null;
  lag1TransitionsP2: Record<string, number> | null;
}

// ── Small numerics ─────────────────────────────────────────────────────────

/** Regularized upper incomplete gamma Q(s, x) via series/continued fraction. */
function gammaQ(s: number, x: number): number {
  if (x < 0 || s <= 0) return NaN;
  if (x === 0) return 1;
  const gln = lnGamma(s);
  if (x < s + 1) {
    // series for P(s,x), return 1 - P
    let sum = 1 / s;
    let term = sum;
    let ap = s;
    for (let i = 0; i < 200; i++) {
      ap += 1;
      term *= x / ap;
      sum += term;
      if (Math.abs(term) < Math.abs(sum) * 1e-12) break;
    }
    const p = sum * Math.exp(-x + s * Math.log(x) - gln);
    return Math.max(0, Math.min(1, 1 - p));
  }
  // continued fraction for Q(s,x)
  let b = x + 1 - s;
  let c = 1 / 1e-30;
  let d = 1 / b;
  let h = d;
  for (let i = 1; i < 200; i++) {
    const an = -i * (i - s);
    b += 2;
    d = an * d + b;
    if (Math.abs(d) < 1e-30) d = 1e-30;
    c = b + an / c;
    if (Math.abs(c) < 1e-30) c = 1e-30;
    d = 1 / d;
    const del = d * c;
    h *= del;
    if (Math.abs(del - 1) < 1e-12) break;
  }
  const q = Math.exp(-x + s * Math.log(x) - gln) * h;
  return Math.max(0, Math.min(1, q));
}

function lnGamma(z: number): number {
  // Lanczos approximation
  const g = 7;
  const c = [
    0.99999999999980993, 676.5203681218851, -1259.1392167224028, 771.32342877765313,
    -176.61502916214059, 12.507343278686905, -0.13857109526572012, 9.9843695780195716e-6,
    1.5056327351493116e-7,
  ];
  if (z < 0.5) return Math.log(Math.PI / Math.sin(Math.PI * z)) - lnGamma(1 - z);
  z -= 1;
  let x = c[0];
  for (let i = 1; i < g + 2; i++) x += c[i] / (z + i);
  const t = z + g + 0.5;
  return 0.5 * Math.log(2 * Math.PI) + (z + 0.5) * Math.log(t) - t + Math.log(x);
}

/** Chi-square upper-tail p-value. */
export function chiSquarePValue(statistic: number, df: number): number {
  if (df <= 0) return NaN;
  return gammaQ(df / 2, statistic / 2);
}

// ── Zero-sum helpers ───────────────────────────────────────────────────────

/** Expected payoff for the given seat when both players play uniform random (= game value for MP/RPS). */
function uniformGameValue(game: GameDef, seat: 1 | 2): number {
  let total = 0;
  for (let i = 0; i < game.numActions; i++) {
    for (let j = 0; j < game.numActions; j++) {
      total += game.payoffMatrix[i][j][seat - 1];
    }
  }
  return total / (game.numActions * game.numActions);
}

/**
 * Marginal exploitability of `seat`: how much the opponent's best response to
 * this seat's empirical marginal distribution would earn above the game value.
 * 0 for a perfectly uniform player in MP/RPS; large for e.g. Always-Rock.
 */
function marginalExploitability(game: GameDef, seat: 1 | 2, actions: number[]): number {
  const n = actions.length;
  const marginal = new Array(game.numActions).fill(0);
  for (const a of actions) marginal[a] += 1 / n;

  const oppSeat = seat === 1 ? 2 : 1;
  let bestOpp = -Infinity;
  for (let oppA = 0; oppA < game.numActions; oppA++) {
    let expected = 0;
    for (let myA = 0; myA < game.numActions; myA++) {
      const cell = seat === 1 ? game.payoffMatrix[myA][oppA] : game.payoffMatrix[oppA][myA];
      expected += marginal[myA] * cell[oppSeat - 1];
    }
    bestOpp = Math.max(bestOpp, expected);
  }
  return bestOpp - uniformGameValue(game, oppSeat as 1 | 2);
}

/**
 * Conditional (online pattern-tracker) exploitability of `seat`.
 * Simulates an opponent that, at each round t > burnIn, predicts this seat's
 * action from Laplace-smoothed first-order transition counts accumulated over
 * rounds < t, plays the best response to that prediction, and banks the payoff.
 * Returns tracker's average payoff minus game value. No look-ahead leakage.
 */
function conditionalExploitability(
  game: GameDef,
  seat: 1 | 2,
  actions: number[],
  burnIn = 10
): number | null {
  const n = actions.length;
  if (n <= burnIn + 2) return null;

  const k = game.numActions;
  const oppSeat = seat === 1 ? 2 : 1;
  // transition counts[prev][next], Laplace alpha=1
  const counts: number[][] = Array.from({ length: k }, () => new Array(k).fill(1));

  let trackerTotal = 0;
  let trackerRounds = 0;

  for (let t = 1; t < n; t++) {
    const prev = actions[t - 1];
    if (t > burnIn) {
      // predict distribution of actions[t] given prev
      const rowSum = counts[prev].reduce((s, c) => s + c, 0);
      const predicted = counts[prev].map((c) => c / rowSum);
      // best response to predicted distribution
      let bestA = 0;
      let bestVal = -Infinity;
      for (let oppA = 0; oppA < k; oppA++) {
        let expected = 0;
        for (let myA = 0; myA < k; myA++) {
          const cell = seat === 1 ? game.payoffMatrix[myA][oppA] : game.payoffMatrix[oppA][myA];
          expected += predicted[myA] * cell[oppSeat - 1];
        }
        if (expected > bestVal) {
          bestVal = expected;
          bestA = oppA;
        }
      }
      const actual = actions[t];
      const cell = seat === 1 ? game.payoffMatrix[actual][bestA] : game.payoffMatrix[bestA][actual];
      trackerTotal += cell[oppSeat - 1];
      trackerRounds++;
    }
    counts[prev][actions[t]] += 1;
  }

  if (trackerRounds === 0) return null;
  return trackerTotal / trackerRounds - uniformGameValue(game, oppSeat as 1 | 2);
}

function totalVariationFromUniform(numActions: number, actions: number[]): number {
  const n = actions.length;
  const marginal = new Array(numActions).fill(0);
  for (const a of actions) marginal[a] += 1 / n;
  let tv = 0;
  for (let i = 0; i < numActions; i++) tv += Math.abs(marginal[i] - 1 / numActions);
  return tv / 2;
}

function lag1RepeatDeviation(numActions: number, actions: number[]): number | null {
  const n = actions.length;
  if (n < 3) return null;
  const marginal = new Array(numActions).fill(0);
  for (const a of actions) marginal[a] += 1 / n;
  const expectedRepeat = marginal.reduce((s: number, p: number) => s + p * p, 0);
  let repeats = 0;
  for (let t = 1; t < n; t++) if (actions[t] === actions[t - 1]) repeats++;
  return Math.abs(repeats / (n - 1) - expectedRepeat);
}

/**
 * Win-stay / lose-shift conditionals for zero-sum play. Win = previous-round
 * payoff > 0, loss = < 0; ties are excluded from both denominators (locked in
 * the Phase 3 pre-registration). Null when a denominator is 0 — never 0/0=0.
 */
function wslsConditionals(
  actions: number[],
  payoffs: number[]
): { stayGivenWin: number | null; shiftGivenLose: number | null } {
  let winN = 0;
  let winStay = 0;
  let loseN = 0;
  let loseShift = 0;
  for (let t = 1; t < actions.length; t++) {
    const prevPay = payoffs[t - 1];
    if (prevPay > 0) {
      winN++;
      if (actions[t] === actions[t - 1]) winStay++;
    } else if (prevPay < 0) {
      loseN++;
      if (actions[t] !== actions[t - 1]) loseShift++;
    }
  }
  return {
    stayGivenWin: winN > 0 ? winStay / winN : null,
    shiftGivenLose: loseN > 0 ? loseShift / loseN : null,
  };
}

/** Lag-1 transition counts, keyed "prev,next". Exploratory — never flattened. */
function lag1Transitions(numActions: number, actions: number[]): Record<string, number> {
  const counts: Record<string, number> = {};
  for (let i = 0; i < numActions; i++) {
    for (let j = 0; j < numActions; j++) counts[`${i},${j}`] = 0;
  }
  for (let t = 1; t < actions.length; t++) {
    counts[`${actions[t - 1]},${actions[t]}`]++;
  }
  return counts;
}

/** G-test of joint outcome counts vs uniform Nash mixed prediction (each cell 1/k²). */
function gTestVsUniform(game: GameDef, rounds: RoundData[]): number {
  const k = game.numActions;
  const n = rounds.length;
  const expected = n / (k * k);
  const counts = new Map<string, number>();
  for (const r of rounds) {
    const key = `${r.player1Action},${r.player2Action}`;
    counts.set(key, (counts.get(key) ?? 0) + 1);
  }
  let g = 0;
  for (let i = 0; i < k; i++) {
    for (let j = 0; j < k; j++) {
      const o = counts.get(`${i},${j}`) ?? 0;
      if (o > 0) g += 2 * o * Math.log(o / expected);
    }
  }
  return chiSquarePValue(g, k * k - 1);
}

// ── Main entry ─────────────────────────────────────────────────────────────

export function computeMetricsV2(
  game: GameDef & { category: string },
  rounds: RoundData[]
): MetricsV2 {
  const n = rounds.length;
  if (n === 0) throw new Error("No rounds to analyze");

  const gameClass = game.category as GameClass;
  const k = game.numActions;

  const p1Actions = rounds.map((r) => r.player1Action);
  const p2Actions = rounds.map((r) => r.player2Action);
  const p1Total = rounds.reduce((s, r) => s + r.player1Payoff, 0);
  const p2Total = rounds.reduce((s, r) => s + r.player2Payoff, 0);

  // Universal: outcome cell rates
  const cellCounts = new Map<string, number>();
  for (const r of rounds) {
    const key = `${r.player1Action},${r.player2Action}`;
    cellCounts.set(key, (cellCounts.get(key) ?? 0) + 1);
  }
  const cellRates: Record<string, number> = {};
  for (let i = 0; i < k; i++) {
    for (let j = 0; j < k; j++) {
      cellRates[`cellRate:${i},${j}`] = (cellCounts.get(`${i},${j}`) ?? 0) / n;
    }
  }

  const nashCells = game.nashEquilibria.map(([a, b]) => `${a},${b}`);
  const hasPureNE = nashCells.length > 0;
  let eqRounds = 0;
  for (const cell of nashCells) eqRounds += cellCounts.get(cell) ?? 0;
  const eqOutcomeRate = hasPureNE ? eqRounds / n : null;

  const cellSharesOfEq: Record<string, number> = {};
  if (hasPureNE && eqRounds > 0) {
    for (const cell of nashCells) {
      cellSharesOfEq[`cellShareOfEq:${cell}`] = (cellCounts.get(cell) ?? 0) / eqRounds;
    }
  } else if (hasPureNE) {
    for (const cell of nashCells) cellSharesOfEq[`cellShareOfEq:${cell}`] = 0;
  }

  // Max joint payoff cell (welfare denominator)
  let maxJoint = -Infinity;
  for (let i = 0; i < k; i++) {
    for (let j = 0; j < k; j++) {
      const [a, b] = game.payoffMatrix[i][j];
      maxJoint = Math.max(maxJoint, a + b);
    }
  }

  const isZeroSum = gameClass === "zero_sum";

  // Cooperation metrics — meaningless for zero-sum, so explicitly null there.
  const p1Coop = isZeroSum ? null : p1Actions.filter((a) => a === 0).length / n;
  const p2Coop = isZeroSum ? null : p2Actions.filter((a) => a === 0).length / n;
  const mutualCoop = isZeroSum
    ? null
    : rounds.filter((r) => r.player1Action === 0 && r.player2Action === 0).length / n;

  const jointPerRound = (p1Total + p2Total) / n;
  const welfareRatio = isZeroSum || maxJoint === 0 ? null : jointPerRound / maxJoint;

  const p1Payoffs = rounds.map((r) => r.player1Payoff);
  const p2Payoffs = rounds.map((r) => r.player2Payoff);
  const wsls1 = isZeroSum ? wslsConditionals(p1Actions, p1Payoffs) : null;
  const wsls2 = isZeroSum ? wslsConditionals(p2Actions, p2Payoffs) : null;
  const isThreeAction = k === 3;
  const round1Indicator = (actions: number[], idx: number): number | null =>
    isZeroSum && isThreeAction ? (actions[0] === idx ? 1 : 0) : null;

  return {
    gameClass,
    numRounds: n,
    avgPayoffPerRoundP1: p1Total / n,
    avgPayoffPerRoundP2: p2Total / n,
    jointPayoffPerRound: jointPerRound,
    eqOutcomeRate,
    cellRates,
    cellSharesOfEq,

    actionCooperationRateP1: p1Coop,
    actionCooperationRateP2: p2Coop,
    actionCooperationRateOverall:
      p1Coop != null && p2Coop != null ? (p1Coop + p2Coop) / 2 : null,
    mutualCooperationRate: mutualCoop,
    welfareRatio,
    round1CoopP1: isZeroSum ? null : p1Actions[0] === 0 ? 1 : 0,
    round1CoopP2: isZeroSum ? null : p2Actions[0] === 0 ? 1 : 0,

    coordinationRate:
      gameClass === "coordination"
        ? rounds.filter((r) => r.player1Action === r.player2Action).length / n
        : null,

    marginalExploitabilityP1: isZeroSum ? marginalExploitability(game, 1, p1Actions) : null,
    marginalExploitabilityP2: isZeroSum ? marginalExploitability(game, 2, p2Actions) : null,
    conditionalExploitabilityP1: isZeroSum ? conditionalExploitability(game, 1, p1Actions) : null,
    conditionalExploitabilityP2: isZeroSum ? conditionalExploitability(game, 2, p2Actions) : null,
    tvFromUniformP1: isZeroSum ? totalVariationFromUniform(k, p1Actions) : null,
    tvFromUniformP2: isZeroSum ? totalVariationFromUniform(k, p2Actions) : null,
    lag1RepeatDeviationP1: isZeroSum ? lag1RepeatDeviation(k, p1Actions) : null,
    lag1RepeatDeviationP2: isZeroSum ? lag1RepeatDeviation(k, p2Actions) : null,
    gTestPValue: isZeroSum ? gTestVsUniform(game, rounds) : null,
    round1RockP1: round1Indicator(p1Actions, 0),
    round1RockP2: round1Indicator(p2Actions, 0),
    round1PaperP1: round1Indicator(p1Actions, 1),
    round1PaperP2: round1Indicator(p2Actions, 1),
    round1ScissorsP1: round1Indicator(p1Actions, 2),
    round1ScissorsP2: round1Indicator(p2Actions, 2),
    wslsStayGivenWinP1: wsls1?.stayGivenWin ?? null,
    wslsStayGivenWinP2: wsls2?.stayGivenWin ?? null,
    wslsShiftGivenLoseP1: wsls1?.shiftGivenLose ?? null,
    wslsShiftGivenLoseP2: wsls2?.shiftGivenLose ?? null,
    lag1TransitionsP1: isZeroSum ? lag1Transitions(k, p1Actions) : null,
    lag1TransitionsP2: isZeroSum ? lag1Transitions(k, p2Actions) : null,
  };
}

/**
 * Flatten MetricsV2 into a single { name → number } map for aggregation and
 * predicate resolution. Null metrics are omitted (not zero — absent).
 */
export function flattenMetrics(m: MetricsV2): Record<string, number> {
  const flat: Record<string, number> = {};
  const scalarKeys: Array<keyof MetricsV2> = [
    "numRounds",
    "avgPayoffPerRoundP1",
    "avgPayoffPerRoundP2",
    "jointPayoffPerRound",
    "eqOutcomeRate",
    "actionCooperationRateP1",
    "actionCooperationRateP2",
    "actionCooperationRateOverall",
    "mutualCooperationRate",
    "welfareRatio",
    "coordinationRate",
    "marginalExploitabilityP1",
    "marginalExploitabilityP2",
    "conditionalExploitabilityP1",
    "conditionalExploitabilityP2",
    "tvFromUniformP1",
    "tvFromUniformP2",
    "lag1RepeatDeviationP1",
    "lag1RepeatDeviationP2",
    "gTestPValue",
    "round1CoopP1",
    "round1CoopP2",
    "round1RockP1",
    "round1RockP2",
    "round1PaperP1",
    "round1PaperP2",
    "round1ScissorsP1",
    "round1ScissorsP2",
    "wslsStayGivenWinP1",
    "wslsStayGivenWinP2",
    "wslsShiftGivenLoseP1",
    "wslsShiftGivenLoseP2",
    // lag1Transitions* stay OFF this list by design: exploratory, never adjudicated.
  ];
  for (const key of scalarKeys) {
    const v = m[key];
    if (typeof v === "number" && Number.isFinite(v)) flat[key] = v;
  }
  Object.assign(flat, m.cellRates, m.cellSharesOfEq);
  return flat;
}
