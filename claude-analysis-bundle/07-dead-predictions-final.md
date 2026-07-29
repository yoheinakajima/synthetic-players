> **The 12 registered author predictions that failed, verbatim, with what happened instead [CONFIRMATORY] (source: registered records)**

# Dead predictions — final program tally

> **STATUS: WORKING DRAFT — PRE-PUBLICATION, NOT FOR CITATION.**
> EXPLORATORY compilation (close-out §3). Confirmatory records:
> `docs/dead-predictions.md` (v1–P4), `docs/phase5-close/adjudication-report.md` (P5).

Every entry was a pre-registered author prediction — direction stated before
data — that the adjudication machinery refuted on the record. Entries 1–10
are quoted from `docs/dead-predictions.md` (unchanged); 11–12 are the Phase 5
additions. Final count: **twelve affirmative refutations.**

| # | Claim | The author predicted | Verdict (key number) | Record |
|---|---|---|---|---|
| 1 | v1 Claim 1 | TFT > 50% cooperation vs Always Defect | **REFUTED** — 0.02 (margin −0.48) | `docs/POSTMORTEM.md` |
| 2 | P3-A1 | Round-1 cooperation higher at δ=.90 than δ=.10 | **REFUTED** — 0.000 at both | `docs/phase3-report.md` |
| 3 | P3-A2 | Risk-dominance separation across δ | **REFUTED** — 0.000 vs 0.000 | `docs/phase3-report.md` |
| 4 | P3-A3 | Round-1 cooperation in human band [36%, 63%] | **REFUTED** — 0.000 | `docs/phase3-report.md` |
| 5 | P3-A4 | Isomorph invariance | **REFUTED** — separation limb fails | `docs/phase3-report.md` |
| 6 | P3-C1 | RPS rock share in [33%, 40%] | **REFUTED** — rock 0.80 | `docs/phase3-report.md` |
| 7 | P3-C3 | First-order tracker exploits the LLM | **REFUTED, sign reversed** — −0.103, CI all-negative | `docs/phase3-report.md` |
| 8 | P3-X1 | The 0.000 corner survives rewording | **REFUTED** — flips to 1.000 under paraphrase | `docs/phase3-report.md` §6 |
| 9 | P4-D3-1 | Labeled-option bias toward first-listed | **NOT SUPPORTED, sign reversed** — −0.1806 | `docs/phase4/d3-report.md` |
| 10 | P4-F directional | Shuffled-history underperforms fo-tracker | **NOT SUPPORTED, nominal sign reversed** — Δ −0.083 | `docs/phase4/f-report.md` |
| 11 | **P5-2** | Task-text switches dominate persona leaning (task-dominant at CP LB ≥ 0.80) | **FAILED — opposite verdict returned: persona-dominant** (pooled task-consistent share 0.128, CP95 [0.104, 0.155], UB ≤ 0.20) | `docs/phase5-close/adjudication-report.md` |
| 12 | **P5-3** | Zero of 16 personas pass the interior-persona existence predicate | **FAILED — 16/16 pass**; p13 passes the Family-E signature clause (δ-slope LB +0.083 > 0), the only arm in the program to do so | `docs/phase5-close/adjudication-report.md` |

Predictions that **held** in Phase 5, for the full picture: P5-1a (corner
mixture, supported 0.094 < 0.10 — by one unit), P5-4 (temperature adds no
interior structure: not refuted, Newcombe LB −0.095; and its noise-mechanism
half *failed descriptively* — entropy fell with T and invalid rate stayed 0,
but that half was registered as secondary, not verdict-bearing).

The program's scoreboard against its own author closes at **12 refuted
predictions across 5 phases**, adjudicated entirely by sealed code. The two
Phase 5 refutations are the most consequential: they select Branch 2 and
invert the interpretation of Phases 3–4 (corner behavior characterizes the
bare subject, not the model's capability envelope).
