# Synthetic Players

> **STATUS: PREPRINT v12 — NEAR-ARXIV MANUSCRIPT AND COMPLETE PUBLIC RECORD.**

## Reviewing the paper?

**Start at [`REVIEW.md`](REVIEW.md).** It is the shortest path to the manuscript, independent verification, generated analyses, novelty boundary, reproduction command, and highest-value review questions.

Current manuscript:

> **Passing Coarse Marginal Checks Can Be Cheap: Persona Mixtures and Imprecise Treatment-Response Estimates in an LLM Persona Panel**

[`docs/paper/paper-draft.md`](docs/paper/paper-draft.md)

**Formatted review copy:** [`docs/paper/synthetic-players-preprint-v12.pdf`](docs/paper/synthetic-players-preprint-v12.pdf) · [build notes](docs/paper/PDF-README.md)

The sealed experimental program is complete. v11 is an explicit post-v10 review addendum; its zero-call analyses, figures, PDF, lint, and 4,576-run replay are generated in GitHub Actions. Current status: [`docs/analysis/submission-blockers.md`](docs/analysis/submission-blockers.md).

## Reproduce the archived record

Anonymous clone, zero credentials, zero live model calls:

```bash
git clone https://github.com/yoheinakajima/synthetic-players
cd synthetic-players/capsule
bash verify.sh
```

Expected result: **4,916/4,916 confirmatory Phase 3–5 runs verified with zero live model calls.**

## What this project is

Synthetic Players is an open experimental laboratory for placing LLM-controlled agents into formally specified strategic games. It studies:

- how behavior changes across wording, labels, payoffs, opponents, personas, temperature, provider routes, and time;
- which findings belong only to one model–prompt–deployment configuration;
- whether persona-conditioned panels preserve response to an experimental lever rather than merely broad aggregate resemblance;
- how preregistration, event sourcing, mechanical adjudication, exact replay, drift monitoring, and post-adjudication correction can make machine-speed research auditable.

The paper's narrow empirical result is:

> A fixed panel of sixteen lightweight persona prompts passed preregistered **coarse marginal checks**. A fixed-panel latent-propensity sensitivity yields median between-prompt shares of 63%–71% (95% intervals 49%–81%); conditional plug-in estimates are 85%–96%. Aggregate continuation-probability contrasts are +0.083 and +0.078 with wide exact intervals, so the study does not establish equivalence or a narrow response bound.

This is not a claim of human substitutability. Human references are protocol-nonmatched, the primary evidence comes from one deployment, and the panel consists of sixteen complete prompt bundles rather than independently sampled people.

## Reviewer map

| artifact | purpose |
|---|---|
| [`REVIEW.md`](REVIEW.md) | Canonical review instructions and questions |
| [`docs/paper/paper-draft.md`](docs/paper/paper-draft.md) | Current v12 preprint Markdown manuscript |
| [`docs/paper/synthetic-players-preprint-v12.pdf`](docs/paper/synthetic-players-preprint-v12.pdf) | Clean review PDF with five vector figures |
| [`docs/paper/history/`](docs/paper/history/) | Exact v2 and v3 manuscripts plus history index |
| [`docs/reviews/`](docs/reviews/) | Round 1–4 review archive, reviewer-role disclosure, and direct outside reproduction |
| [`docs/analysis/submission/submission-analysis-summary.json`](docs/analysis/submission/submission-analysis-summary.json) | Machine-readable generated results |
| [`docs/analysis/submission/`](docs/analysis/submission/) | Exact-episode sensitivity, variance correction, family audit, and count reconciliation |
| [`docs/analysis/novelty-relationships.md`](docs/analysis/novelty-relationships.md) | Occupied territory and precise differentiation |
| [`docs/analysis/literature-map.md`](docs/analysis/literature-map.md) | Broader literature map |
| [`docs/analysis/propositions.md`](docs/analysis/propositions.md) | Partial-identification, microstructure, and coupling statements |
| [`docs/analysis/hierarchy.md`](docs/analysis/hierarchy.md) | Units, clusters, and estimands |
| [`docs/paper/scope-seal-status.md`](docs/paper/scope-seal-status.md) | Scope-seal status and immutable-header explanation |

## Main empirical arc

### Phase 3: one representation, one corner

The bare GPT-4.1 configuration defected in every recorded first round across the registered continuation-probability cells. Framing moved behavior where continuation probability did not, and RPS exhibited a large role-attached rock bias.

Report: [`docs/phase3-report.md`](docs/phase3-report.md)

### X1/X2: one sentence, opposite behavior

Two formally game-equivalent paraphrases moved observed first-round cooperation from 0/20 episodes to 20/20. A registered span ladder localized the switch, and held-out confirmation produced 37/40 cooperation decisions with the switch-bearing sentence versus 0/40 without it.

- [`docs/phase4/x1-semantic-equivalence.md`](docs/phase4/x1-semantic-equivalence.md)
- [`docs/phase4/x1-parser-audit.md`](docs/phase4/x1-parser-audit.md)
- [`docs/phase4/x2-confirmation-report.md`](docs/phase4/x2-confirmation-report.md)

### Phase 4: representation and incentive channels interact

Semantic labels could override payoff dominance in direct conflict, while payoff changes moved behavior when labels did not oppose them. Continuation-probability assays were boundary-confounded at tested surfaces. Adversary behavior was opponent-contingent, and the cross-vendor lane was demoted to descriptive status after sentinel-detected endpoint instability.

- [`docs/phase4/freeze-packet.md`](docs/phase4/freeze-packet.md)
- [`docs/phase4/predicates.md`](docs/phase4/predicates.md)
- [`docs/phase4/final-report.md`](docs/phase4/final-report.md)

### Phase 5: persona conditioning and post-adjudication correction

Sixteen sealed one-sentence personas were crossed with the existing instruments. Historical mechanical verdicts remain intact; completed submission analyses change their scientific interpretation:

| claim | historical result | current interpretation |
|---|---|---|
| P5-1a boundary-mixture predicate | 3/32 restricted cells interior under seat-level CP | Exact episode 2/32; Dirichlet–Jeffreys 5/32. The binary verdict is method-sensitive; continuous composition is primary. |
| P5-1b dispersion comparison | Raw cross-persona SD 0.424–0.480 | Corrected SD 0.418–0.478; approximately 85%–96% of episode-level variation lies between prompt configurations. |
| P5-2 surface-cue dominance | Pooled persona-dominant result | Pooled exact result survives, but the word/payoff-confounded swap cell carries the classification. |
| P5-3 persona-level existence | p13 passed the frozen per-candidate rule | All three post-review family variants are disclosed. The conservative exact sensitivity makes p13 gate-ineligible but is underpowered at n=6; p13 is neither prospectively confirmed nor decisively disconfirmed and remains a replication target. |
| P5-3 clause (b) | All personas passed refusal threshold | All 24 lanes survive simultaneous exact family bounds; choice result is strong, mechanism remains confounded. |

- [`docs/phase5/final-report.md`](docs/phase5/final-report.md)
- [`docs/phase5-close/adjudication-report.md`](docs/phase5-close/adjudication-report.md)
- [`docs/analysis/submission/episode-cluster-sensitivity.md`](docs/analysis/submission/episode-cluster-sensitivity.md)
- [`docs/analysis/submission/p13-family-audit-final.md`](docs/analysis/submission/p13-family-audit-final.md)
- [`docs/analysis/submission/variance-correction.md`](docs/analysis/submission/variance-correction.md)

Sealed historical records are never rewritten. Living documents carry corrections beside quoted historical interpretation.

## Research-integrity contract

The repository records prompt registries, external chronology anchors, archived requests and completions, seeded environment state, adjudication inputs, failed and retried calls, exact replay, registered refutations, post-adjudication corrections, reviewer role changes, and independent verification.

The central boundary is explicit:

> The pipeline can enforce a registered predicate exactly; it cannot guarantee that the predicate represents a valid estimand, test family, or construct.

See [`docs/instance-ledger.md`](docs/instance-ledger.md), [`docs/analysis/claims-ledger.md`](docs/analysis/claims-ledger.md), and [`docs/analysis/dead-predictions-final.md`](docs/analysis/dead-predictions-final.md).

## Counts and scopes

Counts are reconciled in [`docs/analysis/submission/count-reconciliation.md`](docs/analysis/submission/count-reconciliation.md). They are not interchangeable subjects:

- **5,505 archived completed runs** across the full store;
- **4,576 Phase 4–5 replay-contract runs**;
- **54,276 round events** and **108,552 seat-round decisions**;
- **36,251 provider-request events** across the full store;
- **30,530 Phase 4–5 calls** in the transactional ledger;
- **13,141,675 input tokens** and **45,247 output tokens** in that ledger.

## Reproduce the post-adjudication analyses

The submission analyses make no provider calls and run against the archived databases:

```bash
mkdir -p artifacts/api-server/engine/data
xz -dkc capsule/data/engine.db.xz > artifacts/api-server/engine/data/engine.db
xz -dkc capsule/data/budget.db.xz > artifacts/api-server/engine/data/budget.db
python -m pip install numpy scipy
python artifacts/api-server/engine/submission_gate_analyses.py
python artifacts/api-server/engine/submission_gate_finalize.py
python artifacts/api-server/engine/submission_gate_exact_cluster.py
python scripts/augment_p13_audit_variants.py
python artifacts/api-server/engine/submission_gate_variance_fixed.py
python scripts/generate_prompt_delta_figure.py
```

The same sequence is executed by [`.github/workflows/submission-gate-analyses.yml`](.github/workflows/submission-gate-analyses.yml). Generated outputs are committed under `docs/analysis/submission/` and `docs/paper/figures/`.

## Status, license, and citation

The repository became public on 2026-07-29. The sealed experimental program is closed; no new dispatch is authorized without a new registration. Paper-facing review may continue without modifying sealed artifacts or historical verdicts.

Code is MIT-licensed under [`LICENSE`](LICENSE). Released data artifacts and generated research records are CC BY 4.0. Citation metadata are in [`CITATION.cff`](CITATION.cff). The current paper remains a working draft and should not yet be cited.
