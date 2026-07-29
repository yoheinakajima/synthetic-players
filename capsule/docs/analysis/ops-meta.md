# Ops meta — how the honest-science machinery performed

> **STATUS: WORKING DRAFT — PRE-PUBLICATION, NOT FOR CITATION.**
> EXPLORATORY (close-out §3). Sources: driver states, amendment records,
> `docs/phase5-close/adjudication-decisions.json`, freeze ledgers.

## Budget discipline

Phase 5: 10,428 calls against an 11,185 amended cap (93.2% utilization;
per-group 93.0% / 93.0% / 93.0% / 98.2%). Amendment 1's seeded-need
projections matched actuals **to the call** in all three blocks — horizon
spend is a pure function of sealed seeds, so budget error is a pricing
error, never a run-time surprise. Root cause of the original mispricing:
the sealed call table priced from Phase 4 ledger averages instead of
evaluating the deterministic seed lanes; recorded pre-data, caps amended
before dispatch.

## Freeze/unfreeze ledger

Phase 5: five freezes, all operational, zero scientific: (1) budget
preflight bind (resolved by Amendment 1); (2) worktree dirtied by the
driver's own workflow registration; (3–5) HEAD-gate trips from
docs/memory commits landing mid-run. Lesson already in the memory file: do
not commit during runs. The HEAD gate worked exactly as designed — every
trip was a true positive for "the tree changed under a running plan," and
every clearance carries recorded authority.

## Underspecification ledger (freeze-linter escapes)

Four outcome-blind completions were needed at adjudication time (D1–D3
this close-out, plus the Phase 4 E-selection registration-gap precedent).
Pattern: what escapes the linter is never a threshold or a constant — it
is *mapping* text (which recorded data anchors a gate; which direction is
"task-consistent" when word and role dissociate; which predicate bears on
a branch axis). Registered linter follow-ups: conflict-cell coding pinned
at freeze wherever word/role dissociate; branch axes must enumerate their
bearing predicates. Both are checkable at seal time with no data.

## Adjudication integrity

Every confirmatory verdict in Phases 4 and 5 was produced by code with
selftest fixtures, from replay-verified stores, under sealed predicates —
the author's two Phase 5 predictions failed and were published as failed,
which is the system working. Completion-amendment discipline held: all
four completions were signed against outcome-blind material only, and each
records its rationale verbatim in the decisions ledger.

## Cost of honesty (descriptive)

Overhead spend (sentinels + entry batteries) was 4.3% of Phase 5 calls.
The replay audits, seal machinery, and linter cost zero API calls. The
total price of the integrity layer is a rounding error against the runs it
certifies.
