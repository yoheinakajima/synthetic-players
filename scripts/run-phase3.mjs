/**
 * Phase 3 — LLM as Behavioral Subject (pre-registered study).
 *
 * Design doc: docs/phase3-preregistration.md (signed off: gpt-4.1 @ temp 0.7).
 * Subject: llm-gpt-4.1 via the engine-live path (ENGINE drives the LLM loop,
 * event-sources every prompt/response, replay-verifiable with zero live calls).
 *
 * Families:
 *   A  Random-termination repeated PD, LLM self-play, δ ∈ {.10,.50,.75,.90},
 *      canonical + payoff-isomorph arms (8 batches × 20 supergames).
 *      Horizon drawn CLIENT-SIDE: mulberry32(seed ^ 0x54524D), rounds=1,
 *      while rng()<δ rounds++, safety cap 120 (hit ⇒ truncated ⇒ excluded,
 *      disclosed; P≈3e-6). Realized length is hidden from the subject.
 *   B  One-shot PD framing (community/wallstreet/neutral), self-play, n=20 each.
 *   C  RPS 50 rounds × 20: vs pattern-tracker, vs nash-mixed, self-play,
 *      plus the zero-LLM baseline pattern-tracker-vs-nash-mixed.
 *
 * Honesty ordering (enforced, never reversed):
 *   1. claims — all 10 predicates pre-registered BEFORE any :t3 row exists.
 *   2. runs   — resumable seeded replicates under hard budget caps
 *               (A 1,800 / B 160 / C 4,400; global kill-switch 6,360 calls).
 *               Invalid trials keep their seed claimed and are replaced from
 *               the reserved pool (seed 1000+k, once). Budget counts EVERY
 *               recorded llmCall, including invalid trials.
 *   3. verify — zero-live-call replay + metric recomputation of every
 *               completed Phase 3 row; prompt-registry SHA pinned.
 *   4. adjudicate — mechanical verdicts + verdict-flip audit of ALL
 *               pre-existing claims (disclosure requirement).
 *
 * Steps: claims | runs | verify | adjudicate | status | all
 *        xclaims | xruns — Extension X1 (paraphrase robustness, registry phase3-v2)
 * Usage: node scripts/run-phase3.mjs [step]
 * Long runs: setsid nohup node scripts/run-phase3.mjs all > /tmp/phase3.log 2>&1 &
 */

const BASE = process.env.API_BASE ?? "http://localhost:80/api";
const ENGINE = process.env.ENGINE_BASE ?? "http://127.0.0.1:8090";
const REGISTRY_SHA = "73e7a6cac07c83b49985ab3e36edd9d83a4916a41eade624c807ae0307bdc262";
// Extension X1: registry phase3-v2 = phase3-v1 + appended pd-repeated-v2a/v2b.
// Original prompt specs byte-identical; replay of the sealed t3 corpus verifies
// per-prompt hashes (whole-file sha is informational under append-only policy).
const REGISTRY_SHA_X = "808f205a192909e8c2ac1c1ec6210c650017c297978afeb0b899873ea9ae1fc2";

const LLM = "llm-gpt-4.1";
const TRACKER = "pattern-tracker";
const NASH = "nash-mixed";
const SEEDS = Array.from({ length: 20 }, (_, i) => i + 1);
const REPLACEMENT_OFFSET = 1000; // reserved pool for invalid trials (once per seed)
const TEMPERATURE = 0.7;
const MAX_TOKENS = 16;
const HORIZON_RULE = "geometric-mulberry32-cap120"; // draw: mulberry32(seed ^ 0x54524D)
const CAPS = { A: 1800, B: 160, C: 4400, X: 1600, global: 7960 }; // X + amended global per prereg Extension X1
const BASELINE_LABEL = "rock-paper-scissors:pattern-tracker-vs-nash-mixed:t3-baseline";

const log = (...a) => console.log(new Date().toISOString().slice(11, 19), ...a);
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

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

// ── Deterministic horizon draw (family A) ───────────────────────────────────
// Bit-identical mulberry32 (same algorithm as engine/strategies.py port).

function mulberry32(seed) {
  let a = seed >>> 0;
  return function () {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function drawHorizon(seed, deltaPct) {
  const rng = mulberry32((seed ^ 0x54524d) >>> 0);
  const delta = deltaPct / 100;
  let rounds = 1;
  while (rng() < delta) {
    rounds++;
    if (rounds >= 120) return { rounds: 120, truncated: true };
  }
  return { rounds, truncated: false };
}

// ── Study design ────────────────────────────────────────────────────────────

const A_DELTAS = [10, 50, 75, 90];
const A_ARMS = ["prisoners-dilemma", "prisoners-dilemma-iso"];
const B_FRAMINGS = ["community", "wallstreet", "neutral"];

const aLabel = (arm, d) => `${arm}:llm41-selfplay:d${d}:t3`;
const bLabel = (f) => `prisoners-dilemma:llm41-oneshot:${f}:t3`;
const C_VS_TRACKER = "rock-paper-scissors:llm41-vs-pattern-tracker:t3";
const C_VS_NASH = "rock-paper-scissors:llm41-vs-nash-mixed:t3";
const C_SELF = "rock-paper-scissors:llm41-selfplay:t3";

function llmBatches() {
  const batches = [];
  for (const arm of A_ARMS)
    for (const d of A_DELTAS)
      batches.push({
        family: "A",
        label: aLabel(arm, d),
        gameSlug: arm,
        p1: LLM,
        p2: LLM,
        protocol: {
          promptId: "pd-repeated-v1",
          temperature: TEMPERATURE,
          maxTokens: MAX_TOKENS,
          deltaPct: d,
          horizonRule: HORIZON_RULE,
        },
        horizonFor: (seed) => drawHorizon(seed, d),
        callsFor: (rounds) => 2 * rounds,
      });
  for (const f of B_FRAMINGS)
    batches.push({
      family: "B",
      label: bLabel(f),
      gameSlug: "prisoners-dilemma",
      p1: LLM,
      p2: LLM,
      protocol: { promptId: "pd-oneshot-v1", temperature: TEMPERATURE, maxTokens: MAX_TOKENS, framing: f },
      horizonFor: () => ({ rounds: 1, truncated: false }),
      callsFor: () => 2,
    });
  for (const [label, p2, calls] of [
    [C_VS_TRACKER, TRACKER, 50],
    [C_VS_NASH, NASH, 50],
    [C_SELF, LLM, 100],
  ])
    batches.push({
      family: "C",
      label,
      gameSlug: "rock-paper-scissors",
      p1: LLM,
      p2,
      protocol: { promptId: "rps-v1", temperature: TEMPERATURE, maxTokens: MAX_TOKENS },
      horizonFor: () => ({ rounds: 50, truncated: false }),
      callsFor: () => calls,
    });
  return batches;
}

// ── Extension X1: paraphrase robustness (registered post-main-study, pre-data) ─

const X_VARIANTS = ["v2a", "v2b"];
const xLabel = (v) => `prisoners-dilemma:llm41-para-${v}:d90:t3x`;
const X_LABELS = X_VARIANTS.map(xLabel);

function xBatches() {
  // Horizon-matched to the canonical δ=0.90 arm: same seeds 1–20, same
  // mulberry32(seed ^ 0x54524D) draw → identical realized horizons per seed,
  // so any behavioral difference is attributable to prompt surface alone.
  return X_VARIANTS.map((v) => ({
    family: "X",
    label: xLabel(v),
    gameSlug: "prisoners-dilemma",
    p1: LLM,
    p2: LLM,
    protocol: {
      promptId: `pd-repeated-${v}`,
      temperature: TEMPERATURE,
      maxTokens: MAX_TOKENS,
      deltaPct: 90,
      horizonRule: HORIZON_RULE,
    },
    horizonFor: (seed) => drawHorizon(seed, 90),
    callsFor: (rounds) => 2 * rounds,
  }));
}

const ALL_T3_LABELS = [...llmBatches().map((b) => b.label), BASELINE_LABEL];

function familyOfLabel(label) {
  if (!label) return null;
  if (label.endsWith(":t3x")) return label.includes(":llm41-para-") ? "X" : null;
  if (!label.endsWith(":t3")) return null;
  if (label.includes(":llm41-selfplay:d")) return "A";
  if (label.includes(":llm41-oneshot:")) return "B";
  if (label.startsWith("rock-paper-scissors:llm41")) return "C";
  return null;
}

function llmCallsOf(row) {
  try {
    return JSON.parse(row.llmMetaJson ?? "{}")?.runMeta?.llmCalls ?? 0;
  } catch {
    return 0;
  }
}

function computeSpend(experiments) {
  const spend = { A: 0, B: 0, C: 0, X: 0, global: 0 };
  for (const e of experiments) {
    const fam = familyOfLabel(e.batchLabel);
    if (!fam) continue;
    const calls = llmCallsOf(e);
    spend[fam] += calls;
    spend.global += calls;
  }
  return spend;
}

// ── Context ─────────────────────────────────────────────────────────────────

async function loadContext() {
  const [games, strategies] = await Promise.all([api("/games"), api("/strategies")]);
  const game = Object.fromEntries(games.map((g) => [g.slug, g]));
  const strat = Object.fromEntries(strategies.map((s) => [s.slug, s]));
  for (const slug of ["prisoners-dilemma", "prisoners-dilemma-iso", "rock-paper-scissors"])
    if (!game[slug]) throw new Error(`Game "${slug}" missing — restart the API server (seed step)`);
  for (const slug of [LLM, TRACKER, NASH])
    if (!strat[slug]) throw new Error(`Strategy "${slug}" missing — restart the API server (seed step)`);
  return { game, strat };
}

async function assertRegistry(expectedSha) {
  // No default on purpose: every caller pins the sha registered for ITS arm.
  // Sealed original-study steps pin phase3-v1 and refuse loudly now that the
  // registry has grown — no new original-arm data without a further amendment.
  if (!expectedSha) throw new Error("assertRegistry requires the arm's pre-registered sha");
  const res = await fetch(`${ENGINE}/llm-registry`);
  if (!res.ok) throw new Error(`Engine /llm-registry → ${res.status}`);
  const reg = await res.json();
  if (reg.sha256 !== expectedSha)
    throw new Error(
      `PROMPT REGISTRY DRIFT: engine sha ${reg.sha256} ≠ pre-registered ${expectedSha}. ` +
        `Refusing to run — amend the pre-registration first.`
    );
  log(`Prompt registry verified: ${reg.registryVersion} sha256=${reg.sha256.slice(0, 12)}…`);
}

// ── Step: claims (pre-registration) ─────────────────────────────────────────

function p3Claims(ctx) {
  const pdId = ctx.game["prisoners-dilemma"].id;
  const rpsId = ctx.game["rock-paper-scissors"].id;
  const canonHigh = [aLabel("prisoners-dilemma", 75), aLabel("prisoners-dilemma", 90)];
  const canonLow = [aLabel("prisoners-dilemma", 10), aLabel("prisoners-dilemma", 50)];
  const isoHigh = [aLabel("prisoners-dilemma-iso", 75), aLabel("prisoners-dilemma-iso", 90)];
  const isoLow = [aLabel("prisoners-dilemma-iso", 10), aLabel("prisoners-dilemma-iso", 50)];
  const cLlmLabels = [C_VS_TRACKER, C_VS_NASH, C_SELF];

  const provenance =
    `Subject gpt-4.1 (temperature 0.7, maxTokens 16) via the engine-live event-sourced path; ` +
    `prompt registry phase3-v1 sha256 ${REGISTRY_SHA.slice(0, 12)}…; 20 seeded replicates per cell; ` +
    `cluster = supergame/participant/run (self-play experiment values average both seats). ` +
    `Pre-registered in docs/phase3-preregistration.md.`;

  const aScope = { gameSlug: "prisoners-dilemma", focusStrategySlug: LLM };

  return [
    {
      title: "P3-A1: Shadow of the future — round-1 cooperation rises from δ=0.10 to δ=0.90",
      gameId: pdId,
      statement:
        `${provenance} Random-termination repeated PD (canonical arm, neutral labels J/F, horizon hidden): ` +
        `mean round-1 cooperation at δ=0.90 exceeds δ=0.10 with the 95% Welch CI of the difference excluding 0. ` +
        `Human anchor: Roth & Murnighan 1978 (+17.4pp, 19.0%→36.36%) and Murnighan & Roth 1983 (+11.2pp) ` +
        `per Dal Bó & Fréchette 2018 Table 2.`,
      predicate: {
        scope: aScope,
        minExperiments: 12,
        all: [
          {
            label: "round1Coop(δ=.90) − round1Coop(δ=.10) > 0 (95% CI)",
            kind: "diffScopes",
            metric: "round1CoopFocus",
            op: ">",
            threshold: 0,
            scope: { batchLabels: [aLabel("prisoners-dilemma", 90)] },
            scopeB: { batchLabels: [aLabel("prisoners-dilemma", 10)] },
          },
        ],
      },
    },
    {
      title: "P3-A2: Risk-dominance separation — round-1 cooperation higher above δ* (0.75/0.90 vs 0.10/0.50)",
      gameId: pdId,
      statement:
        `${provenance} With δ* = 0.60 (grim vs always-defect risk dominance for R=3,S=0,T=5,P=1): pooled round-1 ` +
        `cooperation in {δ=.75,.90} exceeds {δ=.10,.50}, 95% Welch CI excluding 0. Human anchor: DBF 2018 meta, ` +
        `first supergame 54.22% (risk-dominant) vs 35.64% (not), +18.6pp.`,
      predicate: {
        scope: aScope,
        minExperiments: 24,
        all: [
          {
            label: "round1Coop(δ>δ*) − round1Coop(δ<δ*) > 0 (95% CI)",
            kind: "diffScopes",
            metric: "round1CoopFocus",
            op: ">",
            threshold: 0,
            scope: { batchLabels: canonHigh },
            scopeB: { batchLabels: canonLow },
          },
        ],
      },
    },
    {
      title: "P3-A3: Human-range membership — high-δ round-1 cooperation within [36%, 63%]",
      gameId: pdId,
      statement:
        `${provenance} Pooled canonical-arm round-1 cooperation at δ ∈ {.75,.90} lies in [0.36, 0.63] (point ` +
        `estimate; band = R&M 1978 δ=.895 inexperienced 36.36% to DBF supergame-15 risk-dominant 63.06%; ` +
        `central reference 54.22%).`,
      predicate: {
        scope: aScope,
        minExperiments: 24,
        all: [
          {
            label: "pooled high-δ round1Coop ∈ [0.36, 0.63] (point)",
            kind: "threshold",
            evaluate: "point",
            metric: "round1CoopFocus",
            op: "between",
            threshold: 0.36,
            thresholdHigh: 0.63,
            scope: { batchLabels: canonHigh },
          },
        ],
      },
    },
    {
      title: "P3-A4: Isomorph invariance — separation persists and high-δ level shifts ≤15pp under payoff transform",
      gameId: pdId,
      statement:
        `${provenance} Contamination probe: payoffs affinely transformed ×3+2 → (11,2,17,5), preserving δ_SPE=0.50 ` +
        `and δ*=0.60. (a) The A2-style separation holds in the isomorph arm (CI excludes 0); AND (b) ` +
        `|high-δ round-1 cooperation (canonical) − (isomorph)| ≤ 0.15 (pre-registered equivalence margin, point). ` +
        `(b) failing while (a) holds suggests matrix memorization rather than incentive reasoning.`,
      predicate: {
        scope: aScope,
        minExperiments: 24,
        all: [
          {
            label: "isomorph: round1Coop(δ>δ*) − round1Coop(δ<δ*) > 0 (95% CI)",
            kind: "diffScopes",
            metric: "round1CoopFocus",
            op: ">",
            threshold: 0,
            scope: { gameSlug: "prisoners-dilemma-iso", batchLabels: isoHigh },
            scopeB: { gameSlug: "prisoners-dilemma-iso", batchLabels: isoLow },
          },
          {
            label: "|high-δ round1Coop canonical − isomorph| ≤ 0.15 (point)",
            kind: "diffScopes",
            absolute: true,
            metric: "round1CoopFocus",
            op: "<=",
            threshold: 0.15,
            scope: { gameSlug: "prisoners-dilemma", batchLabels: canonHigh },
            scopeB: { gameSlug: "prisoners-dilemma-iso", batchLabels: isoHigh },
          },
        ],
      },
    },
    {
      title: "P3-B1: Framing direction — Community label raises one-shot cooperation vs Wall Street",
      gameId: pdId,
      statement:
        `${provenance} One-shot PD (numRounds=1, self-play pairs, n=20 pairs per framing): cooperation under the ` +
        `"Community Game" framing exceeds "Wall Street Game", 95% Welch CI excluding 0. Anchor: Liberman, Samuels ` +
        `& Ross 2004 via Zhong, Loewenstein & Murnighan 2007 (direction; ~2× magnitude reported secondhand).`,
      predicate: {
        scope: { gameSlug: "prisoners-dilemma", focusStrategySlug: LLM },
        minExperiments: 12,
        all: [
          {
            label: "coop(community) − coop(wallstreet) > 0 (95% CI)",
            kind: "diffScopes",
            metric: "actionCooperationRateFocus",
            op: ">",
            threshold: 0,
            scope: { batchLabels: [bLabel("community")] },
            scopeB: { batchLabels: [bLabel("wallstreet")] },
          },
        ],
      },
    },
    {
      title: "P3-B2: Framing magnitude — Community/Wall Street cooperation ratio ≥ 1.5",
      gameId: pdId,
      statement:
        `${provenance} Cooperation(Community)/Cooperation(WallStreet) ≥ 1.5 (point; conservative ¾ of the ~2× ` +
        `reported gap) AND the B1 difference CI excludes 0. Pre-registered edge rule: if Cooperation(WallStreet)=0, ` +
        `supported iff Cooperation(Community) ≥ 0.30, else inconclusive.`,
      predicate: {
        scope: { gameSlug: "prisoners-dilemma", focusStrategySlug: LLM },
        minExperiments: 12,
        all: [
          {
            label: "coop(community)/coop(wallstreet) ≥ 1.5 (point; edge rule at denom 0)",
            kind: "ratioScopes",
            metric: "actionCooperationRateFocus",
            op: ">=",
            threshold: 1.5,
            scope: { batchLabels: [bLabel("community")] },
            scopeB: { batchLabels: [bLabel("wallstreet")] },
            ratioEdge: { denomZero: { numerAtLeast: 0.3 } },
          },
          {
            label: "coop(community) − coop(wallstreet) > 0 (95% CI)",
            kind: "diffScopes",
            metric: "actionCooperationRateFocus",
            op: ">",
            threshold: 0,
            scope: { batchLabels: [bLabel("community")] },
            scopeB: { batchLabels: [bLabel("wallstreet")] },
          },
        ],
      },
    },
    {
      title: "P3-B3: Neutral interior — neutral framing falls between Wall Street and Community",
      gameId: pdId,
      statement:
        `${provenance} Mean cooperation is non-decreasing across framings ordered WallStreet ≤ Neutral ≤ Community ` +
        `(point estimates, ties allowed).`,
      predicate: {
        scope: { gameSlug: "prisoners-dilemma", focusStrategySlug: LLM },
        minExperiments: 12,
        all: [
          {
            label: "coop(wallstreet) ≤ coop(neutral) ≤ coop(community) (point, ties ok)",
            kind: "orderedScopes",
            metric: "actionCooperationRateFocus",
            op: ">=",
            threshold: 0,
            scopesOrdered: [
              { batchLabels: [bLabel("wallstreet")] },
              { batchLabels: [bLabel("neutral")] },
              { batchLabels: [bLabel("community")] },
            ],
          },
        ],
      },
    },
    {
      title: "P3-C1: Round-1 RPS distribution — rock modal, share in [33%, 40%], scissors deficit",
      gameId: rpsId,
      statement:
        `${provenance} Across all LLM-seat round-1 decisions in the three RPS batches (n≈80, seat-decision level; ` +
        `self-play contributes both seats and this pooling is pre-registered): (a) rock is modal (rock > paper and ` +
        `rock > scissors); (b) rock share ∈ [0.33, 0.40]; (c) scissors share < 1/3. Anchors: Batzilis et al. 2019 ` +
        `first throws (R 33.99/P 34.82/S 31.20) and Wang, Xu & Zhou 2014 (R .36/P .33/S .32).`,
      predicate: {
        scope: { gameSlug: "rock-paper-scissors", focusStrategySlug: LLM, batchLabels: cLlmLabels },
        minExperiments: 48,
        all: [
          {
            label: "round1 rock > paper (point, seat decisions)",
            kind: "metricVsMetric",
            aggregate: "seatDecision",
            metric: "round1Rock",
            metricB: "round1Paper",
            op: ">",
            threshold: 0,
          },
          {
            label: "round1 rock > scissors (point, seat decisions)",
            kind: "metricVsMetric",
            aggregate: "seatDecision",
            metric: "round1Rock",
            metricB: "round1Scissors",
            op: ">",
            threshold: 0,
          },
          {
            label: "rock share ∈ [0.33, 0.40] (point)",
            kind: "threshold",
            aggregate: "seatDecision",
            evaluate: "point",
            metric: "round1Rock",
            op: "between",
            threshold: 0.33,
            thresholdHigh: 0.4,
          },
          {
            label: "scissors share < 1/3 (point)",
            kind: "threshold",
            aggregate: "seatDecision",
            evaluate: "point",
            metric: "round1Scissors",
            op: "<",
            threshold: 0.3333333333333333,
          },
        ],
      },
    },
    {
      title: "P3-C2: Win-stay/lose-shift signature in RPS",
      gameId: rpsId,
      statement:
        `${provenance} Pooled LLM seat-decision conditionals over rounds with a previous outcome (win = positive ` +
        `payoff, lose = negative, ties excluded): P(stay|win) 95% CI entirely above 1/3 AND P(shift|lose) CI ` +
        `entirely above 2/3 (independence nulls). Either CI entirely below its null ⇒ refuted. Anchors: Wang, Xu ` +
        `& Zhou 2014 (WSLS signature); Zhang, Moisan & Gonzalez 2021 (only ~1/3 of humans outcome-dependent — ` +
        `absence is a human-plausible outcome).`,
      predicate: {
        scope: { gameSlug: "rock-paper-scissors", focusStrategySlug: LLM, batchLabels: cLlmLabels },
        minExperiments: 40,
        all: [
          {
            label: "P(stay|win) > 1/3 (95% CI, seat decisions)",
            kind: "threshold",
            aggregate: "seatDecision",
            metric: "wslsStayGivenWin",
            op: ">",
            threshold: 0.3333333333333333,
          },
          {
            label: "P(shift|lose) > 2/3 (95% CI, seat decisions)",
            kind: "threshold",
            aggregate: "seatDecision",
            metric: "wslsShiftGivenLose",
            op: ">",
            threshold: 0.6666666666666666,
          },
        ],
      },
    },
    {
      title: "P3-C3: Pattern-tracker exploits LLM sequential dependence beyond Nash baseline",
      gameId: rpsId,
      statement:
        `${provenance} The deterministic first-order pattern-tracker earns a higher per-round payoff against the ` +
        `LLM than against nash-mixed (pre-registered zero-LLM baseline batch, 20 runs each), 95% Welch CI of the ` +
        `difference excluding 0. Against a true mixed-Nash player the tracker's expected edge is 0; a CI-positive ` +
        `edge demonstrates exploitable sequential dependence.`,
      predicate: {
        scope: { gameSlug: "rock-paper-scissors", focusStrategySlug: TRACKER },
        minExperiments: 12,
        all: [
          {
            label: "trackerPayoff/round(vs LLM) − (vs nash baseline) > 0 (95% CI)",
            kind: "diffScopes",
            metric: "avgPayoffPerRoundFocus",
            op: ">",
            threshold: 0,
            scope: { batchLabels: [C_VS_TRACKER] },
            scopeB: { batchLabels: [BASELINE_LABEL] },
          },
        ],
      },
    },
  ];
}

// ── Extension X1 claims (paraphrase robustness) ─────────────────────────────

function xClaims(ctx) {
  const pdId = ctx.game["prisoners-dilemma"].id;
  const provenance =
    `Extension X1, registered 2026-07-24 AFTER the main Phase 3 results (disclosed post-result extension; ` +
    `direction and thresholds committed before any extension data existed) and BEFORE any :t3x row. ` +
    `Subject gpt-4.1 (temperature 0.7, maxTokens 16), engine-live event-sourced path; prompt registry ` +
    `phase3-v2 sha256 ${REGISTRY_SHA_X.slice(0, 12)}… (append-only: pd-repeated-v2a/v2b added, phase3-v1 ` +
    `prompts byte-identical); horizons matched to the canonical δ=0.90 arm (same seeds 1–20, same ` +
    `mulberry32 draw). Registered in docs/phase3-preregistration.md, Extension X1.`;
  return [
    {
      title:
        "P3-X1: Paraphrase robustness — round-1 defection at δ=0.90 persists under two prompt rewordings",
      gameId: pdId,
      statement:
        `${provenance} Main study observed round-1 cooperation of exactly 0 in all 160 repeated-PD ` +
        `supergames (pd-repeated-v1). Prediction: the corner solution is a property of the incentive ` +
        `presentation, not of one specific wording — under each of two semantically equivalent paraphrases ` +
        `(v2a: reordered/reworded; v2b: compact outcome notation), mean round-1 cooperation at δ=0.90 stays ` +
        `≤ 0.05. Refutation under any paraphrase is itself a finding (prompt-surface brittleness) and would ` +
        `overturn the report's incentive-insensitivity reading of A1–A3; it will be disclosed as such.`,
      predicate: {
        scope: { gameSlug: "prisoners-dilemma", focusStrategySlug: LLM },
        minExperiments: 20,
        all: [
          {
            label: "round1Coop(paraphrase v2a, δ=0.90) ≤ 0.05",
            metric: "round1CoopFocus",
            op: "<=",
            threshold: 0.05,
            scope: { batchLabels: [xLabel("v2a")] },
          },
          {
            label: "round1Coop(paraphrase v2b, δ=0.90) ≤ 0.05",
            metric: "round1CoopFocus",
            op: "<=",
            threshold: 0.05,
            scope: { batchLabels: [xLabel("v2b")] },
          },
        ],
      },
    },
  ];
}

async function preRegisterClaims(
  ctx,
  { claimsFn = p3Claims, sha = REGISTRY_SHA, guardLabels = ALL_T3_LABELS } = {}
) {
  const claims = claimsFn(ctx);
  const [existingClaims, experiments] = await Promise.all([api("/claims"), api("/experiments")]);
  const byTitle = new Map(existingClaims.map((c) => [c.title, c]));
  const unregistered = claims.filter((c) => !byTitle.has(c.title));
  // Only gate on the registry when actually about to write claims — re-running
  // a sealed arm's claims step stays an idempotent no-op after the registry grows.
  if (unregistered.length > 0) await assertRegistry(sha);

  // Pre-registration guard: ANY row of the guarded arm existing before all its
  // claims are registered would be post-hoc claiming — refuse loudly.
  const t3Rows = experiments.filter((e) => guardLabels.includes(e.batchLabel));
  if (t3Rows.length > 0 && unregistered.length > 0) {
    throw new Error(
      `PRE-REGISTRATION VIOLATION: ${t3Rows.length} Phase 3 row(s) already exist but ` +
        `${unregistered.length} claim(s) are unregistered. Refusing to write post-hoc claims.`
    );
  }

  let created = 0;
  for (const c of claims) {
    if (byTitle.has(c.title)) continue;
    await api("/claims", {
      method: "POST",
      body: {
        title: c.title,
        statement: c.statement,
        gameId: c.gameId,
        predicateJson: JSON.stringify(c.predicate),
      },
    });
    created++;
    log(`  pre-registered: ${c.title}`);
  }
  log(`Step claims: ${created} created, ${claims.length - created} already present (untouched)`);
}

// ── Step: runs ──────────────────────────────────────────────────────────────

function planSeeds(rows) {
  const bySeed = new Map(rows.map((r) => [r.seed, r]));
  // "pending" = created but never executed (e.g. a previous runner died between
  // create and run). Safe to re-run: POST /experiments with the same seed
  // returns the existing row (idempotent create), then /run executes it.
  // "running" rows are genuinely in-flight server-side and stay claimed.
  const claimed = new Set(
    rows.filter((r) => r.status !== "failed" && r.status !== "pending").map((r) => r.seed)
  );
  const todo = [];
  const exhausted = [];
  for (const s of SEEDS) {
    if (!claimed.has(s)) {
      todo.push(s);
      continue;
    }
    if (bySeed.get(s)?.status === "invalid") {
      const rep = REPLACEMENT_OFFSET + s;
      if (!claimed.has(rep)) todo.push(rep);
      else if (bySeed.get(rep)?.status === "invalid") exhausted.push(s);
    }
  }
  const inFlight = rows.filter((r) => r.status === "running" || r.status === "pending");
  return { todo, exhausted, inFlight };
}

/**
 * Run an experiment to a terminal status. If the HTTP request dies (client
 * timeout, killed shell), the server keeps executing — poll instead of
 * re-creating, so the seed is never double-run.
 */
async function runToTerminal(expId) {
  try {
    await api(`/experiments/${expId}/run`, { method: "POST" });
  } catch (err) {
    log(`    run request interrupted (${String(err.message).slice(0, 140)}) — polling for server-side completion`);
  }
  const deadline = Date.now() + 45 * 60_000;
  for (;;) {
    const row = await api(`/experiments/${expId}`);
    if (["completed", "invalid", "failed"].includes(row.status)) return row;
    if (Date.now() > deadline)
      throw new Error(`EXP-${expId} still "${row.status}" after 45 min — aborting (seed stays claimed)`);
    await sleep(10_000);
  }
}

async function runBaseline(ctx) {
  const rows = await api(`/experiments?batchLabel=${encodeURIComponent(BASELINE_LABEL)}`);
  const done = rows.filter((e) => e.status === "completed").length;
  if (done >= SEEDS.length) {
    log(`${BASELINE_LABEL}: ${done}/${SEEDS.length} completed (zero LLM calls)`);
    return;
  }
  const res = await api("/experiments/batch", {
    method: "POST",
    body: {
      gameId: ctx.game["rock-paper-scissors"].id,
      player1StrategyId: ctx.strat[TRACKER].id,
      player2StrategyId: ctx.strat[NASH].id,
      numRounds: 50,
      seeds: SEEDS,
      batchLabel: BASELINE_LABEL,
      notes: "P3-C3 pre-registered zero-LLM baseline (tracker vs nash-mixed)",
    },
  });
  log(`${BASELINE_LABEL}: ran ${res.experimentIds.length}, skipped ${res.skippedSeeds.length} existing`);
}

async function runStudy(
  ctx,
  {
    batches = llmBatches(),
    sha = REGISTRY_SHA,
    claimsFn = p3Claims,
    baseline = true,
    claimsStep = "claims",
  } = {}
) {
  await assertRegistry(sha);

  // Reverse-order guard: never generate data before all claims exist.
  const registered = new Set((await api("/claims")).map((c) => c.title));
  const missing = claimsFn(ctx).filter((c) => !registered.has(c.title));
  if (missing.length > 0)
    throw new Error(`Claims not pre-registered (${missing.length} missing) — run the "${claimsStep}" step first.`);

  if (baseline) await runBaseline(ctx);

  const spend = computeSpend(await api("/experiments"));
  log(`Budget at start: A ${spend.A}/${CAPS.A}, B ${spend.B}/${CAPS.B}, C ${spend.C}/${CAPS.C}, X ${spend.X}/${CAPS.X}, global ${spend.global}/${CAPS.global}`);

  const cappedFamilies = new Set();
  for (const batch of batches) {
    if (cappedFamilies.has(batch.family)) continue;
    let consecutiveFailures = 0;
    // Up to 3 passes per batch: primaries, then replacements for any invalid
    // trials discovered in the previous pass.
    passes: for (let pass = 0; pass < 3; pass++) {
      const rows = await api(`/experiments?batchLabel=${encodeURIComponent(batch.label)}`);
      const { todo, exhausted, inFlight } = planSeeds(rows);
      const done = rows.filter((r) => r.status === "completed").length;
      if (exhausted.length > 0)
        log(`  ⚠ ${batch.label}: seeds ${exhausted.join(",")} invalid twice — permanently excluded (disclosed)`);
      if (inFlight.length > 0)
        log(`  note: ${inFlight.length} in-flight row(s) in ${batch.label} — seeds stay claimed`);
      if (pass === 0) log(`${batch.label}: ${done}/${SEEDS.length} completed, ${todo.length} to run`);
      if (todo.length === 0) break;

      for (const seed of todo) {
        const { rounds, truncated } = batch.horizonFor(seed);
        if (truncated) {
          log(`  ⚠ seed ${seed}: horizon draw hit the 120-round safety cap — supergame excluded (disclosed, no calls made)`);
          continue;
        }
        const expected = batch.callsFor(rounds);
        if (spend[batch.family] + expected > CAPS[batch.family]) {
          log(`  ✋ family ${batch.family} cap: ${spend[batch.family]} spent + ${expected} expected > ${CAPS[batch.family]} — stopping this family (others continue)`);
          cappedFamilies.add(batch.family);
          break passes;
        }
        if (spend.global + expected > CAPS.global)
          throw new Error(
            `GLOBAL KILL-SWITCH: ${spend.global} calls spent + ${expected} expected > ${CAPS.global}. Halting all runs.`
          );

        const t0 = Date.now();
        const created = await api("/experiments", {
          method: "POST",
          body: {
            gameId: ctx.game[batch.gameSlug].id,
            player1StrategyId: ctx.strat[batch.p1].id,
            player2StrategyId: ctx.strat[batch.p2].id,
            numRounds: rounds,
            seed,
            batchLabel: batch.label,
            notes:
              `P3 ${batch.family} replicate seed ${seed}` +
              (batch.protocol.deltaPct != null ? ` (δ=${batch.protocol.deltaPct / 100}, drawn horizon ${rounds})` : "") +
              (seed > REPLACEMENT_OFFSET ? ` [replacement for invalid seed ${seed - REPLACEMENT_OFFSET}]` : ""),
            llmProtocol: batch.protocol,
          },
        });
        const row = await runToTerminal(created.id);
        const calls = llmCallsOf(row);
        spend[batch.family] += calls;
        spend.global += calls;
        const secs = ((Date.now() - t0) / 1000).toFixed(0);
        if (row.status === "completed") {
          consecutiveFailures = 0;
          log(`  seed ${seed}: EXP-${row.id} completed in ${secs}s (${rounds}r, ${calls} calls; ${batch.family} ${spend[batch.family]}/${CAPS[batch.family]}, global ${spend.global}/${CAPS.global})`);
        } else if (row.status === "invalid") {
          consecutiveFailures = 0;
          const repMsg =
            seed <= SEEDS.length
              ? `replacement seed ${REPLACEMENT_OFFSET + seed} queued next pass`
              : "replacement also invalid — cell permanently excluded (disclosed)";
          log(`  ⚠ seed ${seed}: EXP-${row.id} INVALID TRIAL after ${secs}s (${calls} calls still counted) — ${repMsg}`);
        } else {
          consecutiveFailures++;
          log(`  ✗ seed ${seed}: EXP-${row.id} FAILED after ${secs}s — ${String(row.errorMessage).slice(0, 160)}`);
          process.exitCode = 1;
          if (consecutiveFailures >= 3)
            throw new Error(`3 consecutive failures in ${batch.label} — systemic problem, halting to protect budget.`);
        }
      }
    }
  }

  const finalSpend = computeSpend(await api("/experiments"));
  log(`Step runs done. Budget: A ${finalSpend.A}/${CAPS.A}, B ${finalSpend.B}/${CAPS.B}, C ${finalSpend.C}/${CAPS.C}, X ${finalSpend.X}/${CAPS.X}, global ${finalSpend.global}/${CAPS.global}`);
}

// ── Step: verify (zero-live-call replay audit) ──────────────────────────────

async function verifyAll() {
  const experiments = await api("/experiments");
  const targets = experiments.filter(
    (e) => familyOfLabel(e.batchLabel) && e.status === "completed"
  );
  log(`Step verify: replaying ${targets.length} completed Phase 3 runs (zero live LLM calls)…`);
  let ok = 0;
  const failures = [];
  for (const e of targets) {
    const report = await api(`/experiments/${e.id}/replay`, { method: "POST" });
    const meta = JSON.parse(e.llmMetaJson ?? "{}");
    // Stored runMeta sha must equal the sha pre-registered for the run's arm.
    // report.llm.promptRegistrySha256 is the CURRENT (append-only) file sha —
    // informational only; the authoritative byte-exact check is the per-prompt
    // hash verification folded into report.ok.
    const expectedSha = familyOfLabel(e.batchLabel) === "X" ? REGISTRY_SHA_X : REGISTRY_SHA;
    const shaOk = meta?.runMeta?.promptRegistrySha256 === expectedSha;
    if (report.ok && report.llm.liveCalls === 0 && shaOk) ok++;
    else
      failures.push(
        `EXP-${e.id} (${e.batchLabel} seed ${e.seed}): ok=${report.ok} live=${report.llm.liveCalls} shaOk=${shaOk} ` +
          `llmMismatches=${report.llm.mismatches.slice(0, 2).join("; ")} metricMismatches=${report.metrics.mismatches.slice(0, 2).join("; ")}`
      );
  }
  log(`  verified ${ok}/${targets.length} runs bit-exact (replay ok, 0 live calls, registry sha pinned)`);
  if (failures.length > 0) {
    process.exitCode = 1;
    log(`  ✗ ${failures.length} verification failure(s):`);
    for (const f of failures) log(`    ${f}`);
  }
}

// ── Step: adjudicate (+ verdict-flip audit) ─────────────────────────────────

async function adjudicate(ctx) {
  const before = new Map((await api("/claims")).map((c) => [c.id, c.status]));
  const results = await api("/claims/adjudicate-all", { method: "POST" });
  const counts = {};
  for (const r of results) counts[r.status] = (counts[r.status] ?? 0) + 1;
  log(`Step adjudicate: ${JSON.stringify(counts)}`);

  const claims = await api("/claims");
  const p3Titles = new Set([...p3Claims(ctx), ...xClaims(ctx)].map((c) => c.title));

  for (const claim of claims.filter((c) => p3Titles.has(c.title))) {
    log(`  [${claim.status.toUpperCase()}] ${claim.title}`);
    const adj = claim.adjudicationJson ? JSON.parse(claim.adjudicationJson) : null;
    for (const it of adj?.items ?? []) {
      log(
        `      ${it.verdict}: ${it.label} — observed ${it.mean?.toFixed(4) ?? "n/a"}` +
          (it.ciLow != null ? ` CI [${it.ciLow.toFixed(4)}, ${it.ciHigh.toFixed(4)}]` : "") +
          ` (n=${it.n})` +
          (it.note ? ` — ${it.note}` : "")
      );
    }
  }

  // Verdict-flip audit: Phase 3 data + the self-play Focus-mean semantics
  // change can alter the evidence set of ANY pre-existing claim. Disclose
  // every flip rather than silently absorbing it.
  const flips = claims.filter(
    (c) => !p3Titles.has(c.title) && before.has(c.id) && before.get(c.id) !== c.status
  );
  if (flips.length === 0) log("  Verdict-flip audit: no pre-existing claim changed verdict.");
  else {
    log(`  ⚠ Verdict-flip audit: ${flips.length} pre-existing claim(s) changed verdict (disclosed):`);
    for (const c of flips) log(`      ${before.get(c.id)} → ${c.status}: ${c.title}`);
  }
}

// ── Step: status ────────────────────────────────────────────────────────────

async function status() {
  const experiments = await api("/experiments");
  const spend = computeSpend(experiments);
  log(`Budget: A ${spend.A}/${CAPS.A}, B ${spend.B}/${CAPS.B}, C ${spend.C}/${CAPS.C}, X ${spend.X}/${CAPS.X}, global ${spend.global}/${CAPS.global}`);
  for (const label of [...ALL_T3_LABELS, ...X_LABELS]) {
    const rows = experiments.filter((e) => e.batchLabel === label);
    const c = (s) => rows.filter((r) => r.status === s).length;
    log(
      `  ${label}: ${c("completed")}/${SEEDS.length} completed` +
        (c("invalid") ? `, ${c("invalid")} invalid` : "") +
        (c("failed") ? `, ${c("failed")} failed` : "") +
        (c("running") + c("pending") ? `, ${c("running") + c("pending")} in-flight` : "")
    );
  }
}

// ── Main ────────────────────────────────────────────────────────────────────

const step = process.argv[2] ?? "all";
const ctx = await loadContext();
if (step === "claims" || step === "all") await preRegisterClaims(ctx);
if (step === "runs" || step === "all") await runStudy(ctx);
if (step === "xclaims")
  await preRegisterClaims(ctx, { claimsFn: xClaims, sha: REGISTRY_SHA_X, guardLabels: X_LABELS });
if (step === "xruns")
  await runStudy(ctx, {
    batches: xBatches(),
    sha: REGISTRY_SHA_X,
    claimsFn: xClaims,
    baseline: false,
    claimsStep: "xclaims",
  });
if (step === "verify" || step === "all") await verifyAll();
if (step === "adjudicate" || step === "all") await adjudicate(ctx);
if (step === "status") await status();
log(`Phase 3 pipeline step "${step}" finished.`);
