# Count reconciliation

> **STATUS: GENERATED FROM THE ARCHIVED EVENT AND BUDGET STORES — ZERO SUBJECT CALLS.** Counts use different nouns and scopes; none should be described generically as the number of subjects.

## Full archived event store

| unit | count | definition |
|---|---:|---|
| distinct run IDs with any event | 5,540 | any run identifier appearing in the event table |
| completed runs / replay observations | 5,505 | distinct run IDs with `run.completed` |
| invalidated runs | 0 | distinct run IDs with `trial.invalidated` |
| round events | 54,276 | simultaneous move pairs recorded as `round.played` |
| seat-round decisions | 108,552 | two player actions per round event |
| archived provider requests | 36,251 | `llm.requested` events; multi-round episodes contain many requests |

## By phase heuristic

| phase label | provider requests | completed runs |
|---|---:|---:|
| phase4 | 19,993 | 2,864 |
| phase5 | 10,428 | 1,712 |
| unattributed | 5,830 | 929 |

Detailed block × model counts: `figure-sources/count-reconciliation-by-block.csv`. Budget-ledger totals, when present, are in `figure-sources/count-reconciliation-budget.csv`. Machine-readable summary: `figure-sources/count-reconciliation.json`.

## Reporting rule

Use `episodes/runs`, `round events`, `seat-round decisions`, `provider requests`, and `replay observations` only with their exact definitions and scope. The full-store provider-request count is not interchangeable with the Phase 4 transactional ledger or the Phase 5 episode count.
