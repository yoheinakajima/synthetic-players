import { Router, type IRouter } from "express";
import { eq, asc } from "drizzle-orm";
import {
  db,
  analysesTable,
  experimentsTable,
  roundsTable,
  gamesTable,
  strategiesTable,
} from "@workspace/db";
import {
  GetAnalysisParams,
  GetAnalysisResponse,
  CreateAnalysisParams,
  CreateAnalysisResponse,
} from "@workspace/api-zod";
import { computeAnalysis, type GameDef } from "../lib/game-engine";

const router: IRouter = Router();

router.get("/experiments/:experimentId/analysis", async (req, res): Promise<void> => {
  const params = GetAnalysisParams.safeParse(req.params);
  if (!params.success) {
    res.status(400).json({ error: params.error.message });
    return;
  }

  const [analysis] = await db
    .select()
    .from(analysesTable)
    .where(eq(analysesTable.experimentId, params.data.experimentId));

  if (!analysis) {
    res.status(404).json({ error: "Analysis not found for this experiment" });
    return;
  }

  res.json(GetAnalysisResponse.parse(analysis));
});

router.post("/experiments/:experimentId/analysis", async (req, res): Promise<void> => {
  const params = CreateAnalysisParams.safeParse(req.params);
  if (!params.success) {
    res.status(400).json({ error: params.error.message });
    return;
  }

  const [exp] = await db
    .select()
    .from(experimentsTable)
    .where(eq(experimentsTable.id, params.data.experimentId));

  if (!exp) {
    res.status(404).json({ error: "Experiment not found" });
    return;
  }

  if (exp.status !== "completed") {
    res.status(400).json({ error: "Experiment must be completed before analysis" });
    return;
  }

  const [game] = await db.select().from(gamesTable).where(eq(gamesTable.id, exp.gameId));
  const [p1Strat] = await db.select().from(strategiesTable).where(eq(strategiesTable.id, exp.player1StrategyId));
  const [p2Strat] = await db.select().from(strategiesTable).where(eq(strategiesTable.id, exp.player2StrategyId));

  if (!game || !p1Strat || !p2Strat) {
    res.status(400).json({ error: "Game or strategy not found" });
    return;
  }

  const rounds = await db
    .select()
    .from(roundsTable)
    .where(eq(roundsTable.experimentId, exp.id))
    .orderBy(asc(roundsTable.roundNumber));

  if (rounds.length === 0) {
    res.status(400).json({ error: "No rounds found for experiment" });
    return;
  }

  const gameDef: GameDef = {
    id: game.id,
    slug: game.slug,
    numActions: game.numActions,
    actionLabels: JSON.parse(game.actionLabels) as string[],
    payoffMatrix: JSON.parse(game.payoffMatrix) as number[][][],
    nashEquilibria: JSON.parse(game.nashEquilibria) as number[][],
  };

  const result = computeAnalysis(rounds, gameDef, p1Strat.name, p2Strat.name);

  // Upsert analysis
  const [existing] = await db
    .select()
    .from(analysesTable)
    .where(eq(analysesTable.experimentId, exp.id));

  let analysis;
  if (existing) {
    [analysis] = await db
      .update(analysesTable)
      .set(result)
      .where(eq(analysesTable.experimentId, exp.id))
      .returning();
  } else {
    [analysis] = await db
      .insert(analysesTable)
      .values({ experimentId: exp.id, ...result })
      .returning();
  }

  res.status(201).json(CreateAnalysisResponse.parse(analysis));
});

export default router;
