# Game Theory Research Lab

A full-stack research platform that runs game theory experiments with
algorithmic strategies, records complete provenance (every round, every seed),
computes per-game-class statistics, and **mechanically adjudicates research
claims** against the recorded evidence. The lab's papers are generated from
adjudicated data only — including its own refuted claims.

## What it does

- **7 canonical games** across three classes: social dilemmas (Prisoner's
  Dilemma, Public Goods), coordination (Stag Hunt, Battle of the Sexes, Pure
  Coordination, Chicken), zero-sum (Matching Pennies, Rock-Paper-Scissors).
- **8 algorithmic strategies**: Always Cooperate/Defect, Tit-for-Tat, Generous
  TFT, Grim Trigger, Win-Stay-Lose-Shift, Random, Nash Mixed.
- **Seeded, reproducible experiments** — every run stores its RNG seed
  (mulberry32); the same seed reproduces every round exactly.
- **Replicated batches** — matchups with probabilistic strategies run as
  20-seed batches; statistics carry 95% t-intervals.
- **Per-class metrics (v2)** — welfare ratio and cooperation rates for
  dilemmas; equilibrium-outcome/coordination rates for coordination games;
  exploitability and G-tests for zero-sum games. See `docs/METRICS.md`.
- **Mechanical claim adjudication** — claims carry structured predicates and
  receive supported/refuted/inconclusive/untested verdicts with effect sizes.
- **Data-driven papers** with a mandatory errata section. The v1 paper and its
  errors are preserved in `docs/v1/` and analyzed in `docs/POSTMORTEM.md`.

## Architecture

```
artifacts/lab          React + Vite frontend (path /)
artifacts/api-server   Express API (path /api), OpenAPI-first
lib/api-spec           openapi.yaml — single source of truth for the API
lib/api-client-react   Orval-generated React Query hooks
lib/api-zod            Orval-generated Zod schemas (server-side validation)
lib/db                 Drizzle ORM schema + Postgres client
scripts/run-phase1.mjs Reproducible pipeline driver (analyses → batches → adjudication → paper)
```

Data model: `games`, `strategies`, `experiments` (seed, batchLabel, totals),
`rounds` (full action/payoff/reasoning provenance), `analyses`
(analysisVersion 2 + metricsJson), `claims` (predicateJson, adjudicationJson),
`papers`.

## Reproducing the results

Everything is API-driven; the UI is a window onto the same data.

```bash
# One experiment, exactly reproducible
curl -X POST localhost:80/api/experiments -H 'Content-Type: application/json' \
  -d '{"gameId":1,"player1StrategyId":3,"player2StrategyId":2,"numRounds":50,"seed":12345}'
curl -X POST localhost:80/api/experiments/<id>/run       # deterministic given seed
curl -X POST localhost:80/api/experiments/<id>/analysis  # v2 metrics

# A 20-seed replicate batch
curl -X POST localhost:80/api/experiments/batch -H 'Content-Type: application/json' \
  -d '{"gameId":5,"player1StrategyId":7,"player2StrategyId":8,"numRounds":50,"seeds":[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20]}'

# Aggregate with 95% CIs
curl 'localhost:80/api/analyses/aggregate?gameId=5&batchLabel=...'

# Re-adjudicate every claim from stored predicates
curl -X POST localhost:80/api/claims/adjudicate-all

# Or run the whole Phase 1 pipeline end to end
node scripts/run-phase1.mjs all
```

Development: `pnpm install`, then the `API Server` and `web` workflows run
`pnpm --filter @workspace/api-server run dev` and
`pnpm --filter @workspace/lab run dev`. After changing `lib/api-spec/openapi.yaml`,
run `pnpm --filter @workspace/api-spec run codegen`. After schema changes,
`pnpm --filter @workspace/db run push`.

## Honesty policy

- Claims are stated as machine-checkable predicates; the adjudicator — not the
  author — assigns verdicts.
- Refuted claims stay on the record with their evidence (see Claims page).
- Inconclusive means inconclusive: thresholds are not adjusted after seeing
  data.
- Metrics are only reported for game classes where they are defined.
- `docs/POSTMORTEM.md` documents every known v1 error in detail.

## Key documents

| File | Contents |
|---|---|
| `docs/METRICS.md` | Formal definitions of every v2 metric and adjudication rule |
| `docs/POSTMORTEM.md` | The v1 errors, root causes, fixes, verdict deltas |
| `docs/v1/paper-v1.md` | Frozen v1 paper (contains known errors, kept for the record) |
| `docs/v1/claims-v1.json` | Frozen v1 claim set at snapshot time |
| `replit.md` | Working notes: architecture, conventions, decisions |
