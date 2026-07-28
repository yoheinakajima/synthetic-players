# Phase 5 Registry v4 — Seal Record

- **Sealed at:** 2026-07-28 (UTC; commit timestamp of the seal commit is authoritative)
- **Sealed by:** operator approval (mission UI, 2026-07-28: freeze approved with
  amendments 1–6), executed per the frozen order: amended packet re-lint PASS →
  registry v4 seal → external anchor → entry battery → dispatch.
- **What changed at seal:** exactly one line of
  `artifacts/api-server/prompts/registry.json` — `registryVersion`
  `"phase5-v4-proposed"` → `"phase5-v4"`. Zero template, arm, seed, persona,
  binding, or schedule bytes changed. Templates are byte-untouched from the
  phase4-v3 seal; Phase 5 added only the append-only `phase5` anchor block.
- **Pre-seal registry sha256:** `8248214c96b6031cc7db3f0639b3d7d5f239967035128e2ecaed0ab3471d8a82`
- **Post-seal registry sha256:** `c1e7254324c5dbbe185792af0d85b8af587e7686478275ce85f70fadffe42be6`
- **arms.json sha256:** `ab753651b4c0e335f180af1d9c60a37c32c855dfc151b3f6bcf89d412ba5b018`
  (160 arms: 96 tier A, 30 tier B, 24 tier C, 6 entry, 4 sentinel)
- **execution-schedule.json sha256:** `04ceffd74026cea5ed1157f8d704087dda26180c8dd0fd9d20b48183215055d0`
  (1,488 episodes; mulberry32 interleave seed 20260731)
- **personas-v4.json sha256:** `a0b1d7b884c62ced4f48b01fe91bfd1490d3c2d9c2ca77ec59409889ef4ec893`
  (byte-identical to the approved proposal; persona seed 20260728, no reroll)
- **discussion-branches.md sha256:** `1f1d7de9c54811962416a43bc5eed05de7fdd99618d39c88e5a8ec2cde9f0356`
- **scope-seal.md sha256:** `a0389d9f3268d686ff2f4f8b93fa65c43aad77a35c52076ed1f365b4d935c0e6`
- **Seal-gate lint:** `lint-manifest.json` (160 cells, 5 three-layer sealed rules)
  → `lint-result.json` **PASS, zero failures** (C0–C5), run against the
  pre-seal registry and re-run after the flip (templates unchanged by construction).

## Pinned analysis constants (echoed from the approved freeze packet)

- **P5-1a (amended):** primary set restricted to persona-cells whose bare twin
  fails the two-sided (0.05, 0.95) Clopper–Pearson interior gate on recorded
  bare data at T=0.7; **θ₁ = 0.10** on the restricted set; empty restricted set
  ⇒ null verdict. Secondaries: unrestricted fraction + by-cell-family breakdown.
- **θ₂ = 0.20** (temperature-grading predicate).
- **P5-1b (pinned):** Dal Bó & Fréchette 2011 AER 101(1):411–429, R=40 column
  (payoff match (R−P)/(T−P)=0.5). Table 3 first-round cooperation (last seven
  interactions): δ=¾: **61.10%**; δ=½: **18.72%**. Table 7 R=40 strategy shares —
  δ=½: AD .783, AC .078, G .040, TFT .098, WSLS 0, T2 0; δ=¾: AD .109, AC .296,
  G .267, TFT .327, WSLS 0, T2 0. Mechanical map AD→defect, rest→cooperate:
  q = .217 / .891 ⇒ implied human between-subject round-1 SD = √(q(1−q)) =
  **0.4122** (δ=½) / **0.3116** (δ=¾). Predicate: per matched rep-PD cell only
  (one-shots ⇒ null); between-persona SD ≥ **ρ × human SD, ρ = 0.75** (pre-data;
  within one bootstrap-SE band).
- **P5-4 CI method:** Newcombe score-based difference of proportions,
  one-sided 95% lower bound.
- **Sealed banned-word list** (persona preamble content guard; authoritative
  copy in `personas-v4.json` `bannedContentGuard`): `game`, `cooperat`,
  `defect`, `strateg`, `opponent`, `payoff`, `player`, `points`, `prisoner`,
  `dilemma`, `betray`, `trust`, `reciproc`, `compete against`, `win`, `lose`.

## Sealed conditional rules (three-layer anchors, lint C4)

1. **R1-persona-composition** — persona system = preamble + `"\n\n"` + sealed
   bare system, byte-identical; persona sha pinned per arm, re-verified per
   request, re-derived from the sealed store in replay.
2. **R2-per-T-echo** — wire request body's temperature field must equal the
   arm's pinned T on every call (mirror asserted == wire sha; refused pre-dispatch).
3. **R3-revision-pin** — returned model string must equal
   `gpt-4.1-2025-04-14` / `gemini-2.5-flash`; mismatch aborts (archived, spend kept).
4. **Sentinel attestation gate** — dispatch past a sentinel check requires a
   positive `phase5_adjudicate.py` attestation (S1–S5); absence fail-closes.
5. **Registered-shedding-only** — binding cap projections freeze; sheds apply
   the registered order, whole arms, disclosed.

## Budget

Caps sealed in `engine/phase5.py`: P5-A 4,866 / P5-B 2,347 / P5-C 1,316 /
P5-overhead 456; **global Phase 5 kill-switch 8,984** inside the operator's
15,000 authorization. Entry battery (24 calls) and sentinels (200) are
ledgered overhead, operator-approved.

## External anchor

- `docs/phase5-close/SHA256SUMS.txt` — sha256 over all sealed files (listed there).
- OpenTimestamps: `docs/phase5-close/SHA256SUMS.txt.ots`.
- Annotated tag `phase5-v4-seal` + GitHub release `phase5-v4-seal` on
  `yoheinakajima/synthetic-players`.

## Amendment rule

Any subsequent change to registry v4 templates, arms, seeds, personas, or
schedule requires a registered amendment; this record plus the external
anchor is the seal.
