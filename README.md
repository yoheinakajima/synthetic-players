# Synthetic Players

> **STATUS: WORKING RESEARCH RELEASE — PRE-PUBLICATION, NOT FOR CITATION.**
> The sealed experimental program is complete through Phase 5. The current manuscript is [`docs/paper/paper-draft.md`](docs/paper/paper-draft.md); the remaining editorial submission gate is tracked in [`docs/analysis/submission-blockers.md`](docs/analysis/submission-blockers.md).

**Replay the public Phase 4–5 record in one command** — anonymous clone, zero credentials, zero live model calls:

```bash
git clone https://github.com/yoheinakajima/synthetic-players
cd synthetic-players/capsule
bash verify.sh
```

Expected result: **4,576/4,576 completed Phase 4–5 runs replay byte-exact.**

## What this project is

Synthetic Players is an open experimental laboratory for placing LLM-controlled agents into formally specified strategic games. It studies:

- how behavior changes across wording, labels, payoff structures, opponents, personas, temperature, provider routes, and time;
- which findings belong only to one model–prompt–deployment configuration;
- whether persona-conditioned panels preserve response to an experimental lever rather than merely broad aggregate resemblance;
- how preregistration, event sourcing, mechanical adjudication, exact replay, and post-adjudication correction can make machine-speed research auditable.

The current paper’s narrow empirical claim is:

> A fixed panel of sixteen lightweight persona prompts passed preregistered **coarse marginal checks** while showing a small continuation-probability comparative static. Corrected variance estimates place approximately 85%–96% of episode-level variation between prompt configurations; the exact binary corner count is interval-method-sensitive.

This is not a claim of human substitutability. Published human references are protocol-nonmatched, the primary results come from one deployment, and the panel contains sixteen complete prompt bundles rather than independently sampled people.

## Current paper and analysis materials

- **Paper draft v4:** [`docs/paper/paper-draft.md`](docs/paper/paper-draft.md)
- **Submission status:** [`docs/analysis/submission-blockers.md`](docs/analysis/submission-blockers.md)
- **Completed zero-call analyses:** [`docs/analysis/submission/`](docs/analysis/submission/)
- **Novelty relationships:** [`docs/analysis/novelty-relationships.md`](docs/analysis/novelty-relationships.md)
- **Literature map:** [`docs/analysis/literature-map.md`](docs/analysis/literature-map.md)
- **Identification propositions:** [`docs/analysis/propositions.md`](docs/analysis/propositions.md)
- **Sample hierarchy and estimands:** [`docs/analysis/hierarchy.md`](docs/analysis/hierarchy.md)
- **Analysis index:** [`docs/analysis/INDEX.md`](docs/analysis/INDEX.md)

## Main empirical arc

### Phase 3: one representation, one corner

The bare GPT-4.1 configuration defected in every recorded first round across the registered continuation-probability cells. Framing moved behavior where continuation probability did not, and RPS exhibited a large role-attached rock bias.

Report: [`docs/phase3-report.md`](docs/phase3-report.md)

### X1/X2: one sentence, opposite behavior

Two formally game-equivalent paraphrases moved observed first-round cooperation from 0/20 episodes to 20/20. A registered span ladder localized the switch, and held-out confirmation produced 37/40 cooperation decisions with the switch-bearing sentence versus 0/40 without it.

- Semantic-equivalence packet: [`docs/phase4/x1-semantic-equivalence.md`](docs/phase4/x1-semantic-equivalence.md)
- Parser audit: [`docs/phase4/x1-parser-audit.md`](docs/phase4/x1-parser-audit.md)
- X2 confirmation: [`docs/phase4/x2-confirmation-report.md`](docs/phase4/x2-confirmation-report.md)

### Phase 4: representation and incentive channels interact

Semantic labels could override payoff dominance in direct conflict, while payoff changes moved behavior when labels did not oppose them. Continuation-probability assays were corner-confounded at the tested surfaces. Adversary behavior was opponent-contingent, and the cross-vendor lane was demoted to descriptive status after sentinel-detected endpoint instability.

- Freeze packet: [`docs/phase4/freeze-packet.md`](docs/phase4/freeze-packet.md)
- Predicates: [`docs/phase4/predicates.md`](docs/phase4/predicates.md)
- Final report: [`docs/phase4/final-report.md`](docs/phase4/final-report.md)

### Phase 5: persona conditioning and the post-adjudication correction

Sixteen sealed one-sentence personas were crossed with the existing instruments. Historical verdicts remain intact, but the completed submission analyses materially change their scientific interpretation:

| Claim | Historical mechanical result | Completed paper-facing analysis |
|---|---|---|
| P5-1a corner-mixture predicate | 3/32 restricted cells interior under seat-level CP; supported below θ=0.10 | Exact episode interval: 2/32; Dirichlet–Jeffreys sensitivity: 5/32. The binary verdict is method-sensitive; continuous composition is primary. |
| P5-1b dispersion comparison | Raw cross-persona SD 0.424–0.480 | Finite-opportunity-corrected SD 0.418–0.478; approximately 85%–96% of episode-level variation lies between prompt configurations. |
| P5-2 surface-cue dominance | Pooled persona-dominant result | Pooled exact interval remains persona-dominant, but every repeated conflict subcell is mixed; the confounded swap cell carries the pooled classification. |
| P5-3 existence predicate | Fired historically; p13 passed the frozen per-candidate slope rule | Historical gate familywise p=0.0592. Exact episode gate excludes p13; largest surviving slope +0.0833, p=0.7732. No unconfounded existence result survives. |
| P5-3 clause (b) | All personas pass a refusal threshold | All 24 evaluable lanes survive simultaneous exact episode-level family bounds; minimum lower bound 0.462. Choice result is strong, mechanism remains word/payoff-confounded. |
| P5-4 temperature | Registered refutation did not fire | Temperature/entropy observation remains secondary and mechanism-free. |

- Historical final report: [`docs/phase5/final-report.md`](docs/phase5/final-report.md)
- Historical adjudication: [`docs/phase5-close/adjudication-report.md`](docs/phase5-close/adjudication-report.md)
- Exact episode sensitivity: [`docs/analysis/submission/episode-cluster-sensitivity.md`](docs/analysis/submission/episode-cluster-sensitivity.md)
- Final p13 family audit: [`docs/analysis/submission/p13-family-audit-final.md`](docs/analysis/submission/p13-family-audit-final.md)
- Variance correction: [`docs/analysis/submission/variance-correction.md`](docs/analysis/submission/variance-correction.md)
- Clause-(b) mechanism anatomy: [`docs/analysis/post-verdict/clause-b-anatomy.md`](docs/analysis/post-verdict/clause-b-anatomy.md)

Sealed historical records are never rewritten. Living documents carry corrections beside any quoted historical interpretation.

## Research-integrity contract

The repository records:

- prompt registries and per-arm hashes;
- externally anchored preregistrations and amendments;
- every archived request, completion, seed, round, and adjudication input in an append-only event store;
- budget accounting that includes failed and retried calls;
- exact zero-call replay and metric recomputation;
- twelve registered predictions refuted by data;
- one post-adjudication inferential downgrade identified through external review;
- process failures and the rules each failure produced.

The central boundary is explicit:

> The pipeline can enforce a registered predicate exactly; it cannot guarantee that the predicate represents a valid estimand, test family, or construct.

See [`docs/instance-ledger.md`](docs/instance-ledger.md), [`docs/analysis/claims-ledger.md`](docs/analysis/claims-ledger.md), and [`docs/analysis/dead-predictions-final.md`](docs/analysis/dead-predictions-final.md).

## Counts and scopes

Counts are reconciled in [`docs/analysis/submission/count-reconciliation.md`](docs/analysis/submission/count-reconciliation.md). They are not interchangeable subjects:

- **5,505 archived completed runs** across the full store;
- **4,576 Phase 4–5 replay-contract runs**;
- **54,276 round events**;
- **108,552 seat-round decisions**;
- **36,251 archived provider-request events** across the full store;
- **30,530 Phase 4–5 calls** in the transactional budget ledger;
- **13,141,675 input tokens** and **45,247 output tokens** in that ledger.

## Reproducing the submission analyses

The post-adjudication analyses make no provider calls and run against the archived databases:

```bash
mkdir -p artifacts/api-server/engine/data
xz -dkc capsule/data/engine.db.xz > artifacts/api-server/engine/data/engine.db
xz -dkc capsule/data/budget.db.xz > artifacts/api-server/engine/data/budget.db
python -m pip install numpy scipy
python artifacts/api-server/engine/submission_gate_analyses.py
python artifacts/api-server/engine/submission_gate_finalize.py
python artifacts/api-server/engine/submission_gate_exact_cluster.py
```

The same sequence is executed by [`.github/workflows/submission-gate-analyses.yml`](.github/workflows/submission-gate-analyses.yml). Generated outputs are committed under `docs/analysis/submission/`.

## Phase map

| Phase | Purpose | Registration and report |
|---|---|---|
| v1→v2 | Naive harness and mechanical re-adjudication | [`docs/POSTMORTEM.md`](docs/POSTMORTEM.md), [`docs/v1/`](docs/v1/) |
| Phase 3 | Bare configuration: cooperation, framing, RPS | [`docs/phase3-preregistration.md`](docs/phase3-preregistration.md), [`docs/phase3-report.md`](docs/phase3-report.md) |
| X1/X2 | Paraphrase fragility and switch localization | [`docs/phase4/freeze-packet.md`](docs/phase4/freeze-packet.md), [`docs/phase4/x2-confirmation-report.md`](docs/phase4/x2-confirmation-report.md) |
| Phase 4 | Representation, counterfactuals, δ assays, adversaries, sentinels | [`docs/phase4/final-report.md`](docs/phase4/final-report.md) |
| Phase 5 | Persona panel, surface conflicts, temperature, precommitted discussion | [`docs/phase5/process-packet.md`](docs/phase5/process-packet.md), [`docs/phase5/final-report.md`](docs/phase5/final-report.md) |

## Status and scope

The repository became public on 2026-07-29. The sealed experimental program is closed; no new dispatch is authorized without a new registration. Paper-facing analysis can continue without modifying sealed artifacts or historical verdicts.

## License and citation

Code is MIT-licensed under [`LICENSE`](LICENSE). Released data artifacts and generated research records are CC BY 4.0. Citation metadata are in [`CITATION.cff`](CITATION.cff). The current paper remains a working draft and should not yet be cited.
