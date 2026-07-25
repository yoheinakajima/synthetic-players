# Phase 5 process packet

Forward-looking process changes distilled from Phase 4 incidents. Items here
are commitments for the Phase 5 freeze design, not retroactive edits to any
Phase 4 sealed text.

## §1 Freeze-time completeness linter (from sealed-text underspecification instances 1–5)

**Problem.** Five times in Phase 4, sealed or registered text was
underspecified relative to what dispatch actually requires, and the gap
surfaced only at implementation or dispatch eve (provenance-notes.md,
instances 1–5; instance 5: the sentinel third-cell switch existed in neither
the engine's enforcement nor the driver's dispatch; instance-5 follow-up: the
switched cell's template requires `deltaPct`, which no sealed text pinned).
Each was caught before spend — increasingly by the same mechanism: zero-spend
dry runs validating rendered requests against enforcement.

**Commitment.** Phase 5 promotes that mechanism from dispatch-eve habit to a
**seal gate**. At freeze time, a linter mechanically:

1. Enumerates every dispatchable request implied by the sealed text — every
   battery cell, every sentinel cell **including all conditional branches**
   (switch/fallback states), and every resolution-dependent cell under *each
   possible resolution value*, not just the expected one.
2. Renders each request end-to-end (template resolution, parameter pins,
   context assembly) and validates it against engine enforcement with
   zero-spend dry runs.
3. Fails the seal on any missing parameter, unpinned value, unreachable
   branch, undefined tie-break, or engine/driver disagreement about what a
   cell means. An unresolvable-at-freeze value (e.g., data-dependent
   selection) must have a registered *resolution rule plus a registered
   default for every parameter the render path touches* — the linter
   dry-renders the cell under stand-in resolutions to prove the rule is
   executable.

**Acceptance test for the linter itself:** re-run it against the Phase 4
sealed packet as frozen; it must reproduce instances 1–5 as seal failures.

**Why a gate, not a habit.** Dry runs caught instances pre-spend only because
an operator chose to run them at the right moments. A seal that cannot be
produced while an underspecification exists removes the choice.

## §2 Projection discipline (from A-OVH-2)

Budget projections must be derived from ledger prices (calls per episode as
the event store records them), never from design-unit counts (episodes,
cells, checks). Registered in provenance-notes.md with A-OVH-2; carried here
as a freeze-checklist item: every group cap in the Phase 5 budget must cite
the ledger-price arithmetic that produced it.

*(Further items accrue here as Phase 4 closes: candidate entries include the
additive-amendment pattern for sealed-adjacent documents and the
drift-fingerprint cadence design from the sentinel battery.)*
