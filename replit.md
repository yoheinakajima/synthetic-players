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
- `docs/METRICS.md`, `docs/POSTMORTEM.md`, `docs/v1/` — metric definitions, v1 error record, frozen v1 artifacts

## Architecture decisions

- Contract-first: OpenAPI spec gates all codegen; never write types by hand
- Simulation runs on the Python ActiveGraph engine sidecar (`artifacts/api-server/engine/`, activegraph==1.10.0 pinned, run via `uv run python engine/server.py`); Express proxies run/fork/diff/trace to it and remains the only Postgres writer. computeAnalysis() stays in TS in `game-engine.ts`. Every run is seeded (mulberry32, bit-identical TS/Python port); same seed → identical rounds
- Papers are generated server-side from experiment/claim data without requiring an LLM
- Seed is idempotent (checks for existing rows) so restarting the server is safe
- Dashboard aggregate queries use Drizzle's `sql<>` template with explicit `Number()` coercion (Postgres returns bigint aggregates as strings)
- **Reproducibility (v2):** every run is seeded (mulberry32, seed stored on experiment); same seed ⇒ identical rounds. Probabilistic matchups run as 20-seed batches (`POST /experiments/batch`, batchLabel convention `game:p1-vs-p2:v2`)
- **Honesty pipeline (v2):** claims carry `predicateJson`; `POST /claims/adjudicate-all` assigns supported/refuted/inconclusive/untested mechanically (95% t-CI vs threshold for sampled evidence, exact comparison for deterministic). Claims without predicates are `untested`. Verdicts are never hand-set; refuted claims stay on the record
- **Per-class metrics (v2):** analysisVersion 2 + metricsJson; cooperation metrics null for zero-sum games (exploitability + G-test instead); per-round "Nash rate" null for mixed-equilibrium games. UI panels are class-aware
- **Presentation rule:** UI and paper lead with per-round averages; totals always labeled as totals

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
