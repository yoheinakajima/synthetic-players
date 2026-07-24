/**
 * Client for the ActiveGraph engine sidecar (internal Python service).
 * The engine owns simulation execution and its own event store; Express
 * remains the only Postgres writer.
 */

const ENGINE_URL = process.env.ENGINE_URL ?? "http://127.0.0.1:8090";

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

async function engineFetch<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${ENGINE_URL}${path}`, {
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
