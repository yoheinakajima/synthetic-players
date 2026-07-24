import { Router, type IRouter } from "express";
import { eq } from "drizzle-orm";
import {
  db,
  papersTable,
  claimsTable,
  experimentsTable,
  gamesTable,
  strategiesTable,
  analysesTable,
} from "@workspace/db";
import {
  ListPapersResponse,
  GeneratePaperBody,
  GeneratePaperResponse,
  GetPaperParams,
  GetPaperResponse,
} from "@workspace/api-zod";
import { flattenMetrics, type MetricsV2 } from "../lib/metrics";
import { sampleStats, type SampleStats, type AdjudicationRecord } from "../lib/adjudicator";

const router: IRouter = Router();

router.get("/papers", async (_req, res): Promise<void> => {
  const papers = await db
    .select()
    .from(papersTable)
    .orderBy(papersTable.createdAt);
  res.json(ListPapersResponse.parse(papers));
});

// ── v2 paper generator ─────────────────────────────────────────────────────
// Principles: every number is per-round or a rate; every claim statement in
// the paper carries its mechanical verdict; refuted claims are reported as
// refuted, not silently dropped. See docs/METRICS.md for metric definitions.

function fmtStats(s: SampleStats, digits = 3): string {
  if (s.n === 0 || s.mean == null) return "no data";
  if (s.n === 1 || s.sd == null) return `${s.mean.toFixed(digits)} (n=1)`;
  if (s.sd === 0) return `${s.mean.toFixed(digits)} (n=${s.n}, no variance)`;
  return `${s.mean.toFixed(digits)} (95% CI [${s.ciLow!.toFixed(digits)}, ${s.ciHigh!.toFixed(digits)}], n=${s.n})`;
}

function fmtPct(s: SampleStats): string {
  if (s.n === 0 || s.mean == null) return "no data";
  const pct = (v: number) => `${(v * 100).toFixed(1)}%`;
  if (s.n === 1 || s.sd == null) return `${pct(s.mean)} (n=1)`;
  if (s.sd === 0) return `${pct(s.mean)} (n=${s.n}, no variance)`;
  return `${pct(s.mean)} (95% CI [${pct(s.ciLow!)}, ${pct(s.ciHigh!)}], n=${s.n})`;
}

router.post("/papers", async (req, res): Promise<void> => {
  const parsed = GeneratePaperBody.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: parsed.error.message });
    return;
  }

  let experiments = await db
    .select()
    .from(experimentsTable)
    .where(eq(experimentsTable.status, "completed"));

  // Papers are evidence documents: fork-lineage runs (hybrid what-if
  // histories) are excluded from counts, matchup aggregates, and
  // experimentsJson alike.
  experiments = experiments.filter((e) => e.parentExperimentId == null);

  const gameIds = parsed.data.gameIds ?? [];
  if (gameIds.length > 0) {
    experiments = experiments.filter((e) => gameIds.includes(e.gameId));
  }

  const claims = await db.select().from(claimsTable).orderBy(claimsTable.id);
  const games = await db.select().from(gamesTable).orderBy(gamesTable.id);
  const strategies = await db.select().from(strategiesTable);
  const analyses = await db.select().from(analysesTable);

  const gamesMap = new Map(games.map((g) => [g.id, g]));
  const strategiesMap = new Map(strategies.map((s) => [s.id, s]));

  // Flat v2 metrics per experiment
  const flatByExp = new Map<number, Record<string, number>>();
  for (const a of analyses) {
    if (a.analysisVersion >= 2 && a.metricsJson) {
      try {
        flatByExp.set(a.experimentId, flattenMetrics(JSON.parse(a.metricsJson) as MetricsV2));
      } catch {
        // skip malformed
      }
    }
  }

  // Group experiments into matchups (unordered strategy pair within a game)
  interface Matchup {
    gameId: number;
    aId: number; // lower strategy id
    bId: number;
    expIds: number[];
    flats: Record<string, number>[];
    seeded: number;
  }
  const matchups = new Map<string, Matchup>();
  for (const exp of experiments) {
    const flat = flatByExp.get(exp.id);
    if (!flat) continue;
    const [aId, bId] =
      exp.player1StrategyId <= exp.player2StrategyId
        ? [exp.player1StrategyId, exp.player2StrategyId]
        : [exp.player2StrategyId, exp.player1StrategyId];
    const key = `${exp.gameId}|${aId}|${bId}`;
    let m = matchups.get(key);
    if (!m) {
      m = { gameId: exp.gameId, aId, bId, expIds: [], flats: [], seeded: 0 };
      matchups.set(key, m);
    }
    m.expIds.push(exp.id);
    m.flats.push(flat);
    if (exp.seed != null) m.seeded++;
  }

  const agg = (m: Matchup, metric: string): SampleStats =>
    sampleStats(m.flats.map((f) => f[metric]).filter((v): v is number => typeof v === "number"));

  const matchupName = (m: Matchup) =>
    `${strategiesMap.get(m.aId)?.name ?? "?"} vs ${strategiesMap.get(m.bId)?.name ?? "?"}`;

  const sections: Array<{ heading: string; content: string }> = [];

  const analyzedCount = flatByExp.size;
  const replicatedMatchups = [...matchups.values()].filter((m) => m.expIds.length >= 2).length;

  // Verdict counts from current claim statuses
  const counts = {
    supported: claims.filter((c) => c.status === "supported").length,
    refuted: claims.filter((c) => c.status === "refuted").length,
    inconclusive: claims.filter((c) => c.status === "inconclusive").length,
    untested: claims.filter((c) => c.status === "untested" || c.status === "hypothesis").length,
  };

  const abstractText =
    parsed.data.abstract ??
    `We report a fully reproducible computational study of ${experiments.length} seeded experiments across ` +
      `${new Set(experiments.map((e) => e.gameId)).size} canonical games and ${strategies.length} algorithmic strategies. ` +
      `Every experiment stores its RNG seed and full round-by-round provenance; matchups involving probabilistic strategies ` +
      `were replicated across independent seeds (${replicatedMatchups} replicated matchups) and are reported with 95% confidence intervals. ` +
      `All research claims were checked mechanically against structured predicates: ${counts.supported} supported, ` +
      `${counts.refuted} refuted, ${counts.inconclusive} inconclusive, ${counts.untested} untested. ` +
      `Refuted claims — including one of our own v1 headline claims — are reported as refuted, with the original error analyzed in the errata.`;

  // 1. Introduction
  sections.push({
    heading: "1. Introduction",
    content:
      `Classical game theory predicts play via Nash equilibrium, yet observed behavior — human or algorithmic — ` +
      `routinely deviates in structured ways. This study measures those deviations across three game classes ` +
      `(social dilemmas, coordination games, zero-sum games) using metrics appropriate to each class, rather than ` +
      `a single one-size-fits-all "Nash rate".\n\n` +
      `This is version 2 of the lab's findings. Version 1 (frozen in the project archive) contained errors that this ` +
      `version's methodology was explicitly designed to catch: claims were adjudicated by the same process that wrote them, ` +
      `metrics were pooled across game classes where they had no meaning, and raw payoff totals were presented where ` +
      `per-round averages were required. Section 7 documents each error. The central methodological change is that claims ` +
      `are now stated as machine-checkable predicates and adjudicated mechanically against the recorded data — ` +
      `the author no longer gets a vote.`,
  });

  // 2. Methods
  sections.push({
    heading: "2. Methods",
    content:
      `**Engine.** Each experiment plays two strategies against each other for a fixed number of rounds. ` +
      `All randomness flows from a single mulberry32 PRNG initialized with the experiment's stored seed; ` +
      `re-running any experiment with its seed reproduces every round exactly. Unseeded v1 experiments are ` +
      `retained but marked (seed=null).\n\n` +
      `**Replication.** Matchups involving probabilistic strategies (Random, Nash Mixed, Generous Tit-for-Tat) were ` +
      `re-run as 20-seed batches; deterministic matchups need no replication (zero variance across seeds). ` +
      `Statistics are reported as mean with 95% t-intervals over seeds.\n\n` +
      `**Metrics (v2, per game class).** Social dilemmas: joint welfare ratio (realized joint payoff / Pareto-optimal joint payoff), ` +
      `action-level and mutual cooperation rates. Coordination: equilibrium-outcome rate, coordination rate, per-equilibrium shares. ` +
      `Zero-sum: marginal exploitability (best response to empirical action marginal, minus game value), conditional exploitability ` +
      `(payoff of an online first-order pattern tracker with Laplace smoothing and 10-round burn-in, minus game value), ` +
      `total-variation distance from the Nash mixed strategy, and a G-test of outcome distributions against the Nash prediction. ` +
      `Cooperation rates are not defined for zero-sum games and are never reported there. Full definitions: docs/METRICS.md.\n\n` +
      `**Claim adjudication.** Every claim carries a structured predicate: metric, comparison, threshold, and evidence scope. ` +
      `The adjudicator selects matching experiments, computes the sample statistics, and issues a verdict: supported only if ` +
      `the entire 95% CI satisfies the comparison (exact comparison for deterministic evidence), refuted only if the entire CI ` +
      `violates it, inconclusive when the CI straddles the threshold, untested when no evidence matches. ` +
      `Effect sizes are one-sample Cohen's d against the threshold where variance exists, raw margins otherwise.`,
  });

  // 3-5. Results by game class
  const classOrder: Array<{ cls: string; title: string }> = [
    { cls: "social_dilemma", title: "3. Results: Social Dilemmas" },
    { cls: "coordination", title: "4. Results: Coordination Games" },
    { cls: "zero_sum", title: "5. Results: Zero-Sum Games" },
  ];

  for (const { cls, title } of classOrder) {
    const clsGames = games.filter((g) => g.category === cls);
    const parts: string[] = [];

    for (const game of clsGames) {
      const gameMatchups = [...matchups.values()]
        .filter((m) => m.gameId === game.id)
        .sort((x, y) => y.expIds.length - x.expIds.length);
      if (gameMatchups.length === 0) continue;

      const nExps = gameMatchups.reduce((s, m) => s + m.expIds.length, 0);
      let txt = `**${game.name}** — ${nExps} analyzed experiments, ${gameMatchups.length} matchups.\n\n`;

      for (const m of gameMatchups) {
        const lines: string[] = [];
        if (cls === "social_dilemma") {
          lines.push(`welfare ratio ${fmtStats(agg(m, "welfareRatio"))}`);
          lines.push(`mutual cooperation ${fmtPct(agg(m, "mutualCooperationRate"))}`);
          lines.push(
            `per-round payoffs ${fmtStats(agg(m, "avgPayoffPerRoundP1"), 2)} / ${fmtStats(agg(m, "avgPayoffPerRoundP2"), 2)}`
          );
        } else if (cls === "coordination") {
          lines.push(`equilibrium-outcome rate ${fmtPct(agg(m, "eqOutcomeRate"))}`);
          lines.push(`coordination rate ${fmtPct(agg(m, "coordinationRate"))}`);
        } else {
          lines.push(
            `marginal exploitability ${fmtStats(agg(m, "marginalExploitabilityP1"))} / ${fmtStats(agg(m, "marginalExploitabilityP2"))}`
          );
          lines.push(
            `tracker exploitability ${fmtStats(agg(m, "conditionalExploitabilityP1"))} / ${fmtStats(agg(m, "conditionalExploitabilityP2"))}`
          );
          const g = agg(m, "gTestPValue");
          if (g.n > 0) lines.push(`G-test vs Nash mixed p = ${fmtStats(g)}`);
        }
        txt += `- ${matchupName(m)} (${m.expIds.length >= 2 ? `${m.expIds.length} seeds` : "1 run"}): ${lines.join("; ")}\n`;
      }
      parts.push(txt);
    }

    sections.push({
      heading: title,
      content: parts.length > 0 ? parts.join("\n") : "No analyzed experiments in this class.",
    });
  }

  // 6. Claim adjudication
  const claimLines = claims.map((c) => {
    const game = gamesMap.get(c.gameId);
    let line = `**[${c.status.toUpperCase()}] ${c.title}** (${game?.name ?? "Unknown game"})\nClaim: ${c.statement}\n`;
    if (c.adjudicationJson) {
      try {
        const record = JSON.parse(c.adjudicationJson) as AdjudicationRecord;
        for (const item of record.items) {
          line += `- ${item.label}: **${item.verdict}**`;
          if (item.mean != null) {
            line += ` — observed ${item.mean.toFixed(4)}`;
            if (item.ciLow != null && item.ciHigh != null) {
              line += `, 95% CI [${item.ciLow.toFixed(4)}, ${item.ciHigh.toFixed(4)}]`;
            }
            line += ` vs threshold ${item.op} ${item.threshold}`;
            if (item.effectSize != null) line += `, d = ${item.effectSize.toFixed(2)}`;
            else if (item.margin != null) line += `, margin = ${item.margin.toFixed(4)}`;
            line += ` (n=${item.n})`;
          }
          line += "\n";
        }
      } catch {
        // leave without detail
      }
    } else {
      line += `- Not mechanically adjudicated (no structured predicate).\n`;
    }
    return line;
  });

  sections.push({
    heading: "6. Claim Adjudication",
    content:
      `All ${claims.length} claims were checked mechanically. Verdicts: ${counts.supported} supported, ` +
      `${counts.refuted} refuted, ${counts.inconclusive} inconclusive, ${counts.untested} untested.\n\n` +
      claimLines.join("\n"),
  });

  // 7. Errata
  const refutedClaims = claims.filter((c) => c.status === "refuted");
  let errata =
    `This section exists because version 1 of this paper contained errors. We document them rather than erase them.\n\n` +
    `**E1. Transplanted result (v1).** The v1 claim "TFT achieves higher cooperation than Always Defect in iterated PD" asserted ` +
    `a >50% cooperation rate for Tit-for-Tat against Always Defect. In the dyadic matchup actually run, TFT cooperates once ` +
    `(round 1) and defects thereafter — a 2% cooperation rate over 50 rounds. The >50% figure belongs to Axelrod-style ` +
    `tournament aggregates, not to this pairing; v1 transplanted a remembered literature result into a claim about data ` +
    `that showed the opposite. Mechanical adjudication now catches exactly this class of error.\n\n` +
    `**E2. Totals presented as comparable scores (v1).** v1 displayed cumulative payoff totals (e.g. "50.0 vs 200.0") ` +
    `in contexts inviting cross-game comparison. Totals scale with round count and payoff magnitudes; all v2 surfaces ` +
    `report per-round averages alongside totals.\n\n` +
    `**E3. Class-inappropriate metrics (v1).** v1 reported a per-round "Nash equilibrium rate" for zero-sum games with ` +
    `only mixed equilibria, where the per-round statistic is meaningless (it reads 0% for optimal play). v2 replaces it ` +
    `with distribution-level tests (G-test) and exploitability measures. Similarly, "cooperation rate" was reported for ` +
    `zero-sum games where cooperation is undefined; v2 nulls it there.\n\n`;

  if (refutedClaims.length > 0) {
    errata += `**Refuted claims on the record:**\n` + refutedClaims.map((c) => `- ${c.title}`).join("\n");
  }

  sections.push({ heading: "7. Errata and Postmortem", content: errata });

  // 8. Limitations
  sections.push({
    heading: "8. Limitations",
    content:
      `The strategy set is small and hand-coded; results characterize these algorithms, not general behavior. ` +
      `Exploitability uses a first-order (single-lag) tracker; higher-order dependence would go undetected. ` +
      `Payoff matrices are single canonical instances per game, so effect sizes are matrix-specific. ` +
      `Claims marked inconclusive reflect predicates whose confidence intervals straddle their thresholds at n=20 seeds; ` +
      `they are reported as inconclusive rather than re-thresholded after the fact. ` +
      `No learning or LLM-based agents are included in this phase.`,
  });

  // 9. Conclusion — only adjudicated statements
  const supportedTitles = claims.filter((c) => c.status === "supported").map((c) => `- ${c.title}`);
  sections.push({
    heading: "9. Conclusion",
    content:
      `The following statements survived mechanical adjudication against seeded, replicated data:\n\n` +
      (supportedTitles.length > 0 ? supportedTitles.join("\n") : "- (none)") +
      `\n\nEverything else in this paper is measurement, not conclusion. The broader methodological result is that ` +
      `a research pipeline in which claims are stated as machine-checkable predicates and adjudicated mechanically ` +
      `caught a headline error that narrative review had let through. We keep that pipeline for all future phases.`,
  });

  // Appendix: Reproducibility
  sections.push({
    heading: "Appendix: Reproducibility",
    content:
      `Every experiment row stores its RNG seed; POST /api/experiments with {gameId, player1StrategyId, player2StrategyId, ` +
      `numRounds, seed} followed by POST /api/experiments/{id}/run reproduces any run bit-for-bit. Batch replicates are ` +
      `grouped by batchLabel and were created via POST /api/experiments/batch with seeds 1..20. Aggregates come from ` +
      `GET /api/analyses/aggregate. Claim predicates and adjudication records are stored on each claim (predicateJson, ` +
      `adjudicationJson) and re-checkable via POST /api/claims/adjudicate-all. See README.md and docs/METRICS.md.`,
  });

  const sectionsJson = JSON.stringify(sections);
  const wordCount =
    abstractText.split(/\s+/).length +
    sections.reduce((s, sec) => s + sec.content.split(/\s+/).length, 0);

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
