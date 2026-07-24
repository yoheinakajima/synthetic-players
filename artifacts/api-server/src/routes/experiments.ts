import { Router, type IRouter } from "express";
import { eq, and } from "drizzle-orm";
import {
  db,
  experimentsTable,
  gamesTable,
  strategiesTable,
  roundsTable,
  analysesTable,
} from "@workspace/db";
import {
  ListExperimentsQueryParams,
  ListExperimentsResponse,
  CreateExperimentBody,
  CreateExperimentResponse,
  GetExperimentParams,
  GetExperimentResponse,
  RunExperimentParams,
  RunExperimentResponse,
  RunExperimentBatchBody,
  RunExperimentBatchResponse,
  DeleteExperimentParams,
} from "@workspace/api-zod";
import {
  executeExperiment,
  analyzeExperiment,
  generateSeed,
  withPerRoundAverages,
} from "../lib/experiment-service";
import { logger } from "../lib/logger";

const router: IRouter = Router();

async function buildExperimentDetail(exp: typeof experimentsTable.$inferSelect) {
  const [game] = await db.select().from(gamesTable).where(eq(gamesTable.id, exp.gameId));
  const [p1Strategy] = await db.select().from(strategiesTable).where(eq(strategiesTable.id, exp.player1StrategyId));
  const [p2Strategy] = await db.select().from(strategiesTable).where(eq(strategiesTable.id, exp.player2StrategyId));
  const rounds = await db
    .select()
    .from(roundsTable)
    .where(eq(roundsTable.experimentId, exp.id))
    .orderBy(roundsTable.roundNumber);

  return {
    ...withPerRoundAverages(exp),
    game: game ? { ...game, actionLabels: JSON.parse(game.actionLabels) as string[] } : game,
    player1Strategy: p1Strategy,
    player2Strategy: p2Strategy,
    rounds,
  };
}

router.get("/experiments", async (req, res): Promise<void> => {
  const query = ListExperimentsQueryParams.safeParse(req.query);
  if (!query.success) {
    res.status(400).json({ error: query.error.message });
    return;
  }

  const conditions = [];
  if (query.data.gameId != null) {
    conditions.push(eq(experimentsTable.gameId, query.data.gameId));
  }
  if (query.data.status != null) {
    conditions.push(eq(experimentsTable.status, query.data.status));
  }
  if (query.data.batchLabel != null) {
    conditions.push(eq(experimentsTable.batchLabel, query.data.batchLabel));
  }

  const experiments = await db
    .select()
    .from(experimentsTable)
    .where(conditions.length > 0 ? and(...conditions) : undefined)
    .orderBy(experimentsTable.createdAt);

  // Enrich with game and strategy names
  const games = await db.select().from(gamesTable);
  const strategies = await db.select().from(strategiesTable);
  const gamesMap = new Map(games.map((g) => [g.id, g]));
  const stratMap = new Map(strategies.map((s) => [s.id, s]));

  const enriched = experiments.map((exp) => ({
    ...withPerRoundAverages(exp),
    gameName: gamesMap.get(exp.gameId)?.name ?? null,
    player1StrategyName: stratMap.get(exp.player1StrategyId)?.name ?? null,
    player2StrategyName: stratMap.get(exp.player2StrategyId)?.name ?? null,
  }));

  res.json(ListExperimentsResponse.parse(enriched));
});

router.post("/experiments", async (req, res): Promise<void> => {
  const parsed = CreateExperimentBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: parsed.error.message });
    return;
  }

  // Validate game and strategies exist
  const [game] = await db.select().from(gamesTable).where(eq(gamesTable.id, parsed.data.gameId));
  if (!game) {
    res.status(400).json({ error: "Game not found" });
    return;
  }

  const [p1] = await db.select().from(strategiesTable).where(eq(strategiesTable.id, parsed.data.player1StrategyId));
  const [p2] = await db.select().from(strategiesTable).where(eq(strategiesTable.id, parsed.data.player2StrategyId));
  if (!p1 || !p2) {
    res.status(400).json({ error: "Strategy not found" });
    return;
  }

  const [exp] = await db
    .insert(experimentsTable)
    .values({
      gameId: parsed.data.gameId,
      player1StrategyId: parsed.data.player1StrategyId,
      player2StrategyId: parsed.data.player2StrategyId,
      numRounds: parsed.data.numRounds,
      seed: parsed.data.seed ?? generateSeed(),
      batchLabel: parsed.data.batchLabel ?? null,
      notes: parsed.data.notes ?? null,
    })
    .returning();

  const detail = await buildExperimentDetail(exp);
  res.status(201).json(CreateExperimentResponse.parse(detail));
});

/**
 * Seeded replicate batch: creates one experiment per seed, runs each
 * deterministically, and computes its v2 analysis. This is how matchups
 * involving probabilistic strategies get distributions instead of anecdotes.
 */
router.post("/experiments/batch", async (req, res): Promise<void> => {
  const parsed = RunExperimentBatchBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: parsed.error.message });
    return;
  }

  const [game] = await db.select().from(gamesTable).where(eq(gamesTable.id, parsed.data.gameId));
  if (!game) {
    res.status(400).json({ error: "Game not found" });
    return;
  }
  const [p1] = await db.select().from(strategiesTable).where(eq(strategiesTable.id, parsed.data.player1StrategyId));
  const [p2] = await db.select().from(strategiesTable).where(eq(strategiesTable.id, parsed.data.player2StrategyId));
  if (!p1 || !p2) {
    res.status(400).json({ error: "Strategy not found" });
    return;
  }

  const uniqueSeeds = new Set(parsed.data.seeds);
  if (uniqueSeeds.size !== parsed.data.seeds.length) {
    res.status(400).json({ error: "Seeds must be unique within a batch" });
    return;
  }

  const batchLabel = parsed.data.batchLabel ?? `${game.slug}:${p1.slug}-vs-${p2.slug}`;

  // Idempotency: a seed that already exists for this matchup + batchLabel is
  // skipped, never re-run. Re-submitting a partially completed batch fills in
  // only the missing seeds — duplicate seeds would be pseudo-replicates
  // (identical deterministic runs counted twice) and would corrupt CIs.
  const existing = await db
    .select({ seed: experimentsTable.seed })
    .from(experimentsTable)
    .where(
      and(
        eq(experimentsTable.gameId, parsed.data.gameId),
        eq(experimentsTable.player1StrategyId, parsed.data.player1StrategyId),
        eq(experimentsTable.player2StrategyId, parsed.data.player2StrategyId),
        eq(experimentsTable.batchLabel, batchLabel)
      )
    );
  const existingSeeds = new Set(existing.map((e) => e.seed).filter((s): s is number => s != null));
  const newSeeds = parsed.data.seeds.filter((s) => !existingSeeds.has(s));
  const skippedSeeds = parsed.data.seeds.filter((s) => existingSeeds.has(s));

  const experimentIds: number[] = [];
  for (const seed of newSeeds) {
    const [exp] = await db
      .insert(experimentsTable)
      .values({
        gameId: parsed.data.gameId,
        player1StrategyId: parsed.data.player1StrategyId,
        player2StrategyId: parsed.data.player2StrategyId,
        numRounds: parsed.data.numRounds,
        seed,
        batchLabel,
        notes: parsed.data.notes ?? `Batch replicate (seed ${seed})`,
      })
      .returning();

    await executeExperiment(exp.id);
    await analyzeExperiment(exp.id);
    experimentIds.push(exp.id);
  }

  logger.info(
    `Batch "${batchLabel}": ran ${experimentIds.length} seeded replicates, skipped ${skippedSeeds.length} existing (${game.slug}, ${p1.slug} vs ${p2.slug}, ${parsed.data.numRounds} rounds each)`
  );

  res.status(201).json(RunExperimentBatchResponse.parse({ batchLabel, experimentIds, skippedSeeds }));
});

router.get("/experiments/:id", async (req, res): Promise<void> => {
  const params = GetExperimentParams.safeParse(req.params);
  if (!params.success) {
    res.status(400).json({ error: params.error.message });
    return;
  }

  const [exp] = await db
    .select()
    .from(experimentsTable)
    .where(eq(experimentsTable.id, params.data.id));

  if (!exp) {
    res.status(404).json({ error: "Experiment not found" });
    return;
  }

  const detail = await buildExperimentDetail(exp);
  res.json(GetExperimentResponse.parse(detail));
});

router.post("/experiments/:id/run", async (req, res): Promise<void> => {
  const params = RunExperimentParams.safeParse(req.params);
  if (!params.success) {
    res.status(400).json({ error: params.error.message });
    return;
  }

  const [exp] = await db
    .select()
    .from(experimentsTable)
    .where(eq(experimentsTable.id, params.data.id));

  if (!exp) {
    res.status(404).json({ error: "Experiment not found" });
    return;
  }

  if (exp.status === "running") {
    res.status(400).json({ error: "Experiment is already running" });
    return;
  }
  if (exp.status === "completed") {
    res.status(400).json({ error: "Experiment already completed. Create a new experiment to run again." });
    return;
  }

  try {
    const updated = await executeExperiment(exp.id);
    const detail = await buildExperimentDetail(updated);
    res.json(RunExperimentResponse.parse(detail));
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown error";
    res.status(500).json({ error: `Experiment execution failed: ${message}` });
  }
});

router.delete("/experiments/:id", async (req, res): Promise<void> => {
  const params = DeleteExperimentParams.safeParse(req.params);
  if (!params.success) {
    res.status(400).json({ error: params.error.message });
    return;
  }

  // Delete dependents first (no cascade)
  await db.delete(roundsTable).where(eq(roundsTable.experimentId, params.data.id));
  await db.delete(analysesTable).where(eq(analysesTable.experimentId, params.data.id));

  const [deleted] = await db
    .delete(experimentsTable)
    .where(eq(experimentsTable.id, params.data.id))
    .returning();

  if (!deleted) {
    res.status(404).json({ error: "Experiment not found" });
    return;
  }

  res.sendStatus(204);
});

export default router;
