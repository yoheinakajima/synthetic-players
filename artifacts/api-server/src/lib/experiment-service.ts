/**
 * Shared experiment execution + analysis service.
 * Used by both the single-run route and the seeded batch runner so the
 * execution path is identical everywhere.
 */

import { eq, asc } from "drizzle-orm";
import {
  db,
  experimentsTable,
  gamesTable,
  strategiesTable,
  roundsTable,
  analysesTable,
} from "@workspace/db";
import { computeAnalysis, type GameDef } from "./game-engine";
import { runOnEngine, EngineUnreachableError, EngineRequestError } from "./engine-client";
import { computeMetricsV2 } from "./metrics";
import { invalidateEvidenceCache } from "./adjudicator";

/** Map engine failures to an HTTP status + message (502 when the sidecar is down). */
export function engineErrorStatus(err: unknown): { status: number; message: string } {
  if (err instanceof EngineUnreachableError) return { status: 502, message: err.message };
  if (err instanceof EngineRequestError)
    return { status: err.status >= 500 ? 502 : err.status, message: err.message };
  return { status: 500, message: err instanceof Error ? err.message : "Unknown error" };
}

export type ExperimentRow = typeof experimentsTable.$inferSelect;
export type GameRow = typeof gamesTable.$inferSelect;

export function toGameDef(game: GameRow): GameDef & { category: string } {
  return {
    id: game.id,
    slug: game.slug,
    numActions: game.numActions,
    actionLabels: JSON.parse(game.actionLabels) as string[],
    payoffMatrix: JSON.parse(game.payoffMatrix) as number[][][],
    nashEquilibria: JSON.parse(game.nashEquilibria) as number[][],
    category: game.category,
  };
}

/** Random 31-bit seed. Only the seed is random — the run itself is fully determined by it. */
export function generateSeed(): number {
  return Math.floor(Math.random() * 2147483647);
}

/** Add computed per-round payoff averages (presentation values — totals stay totals). */
export function withPerRoundAverages<
  T extends { player1TotalPayoff: number | null; player2TotalPayoff: number | null; numRounds: number },
>(exp: T): T & { player1AvgPayoffPerRound: number | null; player2AvgPayoffPerRound: number | null } {
  return {
    ...exp,
    player1AvgPayoffPerRound:
      exp.player1TotalPayoff != null && exp.numRounds > 0
        ? exp.player1TotalPayoff / exp.numRounds
        : null,
    player2AvgPayoffPerRound:
      exp.player2TotalPayoff != null && exp.numRounds > 0
        ? exp.player2TotalPayoff / exp.numRounds
        : null,
  };
}

/**
 * Run an experiment end to end: seed (persisting one if absent), play all
 * rounds deterministically, store rounds, update totals. Throws on failure
 * after marking the experiment failed.
 */
export async function executeExperiment(expId: number): Promise<ExperimentRow> {
  const [exp] = await db.select().from(experimentsTable).where(eq(experimentsTable.id, expId));
  if (!exp) throw new Error(`Experiment ${expId} not found`);

  const [game] = await db.select().from(gamesTable).where(eq(gamesTable.id, exp.gameId));
  const [p1Strat] = await db
    .select()
    .from(strategiesTable)
    .where(eq(strategiesTable.id, exp.player1StrategyId));
  const [p2Strat] = await db
    .select()
    .from(strategiesTable)
    .where(eq(strategiesTable.id, exp.player2StrategyId));
  if (!game || !p1Strat || !p2Strat) throw new Error("Game or strategy not found");

  // Ensure a persisted seed BEFORE running, so every run is reproducible.
  let seed = exp.seed;
  if (seed == null) {
    seed = generateSeed();
    await db.update(experimentsTable).set({ seed }).where(eq(experimentsTable.id, exp.id));
  }

  await db.update(experimentsTable).set({ status: "running" }).where(eq(experimentsTable.id, exp.id));

  try {
    // Simulation runs on the ActiveGraph engine sidecar. If the engine is
    // unreachable this throws before any rounds are persisted.
    const result = await runOnEngine({
      game: toGameDef(game),
      strategy1Slug: p1Strat.slug,
      strategy2Slug: p2Strat.slug,
      numRounds: exp.numRounds,
      seed,
    });

    // Delete any existing rounds (re-run scenario)
    await db.delete(roundsTable).where(eq(roundsTable.experimentId, exp.id));

    if (result.rounds.length > 0) {
      await db.insert(roundsTable).values(
        result.rounds.map((r) => ({
          experimentId: exp.id,
          roundNumber: r.roundNumber,
          player1Action: r.player1Action,
          player2Action: r.player2Action,
          player1Payoff: r.player1Payoff,
          player2Payoff: r.player2Payoff,
          player1Reasoning: r.player1Reasoning,
          player2Reasoning: r.player2Reasoning,
          isNashOutcome: r.isNashOutcome,
        }))
      );
    }

    const [updated] = await db
      .update(experimentsTable)
      .set({
        status: "completed",
        engineRunId: result.engineRunId,
        player1TotalPayoff: result.player1TotalPayoff,
        player2TotalPayoff: result.player2TotalPayoff,
        cooperationRate: result.cooperationRate,
        nashDeviationScore: result.nashDeviationScore,
        completedAt: new Date(),
        errorMessage: null,
      })
      .where(eq(experimentsTable.id, exp.id))
      .returning();

    invalidateEvidenceCache();
    return updated;
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown error";
    await db
      .update(experimentsTable)
      .set({ status: "failed", errorMessage: message })
      .where(eq(experimentsTable.id, exp.id));
    throw err;
  }
}

/**
 * Compute (or recompute) the analysis for a completed experiment.
 * Writes analysisVersion 2 with the per-game-class metrics in metricsJson,
 * while keeping the legacy v1 columns populated for continuity.
 */
export async function analyzeExperiment(expId: number): Promise<typeof analysesTable.$inferSelect> {
  const [exp] = await db.select().from(experimentsTable).where(eq(experimentsTable.id, expId));
  if (!exp) throw new Error(`Experiment ${expId} not found`);
  if (exp.status !== "completed") throw new Error(`Experiment ${expId} is not completed`);

  const [game] = await db.select().from(gamesTable).where(eq(gamesTable.id, exp.gameId));
  const [p1Strat] = await db
    .select()
    .from(strategiesTable)
    .where(eq(strategiesTable.id, exp.player1StrategyId));
  const [p2Strat] = await db
    .select()
    .from(strategiesTable)
    .where(eq(strategiesTable.id, exp.player2StrategyId));
  if (!game || !p1Strat || !p2Strat) throw new Error("Game or strategy not found");

  const rounds = await db
    .select()
    .from(roundsTable)
    .where(eq(roundsTable.experimentId, exp.id))
    .orderBy(asc(roundsTable.roundNumber));
  if (rounds.length === 0) throw new Error(`No rounds found for experiment ${expId}`);

  const gameDef = toGameDef(game);
  const legacy = computeAnalysis(rounds, gameDef, p1Strat.name, p2Strat.name);
  const metricsV2 = computeMetricsV2(gameDef, rounds);

  const values = {
    ...legacy,
    analysisVersion: 2,
    metricsJson: JSON.stringify(metricsV2),
  };

  const [existing] = await db
    .select()
    .from(analysesTable)
    .where(eq(analysesTable.experimentId, exp.id));

  let analysis;
  if (existing) {
    [analysis] = await db
      .update(analysesTable)
      .set(values)
      .where(eq(analysesTable.experimentId, exp.id))
      .returning();
  } else {
    [analysis] = await db
      .insert(analysesTable)
      .values({ experimentId: exp.id, ...values })
      .returning();
  }

  invalidateEvidenceCache();
  return analysis;
}
