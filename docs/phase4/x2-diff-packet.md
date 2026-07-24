# X2 Diff Packet (freeze packet §D) — span decomposition, ladders, selection & confirmation

## Mechanical decomposition (sealed)

`pd-repeated-v1` → `pd-repeated-v2a` decomposes into **k = 6 rendered spans** plus one
inert span; the decomposition is *proven mechanical* by construction:
`scripts/build-registry-v3.mjs` assembles every rung from the span table and **asserts
byte-exact equality** of `assemble(∅)` with the sealed v1 bundle and `assemble(all)`
with the sealed v2a bundle on every build. Span texts are quoted in
[`x1-prompt-disclosure.md`](x1-prompt-disclosure.md) §2; template shas per rung are in
[`registry-v3-manifest.md`](registry-v3-manifest.md).

| Span | Content | Grammaticality of intermediates |
|---|---|---|
| S1 | system message | whole-message replacement — grammatical by construction |
| S2 | continuation sentence (wording **and** position, one atomic op) | whole-sentence move/replace |
| S3 | choice-instruction sentence | whole-sentence replace |
| S4 | payoff block (intro + 4 lines) | whole-block replace |
| S5 | history presentation (only the first-round sentence renders in round 1; header/line changes ride along, disclosed) | whole-field replaces |
| S6 | final choice line | whole-line replace |
| S7 | retrySuffix — **registered inert**: zero retries occurred in any Phase 3/X1 arm (parser audit); if a retry ever fires in X2 this is disclosed and the rung's episodes flagged | n/a (never rendered) |

Every intermediate rung mixes complete sentences/blocks from two professionally
grammatical bundles; the only register mixing ("participant" vs "person" across spans)
is disclosed as intentional — spans are atomic units, not style harmonization.

## Ladders (sealed rung templates, registry v3)

Forward F_i = spans 1..i at v2a (F0 ≡ v1, F6 ≡ v2a; F1–F5 new: `pd-x2-f1..f5`).
Reverse R_i = spans 1..i reverted to v1 from v2a (R1–R5: `pd-x2-r1..r5`). 10 new rungs
= 2(k−1). Screening: 10 episodes/rung, δ=.90, X1 environment seeds 1–10 with matched
horizon draws (registered subset: first 10 of the X1 list), GPT-4.1 only,
**exploratory** — no confirmatory claim attaches to screening data.

## Selection rule (frozen) and confirmation

Adjacent gaps along each ladder on episode-level round-1 cooperation; **candidate iff
max |Δ| ≥ 0.50**; select largest |Δ|, ties → lowest span index, forward ladder first;
selection written to the event store before confirmation. Confirmation: exact minimal
pair around the selected span, 20 fresh-seed episodes per side (seeds **2953–2972**
per `arms.json`, allocated to no other block), predicate **P4-X2-1**
(`predicates.md`): one-sided 95% lower
bound of the screened-direction gap > 0.50 with sign match. No candidate → registered
"distributed effect" outcome; confirmation budget unspent.

## Calls

Screening ≈ 10 rungs × 10 eps × 15.9 calls/ep ≈ **1,590**; confirmation ≤ 2 × 20 ×
15.9 ≈ **636**; total ≤ **2,226** (within the 2,700 X2 cap). Formula-check: 318(k−1) +
636 = 2,226 at k=6. ✓
