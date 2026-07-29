# Analysis pack — index (close-out §3)

> **STATUS: WORKING DRAFT — PRE-PUBLICATION, NOT FOR CITATION.**
> EXPLORATORY unless a row explicitly points to a sealed phase report. Nothing in this directory changes historical verdicts; confirmatory numbers live in the per-phase reports and `docs/phase5-close/`.

## Paper-facing entry points

| file | contents |
|---|---|
| [`../paper/paper-draft.md`](../paper/paper-draft.md) | Current full paper draft, revised through the submission-gate audit |
| [`submission-blockers.md`](submission-blockers.md) | Active submission gate: zero-call statistical sensitivities, citation work, count reconciliation, and release polish |
| [`novelty-relationships.md`](novelty-relationships.md) | Closest occupied territory, safe differentiation, and claims to avoid |
| [`literature-map.md`](literature-map.md) | Thematic literature map spanning synthetic participants, strategic behavior, personas, causal surrogacy, validity, and metascience |
| [`propositions.md`](propositions.md) | Partial-identification, microstructure, and cross-condition-coupling propositions |
| [`hierarchy.md`](hierarchy.md) | Deployment→call hierarchy, historical counting units, dependence clusters, and fixed-panel versus persona-population estimands |

## Core close-out documents

| file | contents |
|---|---|
| `claims-ledger.md` / `claims-ledger.csv` | Every registered claim v1→P5 with tier, direction, verdict, key number, and record pointer |
| `dead-predictions-final.md` | Final tally: **12 refuted author predictions** across five phases, distinct from the later post-adjudication inferential downgrade |
| `human-anchor-scorecard.md` | Human-anchored comparisons with published comparator status and scope notes |
| `corner-map.md` | Interior/corner flags for every cell run, including disclosed not-run lanes |
| `persona-pack/README.md` | Persona-panel composition, interior cells, p13 record, and swap-cell ambiguity |
| `temperature-pack/README.md` | Temperature sweep, entropy observation, invalid-output record, and unit-level movement |
| `distribution-pack/README.md` | Persona panel versus published nonmatched comparator: coarse marginal checks, observed dispersion, weak δ response, and shape notes |
| `stability-compendium.md` | Sentinel trajectories, 4,576 byte-exact replays, and cross-vendor anti-replication |
| `ops-meta.md` | Budget accounting, freeze ledger, linter escapes, and integrity-layer cost |
| `program-synthesis-DRAFT.md` | Earlier close-out synthesis; retained as a living analysis artifact, superseded for paper wording by `docs/paper/paper-draft.md` |

## R2 and submission-audit documents

| file | contents |
|---|---|
| `r2/p13-family-audit.md` | Initial post-adjudication family audit: 2,000-permutation boundary result; p13 downgraded from confirmatory interpretation; final high-precision audit remains a submission task |
| `claim-dependencies.md` | Scan of language depending on p13 status, comparator matching, human interiority, trait causality, guard wording, and moment matching |
| `persona-table.md` | All sixteen sealed persona sentences verbatim with hashes; confirmatory unit is the complete sentence |
| `cut-map.md` | Main/supplement architecture: claim, mechanism, and credibility layers |
| `df-microdata-PENDING.md` | DF2011 microdata access status and scoped fallback |
| `r2/df2011-reanalysis-FIXTURE-SELFTEST.md` | Self-test transcript of the DF reanalysis pipeline using a synthetic fixture, not DF values |
| `r2/capsule-verification.md` | Clean-directory capsule verification: 4,576/4,576 byte-exact, zero credentials |

## Post-verdict analyses (`post-verdict/`)

Targeted re-analyses of the recorded data answering questions opened by the Phase 5 verdicts. These are exploratory, use zero new subject calls, and are generated from the event store. Read order in `post-verdict/INDEX.md`:

- clause-(b) confound anatomy;
- p13 deep-dive;
- interior-cell census;
- P5-2 decomposition;
- entropy-versus-temperature observation.

Figure sources are under `post-verdict/figure-sources/pv-*.csv`.

## Figure sources (`figure-sources/`)

| csv | figure it feeds |
|---|---|
| `p5-persona-cell-map.csv` | 96-cell interior map under the historical registered rule |
| `p5-persona-means.csv` | Per-persona round-one means, histograms, and leaning splits |
| `p5-temperature-curves.csv` | Interiority and mean versus temperature per unit, including bare lanes |
| `p5-swap-refusal.csv` | Swap-cell word-choice shares per persona × temperature |
| `p5-tierC-gemini.csv` | Descriptive cross-vendor gates |
| `p5-bare-anchors.csv` | Bare gate table used in outcome-blind completion D1 |
| `p4-x2-span-ladder.csv` | X2 paraphrase-span ladder rung means |
| `p4-d2-swap.csv` | D2 role/word cell means, both vendors |
| `p4-e-ceiling.csv` | E assay δ-cell means and corner-confounding |
| `p4-f-adversary.csv` | F per-arm per-round advantage, both vendors |
| `p4-sentinel-gemini-oscillation.csv` | v2a × Gemini sentinel trajectory |

Regenerate the P5 CSVs from the event store:

```bash
cd artifacts/api-server
uv run --with numpy --with scipy python engine/gen_analysis_pack.py
```

The generated pack is exploratory unless a file explicitly points to a sealed confirmatory source.
