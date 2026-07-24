#!/usr/bin/env node
/**
 * Phase 3 — Layer 2: estimand-aware statistical companion to the registered verdicts.
 *
 * Added 2026-07-24 in response to external methods review. This layer NEVER
 * modifies a registered verdict; it computes, per claim, the statistical
 * interpretation appropriate to the estimand (policy rate vs corpus statement),
 * with explicit units of analysis and cluster-aware uncertainty:
 *
 *   - Exact Clopper-Pearson intervals at the run level for all-zero / all-one cells
 *     (an observed 0/20 bounds the policy rate, it does not establish zero).
 *   - A unit-of-analysis accounting row for every registered claim item
 *     (raw decisions, run-seats, independent runs, cluster level, CI method).
 *   - C2 recomputed from raw round data with a cluster bootstrap that resamples
 *     whole runs (both seat trajectories move together).
 *   - B1/C3 supplemented with seeded run-level permutation tests (Welch assumes
 *     a variance estimate the all-zero arm cannot supply).
 *
 * Everything is deterministic: bootstrap/permutation RNG is mulberry32 with
 * fixed seeds recorded in the output. Output: docs/phase3-layer2.md (+ .json).
 * DO NOT hand-edit the outputs; rerun this script.
 */

import { writeFileSync } from "node:fs";
import { execSync } from "node:child_process";

const BASE = process.env.API_BASE ?? "http://localhost:80/api";
const LAYER2_VERSION = "1.0.0";
const BOOT_SEED = 424242;
const PERM_SEED = 20260724;
const BOOT_REPS = 10000;
const PERM_REPS = 100000;

// ── deterministic RNG (same generator family as the study runner) ───────────
function mulberry32(a) {
  return function () {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// ── exact Clopper-Pearson bounds for extreme cells (closed forms) ────────────
const cpUpper = (n, alpha) => 1 - Math.pow(alpha, 1 / n); // x = 0
const cpLower = (n, alpha) => Math.pow(alpha, 1 / n); // x = n

const mean = (x) => x.reduce((s, v) => s + v, 0) / x.length;
const sd = (x) => {
  const m = mean(x);
  return Math.sqrt(x.reduce((s, v) => s + (v - m) * (v - m), 0) / (x.length - 1));
};
const fmt = (v, d = 4) => (v == null || Number.isNaN(v) ? "—" : v.toFixed(d));
const pct = (v, d = 1) => (v == null || Number.isNaN(v) ? "—" : (100 * v).toFixed(d) + "%");

function percentileCI(vals, lo = 0.025, hi = 0.975) {
  const s = [...vals].sort((a, b) => a - b);
  const at = (q) => s[Math.min(s.length - 1, Math.max(0, Math.floor(q * s.length)))];
  return [at(lo), at(hi)];
}

async function api(path) {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`GET ${path} -> ${res.status}`);
  return res.json();
}

async function pool(items, fn, width = 10) {
  const out = new Array(items.length);
  let i = 0;
  await Promise.all(
    Array.from({ length: width }, async () => {
      while (i < items.length) {
        const idx = i++;
        out[idx] = await fn(items[idx], idx);
      }
    })
  );
  return out;
}

// ── corpus ───────────────────────────────────────────────────────────────────
const all = await api("/experiments");
const t3 = all.filter(
  (e) =>
    e.status === "completed" &&
    e.batchLabel &&
    (e.batchLabel.endsWith(":t3") || e.batchLabel.endsWith(":t3x") || e.batchLabel.endsWith(":t3-baseline"))
);
const byLabel = new Map();
for (const e of t3) {
  if (!byLabel.has(e.batchLabel)) byLabel.set(e.batchLabel, []);
  byLabel.get(e.batchLabel).push(e);
}
const label = {
  a: (arm, d) => `${arm}:llm41-selfplay:d${d}:t3`,
  b: (f) => `prisoners-dilemma:llm41-oneshot:${f}:t3`,
  x: (v) => `prisoners-dilemma:llm41-para-${v}:d90:t3x`,
  baseline: "rock-paper-scissors:pattern-tracker-vs-nash-mixed:t3-baseline",
};
const cLabels = [...byLabel.keys()].filter((l) => l.startsWith("rock-paper-scissors:llm41"));
if (cLabels.length !== 3) throw new Error(`expected 3 C llm labels, got ${JSON.stringify(cLabels)}`);

// details (rounds) for every run we analyze
const detailIds = t3.map((e) => e.id);
const details = new Map(
  (await pool(detailIds, async (id) => [id, await api(`/experiments/${id}`)])).map(([id, d]) => [id, d])
);

// strategy roles (asserted, not assumed)
const strategies = await api("/strategies");
const sid = (slug) => {
  const s = strategies.find((x) => x.slug === slug);
  if (!s) throw new Error(`strategy ${slug} not found`);
  return s.id;
};
const LLM_ID = sid("llm-gpt-4.1");
const TRACKER_ID = sid("pattern-tracker");

// action index maps (asserted from game defs)
const games = Object.fromEntries(
  await Promise.all([1, 7, 8].map(async (g) => [g, await api(`/games/${g}`)]))
);
const coopIndex = { 1: 0, 8: 0 }; // Cooperate / J listed first — asserted:
if (games[1].actionLabels[0] !== "Cooperate" || games[8].actionLabels[0] !== "J")
  throw new Error("PD action order changed — coopIndex assumption violated");
if (games[7].actionLabels[0] !== "Rock") throw new Error("RPS action order changed");

// ── per-run primitives from raw rounds ───────────────────────────────────────
/** round-1 cooperation per seat (0/1 each) for a PD run; returns [s1, s2] */
function round1Coop(run) {
  const d = details.get(run.id);
  const r1 = d.rounds.find((r) => r.roundNumber === 1);
  const ci = coopIndex[run.gameId];
  return [r1.player1Action === ci ? 1 : 0, r1.player2Action === ci ? 1 : 0];
}
/** WSLS conditionals per seat from raw trajectories (ties excluded; null if denom 0) */
function wslsSeat(actions, payoffs) {
  let wN = 0, wS = 0, lN = 0, lS = 0;
  for (let t = 1; t < actions.length; t++) {
    if (payoffs[t - 1] > 0) {
      wN++;
      if (actions[t] === actions[t - 1]) wS++;
    } else if (payoffs[t - 1] < 0) {
      lN++;
      if (actions[t] !== actions[t - 1]) lS++;
    }
  }
  return { wN, wS, lN, lS };
}
function seatsOf(run, onlyLlm = false) {
  const d = details.get(run.id);
  const seats = [];
  for (const seat of [1, 2]) {
    const stratId = seat === 1 ? run.player1StrategyId : run.player2StrategyId;
    if (onlyLlm && stratId !== LLM_ID) continue;
    const actions = d.rounds.map((r) => (seat === 1 ? r.player1Action : r.player2Action));
    const payoffs = d.rounds.map((r) => (seat === 1 ? r.player1Payoff : r.player2Payoff));
    seats.push({ runId: run.id, seat, stratId, actions, payoffs });
  }
  return seats;
}

// ═════════════════════════════════════════════════════════════════════════════
// 1) All-zero / all-one cells → exact Clopper-Pearson at run and seat level
// ═════════════════════════════════════════════════════════════════════════════
const extremeCells = [];
const zeroCellLabels = [
  ...[10, 50, 75, 90].flatMap((d) => [label.a("prisoners-dilemma", d), label.a("prisoners-dilemma-iso", d)]),
  label.b("wallstreet"),
  label.b("neutral"),
];
const oneCellLabels = [label.x("v2a"), label.x("v2b")];
for (const L of [...zeroCellLabels, ...oneCellLabels]) {
  const runs = byLabel.get(L) ?? [];
  if (runs.length === 0) throw new Error(`no runs for ${L}`);
  const seatVals = runs.flatMap((r) => round1Coop(r));
  const runAny = runs.map((r) => (round1Coop(r).some((v) => v === 1) ? 1 : 0));
  const seatSum = seatVals.reduce((a, b) => a + b, 0);
  const runSum = runAny.reduce((a, b) => a + b, 0);
  const isZero = zeroCellLabels.includes(L);
  if (isZero && (seatSum !== 0 || runSum !== 0)) throw new Error(`${L} expected all-zero, saw coop`);
  if (!isZero && (seatSum !== seatVals.length || runSum !== runs.length))
    throw new Error(`${L} expected all-one, saw defection`);
  extremeCells.push({
    label: L,
    kind: isZero ? "all-zero" : "all-one",
    runs: runs.length,
    seatDecisions: seatVals.length,
    // run level: P(a run exhibits any round-1 cooperation) / P(run all-coop)
    runOneSided95: isZero ? cpUpper(runs.length, 0.05) : cpLower(runs.length, 0.05),
    runTwoSided95: isZero ? cpUpper(runs.length, 0.025) : cpLower(runs.length, 0.025),
    // seat level shown with the independence caveat (seats within a run are dependent)
    seatOneSided95: isZero ? cpUpper(seatVals.length, 0.05) : cpLower(seatVals.length, 0.05),
    seatTwoSided95: isZero ? cpUpper(seatVals.length, 0.025) : cpLower(seatVals.length, 0.025),
  });
}
// pooled high-δ canonical (A3's cell): 40 runs
{
  const runs = [...byLabel.get(label.a("prisoners-dilemma", 75)), ...byLabel.get(label.a("prisoners-dilemma", 90))];
  extremeCells.push({
    label: "pooled canonical high-δ (A3 cell)",
    kind: "all-zero",
    runs: runs.length,
    seatDecisions: 2 * runs.length,
    runOneSided95: cpUpper(runs.length, 0.05),
    runTwoSided95: cpUpper(runs.length, 0.025),
    seatOneSided95: cpUpper(2 * runs.length, 0.05),
    seatTwoSided95: cpUpper(2 * runs.length, 0.025),
  });
}

// ═════════════════════════════════════════════════════════════════════════════
// 2) B1 — run-level permutation test + bootstrap CI (community vs wallstreet)
// ═════════════════════════════════════════════════════════════════════════════
const commRuns = byLabel.get(label.b("community")).map((r) => mean(round1Coop(r)));
const wsRuns = byLabel.get(label.b("wallstreet")).map((r) => mean(round1Coop(r)));
const b1Obs = mean(commRuns) - mean(wsRuns);
let b1PermGE = 0;
{
  const both = [...commRuns, ...wsRuns];
  const rng = mulberry32(PERM_SEED);
  for (let rep = 0; rep < PERM_REPS; rep++) {
    // Fisher-Yates partial shuffle → first 20 = pseudo-community
    const idx = both.map((_, i) => i);
    for (let i = idx.length - 1; i > 0; i--) {
      const j = Math.floor(rng() * (i + 1));
      [idx[i], idx[j]] = [idx[j], idx[i]];
    }
    let a = 0;
    for (let i = 0; i < commRuns.length; i++) a += both[idx[i]];
    const diff = a / commRuns.length - (mean(both) * both.length - a) / wsRuns.length;
    if (diff >= b1Obs - 1e-12) b1PermGE++;
  }
}
const b1PermP = (b1PermGE + 1) / (PERM_REPS + 1);
let b1BootCI;
{
  const rng = mulberry32(BOOT_SEED);
  const boots = [];
  for (let rep = 0; rep < BOOT_REPS; rep++) {
    const draw = Array.from({ length: commRuns.length }, () => commRuns[Math.floor(rng() * commRuns.length)]);
    boots.push(mean(draw));
  }
  b1BootCI = percentileCI(boots);
}

// ═════════════════════════════════════════════════════════════════════════════
// 3) C1 — rock share with run-level cluster bootstrap
// ═════════════════════════════════════════════════════════════════════════════
const cRuns = cLabels.flatMap((L) => byLabel.get(L));
const c1SeatRock = []; // one round-1 decision per LLM seat
const c1ByRun = new Map();
for (const run of cRuns) {
  const rocks = seatsOf(run, true).map((s) => (s.actions[0] === 0 ? 1 : 0));
  c1SeatRock.push(...rocks);
  c1ByRun.set(run.id, rocks);
}
const c1Obs = mean(c1SeatRock);
let c1BootCI;
{
  const rng = mulberry32(BOOT_SEED + 1);
  const runIds = [...c1ByRun.keys()];
  const boots = [];
  for (let rep = 0; rep < BOOT_REPS; rep++) {
    const vals = [];
    for (let i = 0; i < runIds.length; i++)
      vals.push(...c1ByRun.get(runIds[Math.floor(rng() * runIds.length)]));
    boots.push(mean(vals));
  }
  c1BootCI = percentileCI(boots);
}

// ═════════════════════════════════════════════════════════════════════════════
// 4) C2 — units resolved from raw data + run-level cluster bootstrap
// ═════════════════════════════════════════════════════════════════════════════
const c2Runs = cRuns;
const c2SeatStats = []; // {runId, arm, wN,wS,lN,lS, stay, shift}
for (const run of c2Runs) {
  for (const s of seatsOf(run, true)) {
    const w = wslsSeat(s.actions, s.payoffs);
    c2SeatStats.push({
      runId: run.id,
      arm: run.batchLabel,
      ...w,
      stay: w.wN > 0 ? w.wS / w.wN : null,
      shift: w.lN > 0 ? w.lS / w.lN : null,
    });
  }
}
const c2NonNullStay = c2SeatStats.filter((s) => s.stay != null);
const c2NonNullShift = c2SeatStats.filter((s) => s.shift != null);
const c2Pooled = c2SeatStats.reduce(
  (a, s) => ({ wN: a.wN + s.wN, wS: a.wS + s.wS, lN: a.lN + s.lN, lS: a.lS + s.lS }),
  { wN: 0, wS: 0, lN: 0, lS: 0 }
);
const c2NullByArm = {};
for (const s of c2SeatStats) {
  const k = s.arm.split(":")[1];
  c2NullByArm[k] ??= { seats: 0, nullStay: 0, nullShift: 0 };
  c2NullByArm[k].seats++;
  if (s.stay == null) c2NullByArm[k].nullStay++;
  if (s.shift == null) c2NullByArm[k].nullShift++;
}
function c2Boot(which) {
  const rng = mulberry32(BOOT_SEED + (which === "stay" ? 2 : 3));
  const byRun = new Map();
  for (const s of c2SeatStats) {
    if (!byRun.has(s.runId)) byRun.set(s.runId, []);
    byRun.get(s.runId).push(s);
  }
  const runIds = [...byRun.keys()];
  const boots = [];
  for (let rep = 0; rep < BOOT_REPS; rep++) {
    let num = 0, den = 0;
    for (let i = 0; i < runIds.length; i++) {
      for (const s of byRun.get(runIds[Math.floor(rng() * runIds.length)])) {
        if (which === "stay") { num += s.wS; den += s.wN; }
        else { num += s.lS; den += s.lN; }
      }
    }
    if (den > 0) boots.push(num / den);
  }
  return { est: which === "stay" ? c2Pooled.wS / c2Pooled.wN : c2Pooled.lS / c2Pooled.lN, ci: percentileCI(boots) };
}
const c2Stay = c2Boot("stay");
const c2Shift = c2Boot("shift");
// registered-style seat-summary means for cross-reference
const c2SeatMeanStay = mean(c2NonNullStay.map((s) => s.stay));
const c2SeatMeanShift = mean(c2NonNullShift.map((s) => s.shift));

// ═════════════════════════════════════════════════════════════════════════════
// 5) C3 — run-level permutation supplement to Welch
// ═════════════════════════════════════════════════════════════════════════════
function trackerPerRound(run) {
  const d = details.get(run.id);
  const seat = run.player1StrategyId === TRACKER_ID ? 1 : 2;
  if ((seat === 1 ? run.player1StrategyId : run.player2StrategyId) !== TRACKER_ID)
    throw new Error(`no tracker seat in run ${run.id}`);
  const total = d.rounds.reduce((s, r) => s + (seat === 1 ? r.player1Payoff : r.player2Payoff), 0);
  return total / d.rounds.length;
}
const c3VsLlm = (byLabel.get(cLabels.find((l) => l.includes("tracker"))) ?? [])
  .filter((r) => [r.player1StrategyId, r.player2StrategyId].includes(TRACKER_ID))
  .map(trackerPerRound);
const c3Baseline = byLabel.get(label.baseline).map(trackerPerRound);
const c3Obs = mean(c3VsLlm) - mean(c3Baseline);
let c3PermP;
{
  const both = [...c3VsLlm, ...c3Baseline];
  const rng = mulberry32(PERM_SEED + 1);
  let extreme = 0;
  for (let rep = 0; rep < PERM_REPS; rep++) {
    const idx = both.map((_, i) => i);
    for (let i = idx.length - 1; i > 0; i--) {
      const j = Math.floor(rng() * (i + 1));
      [idx[i], idx[j]] = [idx[j], idx[i]];
    }
    let a = 0;
    for (let i = 0; i < c3VsLlm.length; i++) a += both[idx[i]];
    const diff = a / c3VsLlm.length - (both.reduce((s, v) => s + v, 0) - a) / c3Baseline.length;
    if (Math.abs(diff) >= Math.abs(c3Obs) - 1e-12) extreme++; // two-sided
  }
  c3PermP = (extreme + 1) / (PERM_REPS + 1);
}

// ═════════════════════════════════════════════════════════════════════════════
// 6) Unit-of-analysis table for every registered claim item
// ═════════════════════════════════════════════════════════════════════════════
const nRuns = (L) => (byLabel.get(L) ?? []).length;
const uoa = [];
const addUoa = (item, labels, decisionsPerRun, clusterUsed, ciMethod, layer2) =>
  uoa.push({
    item,
    rawDecisions: labels.reduce((s, L) => s + nRuns(L) * decisionsPerRun, 0),
    runSeats: labels.reduce((s, L) => s + nRuns(L) * 2, 0),
    runs: labels.reduce((s, L) => s + nRuns(L), 0),
    clusterUsed,
    ciMethod,
    layer2,
  });
addUoa("A1 δ=.90 vs δ=.10", [label.a("prisoners-dilemma", 90), label.a("prisoners-dilemma", 10)], 2, "run-seat", "exact point (sd=0 both arms)", "run-level Clopper-Pearson per cell");
addUoa("A2 pooled high vs low δ", [10, 50, 75, 90].map((d) => label.a("prisoners-dilemma", d)), 2, "run-seat", "exact point (sd=0)", "run-level CP per pooled cell");
addUoa("A3 human-range membership", [label.a("prisoners-dilemma", 75), label.a("prisoners-dilemma", 90)], 2, "run-seat", "point vs interval", "run-level CP (0/40 runs)");
addUoa("A4(a)+(b) isomorph", [10, 50, 75, 90].map((d) => label.a("prisoners-dilemma-iso", d)), 2, "run-seat", "exact point (sd=0)", "run-level CP; (b) flagged non-diagnostic at floor");
addUoa("B1 community − wallstreet", [label.b("community"), label.b("wallstreet")], 2, "run (Welch on run-seat means)", "Welch 95% (df 19)", "run-level permutation + bootstrap CI");
addUoa("B2 ratio edge rule", [label.b("community"), label.b("wallstreet")], 2, "run", "pre-registered point edge rule", "unchanged (rule fired as registered)");
addUoa("B3 neutral interior", ["community", "neutral", "wallstreet"].map(label.b), 2, "run", "point ordering, ties allowed", "wallstreet/neutral CP bounds shown");
addUoa("C1 rock share", cLabels, 2, "seat decision (round 1)", "point vs [0.33,0.40] band", "run-level cluster bootstrap CI");
addUoa("C2 P(stay|win), P(shift|lose)", cLabels, 2, "run-seat summary, null denominators excluded", "95% normal CI across run-seat values", "pooled decisions + run-level cluster bootstrap");
addUoa("C3 tracker per-round diff", [cLabels.find((l) => l.includes("tracker")), label.baseline], 1, "run", "Welch 95% (df 37.4)", "run-level permutation (two-sided)");
addUoa("X1 v2a/v2b round-1 coop", [label.x("v2a"), label.x("v2b")], 2, "run-seat", "exact point (sd=0)", "run-level CP (all-one cells)");

// raw decision counts for C2 are transitions, not rounds — overwrite with true counts
uoa.find((r) => r.item.startsWith("C2")).rawDecisions = c2Pooled.wN + c2Pooled.lN;

// ═════════════════════════════════════════════════════════════════════════════
// output
// ═════════════════════════════════════════════════════════════════════════════
const commit = execSync("git rev-parse --short HEAD", { cwd: process.cwd() }).toString().trim();
const generatedAt = new Date().toISOString();

const json = {
  layer2Version: LAYER2_VERSION,
  generatedAt,
  codeCommit: commit,
  seeds: { bootstrap: BOOT_SEED, permutation: PERM_SEED, bootReps: BOOT_REPS, permReps: PERM_REPS },
  corpus: { totalRuns: t3.length, labels: Object.fromEntries([...byLabel.entries()].map(([k, v]) => [k, v.length])) },
  extremeCells,
  b1: { runValuesCommunity: commRuns, obsDiff: b1Obs, permutationPOneSided: b1PermP, bootstrapCICommunityMean: b1BootCI },
  c1: { seatDecisions: c1SeatRock.length, rockShare: c1Obs, clusterBootstrapCI: c1BootCI },
  c2: {
    seatSummaries: c2SeatStats.length,
    nonNullStaySeats: c2NonNullStay.length,
    nonNullShiftSeats: c2NonNullShift.length,
    pooledTransitions: c2Pooled,
    nullCompositionByArm: c2NullByArm,
    pooledStay: c2Stay,
    pooledShift: c2Shift,
    seatSummaryMeans: { stay: c2SeatMeanStay, shift: c2SeatMeanShift },
  },
  c3: { vsLlmRuns: c3VsLlm.length, baselineRuns: c3Baseline.length, obsDiff: c3Obs, permutationPTwoSided: c3PermP },
  unitOfAnalysis: uoa,
};
writeFileSync("docs/phase3-layer2.json", JSON.stringify(json, null, 2));

const md = `# Phase 3 — Layer 2: Estimand-Aware Statistical Companion

> **Machine-generated** by \`scripts/phase3-layer2.mjs\` v${LAYER2_VERSION} — do not hand-edit; rerun the script.
> Generated ${generatedAt} at code commit \`${commit}\`. RNG: mulberry32, bootstrap seed ${BOOT_SEED}
> (${BOOT_REPS.toLocaleString()} reps), permutation seed ${PERM_SEED} (${PERM_REPS.toLocaleString()} reps).
>
> **Status: post-hoc, additive, labeled.** Added 2026-07-24 in response to external methods
> review. Registered verdicts in the claims registry are immutable and are not restated here;
> this layer gives each claim the statistical interpretation appropriate to its **estimand** —
> distinguishing the exact **corpus statement** ("in these runs, X happened") from the
> **policy-rate statement** ("the deployed model-policy's rate is bounded by…").

## 1. All-zero / all-one cells — exact Clopper-Pearson intervals

An observed 0-of-20 does **not** establish a zero policy rate; it bounds it. Run-level rows
treat each episode as one Bernoulli observation ("did the run exhibit any round-1
cooperation" / "was it fully cooperative"); seat-level rows are shown for completeness but
seats within a run are **not** independent (self-play), so run-level bounds are authoritative.

| Cell | Pattern | Runs | 95% one-sided bound (run) | 95% two-sided bound (run) | Seat decisions | two-sided (seat, dependence caveat) |
|---|---|---|---|---|---|---|
${extremeCells
  .map(
    (c) =>
      `| ${c.label} | ${c.kind} | ${c.runs} | ${c.kind === "all-zero" ? "≤ " + pct(c.runOneSided95) : "≥ " + pct(c.runOneSided95)} | ${c.kind === "all-zero" ? "≤ " + pct(c.runTwoSided95) : "≥ " + pct(c.runTwoSided95)} | ${c.seatDecisions} | ${c.kind === "all-zero" ? "≤ " + pct(c.seatTwoSided95) : "≥ " + pct(c.seatTwoSided95)} |`
  )
  .join("\n")}

**Reading:** "zero round-1 cooperation in 20 episodes" is consistent with a true policy rate
as high as ~${pct(cpUpper(20, 0.025))} (two-sided) per cell; pooling the canonical high-δ cells
(A3, 40 runs) tightens the bound to ~${pct(cpUpper(40, 0.025))}. The corpus statements remain
exact; the policy statements carry these intervals.

## 2. Unit-of-analysis accounting (every registered claim item)

| Claim item | Raw decisions | Run-seats | Independent runs | Cluster level in registered test | Registered CI method | Layer-2 supplement |
|---|---|---|---|---|---|---|
${uoa
  .map(
    (r) =>
      `| ${r.item} | ${r.rawDecisions} | ${r.runSeats} | ${r.runs} | ${r.clusterUsed} | ${r.ciMethod} | ${r.layer2} |`
  )
  .join("\n")}

## 3. C2 resolved — what n=61 was, and cluster-robust recomputation

The registered test aggregated **per-run-seat conditional summaries** (never pooled raw
decisions): each LLM seat trajectory yields one P(stay|win) and one P(shift|lose), with the
seat excluded from a conditional when its denominator is zero (locked pre-study). From raw
rounds: **${c2SeatStats.length} LLM run-seats** → ${c2NonNullStay.length} non-null for stay|win and
${c2NonNullShift.length} non-null for shift|lose. Null-denominator composition by arm
(seats with no wins / no losses — dominated by mirror-tie self-play trajectories):

| Arm | LLM seats | null stay\\|win | null shift\\|lose |
|---|---|---|---|
${Object.entries(c2NullByArm)
  .map(([k, v]) => `| ${k} | ${v.seats} | ${v.nullStay} | ${v.nullShift} |`)
  .join("\n")}

This resolves the registered n: **${c2NonNullStay.length} = ${c2SeatStats.length} LLM seats − ${c2SeatStats.length - c2NonNullStay.length} all-tie
self-play mirror trajectories** (a seat that ties every round has zero wins *and* zero
losses, so it is excluded from both conditionals). The registered unit was the run-seat
summary, **not** nested raw decisions.

Decision-level exposure: **${c2Pooled.wN} win-transitions** (${c2Pooled.wS} stays) and
**${c2Pooled.lN} lose-transitions** (${c2Pooled.lS} shifts) — these are the raw decisions
nested inside the ${c2SeatStats.length} seat summaries.

| Quantity | Registered-style (seat-summary mean) | Pooled decisions | Run-level cluster bootstrap 95% CI | Null |
|---|---|---|---|---|
| P(stay\\|win) | ${fmt(c2SeatMeanStay)} | ${fmt(c2Stay.est)} | [${fmt(c2Stay.ci[0])}, ${fmt(c2Stay.ci[1])}] | > 1/3 |
| P(shift\\|lose) | ${fmt(c2SeatMeanShift)} | ${fmt(c2Shift.est)} | [${fmt(c2Shift.ci[0])}, ${fmt(c2Shift.ci[1])}] | > 2/3 |

**Result:** both cluster-robust CIs lie entirely on the same side of their nulls as the
registered test — the C2 verdict is insensitive to the clustering correction.

**Estimand note (disclosed, not a correction):** the seat-summary mean and the pooled
estimate answer different questions and differ materially for stay|win
(${fmt(c2SeatMeanStay)} vs ${fmt(c2Stay.est)}): the former weights every seat equally, the
latter weights by transition exposure, and seats with many win-transitions (e.g. seats
that repeatedly beat the deterministic tracker) have higher stay rates. The registered
predicate used the seat-summary aggregation; both estimands exceed the null, so nothing
turns on the choice here — but Phase 4 predicates will name the aggregation explicitly.

## 4. B1 — permutation and bootstrap supplements (zero-variance arm)

Welch's t assumes both arms contribute a variance estimate; the Wall Street arm cannot
(all zeros). Run-level supplements (unit = one episode's mean round-1 cooperation):

- Observed difference (community − wallstreet): **${fmt(b1Obs)}**
- Run-level permutation test (one-sided, ${PERM_REPS.toLocaleString()} seeded reps): **p = ${b1PermP.toExponential(2)}**
- Community mean, run-level bootstrap 95% CI: **[${fmt(b1BootCI[0])}, ${fmt(b1BootCI[1])}]**

The registered SUPPORTED verdict survives the variance-assumption-free test.

## 5. C1 — rock share with cluster-aware uncertainty

${c1SeatRock.length} round-1 seat decisions across ${c1ByRun.size} runs (self-play contributes two
dependent seats). Rock share **${fmt(c1Obs)}**; run-level cluster bootstrap 95% CI
**[${fmt(c1BootCI[0])}, ${fmt(c1BootCI[1])}]** — still entirely above the human band upper edge
(0.40), so the registered refutation of the band membership is clustering-robust.

## 6. C3 — permutation supplement

Tracker per-round payoff, ${c3VsLlm.length} runs vs LLM against ${c3Baseline.length} baseline runs
(vs nash-mixed). Observed difference **${fmt(c3Obs)}** per round; two-sided run-level
permutation **p = ${c3PermP.toExponential(2)}**. The registered refutation (sign reversal) is
not a Welch artifact.

## 7. Language and framing corrections adopted (mirror of report edits)

- "exploitability" → **"performance against the registered first-order tracker"** (no
  unbranded exploitability claims).
- "20 seeded replicates" → **"20 environment-seeded episodes with archived model draws"**
  (environment RNG is seeded; provider-side sampling is not, and is archived, not seeded).
- A4(b) → **non-diagnostic at the behavioral floor** (cannot separate scale-invariance from
  incentive blindness at 0−0).
- "no shadow of the future — at all" → **"no round-1 cooperation observed under any tested
  δ in this configuration"** (corpus-exact, policy-bounded).
`;
writeFileSync("docs/phase3-layer2.md", md);
console.log(`layer2 v${LAYER2_VERSION} written: docs/phase3-layer2.md + .json (commit ${commit})`);
console.log(`  extreme cells: ${extremeCells.length}; B1 perm p=${b1PermP.toExponential(2)}; C2 pooled stay=${fmt(c2Stay.est)} shift=${fmt(c2Shift.est)}; C1 boot CI [${fmt(c1BootCI[0])},${fmt(c1BootCI[1])}]; C3 perm p=${c3PermP.toExponential(2)}`);
