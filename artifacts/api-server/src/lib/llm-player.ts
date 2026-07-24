/**
 * LLM strategy player: makes one decision per round via the Replit AI
 * Integrations OpenAI proxy, with the full game history in context.
 *
 * Reproducibility class: LLM runs are NOT seed-reproducible (the provider
 * pins temperature = 1 for gpt-5 family models). Instead they are
 * EVENT-SOURCED: every decision (action + stated reasoning) is recorded and
 * materialized on the ActiveGraph engine as a "scripted" seat, so the exact
 * run replays and forks byte-identically from its event log. Scientific
 * claims about LLM behavior therefore always need replicate batches + CIs.
 */

import { openai } from "@workspace/integrations-openai-ai-server";
import { isRateLimitError } from "@workspace/integrations-openai-ai-server/batch";
import type { GameDef } from "./game-engine";
import type { ScriptedMove } from "./engine-client";
import { PREDICTABLE_OPPONENTS, predictOpponentAction, type LiveRound } from "./opponent-predictor";

export const LLM_PROMPT_VERSION = "iterated-game-player-v1";
const MAX_ATTEMPTS = 4;

export class LlmDecisionError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "LlmDecisionError";
  }
}

export interface LlmSeatSpec {
  kind: "llm";
  model: string;
  strategySlug: string;
}
export interface ClassicSeatSpec {
  kind: "classic";
  slug: string;
}
export type SeatSpec = LlmSeatSpec | ClassicSeatSpec;

export interface LlmRunMeta {
  models: Record<string, string>; // seat ("p1"/"p2") → model id
  promptVersion: string;
  temperature: string; // provider-controlled for gpt-5 family
  horizonDisclosed: boolean;
  llmCalls: number;
  promptTokens: number;
  completionTokens: number;
  retriedCalls: number;
}

export interface LiveLoopResult {
  history: LiveRound[];
  p1Moves: ScriptedMove[] | null;
  p2Moves: ScriptedMove[] | null;
  meta: LlmRunMeta;
}

function describeMatrixForSeat(game: GameDef, playerNum: 1 | 2): string {
  const lines: string[] = [];
  for (let mine = 0; mine < game.numActions; mine++) {
    for (let theirs = 0; theirs < game.numActions; theirs++) {
      const cell =
        playerNum === 1 ? game.payoffMatrix[mine][theirs] : game.payoffMatrix[theirs][mine];
      const my = playerNum === 1 ? cell[0] : cell[1];
      const their = playerNum === 1 ? cell[1] : cell[0];
      lines.push(
        `If you play ${mine} (${game.actionLabels[mine]}) and they play ${theirs} (${game.actionLabels[theirs]}): you get ${my}, they get ${their}.`
      );
    }
  }
  return lines.join("\n");
}

function historyForSeat(history: LiveRound[], playerNum: 1 | 2): string {
  if (history.length === 0) return "No rounds have been played yet.";
  return history
    .map((r, i) => {
      const my = playerNum === 1 ? r.p1Action : r.p2Action;
      const their = playerNum === 1 ? r.p2Action : r.p1Action;
      const myPay = playerNum === 1 ? r.p1Payoff : r.p2Payoff;
      const theirPay = playerNum === 1 ? r.p2Payoff : r.p1Payoff;
      return `Round ${i + 1}: you played ${my}, opponent played ${their} → you got ${myPay}, they got ${theirPay}.`;
    })
    .join("\n");
}

function extractJsonObject(text: string): { action: unknown; reasoning?: unknown } {
  const cleaned = text.replace(/```(?:json)?/gi, "").trim();
  const start = cleaned.indexOf("{");
  const end = cleaned.lastIndexOf("}");
  if (start === -1 || end <= start) throw new LlmDecisionError(`no JSON object in reply: ${text.slice(0, 200)}`);
  return JSON.parse(cleaned.slice(start, end + 1)) as { action: unknown; reasoning?: unknown };
}

const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

interface DecideResult {
  action: number;
  reasoning: string;
  promptTokens: number;
  completionTokens: number;
  attempts: number;
}

export async function decideLlmMove(input: {
  game: GameDef & { name?: string };
  history: LiveRound[];
  playerNum: 1 | 2;
  model: string;
  numRounds: number;
}): Promise<DecideResult> {
  const { game, history, playerNum, model, numRounds } = input;
  const roundNum = history.length + 1;

  const system = [
    `You are Player ${playerNum} in an iterated two-player game: ${game.name ?? game.slug}.`,
    `Both players choose actions simultaneously each round.`,
    `Your available actions (choose by index): ${game.actionLabels.map((l, i) => `${i}=${l}`).join(", ")}.`,
    `Payoffs from YOUR perspective:`,
    describeMatrixForSeat(game, playerNum),
    `The match lasts exactly ${numRounds} rounds. Your goal is to maximize YOUR OWN total payoff over all ${numRounds} rounds.`,
    `Respond with ONLY a JSON object, no other text: {"action": <action index>, "reasoning": "<1-2 sentences>"}`,
  ].join("\n");

  const user = [
    `History so far:`,
    historyForSeat(history, playerNum),
    ``,
    `This is round ${roundNum} of ${numRounds}. Choose your action.`,
  ].join("\n");

  let promptTokens = 0;
  let completionTokens = 0;
  let lastErr: unknown;

  for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
    try {
      const resp = await openai.chat.completions.create({
        model,
        max_completion_tokens: 8192,
        messages: [
          { role: "system", content: system },
          { role: "user", content: user },
        ],
      });
      promptTokens += resp.usage?.prompt_tokens ?? 0;
      completionTokens += resp.usage?.completion_tokens ?? 0;
      const text = resp.choices[0]?.message?.content ?? "";
      const parsed = extractJsonObject(text);
      const action = Number(parsed.action);
      if (!Number.isInteger(action) || action < 0 || action >= game.numActions) {
        throw new LlmDecisionError(`invalid action ${String(parsed.action)} (round ${roundNum})`);
      }
      const reasoning =
        typeof parsed.reasoning === "string" && parsed.reasoning.trim().length > 0
          ? parsed.reasoning.trim().slice(0, 2000)
          : "(no reasoning given)";
      return { action, reasoning, promptTokens, completionTokens, attempts: attempt };
    } catch (err) {
      lastErr = err;
      if (attempt === MAX_ATTEMPTS) break;
      const backoff = isRateLimitError(err) ? 5000 * attempt : 1000 * attempt;
      await sleep(backoff);
    }
  }
  throw new LlmDecisionError(
    `LLM decision failed after ${MAX_ATTEMPTS} attempts (round ${roundNum}, model ${model}): ${
      lastErr instanceof Error ? lastErr.message : String(lastErr)
    }`
  );
}

/**
 * Play a full game live: LLM seats decide via the model, classic seats are
 * predicted locally (deterministic strategies only). Returns the complete
 * history plus per-seat scripted move lists ready for engine materialization.
 */
export async function playLlmLiveLoop(input: {
  game: GameDef & { name?: string };
  seats: { p1: SeatSpec; p2: SeatSpec };
  numRounds: number;
}): Promise<LiveLoopResult> {
  const { game, seats, numRounds } = input;

  for (const [label, seat] of [
    ["p1", seats.p1],
    ["p2", seats.p2],
  ] as const) {
    if (seat.kind === "classic" && !PREDICTABLE_OPPONENTS.has(seat.slug)) {
      throw new LlmDecisionError(
        `LLM matchups support deterministic opponents (${[...PREDICTABLE_OPPONENTS].join(", ")}) ` +
          `or LLM-vs-LLM; seat ${label} plays "${seat.slug}"`
      );
    }
  }

  const history: LiveRound[] = [];
  const p1Moves: ScriptedMove[] = [];
  const p2Moves: ScriptedMove[] = [];
  const meta: LlmRunMeta = {
    models: {
      ...(seats.p1.kind === "llm" ? { p1: seats.p1.model } : {}),
      ...(seats.p2.kind === "llm" ? { p2: seats.p2.model } : {}),
    },
    promptVersion: LLM_PROMPT_VERSION,
    temperature: "provider-default (fixed at 1 for gpt-5 family)",
    horizonDisclosed: true,
    llmCalls: 0,
    promptTokens: 0,
    completionTokens: 0,
    retriedCalls: 0,
  };

  const seatAction = async (seat: SeatSpec, playerNum: 1 | 2): Promise<ScriptedMove | number> => {
    if (seat.kind === "classic") {
      return predictOpponentAction(seat.slug, history, playerNum, game);
    }
    const d = await decideLlmMove({ game, history, playerNum, model: seat.model, numRounds });
    meta.llmCalls += 1;
    meta.promptTokens += d.promptTokens;
    meta.completionTokens += d.completionTokens;
    if (d.attempts > 1) meta.retriedCalls += 1;
    return { action: d.action, reasoning: d.reasoning };
  };

  for (let n = 1; n <= numRounds; n++) {
    // Sequential p1-then-p2, matching engine order. Decisions only see prior
    // rounds, so ordering cannot leak the same-round opponent move.
    const m1 = await seatAction(seats.p1, 1);
    const m2 = await seatAction(seats.p2, 2);
    const a1 = typeof m1 === "number" ? m1 : m1.action;
    const a2 = typeof m2 === "number" ? m2 : m2.action;
    if (typeof m1 !== "number") p1Moves.push(m1);
    if (typeof m2 !== "number") p2Moves.push(m2);
    const [p1Payoff, p2Payoff] = game.payoffMatrix[a1][a2];
    history.push({ p1Action: a1, p2Action: a2, p1Payoff, p2Payoff });
  }

  return {
    history,
    p1Moves: seats.p1.kind === "llm" ? p1Moves : null,
    p2Moves: seats.p2.kind === "llm" ? p2Moves : null,
    meta,
  };
}
