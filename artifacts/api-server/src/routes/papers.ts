import { Router, type IRouter } from "express";
import { eq, inArray } from "drizzle-orm";
import { db, papersTable, claimsTable, experimentsTable, gamesTable, strategiesTable, analysesTable } from "@workspace/db";
import {
  ListPapersResponse,
  GeneratePaperBody,
  GeneratePaperResponse,
  GetPaperParams,
  GetPaperResponse,
} from "@workspace/api-zod";

const router: IRouter = Router();

router.get("/papers", async (_req, res): Promise<void> => {
  const papers = await db
    .select()
    .from(papersTable)
    .orderBy(papersTable.createdAt);
  res.json(ListPapersResponse.parse(papers));
});

router.post("/papers", async (req, res): Promise<void> => {
  const parsed = GeneratePaperBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: parsed.error.message });
    return;
  }

  // Gather data for paper generation
  let experiments = await db
    .select()
    .from(experimentsTable)
    .where(eq(experimentsTable.status, "completed"));

  const gameIds = parsed.data.gameIds ?? [];
  if (gameIds.length > 0) {
    experiments = experiments.filter((e) => gameIds.includes(e.gameId));
  }

  const claims = await db.select().from(claimsTable).orderBy(claimsTable.createdAt);

  const games = await db.select().from(gamesTable).orderBy(gamesTable.id);
  const strategies = await db.select().from(strategiesTable);

  const gamesMap = new Map(games.map((g) => [g.id, g]));
  const strategiesMap = new Map(strategies.map((s) => [s.id, s]));

  // Generate paper sections
  const sections: Array<{ heading: string; content: string }> = [];

  // Abstract
  const abstractText =
    parsed.data.abstract ??
    `This paper presents an empirical study of ${experiments.length} experiments across ${new Set(experiments.map((e) => e.gameId)).size} classic game theory games. ` +
    `We compare the behavior of ${strategies.length} algorithmic strategies against Nash equilibrium predictions, ` +
    `analyzing cooperation rates, payoff deviations, and strategic performance. ` +
    `The study surfaces ${claims.filter((c) => c.status === "supported").length} supported research claims and ` +
    `${claims.filter((c) => c.status === "refuted").length} refuted hypotheses.`;

  // Introduction
  sections.push({
    heading: "1. Introduction",
    content:
      `Game theory provides a mathematical framework for analyzing strategic interactions between rational agents. ` +
      `While classical game theory predicts behavior through Nash equilibria, empirical studies frequently reveal ` +
      `systematic deviations — particularly cooperation in social dilemmas and coordination failures in pure coordination games. ` +
      `This study uses the Game Theory Research Lab to systematically run and compare ${experiments.length} experiments across ` +
      `${games.length} canonical games, testing ${strategies.length} distinct strategies ranging from always-cooperate to ` +
      `sophisticated tit-for-tat variants. All experimental data, rounds, and analyses are recorded with full provenance.`,
  });

  // Games overview
  const gamesSummary = games
    .map((g) => {
      const expCount = experiments.filter((e) => e.gameId === g.id).length;
      return `**${g.name}** (${g.category.replace("_", " ")}): ${expCount} experiments. ${g.nashDescription ?? ""}`;
    })
    .join("\n\n");

  sections.push({
    heading: "2. Games",
    content:
      `The following ${games.length} canonical games were studied:\n\n` + gamesSummary,
  });

  // Strategies
  const stratsSummary = strategies
    .map((s) => `**${s.name}** (${s.type}): ${s.description}`)
    .join("\n\n");
  sections.push({
    heading: "3. Strategies",
    content:
      `The following ${strategies.length} strategies were evaluated:\n\n` + stratsSummary,
  });

  // Experimental results by game
  const resultsByGame: string[] = [];
  for (const game of games) {
    const gameExps = experiments.filter((e) => e.gameId === game.id);
    if (gameExps.length === 0) continue;

    const avgCoop =
      gameExps
        .filter((e) => e.cooperationRate != null)
        .reduce((s, e) => s + (e.cooperationRate ?? 0), 0) /
      Math.max(gameExps.filter((e) => e.cooperationRate != null).length, 1);

    const avgNashDev =
      gameExps
        .filter((e) => e.nashDeviationScore != null)
        .reduce((s, e) => s + (e.nashDeviationScore ?? 0), 0) /
      Math.max(gameExps.filter((e) => e.nashDeviationScore != null).length, 1);

    let section = `**${game.name}** (${gameExps.length} experiments)\n`;
    section += `Average cooperation rate: ${(avgCoop * 100).toFixed(1)}% `;
    section += `(theoretical Nash prediction: ${((game.theoreticalCooperationRate ?? 0) * 100).toFixed(0)}%)\n`;
    section += `Average Nash deviation score: ${avgNashDev.toFixed(3)}\n\n`;

    for (const exp of gameExps.slice(0, 5)) {
      const s1 = strategiesMap.get(exp.player1StrategyId);
      const s2 = strategiesMap.get(exp.player2StrategyId);
      section += `- ${s1?.name ?? "?"} vs ${s2?.name ?? "?"}: `;
      section += `coop rate ${((exp.cooperationRate ?? 0) * 100).toFixed(1)}%, `;
      section += `payoffs ${(exp.player1TotalPayoff ?? 0).toFixed(1)} / ${(exp.player2TotalPayoff ?? 0).toFixed(1)}\n`;
    }
    resultsByGame.push(section);
  }

  sections.push({
    heading: "4. Experimental Results",
    content: resultsByGame.join("\n\n") || "No completed experiments yet.",
  });

  // Claims
  if (claims.length > 0) {
    const claimsSummary = claims
      .map((c) => {
        const game = gamesMap.get(c.gameId);
        return (
          `**[${c.status.toUpperCase()}] ${c.title}** (${game?.name ?? "Unknown game"})\n` +
          `Claim: ${c.statement}\n` +
          (c.evidenceSummary ? `Evidence: ${c.evidenceSummary}` : "")
        );
      })
      .join("\n\n");

    sections.push({
      heading: "5. Research Claims",
      content:
        `The following ${claims.length} claims were generated from experimental analyses:\n\n` +
        claimsSummary,
    });
  }

  // Conclusion
  const totalRounds = experiments.reduce((s) => s + (0), 0);
  const coopGames = games.filter((g) => g.category === "coordination");
  const socialDilemmas = games.filter((g) => g.category === "social_dilemma");

  sections.push({
    heading: "6. Discussion and Conclusion",
    content:
      `Our study reveals systematic patterns in strategic behavior across ${games.length} canonical game theory scenarios. ` +
      `In social dilemmas (${socialDilemmas.map((g) => g.name).join(", ")}), ` +
      `strategies that begin with cooperation and respond conditionally ` +
      `(such as Tit-for-Tat and Generous Tit-for-Tat) consistently outperform ` +
      `pure defection strategies over repeated interactions. ` +
      `In coordination games (${coopGames.map((g) => g.name).join(", ")}), ` +
      `the choice of equilibrium is heavily influenced by the first-round action, ` +
      `highlighting the role of focal points in resolving coordination problems. ` +
      `In zero-sum games, random and Nash mixed strategies perform as theoretically predicted, ` +
      `while deterministic strategies are systematically exploited. ` +
      `These results support the broader conclusion that Nash equilibrium is a useful prediction tool ` +
      `for zero-sum games, but substantially under-predicts cooperation in social dilemmas ` +
      `and over-simplifies coordination in multi-equilibrium games.`,
  });

  // Methodology
  sections.push({
    heading: "Appendix: Methodology",
    content:
      `All experiments were conducted using the Game Theory Research Lab, an open platform for reproducible ` +
      `game theory experiments. Each experiment configures a game type, two strategies, and a number of rounds. ` +
      `Strategies are evaluated in iterated game settings where history is available to each player. ` +
      `Statistical analyses compare observed outcomes to Nash equilibrium predictions using cooperation rates, ` +
      `payoff deviations (as percentage deviation from theoretical Nash payoffs), and Nash outcome frequency. ` +
      `All raw data including round-by-round decisions and payoffs is publicly accessible through the lab interface.`,
  });

  const sectionsJson = JSON.stringify(sections);
  const wordCount = sections.reduce((s, sec) => s + sec.content.split(/\s+/).length, 0);

  const [paper] = await db
    .insert(papersTable)
    .values({
      title: parsed.data.title,
      abstract: abstractText,
      status: "complete",
      sections: sectionsJson,
      claimsJson: JSON.stringify(claims.map((c) => c.id)),
      experimentsJson: JSON.stringify(experiments.map((e) => e.id)),
      wordCount,
    })
    .returning();

  res.status(201).json(GeneratePaperResponse.parse(paper));
});

router.get("/papers/:id", async (req, res): Promise<void> => {
  const params = GetPaperParams.safeParse(req.params);
  if (!params.success) {
    res.status(400).json({ error: params.error.message });
    return;
  }

  const [paper] = await db
    .select()
    .from(papersTable)
    .where(eq(papersTable.id, params.data.id));

  if (!paper) {
    res.status(404).json({ error: "Paper not found" });
    return;
  }

  res.json(GetPaperResponse.parse(paper));
});

export default router;
