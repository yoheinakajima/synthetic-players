/**
 * Phase 2 · Track 1 — counterfactual evidence pipeline (fork science).
 *
 * Honesty ordering: claims are PRE-REGISTERED (step "claims") before any fork
 * data exists (step "forks"), then mechanically adjudicated. Never reverse.
 *
 * Steps (all idempotent; safe to re-run):
 *   claims     pre-register fork-comparison claims (by title)
 *   forks      ensure parent batches, then create fork batches
 *   adjudicate adjudicate all claims, print verdict table
 *   backfill   materialize verified engine runs for the whole seeded corpus
 *              (drift detector; slow — run separately)
 *   all        claims → forks → adjudicate
 *
 * Usage: node scripts/run-phase2-track1.mjs [all|claims|forks|adjudicate|backfill]
 */

const BASE = process.env.API_BASE ?? "http://localhost:80/api";
const log = (...args) => console.log(new Date().toISOString().slice(11, 19), ...args);

async function api(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
    body: options.body ? JSON.stringify(options.body) : undefined,
  });
  const text = await res.text();
  if (!res.ok) throw new Error(`${options.method ?? "GET"} ${path} → ${res.status}: ${text.slice(0, 300)}`);
  return text ? JSON.parse(text) : null;
}

// ── Shared context ──────────────────────────────────────────────────────────

const FORK_ROUND = 25;
const LATE_FORK_ROUND = 40;
const PARENTS_LABEL = "prisoners-dilemma:tit-for-tat-vs-always-defect:fork-parents";
// 20 seeds: deterministic families collapse to identical replicates (sd=0),
// but stochastic swap-ins (generous TFT) need real replication for a CI.
const PARENT_SEEDS = Array.from({ length: 20 }, (_, i) => i + 1);
const RANDOM_PARENTS_LABEL = "prisoners-dilemma:tit-for-tat-vs-random:fork-parents";
const FORK_LABELS = {
  ac25: "pd:tft-vs-ad:fork-ac@25",
  tft25: "pd:tft-vs-ad:fork-tft@25",
  wsls25: "pd:tft-vs-ad:fork-wsls@25",
  gtft25: "pd:tft-vs-ad:fork-gtft@25",
  ac40: "pd:tft-vs-ad:fork-ac@40",
  rndAc25: "pd:tft-vs-rnd:fork-ac@25",
};

async function loadContext() {
  const [games, strategies, experiments] = await Promise.all([
    api("/games"),
    api("/strategies"),
    api("/experiments?status=completed"),
  ]);
  const pd = games.find((g) => g.slug === "prisoners-dilemma");
  const slug = Object.fromEntries(strategies.map((s) => [s.slug, s]));
  for (const need of [
    "tit-for-tat", "always-defect", "always-cooperate",
    "win-stay-lose-shift", "generous-tit-for-tat", "random",
  ]) {
    if (!slug[need]) throw new Error(`Strategy "${need}" missing`);
  }

  // Locate the existing PD tit-for-tat ⇄ random v2 batch and its seat order.
  const rndBatchExp = experiments.find(
    (e) =>
      e.batchLabel &&
      e.batchLabel.startsWith("prisoners-dilemma:") &&
      e.batchLabel.endsWith(":v2") &&
      e.batchLabel.includes("tit-for-tat") &&
      e.batchLabel.includes("random") &&
      !e.batchLabel.includes("generous")
  );
  let randomBatch;
  if (rndBatchExp) {
    const p1IsRandom = rndBatchExp.player1StrategyId === slug["random"].id;
    randomBatch = {
      label: rndBatchExp.batchLabel,
      p1Slug: p1IsRandom ? "random" : "tit-for-tat",
      p2Slug: p1IsRandom ? "tit-for-tat" : "random",
      randomSeat: p1IsRandom ? 1 : 2,
      mustCreate: false,
    };
  } else {
    // No TFT/Random pairing in the v2 corpus — this pipeline creates its own
    // parent batch (in the forks step, AFTER claims are pre-registered).
    randomBatch = {
      label: RANDOM_PARENTS_LABEL,
      p1Slug: "tit-for-tat",
      p2Slug: "random",
      randomSeat: 2,
      mustCreate: true,
    };
  }
  return { pd, slug, randomBatch };
}

// ── Step: claims (pre-registration) ─────────────────────────────────────────

async function preRegisterClaims(ctx) {
  const { pd, randomBatch } = ctx;
  const parentScope = {
    gameId: pd.id,
    player1StrategySlug: "tit-for-tat",
    player2StrategySlug: "always-defect",
    batchLabel: PARENTS_LABEL,
  };
  const item = (metric, op, threshold, extra = {}) => ({ metric, op, threshold, ...extra });
  const forkItem = (forkPatch, metric, op, threshold, extra = {}) =>
    item(metric, op, threshold, { ...extra, scope: { fork: { forkRound: FORK_ROUND, ...forkPatch } } });

  const claims = [
    {
      title: "Unconditional cooperation rescues welfare after mutual defection",
      statement:
        `In iterated PD (TFT vs Always Defect, locked in mutual defection), replacing the defector ` +
        `with Always Cooperate at round ${FORK_ROUND} recovers at least 80% of the post-fork welfare gap to mutual cooperation.`,
      predicate: {
        scope: parentScope,
        all: [
          forkItem(
            { player2StrategySlug: "always-cooperate", batchLabel: FORK_LABELS.ac25 },
            "postFork.welfareRecoveryFrac", ">=", 0.8,
            { label: "AC swap recovers ≥80% of the welfare gap" }
          ),
        ],
      },
    },
    {
      title: "Tit-for-Tat cannot restart cooperation from a defection history (echo trap)",
      statement:
        `Replacing Always Defect with a second Tit-for-Tat at round ${FORK_ROUND} does NOT restore cooperation: ` +
        `both TFTs echo the inherited defection forever. Predicted recovery ≤5% and post-fork mutual cooperation ≤2%.`,
      predicate: {
        scope: parentScope,
        all: [
          forkItem(
            { player2StrategySlug: "tit-for-tat", batchLabel: FORK_LABELS.tft25 },
            "postFork.welfareRecoveryFrac", "<=", 0.05,
            { label: "TFT swap recovers ≤5% of the welfare gap" }
          ),
          forkItem(
            { player2StrategySlug: "tit-for-tat", batchLabel: FORK_LABELS.tft25 },
            "postFork.mutualCoopRateFork", "<=", 0.02,
            { label: "post-fork mutual cooperation ≤2%" }
          ),
        ],
      },
    },
    {
      title: "Win-Stay-Lose-Shift only partially escapes mutual defection",
      statement:
        `Replacing Always Defect with Win-Stay-Lose-Shift at round ${FORK_ROUND} against TFT produces a persistent ` +
        `exploit cycle rather than stable cooperation: predicted welfare recovery between 30% and 70%.`,
      predicate: {
        scope: parentScope,
        all: [
          forkItem(
            { player2StrategySlug: "win-stay-lose-shift", batchLabel: FORK_LABELS.wsls25 },
            "postFork.welfareRecoveryFrac", "between", 0.3,
            { thresholdHigh: 0.7, label: "WSLS swap recovers 30–70% of the welfare gap" }
          ),
        ],
      },
    },
    {
      title: "Generosity is the minimal rescue: Generous TFT restores cooperation where strict TFT fails",
      statement:
        `Replacing Always Defect with Generous Tit-for-Tat at round ${FORK_ROUND} breaks the defection echo through ` +
        `forgiveness and recovers at least 80% of the post-fork welfare gap — the strict-TFT swap (see echo-trap claim) cannot.`,
      predicate: {
        scope: parentScope,
        all: [
          forkItem(
            { player2StrategySlug: "generous-tit-for-tat", batchLabel: FORK_LABELS.gtft25 },
            "postFork.welfareRecoveryFrac", ">=", 0.8,
            { label: "GTFT swap recovers ≥80% of the welfare gap" }
          ),
        ],
      },
    },
    {
      title: "Rescue timing barely changes per-round recovery efficiency",
      statement:
        `Switching Always Defect to Always Cooperate rescues welfare at the same per-round efficiency whether it ` +
        `happens at round ${FORK_ROUND} or round ${LATE_FORK_ROUND} of 50: recovery ≥90% of the gap in both cases.`,
      predicate: {
        scope: parentScope,
        all: [
          forkItem(
            { player2StrategySlug: "always-cooperate", batchLabel: FORK_LABELS.ac25 },
            "postFork.welfareRecoveryFrac", ">=", 0.9,
            { label: `AC swap at round ${FORK_ROUND}: recovery ≥90%` }
          ),
          item("postFork.welfareRecoveryFrac", ">=", 0.9, {
            label: `AC swap at round ${LATE_FORK_ROUND}: recovery ≥90%`,
            scope: {
              fork: {
                forkRound: LATE_FORK_ROUND,
                player2StrategySlug: "always-cooperate",
                batchLabel: FORK_LABELS.ac40,
              },
            },
          }),
        ],
      },
    },
  ];

  {
    const swapSeatSlugKey = randomBatch.randomSeat === 1 ? "player1StrategySlug" : "player2StrategySlug";
    claims.push({
      title: "Replacing noise with commitment recovers most of the cooperative gap",
      statement:
        `In iterated PD (TFT vs Random across 20 seeds), replacing the random player with Always Cooperate at ` +
        `round ${FORK_ROUND} recovers at least half of the post-fork welfare gap (95% CI over paired replicates).`,
      predicate: {
        scope: {
          gameId: pd.id,
          player1StrategySlug: randomBatch.p1Slug,
          player2StrategySlug: randomBatch.p2Slug,
          batchLabel: randomBatch.label,
        },
        minExperiments: 10,
        all: [
          forkItem(
            { [swapSeatSlugKey]: "always-cooperate", batchLabel: FORK_LABELS.rndAc25 },
            "postFork.welfareRecoveryFrac", ">=", 0.5,
            { label: "AC-for-Random swap recovers ≥50% of the welfare gap" }
          ),
        ],
      },
    });
  }

  const existing = await api("/claims");
  const byTitle = new Map(existing.map((c) => [c.title, c]));
  let created = 0, skipped = 0;
  for (const c of claims) {
    if (byTitle.has(c.title)) { skipped++; continue; }
    await api("/claims", {
      method: "POST",
      body: {
        title: c.title,
        statement: c.statement,
        gameId: c.predicate.scope.gameId,
        predicateJson: JSON.stringify(c.predicate),
      },
    });
    created++;
    log(`  pre-registered: ${c.title}`);
  }
  log(`Step claims: ${created} created, ${skipped} already present (untouched)`);
}

// ── Step: forks ──────────────────────────────────────────────────────────────

async function createForks(ctx) {
  const { pd, slug, randomBatch } = ctx;

  // Parent batch for the deterministic family (idempotent batch endpoint).
  const batch = await api("/experiments/batch", {
    method: "POST",
    body: {
      gameId: pd.id,
      player1StrategyId: slug["tit-for-tat"].id,
      player2StrategyId: slug["always-defect"].id,
      numRounds: 50,
      seeds: PARENT_SEEDS,
      batchLabel: PARENTS_LABEL,
    },
  });
  log(`Step forks: parents ready (${batch.experimentIds?.length ?? 0} new, ${batch.skippedSeeds?.length ?? 0} existing)`);

  if (randomBatch.mustCreate) {
    const rb = await api("/experiments/batch", {
      method: "POST",
      body: {
        gameId: pd.id,
        player1StrategyId: slug[randomBatch.p1Slug].id,
        player2StrategyId: slug[randomBatch.p2Slug].id,
        numRounds: 50,
        seeds: PARENT_SEEDS,
        batchLabel: randomBatch.label,
      },
    });
    log(`  random parents ready (${rb.experimentIds?.length ?? 0} new, ${rb.skippedSeeds?.length ?? 0} existing)`);
  }

  const forkBatches = [
    { batchLabel: PARENTS_LABEL, forkRound: FORK_ROUND, player2StrategyId: slug["always-cooperate"].id, forkBatchLabel: FORK_LABELS.ac25 },
    { batchLabel: PARENTS_LABEL, forkRound: FORK_ROUND, player2StrategyId: slug["tit-for-tat"].id, forkBatchLabel: FORK_LABELS.tft25 },
    { batchLabel: PARENTS_LABEL, forkRound: FORK_ROUND, player2StrategyId: slug["win-stay-lose-shift"].id, forkBatchLabel: FORK_LABELS.wsls25 },
    { batchLabel: PARENTS_LABEL, forkRound: FORK_ROUND, player2StrategyId: slug["generous-tit-for-tat"].id, forkBatchLabel: FORK_LABELS.gtft25 },
    { batchLabel: PARENTS_LABEL, forkRound: LATE_FORK_ROUND, player2StrategyId: slug["always-cooperate"].id, forkBatchLabel: FORK_LABELS.ac40 },
  ];
  forkBatches.push({
    batchLabel: randomBatch.label,
    forkRound: FORK_ROUND,
    [randomBatch.randomSeat === 1 ? "player1StrategyId" : "player2StrategyId"]: slug["always-cooperate"].id,
    forkBatchLabel: FORK_LABELS.rndAc25,
  });

  for (const fb of forkBatches) {
    const r = await api("/experiments/fork-batch", { method: "POST", body: fb });
    log(
      `  ${fb.forkBatchLabel}: ${r.created.length} created, ${r.skippedParents.length} skipped` +
        (r.failed.length ? `, ${r.failed.length} FAILED (${r.failed[0].error.slice(0, 120)})` : "")
    );
    if (r.failed.length) process.exitCode = 1;
  }
}

// ── Step: adjudicate ────────────────────────────────────────────────────────

async function adjudicate() {
  const results = await api("/claims/adjudicate-all", { method: "POST" });
  const counts = {};
  for (const r of results) counts[r.status] = (counts[r.status] ?? 0) + 1;
  log(`Step adjudicate: ${JSON.stringify(counts)}`);

  const claims = await api("/claims");
  const byId = new Map(claims.map((c) => [c.id, c]));
  for (const r of results) {
    const claim = byId.get(r.claimId);
    const isForkClaim = claim?.predicateJson?.includes('"fork"');
    if (!isForkClaim) continue;
    log(`  [${r.status.toUpperCase()}] ${claim.title}`);
    const adj = claim?.adjudicationJson ? JSON.parse(claim.adjudicationJson) : null;
    for (const it of adj?.items ?? []) {
      log(
        `      ${it.verdict}: ${it.label} — observed ${it.mean?.toFixed(4) ?? "n/a"}` +
          (it.ciLow != null ? ` CI [${it.ciLow.toFixed(4)}, ${it.ciHigh.toFixed(4)}]` : "") +
          ` (n=${it.n}, ${it.op} ${it.threshold}${it.thresholdHigh != null ? `–${it.thresholdHigh}` : ""})`
      );
    }
  }
}

// ── Step: backfill (whole-corpus drift check; slow) ─────────────────────────

async function backfill() {
  const experiments = await api("/experiments?status=completed");
  const targets = experiments.filter(
    (e) => e.parentExperimentId == null && e.seed != null && !e.engineRunId
  );
  const unseeded = experiments.filter((e) => e.parentExperimentId == null && e.seed == null).length;
  log(`Step backfill: ${targets.length} to materialize (${unseeded} unseeded legacy runs stay as-is)`);

  let ok = 0, drift = 0, failed = 0;
  const queue = [...targets];
  const workers = Array.from({ length: 4 }, async () => {
    while (queue.length > 0) {
      const exp = queue.shift();
      try {
        await api(`/experiments/${exp.id}/engine-run`, { method: "POST" });
        ok++;
      } catch (err) {
        if (String(err.message).includes("409")) {
          drift++;
          log(`  DRIFT ALARM on experiment ${exp.id}: ${err.message.slice(0, 200)}`);
        } else {
          failed++;
          log(`  failed ${exp.id}: ${err.message.slice(0, 120)}`);
        }
      }
      if ((ok + drift + failed) % 50 === 0) log(`  progress: ${ok + drift + failed}/${targets.length}`);
    }
  });
  await Promise.all(workers);
  log(`  done: ${ok} materialized, ${drift} DRIFT, ${failed} failed`);
  if (drift > 0) {
    log("  ⚠ Determinism drift detected — stored data no longer reproduces on the engine. Investigate before trusting new runs.");
    process.exitCode = 1;
  }
}

// ── Main ────────────────────────────────────────────────────────────────────

const step = process.argv[2] ?? "all";
const ctx = await loadContext();
if (step === "claims" || step === "all") await preRegisterClaims(ctx);
if (step === "forks" || step === "all") await createForks(ctx);
if (step === "adjudicate" || step === "all") await adjudicate();
if (step === "backfill") await backfill();
log("Phase 2 · Track 1 pipeline finished.");
