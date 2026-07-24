/**
 * Client for the ActiveGraph engine sidecar (internal Python service).
 * The engine owns simulation execution and its own event store; Express
 * remains the only Postgres writer.
 */

import { fetch as undiciFetch, Agent } from "undici";

const ENGINE_URL = process.env.ENGINE_URL ?? "http://127.0.0.1:8090";

/**
 * LLM subject runs make one live model call per decision and can legitimately
 * take many minutes (a 50-round self-play supergame is ~100 calls). The
 * default fetch dispatcher aborts when response headers take >5 minutes,
 * which would mark the experiment failed while the engine keeps making
 * budgeted LLM calls — silently corrupting Phase 3 budget accounting. LLM
 * runs therefore go through a dedicated long-timeout dispatcher.
 */
const llmRunAgent = new Agent({ headersTimeout: 3_600_000, bodyTimeout: 3_600_000 });
const llmRunFetch = ((input: Parameters<typeof undiciFetch>[0], init?: Parameters<typeof undiciFetch>[1]) =>
  undiciFetch(input, { ...init, dispatcher: llmRunAgent })) as unknown as typeof fetch;

export class EngineUnreachableError extends Error {
  constructor(cause: string) {
    super(`Simulation engine is unreachable: ${cause}`);
    this.name = "EngineUnreachableError";
  }
}

export class EngineRequestError extends Error {
  status: number;
  constructor(status: number, detail: string) {
    super(detail);
    this.name = "EngineRequestError";
    this.status = status;
  }
}

export interface EngineGameDef {
  slug: string;
  numActions: number;
  actionLabels: string[];
  payoffMatrix: number[][][];
  nashEquilibria: number[][];
}

export interface EngineRound {
  roundNumber: number;
  player1Action: number;
  player2Action: number;
  player1Payoff: number;
  player2Payoff: number;
  player1Reasoning: string;
  player2Reasoning: string;
  isNashOutcome: boolean;
}

export interface EngineRunResult {
  engineRunId: string;
  seed: number;
  rounds: EngineRound[];
  player1TotalPayoff: number;
  player2TotalPayoff: number;
  cooperationRate: number;
  nashDeviationScore: number;
}

export interface EngineForkResult extends EngineRunResult {
  parentEngineRunId: string;
  forkRound: number;
}

export interface EngineDiffResult {
  parentEngineRunId: string;
  forkEngineRunId: string;
  sharedEvents: number;
  parentOnlyEvents: number;
  forkOnlyEvents: number;
  divergentObjects: number;
  divergentRelations: number;
  isIdentical: boolean;
  divergenceRound: number | null;
  parentRounds: EngineRound[];
  forkRounds: EngineRound[];
  parentSummary: {
    player1TotalPayoff: number;
    player2TotalPayoff: number;
    cooperationRate: number;
    nashDeviationScore: number;
  };
  forkSummary: EngineDiffResult["parentSummary"];
}

export interface EngineTraceEvent {
  eventId: string;
  type: string;
  actor: string | null;
  causedBy: string | null;
  timestamp: string | null;
  roundNumber: number | null;
  payload: Record<string, unknown>;
}

async function engineFetch<T>(
  path: string,
  init?: RequestInit,
  fetchImpl: typeof fetch = fetch
): Promise<T> {
  let res: Response;
  try {
    res = await fetchImpl(`${ENGINE_URL}${path}`, {
      ...init,
      headers: { "Content-Type": "application/json", ...init?.headers },
    });
  } catch (err) {
    throw new EngineUnreachableError(err instanceof Error ? err.message : String(err));
  }
  if (!res.ok) {
    let detail = `engine returned ${res.status}`;
    try {
      const body = (await res.json()) as { detail?: string };
      if (body.detail) detail = body.detail;
    } catch {
      // keep generic detail
    }
    throw new EngineRequestError(res.status, detail);
  }
  return (await res.json()) as T;
}

/** One externally decided move for a "scripted" engine seat (LLM event-sourcing). */
export interface ScriptedMove {
  action: number;
  reasoning?: string | null;
}

export function runOnEngine(input: {
  game: EngineGameDef;
  strategy1Slug: string;
  strategy2Slug: string;
  numRounds: number;
  seed: number;
  scripted1?: ScriptedMove[] | null;
  scripted2?: ScriptedMove[] | null;
}): Promise<EngineRunResult> {
  return engineFetch<EngineRunResult>("/runs", {
    method: "POST",
    body: JSON.stringify(input),
  });
}

export function forkOnEngine(
  parentEngineRunId: string,
  input: {
    forkRound: number;
    strategy1Slug?: string | null;
    strategy2Slug?: string | null;
    scripted1?: ScriptedMove[] | null;
    scripted2?: ScriptedMove[] | null;
  }
): Promise<EngineForkResult> {
  return engineFetch<EngineForkResult>(
    `/runs/${encodeURIComponent(parentEngineRunId)}/fork`,
    { method: "POST", body: JSON.stringify(input) }
  );
}

export function diffOnEngine(
  parentEngineRunId: string,
  forkEngineRunId: string
): Promise<EngineDiffResult> {
  return engineFetch<EngineDiffResult>(
    `/runs/${encodeURIComponent(parentEngineRunId)}/diff/${encodeURIComponent(forkEngineRunId)}`
  );
}

export function traceOnEngine(
  engineRunId: string
): Promise<{ engineRunId: string; events: EngineTraceEvent[] }> {
  return engineFetch(`/runs/${encodeURIComponent(engineRunId)}/trace`);
}

// ── Phase 3: engine-side LLM behavioral runs ───────────────────────────────

/** Subject-protocol parameters passed through to the engine (and stored on the run). */
export interface EngineLlmConfig {
  model: string;
  temperature: number;
  maxTokens: number;
  promptId: string;
  framing?: string;
  deltaPct?: number;
  horizonRule?: string;
}

export interface EngineLlmRunMeta {
  llmCalls: number;
  retriedCalls: number;
  inputTokens: number;
  outputTokens: number;
  model: string;
  temperature: number;
  maxTokens: number;
  promptId: string;
  promptRegistrySha256: string;
}

export interface EngineLlmRunResult {
  engineRunId: string;
  seed: number;
  invalidTrial: boolean;
  rounds: EngineRound[];
  meta: EngineLlmRunMeta;
  // present only when invalidTrial === false:
  player1TotalPayoff?: number;
  player2TotalPayoff?: number;
  cooperationRate?: number;
  nashDeviationScore?: number;
}

export interface EngineLlmReplayResult {
  engineRunId: string;
  ok: boolean;
  invalidTrial: boolean;
  recordedLlmCalls: number;
  llmCallsVerified: number;
  roundsCompared: number;
  liveCalls: number;
  promptRegistrySha256: string;
  /**
   * Informational: present when the append-only prompt registry file has
   * grown since this run was recorded. Per-prompt hash verification (folded
   * into `ok`) remains the authoritative byte-exact check.
   */
  registryFileDrift: { recorded: string | null; current: string; note: string } | null;
  mismatches: string[];
}

export function runLlmOnEngine(input: {
  game: EngineGameDef;
  strategy1Slug: string;
  strategy2Slug: string;
  numRounds: number;
  seed: number;
  llm: EngineLlmConfig;
}): Promise<EngineLlmRunResult> {
  return engineFetch<EngineLlmRunResult>(
    "/llm-runs",
    {
      method: "POST",
      body: JSON.stringify(input),
    },
    llmRunFetch
  );
}

export function replayLlmOnEngine(engineRunId: string): Promise<EngineLlmReplayResult> {
  return engineFetch<EngineLlmReplayResult>(
    `/llm-runs/${encodeURIComponent(engineRunId)}/replay`,
    { method: "POST" }
  );
}

export function getEngineLlmRegistry(): Promise<{
  registryVersion: string;
  sha256: string;
  promptIds: string[];
}> {
  return engineFetch("/llm-registry");
}
