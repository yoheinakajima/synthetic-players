# Program claims ledger — v1 through Phase 5

> **STATUS: WORKING DRAFT — PRE-PUBLICATION, NOT FOR CITATION.**
> EXPLORATORY compilation (close-out §3). Machine-readable:
> `claims-ledger.csv`. Every verdict is quoted from its confirmatory record
> (last column of the CSV); nothing here re-adjudicates anything.

## Reading the ledger

- **Verdict vocabulary** is each phase's registered vocabulary verbatim:
  SUPPORTED / NOT SUPPORTED / REFUTED / INCONCLUSIVE / registered branch
  names (corner-confounded, only-first, payoff-dominant) / Phase 5's
  supported / persona-dominant / not refuted / pass counts.
- **Refuted vs not-supported** is load-bearing: refuted means a registered
  direction was affirmatively reversed; not-supported means non-detection.
  The reconciliation lives in `docs/dead-predictions.md` and
  `dead-predictions-final.md` (final tally: 12 refuted author predictions).

## Shape of the ledger

- **v1:** 1 refuted, 4 supported (v2-exact), 4 inconclusive under
  re-adjudication.
- **Phase 3:** 6 refuted (incl. the paraphrase corner-flip X1 that set the
  program's thesis), 3 supported.
- **Phase 4:** the thesis phase — role channel and screening span supported
  on the primary tier; presentation effects null on primary but alive on
  the cross-vendor mirror (vendor-divergent, twice with opposite signs);
  E corner-confounded (registered branch); F resolves to only-first with
  two surprises (ngram2 exploits; the subject *beats* first-order
  tracking); gemini F tier demoted descriptive-only by sentinel ruling.
- **Phase 5:** both registered author predictions with teeth failed —
  P5-2 returned the opposite verdict (persona-dominant) and P5-3 returned
  16/16 against a prediction of zero — while the population predicates
  held (P5-1a by a single unit) and temperature stayed inert (P5-4 not
  refuted). Branch 2 selected.

## Cross-phase through-line

Phases 3–4 established: corners everywhere, switched by local semantic
content (paraphrase X1 → X2 span ladder +0.925; D2 role channel; word
channel null on gpt). Phase 5 shows the corners characterize the **bare**
subject, not the model: a sealed persona layer relocates the operating
point (P5-2 persona-dominant), and one persona (p13) produces the
program's only positive δ-slope through an interior gate. The claims
ledger's arc is: every human-likeness prediction about the bare subject
died; the first human-signature detection appeared exactly one
conditioning layer up.

## Post-adjudication status changes (R2, 2026-07-29 — EXPLORATORY layer)

> The registered mechanical verdicts above are historical and unchanged.

- **First post-adjudication claim-status downgrade — externally
  identified inferential defect.** The registered P5-3 clause-(a)
  per-persona one-sided 95% slope test did not control the family error
  for the existence claim (evaluable family: 32 clause-(a) candidates;
  96 registered-eligible). Family permutation audit
  (`docs/analysis/r2/p13-family-audit.md`): p = 0.0525 ± 0.0050 (MC SE,
  B=2,000); the registered procedure's empirical family-wise false-fire
  rate under the null is 12.9%. p13's slope interpretation is
  **downgraded to suggestive**. Explicitly NOT an empirical refutation;
  the dead-predictions count stays **12**. Clause (b) survives
  Bonferroni over its full family but remains mechanism-confounded.
  New rule, linter-checked going forward (freeze_lint **C8**): every
  registered predicate must declare its family-level error control at
  freeze.
