# Claude analysis bundle — INDEX (read in order)

Handoff package for the pre-final-paper analysis session. The registered record is CLOSED; files marked CONFIRMATORY are the record, files marked EXPLORATORY are descriptive re-analysis and carry no verdict weight. Everything is regenerable from the event store in the repo (release `phase5-final`).

| # | file | status | what it is |
|---|---|---|---|
| 01 | `01-phase5-final-report.md` | CONFIRMATORY | Phase 5 final report: sealed predicates P5-1a/1b/2/3/4, axes, Branch 2 |
| 02 | `02-phase4-final-report.md` | CONFIRMATORY | Phase 4 final report: D1-D3/E/F/X1/X2 verdicts (as sealed) |
| 03 | `03-phase3-report.md` | CONFIRMATORY | Phase 3 report (as sealed) |
| 04 | `04-branch-selection.md` | CONFIRMATORY | Machine branch-selection record: axes A/B/C -> Branch 2, variant retained |
| 05 | `05-discussion-branches-SEALED.md` | CONFIRMATORY | Sealed pre-committed discussion branches, byte-identical to registration sha 1f1d7de9...e356; Branch 2 is the selected text |
| 06 | `06-claims-ledger.md` | CONFIRMATORY | Every registered claim v1->P5 with verdict and source record |
| 06b | `06b-claims-ledger.csv` | CONFIRMATORY | Machine-readable claims ledger (same content as 06) |
| 07 | `07-dead-predictions-final.md` | CONFIRMATORY | The 12 registered author predictions that failed, verbatim, with what happened instead |
| 08 | `08-human-anchor-scorecard.md` | EXPLORATORY | 7 human-benchmark anchors vs the pool: levels/SD match, delta-response ~1/5 human |
| 09 | `09-corner-map.md` | EXPLORATORY | Corner/interior map of all 96 persona-cells + bare lanes |
| 09b | `09b-persona-cell-map.csv` | EXPLORATORY | Per persona-cell: rate, CP95, interior flag (96 rows; the corner-map table) |
| 10 | `10-pv-clause-b-anatomy.md` | EXPLORATORY | P5-3 clause-(b) word/payoff confound anatomy; what the data cannot decide |
| 10b | `10b-pv-swap-choice.csv` | EXPLORATORY | Per-persona x T swap choice table (refusal + word-choice, CIs) |
| 11 | `11-pv-p13-deep-dive.md` | EXPLORATORY | p13 (sole delta-slope pass): card, all cells, trajectories, trait gradient |
| 12 | `12-pv-interior-census.md` | EXPLORATORY | Corrected census of all 14 interior persona-cells (Branch-2 exhibit) |
| 12b | `12b-pv-interior-census.csv` | EXPLORATORY | The 14 interior cells as data (persona, cell, rate, CI) |
| 13 | `13-pv-p52-decomposition.md` | EXPLORATORY | P5-2 pooled 0.128 split: unconfounded rep subset vs word-confounded swap |
| 14 | `14-pv-entropy-anomaly.md` | EXPLORATORY | Falling entropy-vs-T decomposed by lane/family; matched-unit Simpson test |
| 15 | `15-persona-pack.md` | EXPLORATORY | Persona-pack key tables: leaning gaps, interiority factor pattern, p13 |
| 16 | `16-temperature-pack.md` | EXPLORATORY | Temperature sweep summary incl. the entropy-decline observation |
| 17 | `17-distribution-pack.md` | EXPLORATORY | Pool vs DF2011 human distributions: pins, SDs, bimodality, delta-drop |
| 18 | `18-stability-compendium.md` | EXPLORATORY | Every stability/replication check across the program in one place |
| 19 | `19-adjudication-decisions.json` | CONFIRMATORY | All four outcome-blind completions (D1-D3 + twin table), operator-signed, verbatim rationales |
| 20 | `20-instance-ledger.md` | CONFIRMATORY | Instance ledger: every process deviation/underspecification across the program |
| 21 | `21-ops-meta.md` | EXPLORATORY | Operational meta: budget, invalids, sentinels, infrastructure notes |
| 22 | `22-program-synthesis-DRAFT.md` | EXPLORATORY | WORKING DRAFT program synthesis — no new claims; the narrative skeleton |

Total bundle size: 0.12 MB of text (26 files).

Companion (not in bundle, in repo/release): full adjudication JSON (`docs/phase5-close/adjudication-report.json`), event-store snapshots, replay audit, figure-source CSVs.
