# Synthetic Players

> **STATUS: WORKING RESEARCH RELEASE — PRE-PUBLICATION, NOT FOR CITATION.**
> The sealed experimental program is complete through Phase 5. The current paper-facing revision is [`docs/paper/paper-draft.md`](docs/paper/paper-draft.md); unresolved submission analyses are tracked in [`docs/analysis/submission-blockers.md`](docs/analysis/submission-blockers.md).

**Replay the public record in one command** — anonymous clone, zero credentials, zero live model calls:

```bash
git clone https://github.com/yoheinakajima/synthetic-players
cd synthetic-players/capsule
bash verify.sh
```

Expected result: **4,576/4,576 archived observations replay byte-exact.**

## What this project is

Synthetic Players is an open experimental laboratory for placing LLM-controlled agents into formally specified strategic games. It studies:

- how model behavior changes across wording, labels, payoff structures, opponents, personas, temperature, provider routes, and time;
- when a result belongs only to one model–prompt–deployment configuration;
- whether persona-conditioned panels preserve the response to an experimental lever, not merely broad aggregate resemblance;
- how preregistration, event sourcing, mechanical adjudication, and exact replay can make machine-speed research auditable.

The current paper’s narrow empirical claim is:

> A fixed panel of sixteen lightweight persona prompts passed preregistered **coarse marginal checks** while showing a small continuation-probability comparative static; the observed spread was carried largely by between-prompt composition of empirically corner-concentrated policies.

This is not a claim of human substitutability. Published human references are protocol-nonmatched, the primary results come from one model deployment, historical round-one intervals counted seats nested within episodes, and several zero-call submission sensitivities remain open.

## Current paper and review materials

- **Paper draft:** [`docs/paper/paper-draft.md`](docs/paper/paper-draft.md)
- **Submission gate:** [`docs/analysis/submission-blockers.md`](docs/analysis/submission-blockers.md)
- **Novelty relationships:** [`docs/analysis/novelty-relationships.md`](docs/analysis/novelty-relationships.md)
- **Literature map:** [`docs/analysis/literature-map.md`](docs/analysis/literature-map.md)
- **Identification propositions:** [`docs/analysis/propositions.md`](docs/analysis/propositions.md)
- **Sample hierarchy and estimands:** [`docs/analysis/hierarchy.md`](docs/analysis/hierarchy.md)
- **Analysis index:** [`docs/analysis/INDEX.md`](docs/analysis/INDEX.md)

## Main empirical arc

### Phase 3: corners and framing

The bare GPT-4.1 configuration defected in every recorded first round across the registered continuation-probability cells. Community-versus-Wall-Street framing moved behavior where continuation probability did not, and RPS exhibited a large role-attached rock bias.

Report: [`docs/phase3-report.md`](docs/phase3-report.md)

### X1/X2: one sentence, opposite corners

Two formally game-equivalent paraphrases moved observed first-round cooperation from 0/20 episodes to 20/20. A preregistered span ladder localized the switch and a held-out confirmation produced 37/40 cooperation decisions under the switch-bearing sentence versus 0/40 without it.

- Semantic-equivalence packet: [`docs/phase4/x1-semantic-equivalence.md`](docs/phase4/x1-semantic-equivalence.md)
- Parser audit: [`docs/phase4/x1-parser-audit.md`](docs/phase4/x1-parser-audit.md)
- X2 confirmation: [`docs/phase4/x2-confirmation-report.md`](docs/phase4/x2-confirmation-report.md)

### Phase 4: representation, incentives, and opponents

The representation battery showed that semantic cues can override payoff dominance in registered conflict cells, while payoff sensitivity remains representation-conditional rather than absent. The continuation-probability assays were corner-confounded at the tested surfaces. Adversary results were opponent-contingent, and the cross-vendor lane was demoted to descriptive status after sentinel-detected endpoint instability.

- Freeze packet: [`docs/phase4/freeze-packet.md`](docs/phase4/freeze-packet.md)
- Predicates: [`docs/phase4/predicates.md`](docs/phase4/predicates.md)
- Final report: [`docs/phase4/final-report.md`](docs/phase4/final-report.md)

### Phase 5: persona conditioning

Sixteen sealed one-sentence personas were crossed with the existing instruments. The historical adjudication reported:

| Claim | Historical mechanical result | Current paper-facing interpretation |
|---|---|---|
| P5-1a corner-mixture predicate | Supported at 3/32 = 0.094 against θ = 0.10, by one unit | Continuous census is primary; episode-clustered reclassification is a submission blocker |
| P5-1b dispersion comparison | Corner-mixture-consistent in all four registered cells | Raw observed SDs include finite-opportunity measurement noise; latent-variance equivalence is not claimed |
| P5-2 surface-cue dominance | Persona-dominant pooled result | Pooled result is carried by a word/payoff-confounded swap cell; describe as control-channel interactions |
| P5-3 existence predicate | Fired historically; clause (b) strong but mechanism-confounded; p13 also passed the per-candidate slope rule | p13 is a replication target after external review exposed missing family-level error control and a nonfinal boundary audit |
| P5-4 temperature | Registered refutation did not fire | Temperature/entropy observation is secondary and mechanism-free |

- Final report: [`docs/phase5/final-report.md`](docs/phase5/final-report.md)
- Adjudication: [`docs/phase5-close/adjudication-report.md`](docs/phase5-close/adjudication-report.md)
- p13 family audit: [`docs/analysis/r2/p13-family-audit.md`](docs/analysis/r2/p13-family-audit.md)
- Clause-(b) confound anatomy: [`docs/analysis/post-verdict/clause-b-anatomy.md`](docs/analysis/post-verdict/clause-b-anatomy.md)

Sealed historical records are never rewritten. Living paper-facing documents carry corrections beside any quoted historical interpretation.

## Research-integrity contract

The repository records:

- prompt registries and per-arm hashes;
- externally anchored preregistrations and amendments;
- every request, completion, seed, round, and adjudication input in an append-only event store;
- budget accounting that includes failed and retried calls;
- exact zero-call replay and metric recomputation;
- twelve registered predictions refuted by data;
- one post-adjudication inferential downgrade identified through external review;
- process failures and the rules each failure produced.

The central boundary is explicit:

> The pipeline can enforce a registered predicate exactly; it cannot guarantee that the predicate represents a valid estimand, test family, or construct.

See [`docs/instance-ledger.md`](docs/instance-ledger.md), [`docs/analysis/claims-ledger.md`](docs/analysis/claims-ledger.md), and [`docs/analysis/dead-predictions-final.md`](docs/analysis/dead-predictions-final.md).

## Reproducibility contract

The citable-in-principle technical claim is that the archived record can be replayed without credentials or live model access. For the non-capsule workflow:

```bash
bash scripts/restore-data.sh
cd artifacts/api-server
(uv run python engine/server.py &) && sleep 2
cd engine
uv run python phase4_step8_audit.py
```

Adjudication scripts are deterministic from the restored event store. The fresh-clone transcript is in [`docs/close-out-verification.md`](docs/close-out-verification.md), and public verification is documented in [`docs/public-verification.md`](docs/public-verification.md).

## Scale and counts

Counts use different units and scopes; do not treat them as interchangeable subjects.

- Phase 5: 1,712 valid completed episodes, two seats per episode.
- Full current store: 54,276 round events and 36,251 archived `llm.requested` events.
- Public replay contract: 4,576 archived observations.
- Phase 4 transactional ledger: 20,102 provider calls, 9,135,321 input tokens, 33,510 output tokens.

The reconciled hierarchy and open count-table requirement are documented in [`docs/analysis/hierarchy.md`](docs/analysis/hierarchy.md) and [`docs/analysis/submission-blockers.md`](docs/analysis/submission-blockers.md).

## Phase map

| Phase | Purpose | Registration and report |
|---|---|---|
| v1→v2 | Naive harness and mechanical re-adjudication | [`docs/POSTMORTEM.md`](docs/POSTMORTEM.md), [`docs/v1/`](docs/v1/) |
| Phase 3 | Bare subject: cooperation, framing, RPS | [`docs/phase3-preregistration.md`](docs/phase3-preregistration.md), [`docs/phase3-report.md`](docs/phase3-report.md) |
| X1/X2 | Paraphrase fragility and switch localization | [`docs/phase4/freeze-packet.md`](docs/phase4/freeze-packet.md), [`docs/phase4/x2-confirmation-report.md`](docs/phase4/x2-confirmation-report.md) |
| Phase 4 | Representation, counterfactuals, δ assays, adversaries, sentinels | [`docs/phase4/final-report.md`](docs/phase4/final-report.md) |
| Phase 5 | Persona panel, surface conflicts, temperature, precommitted discussion | [`docs/phase5/process-packet.md`](docs/phase5/process-packet.md), [`docs/phase5/final-report.md`](docs/phase5/final-report.md) |

## Repository layout

- `artifacts/api-server/engine/` — event-store server, dispatch drivers, adjudicators, replay and audit scripts
- `artifacts/api-server/prompts/registry.json` — sealed prompt registry
- `docs/phase3*`, `docs/phase4/`, `docs/phase5/`, `docs/phase5-close/` — registrations, reports, amendments, and close-out records
- `docs/analysis/` — exploratory analyses, paper-facing theory, novelty map, and submission gate
- `docs/paper/` — current paper draft and sealed discussion artifacts
- `capsule/` — anonymous zero-credential reproduction capsule

## Status and scope

The repository became public on 2026-07-29. The sealed experimental program is closed; no new dispatch is authorized without a new registration. Paper-facing analysis and writing can continue without changing sealed artifacts or historical verdicts.

## License and citation

Code is MIT-licensed under [`LICENSE`](LICENSE). Released data artifacts and generated research records are CC BY 4.0. Citation metadata are in [`CITATION.cff`](CITATION.cff). The current paper remains a working draft and should not yet be cited.
