# Registered shedding order for a global-cap bind (pre-F, 2026-07-25)

Worst-case global projection after A-OVH-2 is ≈ 20,812 of 21,000 — ~200 calls
of headroom. This file registers, **before any F dispatch**, the order in which
F arms are shed if the global cap binds, so a bind never becomes a
discretionary mid-data call. The order is fixed now; applying it later is
mechanical.

## Trigger (mechanical, no judgment at apply time)

- At F preflight: if `spent + remaining_need(F) > 21,000` (remaining need
  computed per episode from the sealed schedule and horizon rule, exactly as
  the driver prices it), shed arms in the order below — whole arms only,
  never partial — until the projection clears.
- At a mid-block bind (engine refusal on the group or global cap): the driver
  freezes as designed; the resume plan applies the next shed in this order.
  No other mid-block response is permitted.
- Every shed is disclosed in provenance-notes.md at apply time, with the
  projection arithmetic that triggered it. Shed arms are reported as
  "not run — registered shed order," never as missing data.

## Order

1. **SHED-1 — `p4-f-ngram3-gpt`** (~1,000 calls relief: 20 eps × 50 rounds ×
   1 subject call). Directed by the operator per the sign-off's least-loaded
   judgment: the order-3 tracker is the most redundant probe — the order-2
   tracker (`ngram2`) covers the tracker family at lower order for both
   models, so third-order structure is the least-loaded increment.
2. **SHED-2 (proposed) — `p4-f-shuffled-history-cvx`** (~1,000 calls relief).
   Rationale, in priority order: (a) controls shed before treatment probes —
   shuffled-history destroys temporal contingency as a control for history
   dependence, and its gpt twin continues to carry that control for the
   primary subject; (b) the secondary model (cvx) sheds before the primary
   (gpt) everywhere — cvx is the comparator, and every cvx arm retains a gpt
   sibling; (c) treatment probes (`fo-tracker`, `switcher-r26`,
   `wsls-targeter`, `ngram2`) stay intact for both models at depth 2.
3. Should depth 3 ever be needed (it is not projected), the same two
   invariants extend the order: remaining cvx control/probe arms before any
   gpt arm; primary-model treatment arms shed last, and only with a new
   operator decision.

Depth 1 alone (~1,000 calls) more than covers the projected worst-case
overage (~0; headroom ~200); depth 2 is insurance against projection error of
the kind corrected in A-OVH-2.

SHED-1 is operator-directed. SHED-2/3 are proposed here and stand unless the
operator amends them before F preflight.
