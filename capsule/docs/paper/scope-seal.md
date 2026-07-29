# Paper one — scope seal

> **STATUS: PROPOSED — UNSEALED.** Seals (hash-anchored with registry v4)
> before any Phase 5 dispatch.

**Phase 5 is the final experiment for paper one.** This is sealed as a
stopping rule, not a preference:

1. **No new arms.** After registry v4 seals, no arm, cell, persona, template,
   temperature, subject model, or predicate is added to paper one for any
   reason — including "one quick check" of something Phase 5 surfaces. The
   registry is append-only up to the seal and immutable after it.
2. **No Phase 6 before publication.** Whatever Phase 5 surfaces beyond its
   registered predicates — suggestive patterns, unexplained cells, promising
   persona regions, temperature anomalies — is routed to **future work**: it
   may be described in the paper's future-work section, but it may not be
   measured, probed, replicated, or "confirmed" under paper one's registrations.
3. **The discussion is already written.** The published discussion/conclusion
   must be byte-diffable against the pre-committed branch in
   [`discussion-branches.md`](discussion-branches.md) selected by the
   registered verdicts. Deviations are seal violations, disclosed as such.
4. **Exit condition.** Paper one closes when: Phase 5 verdicts are issued by
   the registered adjudicators, the replay audit passes, the selected branch
   is spliced verbatim, and the final record is anchored (tag + release +
   OTS) like `phase4-final`.

Routing rule for future work: anything not decidable by a predicate sealed
in registry v4 is out of scope by construction. The list of such items is
kept in the paper's future-work section with pointers to the record, so the
boundary is auditable.
