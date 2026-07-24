import { Router, type IRouter } from "express";
import { eq, and, isNull, count, avg, sql } from "drizzle-orm";
import {
  db,
  experimentsTable,
  roundsTable,
  gamesTable,
  strategiesTable,
  claimsTable,
  papersTable,
  analysesTable,
} from "@workspace/db";
import {
  GetDashboardStatsResponse,
  GetStrategyLeaderboardResponse,
  GetGameSummariesResponse,
  GetRecentActivityQueryParams,
  GetRecentActivityResponse,
} from "@workspace/api-zod";

const router: IRouter = Router();

router.get("/dashboard/stats", async (_req, res): Promise<void> => {
  const [expStats] = await db
    .select({
      total: count(),
      completed: sql<number>`count(*) filter (where ${experimentsTable.status} = 'completed')`,
    })
    .from(experimentsTable);

  const [roundStats] = await db.select({ total: count() }).from(roundsTable);
  const [gameStats] = await db
    .select({
      covered: sql<number>`count(distinct ${experimentsTable.gameId}) filter (where ${experimentsTable.status} = 'completed')`,
    })
    .from(experimentsTable);

  const [claimStats] = await db
    .select({
      total: count(),
      supported: sql<number>`count(*) filter (where ${claimsTable.status} = 'supported')`,
      refuted: sql<number>`count(*) filter (where ${claimsTable.status} = 'refuted')`,
    })
    .from(claimsTable);

  const [paperStats] = await db.select({ total: count() }).from(papersTable);

  // Averages are evidence-like: exclude exploratory fork runs.
  const [avgStats] = await db
    .select({
      avgNashDev: avg(experimentsTable.nashDeviationScore),
      avgCoop: avg(experimentsTable.cooperationRate),
    })
    .from(experimentsTable)
    .where(
      and(
        eq(experimentsTable.status, "completed"),
        isNull(experimentsTable.parentExperimentId)
      )
    );

  res.json(
    GetDashboardStatsResponse.parse({
      totalExperiments: Number(expStats?.total ?? 0),
      completedExperiments: Number(expStats?.completed ?? 0),
      totalRounds: Number(roundStats?.total ?? 0),
      gamesCovered: Number(gameStats?.covered ?? 0),
      claimsGenerated: Number(claimStats?.total ?? 0),
      supportedClaims: Number(claimStats?.supported ?? 0),
      refutedClaims: Number(claimStats?.refuted ?? 0),
      papersGenerated: Number(paperStats?.total ?? 0),
      avgNashDeviationScore:
        avgStats?.avgNashDev != null ? Number(avgStats.avgNashDev) : null,
      avgCooperationRate:
        avgStats?.avgCoop != null ? Number(avgStats.avgCoop) : null,
    })
  );
});

router.get("/dashboard/strategy-leaderboard", async (_req, res): Promise<void> => {
  const strategies = await db.select().from(strategiesTable);

  const rows = await Promise.all(
    strategies.map(async (strat) => {
      // Leaderboard is an evidence surface: fork-lineage runs are excluded —
      // a fork's totals span a hybrid history that would be misattributed
      // to the post-swap strategy.
      const p1Exps = await db
        .select({
          payoff: experimentsTable.player1TotalPayoff,
          nashDev: experimentsTable.nashDeviationScore,
          coop: experimentsTable.cooperationRate,
          rounds: experimentsTable.numRounds,
        })
        .from(experimentsTable)
        .where(
          and(
            eq(experimentsTable.player1StrategyId, strat.id),
            isNull(experimentsTable.parentExperimentId)
          )
        );

      const p2Exps = await db
        .select({
          payoff: experimentsTable.player2TotalPayoff,
          nashDev: experimentsTable.nashDeviationScore,
          coop: experimentsTable.cooperationRate,
          rounds: experimentsTable.numRounds,
        })
        .from(experimentsTable)
        .where(
          and(
            eq(experimentsTable.player2StrategyId, strat.id),
            isNull(experimentsTable.parentExperimentId)
          )
        );

      const allExps = [...p1Exps, ...p2Exps].filter(
        (e) => e.payoff != null && e.nashDev != null
      );

      if (allExps.length === 0) {
        return {
          strategyId: strat.id,
          strategyName: strat.name,
          strategyType: strat.type,
          experimentsPlayed: 0,
          avgPayoff: 0,
          avgNashDeviationScore: 0,
          cooperationRate: null,
          rank: 0,
        };
      }

      const avgPayoff =
        allExps.reduce((s, e) => s + (e.payoff ?? 0) / (e.rounds ?? 1), 0) /
        allExps.length;
      const avgNashDev =
        allExps.reduce((s, e) => s + (e.nashDev ?? 0), 0) / allExps.length;
      const coopExps = allExps.filter((e) => e.coop != null);
      const avgCoop =
        coopExps.length > 0
          ? coopExps.reduce((s, e) => s + (e.coop ?? 0), 0) / coopExps.length
          : null;

      return {
        strategyId: strat.id,
        strategyName: strat.name,
        strategyType: strat.type,
        experimentsPlayed: allExps.length,
        avgPayoff,
        avgNashDeviationScore: avgNashDev,
        cooperationRate: avgCoop,
        rank: 0,
      };
    })
  );

  // Sort by avg payoff desc, assign ranks
  rows.sort((a, b) => b.avgPayoff - a.avgPayoff);
  rows.forEach((r, i) => {
    r.rank = i + 1;
  });

  res.json(GetStrategyLeaderboardResponse.parse(rows));
});

router.get("/dashboard/game-summaries", async (_req, res): Promise<void> => {
  const games = await db.select().from(gamesTable);

  const summaries = await Promise.all(
    games.map(async (game) => {
      const exps = await db
        .select()
        .from(experimentsTable)
        .where(eq(experimentsTable.gameId, game.id));

      // Evidence surface: exclude exploratory fork-lineage runs.
      const completed = exps.filter(
        (e) => e.status === "completed" && e.parentExperimentId == null
      );
      const coopExps = completed.filter((e) => e.cooperationRate != null);
      const nashExps = completed.filter((e) => e.nashDeviationScore != null);

      // Get analyses for this game's experiments
      const completedIds = completed.map((e) => e.id);
      let avgPayoffDev = 0;
      if (completedIds.length > 0) {
        const analyses = await db
          .select()
          .from(analysesTable)
          .where(
            sql`${analysesTable.experimentId} = ANY(ARRAY[${sql.join(completedIds.map((id) => sql`${id}`), sql`, `)}]::int[])`
          );
        if (analyses.length > 0) {
          avgPayoffDev =
            analyses.reduce(
              (s, a) =>
                s +
                (Math.abs(a.player1PayoffDeviation) + Math.abs(a.player2PayoffDeviation)) / 2,
              0
            ) / analyses.length;
        }
      }

      const [claimCount] = await db
        .select({ n: count() })
        .from(claimsTable)
        .where(eq(claimsTable.gameId, game.id));

      return {
        gameId: game.id,
        gameName: game.name,
        gameSlug: game.slug,
        category: game.category,
        experimentsRun: completed.length,
        avgCooperationRate:
          coopExps.length > 0
            ? coopExps.reduce((s, e) => s + (e.cooperationRate ?? 0), 0) / coopExps.length
            : 0,
        avgNashEquilibriumRate: 0, // computed from analyses, approximate here
        avgPayoffDeviation: avgPayoffDev,
        claimsCount: claimCount?.n ?? 0,
      };
    })
  );

  res.json(GetGameSummariesResponse.parse(summaries));
});

router.get("/dashboard/activity", async (req, res): Promise<void> => {
  const query = GetRecentActivityQueryParams.safeParse(req.query);
  if (!query.success) {
    res.status(400).json({ error: query.error.message });
    return;
  }
  const limit = query.data.limit ?? 20;

  const activities: Array<{
    id: string;
    type: string;
    title: string;
    description: string;
    timestamp: Date;
    relatedId: number | null;
  }> = [];

  // Recent completed experiments
  const recentExps = await db
    .select()
    .from(experimentsTable)
    .where(eq(experimentsTable.status, "completed"))
    .orderBy(sql`${experimentsTable.completedAt} desc nulls last`)
    .limit(limit);

  const games = await db.select().from(gamesTable);
  const strategies = await db.select().from(strategiesTable);
  const gamesMap = new Map(games.map((g) => [g.id, g]));
  const stratMap = new Map(strategies.map((s) => [s.id, s]));

  for (const exp of recentExps) {
    const game = gamesMap.get(exp.gameId);
    const s1 = stratMap.get(exp.player1StrategyId);
    const s2 = stratMap.get(exp.player2StrategyId);
    activities.push({
      id: `exp-${exp.id}`,
      type: "experiment_completed",
      title: `Experiment completed: ${game?.name ?? "Unknown"}`,
      description: `${s1?.name ?? "?"} vs ${s2?.name ?? "?"} — ${exp.numRounds} rounds, cooperation rate ${((exp.cooperationRate ?? 0) * 100).toFixed(1)}%`,
      timestamp: exp.completedAt ?? exp.createdAt,
      relatedId: exp.id,
    });
  }

  // Recent claims
  const recentClaims = await db
    .select()
    .from(claimsTable)
    .orderBy(sql`${claimsTable.updatedAt} desc`)
    .limit(limit);

  for (const claim of recentClaims) {
    const isNew = Math.abs(claim.updatedAt.getTime() - claim.createdAt.getTime()) < 5000;
    activities.push({
      id: `claim-${claim.id}`,
      type: isNew ? "claim_created" : "claim_updated",
      title: isNew ? `New claim: ${claim.title}` : `Claim updated: ${claim.title}`,
      description: `Status: ${claim.status} — ${claim.statement.slice(0, 100)}${claim.statement.length > 100 ? "…" : ""}`,
      timestamp: claim.updatedAt,
      relatedId: claim.id,
    });
  }

  // Recent analyses
  const recentAnalyses = await db
    .select()
    .from(analysesTable)
    .orderBy(sql`${analysesTable.createdAt} desc`)
    .limit(limit);

  for (const analysis of recentAnalyses) {
    const exp = recentExps.find((e) => e.id === analysis.experimentId);
    const game = exp ? gamesMap.get(exp.gameId) : null;
    activities.push({
      id: `analysis-${analysis.id}`,
      type: "analysis_created",
      title: `Analysis generated${game ? `: ${game.name}` : ""}`,
      description: analysis.summary.slice(0, 120) + (analysis.summary.length > 120 ? "…" : ""),
      timestamp: analysis.createdAt,
      relatedId: analysis.experimentId,
    });
  }

  // Sort all by timestamp descending, take top N
  activities.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
  const top = activities.slice(0, limit);

  res.json(GetRecentActivityResponse.parse(top));
});

export default router;
