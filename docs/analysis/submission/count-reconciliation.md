# Count reconciliation

> **STATUS: GENERATED FROM THE ARCHIVED EVENT AND BUDGET STORES — ZERO SUBJECT CALLS.** Counts use different nouns and scopes; none should be described generically as the number of subjects.

## Full archived event store

| unit | count | definition |
|---|---:|---|
| distinct run IDs with any event | 5,540 | any run identifier appearing in the event table |
| archived completed runs | 5,505 | all distinct run IDs with `run.completed`, including earlier phases |
| public Phase 4+5 replay observations | 4,576 | 2,864 Phase 4 plus 1,712 Phase 5 completed runs covered by the public replay contract |
| invalidated runs | 0 | distinct run IDs with `trial.invalidated` |
| round events | 54,276 | simultaneous move pairs recorded as `round.played` |
| seat-round decisions | 108,552 | two player actions per round event |
| archived provider-request events | 36,251 | all `llm.requested` events in the full store |

## Phase 4+5 transactional budget ledger

| scope | calls |
|---|---:|
| Phase 4, including X2, sentinels, and infrastructure | 20,102 |
| Phase 5, including entry and sentinels | 10,428 |
| **Phase 4+5 total** | **30,530** |

The same ledger records **13,141,675 input tokens** and **45,247 output tokens**. It is narrower than the full event store because earlier phases were not recorded in this transactional ledger.

## By phase heuristic in the event store

| phase label | provider requests | completed runs |
|---|---:|---:|
| phase4 | 19,993 | 2,864 |
| phase5 | 10,428 | 1,712 |
| unattributed | 5,830 | 929 |

Detailed block × model counts: `figure-sources/count-reconciliation-by-block.csv`. Budget-ledger totals are in `figure-sources/count-reconciliation-budget.csv`. Machine-readable summary: `figure-sources/count-reconciliation.json`.

## Reporting rule

Use `episodes/runs`, `round events`, `seat-round decisions`, `provider requests`, `transactional ledger calls`, and `replay observations` only with their exact definitions and scope. In particular, 5,505 archived completed runs are not the same quantity as the 4,576-run Phase 4+5 public replay contract, and 36,251 archived request events are not the same scope as the 30,530-call Phase 4+5 transactional ledger.
