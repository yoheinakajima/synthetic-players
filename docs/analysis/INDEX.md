# Analysis pack — reviewer index

> **STATUS: READY FOR FULL SCIENTIFIC REVIEW — WORKING MATERIAL, NOT FOR CITATION.** Nothing here changes historical mechanical verdicts. Sealed records remain in the phase reports and `docs/phase5-close/`; later analyses are explicitly labeled post-adjudication or exploratory.

## Reviewer entry points

| file | contents |
|---|---|
| [`../../REVIEW.md`](../../REVIEW.md) | Canonical review instructions, claim summary, reproduction command, and review questions |
| [`../paper/paper-draft.md`](../paper/paper-draft.md) | Current v8 Markdown manuscript |
| [`../paper/synthetic-players-review-draft-v8.pdf`](../paper/synthetic-players-review-draft-v8.pdf) | Line-numbered Explore Science review PDF with five figures |
| [`../reviews/`](../reviews/) | Round 1–4 review archive, role disclosure, and Round 4 direct outside reproduction |
| [`submission-blockers.md`](submission-blockers.md) | Scientific review gate complete; formal-submission and history tasks tracked explicitly |
| [`novelty-relationships.md`](novelty-relationships.md) | Occupied territory, precise differentiation, and claims to avoid |
| [`literature-map.md`](literature-map.md) | Synthetic participants, strategic behavior, personas, causal surrogacy, validity, and metascience |
| [`propositions.md`](propositions.md) | Partial identification, microstructure, and cross-condition coupling |
| [`hierarchy.md`](hierarchy.md) | Counting units, dependence clusters, fixed-panel and persona-population estimands |
| [`../paper/scope-seal-status.md`](../paper/scope-seal-status.md) | Living clarification of the byte-sealed stopping rule |

## Completed submission analyses (`submission/`)

| file | result |
|---|---|
| [`submission/episode-cluster-sensitivity.md`](submission/episode-cluster-sensitivity.md) | Historical/exact/Dirichlet restricted counts 3/2/5 of 32 and all-cell counts 14/11/19 of 96; binary classification is method-sensitive. |
| [`submission/p13-family-audit-final.md`](submission/p13-family-audit-final.md) | All computed variants reported: historical gate p=0.059230; retained non-primary percentile-bootstrap p=0.043455; primary exact-episode gate excludes p13 and yields p=0.773206. |
| [`submission/variance-correction.md`](submission/variance-correction.md) | Corrected between-prompt SD 0.418–0.478; approximately 85%–96% of episode-level variation lies between prompt configurations. |
| [`submission/count-reconciliation.md`](submission/count-reconciliation.md) | Reconciles 5,505 archived completed runs, 4,576 replay-contract runs, 108,552 seat-round decisions, 36,251 request events, and 30,530 Phase 4–5 ledger calls. |
| [`submission/submission-analysis-summary.json`](submission/submission-analysis-summary.json) | Machine-readable summary, including aggregate and per-prompt continuation-probability contrasts |
| [`submission/figure-sources/`](submission/figure-sources/) | Cell-level, family-audit, variance, P5-2, clause-(b), and count CSV/JSON outputs |
| [`../paper/figures/prompt-indexed-delta.svg`](../paper/figures/prompt-indexed-delta.svg) | Prompt-indexed δ-response figure with exact intervals and aggregate uncertainty |

### Reproduction scripts

- `artifacts/api-server/engine/submission_gate_analyses.py`
- `artifacts/api-server/engine/submission_gate_finalize.py`
- `artifacts/api-server/engine/submission_gate_exact_cluster.py`
- `artifacts/api-server/engine/submission_gate_variance_fixed.py`
- `scripts/augment_p13_audit_variants.py`
- `scripts/generate_prompt_delta_figure.py`
- `.github/workflows/submission-gate-analyses.yml`

## Core close-out documents

| file | contents |
|---|---|
| `claims-ledger.md` / `claims-ledger.csv` | Every registered claim v1→P5 with tier, direction, historical verdict, key number, and record pointer |
| `dead-predictions-final.md` | Twelve author predictions refuted by data, distinct from the later inferential downgrade |
| `human-anchor-scorecard.md` | Published human references with protocol-nonmatched scope notes |
| `corner-map.md` | Historical seat-level boundary map, including disclosed not-run lanes |
| `persona-table.md` | All sixteen sealed persona sentences and hashes; confirmatory unit is the complete sentence |
| `persona-pack/README.md` | Persona-panel historical analyses; superseded for paper inference by `submission/` |
| `temperature-pack/README.md` | Temperature sweep, entropy observation, invalid-output record, and unit-level movement |
| `distribution-pack/README.md` | Historical distribution comparison; use corrected variance analysis for current paper claims |
| `stability-compendium.md` | Sentinel trajectories, replay record, and cross-vendor anti-replication |
| `ops-meta.md` | Budget accounting, freeze ledger, linter escapes, and integrity-layer cost |
| `program-synthesis-DRAFT.md` | Program-level synthesis; current paper wording lives in `docs/paper/paper-draft.md` |

## Superseded and contextual analyses

| file | status |
|---|---|
| `r2/p13-family-audit.md` | Initial 2,000-permutation audit; superseded by the final submission audit |
| `claim-dependencies.md` | Earlier language-dependency scan; final automated lint is authoritative |
| `cut-map.md` | Main/supplement architecture used during revision |
| `df-microdata-PENDING.md` | Licensed DF2011 data access status; contextual Q5 is deferred and nonblocking |
| `r2/df2011-reanalysis-FIXTURE-SELFTEST.md` | Synthetic-fixture self-test, not DF results |
| `r2/capsule-verification.md` | Clean-directory capsule verification |

## Post-verdict analyses (`post-verdict/`)

Exploratory zero-call analyses of archived data:

- clause-(b) confound anatomy;
- p13 deep-dive, superseded for inference by the family audit;
- interior-cell census;
- P5-2 decomposition;
- entropy-versus-temperature observation.

## Historical figure sources (`figure-sources/`)

- `p5-persona-cell-map.csv` — historical 96-cell seat-level map;
- `p5-persona-means.csv` — per-persona round-one means and leaning splits;
- `p5-temperature-curves.csv` — interiority and mean versus temperature;
- `p5-swap-refusal.csv` — historical swap-cell shares;
- `p5-tierC-gemini.csv` — descriptive cross-vendor gates;
- `p5-bare-anchors.csv` — bare gate table used in outcome-blind completion D1;
- `p4-x2-span-ladder.csv` — X2 paraphrase-span ladder;
- `p4-d2-swap.csv` — D2 role/word cells;
- `p4-e-ceiling.csv` — E boundary-confounding;
- `p4-f-adversary.csv` — F adversary performance;
- `p4-sentinel-gemini-oscillation.csv` — cross-vendor sentinel trajectory.
