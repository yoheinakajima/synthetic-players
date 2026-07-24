import { Router, type IRouter } from "express";
import { eq, and, isNull } from "drizzle-orm";
import { db, analysesTable, experimentsTable } from "@workspace/db";
import {
  GetAnalysisParams,
  GetAnalysisResponse,
  CreateAnalysisParams,
  CreateAnalysisResponse,
  GetAggregateAnalysisQueryParams,
  GetAggregateAnalysisResponse,
} from "@workspace/api-zod";
import { analyzeExperiment } from "../lib/experiment-service";
import { flattenMetrics, type MetricsV2 } from "../lib/metrics";
import { sampleStats } from "../lib/adjudicator";

const router: IRouter = Router();

/**
 * Aggregate v2 metrics across analyzed experiments matching the filter.
 * Returns mean / sd / 95% t-interval per metric — the numbers behind every
 * "X ± Y" statement in the paper.
 */
router.get("/analyses/aggregate", async (req, res): Promise<void> => {
  const query = GetAggregateAnalysisQueryParams.safeParse(req.query);
  if (!query.success) {
    res.status(400).json({ error: query.error.message });
    return;
  }

  // Aggregates are evidence: exclude fork-lineage experiments (hybrid histories).
  const conditions = [
    eq(experimentsTable.status, "completed"),
    isNull(experimentsTable.parentExperimentId),
  ];
  if (query.data.gameId != null) conditions.push(eq(experimentsTable.gameId, query.data.gameId));
  if (query.data.player1StrategyId != null)
    conditions.push(eq(experimentsTable.player1StrategyId, query.data.player1StrategyId));
  if (query.data.player2StrategyId != null)
    conditions.push(eq(experimentsTable.player2StrategyId, query.data.player2StrategyId));
  if (query.data.batchLabel != null)
    conditions.push(eq(experimentsTable.batchLabel, query.data.batchLabel));

  const rows = await db
    .select({ analysis: analysesTable })
    .from(analysesTable)
    .innerJoin(experimentsTable, eq(analysesTable.experimentId, experimentsTable.id))
    .where(and(...conditions));

  const flats: Record<string, number>[] = [];
  for (const { analysis } of rows) {
    if (analysis.analysisVersion < 2 || !analysis.metricsJson) continue;
    try {
      flats.push(flattenMetrics(JSON.parse(analysis.metricsJson) as MetricsV2));
    } catch {
      // skip malformed
    }
  }

  const metricNames = new Set<string>();
  for (const flat of flats) for (const key of Object.keys(flat)) metricNames.add(key);

  const metrics = [...metricNames].sort().map((name) => {
    const values = flats.map((f) => f[name]).filter((v): v is number => typeof v === "number");
    const stats = sampleStats(values);
    return {
      name,
      n: stats.n,
      mean: stats.mean ?? 0,
      sd: stats.sd,
      ciLow: stats.ciLow,
      ciHigh: stats.ciHigh,
    };
  });

  res.json(
    GetAggregateAnalysisResponse.parse({
      n: flats.length,
      gameId: query.data.gameId ?? null,
      player1StrategyId: query.data.player1StrategyId ?? null,
      player2StrategyId: query.data.player2StrategyId ?? null,
      batchLabel: query.data.batchLabel ?? null,
      metrics,
    })
  );
});

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

  // Forks are exploratory what-if runs with hybrid histories. They get the
  // engine's diff view, but never an analysis row — analyses are evidence,
  // and fork metrics would contaminate claim adjudication and aggregates.
  if (exp.parentExperimentId != null) {
    res.status(400).json({
      error:
        "Fork experiments are exploratory and excluded from evidence. Use the parent-vs-fork diff view instead.",
    });
    return;
  }

  try {
    const analysis = await analyzeExperiment(exp.id);
    res.status(201).json(CreateAnalysisResponse.parse(analysis));
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown error";
    res.status(400).json({ error: message });
  }
});

export default router;
