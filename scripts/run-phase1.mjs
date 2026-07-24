#!/usr/bin/env node
/**
 * Phase 1 execution driver:
 *   1. Recompute v2 analyses for ALL completed experiments (baseline recalibration)
 *   2. Run 20-seed batches for every matchup involving a probabilistic strategy
 *   3. Mechanically adjudicate all claims
 *   4. Generate paper v2
 *
 * Idempotent-ish: batches are skipped if their batchLabel already has experiments.
 */

const BASE = process.env.API_BASE ?? "http://localhost:80/api";
const SEEDS = Array.from({ length: 20 }, (_, i) => i + 1);
const PROBABILISTIC = new Set(["random", "nash-mixed", "generous-tit-for-tat"]);

async function api(path, opts = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...opts,
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`${opts.method ?? "GET"} ${path} → ${res.status}: ${body.slice(0, 300)}`);
  }
  return res.status === 204 ? null : res.json();
}

const log = (...args) => console.log(new Date().toISOString().slice(11, 19), ...args);

// ── Step 1: recompute v2 analyses for all completed experiments ────────────
async function recomputeAnalyses() {
  const experiments = await api("/experiments?status=completed");
  log(`Step 1: recomputing v2 analyses for ${experiments.length} completed experiments`);
  let ok = 0, failed = 0;
  for (const exp of experiments) {
    try {
      await api(`/experiments/${exp.id}/analysis`, { method: "POST" });
      ok++;
    } catch (err) {
      failed++;
      log(`  analysis failed for experiment ${exp.id}: ${err.message}`);
    }
  }
  log(`  done: ${ok} ok, ${failed} failed`);
}

// ── Step 2: seeded batches for probabilistic matchups ──────────────────────
async function runBatches() {
  const [experiments, strategies, games] = await Promise.all([
    api("/experiments?status=completed"),
    api("/strategies"),
    api("/games"),
  ]);
  const stratById = new Map(strategies.map((s) => [s.id, s]));
  const gameById = new Map(games.map((g) => [g.id, g]));

  // Distinct matchups involving ≥1 probabilistic strategy (unordered pair)
  const seen = new Map();
  for (const exp of experiments) {
    const s1 = stratById.get(exp.player1StrategyId);
    const s2 = stratById.get(exp.player2StrategyId);
    if (!s1 || !s2) continue;
    if (!PROBABILISTIC.has(s1.slug) && !PROBABILISTIC.has(s2.slug)) continue;
    const [aId, bId] = s1.id <= s2.id ? [s1.id, s2.id] : [s2.id, s1.id];
    const key = `${exp.gameId}|${aId}|${bId}`;
    if (!seen.has(key)) {
      seen.set(key, { gameId: exp.gameId, p1: aId, p2: bId, numRounds: exp.numRounds });
    }
  }

  log(`Step 2: ${seen.size} probabilistic matchups to replicate across ${SEEDS.length} seeds`);

  let ran = 0, skipped = 0;
  for (const [, m] of seen) {
    const game = gameById.get(m.gameId);
    const s1 = stratById.get(m.p1);
    const s2 = stratById.get(m.p2);
    const batchLabel = `${game.slug}:${s1.slug}-vs-${s2.slug}:v2`;

    // The batch endpoint is idempotent per (matchup, batchLabel, seed): it
    // runs only missing seeds and reports the rest in skippedSeeds, so a
    // partially completed batch is safely filled in on re-run.
    const t0 = Date.now();
    const result = await api("/experiments/batch", {
      method: "POST",
      body: JSON.stringify({
        gameId: m.gameId,
        player1StrategyId: m.p1,
        player2StrategyId: m.p2,
        numRounds: m.numRounds,
        seeds: SEEDS,
        batchLabel,
      }),
    });
    if (result.experimentIds.length === 0) {
      skipped++;
      log(`  skip ${batchLabel} (all ${result.skippedSeeds.length} seeds already run)`);
      continue;
    }
    ran++;
    log(`  ${batchLabel}: ${result.experimentIds.length} new replicates (${result.skippedSeeds.length} existing) in ${((Date.now() - t0) / 1000).toFixed(1)}s`);
  }
  log(`  done: ${ran} batches run, ${skipped} skipped`);
}

// ── Step 3: adjudicate all claims ───────────────────────────────────────────
async function adjudicate() {
  log("Step 3: adjudicating all claims");
  const results = await api("/claims/adjudicate-all", { method: "POST" });
  for (const r of results) {
    log(`  #${r.claimId} [${r.status.toUpperCase()}] ${r.title}`);
    if (r.note) log(`      ${r.note.slice(0, 220)}`);
  }
  return results;
}

// ── Step 4: generate paper v2 ───────────────────────────────────────────────
async function generatePaper() {
  log("Step 4: generating paper v2");
  const paper = await api("/papers", {
    method: "POST",
    body: JSON.stringify({
      title:
        "Seeded, Replicated, and Mechanically Adjudicated: Algorithmic Behavior Across Three Game Classes (v2)",
    }),
  });
  log(`  paper #${paper.id} generated, ${paper.wordCount} words`);
  return paper;
}

const steps = process.argv[2] ?? "all";
if (steps === "all" || steps === "1") await recomputeAnalyses();
if (steps === "all" || steps === "2") await runBatches();
if (steps === "all" || steps === "3") await adjudicate();
if (steps === "all" || steps === "4") await generatePaper();
log("Phase 1 execution complete.");
