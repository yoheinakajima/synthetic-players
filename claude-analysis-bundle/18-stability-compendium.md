> **Every stability/replication check across the program in one place [EXPLORATORY] (source: engine/gen_analysis_pack.py)**

# Stability compendium — sentinels, drift, and replication across phases

> **STATUS: WORKING DRAFT — PRE-PUBLICATION, NOT FOR CITATION.**
> EXPLORATORY (close-out §3). Sources: `docs/phase4/final-report.md`
> §Sentinel, `docs/phase4/f-report.json:sentinelTrajectoryV2aGemini`,
> `figure-sources/p4-sentinel-gemini-oscillation.csv`, Phase 5 driver state
> + `docs/phase5-close/adjudication-report.md`, replay audits.

## Sentinel record by phase

- **Phase 4 (gpt lanes):** 10/10 at every check throughout — no drift ever
  observed on the primary vendor.
- **Phase 4 (v2a × gemini):** the program's one instability. Trajectory
  10 → 9 → 9 → 8 → 8 → 7* → [re-baseline 10] → 6* → 7* → 6* → 7*; rule (c)
  fired repeatedly; the series never closed clean; consequence was
  registered and material — the Family-F gemini tier was demoted to
  DESCRIPTIVE-ONLY (operator ruling, 2026-07-28).
- **Phase 5 (both vendors):** all 10 checks (0–9) POSITIVE, S1–S5 green at
  every checkpoint, both persona-fingerprint and bare lanes in band. The
  gemini instability did not recur — consistent with it being v2a-template
  specific rather than vendor-global, though the Phase 5 sentinel lanes use
  different templates, so this is a change of instrument, not a resolution.

## Replay integrity (byte-exactness across the program)

- Phase 4 step-8 audit: 2,864/2,864 completed observations byte-exact;
  rng draw-count profiles match sealed adversary specs exactly.
- Phase 5 audit: 1,712/1,712 runs byte-exact with per-event
  model/temperature pin asserts; 0 mismatches.
- Combined: **4,576 replayed observations, zero mismatches, zero live
  calls** — the program's entire evidentiary base is mechanically
  reproducible from the sealed stores.

## Invalid-trial record

Phase 4: 0 invalid store-wide (24 provider-failure partials, verified
non-observations). Phase 5: 0 invalid at all three temperatures (1,712
runs). The registered exclusion machinery never had to fire in either
phase — parse validity is not a live risk for these models on these
instruments, including at T=1.3 (a registered surprise; see
temperature-pack).

## Cross-vendor replication scoreboard (context for stability)

Where both vendors ran the same confirmatory instrument: D2 role channel
replicated (both supported); D1 presentation effects and D3 bias direction
**anti-replicated** (null-vs-supported; opposite signs); F adversary
profile anti-replicated in sign (fo-tracker −0.118 gpt vs +0.159 gemini,
descriptive). Single-vendor stability (sentinels, replay) is excellent
while cross-vendor behavioral portability is poor — stability of the
record, not of the phenomenon.
