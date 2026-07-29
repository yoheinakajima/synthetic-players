# Phase 5 final report

> **STATUS: WORKING DRAFT — PRE-PUBLICATION, NOT FOR CITATION.**

Issued 2026-07-28, at completion of the Phase 5 close-out pipeline: replay
audit → mechanical adjudication → branch selection. Every verdict below is
the sealed-predicate adjudicator's output
(`engine/phase5_closeout_adjudicate.py`), promoted to FINAL because the
replay audit is **CLEAN**: 1,712/1,712 Phase 5 runs replay byte-exact with
per-event model/temperature pin asserts (R2e/R3e), 0 mismatches, 0 invalid
trials store-wide (`docs/phase5-close/replay-audit.md`). No claim,
threshold, tier, or branch was chosen, changed, or dropped after data
became visible; the outcome-blind completions and amendments that did occur
are listed below with their registration character.

## Verdicts (registered vocabulary, verbatim from the adjudicator)

| predicate | verdict |
|---|---|
| **P5-1a** interior fraction (primary) | **SUPPORTED** — restricted fraction 3/32 = 0.09375 < θ₁ = 0.10 |
| **P5-1b** between-persona SD vs human panels | **corner-mixture-consistent** in all 4 matched rep cells (one-shots: null) |
| **P5-2** surface-cue dominance | **persona-dominant** — pooled task-consistent share 0.128, CP95 [0.104, 0.155]; registered prediction (task-dominant) **failed** |
| **P5-3** interior-persona existence | **16/16 personas pass**; registered prediction (zero of 16) **failed** |
| **P5-4** temperature refutation | **not refuted** — Newcombe one-sided LB95 −0.095 ≤ 0 |

Axes: A = supported · B = **at-least-one** · C = no → **Branch 2** (rule 1
fires; A and C never consulted). Detail: `docs/phase5-close/adjudication-report.md`.

### Margin and mechanism disclosures (registered-adjacent, not verdict-bearing)

- P5-1a passed by a single unit: one more interior persona-cell in the
  restricted set would have flipped it (4/32 = 0.125 ≥ θ₁).
- P5-3 clause (b) fired for all 16 personas because every persona
  overwhelmingly chooses the payoff-dominant option displayed under the
  word COOPERATE in the swap cell (per-persona CP LBs 0.55–0.91; the bare
  subject: 0/40). Word-choice and payoff-dominance coincide in this cell —
  the sealed predicate keys on the choice, not the mechanism. The
  coop-leaning × swap descriptive probe (D2) shows the same word-side
  choice, consistent with lexical rather than incentive operation.
- P5-3 clause (a) additionally fired for **p13** (Harper: competitive,
  patient, risk-averse, 61): both s2a δ-cells interior AND δ-slope
  one-sided 95% LB = +0.083 > 0 — the only arm in the entire program to
  pass the Family-E human-signature assay.
- P5-4 secondaries: invalid rate 0 at every T (0/1376, 0/168, 0/168);
  round-1 choice entropy **falls** with T (0.906 → 0.787 → 0.777). The
  registered flip-noise mechanism did not appear; the confirmatory verdict
  is unaffected.

## Selected discussion branch

- File: `docs/paper/discussion-branches.md`, sha256
  `1f1d7de9c54811962416a43bc5eed05de7fdd99618d39c88e5a8ec2cde9f0356` —
  **byte-identical to the sealed sha** (seal-record.md; sealed 2026-07-28
  UTC, seal-commit timestamp authoritative; external anchor
  `docs/phase5-close/SHA256SUMS.txt.ots`).
- Selected: **Branch 2 — an interior persona exists**, with the P5-2
  variant paragraph **(not task-dominant)**. Combination-table row:
  `| supported | at-least-one | no | Branch 2 |`.

Selected branch text, quoted verbatim from the sealed file:

> The headline of Phase 5 is an existence result the program registered
> against itself: at least one persona in the sealed sixteen passed the
> two-sided assay gate and showed the registered signature of incentive
> sensitivity. The author's registered prediction — that none would — is
> refuted, and the refutation is the finding. Human-likeness, absent in the
> bare subject throughout Phases 3 and 4, can be relocated into the
> conditioning layer: some region of persona space induces interior
> behavior with a positive discount-factor slope (or registered-rate
> refusal of the dominated mislabeled option), where the bare subject shows
> corners and surface-cue tracking.
>
> Which persona(s) passed, and their registered trait factors, are reported
> in the results section exactly as adjudicated; nothing in this
> pre-committed text depends on which cell cleared the gate. What the
> existence result changes is the interpretation of the program's earlier
> phases: the corner behavior of Phases 3–4 characterizes the bare subject,
> not the model's capability envelope. The capability was recoverable by
> content-side conditioning that contains no game-relevant instruction —
> trait words only, under the sealed banned-content guard.
>
> *P5-2 variant (not task-dominant):* Consistent with the existence result,
> the dominance hierarchy did not resolve for the task side: persona
> framing contested or beat the task-text switches in registered conflict
> cells. The two results together indicate that the system-prompt layer is
> not inert decoration but a genuine second channel of behavioral control.
>
> The scope of the claim is deliberately narrow. One (or few) passing
> persona(s) out of sixteen is not a human-like population; the population
> predicates (P5-1) are reported alongside, and the between-persona
> variance comparison against the cited human panels bounds how much of the
> interior the pool actually covers. Whether the passing region of persona
> space is stable, extensible, or mechanistically interpretable is future
> work — and under the sealed scope rule, it stays there: no new arms were
> added, and the program ends with paper one.

Interpretation caution carried into the paper: the P5-3 result is 15/16 via
the swap-refusal clause where word and payoff coincide, plus one persona
(p13) via the δ-slope clause. The branch text's "incentive sensitivity"
reading rests firmly only on p13; the mechanism disclosure above must
accompany any use of the 16/16 figure.

## Non-observations and per-window disclosures

- **0 invalid trials** in all 1,712 Phase 5 runs; the registered exclusion
  rule had nothing to exclude (invalid-incl/excl tabulations are identical).
- No provider-failure partials in Phase 5 (Phase 4 had 24; Phase 5: none).
- Bare-lattice gap disclosed: rep-d90-s2p, rep-d10-s2a, rep-d10-s2p have no
  exact-template bare run at T=0.7 anywhere in the record; under
  outcome-blind completion D1 they were dropped from restricted-set
  candidacy and appear in registered secondaries flagged accordingly. The
  corner map marks their bare lanes as not run.
- P5-4 clause 2 (δ-slope appearing at high T) is non-estimable by the
  registered aliasing disclosure (T never crossed with δ=0.10); disclosed,
  not adjudicated.
- Tier C (gemini, 8 personas × 3 cells) is descriptive-only as registered;
  per-cell gates in `adjudication-report.json:tierCDescriptive`.

## Amendments and outcome-blind completions (root causes recorded)

1. **Amendment 1 (pre-data): budget cap correction** — sealed call table
   priced rep-PD from Phase 4 per-episode averages instead of the
   deterministic seeded horizons; caps raised 8,984 → 11,185 before any
   Phase 5 dispatch (`docs/phase5/amendment-1-caps.md`).
2. **Outcome-blind completions D1–D3** (`adjudication-decisions.json`),
   operator-signed against the bare-gate table only: D1 exact-twin-only
   restricted set; D2 role-level conflict coding, defect-leaning × swap
   only, coop-leaning × swap demoted to descriptive probe; D3 Axis A =
   P5-1a alone. Root cause in each case: the freeze packet under-specified
   a bit the linter did not check. Linter follow-ups recorded: conflict-cell
   coding must be pinned at freeze wherever word and role dissociate;
   branch axes must enumerate their bearing predicates explicitly.

## Operational freeze/unfreeze ledger (never scientific)

Five operational freezes, all cleared with recorded authority
(`phase5-driver-state.json:manualUnfreezes`): (1) preflight budget bind →
resolved by Amendment 1; (2) dirty worktree from the driver's own workflow
registration; (3)–(5) HEAD-moved-since-preflight trips caused by
documentation/memory commits during the run (root cause: committing during
runs trips the registered HEAD gate; lesson recorded). **Zero scientific
freezes, zero refusals, zero invalid trials.**

## Sentinel record

All 10 scheduled sentinel checks (0–9) attested POSITIVE, evaluator exit 0,
S1–S5 all green at every checkpoint (driver state `sentinelAttestations`;
per-check records in the event store). Both models' fingerprint lanes and
the bare lanes stayed in band throughout — no counterpart to the Phase 4
v2a × gemini instability appeared.

## Budget actuals (ledger, from the event store)

| group | actual calls | cap (amended) |
|---|---|---|
| P5-A | 5,168 | 5,556 |
| P5-B | 3,374 | 3,627 |
| P5-C | 1,438 | 1,546 |
| overhead (entry battery + sentinels) | 448 | 456 |
| **total** | **10,428** | **11,185** (operator standing cap 15,000) |

Exact seeded-need projections from Amendment 1 matched actuals to the call
(5,168 / 3,374 / 1,438).

## Record

- Adjudication: `docs/phase5-close/adjudication-report.{json,md}`
- Decisions ledger: `docs/phase5-close/adjudication-decisions.json`
- Branch selection: `docs/phase5-close/branch-selection.md`
- Replay audit: `docs/phase5-close/replay-audit.{json,md}`
- Seal + anchor: `docs/phase5/seal-record.md`,
  `docs/phase5-close/SHA256SUMS.txt{,.ots}`
