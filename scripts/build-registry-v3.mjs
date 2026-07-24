#!/usr/bin/env node
/**
 * Registry v3 builder — Phase 4 freeze-packet sections B and C.
 *
 * Appends Phase 4 prompt templates to prompts/registry.json (append-only: existing
 * keys are asserted byte-untouched), computes per-template sha256s, generates the
 * complete arm table (D1 64, D2 8, D3 36, E 4, X2 rungs + confirmation, F 11,
 * sentinels) with dynamic-binding pins and environment-seed assignments, plus the
 * sealed interleaved execution schedule. Emits:
 *   docs/phase4/registry-v3-manifest.md   (human-readable, actual SHAs)
 *   docs/phase4/arms.json                 (machine manifest: arms, bindings, seeds)
 *   docs/phase4/execution-schedule.json   (sealed episode-level order)
 * X2 rung assembly asserts byte-exact reproduction of the sealed v1/v2a endpoints —
 * the mechanical-diff proof required by sign-off §6.1.
 * No LLM calls. Deterministic output (schedule RNG: mulberry32, seed recorded).
 */
import { readFileSync, writeFileSync, mkdirSync } from "node:fs";
import { createHash } from "node:crypto";

const REG_PATH = "artifacts/api-server/prompts/registry.json";
const SCHEDULE_SEED = 20260724;
const sha = (s) => createHash("sha256").update(s).digest("hex");
// Recursive canonical serializer: sorted keys at EVERY level, arrays in order.
// (A key-whitelist JSON.stringify is NOT sufficient — it drops nested-object
// content from the hashed material; caught in architect review.)
const canonical = (v) => {
  if (Array.isArray(v)) return "[" + v.map(canonical).join(",") + "]";
  if (v && typeof v === "object")
    return "{" + Object.keys(v).sort().map((k) => JSON.stringify(k) + ":" + canonical(v[k])).join(",") + "}";
  return JSON.stringify(v);
};

function mulberry32(a) {
  return function () {
    a |= 0; a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const reg = JSON.parse(readFileSync(REG_PATH, "utf8"));
const P = reg.prompts;
// append-only guard: the five sealed Phase 3 prompt ids must exist and stay untouched
const sealed = ["pd-oneshot-v1", "pd-repeated-v1", "pd-repeated-v2a", "pd-repeated-v2b", "rps-v1"];
const sealedShas = {};
for (const id of sealed) {
  if (!P[id]) throw new Error(`sealed prompt ${id} missing`);
  sealedShas[id] = sha(canonical(P[id]));
}

// ═══════════════════════ span decomposition (X2, sign-off §6.1) ═══════════════
// Six rendered spans + inert retrySuffix. Assembly below reproduces the sealed
// endpoints byte-exactly (asserted), which constitutes the mechanical-diff proof.
const V1 = P["pd-repeated-v1"], V2A = P["pd-repeated-v2a"];
const SPAN = {
  1: { name: "system message", v1: V1.system, v2: V2A.system },
  2: {
    name: "continuation sentence (wording + position)",
    v1: "After every round there is a {deltaPct}% chance the session continues with another round.",
    v2: "At the end of each round there is a {deltaPct}% chance that the session goes on for one more round.",
  },
  3: {
    name: "choice instruction",
    v1: "You and another participant each choose one letter, J or F, at the same time.",
    v2: "You and another person each pick one letter at the same time: J or F.",
  },
  4: {
    name: "payoff block",
    v1: "Points for each combination:\n- You choose J, other chooses J: you earn {rr} points; they earn {rr} points.\n- You choose J, other chooses F: you earn {rs} points; they earn {rt} points.\n- You choose F, other chooses J: you earn {rt} points; they earn {rs} points.\n- You choose F, other chooses F: you earn {rp} points; they earn {rp} points.",
    v2: "The points work like this:\n- If you pick J and they pick J, you receive {rr} points and they receive {rr} points.\n- If you pick J and they pick F, you receive {rs} points and they receive {rt} points.\n- If you pick F and they pick J, you receive {rt} points and they receive {rs} points.\n- If you pick F and they pick F, you receive {rp} points and they receive {rp} points.",
  },
  5: {
    name: "history presentation",
    v1: { historyHeader: V1.historyHeader, historyLine: V1.historyLine, firstRound: V1.firstRound },
    v2: { historyHeader: V2A.historyHeader, historyLine: V2A.historyLine, firstRound: V2A.firstRound },
  },
  6: {
    name: "final choice line",
    v1: "Round {round}. Your choice (J or F):",
    v2: "Round {round}. Pick J or F:",
  },
};
const K_SPANS = 6; // retrySuffix (span 7) registered inert: zero retries in all arms

/** Assemble a rung bundle: spans in `applied` take v2a text/position, others v1. */
function assembleRung(applied) {
  const has = (i) => applied.includes(i);
  const cont = has(2) ? SPAN[2].v2 : SPAN[2].v1;
  const parts = [];
  if (has(2)) parts.push(cont); // v2a position: first line
  parts.push(has(3) ? SPAN[3].v2 : SPAN[3].v1);
  parts.push(has(4) ? SPAN[4].v2 : SPAN[4].v1);
  if (!has(2)) parts.push(cont); // v1 position: after payoff block
  const user = parts.join("\n") + "\n\n{history}\n\n" + (has(6) ? SPAN[6].v2 : SPAN[6].v1);
  const hist = has(5) ? SPAN[5].v2 : SPAN[5].v1;
  return {
    options: ["J", "F"],
    system: has(1) ? SPAN[1].v2 : SPAN[1].v1,
    user,
    historyHeader: hist.historyHeader,
    historyLine: hist.historyLine,
    firstRound: hist.firstRound,
    retrySuffix: has(7) ? V2A.retrySuffix : V1.retrySuffix, // span 7 inert; F-path keeps v1, R-path v2a
  };
}
// byte-exact endpoint assertions (mechanical-diff proof)
{
  const f0 = assembleRung([]);
  const fk = assembleRung([1, 2, 3, 4, 5, 6, 7]);
  for (const key of ["system", "user", "historyHeader", "historyLine", "firstRound", "retrySuffix"]) {
    if (f0[key] !== V1[key]) throw new Error(`span assembly(∅) mismatch vs sealed v1 at ${key}`);
    if (fk[key] !== V2A[key]) throw new Error(`span assembly(all) mismatch vs sealed v2a at ${key}`);
  }
}

// ═══════════════════════ D1/D2 one-shot + repeated template families ══════════
// Wording family W: w1 = sealed v1 style; w2a = registered one-shot adaptation of
// v2a (NEW composition — flagged for semantic-invariance audit before sealing).
// Label set L: neu = J/F ("letter"); sem = COOPERATE/DEFECT ("word").
// Option order O: cf = cooperation-role token first; df = defect-role token first.
// Payoff-line order P: ad = as defined (CC,CD,DC,DD); pm = permuted (reversed).
// Matrix M is DYNAMIC: placeholders {rr},{rs},{rt},{rp} pinned per arm.

const TOK = { neu: ["J", "F"], sem: ["COOPERATE", "DEFECT"] };
const UNIT = { neu: "letter", sem: "word" };

function oneShotTemplate(w, l, o, p) {
  const [C, D] = TOK[l];
  const [first, second] = o === "cf" ? [C, D] : [D, C];
  const unit = UNIT[l];
  const linesV1 = [
    `- You choose ${C}, other chooses ${C}: you earn {rr} points; they earn {rr} points.`,
    `- You choose ${C}, other chooses ${D}: you earn {rs} points; they earn {rt} points.`,
    `- You choose ${D}, other chooses ${C}: you earn {rt} points; they earn {rs} points.`,
    `- You choose ${D}, other chooses ${D}: you earn {rp} points; they earn {rp} points.`,
  ];
  const linesV2 = [
    `- If you pick ${C} and they pick ${C}, you receive {rr} points and they receive {rr} points.`,
    `- If you pick ${C} and they pick ${D}, you receive {rs} points and they receive {rt} points.`,
    `- If you pick ${D} and they pick ${C}, you receive {rt} points and they receive {rs} points.`,
    `- If you pick ${D} and they pick ${D}, you receive {rp} points and they receive {rp} points.`,
  ];
  const order = (lines) => (p === "ad" ? lines : [...lines].reverse());
  if (w === "w1") {
    return {
      options: [C, D],
      system: `You are Player {seat} in a decision-making study. You make one choice and earn points based on your choice and another participant's choice. Reply with exactly one ${unit} and nothing else.`,
      user:
        `You and another participant each choose one ${unit}, ${first} or ${second}, at the same time. This happens exactly once.\n` +
        `Points for each combination:\n${order(linesV1).join("\n")}\n\nYour choice (${first} or ${second}):`,
      retrySuffix: `\n\nYour previous reply was not a valid choice. Reply with exactly one ${unit}: ${first} or ${second}.`,
    };
  }
  return {
    options: [C, D],
    system: `You are Player {seat} in a decision-making session. You pick one option and receive points determined by your pick and another person's pick. Answer with a single ${unit} only.`,
    user:
      `You and another person each pick one ${unit} at the same time: ${first} or ${second}. This happens one time only.\n` +
      `The points work like this:\n${order(linesV2).join("\n")}\n\nYour pick (${first} or ${second}):`,
    retrySuffix: `\n\nThat was not a valid answer. Answer with a single ${unit}: ${first} or ${second}.`,
  };
}

function repeatedTemplate(w, l, o, p) {
  const [C, D] = TOK[l];
  const [first, second] = o === "cf" ? [C, D] : [D, C];
  const unit = UNIT[l];
  const os = oneShotTemplate(w, l, o, p); // reuse payoff-line construction
  const payoffBlock = os.user.split("\n").filter((x) => x.startsWith("- ")).join("\n");
  if (w === "w1") {
    return {
      options: [C, D],
      system: `You are Player {seat} in a decision-making study. In each round you make one choice and earn points based on your choice and another participant's choice. Reply with exactly one ${unit} and nothing else.`,
      user:
        `You and another participant each choose one ${unit}, ${first} or ${second}, at the same time.\n` +
        `Points for each combination:\n${payoffBlock}\n` +
        `After every round there is a {deltaPct}% chance the session continues with another round.\n\n{history}\n\nRound {round}. Your choice (${first} or ${second}):`,
      historyHeader: "Previous rounds:",
      historyLine: "Round {n}: you chose {you}, the other chose {them}. You earned {youPts} points; they earned {themPts} points.",
      firstRound: "This is the first round.",
      retrySuffix: `\n\nYour previous reply was not a valid choice. Reply with exactly one ${unit}: ${first} or ${second}.`,
    };
  }
  return {
    options: [C, D],
    system: `You are Player {seat} in a decision-making session. Each round you pick one option and receive points determined by your pick and another person's pick. Answer with a single ${unit} only.`,
    user:
      `At the end of each round there is a {deltaPct}% chance that the session goes on for one more round.\n` +
      `You and another person each pick one ${unit} at the same time: ${first} or ${second}.\n` +
      `The points work like this:\n${payoffBlock}\n\n{history}\n\nRound {round}. Pick ${first} or ${second}:`,
    historyHeader: "Rounds so far:",
    historyLine: "Round {n}: you picked {you} and they picked {them} — {youPts} points for you, {themPts} for them.",
    firstRound: "No rounds have happened yet.",
    retrySuffix: `\n\nThat was not a valid answer. Answer with a single ${unit}: ${first} or ${second}.`,
  };
}

// sanity: w1/neu/cf/ad repeated must equal sealed pd-repeated-v1 byte-for-byte
{
  const t = repeatedTemplate("w1", "neu", "cf", "ad");
  for (const key of ["system", "user", "historyHeader", "historyLine", "firstRound"]) {
    if (t[key] !== V1[key]) throw new Error(`repeated(w1,neu,cf,ad) diverges from sealed v1 at ${key}`);
  }
}

// ═══════════════════════ build new prompt entries ═════════════════════════════
const newPrompts = {};
// Idempotent for 4-proposed entries (rebuild pre-seal is allowed and deterministic);
// collision with a sealed (non-proposed) id is always fatal.
const add = (id, spec, meta) => {
  if (P[id] && P[id].phase !== "4-proposed") throw new Error(`prompt id collision with sealed entry: ${id}`);
  newPrompts[id] = { ...spec, phase: "4-proposed", ...meta };
};

const W = ["w1", "w2a"], L = ["neu", "sem"], O = ["cf", "df"], PP = ["ad", "pm"];
for (const w of W) for (const l of L) for (const o of O) for (const p of PP) {
  add(`pd-os-${w}-${l}-${o}-${p}`, oneShotTemplate(w, l, o, p), { family: "d1-oneshot" });
  add(`pd-rep-${w}-${l}-${o}-${p}`, repeatedTemplate(w, l, o, p), { family: "e-repeated-candidate" });
}
// E community presentation: v1-style repeated with the sealed Community line prefixed
{
  const t = repeatedTemplate("w1", "neu", "cf", "ad");
  add("pd-rep-community-w1", { ...t, user: "This is called the Community Game. " + t.user }, { family: "e-community" });
}
// X2 rungs: forward F1..F5 (spans 1..i to v2a) and reverse R1..R5 (spans 1..i back to v1)
const spanOrder = [1, 2, 3, 4, 5, 6];
for (let i = 1; i < K_SPANS; i++) {
  add(`pd-x2-f${i}`, assembleRung(spanOrder.slice(0, i)), { family: "x2-forward", spansApplied: spanOrder.slice(0, i) });
  add(`pd-x2-r${i}`, assembleRung(spanOrder.slice(i)), { family: "x2-reverse", spansReverted: spanOrder.slice(0, i) });
}
// D3 neutral-symbol RPS: tokens fixed [X,Y,Z]; role mapping + display order are
// registered dynamic bindings; {beatsLine} and {optList} rendered deterministically.
add("rps-sym-v1", {
  options: ["X", "Y", "Z"],
  system: "You are Player {seat} in a decision-making study. In each round you make one choice. Reply with exactly one letter and nothing else.",
  user:
    "You are playing a symbol game against another player for {numRounds} rounds.\n" +
    "Each round, you and the other player choose {optList} at the same time.\n" +
    "{beatsLine} The same choice is a tie.\n" +
    "Scoring each round: win +1 point, tie 0 points, loss -1 point.\n\n{history}\n\nRound {round}. Your choice ({optList}):",
  historyHeader: "Previous rounds:",
  historyLine: "Round {n}: you chose {you}, the other chose {them}. {outcome}",
  outcomes: { win: "You won (+1).", tie: "Tie (0).", lose: "You lost (-1)." },
  firstRound: "This is the first round.",
  retrySuffix: "\n\nYour previous reply was not a valid choice. Reply with exactly one letter: {optList}.",
}, { family: "d3-rps-symbols" });

// ═══════════════════════ matrices + arms ══════════════════════════════════════
const MATRIX = {
  can: { rr: 3, rs: 0, rt: 5, rp: 1 },
  aff: { rr: 11, rs: 2, rt: 17, rp: 5 }, // canonical ×3 + 2
  nva: { rr: 4, rs: 1, rt: 6, rp: 2 },
  nvb: { rr: 7, rs: 2, rt: 9, rp: 3 },
  cfd: { rr: 5, rs: 4, rt: 3, rp: 1 }, // D2 cooperation-dominant counterfactual
};
// PD-class assertions for the three non-counterfactual novel/affine matrices
for (const k of ["can", "aff", "nva", "nvb"]) {
  const { rr: R, rs: S, rt: T, rp: Pp } = MATRIX[k];
  if (!(T > R && R > Pp && Pp > S && 2 * R > T + S)) throw new Error(`matrix ${k} not PD-class`);
}
// cfd: cooperation-role strictly dominant
{
  const { rr: R, rs: S, rt: T, rp: Pp } = MATRIX.cfd;
  if (!(R > T && S > Pp)) throw new Error("cfd matrix: cooperation-role not strictly dominant");
}

const arms = [];
const MODELS = { primary: "gpt-4.1", cross: "claude-haiku-4-5" };
let seedCursor = 2001; // Phase 3 used 1–20 (+1000 replacement pool); Phase 4 starts at 2001
const takeSeeds = (n) => Array.from({ length: n }, () => seedCursor++);

// D1: 64 cells × both models, 10 episodes each; same template+binding, per-model arms
for (const m of ["can", "aff", "nva", "nvb"]) for (const w of W) for (const l of L) for (const o of O) for (const p of PP) {
  const cellSeeds = takeSeeds(10); // shared seed list across models (matched environments)
  for (const model of ["primary", "cross"]) {
    arms.push({
      armId: `p4-d1-${m}-${w}-${l}-${o}-${p}-${model === "primary" ? "gpt" : "cvx"}`,
      block: "D1", templateId: `pd-os-${w}-${l}-${o}-${p}`, game: "one-shot PD self-play",
      bindings: { matrix: m, ...MATRIX[m], labelRoleMap: "aligned" },
      episodes: 10, seeds: cellSeeds, model: MODELS[model], deltaPct: null,
    });
  }
}
// D2: 8 cells (W × G × S) × both models, 20 episodes; semantic labels, cf/ad fixed
for (const w of W) for (const g of ["can", "cfd"]) for (const s of ["al", "sw"]) {
  const cellSeeds = takeSeeds(20);
  for (const model of ["primary", "cross"]) {
    arms.push({
      armId: `p4-d2-${w}-${g}-${s}-${model === "primary" ? "gpt" : "cvx"}`,
      block: "D2", templateId: `pd-os-${w}-sem-cf-ad`, game: "one-shot PD self-play",
      bindings: {
        matrix: g, ...MATRIX[g], labelRoleMap: s === "al" ? "aligned" : "swapped",
        note: "swapped: the word COOPERATE displays the defection-role; payoff values bound to displayed words via the role map; parser records the DISPLAYED choice; strategic role derived in analysis from this binding",
      },
      episodes: 20, seeds: cellSeeds, model: MODELS[model], deltaPct: null,
    });
  }
}
// D3: 36 mapping×order cells × 2 replicates × both models (1 round, 2 seats)
const perms3 = [[0,1,2],[0,2,1],[1,0,2],[1,2,0],[2,0,1],[2,1,0]];
for (let mi = 0; mi < 6; mi++) for (let oi = 0; oi < 6; oi++) {
  const cellSeeds = takeSeeds(2);
  for (const model of ["primary", "cross"]) {
    arms.push({
      armId: `p4-d3-map${mi + 1}-ord${oi + 1}-${model === "primary" ? "gpt" : "cvx"}`,
      block: "D3", templateId: "rps-sym-v1", game: "RPS 1-round self-play",
      bindings: {
        roleMapping: { X: ["rock","paper","scissors"][perms3[mi][0]], Y: ["rock","paper","scissors"][perms3[mi][1]], Z: ["rock","paper","scissors"][perms3[mi][2]] },
        displayOrder: perms3[oi].map((i) => ["X","Y","Z"][i]),
        renderRule: "optList = displayOrder joined with ', ' and final ' or '; beatsLine derived from roleMapping via the fixed sentence '<winner> beats <loser>' over the three beat relations in display order",
      },
      episodes: 2, seeds: cellSeeds, model: MODELS[model], deltaPct: null,
    });
  }
}
// E: 4 cells × both models; D-selected template resolved mechanically after D1
for (const pres of ["community", "dselected"]) for (const d of [10, 90]) {
  const cellSeeds = takeSeeds(20);
  for (const model of ["primary", "cross"]) {
    arms.push({
      armId: `p4-e-${pres}-d${d}-${model === "primary" ? "gpt" : "cvx"}`,
      block: "E",
      templateId: pres === "community" ? "pd-rep-community-w1" : "RESOLVED-BY-D1-SELECTION(pd-rep-*)",
      game: "repeated PD self-play, geometric horizon cap 120",
      bindings: { matrix: "can", ...MATRIX.can, selectionRule: pres === "dselected" ? "D1 cell (primary-model data only) with episode-level round-1 cooperation nearest 0.5; tie-break lowest sealed arm ID; repeated-family counterpart of the selected one-shot template; selection written to event store before any E run" : undefined },
      episodes: 20, seeds: cellSeeds, model: MODELS[model], deltaPct: d,
    });
  }
}
// X2: primary model only; screening rungs use X1 seeds 1–10 (registered subset)
for (let i = 1; i < K_SPANS; i++) {
  for (const path of ["f", "r"]) {
    arms.push({
      armId: `p4-x2-${path}${i}`, block: "X2-screening", templateId: `pd-x2-${path}${i}`,
      game: "repeated PD self-play, δ=.90, X1-matched horizons",
      bindings: { matrix: "can", ...MATRIX.can }, episodes: 10,
      seeds: [1,2,3,4,5,6,7,8,9,10], seedNote: "X1 environment-seed list (first 10) with matched horizon draws",
      model: MODELS.primary, deltaPct: 90,
    });
  }
}
{
  const confSeeds = takeSeeds(20);
  for (const side of ["lo", "hi"]) {
    arms.push({
      armId: `p4-x2-conf-${side}`, block: "X2-confirmation",
      templateId: "RESOLVED-BY-SCREENING(minimal pair)", game: "repeated PD self-play, δ=.90",
      bindings: { matrix: "can", ...MATRIX.can, rule: "exact minimal pair around the selected span; fresh seeds; runs only if screening finds an adjacent |Δ| ≥ 0.50" },
      episodes: 20, seeds: confSeeds, model: MODELS.primary, deltaPct: 90,
    });
  }
}
// F: 50 rounds (stabilization gate FAILED at |Δstay|=0.0512 > 0.05 → 50-round design)
const F_OPP = ["fo-tracker", "ngram2", "ngram3", "wsls-targeter", "switcher-r26", "shuffled-history"];
for (const opp of F_OPP) {
  const oppSeeds = takeSeeds(20);
  for (const model of ["primary", "cross"]) {
    if (model === "cross" && opp === "ngram3") continue; // dropped for cross-vendor per sign-off
    arms.push({
      armId: `p4-f-${opp}-${model === "primary" ? "gpt" : "cvx"}`, block: "F",
      templateId: "rps-v1", game: "RPS 50 rounds vs engine adversary",
      bindings: { opponent: opp, rounds: 50, switchRound: opp === "switcher-r26" ? 26 : undefined, signConvention: "reported payoff = ADVERSARY per-round payoff against the subject; positive = adversary exploits subject" },
      episodes: 20, seeds: oppSeeds, model: MODELS[model], deltaPct: null,
    });
  }
}
// Sentinels: 3 cells × 10 episodes per check, horizon forced to 1 (fingerprint only)
for (const [cell, tid] of [["v1", "pd-repeated-v1"], ["v2a", "pd-repeated-v2a"], ["fallback", "pd-os-w1-neu-cf-ad"]]) {
  arms.push({
    armId: `p4-sent-${cell}`, block: "sentinel", templateId: tid,
    game: cell === "fallback" ? "one-shot PD self-play" : "repeated PD self-play, horizon forced to 1 (round-1 fingerprint)",
    bindings: { matrix: "can", ...MATRIX.can, monitoringOnly: true, note: "never pooled into experimental inference; third cell switches to the D-selected representation once written to the event store" },
    episodes: 10, seeds: "per-check: 9001+checkIndex*10 … +9", model: "per-check: each subject model", deltaPct: cell === "fallback" ? null : 90,
  });
}

// ═══════════════════════ write registry + manifests ═══════════════════════════
for (const [id, spec] of Object.entries(newPrompts)) P[id] = spec;
reg.registryVersion = "phase4-v3-proposed";
const V3_NOTE = "2026-07-24 v3-proposed: Phase 4 templates appended (append-only; Phase 3 entries byte-untouched, per-prompt shas verified). Arms/bindings/seeds: docs/phase4/arms.json. Runs blocked pending one-line approval.";
if (!(reg.notes || "").includes("v3-proposed:")) reg.notes = (reg.notes ? reg.notes + " | " : "") + V3_NOTE;
writeFileSync(REG_PATH, JSON.stringify(reg, null, 1));

// post-write integrity: sealed entries unchanged
const reg2 = JSON.parse(readFileSync(REG_PATH, "utf8"));
for (const id of sealed) {
  if (sha(canonical(reg2.prompts[id])) !== sealedShas[id]) throw new Error(`append-only violation on ${id}`);
}

const tShas = Object.fromEntries(Object.entries(newPrompts).map(([id, s]) => [id, sha(canonical(s))]));
mkdirSync("docs/phase4", { recursive: true });
writeFileSync("docs/phase4/arms.json", JSON.stringify({
  generatedAt: new Date().toISOString(), scheduleSeed: SCHEDULE_SEED,
  models: MODELS, sealedPhase3Shas: sealedShas, templateShas: tShas,
  seedPolicy: "Phase 4 experimental seeds 2001+ (disjoint from Phase 3 1–20/1000+ and X1); X2 screening reuses X1 seeds 1–10 by registered rule; sentinel pool 9001+",
  arms,
}, null, 1));

// sealed execution schedule: episode-level interleave of model × condition
const episodes = [];
for (const a of arms) {
  if (a.block === "sentinel" || a.block === "X2-confirmation") continue; // scheduled relative to blocks
  if (!Array.isArray(a.seeds)) continue;
  a.seeds.forEach((s, i) => episodes.push({ armId: a.armId, block: a.block, model: a.model, seed: s, ep: i + 1 }));
}
const rng = mulberry32(SCHEDULE_SEED);
// within each block, shuffle (arm × episode × model) jointly → models interleaved
const blocksOrder = ["X2-screening", "D1", "D2", "D3", "E", "F"]; // per sign-off §14 (X2 screening with D; E after selection; F last)
const schedule = [];
for (const b of blocksOrder) {
  const items = episodes.filter((e) => e.block === b);
  for (let i = items.length - 1; i > 0; i--) {
    const j = Math.floor(rng() * (i + 1));
    [items[i], items[j]] = [items[j], items[i]];
  }
  schedule.push({ block: b, note: b === "E" ? "runs only after D-selected arm written to event store; sentinel immediately before and after this block" : "sentinel immediately before and after this block", episodes: items });
}
writeFileSync("docs/phase4/execution-schedule.json", JSON.stringify({ scheduleSeed: SCHEDULE_SEED, blocks: schedule }, null, 1));

// human-readable manifest
const armRows = arms.map((a) =>
  `| ${a.armId} | ${a.block} | ${a.templateId} | ${a.templateId.startsWith("RESOLVED") ? "—" : (tShas[a.templateId] ?? sealedShas[a.templateId] ?? "—").slice(0, 12)}… | ${a.episodes} | ${Array.isArray(a.seeds) ? `${a.seeds[0]}–${a.seeds[a.seeds.length - 1]}` : a.seeds} | ${a.model} |`
).join("\n");
writeFileSync("docs/phase4/registry-v3-manifest.md", `# Registry v3 Manifest (PROPOSED — sealed at approval, then externally anchored)

> Machine-generated by \`scripts/build-registry-v3.mjs\`. Append-only: the five Phase 3
> prompt entries are byte-untouched (shas verified pre/post append). No runs are
> authorized; every arm below is inert until the one-line approval.

## Sealed Phase 3 entries (unchanged)

${sealed.map((id) => `- \`${id}\` — sha256 \`${sealedShas[id]}\``).join("\n")}

## New templates (${Object.keys(newPrompts).length}) — canonical-JSON sha256

| Template | Family | sha256 |
|---|---|---|
${Object.entries(newPrompts).map(([id, s]) => `| \`${id}\` | ${s.family} | \`${tShas[id]}\` |`).join("\n")}

Canonical render/hash rule: template spec hashed as canonical JSON (sorted keys); a
rendered message bundle hashes as sha256 of \`system + "\\x1e" + user\` after dynamic-field
substitution; permitted dynamic fields per family are exactly those named in the template
text plus the pinned bindings in \`arms.json\`. Any other substitution is a violation the
engine must reject (server-side enforcement, sign-off §10.1).

Parser contract (all PD families): strip → uppercase → exact match against the template's
\`options\` array; the match yields the DISPLAYED option index; strategic role is derived
in analysis from the arm's \`labelRoleMap\`/\`roleMapping\` binding. One retry with
\`retrySuffix\`, then replacement from the reserved pool. Parser version: pinned at engine
hardening (freeze packet provider section).

## Arms (${arms.length})

| Arm | Block | Template | Template sha | Episodes | Seeds | Model |
|---|---|---|---|---|---|---|
${armRows}

## X2 span decomposition (k = ${K_SPANS} rendered spans; retrySuffix registered inert)

Byte-exact endpoint proof: \`assembleRung(∅)\` ≡ sealed \`pd-repeated-v1\`,
\`assembleRung({1..7})\` ≡ sealed \`pd-repeated-v2a\` (asserted on every build).
Spans: ${Object.entries(SPAN).map(([i, s]) => `S${i} ${s.name}`).join("; ")}.
`);
// seed accounting: per-block allocated ranges + disjointness assertions
const ranges = {};
for (const a of arms) {
  if (!Array.isArray(a.seeds)) continue;
  const key = a.block;
  const mn = Math.min(...a.seeds), mx = Math.max(...a.seeds);
  ranges[key] = ranges[key] ? [Math.min(ranges[key][0], mn), Math.max(ranges[key][1], mx)] : [mn, mx];
}
// X2 screening deliberately reuses X1 seeds 1–10; every other block must live in 2001+
for (const [blk, [mn, mx]] of Object.entries(ranges)) {
  if (blk === "X2-screening") {
    if (mn < 1 || mx > 10) throw new Error("X2 screening must use X1 seeds 1–10");
  } else if (mn < 2001) throw new Error(`block ${blk} strays below the Phase 4 seed floor (2001): ${mn}`);
}
// allocated (cursor-based) blocks must be pairwise disjoint
const alloc = Object.entries(ranges).filter(([b]) => b !== "X2-screening").sort((x, y) => x[1][0] - y[1][0]);
for (let i = 1; i < alloc.length; i++) {
  if (alloc[i][1][0] <= alloc[i - 1][1][1]) {
    // interleaved allocation within the cursor is fine only if the actual seed SETS are disjoint
    const seen = new Set();
    for (const a of arms) if (Array.isArray(a.seeds) && a.block !== "X2-screening")
      for (const s of a.seeds) { if (seen.has(s)) throw new Error(`seed ${s} allocated twice`); seen.add(s); }
    break;
  }
}
console.log(`registry v3: +${Object.keys(newPrompts).length} templates, ${arms.length} arms, schedule blocks ${blocksOrder.join(">")}`);
console.log(`seeds allocated: 2001–${seedCursor - 1}; X2 rungs 2(k-1)=${2 * (K_SPANS - 1)}; endpoints byte-verified`);
console.log("per-block seed ranges (AUTHORITATIVE — docs must quote these):");
for (const [blk, [mn, mx]] of Object.entries(ranges)) console.log(`  ${blk}: ${mn}–${mx}`);
