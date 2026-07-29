# Round 5 response plan — Explore Science review

> **STATUS: PROPOSED RESPONSE PLAN, 2026-07-29.** This plan governs revisions to the living manuscript and post-adjudication analyses. It does not reopen the sealed experimental program, authorize new model calls, or modify historical mechanical verdicts.

## Response principles

1. **Correct rather than defend imprecise language.** Several critiques identify real overstatement or missing explanation; adopt them directly.
2. **Separate invalid original confirmation from post hoc disconfirmation.** The original p13 rule lacked family/dependence control. The current archive also lacks enough information to provide a powerful conservative rejection. Both facts can be true.
3. **Keep all computed variants visible.** No result is removed because it is favorable or unfavorable.
4. **Do not manufacture controls after the scope seal.** Missing format controls and numeric/semantic de-confounding become explicit limitations and prospective designs.
5. **Make the paper self-contained.** A diligent reader should understand phase chronology, protocol IDs, gates, and the X2 localization procedure without opening the repository.

## Priority 0 — complete the review record

- [x] Archive a faithful Round 5 synthesis and the source PDF hash.
- [ ] Obtain the three online-only Explore Science issues omitted from the standard PDF.
- [ ] Append those issues and dispositions to the Round 5 review record.
- [ ] Add Round 5 to `docs/reviews/README.md` and the canonical reviewer entry point.

## Priority 1 — analytical corrections before v7

### 1. Dynamic permutation gate documentation — B1

**Current evidence:** `submission_gate_exact_cluster.py` dynamically recomputes the gate for each candidate inside every permutation. It precomputes the gate decision for every possible episode-count triple and then applies the appropriate lookup to both permuted conditions on every iteration.

**Actions**

- [ ] Add one explicit sentence in §4.4: both condition gates are reapplied for every candidate within each of the 200,000 permutations; no observed-data candidate mask is reused.
- [ ] State the implementation: lookup tables cover every possible `(count_0, count_0.5, count_1)` composition; the Monte Carlo loop performs approximately `32 × 200,000 × 2 conditions × 2 gate constructions = 25.6 million` gate lookups, after finite precomputation of exact bounds.
- [ ] Add a unit/regression test that contrasts dynamic filtering against a deliberately static mask on a small fixture.
- [ ] Link the exact code lines and generated JSON from the family-audit methods note.

**Expected disposition:** resolved by documentation and test; no new statistical result.

### 2. Exact-gate attainability and power audit — B3

**Problem:** The manuscript currently gives the conservative exact gate a quasi-disconfirmatory role even though six episodes per condition produce very coarse, highly conservative intervals.

**Actions**

- [ ] Add a zero-call script, e.g. `scripts/audit_exact_gate_power.py`, that:
  - enumerates every possible three-valued episode-outcome composition at `n=6`;
  - reports all gate-passing means and the maximum possible gate-passing slope;
  - verifies whether any outcome configuration can produce familywise rejection under the archived 32-candidate permutation structure;
  - simulates power for prospective designs over `n ∈ {6, 12, 20, 40, 80, 160}` and family sizes `m ∈ {1, 4, 16, 32}` under declared response surfaces;
  - writes machine-readable JSON/CSV and a short methods note.
- [ ] Replace “does not survive dependence-aware inference” with:

  > The frozen rule did not prospectively establish p13 after valid family and dependence control. The conservative post-adjudication gate is too underpowered at the archived sample size to confirm or refute a persona-level response; p13 remains a replication target.

- [ ] Distinguish three claims:
  1. the historical mechanical verdict fired;
  2. prospective family-controlled confirmation was absent;
  3. the current archive is not powerful enough for a decisive conservative re-test.
- [ ] Link the prospective Phase 6 sizing section directly from §4.4.

**Expected disposition:** substantial interpretive correction; core paper claim unaffected.

### 3. Bootstrap rationale correction — B5

**Problem:** The current text incorrectly implies that an exact-corner percentile interval can falsely pass the `(0.05,0.95)` interiority gate.

**Actions**

- [ ] Remove that claim from the manuscript, audit report, generated figure caption, summary JSON status text, and any scripts that regenerate it.
- [ ] Use the technically defensible rationale:

  > The exact projection is the conservative reference sensitivity because it has finite-sample coverage guarantees for the episode-level mean. The percentile cluster bootstrap is retained as a post hoc sensitivity but, at `n=6` with a discrete outcome and boundary mass, has no comparable coverage guarantee and can understate uncertainty.

- [ ] Continue to report the bootstrap `p=0.043455` symmetrically.
- [ ] Consider dropping the labels “primary” and “non-primary” in favor of “conservative exact sensitivity” and “percentile-bootstrap sensitivity,” since neither was registered at the original freeze. The paper may state which is used for conservative interpretation without implying prospective selection.

**Expected disposition:** accept and correct; no numerical recomputation necessarily required unless the new power audit changes labels.

## Priority 2 — construct and provenance boundaries

### 4. Persona-prefix format confound — B2

**Actions**

- [ ] Replace “personas add separable presence and direction effects” with:

  > Adding any registered persona-format prefix reverses the bare swap-cell choice, while differences among persona prompts covary with the registered leaning classification.

- [ ] State that the bare-versus-prefix contrast bundles semantic identity content, prompt length, position, and token-sequence disruption.
- [ ] Clarify that the leaning-group contrast is format-matched at the template level but still aliases names, ages, occupations, and trait words.
- [ ] Add a limitation and a Phase 6 control: a length-, position-, punctuation-, and register-matched non-semantic filler prefix plus multiple neutral-prefix variants.

**Expected disposition:** qualify the construct; do not add a post-seal cell.

### 5. Continuation treatment mixes incentive and representation — B7

**Actions**

- [ ] Prefer “continuation-probability treatment” or “continuation treatment under a specified wording” over unqualified “economic lever” or “incentive response.”
- [ ] State that changing `10%` to `90%` changes the environment's continuation process and the text used to disclose it; round-one behavior responds to the complete represented treatment.
- [ ] Interpret `+0.083/+0.078` as undecomposed treatment contrasts, not pure payoff/incentive sensitivity.
- [ ] Add a prospective factorial crossing continuation probability with alternative parameter-only and semantic wordings.

**Expected disposition:** terminology and construct-validity correction; core point estimates unchanged.

### 6. Raw completion tamper-evidence boundary — A2

**Actions**

- [ ] Audit the event schema and release manifests for:
  - provider response IDs;
  - raw provider JSON retention;
  - per-event or per-payload SHA-256 fields;
  - database/capsule snapshot hashes;
  - timing of OpenTimestamps anchors.
- [ ] Write a provenance matrix distinguishing:
  1. registration/freeze chronology;
  2. event-store replayability;
  3. batch archive integrity after a sealed release;
  4. receipt-time payload hashing;
  5. provider-side attestation/TLS provenance.
- [ ] If payloads were not hashed at receipt, say so plainly. Do not imply that byte-exact replay authenticates the provider's original response.
- [ ] Add receipt-time hash chaining and provider response-ID capture as a future protocol requirement.

**Expected disposition:** evidence audit followed by precise narrowing or documentation of existing hashes.

## Priority 3 — self-contained reporting

### 7. Phase architecture table — A1

Add a compact table in §3 with columns:

| stage | primary question | configuration/unit | registration status | role in paper |
|---|---|---|---|---|
| v1/v2 instrument development | Can claims be mechanically replayed/adjudicated? | archived run corpus | historical/postmortem | motivates pipeline |
| Phase 3 | How does the bare configuration behave in PD, framing, and RPS? | bare GPT-4.1 episodes | prospectively registered claims | baseline behavior |
| X1/X2 extensions | Is the Phase 3 corner representation-dependent, and where is the switch? | formally equivalent wording variants; held-out minimal pair | result-informed but registered before extension data | representation mechanism |
| Phase 4 | How do wording, labels, payoffs, opponents, and provider routes interact? | bare configurations and adversaries | frozen before block data | robustness map |
| Phase 5 | What does lightweight persona conditioning change? | fixed 16-prompt persona panel | confirmatory predicates registered before adjudicating data | main composition analysis |

Audit the program's own phase naming before finalizing the labels so that “five-phase” matches the repository chronology exactly.

### 8. Protocol glossary — B4

Define at first use and collect in a compact box/table:

- `S2-absent`: original repeated-game wording without the switch-bearing continuation sentence;
- `S2-present`: wording with that sentence;
- `P5-1a`: restricted boundary/interiority census;
- `P5-1b`: dispersion criterion;
- `P5-2`: task-text versus persona-consistent choice coding in conflict cells;
- `P5-3(a)`: gated persona-level continuation-treatment slope existence clause;
- `P5-3(b)`: swap-cell refusal/choice threshold clause;
- historical verdict versus post-adjudication sensitivity.

### 9. Span ladder definition — B6

Add a self-contained description in §4.3:

- mechanical six-span decomposition of v1 and v2a;
- complete sentence/block replacements, not arbitrary token deletion;
- forward and reverse ladders, ten new rungs;
- exploratory screening with ten episodes per rung;
- frozen adjacent-gap threshold `|Δ| ≥ 0.50` and deterministic tie-break;
- selected S2 minimal pair;
- 20 fresh episodes per side, seeds 2953–2972, GPT-4.1 at temperature 0.7;
- held-out result 0/40 versus 37/40 decisions.

Avoid claiming that this rules out all positional/context interactions; it identifies the switch-bearing registered span under the tested ladder.

## Priority 4 — figure and machine-readable corrections

### 10. Figure 5 attribution — C1

- [ ] Retitle the figure **Post-adjudication family-audit constructions**.
- [ ] Historical and percentile bars: label `p13/s2a`, observed max slope `+0.4167`.
- [ ] Exact bar: show `p13 excluded by interiority gate`; separately label the maximum eligible candidate `p05/s2a`, slope `+0.0833`, familywise `p=0.773206`.
- [ ] Update the caption so no visual element attributes `p=0.773206` to p13.
- [ ] Add a “candidate” field to the figure-source CSV/JSON if not already present.

## Priority 5 — v7 package and response matrix

- [ ] Create a point-by-point response table with columns: reviewer issue, agree/disagree, evidence, manuscript change, analysis change, future-work change.
- [ ] Regenerate Markdown, figures, machine-readable summary, and line-numbered PDF as v7.
- [ ] Run paper lint, link checks, sealed-boundary check, zero-call analyses, and full capsule replay.
- [ ] Ask one independent reviewer to verify the B1 dynamic-gate statement, B3 power audit, B5 corrected rationale, and C1 figure attribution specifically.

## Proposed claim language after Round 5

### Core result

> In this fixed sixteen-prompt panel, broad marginal criteria coexist with corrected estimates assigning most episode-level variation to differences among prompt configurations. The observed continuation-treatment point contrasts are small on the unit scale but too imprecise to establish equivalence, a null response, or a narrow upper bound.

### p13

> p13 passed the frozen per-candidate rule, but that rule lacked prospective family and dependence control. Post-adjudication procedures yield materially different answers, and the conservative exact procedure is underpowered at the archived sample size. The record therefore supplies neither prospectively controlled confirmation nor decisive disconfirmation; p13 is a replication target.

### Persona-prefix effect

> Adding a persona-format prefix reverses the bare swap-cell choice, but the contrast is not semantically isolated from length, position, and token-sequence changes. Differences among persona prompts remain substantial under a common template.

### Continuation treatment

> The registered contrast is a response to a represented continuation-probability treatment, combining the formal environment parameter with the wording used to communicate it.

## Scope and sequencing

### Can be completed now with zero model calls

- A1, A2 evidence audit, B1, B3 enumeration/simulation, B4, B5, B6, B7, C1;
- review archive and response matrix;
- v7 PDF and reproducibility checks.

### Requires a new prospectively registered phase

- format-matched filler persona-prefix control;
- numeric continuation probability × wording factorial;
- p13 or small-family replication with adequate episode-level power;
- receipt-time payload hash chain if added prospectively to new provider calls.

## Release gate

Do not merge the Round 5 response until:

1. all ten detailed issues have a documented disposition;
2. the three online-only issues have been obtained or explicitly marked unavailable;
3. the exact-gate power audit is reproducible;
4. the bootstrap rationale and p13 language are corrected consistently across paper, figures, review docs, and generated summaries;
5. Figure 5 no longer attributes the exact-gate result to p13;
6. the full v7 build and capsule replay pass.
