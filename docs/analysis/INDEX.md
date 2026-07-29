# Analysis pack — index

> **STATUS: WORKING DRAFT — PRE-PUBLICATION, NOT FOR CITATION.** Nothing in this directory changes historical mechanical verdicts. Sealed confirmatory records remain in the phase reports and `docs/phase5-close/`; later analyses are explicitly labeled post-adjudication or exploratory.

## Paper-facing entry points

| file | contents |
|---|---|
| [`../paper/paper-draft.md`](../paper/paper-draft.md) | Current v4 manuscript with completed submission analyses integrated |
| [`submission-blockers.md`](submission-blockers.md) | Current gate: statistical blockers closed; citation, bibliography, and final link/release checks remain |
| [`novelty-relationships.md`](novelty-relationships.md) | Occupied territory, safe differentiation, and claims to avoid |
| [`literature-map.md`](literature-map.md) | Thematic map spanning synthetic participants, strategic behavior, personas, causal surrogacy, validity, and metascience |
| [`propositions.md`](propositions.md) | Partial identification, microstructure, and cross-condition coupling |
| [`hierarchy.md`](hierarchy.md) | Counting units, dependence clusters, and fixed-panel versus persona-population estimands |
| [`program-synthesis-DRAFT.md`](program-synthesis-DRAFT.md) | Full v1→Phase 5 arc with the final zero-call corrections |

## Completed submission analyses (`submission/`)

| file | result |
|---|---|
| [`submission/episode-cluster-sensitivity.md`](submission/episode-cluster-sensitivity.md) | Historical 3/32 restricted interior cells; exact episode 2/32; Dirichlet–Jeffreys 5/32. Binary P5-1a classification is method-sensitive. |
| [`submission/p13-family-audit-final.md`](submission/p13-family-audit-final.md) | Historical gate familywise p=0.0592; exact episode gate excludes p13 and yields maximum surviving slope +0.0833, p=0.7732. |
| [`submission/variance-correction.md`](submission/variance-correction.md) | Corrected between-prompt SD 0.418–0.478; approximately 85%–96% of episode-level variation lies between prompt configurations. |
| [`submission/count-reconciliation.md`](submission/count-reconciliation.md) | Reconciles 5,505 archived completed runs, 4,576 replay-contract runs, 36,251 request events, and 30,530 Phase 4–5 ledger calls. |
| [`submission/submission-analysis-summary.json`](submission/submission-analysis-summary.json) | Machine-readable summary of all completed zero-call analyses |
| [`submission/figure-sources/`](submission/figure-sources/) | Cell-level, family-audit, variance, P5-2, clause-(b), and count CSV/JSON outputs |

Reproduction scripts:

- `artifacts/api-server/engine/submission_gate_analyses.py`
- `artifacts/api-server/engine/submission_gate_finalize.py`
- `artifacts/api-server/engine/submission_gate_exact_cluster.py`
- `.github/workflows/submission-gate-analyses.yml`

## Core close-out documents

| file | contents |
|---|---|
| `claims-ledger.md` / `claims-ledger.csv` | Every registered claim v1→P5 with tier, direction, historical verdict, key number, and record pointer |
| `dead-predictions-final.md` | Twelve author predictions refuted by data, distinct from the later inferential downgrade |
| `human-anchor-scorecard.md` | Published human references with nonmatched-comparator scope notes |
| `corner-map.md` | Historical seat-level interior/corner map, including disclosed not-run lanes |
| `persona-pack/README.md` | Persona-panel composition and the historical p13/swap record; superseded for inference by `submission/` |
| `temperature-pack/README.md` | Temperature sweep, entropy observation, invalid-output record, and unit-level movement |
| `distribution-pack/README.md` | Historical distribution comparison; use the corrected variance analysis for paper claims |
| `stability-compendium.md` | Sentinel trajectories, replay record, and cross-vendor anti-replication |
| `ops-meta.md` | Budget accounting, freeze ledger, linter escapes, and integrity-layer cost |

## Earlier R2 revision documents

| file | contents |
|---|---|
| `r2/p13-family-audit.md` | Initial 2,000-permutation audit; superseded by `submission/p13-family-audit-final.md` |
| `claim-dependencies.md` | Earlier language-dependency scan; a final automated scan remains before submission |
| `persona-table.md` | All sixteen sealed persona sentences and hashes; confirmatory unit is the complete sentence |
| `cut-map.md` | Main/supplement architecture |
| `df-microdata-PENDING.md` | Official DF2011 data access status and exact operator action |
| `r2/df2011-reanalysis-FIXTURE-SELFTEST.md` | Synthetic-fixture self-test of the DF reanalysis script—not DF results |
| `r2/capsule-verification.md` | Clean-directory capsule verification: 4,576/4,576 byte-exact, zero credentials |

## Post-verdict analyses (`post-verdict/`)

These are exploratory, zero-call reanalyses of the archived data. Read order in `post-verdict/INDEX.md`:

- clause-(b) confound anatomy;
- p13 deep-dive, now superseded for inference by the exact family audit;
- interior-cell census;
- P5-2 decomposition;
- entropy-versus-temperature observation.

## Historical figure sources (`figure-sources/`)

| csv | figure it feeds |
|---|---|
| `p5-persona-cell-map.csv` | Historical 96-cell seat-level interior map |
| `p5-persona-means.csv` | Per-persona round-one means and leaning splits |
| `p5-temperature-curves.csv` | Interiority and mean versus temperature |
| `p5-swap-refusal.csv` | Historical swap-cell shares |
| `p5-tierC-gemini.csv` | Descriptive cross-vendor gates |
| `p5-bare-anchors.csv` | Bare gate table used in outcome-blind completion D1 |
| `p4-x2-span-ladder.csv` | X2 paraphrase-span ladder |
| `p4-d2-swap.csv` | D2 role/word cells |
| `p4-e-ceiling.csv` | E corner-confounding |
| `p4-f-adversary.csv` | F adversary performance |
| `p4-sentinel-gemini-oscillation.csv` | Cross-vendor sentinel trajectory |

The historical analysis pack can be regenerated with:

```bash
cd artifacts/api-server
uv run --with numpy --with scipy python engine/gen_analysis_pack.py
```
