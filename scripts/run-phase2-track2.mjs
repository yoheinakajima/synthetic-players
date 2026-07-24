/**
 * Phase 2 · Track 2 — LLM-backed strategies with event-sourced decisions.
 *
 * Design: GPT-5 Mini (via Replit AI Integrations, prompt iterated-game-player-v1)
 * plays player 1 in iterated Prisoner's Dilemma (20 rounds, horizon disclosed)
 * against three deterministic opponents, n=6 replicates each:
 *   tit-for-tat, always-defect, grim-trigger
 *
 * Honesty ordering: claims are PRE-REGISTERED (step "claims") before any LLM
 * data exists (step "runs"), then mechanically adjudicated. Never reverse.
 * The claims step ABORTS if the target batches already contain data and the
 * claims are not yet registered — that would be post-hoc claim writing.
 *
 * LLM runs are sampled behavior (provider pins temperature for gpt-5 family),
 * NOT seed-reproducible; they are event-sourced instead. Claims therefore
 * aggregate across replicates with CIs — never single anecdotes.
 *
 * Steps (all idempotent; safe to re-run):
 *   claims     pre-register the four T2 claims (by title)
 *   runs       top up each matchup to n=6 completed runs (resumable; each
 *              invocation continues where the last stopped — LLM runs are
 *              slow, ~2-3 min per 20-round game)
 *   adjudicate adjudicate all claims, print T2 verdicts + verdict-flip audit
 *              of pre-existing claims (disclosure requirement)
 *   all        claims → runs → adjudicate
 *
 * Usage: node scripts/run-phase2-track2.mjs [all|claims|runs|adjudicate]
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

// ── Shared study design ─────────────────────────────────────────────────────

const LLM_SLUG = "llm-gpt-5-mini";
const NUM_ROUNDS = 20;
const N_REPLICATES = 6;
const SEEDS = [1, 2, 3, 4, 5, 6];
const MATCHUPS = [
  { opp: "tit-for-tat", label: "prisoners-dilemma:llm-vs-tit-for-tat:t2" },
  { opp: "always-defect", label: "prisoners-dilemma:llm-vs-always-defect:t2" },
  { opp: "grim-trigger", label: "prisoners-dilemma:llm-vs-grim-trigger:t2" },
];

async function loadContext() {
  const [games, strategies, experiments] = await Promise.all([
    api("/games"),
    api("/strategies"),
    api("/experiments"),
  ]);
  const pd = games.find((g) => g.slug === "prisoners-dilemma");
  if (!pd) throw new Error("prisoners-dilemma game missing");
  const slug = Object.fromEntries(strategies.map((s) => [s.slug, s]));
  for (const need of [LLM_SLUG, ...MATCHUPS.map((m) => m.opp)]) {
    if (!slug[need]) throw new Error(`Strategy "${need}" missing`);
  }
  return { pd, slug, experiments };
}

const completedIn = (experiments, label) =>
  experiments.filter((e) => e.batchLabel === label && e.status === "completed");

// ── Step: claims (pre-registration) ─────────────────────────────────────────

function t2Claims(pd) {
  const scope = (opp, label) => ({
    gameId: pd.id,
    player1StrategySlug: LLM_SLUG,
    player2StrategySlug: opp,
    batchLabel: label,
    focusStrategySlug: LLM_SLUG,
  });
  const provenance =
    `GPT-5 Mini via Replit AI Integrations, prompt iterated-game-player-v1, ` +
    `${NUM_ROUNDS}-round iterated PD with the horizon disclosed, n=${N_REPLICATES} event-sourced replicates.`;

  return [
    {
      title: "LLM (GPT-5 Mini) sustains mutual cooperation with Tit-for-Tat in iterated PD",
      statement:
        `Playing ${provenance} Against Tit-for-Tat, the LLM establishes and sustains reciprocal cooperation: ` +
        `mean mutual-cooperation rate ≥ 50% of rounds across replicates, despite the known end-game defection incentive.`,
      predicate: {
        scope: scope("tit-for-tat", MATCHUPS[0].label),
        minExperiments: N_REPLICATES,
        all: [
          {
            metric: "mutualCooperationRate",
            op: ">=",
            threshold: 0.5,
            label: "mean mutual cooperation ≥50% of rounds vs TFT",
          },
        ],
      },
    },
    {
      title: "LLM (GPT-5 Mini) does not exploitably cooperate against Always Defect",
      statement:
        `Playing ${provenance} Against Always Defect, the LLM recognizes relentless defection and stops offering ` +
        `cooperation: its mean cooperation rate stays ≤ 30% of rounds (occasional early probes allowed).`,
      predicate: {
        scope: scope("always-defect", MATCHUPS[1].label),
        minExperiments: N_REPLICATES,
        all: [
          {
            metric: "actionCooperationRateFocus",
            op: "<=",
            threshold: 0.3,
            label: "LLM cooperation rate ≤30% vs Always Defect",
          },
        ],
      },
    },
    {
      title: "LLM (GPT-5 Mini) approaches best-response payoff against Always Defect",
      statement:
        `Playing ${provenance} Against Always Defect the best response is to always defect (1.0/round; each ` +
        `cooperative probe costs 1). The LLM averages ≥ 0.85/round, i.e. it forfeits at most ~3 rounds' worth of probes.`,
      predicate: {
        scope: scope("always-defect", MATCHUPS[1].label),
        minExperiments: N_REPLICATES,
        all: [
          {
            metric: "avgPayoffPerRoundFocus",
            op: ">=",
            threshold: 0.85,
            label: "LLM payoff ≥0.85/round vs Always Defect (best response = 1.0)",
          },
        ],
      },
    },
    {
      title: "LLM (GPT-5 Mini) preserves cooperation against Grim Trigger",
      statement:
        `Playing ${provenance} Against Grim Trigger a single defection destroys all future cooperation. The LLM ` +
        `avoids triggering it long enough to keep mean mutual cooperation ≥ 50% of rounds across replicates.`,
      predicate: {
        scope: scope("grim-trigger", MATCHUPS[2].label),
        minExperiments: N_REPLICATES,
        all: [
          {
            metric: "mutualCooperationRate",
            op: ">=",
            threshold: 0.5,
            label: "mean mutual cooperation ≥50% of rounds vs Grim Trigger",
          },
        ],
      },
    },
  ];
}

async function preRegisterClaims(ctx) {
  const { pd, experiments } = ctx;
  const claims = t2Claims(pd);
  const existing = await api("/claims");
  const byTitle = new Map(existing.map((c) => [c.title, c]));

  // Pre-registration guard: creating a claim whose target batch already has
  // data would be post-hoc claiming — refuse loudly.
  for (const m of MATCHUPS) {
    const have = completedIn(experiments, m.label).length;
    const claimsForBatch = claims.filter((c) => c.predicate.scope.batchLabel === m.label);
    const unregistered = claimsForBatch.filter((c) => !byTitle.has(c.title));
    if (have > 0 && unregistered.length > 0) {
      throw new Error(
        `PRE-REGISTRATION VIOLATION: batch "${m.label}" already has ${have} completed runs ` +
          `but ${unregistered.length} claim(s) for it are not registered. Refusing to write post-hoc claims.`
      );
    }
  }

  let created = 0, skipped = 0;
  for (const c of claims) {
    if (byTitle.has(c.title)) { skipped++; continue; }
    await api("/claims", {
      method: "POST",
      body: {
        title: c.title,
        statement: c.statement,
        gameId: pd.id,
        predicateJson: JSON.stringify(c.predicate),
      },
    });
    created++;
    log(`  pre-registered: ${c.title}`);
  }
  log(`Step claims: ${created} created, ${skipped} already present (untouched)`);
}

// ── Step: runs (resumable) ──────────────────────────────────────────────────

async function runStudy(ctx) {
  const { pd, slug } = ctx;

  // Reverse-order guard: never generate data before the claims exist.
  const registered = new Map((await api("/claims")).map((c) => [c.title, c]));
  const missing = t2Claims(pd).filter((c) => !registered.has(c.title));
  if (missing.length > 0) {
    throw new Error(
      `Claims not pre-registered (${missing.length} missing) — run the "claims" step first.`
    );
  }

  for (const m of MATCHUPS) {
    // Fresh state each matchup: earlier invocations (or a timed-out shell
    // whose server-side run still finished) may have completed seeds already.
    // A seed is CLAIMED by any non-failed experiment: a "running" row from a
    // killed client usually still completes server-side, so re-creating its
    // seed would produce duplicate replicates. Only a failed row frees a seed.
    const all = await api("/experiments");
    const inBatch = all.filter((e) => e.batchLabel === m.label);
    const done = inBatch.filter((e) => e.status === "completed");
    const claimedSeeds = new Set(inBatch.filter((e) => e.status !== "failed").map((e) => e.seed));
    const inFlight = inBatch.filter((e) => e.status === "running" || e.status === "pending");
    if (inFlight.length > 0) {
      log(
        `  note: ${inFlight.length} in-flight run(s) [${inFlight.map((e) => `EXP-${e.id} seed ${e.seed}`).join(", ")}] — ` +
          `their seeds stay claimed; re-invoke later if one is permanently stuck`
      );
    }
    const todo = SEEDS.filter((s) => !claimedSeeds.has(s)).slice(
      0,
      Math.max(0, N_REPLICATES - done.length - inFlight.length)
    );
    log(`${m.label}: ${done.length}/${N_REPLICATES} completed, running ${todo.length} more`);

    for (const seed of todo) {
      const t0 = Date.now();
      const created = await api("/experiments", {
        method: "POST",
        body: {
          gameId: pd.id,
          player1StrategyId: slug[LLM_SLUG].id,
          player2StrategyId: slug[m.opp].id,
          numRounds: NUM_ROUNDS,
          seed,
          batchLabel: m.label,
          notes: `T2 replicate seed ${seed}: ${LLM_SLUG} vs ${m.opp} (${NUM_ROUNDS} rounds, horizon disclosed)`,
        },
      });
      try {
        const run = await api(`/experiments/${created.id}/run`, { method: "POST" });
        const meta = run.llmMetaJson ? JSON.parse(run.llmMetaJson) : {};
        log(
          `  seed ${seed}: EXP-${created.id} completed in ${((Date.now() - t0) / 1000).toFixed(0)}s ` +
            `(coop=${run.cooperationRate?.toFixed(2)}, ${meta.llmCalls ?? "?"} calls, ` +
            `${meta.retriedCalls ?? 0} retried)`
        );
      } catch (err) {
        log(`  seed ${seed}: EXP-${created.id} FAILED — ${err.message.slice(0, 200)}`);
        process.exitCode = 1;
      }
    }
  }

  const finalState = await api("/experiments");
  const summary = MATCHUPS.map(
    (m) => `${m.label}: ${completedIn(finalState, m.label).length}/${N_REPLICATES}`
  ).join(" | ");
  log(`Step runs: ${summary}`);
}

// ── Step: adjudicate (+ verdict-flip audit) ─────────────────────────────────

async function adjudicate(ctx) {
  const before = new Map((await api("/claims")).map((c) => [c.id, c.status]));
  const results = await api("/claims/adjudicate-all", { method: "POST" });
  const counts = {};
  for (const r of results) counts[r.status] = (counts[r.status] ?? 0) + 1;
  log(`Step adjudicate: ${JSON.stringify(counts)}`);

  const claims = await api("/claims");
  const t2Titles = new Set(t2Claims(ctx.pd).map((c) => c.title));

  for (const claim of claims.filter((c) => t2Titles.has(c.title))) {
    log(`  [${claim.status.toUpperCase()}] ${claim.title}`);
    const adj = claim.adjudicationJson ? JSON.parse(claim.adjudicationJson) : null;
    for (const it of adj?.items ?? []) {
      log(
        `      ${it.verdict}: ${it.label} — observed ${it.mean?.toFixed(4) ?? "n/a"}` +
          (it.ciLow != null ? ` CI [${it.ciLow.toFixed(4)}, ${it.ciHigh.toFixed(4)}]` : "") +
          ` (n=${it.n}, ${it.op} ${it.threshold}${it.thresholdHigh != null ? `–${it.thresholdHigh}` : ""})`
      );
    }
  }

  // Verdict-flip audit: LLM data entering the corpus may change the evidence
  // set of ANY pre-existing claim whose scope does not pin strategies or a
  // batch. Disclose every flip rather than silently absorbing it.
  const flips = claims.filter(
    (c) => !t2Titles.has(c.title) && before.has(c.id) && before.get(c.id) !== c.status
  );
  if (flips.length === 0) {
    log("  Verdict-flip audit: no pre-existing claim changed verdict.");
  } else {
    log(`  ⚠ Verdict-flip audit: ${flips.length} pre-existing claim(s) changed verdict:`);
    for (const c of flips) log(`      ${before.get(c.id)} → ${c.status}: ${c.title}`);
  }
}

// ── Main ────────────────────────────────────────────────────────────────────

const step = process.argv[2] ?? "all";
const ctx = await loadContext();
if (step === "claims" || step === "all") await preRegisterClaims(ctx);
if (step === "runs" || step === "all") await runStudy(ctx);
if (step === "adjudicate" || step === "all") await adjudicate(ctx);
log("Phase 2 · Track 2 pipeline finished.");
