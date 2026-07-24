/**
 * Shared experiment execution + analysis service.
 * Used by both the single-run route and the seeded batch runner so the
 * execution path is identical everywhere.
 */

import { eq, asc, and, inArray } from "drizzle-orm";
import type { Strategy } from "@workspace/db";
import type { EngineRunResult } from "./engine-client";
import { playLlmLiveLoop, type SeatSpec } from "./llm-player";
import {
  db,
  experimentsTable,
  gamesTable,
  strategiesTable,
  roundsTable,
  analysesTable,
} from "@workspace/db";
import { computeAnalysis, type GameDef } from "./game-engine";
import {
  runOnEngine,
  forkOnEngine,
  runLlmOnEngine,
  replayLlmOnEngine,
  EngineUnreachableError,
  EngineRequestError,
  type EngineLlmReplayResult,
} from "./engine-client";
import { computeMetricsV2, flattenMetrics, type MetricsV2 } from "./metrics";
import { invalidateEvidenceCache } from "./adjudicator";

/**
 * Structured payload the engine embeds in a mid-run LLM failure (llm_runner
 * wraps unexpected exceptions as JSON so partial provider spend stays
 * auditable). Returns null for any other error shape.
 */
interface EnginePartialSpend {
  error: string;
  engineRunId: string | null;
  llmCalls: number;
  inputTokens: number | null;
  outputTokens: number | null;
}

function parseEnginePartialSpend(err: unknown): EnginePartialSpend | null {
  if (!(err instanceof EngineRequestError)) return null;
  try {
    const raw = JSON.parse(err.message) as Record<string, unknown>;
    if (raw?.partial !== true || typeof raw.llmCalls !== "number") return null;
    return {
      error: typeof raw.error === "string" ? raw.error : "unknown engine failure",
      engineRunId: typeof raw.engineRunId === "string" ? raw.engineRunId : null,
      llmCalls: raw.llmCalls,
      inputTokens: typeof raw.inputTokens === "number" ? raw.inputTokens : null,
      outputTokens: typeof raw.outputTokens === "number" ? raw.outputTokens : null,
    };
  } catch {
    return null;
  }
}

/** Stored rounds and a fresh engine replay disagree — determinism is broken somewhere. */
export class EngineDriftError extends Error {
  roundNumber: number;
  constructor(expId: number, roundNumber: number, detail: string) {
    super(
      `Engine drift on experiment ${expId} at round ${roundNumber}: ${detail}. ` +
        `Stored data was NOT modified — investigate before re-running.`
    );
    this.name = "EngineDriftError";
    this.roundNumber = roundNumber;
  }
}

/** A run was requested for an experiment already running or completed (lost the acquire race). */
export class ExperimentBusyError extends Error {
  constructor(expId: number) {
    super(`Experiment ${expId} is already running or completed`);
    this.name = "ExperimentBusyError";
  }
}

/** Map engine failures to an HTTP status + message (502 when the sidecar is down). */
export function engineErrorStatus(err: unknown): { status: number; message: string } {
  if (err instanceof ExperimentBusyError) return { status: 409, message: err.message };
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

// ── Phase 3: engine-live LLM subject protocol ──────────────────────────────

/** Subject protocol stored under llmMetaJson.protocol at experiment creation. */
export interface Phase3Protocol {
  promptId: string;
  temperature: number;
  maxTokens: number;
  framing?: string | null;
  deltaPct?: number | null;
  horizonRule?: string | null;
}

/**
 * Extract the Phase 3 protocol from llmMetaJson. Returns null for non-Phase-3
 * rows (no "protocol" key — e.g. Track 2 runMeta or classic experiments).
 * A PRESENT but malformed protocol throws: silently downgrading a Phase 3
 * experiment to the legacy path would corrupt the pre-registered design.
 */
export function parsePhase3Protocol(llmMetaJson: string | null): Phase3Protocol | null {
  if (!llmMetaJson) return null;
  let parsed: unknown;
  try {
    parsed = JSON.parse(llmMetaJson);
  } catch {
    return null;
  }
  if (parsed == null || typeof parsed !== "object" || !("protocol" in parsed)) return null;
  const p = (parsed as { protocol: unknown }).protocol;
  if (p == null || typeof p !== "object")
    throw new Error("llmMetaJson.protocol is present but not an object");
  const proto = p as Record<string, unknown>;
  if (
    typeof proto.promptId !== "string" ||
    typeof proto.temperature !== "number" ||
    typeof proto.maxTokens !== "number"
  ) {
    throw new Error(
      "llmMetaJson.protocol is malformed: promptId (string), temperature (number) and maxTokens (number) are required"
    );
  }
  return {
    promptId: proto.promptId,
    temperature: proto.temperature,
    maxTokens: proto.maxTokens,
    framing: typeof proto.framing === "string" ? proto.framing : null,
    deltaPct: typeof proto.deltaPct === "number" ? proto.deltaPct : null,
    horizonRule: typeof proto.horizonRule === "string" ? proto.horizonRule : null,
  };
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

  // Atomically acquire the run: only a pending/failed experiment can move to
  // "running", and only one caller wins this conditional update. Without the
  // CAS, two concurrent /run requests could both execute the same experiment
  // — for LLM seats that means two different sampled trajectories, with the
  // loser overwriting the winner (or a late failure flipping a completed run
  // back to failed). The route's status pre-check is a fast path; this is the
  // authoritative guard.
  const acquired = await db
    .update(experimentsTable)
    .set({ status: "running", errorMessage: null })
    .where(
      and(
        eq(experimentsTable.id, exp.id),
        inArray(experimentsTable.status, ["pending", "failed"])
      )
    )
    .returning({ id: experimentsTable.id });
  if (acquired.length === 0) throw new ExperimentBusyError(exp.id);

  // Ensure a persisted seed BEFORE running, so every run is reproducible.
  let seed = exp.seed;
  if (seed == null) {
    seed = generateSeed();
    await db.update(experimentsTable).set({ seed }).where(eq(experimentsTable.id, exp.id));
  }

  try {
    const gameDef = toGameDef(game);
    let result: EngineRunResult;
    let llmMetaJson: string | null = null;

    const protocol = parsePhase3Protocol(exp.llmMetaJson);
    const hasAiSeat = p1Strat.type === "ai_model" || p2Strat.type === "ai_model";

    if (hasAiSeat && protocol != null) {
      // Phase 3 subject run: the ENGINE drives the LLM loop and event-sources
      // every prompt/response (llm.requested / llm.responded) for
      // zero-live-call replay verification. Express only persists results.
      const subject = p1Strat.type === "ai_model" ? p1Strat : p2Strat;
      if (!subject.modelId)
        throw new Error(`AI strategy "${subject.slug}" has no modelId configured`);
      if (
        p1Strat.type === "ai_model" &&
        p2Strat.type === "ai_model" &&
        p1Strat.modelId !== p2Strat.modelId
      )
        throw new Error("Phase 3 self-play requires the same model in both seats");

      let llmRun: Awaited<ReturnType<typeof runLlmOnEngine>>;
      try {
        llmRun = await runLlmOnEngine({
          game: gameDef,
          strategy1Slug: p1Strat.type === "ai_model" ? "llm-subject" : p1Strat.slug,
          strategy2Slug: p2Strat.type === "ai_model" ? "llm-subject" : p2Strat.slug,
          numRounds: exp.numRounds,
          seed,
          llm: {
            model: subject.modelId,
            temperature: protocol.temperature,
            maxTokens: protocol.maxTokens,
            promptId: protocol.promptId,
            ...(protocol.framing != null ? { framing: protocol.framing } : {}),
            ...(protocol.deltaPct != null ? { deltaPct: protocol.deltaPct } : {}),
            ...(protocol.horizonRule != null ? { horizonRule: protocol.horizonRule } : {}),
          },
        });
      } catch (engineErr) {
        const partial = parseEnginePartialSpend(engineErr);
        if (partial) {
          // The engine failed mid-run but reported the provider calls it had
          // already made. Persist that spend BEFORE the generic failure
          // handler marks the row failed: the Phase 3 runner sums
          // runMeta.llmCalls over ALL statuses, so burned calls stay visible
          // to budget accounting even on failure.
          await db
            .update(experimentsTable)
            .set({
              engineRunId: partial.engineRunId,
              llmMetaJson: JSON.stringify({
                protocol,
                runMeta: {
                  llmCalls: partial.llmCalls,
                  inputTokens: partial.inputTokens,
                  outputTokens: partial.outputTokens,
                  partial: true,
                },
              }),
            })
            .where(eq(experimentsTable.id, exp.id));
          throw new Error(
            `Engine LLM run failed after ${partial.llmCalls} provider call(s) — ` +
              `spend persisted on the failed row: ${partial.error}`
          );
        }
        throw engineErr;
      }

      if (llmRun.invalidTrial) {
        // Pre-registered invalid-trial rule: unparseable subject response
        // after one retry. No rounds are stored, the row is excluded from
        // evidence (status filter) and its seed is dead — the Phase 3 runner
        // substitutes a replacement seed (1000+k). Calls made before
        // invalidation still count against the budget via runMeta.llmCalls.
        await db.delete(roundsTable).where(eq(roundsTable.experimentId, exp.id));
        const [invalidRow] = await db
          .update(experimentsTable)
          .set({
            status: "invalid",
            engineRunId: llmRun.engineRunId,
            player1TotalPayoff: null,
            player2TotalPayoff: null,
            cooperationRate: null,
            nashDeviationScore: null,
            llmMetaJson: JSON.stringify({ protocol, runMeta: llmRun.meta }),
            completedAt: null,
            errorMessage:
              "Invalid trial: subject response unparseable after one retry (pre-registered exclusion rule)",
          })
          .where(eq(experimentsTable.id, exp.id))
          .returning();
        invalidateEvidenceCache();
        return invalidRow;
      }

      if (
        llmRun.player1TotalPayoff == null ||
        llmRun.player2TotalPayoff == null ||
        llmRun.cooperationRate == null ||
        llmRun.nashDeviationScore == null
      )
        throw new Error("Engine returned a valid LLM trial without summary totals");

      result = {
        engineRunId: llmRun.engineRunId,
        seed: llmRun.seed,
        rounds: llmRun.rounds,
        player1TotalPayoff: llmRun.player1TotalPayoff,
        player2TotalPayoff: llmRun.player2TotalPayoff,
        cooperationRate: llmRun.cooperationRate,
        nashDeviationScore: llmRun.nashDeviationScore,
      };
      llmMetaJson = JSON.stringify({ protocol, runMeta: llmRun.meta });
    } else if (hasAiSeat) {
      // Track 2 legacy path (Node-driven live loop + scripted materialization).
      // Phase 3 subjects must never take it: their design requires the
      // engine-side event log, registry prompts and the invalid-trial rule.
      if (p1Strat.slug === "llm-gpt-4.1" || p2Strat.slug === "llm-gpt-4.1")
        throw new Error(
          "llm-gpt-4.1 is a Phase 3 subject: create the experiment with llmProtocol " +
            "(stored as llmMetaJson.protocol) — ad-hoc runs are refused to protect the pre-registered design"
        );
      const llmRun = await runLlmExperiment({
        gameDef: { ...gameDef, name: game.name },
        p1Strat,
        p2Strat,
        numRounds: exp.numRounds,
        seed,
      });
      result = llmRun.result;
      llmMetaJson = llmRun.llmMetaJson;
    } else {
      // Simulation runs on the ActiveGraph engine sidecar. If the engine is
      // unreachable this throws before any rounds are persisted.
      result = await runOnEngine({
        game: gameDef,
        strategy1Slug: p1Strat.slug,
        strategy2Slug: p2Strat.slug,
        numRounds: exp.numRounds,
        seed,
      });
    }

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
        llmMetaJson,
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
 * Ensure a completed pre-engine experiment has an engine run, by replaying it
 * on the engine with its stored seed and verifying the replay reproduces the
 * stored rounds EXACTLY before persisting engineRunId. On any mismatch this
 * throws EngineDriftError and writes nothing — a silent near-match would
 * corrupt fork lineage. Doubles as a determinism drift detector.
 */
export async function ensureEngineRun(
  expId: number
): Promise<{ exp: ExperimentRow; engineRunId: string; alreadyHad: boolean; }> {
  const [exp] = await db.select().from(experimentsTable).where(eq(experimentsTable.id, expId));
  if (!exp) throw new Error(`Experiment ${expId} not found`);
  if (exp.engineRunId) return { exp, engineRunId: exp.engineRunId, alreadyHad: true };
  if (exp.status !== "completed")
    throw new Error(`Experiment ${expId} is not completed — run it instead`);
  if (exp.seed == null)
    throw new Error(
      `Experiment ${expId} is an unseeded legacy run — it cannot be reproduced on the engine`
    );

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

  const stored = await db
    .select()
    .from(roundsTable)
    .where(eq(roundsTable.experimentId, exp.id))
    .orderBy(asc(roundsTable.roundNumber));
  if (stored.length !== exp.numRounds)
    throw new Error(
      `Experiment ${expId} has ${stored.length} stored rounds, expected ${exp.numRounds}`
    );

  // LLM (ai_model) seats are event-sourced, not seed-derived: rematerialize
  // them from the stored decision log as scripted engine seats. Classic seats
  // replay from the seed as usual. The exact-match check below applies either
  // way, so a corrupted decision log can never be linked to an engine run.
  const p1Scripted = p1Strat.type === "ai_model";
  const p2Scripted = p2Strat.type === "ai_model";
  const asMoves = (which: 1 | 2) =>
    stored.map((r) => ({
      action: which === 1 ? r.player1Action : r.player2Action,
      reasoning: which === 1 ? r.player1Reasoning : r.player2Reasoning,
    }));
  const result = await runOnEngine({
    game: toGameDef(game),
    strategy1Slug: p1Scripted ? "scripted" : p1Strat.slug,
    strategy2Slug: p2Scripted ? "scripted" : p2Strat.slug,
    numRounds: exp.numRounds,
    seed: exp.seed,
    scripted1: p1Scripted ? asMoves(1) : undefined,
    scripted2: p2Scripted ? asMoves(2) : undefined,
  });

  for (let i = 0; i < stored.length; i++) {
    const s = stored[i];
    const r = result.rounds[i];
    if (!r || r.roundNumber !== s.roundNumber)
      throw new EngineDriftError(expId, s.roundNumber, "round sequence mismatch");
    if (r.player1Action !== s.player1Action || r.player2Action !== s.player2Action)
      throw new EngineDriftError(
        expId,
        s.roundNumber,
        `actions stored (${s.player1Action},${s.player2Action}) vs replay (${r.player1Action},${r.player2Action})`
      );
    if (r.player1Payoff !== s.player1Payoff || r.player2Payoff !== s.player2Payoff)
      throw new EngineDriftError(
        expId,
        s.roundNumber,
        `payoffs stored (${s.player1Payoff},${s.player2Payoff}) vs replay (${r.player1Payoff},${r.player2Payoff})`
      );
  }

  await db
    .update(experimentsTable)
    .set({ engineRunId: result.engineRunId })
    .where(eq(experimentsTable.id, exp.id));
  return { exp: { ...exp, engineRunId: result.engineRunId }, engineRunId: result.engineRunId, alreadyHad: false };
}

/**
 * Fork a completed engine-backed experiment at a round, optionally swapping
 * either seat's strategy. Persists the fork experiment + rounds and
 * invalidates evidence caches (fork pairs are adjudication evidence).
 */
export async function forkExperimentFromParent(
  parent: ExperimentRow,
  opts: {
    forkRound: number;
    player1StrategyId?: number | null;
    player2StrategyId?: number | null;
    notes?: string | null;
    batchLabel?: string | null;
  }
): Promise<ExperimentRow> {
  if (parent.status !== "completed" || !parent.engineRunId)
    throw new Error("Only completed experiments with an engine run can be forked");
  if (opts.forkRound < 1 || opts.forkRound > parent.numRounds)
    throw new Error(`forkRound must be between 1 and ${parent.numRounds}`);

  const p1StrategyId = opts.player1StrategyId ?? parent.player1StrategyId;
  const p2StrategyId = opts.player2StrategyId ?? parent.player2StrategyId;
  const [p1Strat] = await db
    .select()
    .from(strategiesTable)
    .where(eq(strategiesTable.id, p1StrategyId));
  const [p2Strat] = await db
    .select()
    .from(strategiesTable)
    .where(eq(strategiesTable.id, p2StrategyId));
  if (!p1Strat || !p2Strat) throw new Error("Strategy not found");

  // Event-sourced (LLM) seats cannot exist on forks: replaying an LLM's
  // recorded moves against a different unfolding history would fabricate
  // decisions the model never made for that context, and running the model
  // live mid-fork is a Track 3 concern. Every fork seat must be classic.
  if (p1Strat.type === "ai_model" || p2Strat.type === "ai_model")
    throw new Error(
      "Forks cannot have an LLM seat — swap every LLM seat to a classic strategy " +
        "(replaying recorded LLM moves against a changed history would fabricate decisions)"
    );

  const result = await forkOnEngine(parent.engineRunId, {
    forkRound: opts.forkRound,
    strategy1Slug: p1Strat.slug,
    strategy2Slug: p2Strat.slug,
  });

  let forkExp: ExperimentRow;
  try {
    [forkExp] = await db
      .insert(experimentsTable)
      .values({
        gameId: parent.gameId,
        player1StrategyId: p1StrategyId,
        player2StrategyId: p2StrategyId,
        numRounds: parent.numRounds,
        seed: parent.seed,
        batchLabel: opts.batchLabel ?? null,
        engineRunId: result.engineRunId,
        parentExperimentId: parent.id,
        forkRound: opts.forkRound,
        status: "completed",
        player1TotalPayoff: result.player1TotalPayoff,
        player2TotalPayoff: result.player2TotalPayoff,
        cooperationRate: result.cooperationRate,
        nashDeviationScore: result.nashDeviationScore,
        completedAt: new Date(),
        notes: opts.notes ?? `Fork of EXP-${parent.id} at round ${opts.forkRound}`,
      })
      .returning();
  } catch (err) {
    // Unique fork-identity violation (experiments_fork_identity_idx): a
    // concurrent identical fork won the race. Forks are deterministic given
    // (parent, round, strategies), so the existing row IS this fork — return
    // it instead of failing, making labeled fork creation truly idempotent.
    const code =
      (err as { code?: string })?.code ??
      (err as { cause?: { code?: string } })?.cause?.code;
    if (code === "23505" && opts.batchLabel != null) {
      const [existing] = await db
        .select()
        .from(experimentsTable)
        .where(
          and(
            eq(experimentsTable.parentExperimentId, parent.id),
            eq(experimentsTable.forkRound, opts.forkRound),
            eq(experimentsTable.player1StrategyId, p1StrategyId),
            eq(experimentsTable.player2StrategyId, p2StrategyId),
            eq(experimentsTable.batchLabel, opts.batchLabel)
          )
        );
      if (existing) return existing;
    }
    throw err;
  }

  await db.insert(roundsTable).values(
    result.rounds.map((r) => ({
      experimentId: forkExp.id,
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

  invalidateEvidenceCache();
  return forkExp;
}

export class LlmMaterializationError extends Error {
  constructor(message: string) {
    super(`LLM run materialization failed: ${message}`);
    this.name = "LlmMaterializationError";
  }
}

/**
 * Execute an experiment with at least one LLM seat: live loop first (the
 * model decides each round with full history), then an engine run with the
 * decision log as scripted seat(s), verified round-by-round against the live
 * loop. The engine result is authoritative; any divergence (e.g. opponent
 * predictor drift) fails the experiment rather than persisting a near-match.
 */
async function runLlmExperiment(input: {
  gameDef: ReturnType<typeof toGameDef> & { name?: string };
  p1Strat: Strategy;
  p2Strat: Strategy;
  numRounds: number;
  seed: number;
}): Promise<{ result: EngineRunResult; llmMetaJson: string }> {
  const { gameDef, p1Strat, p2Strat, numRounds, seed } = input;

  const seat = (s: Strategy): SeatSpec => {
    if (s.type !== "ai_model") return { kind: "classic", slug: s.slug };
    if (!s.modelId) throw new Error(`AI strategy "${s.slug}" has no modelId configured`);
    return { kind: "llm", model: s.modelId, strategySlug: s.slug };
  };

  const live = await playLlmLiveLoop({
    game: gameDef,
    seats: { p1: seat(p1Strat), p2: seat(p2Strat) },
    numRounds,
  });

  const result = await runOnEngine({
    game: gameDef,
    strategy1Slug: p1Strat.type === "ai_model" ? "scripted" : p1Strat.slug,
    strategy2Slug: p2Strat.type === "ai_model" ? "scripted" : p2Strat.slug,
    numRounds,
    seed,
    scripted1: live.p1Moves ?? undefined,
    scripted2: live.p2Moves ?? undefined,
  });

  if (result.rounds.length !== live.history.length)
    throw new LlmMaterializationError(
      `engine produced ${result.rounds.length} rounds, live loop played ${live.history.length}`
    );
  for (let i = 0; i < live.history.length; i++) {
    const l = live.history[i];
    const r = result.rounds[i];
    if (r.player1Action !== l.p1Action || r.player2Action !== l.p2Action)
      throw new LlmMaterializationError(
        `round ${r.roundNumber}: live actions (${l.p1Action},${l.p2Action}) vs engine ` +
          `(${r.player1Action},${r.player2Action}) — opponent predictor drift`
      );
    if (r.player1Payoff !== l.p1Payoff || r.player2Payoff !== l.p2Payoff)
      throw new LlmMaterializationError(
        `round ${r.roundNumber}: payoffs live (${l.p1Payoff},${l.p2Payoff}) vs engine ` +
          `(${r.player1Payoff},${r.player2Payoff})`
      );
  }

  return { result, llmMetaJson: JSON.stringify(live.meta) };
}

export interface Phase3ReplayReport {
  experimentId: number;
  engineRunId: string;
  ok: boolean;
  llm: Omit<EngineLlmReplayResult, "engineRunId">;
  metrics: { match: boolean; mismatches: string[] };
}

/**
 * Verify a completed Phase 3 experiment end to end WITHOUT any live LLM call:
 *   1. Engine replay — re-renders every prompt from the registry + stored
 *      actions, replays responses from the event-sourced LLM cache, re-parses,
 *      recomputes deterministic seats, and compares to stored rounds.
 *   2. Metric recomputation — recomputes metricsV2 from stored DB rounds and
 *      compares byte-for-byte against the stored analysis JSON.
 * Returns ok=false with itemized mismatches rather than throwing, so audits
 * can report on every experiment (HTTP 200 either way).
 */
export async function replayPhase3Experiment(expId: number): Promise<Phase3ReplayReport> {
  const [exp] = await db.select().from(experimentsTable).where(eq(experimentsTable.id, expId));
  if (!exp) throw new Error(`Experiment ${expId} not found`);
  const protocol = parsePhase3Protocol(exp.llmMetaJson);
  if (protocol == null)
    throw new Error(
      `Experiment ${expId} is not a Phase 3 LLM experiment (no llmMetaJson.protocol)`
    );
  if (exp.status !== "completed" || !exp.engineRunId)
    throw new Error(
      `Experiment ${expId} has status "${exp.status}"${exp.engineRunId ? "" : " and no engine run"} — only completed Phase 3 runs can be replay-verified`
    );

  const llmFull = await replayLlmOnEngine(exp.engineRunId);
  const { engineRunId: _ignored, ...llm } = llmFull;

  const mismatches: string[] = [];
  let match = false;
  const [game] = await db.select().from(gamesTable).where(eq(gamesTable.id, exp.gameId));
  const [analysis] = await db
    .select()
    .from(analysesTable)
    .where(eq(analysesTable.experimentId, exp.id));
  const rounds = await db
    .select()
    .from(roundsTable)
    .where(eq(roundsTable.experimentId, exp.id))
    .orderBy(asc(roundsTable.roundNumber));

  if (!game) {
    mismatches.push("game row missing");
  } else if (rounds.length === 0) {
    mismatches.push("no stored rounds");
  } else if (!analysis?.metricsJson || analysis.analysisVersion < 2) {
    mismatches.push("no stored v2 analysis to compare");
  } else {
    const recomputed = computeMetricsV2(toGameDef(game), rounds);
    match = JSON.stringify(recomputed) === analysis.metricsJson;
    if (!match) {
      const a = flattenMetrics(recomputed);
      const b = flattenMetrics(JSON.parse(analysis.metricsJson) as MetricsV2);
      for (const key of new Set([...Object.keys(a), ...Object.keys(b)])) {
        if (a[key] !== b[key]) {
          mismatches.push(`${key}: recomputed ${a[key]} vs stored ${b[key]}`);
          if (mismatches.length >= 20) break;
        }
      }
      if (mismatches.length === 0)
        mismatches.push("non-scalar metric fields differ (exact JSON mismatch)");
    }
  }

  return {
    experimentId: exp.id,
    engineRunId: exp.engineRunId,
    ok: llm.ok && match,
    llm,
    metrics: { match, mismatches },
  };
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
  // Service-level guard (route also rejects): fork-lineage experiments are
  // exploratory hybrids and must never receive analysis rows — analyses are
  // the evidence pool for claim adjudication.
  if (exp.parentExperimentId != null)
    throw new Error(
      `Experiment ${expId} is a fork — forks are exploratory and excluded from evidence`
    );

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
