# Round 5 validation record — v7 reviewer package

> **STATUS: VALIDATED REVIEW PACKAGE, 2026-07-30.** This record documents the tests applied after integrating all thirteen Explore Science minor issues. It is a living review artifact, not sealed experimental evidence, and it changes no historical mechanical verdict. Source review: [`round-5-explore-science-review.md`](round-5-explore-science-review.md).

## Scope

Validated branch: `agent/round4-review-pdf-v6`  
Pull request: #3  
Current manuscript: `docs/paper/paper-draft.md` (v7)  
Formatted review copy: `docs/paper/synthetic-players-review-draft-v7.pdf`

## Issue coverage

All thirteen Explore Science issues have a recorded disposition in `round-5-disposition-matrix.md`:

- A1–A2;
- B1–B9;
- C1–C2.

The three online-only issues—B8, B9, and C2—are included.

## Zero-call analytical verification

### Dynamic gate reapplication — B1

- The complete condition-level interiority gate is dynamically reapplied to every candidate inside every permutation.
- Lookup tables were checked against direct gate calculations over every possible observed composition: 56 cases, 0 failures.
- At 200,000 permutations, the implementation performs 25,600,000 condition-gate lookup applications across 32 candidates, two conditions, and two constructions.
- A 5,000-draw regression against an intentionally incorrect static observed-data mask differed in 718 draws (14.36%), proving the implementation is not silently equivalent to static masking.

### Exact-gate attainability and power — B3

- With six episodes per condition, the conservative exact gate admits sample means only from 0.333 to 0.667.
- The maximum slope between two eligible cells is 0.333.
- Under the archived 32-candidate null structure, the estimated familywise tail probability at that maximum is 0.075040 (15,007/200,000 permutations; fixed seed 20260792).
- Therefore the archived exact-gate family cannot reach a conventional 0.05 familywise rejection at n=6.
- Scientific status: p13 was not prospectively family-confirmed by the frozen rule and is not decisively disconfirmed by the underpowered conservative post-adjudication procedure; it remains a replication target.
- Prospective, explicitly model-dependent planning simulations are published under `docs/analysis/submission/round5/figure-sources/prospective-power.csv`.

### Percentile-bootstrap rationale — B5

The v7 paper and generated audit documents no longer claim that exact-corner bootstrap degeneracy can create a false-positive interiority classification. The exact projection is described as the conservative finite-sample coverage reference; the percentile bootstrap is retained as a small-sample post-adjudication sensitivity without a comparable coverage guarantee at n=6.

### Completion provenance — A2

The audit found that Phase 4–5 records contain:

- complete rendered system and user messages for 30,421/30,421 request events;
- bundle SHA-256 and deterministic request-body SHA-256 fields;
- engine commit and provider route;
- raw completion text and provider response IDs for 30,397/30,397 response events.

The live adapter asserted that the deterministic request-body hash of the sent fields matched the recorded mirror. Individual raw completion payloads were not separately hash-chained or provider-attested at receipt, and the complete provider JSON object was not retained. `capsule/SHA256SUMS.capsule` covers `data/engine.db.xz`, so the released snapshot is tamper-evident relative to publication; replay does not prove that no edit occurred between receipt and snapshot sealing.

## Manuscript and figure verification

The v7 manuscript now includes:

- a five-stage architecture table;
- an inline protocol glossary;
- an operational definition of the X2 span ladder and held-out confirmation;
- a Gemini descriptive-results pointer;
- probability-theory grounding for Proposition B;
- format/content-confound language for the persona-prefix contrast;
- represented-treatment language for continuation probability;
- corrected p13 power and status language.

Figures were checked against source data:

- Figure 1 uses diamonds for fixed-panel aggregate estimates and retains non-degenerate intervals at observed boundaries;
- Figure 5 identifies p13 as ineligible under the conservative exact gate and attributes `p=0.773206` to p05/s2a, the largest eligible candidate.

## Automated validation

GitHub Actions completed successfully after the final polish:

1. regenerated all zero-call analyses from the archived databases;
2. regenerated all figures and machine-readable summaries;
3. built the line-numbered v7 PDF;
4. passed PDF text/page preflight;
5. passed assertion, relative-link, and sealed-boundary lint;
6. replayed all 4,576 Phase 4–5 runs byte-exact with zero credentials and zero live provider calls;
7. uploaded the complete v7 review package.

## PDF preflight and visual inspection

- Format: PDF 1.5, letter size, 19 pages, unencrypted, text-native.
- SHA-256: `48390128ec92cf92b59dce48e91e969a10ff7869f40a28efd03a1f3eee8ffeb9`.
- Rendered all 19 pages at 150 dpi and inspected the complete contact sheet plus the phase table, all five figures, correction table, limitations/provenance section, prospective-replication section, and correction ledger at full-page resolution.
- No clipped text, overlapping blocks, broken glyphs, malformed tables, or unreadable figures were observed.

## Evidence boundary

No sealed registration, frozen predicate, historical adjudication, precommitted discussion branch, raw event data, or historical verdict was edited. The Round 5 work consists of zero-call post-adjudication analysis, living-manuscript correction, reviewer-facing documentation, and generated figures/PDF.

## Remaining work

No known analytical or reporting blocker remains for another scientific review round. Remaining tasks are venue-facing:

- final target-venue selection and formatting;
- venue-specific AI-assistance disclosure;
- optional independent re-review of the v7 response package;
- future prospectively registered controls and replication described in the manuscript.
