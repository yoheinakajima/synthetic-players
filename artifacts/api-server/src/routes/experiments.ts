import { Router, type IRouter } from "express";
import { eq, and, isNull, isNotNull } from "drizzle-orm";
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
  ReplayExperimentParams,
  ReplayExperimentResponse,
  RunExperimentBatchBody,
  RunExperimentBatchResponse,
  DeleteExperimentParams,
} from "@workspace/api-zod";
import {
  executeExperiment,
  analyzeExperiment,
  generateSeed,
  withPerRoundAverages,
  engineErrorStatus,
  ensureEngineRun,
  forkExperimentFromParent,
  replayPhase3Experiment,
  parsePhase3Protocol,
  type Phase3Protocol,
  toGameDef,
  EngineDriftError,
} from "../lib/experiment-service";
import { computeForkComparison } from "../lib/fork-metrics";
import { logger } from "../lib/logger";
import { diffOnEngine, traceOnEngine } from "../lib/engine-client";
import {
  ForkExperimentParams,
  ForkExperimentBody,
  ForkExperimentResponse,
  EnsureEngineRunParams,
  EnsureEngineRunResponse,
  ForkExperimentBatchBody,
  ForkExperimentBatchResponse,
  GetExperimentDiffParams,
  GetExperimentDiffResponse,
  GetExperimentTraceParams,
  GetExperimentTraceResponse,
} from "@workspace/api-zod";

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

  // Phase 3 protocol validation at creation time, so a protocol can never be
  // attached to a classic matchup and a Phase 3 subject can never be created
  // without one (the run path re-checks, but failing here is cheaper).
  const llmProtocol = parsed.data.llmProtocol ?? null;
  const hasAiSeat = p1.type === "ai_model" || p2.type === "ai_model";
  if (llmProtocol != null && !hasAiSeat) {
    res.status(400).json({ error: "llmProtocol requires at least one LLM (ai_model) seat" });
    return;
  }
  if (llmProtocol == null && (p1.slug === "llm-gpt-4.1" || p2.slug === "llm-gpt-4.1")) {
    res.status(400).json({
      error:
        "llm-gpt-4.1 is a Phase 3 subject — experiments must be created with llmProtocol (pre-registered design)",
    });
    return;
  }

  try {
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
        llmMetaJson: llmProtocol != null ? JSON.stringify({ protocol: llmProtocol }) : null,
      })
      .returning();
    const detail = await buildExperimentDetail(exp);
    res.status(201).json(CreateExperimentResponse.parse(detail));
  } catch (err) {
    // Replicate-identity conflict (experiments_replicate_identity_idx): a
    // concurrent create raced us to the same (game, strategies, batch, seed).
    // Return the existing row so replicate creation is idempotent instead of
    // 500-ing or spawning a duplicate.
    const code =
      (err as { code?: string })?.code ?? (err as { cause?: { code?: string } })?.cause?.code;
    if (code === "23505" && parsed.data.batchLabel != null && parsed.data.seed != null) {
      const [existing] = await db
        .select()
        .from(experimentsTable)
        .where(
          and(
            eq(experimentsTable.gameId, parsed.data.gameId),
            eq(experimentsTable.player1StrategyId, parsed.data.player1StrategyId),
            eq(experimentsTable.player2StrategyId, parsed.data.player2StrategyId),
            eq(experimentsTable.batchLabel, parsed.data.batchLabel),
            eq(experimentsTable.seed, parsed.data.seed),
            isNull(experimentsTable.parentExperimentId)
          )
        );
      if (existing) {
        // Never silently reuse a row whose stored protocol differs from the
        // one submitted — a resumed runner would run under the WRONG protocol.
        const normalize = (p: Phase3Protocol | null) =>
          p == null
            ? null
            : JSON.stringify({
                promptId: p.promptId,
                temperature: p.temperature,
                maxTokens: p.maxTokens,
                framing: p.framing ?? null,
                deltaPct: p.deltaPct ?? null,
                horizonRule: p.horizonRule ?? null,
              });
        const submitted: Phase3Protocol | null =
          llmProtocol != null
            ? {
                promptId: llmProtocol.promptId,
                temperature: llmProtocol.temperature,
                maxTokens: llmProtocol.maxTokens,
                framing: llmProtocol.framing ?? null,
                deltaPct: llmProtocol.deltaPct ?? null,
                horizonRule: llmProtocol.horizonRule ?? null,
              }
            : null;
        let row = existing;
        if (normalize(parsePhase3Protocol(existing.llmMetaJson)) !== normalize(submitted)) {
          if (existing.status === "pending" || existing.status === "failed") {
            // No evidence produced yet — adopt the submitted protocol so a
            // corrected runner can recover this seed slot.
            const [updated] = await db
              .update(experimentsTable)
              .set({
                llmMetaJson: submitted != null ? JSON.stringify({ protocol: submitted }) : null,
              })
              .where(eq(experimentsTable.id, existing.id))
              .returning();
            row = updated;
          } else {
            res.status(409).json({
              error: `Experiment ${existing.id} already ran (status "${existing.status}") under a different llmProtocol — refusing to reuse or mutate it`,
            });
            return;
          }
        }
        const detail = await buildExperimentDetail(row);
        res.status(200).json(CreateExperimentResponse.parse(detail));
        return;
      }
    }
    throw err;
  }
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

  // LLM seats make one model call per round: a whole batch in one request
  // would run for many minutes and risk client timeouts. Replicate LLM runs
  // one experiment at a time (create + run) instead.
  if (p1.type === "ai_model" || p2.type === "ai_model") {
    res.status(400).json({
      error:
        "Batch runs are not supported for LLM strategies — create and run replicates individually",
    });
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
    let exp;
    try {
      [exp] = await db
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
    } catch (err) {
      // Concurrent batch/runner raced us to this exact (matchup, batch, seed)
      // slot (experiments_replicate_identity_idx). Treat as already-existing.
      const code =
        (err as { code?: string })?.code ?? (err as { cause?: { code?: string } })?.cause?.code;
      if (code === "23505") {
        skippedSeeds.push(seed);
        continue;
      }
      throw err;
    }

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
    // Keep run semantics aligned with the batch route: every completed run
    // gets its v2 analysis immediately, so claims adjudication always sees
    // singly-run experiments (LLM replicates run through this path).
    // Invalid trials (Phase 3 unparseable-response rule) have no rounds and
    // never receive an analysis — they are excluded from evidence by status.
    if (updated.status === "completed") {
      await analyzeExperiment(updated.id);
    }
    const detail = await buildExperimentDetail(updated);
    res.json(RunExperimentResponse.parse(detail));
  } catch (err) {
    const { status, message } = engineErrorStatus(err);
    res.status(status).json({ error: `Experiment execution failed: ${message}` });
  }
});

/**
 * Zero-live-call verification of a completed Phase 3 LLM experiment:
 * engine-side replay from the event-sourced LLM cache + local metric
 * recomputation against the stored analysis. Always 200 with ok:false on
 * verification mismatch (auditing must be able to report every experiment);
 * 400 only when the experiment is not replayable at all.
 */
router.post("/experiments/:id/replay", async (req, res): Promise<void> => {
  const params = ReplayExperimentParams.safeParse(req.params);
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

  try {
    const report = await replayPhase3Experiment(exp.id);
    res.json(ReplayExperimentResponse.parse(report));
  } catch (err) {
    const { status, message } = engineErrorStatus(err);
    // Plain service errors here are precondition failures (not Phase 3 /
    // not completed), not server faults.
    res
      .status(status === 500 ? 400 : status)
      .json({ error: `Replay verification failed: ${message}` });
  }
});

router.post("/experiments/:id/fork", async (req, res): Promise<void> => {
  const params = ForkExperimentParams.safeParse(req.params);
  const body = ForkExperimentBody.safeParse(req.body);
  if (!params.success || !body.success) {
    res.status(400).json({ error: (params.success ? body : params).error!.message });
    return;
  }

  const [parent] = await db
    .select()
    .from(experimentsTable)
    .where(eq(experimentsTable.id, params.data.id));

  if (!parent) {
    res.status(404).json({ error: "Experiment not found" });
    return;
  }
  if (parent.status !== "completed" || !parent.engineRunId) {
    res.status(400).json({ error: "Only completed experiments with an engine run can be forked" });
    return;
  }
  if (body.data.forkRound < 1 || body.data.forkRound > parent.numRounds) {
    res.status(400).json({ error: `forkRound must be between 1 and ${parent.numRounds}` });
    return;
  }

  const p1StrategyId = body.data.player1StrategyId ?? parent.player1StrategyId;
  const p2StrategyId = body.data.player2StrategyId ?? parent.player2StrategyId;
  const [p1Strat] = await db.select().from(strategiesTable).where(eq(strategiesTable.id, p1StrategyId));
  const [p2Strat] = await db.select().from(strategiesTable).where(eq(strategiesTable.id, p2StrategyId));
  if (!p1Strat || !p2Strat) {
    res.status(400).json({ error: "Strategy not found" });
    return;
  }

  try {
    const forkExp = await forkExperimentFromParent(parent, {
      forkRound: body.data.forkRound,
      player1StrategyId: body.data.player1StrategyId,
      player2StrategyId: body.data.player2StrategyId,
      notes: body.data.notes,
    });
    const detail = await buildExperimentDetail(forkExp);
    res.status(201).json(ForkExperimentResponse.parse(detail));
  } catch (err) {
    const { status, message } = engineErrorStatus(err);
    res.status(status).json({ error: `Fork failed: ${message}` });
  }
});

router.post("/experiments/:id/engine-run", async (req, res): Promise<void> => {
  const params = EnsureEngineRunParams.safeParse(req.params);
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

  try {
    const r = await ensureEngineRun(exp.id);
    res.json(
      EnsureEngineRunResponse.parse({
        experimentId: exp.id,
        engineRunId: r.engineRunId,
        alreadyHad: r.alreadyHad,
      })
    );
  } catch (err) {
    if (err instanceof EngineDriftError) {
      logger.error({ experimentId: exp.id, message: err.message }, "engine determinism drift");
      res.status(409).json({ error: err.message });
      return;
    }
    const { status, message } = engineErrorStatus(err);
    res
      .status(status === 500 ? 400 : status)
      .json({ error: `Engine run materialization failed: ${message}` });
  }
});

router.post("/experiments/fork-batch", async (req, res): Promise<void> => {
  const body = ForkExperimentBatchBody.safeParse(req.body);
  if (!body.success) {
    res.status(400).json({ error: body.error.message });
    return;
  }
  const { batchLabel, forkRound, forkBatchLabel, notes } = body.data;

  const parents = await db
    .select()
    .from(experimentsTable)
    .where(
      and(
        eq(experimentsTable.batchLabel, batchLabel),
        eq(experimentsTable.status, "completed"),
        isNull(experimentsTable.parentExperimentId)
      )
    );
  if (parents.length === 0) {
    res.status(400).json({ error: `No completed experiments in batch "${batchLabel}"` });
    return;
  }

  for (const stratId of [body.data.player1StrategyId, body.data.player2StrategyId]) {
    if (stratId != null) {
      const [s] = await db.select().from(strategiesTable).where(eq(strategiesTable.id, stratId));
      if (!s) {
        res.status(400).json({ error: `Strategy ${stratId} not found` });
        return;
      }
    }
  }

  // Idempotency: a parent is skipped when a completed fork with the same
  // round, strategies, and fork batch label already exists.
  const existingForks = await db
    .select()
    .from(experimentsTable)
    .where(
      and(
        eq(experimentsTable.batchLabel, forkBatchLabel),
        isNotNull(experimentsTable.parentExperimentId)
      )
    );

  const created: number[] = [];
  const skippedParents: number[] = [];
  const failed: Array<{ parentExperimentId: number; error: string }> = [];

  for (const parent of parents) {
    const p1Id = body.data.player1StrategyId ?? parent.player1StrategyId;
    const p2Id = body.data.player2StrategyId ?? parent.player2StrategyId;
    const dup = existingForks.find(
      (f) =>
        f.parentExperimentId === parent.id &&
        f.forkRound === forkRound &&
        f.player1StrategyId === p1Id &&
        f.player2StrategyId === p2Id &&
        f.status === "completed"
    );
    if (dup) {
      skippedParents.push(parent.id);
      continue;
    }
    try {
      const ensured = await ensureEngineRun(parent.id);
      const forkExp = await forkExperimentFromParent(ensured.exp, {
        forkRound,
        player1StrategyId: body.data.player1StrategyId,
        player2StrategyId: body.data.player2StrategyId,
        batchLabel: forkBatchLabel,
        notes: notes ?? `Fork of EXP-${parent.id} at round ${forkRound} [${forkBatchLabel}]`,
      });
      created.push(forkExp.id);
    } catch (err) {
      failed.push({
        parentExperimentId: parent.id,
        error: err instanceof Error ? err.message : "Unknown error",
      });
    }
  }

  logger.info(
    { forkBatchLabel, created: created.length, skipped: skippedParents.length, failed: failed.length },
    "fork batch finished"
  );
  res.json(
    ForkExperimentBatchResponse.parse({ forkBatchLabel, created, skippedParents, failed })
  );
});

router.get("/experiments/:id/diff", async (req, res): Promise<void> => {
  const params = GetExperimentDiffParams.safeParse(req.params);
  if (!params.success) {
    res.status(400).json({ error: params.error.message });
    return;
  }

  const [fork] = await db
    .select()
    .from(experimentsTable)
    .where(eq(experimentsTable.id, params.data.id));

  if (!fork) {
    res.status(404).json({ error: "Experiment not found" });
    return;
  }
  if (fork.parentExperimentId == null || fork.forkRound == null || !fork.engineRunId) {
    res.status(400).json({ error: "Experiment is not a fork with an engine run" });
    return;
  }

  const [parent] = await db
    .select()
    .from(experimentsTable)
    .where(eq(experimentsTable.id, fork.parentExperimentId));

  if (!parent?.engineRunId) {
    res.status(400).json({ error: "Parent experiment has no engine run" });
    return;
  }

  try {
    const d = await diffOnEngine(parent.engineRunId, fork.engineRunId);

    // Paired post-fork-window metrics — the evidence-grade fork comparison.
    let postForkWindow: ReturnType<typeof computeForkComparison> | undefined;
    try {
      const [gameRow] = await db.select().from(gamesTable).where(eq(gamesTable.id, fork.gameId));
      if (gameRow) {
        postForkWindow = computeForkComparison(
          toGameDef(gameRow),
          d.parentRounds,
          d.forkRounds,
          fork.forkRound
        );
      }
    } catch (err) {
      logger.warn(
        { forkId: fork.id, error: err instanceof Error ? err.message : String(err) },
        "post-fork window metrics unavailable"
      );
    }

    res.json(
      GetExperimentDiffResponse.parse({
        forkExperimentId: fork.id,
        parentExperimentId: parent.id,
        forkRound: fork.forkRound,
        divergenceRound: d.divergenceRound,
        sharedEvents: d.sharedEvents,
        parentOnlyEvents: d.parentOnlyEvents,
        forkOnlyEvents: d.forkOnlyEvents,
        divergentObjects: d.divergentObjects,
        divergentRelations: d.divergentRelations,
        isIdentical: d.isIdentical,
        parentRounds: d.parentRounds,
        forkRounds: d.forkRounds,
        parentSummary: d.parentSummary,
        forkSummary: d.forkSummary,
        ...(postForkWindow ? { postForkWindow } : {}),
      })
    );
  } catch (err) {
    const { status, message } = engineErrorStatus(err);
    res.status(status).json({ error: `Diff failed: ${message}` });
  }
});

router.get("/experiments/:id/trace", async (req, res): Promise<void> => {
  const params = GetExperimentTraceParams.safeParse(req.params);
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
  if (!exp.engineRunId) {
    res.status(400).json({ error: "Experiment has no engine run yet" });
    return;
  }

  try {
    const t = await traceOnEngine(exp.engineRunId);
    res.json(
      GetExperimentTraceResponse.parse({
        experimentId: exp.id,
        engineRunId: t.engineRunId,
        events: t.events.map((e) => {
          const p = e.payload ?? {};
          return {
            eventId: e.eventId,
            type: e.type,
            actor: e.actor,
            causedBy: e.causedBy,
            timestamp: e.timestamp,
            roundNumber: e.roundNumber,
            player1Action: (p.player1Action as number | undefined) ?? null,
            player2Action: (p.player2Action as number | undefined) ?? null,
            player1Reasoning: (p.player1Reasoning as string | undefined) ?? null,
            player2Reasoning: (p.player2Reasoning as string | undefined) ?? null,
            strategy1Slug: (p.strategy1Slug as string | undefined) ?? null,
            strategy2Slug: (p.strategy2Slug as string | undefined) ?? null,
          };
        }),
      })
    );
  } catch (err) {
    const { status, message } = engineErrorStatus(err);
    res.status(status).json({ error: `Trace failed: ${message}` });
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
