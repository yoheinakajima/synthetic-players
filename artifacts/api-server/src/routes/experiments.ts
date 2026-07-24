import { Router, type IRouter } from "express";
import { eq, and } from "drizzle-orm";
import {
  db,
  experimentsTable,
  gamesTable,
  strategiesTable,
  roundsTable,
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
  DeleteExperimentParams,
} from "@workspace/api-zod";
import { runGame, type GameDef } from "../lib/game-engine";

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
    ...exp,
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
    ...exp,
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
      notes: parsed.data.notes ?? null,
    })
    .returning();

  const detail = await buildExperimentDetail(exp);
  res.status(201).json(CreateExperimentResponse.parse(detail));
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

  // Load game and strategies
  const [game] = await db.select().from(gamesTable).where(eq(gamesTable.id, exp.gameId));
  const [p1Strat] = await db.select().from(strategiesTable).where(eq(strategiesTable.id, exp.player1StrategyId));
  const [p2Strat] = await db.select().from(strategiesTable).where(eq(strategiesTable.id, exp.player2StrategyId));

  if (!game || !p1Strat || !p2Strat) {
    res.status(400).json({ error: "Game or strategy not found" });
    return;
  }

  // Mark as running
  await db
    .update(experimentsTable)
    .set({ status: "running" })
    .where(eq(experimentsTable.id, exp.id));

  try {
    const gameDef: GameDef = {
      id: game.id,
      slug: game.slug,
      numActions: game.numActions,
      actionLabels: JSON.parse(game.actionLabels) as string[],
      payoffMatrix: JSON.parse(game.payoffMatrix) as number[][][],
      nashEquilibria: JSON.parse(game.nashEquilibria) as number[][],
    };

    const result = runGame(gameDef, p1Strat.slug, p2Strat.slug, exp.numRounds);

    // Delete any existing rounds (re-run scenario)
    await db.delete(roundsTable).where(eq(roundsTable.experimentId, exp.id));

    // Insert rounds
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

    // Update experiment with results
    const [updated] = await db
      .update(experimentsTable)
      .set({
        status: "completed",
        player1TotalPayoff: result.player1TotalPayoff,
        player2TotalPayoff: result.player2TotalPayoff,
        cooperationRate: result.cooperationRate,
        nashDeviationScore: result.nashDeviationScore,
        completedAt: new Date(),
        errorMessage: null,
      })
      .where(eq(experimentsTable.id, exp.id))
      .returning();

    const detail = await buildExperimentDetail(updated);
    res.json(RunExperimentResponse.parse(detail));
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown error";
    await db
      .update(experimentsTable)
      .set({ status: "failed", errorMessage: message })
      .where(eq(experimentsTable.id, exp.id));

    res.status(500).json({ error: `Experiment execution failed: ${message}` });
  }
});

router.delete("/experiments/:id", async (req, res): Promise<void> => {
  const params = DeleteExperimentParams.safeParse(req.params);
  if (!params.success) {
    res.status(400).json({ error: params.error.message });
    return;
  }

  // Delete rounds first (no cascade)
  await db.delete(roundsTable).where(eq(roundsTable.experimentId, params.data.id));

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
