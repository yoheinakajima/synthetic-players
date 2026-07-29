> **Instance ledger: every process deviation/underspecification across the program [CONFIRMATORY] (source: maintained per process packet)**

# Instance ledger: the process-failure record

This document consolidates every disclosed process failure, registration gap,
and checker gap across the project — from the first v1 registration gap
through the Phase 4 evaluator-attestation gap. It exists because the failures,
their catch mechanisms, and the rules they produced are the project's protocol
contribution: the science results are one output; the machinery that survived
its own author is the other.

Reading order: each entry gives the cause, the mechanism that caught it, the
fix, and the durable rule it produced. Pointers go to the contemporaneous
record (the entries below summarize; the pointers are authoritative). Nothing
here was removed from history — the mistakes are part of the record and stay
in it.

## The five durable rules (produced by the instances below)

1. **Completeness linter** (Phase 5 seal gate): at freeze time, mechanically
   render every scheduled dispatch against enforcement — sealed text that
   cannot be rendered is not sealed. From instances 1–5.
2. **Attestation gating**: dispatch gates require positive evaluator
   attestation for every preceding sentinel check; absence of evaluation
   fail-closes. "No fire seen" is never "no fire". From the alert-6 lapse.
3. **Three-layer rule**: every sealed conditional rule must exist in dispatch,
   enforcement, AND the replay checker; grep all three before sealing. From
   the sentinel-switch deltaPct replay gap and the `_e_sched_seed` indexing
   gap.
4. **Signature-based non-observation**: a completed run is an observation; a
   provider-failure partial is a non-observation identified by mechanical
   store signature, never by narrative memory (the scan found 22 where the
   narrative remembered 3).
5. **Per-window indexing / store-derived identification**: adjudicators
   re-derive membership from event-store attributes (seeds, prompts, models),
   never from labels, batch names, or assumed orderings.

## The ledger

| # | Instance | Cause | Caught by | Fix | Rule produced | Record |
|---|---|---|---|---|---|---|
| 1 | v1 literature transplant | Claim 1 (TFT >50% coop) written from memory of the literature; data shows 2% | v2 mechanical re-adjudication | Structured predicates; author never adjudicates | Claims are machine-checkable predicates | `docs/POSTMORTEM.md` §E1 |
| 2 | v1 metric mismatch | Cooperation/Nash metrics applied to zero-sum games where undefined | v2 audit | Per-class metric suite; `null` where undefined | Per-class metrics; undefined ⇒ null, never 0 | `docs/POSTMORTEM.md` §E3 |
| 3 | v1 stochastic optimism | Single unseeded runs treated as facts; straddling CIs ignored | v2 audit | Seeded PRNG; 20-seed replicates; CI adjudication (3 v1 claims went inconclusive) | Stochastic ⇒ seeded replicates + CIs | `docs/POSTMORTEM.md` §E4 |
| 4 | Gate-0 Claude failure | claude-haiku-4-5 emitted CoT prose, truncating at the 16-token cap — failed clean-stop | Gate-0 evaluator (registered pre-check) | Registered amendment: cross-vendor twin became gemini-2.5-flash | Behavioral fit gate for every cross-vendor candidate | `docs/phase4/gate0-report-round1-claude-FAIL.md` |
| 5 | Anomaly-freeze persistence | Driver freezes did not persist the frozen flag to disk | Pre-dispatch audit | Freezes always persist before returning | Fail-closed state persistence | `docs/phase4/provenance-notes.md` (pre-dispatch entries) |
| 6 | At-most-once dispatch gap | Interruptions left no inflight marker for recovery reconciliation | Pre-dispatch audit | Inflight marker persisted before every POST | At-most-once dispatch guard | `docs/phase4/provenance-notes.md` |
| 7 | Reverse-ladder indexing | X2 screening reverse-span indices inverted vs the sealed definition | Pre-dispatch audit | Corrected to the sealed definition before any dispatch | Manifest-driven materialization | `docs/phase4/provenance-notes.md` |
| 8 | Requested-seed gap | Phase 4 seeds absent from `llm.requested` payloads — at-most-once recovery impossible | Pre-dispatch audit | Environment seed recorded on every request | Seed capture on request is authoritative | `docs/phase4/provenance-notes.md` |
| 9 | X1 endpoint resolution | Adjudicator resolved runs by batch labels the store does not carry | Audit | Rewritten to re-derive from store attributes alone | Store-derived identification (rule 5) | `docs/phase4/provenance-notes.md` |
| 10 | E-dselected registration gap (sealed-text instance 1) | Sealed packet omitted the D-selected template selection rule | Audit during D1 | Prospective outcome-blind completion amendment (rule INTERIOR) | Completion-amendment pattern (outcome-blind, sealed-material-only) | `docs/phase4/provenance-notes.md`, `docs/phase4/e-selection-report.md` |
| 11 | X2-confirmation schedule gap (instance 3) | Conditional confirmation block missing from the generated schedule | Driver crash (fail-closed) | Amendments-file materialization; driver checks amendments | Amendments are files, not memory | `docs/phase4/provenance-notes.md`, `execution-schedule-amendments.json` |
| 12 | Resolved-arm dispatch gap (instance 4) | Driver froze on `RESOLVED-BY-*` templates as out-of-scope | Zero-spend dry run | Substitute concrete templates from written resolutions | Resolutions are store rows, dereferenced mechanically | `docs/phase4/provenance-notes.md` |
| 13 | D3 presentation schema | Adjudicator assumed canonical label order instead of sealed `displayOrder` | Fail-closed adjudicator check | Schema-true rewrite with four stronger equality checks | Fail-closed schema verification | `docs/phase4/provenance-notes.md` |
| 14 | Sentinel drift (alert 5) | gemini v2a cell eroded 10→7 across checks | Sentinel evaluator, check 5 | Operator re-baseline at check 6; doubled cadence; window-indexing riders | Continuous behavioral fingerprinting | `docs/phase4/sentinel-alert-5-memo.md` |
| 15 | Sentinel-switch deltaPct pin (instance 5) | Sealed third-cell switch pinned no `deltaPct` for the pd-rep rendering | Zero-spend dry run | Donor deltaPct from the sentinel battery, registered before dispatch | Sealed text must render (→ completeness linter) | `docs/phase4/provenance-notes.md` |
| 16 | Budget projection error | Projection priced in design units (episodes), not ledger prices (calls) | Post-amendment audit | Correcting amendment A-OVH-2 | Projections from ledger prices only | `docs/phase4/budget-amendments.md` |
| 17 | Provider-failure partials | gemini 429/transport errors produced partial runs | Registered failure rule + mechanical scan | Signature-based non-observation; pacing + single bounded re-dispatch | Rule 4; scan is the ledger of record (22, not the narrated 3) | `docs/phase4/provenance-notes.md`, `docs/phase4/f-report.md` |
| 18 | `_e_sched_seed` indexing | Adjudicator refused valid E runs: 1-based episode vs 0-based seeds array | Fail-closed entry gate | Checker-side helper (ep−1), verified against schedule | Per-window indexing discipline (rule 5) | `docs/phase4/provenance-notes.md` |
| 19 | F capability gap (F-SPEC-1) | F scheduled against opponent strategies the engine did not implement | Pre-dispatch capability check | Completion amendment: sealed specs → implementations, fixtures became selftests verbatim | Spec-to-fixture-to-selftest chain | `docs/phase4/f-opponent-specs.md` §9.1 |
| 20 | Evaluator attestation lapse (alert 6) | Sentinel checks 9–10 dispatched but not evaluated during recovery churn; F h2 dispatched past an unevaluated fired check; console "10/10" was a dispatch count, not a rule outcome | Late evaluator run (self-audit) | Operator ruling: alerts stand; gemini F tier demoted descriptive-only; driver attestation gate; dispatch-count prints renamed | Attestation gating (rule 2) | `docs/phase4/sentinel-alert-6-memo.md` |
| 21 | Replay-checker substitution gap | Sealed switch rule existed in dispatch+enforcement but not the replay re-derivation — step-8 audit failed 80/80 post-switch fallback runs on good data | §F.3 replay audit (fail-closed) | Checker-side mirror keyed on recorded check index; fail-closed against the written resolution | Three-layer rule (rule 3) | `docs/phase4/provenance-notes.md` (step-8 entries) |
| 22 | F engine-commit set | F adjudication checked only clean/dirty, not which commits | Post-finals review round | Refuse commits outside the registered four-commit F dispatch set; set disclosed in `f-report.json` | Registry-bound engine commits | `docs/phase4/provenance-notes.md` (review-hardening entry) |

## What the trend line shows

The catch mechanism migrated over the project's life: v1 errors were caught by
a wholesale re-audit (expensive, late); mid-Phase-4 gaps were caught by
zero-spend dry runs and fail-closed adjudicator gates (cheap, before spend);
the last three were caught by the replay audit and a post-finals review round
(mechanical, after the fact, but before anything was cited). Every rule above
exists to move the catch earlier. None of the 22 instances changed a sealed
claim, threshold, or verdict after data became visible; where an instance
touched confirmatory standing at all, the resolution went the conservative
direction (alert 6: tier demotion, never rescue).
