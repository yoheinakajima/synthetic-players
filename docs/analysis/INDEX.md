# Analysis pack — index (close-out §3)

> **STATUS: WORKING DRAFT — PRE-PUBLICATION, NOT FOR CITATION.**
> EXPLORATORY. Nothing in this directory is verdict-bearing; every
> confirmatory number lives in the per-phase reports and
> `docs/phase5-close/`. Compiled 2026-07-28 after the Phase 5 close-out
> adjudication (Branch 2 selected).

## Documents

| file | contents |
|---|---|
| `claims-ledger.md` / `claims-ledger.csv` | Every registered claim v1→P5 with tier, direction, verdict, key number, record pointer |
| `dead-predictions-final.md` | Final tally: **12 refuted author predictions** across 5 phases (10 from v1–P4 + P5-2, P5-3), with the held-predictions reconciliation |
| `human-anchor-scorecard.md` | All 7 human-anchored comparisons: bare subject vs persona pool vs published pins |
| `corner-map.md` | Interior/corner flags for every cell ever run, incl. the 3 not-run bare rep lanes (disclosed) |
| `persona-pack/README.md` | Leaning mixture, interior-persona factor structure, p13 (δ-slope persona), swap-cell mechanism ambiguity |
| `temperature-pack/README.md` | T-sweep: entropy *falls* with T, 0 invalids at T=1.3, interior movement per unit |
| `distribution-pack/README.md` | Persona pools vs DF2011: levels/SD match, δ-response 5× too small, bimodal shape |
| `stability-compendium.md` | Sentinel trajectories all phases, 4,576 byte-exact replays, cross-vendor anti-replication |
| `ops-meta.md` | Budget-to-the-call, freeze ledger, linter-escape pattern, cost of the integrity layer |
| `program-synthesis-DRAFT.md` | §4 working-draft synthesis: the v1→P5 arc in one document (no new claims) |

## Post-verdict analyses (`post-verdict/`)

Targeted re-analyses of the recorded data answering the questions the
Branch-2 verdicts opened (EXPLORATORY; zero new subject calls; generated
by `engine/gen_post_verdict.py`). Read order in `post-verdict/INDEX.md`:
clause-(b) confound anatomy · p13 deep-dive · interior-cell census ·
P5-2 decomposition · entropy-vs-T anomaly. Figure sources under
`post-verdict/figure-sources/pv-*.csv`.

## Figure sources (`figure-sources/`)

| csv | figure it feeds |
|---|---|
| `p5-persona-cell-map.csv` | 96-cell interior map (tier A) with CP bounds |
| `p5-persona-means.csv` | per-persona round-1 means per cell (histograms, leaning splits) |
| `p5-temperature-curves.csv` | interior/mean vs T per unit, incl. bare lanes |
| `p5-swap-refusal.csv` | swap-cell word-choice shares per persona × T |
| `p5-tierC-gemini.csv` | tier-C descriptive gates |
| `p5-bare-anchors.csv` | the bare gate table used in outcome-blind completion D1 |
| `p4-x2-span-ladder.csv` | X2 paraphrase-span ladder rung means |
| `p4-d2-swap.csv` | D2 role/word cell means, both vendors |
| `p4-e-ceiling.csv` | E assay δ-cell means (corner-confounding) |
| `p4-f-adversary.csv` | F per-arm per-round advantage, both vendors |
| `p4-sentinel-gemini-oscillation.csv` | the v2a × gemini sentinel trajectory |

Regenerate the P5 CSVs: `cd artifacts/api-server && uv run --with numpy
--with scipy python engine/gen_analysis_pack.py` (reads the event store;
exploratory only).
