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
- `artifacts/api-server/src/lib/game-engine.ts` — all game theory strategy logic and game runner
- `artifacts/api-server/src/lib/seed.ts` — seeds 7 games and 8 strategies on startup (idempotent)
- `artifacts/api-server/src/routes/` — one file per domain (games, strategies, experiments, rounds, analyses, claims, papers, dashboard)
- `artifacts/lab/src/pages/` — frontend pages (Dashboard, GameCatalog, GameDetail, Experiments, NewExperiment, ExperimentDetail, Claims, Papers, PaperDetail)

## Architecture decisions

- Contract-first: OpenAPI spec gates all codegen; never write types by hand
- Game engine is pure TypeScript functions in `game-engine.ts` — strategies are keyed by slug, runGame() executes all rounds, computeAnalysis() produces statistical output
- Papers are generated server-side from experiment/claim data without requiring an LLM
- Seed is idempotent (checks for existing rows) so restarting the server is safe
- Dashboard aggregate queries use Drizzle's `sql<>` template with explicit `Number()` coercion (Postgres returns bigint aggregates as strings)

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
- Game engine strategies are registered by slug — new strategies are added to `STRATEGIES` map in `game-engine.ts` and seeded in `seed.ts`
