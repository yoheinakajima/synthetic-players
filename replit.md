# Game Theory Research Lab

A public academic research platform that runs classic game theory experiments, records every decision with full provenance, compares behavior against Nash equilibria, generates statistical analyses, tracks research claims, and compiles academic papers.

## Run & Operate

- `pnpm --filter @workspace/api-server run dev` — run the API server (port 8080, proxied at /api)
- `pnpm --filter @workspace/lab run dev` — run the frontend (port assigned by workflow)
- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from the OpenAPI spec
- `pnpm --filter @workspace/db run push` — push DB schema changes (dev only)
- Required env: `DATABASE_URL` — Postgres connection string

## Stack

- pnpm workspaces, Node.js 24, TypeScript 5.9
- API: Express 5
- DB: PostgreSQL + Drizzle ORM
- Validation: Zod (`zod/v4`), `drizzle-zod`
- API codegen: Orval (from OpenAPI spec)
- Frontend: React + Vite, TanStack Query, wouter, shadcn/ui, Recharts

## Where things live

- `lib/api-spec/openapi.yaml` — single source of truth for all API contracts
- `lib/db/src/schema/` — Drizzle table definitions (games, strategies, experiments, rounds, analyses, claims, papers)
- `artifacts/api-server/engine/` — Python ActiveGraph simulation engine sidecar (strategies.py, engine.py, server.py; localhost-only FastAPI on port 8090, SQLite event store in engine/data/)
- `artifacts/api-server/src/lib/game-engine.ts` — TS round analysis (computeAnalysis) only; simulation now runs on the engine sidecar
- `artifacts/api-server/src/lib/engine-client.ts` — HTTP client for the engine sidecar (ENGINE_URL env)
- `artifacts/api-server/src/lib/metrics.ts` — v2 per-game-class metric suite (see docs/METRICS.md)
- `artifacts/api-server/src/lib/adjudicator.ts` — mechanical claim adjudication (predicates → verdicts with CIs/effect sizes)
- `artifacts/api-server/src/lib/claim-predicates.ts` — structured predicates for the 11 v1 claims (startup backfill)
- `artifacts/api-server/src/lib/experiment-service.ts` — shared execute/analyze logic used by single + batch runs
- `artifacts/api-server/src/lib/seed.ts` — seeds 7 games and 8 strategies on startup (idempotent)
- `artifacts/api-server/src/routes/` — one file per domain (games, strategies, experiments, rounds, analyses, claims, papers, dashboard)
- `artifacts/lab/src/pages/` — frontend pages (Dashboard, GameCatalog, GameDetail, Experiments, NewExperiment, ExperimentDetail, Claims, Papers, PaperDetail)
- `scripts/run-phase1.mjs` — reproducible pipeline driver (v2 analyses → 20-seed batches → adjudicate-all → paper)
- `scripts/run-phase2-track2.mjs`, `scripts/run-phase3.mjs` — pre-registered study runners (claims → runs → verify → adjudicate; resumable, budget-capped)
- `artifacts/api-server/engine/llm_subject.py`, `llm_runner.py` — engine-live LLM seat (prompt registry, OpenAI provider, LLMCache event sourcing, zero-live-call replay)
- `docs/METRICS.md`, `docs/POSTMORTEM.md`, `docs/v1/` — metric definitions, v1 error record, frozen v1 artifacts
- `docs/phase3-preregistration.md` — Phase 3 pre-registration (predicates, budgets, invalid-trial + truncation rules)

## Architecture decisions

- Contract-first: OpenAPI spec gates all codegen; never write types by hand
- Simulation runs on the Python ActiveGraph engine sidecar (`artifacts/api-server/engine/`, activegraph==1.10.0 pinned, run via `uv run python engine/server.py`); Express proxies run/fork/diff/trace to it and remains the only Postgres writer. computeAnalysis() stays in TS in `game-engine.ts`. Every run is seeded (mulberry32, bit-identical TS/Python port); same seed → identical rounds
- Papers are generated server-side from experiment/claim data without requiring an LLM
- Seed is idempotent (checks for existing rows) so restarting the server is safe
- Dashboard aggregate queries use Drizzle's `sql<>` template with explicit `Number()` coercion (Postgres returns bigint aggregates as strings)
- **Reproducibility (v2):** every run is seeded (mulberry32, seed stored on experiment); same seed ⇒ identical rounds. Probabilistic matchups run as 20-seed batches (`POST /experiments/batch`, batchLabel convention `game:p1-vs-p2:v2`)
- **LLM strategies (Track 2):** `ai_model` strategies (gpt-5-mini via Replit AI Integrations, no API key) decide live each round; runs are event-sourced, not seed-reproducible — the decision log (actions + reasonings) replays on the engine as `scripted` seats with exact-match verification, provenance in `experiments.llmMetaJson`. Deterministic opponents or LLM-vs-LLM only; no LLM seats on forks; excluded from batch endpoint. See docs/METRICS.md "LLM runs".
- **Honesty pipeline (v2):** claims carry `predicateJson`; `POST /claims/adjudicate-all` assigns supported/refuted/inconclusive/untested mechanically (95% t-CI vs threshold for sampled evidence, exact comparison for deterministic). Claims without predicates are `untested`. Verdicts are never hand-set; refuted claims stay on the record
- **Per-class metrics (v2):** analysisVersion 2 + metricsJson; cooperation metrics null for zero-sum games (exploitability + G-test instead); per-round "Nash rate" null for mixed-equilibrium games. UI panels are class-aware
- **Presentation rule:** UI and paper lead with per-round averages; totals always labeled as totals
- **Fork exclusion rule:** fork-lineage experiments (parentExperimentId set) are exploratory, never evidence — no analysis rows, skipped by the adjudicator, aggregate endpoint, and leaderboard. Study forks via the parent-vs-fork diff view. Only engine-era experiments (with engineRunId) are forkable; pre-engine runs would need a seeded re-run to backfill engineRunId
- **Fork-comparison evidence (Phase 2 · Track 1):** the one principled exception to fork exclusion — paired parent-vs-fork metrics over the shared post-fork window (`postFork.*` metrics, `scope.fork` predicate blocks; see docs/METRICS.md). `POST /experiments/fork-batch` forks a whole batch idempotently, auto-materializing engine runs via verified seeded replay (`POST /experiments/:id/engine-run`, 409 on determinism drift, writes nothing on mismatch). Entire seeded corpus (396 runs) backfilled with 0 drift. Adjudicator treats sd < 1e-12 as deterministic evidence (float residue ≠ variance)

- **Phase 3 results (July 2026):** 320 runs (280 main + 40 X1), 5,820 calls, 0 invalid, 320/320 replay-verified. gpt-4.1 @0.7: zero round-1 cooperation in ALL repeated PD under v1 wording (A family fully refuted); framing effect real (community 17.5% vs wallstreet 0%, B1 supported); RPS rock 80% (human band refuted), WSLS supported (shift|lose 0.97); tracker LOST to the LLM (C3 sign-reversed refutation). **Extension X1 (result-informed, prospectively registered): paraphrase-robustness prediction REFUTED — under two rewordings of the δ=.90 arm all 20 recorded episodes begin with cooperation vs all 20 with defection under v1 (same seeds). Approved headline: prompt wording dominated the tested incentive manipulation and rendered single-wording behavioral inference non-identifiable (never "not incentive-determined"). Paraphrase arms now standing protocol.** See docs/phase3-report.md §6, layer-2 companion docs/phase3-layer2.md
- **LLM as behavioral subject (Phase 3):** experiments with `llmMetaJson.protocol` + an `ai_model` seat run **engine-live** — the engine drives the LLM loop (gpt-4.1, temperature/maxTokens pinned in the protocol), event-sources every call as `LLMCache` events, and replays with zero live calls via `POST /experiments/:id/replay` (byte-compares actions/payoffs and recomputes metrics). Invalid trials (unparseable after retry) persist as status `invalid` with call counts — they claim their seed and spend budget but are never evidence; replacement seeds are 1000+k, drawn once. Prompt registry sha is pinned by the runner; drift aborts the study. Engine-client uses a long-timeout undici dispatcher for `/llm-runs` (default 5-min fetch cap would fail long self-play runs while the engine keeps spending)
- **Phase 4 (July 2026, APPROVED 2026-07-24T15:18:49Z — EXECUTING):** complete freeze packet in `docs/phase4/freeze-packet.md` (predicates A–G: D1 64-cell representation×incentive factorial, D2 payoff-word decoupling, D3 symbol positional-attraction, E gate+slope, X2 wording-switch localization k=6 spans, F adversarial RPS at 50 rounds — 30-round gate honestly FAILED by 0.0012). Registry v3 appended (`4-proposed`, 44 templates, 250 arms, seeds 2001–3092); cross-vendor subject gemini-2.5-flash via Replit AI Integrations Gemini route (amendment A1, 2026-07-24: claude-haiku-4-5 failed Gate 0 round 1 behaviorally — cannot complete a turn at maxTokens=16; gemini gate-tested PASS round 2, adapter `engine/gemini_provider.py`); budget ≈18,800 calls/$261 upper bound, global kill-switch 21,000. **Gate 0 PASSED (round 2); step 2 DONE 2026-07-24 — §F.3 capture/enforcement/replay implemented (`engine/phase4.py`, `phase4_runner.py`, `phase4_providers.py`, `provenance.py`; PARSER_VERSION `strip-upper-exact-v1.p4.2026-07-24`; budget ledger `engine/data/budget.db` with exact Gate-0 backfill 15 calls / 2,972 in / 63 out; live runs 403-gated until seal; 53-check selftest `engine/selftest_phase4.py` (incl. per-call Gemini `thoughts_token_count == 0` guard) + Phase 3 replay byte-exact; implementation note in provider-packet §3). Step 3 DONE 2026-07-24 — registry v3 SEALED (`phase4-v3`, post-seal sha `0c084b73…`) + externally anchored: annotated tag `phase4-v3-seal` + GitHub release 2026-07-24T19:04:16Z on `yoheinakajima/synthetic-players` (assets registry/arms/SHA256SUMS; `docs/phase4/seal-record.md`). Next: step 4 — sentinel + X2 screening + D1→D2→D3 per the sealed schedule.** X1 report amendments applied (episode-level corners, provenance appendix §7, positioning §8)

## Product

**Games:** 7 classic game theory games seeded at startup:
- Prisoner's Dilemma (social_dilemma)
- Stag Hunt (coordination)
- Chicken Game (social_dilemma)
- Battle of the Sexes (coordination)
- Matching Pennies (zero_sum)
- Pure Coordination Game (coordination)
- Rock-Paper-Scissors (zero_sum)

**Strategies:** 8 algorithmic strategies:
- Always Cooperate, Always Defect, Tit-for-Tat, Grim Trigger, Random, Win-Stay Lose-Shift (Pavlov), Nash Mixed Strategy, Generous Tit-for-Tat

**Workflow:** Create experiment → Run → Analyze → Create claims → Generate paper

## User preferences

_Populate as you build — explicit user instructions worth remembering across sessions._

## Gotchas

- After any schema change: `pnpm --filter @workspace/db run push` then restart API server
- After any OpenAPI spec change: `pnpm --filter @workspace/api-spec run codegen` then restart API server
- Drizzle `sql<number>` aggregates come back as strings from Postgres — always wrap with `Number()`
- `useToast` must be imported from `@/hooks/use-toast`, not `@/components/ui/toast`
- Express 5: use `/{*splat}` for wildcard routes, never bare `*`

## Pointers

- See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details
- Game engine strategies are registered by slug — new strategies are added to `STRATEGY_FNS` in `artifacts/api-server/engine/strategies.py` and seeded in `seed.ts`
