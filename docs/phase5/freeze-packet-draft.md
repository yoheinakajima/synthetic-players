# Phase 5 Freeze Packet — DRAFT FOR SIGN-OFF

> **STATUS: PROPOSED — UNREGISTERED, UNSEALED, NOT RUN.** Nothing dispatches
> before the operator's one-line approval of this packet. Order at approval:
> predicates freeze first → registry v4 seals (append-only, per-arm shas,
> external anchor at seal like `phase4-v3-seal`) → entry verification (live
> calls) → runs. Items marked **PIN AT FREEZE** get exact values written in
> before the seal; every other number below is final as proposed.

Design sketch (operator's order, committed verbatim):
[`design-sketch.md`](design-sketch.md). Entry-criteria verification record:
[`entry-criteria-verification.md`](entry-criteria-verification.md).

## §0 Entry criteria — status

All five instance-ledger rules verified with mechanical evidence; see the
verification record. Summary: (1) completeness linter **live**
(`engine/freeze_lint.py`), acceptance test reproduces the five Phase 4
sealed-text instances as seal failures, plus fail-closed shape and exact-coverage checks (8/8); (2) attestation gating **live**
(unchanged Phase 4 driver code); (3) three-layer rule **mechanized** as
linter check C4; (4) watchdog auto-resume **live** for the registered
signature list only (`engine/watchdog.py`, `engine/resume-signatures.json`),
scientific freezes stay manual; (5) budget **derived from ledger prices**
(`engine/phase5_budget.py` reads `budget.db` per-run actuals). The design
sketch is committed under `docs/phase5/` per §0.

## §1 Persona registry (registry v4) — proposed contents

Generated pre-data by `engine/gen_personas.py`: seeded (mulberry32, seed
**20260728**), fully crossed factors — age band {early-30s, early-60s} ×
{agreeable|competitive} × {patient|impulsive} × {risk-averse|risk-seeking} =
16 — with name/age/occupation drawn without replacement from registered
lists by the same stream. Banned-content guard greps every preamble (game/
cooperation/strategy/payoff/... word list in the generator); generation
fails on any hit. Full registry with per-persona sha256:
[`personas-v4-proposed.json`](personas-v4-proposed.json).

| id | leaning | preamble |
|---|---|---|
| p01 | coop | You are Arden, a 31-year-old bus driver. People who know you describe you as agreeable, patient, and risk-averse. |
| p02 | coop | You are Sasha, a 35-year-old nurse. People who know you describe you as agreeable, patient, and risk-seeking. |
| p03 | coop | You are Quinn, a 31-year-old electrician. People who know you describe you as agreeable, impulsive, and risk-averse. |
| p04 | defect | You are Marlow, a 31-year-old physiotherapist. People who know you describe you as agreeable, impulsive, and risk-seeking. |
| p05 | coop | You are Riley, a 35-year-old optician. People who know you describe you as competitive, patient, and risk-averse. |
| p06 | defect | You are Tatum, a 33-year-old pharmacist. People who know you describe you as competitive, patient, and risk-seeking. |
| p07 | defect | You are Devon, a 34-year-old dental hygienist. People who know you describe you as competitive, impulsive, and risk-averse. |
| p08 | defect | You are Avery, a 32-year-old librarian. People who know you describe you as competitive, impulsive, and risk-seeking. |
| p09 | coop | You are Rowan, a 64-year-old archivist. People who know you describe you as agreeable, patient, and risk-averse. |
| p10 | coop | You are Morgan, a 63-year-old surveyor. People who know you describe you as agreeable, patient, and risk-seeking. |
| p11 | coop | You are Jordan, a 61-year-old accountant. People who know you describe you as agreeable, impulsive, and risk-averse. |
| p12 | defect | You are Casey, a 65-year-old veterinary technician. People who know you describe you as agreeable, impulsive, and risk-seeking. |
| p13 | coop | You are Harper, a 61-year-old landscape gardener. People who know you describe you as competitive, patient, and risk-averse. |
| p14 | defect | You are Ellis, a 65-year-old bookkeeper. People who know you describe you as competitive, patient, and risk-seeking. |
| p15 | defect | You are Reese, a 63-year-old school teacher. People who know you describe you as competitive, impulsive, and risk-averse. |
| p16 | defect | You are Emerson, a 62-year-old carpenter. People who know you describe you as competitive, impulsive, and risk-seeking. |

**Composition rule (registered):** `persona_system = preamble + "\n\n" +
<sealed bare system text of the cell's template, byte-identical>`. The user
layer is byte-identical to the sealed Phase 3/4 templates, so every Phase 5
cell has an exact bare-subject twin in the prior record. Self-play pairs use
the same persona in both seats (X1/E lineage); seat pooling disclosed as
before.

**Leaning rule (registered at generation, never from behavior):**
cooperative-leaning iff ≥2 of {agreeable, patient, risk-averse}. The full
cross yields exactly 8/8.

**Participant definition:** one persona × one seed lane.

## §2 Temperature factor

T ∈ {0.7, 1.0, 1.3}; 0.7 is the program constant. Verification: the provider
adapters already pass `temperature` through explicitly
(`engine/phase4_providers.py`); at entry, the Gate-0-style battery (24 calls,
§5) asserts the echoed temperature in provenance **per call, per T** — the
Phase 3 packet assertion extended per-T. If T=1.3 degrades parse rates, that
is data: **invalid-trial rate per T is a registered secondary outcome**; the
registered exclusion rule stands unchanged.

**Registered operator prediction (on the record):** raising T adds symmetric
flip-noise around the corners and raises invalid rates, without increasing
the interior fraction — variance manufactured, behavior unchanged.
Refutation = interior fraction rising with T, or payoff-graded response
appearing (P5-4).

## §3 Task cells — six, all reusing sealed templates

| cell | template lineage | notes |
|---|---|---|
| rep-PD δ=0.10, S2-present | sealed pd-rep family, w2a (paraphrase present) | main instrument |
| rep-PD δ=0.10, S2-absent | sealed pd-rep family, w1 | |
| rep-PD δ=0.90, S2-present | sealed pd-rep family, w2a | |
| rep-PD δ=0.90, S2-absent | sealed pd-rep family, w1 | |
| one-shot label-swap, canonical payoffs | sealed D2 swap template | token-vs-dominance probe |
| one-shot Community framing | sealed community template | bare subject's near-interior point (P3 Δ=0.175); variance anchor |

Template ids + shas bind at registry-v4 generation from the sealed Phase 3/4
registry entries (byte-identical user layers; the exact id list is emitted by
the registry-v4 generator and lint-verified against `prompts/registry.json`).

## §4 Claim families — draft predicates (freeze at sign-off)

Common machinery, unchanged from Phase 4: episode-level units, Clopper–
Pearson 95% intervals, α=0.05, mechanical adjudicators only, per-window
store-derived indexing, verdict branches written before dispatch.

**P5-1 corner mixture.** Persona pools are mixtures of corners, not interior
distributions.
- P5-1a (interior fraction) — **AMENDED AT FREEZE (operator, 2026-07-28)**:
  unit = persona-cell. A persona-cell is *interior* iff its episode-level
  cooperation CP interval sits **wholly inside (0.05, 0.95)** — the Phase 4
  two-sided gate reused verbatim. **Primary set (restricted):** only
  persona-cells whose **bare twin fails the interior gate** (the same
  two-sided gate applied to the recorded bare data at T = 0.7). Supported iff
  the interior fraction on that restricted set < **θ₁ = 0.10 (PINNED)**.
  Registered edge case: if the restricted set is empty (every bare cell is
  interior), P5-1a is **undefined — null verdict, disclosed**, never coerced
  to supported/refuted. **Registered secondaries:** unrestricted interior
  fraction over all 96 persona-cells; by-cell-family breakdown (rep δ=.90,
  rep δ=.10, one-shot swap, one-shot community).
- P5-1b (population variance) — **PINNED AT FREEZE**. Human source:
  Dal Bó & Fréchette (2011), "The Evolution of Cooperation in Infinitely
  Repeated Games: Experimental Evidence," *American Economic Review* 101(1):
  411–429. Payoff matching: our normalized stage-game gain
  (R−P)/(T−P) = 0.5 sits nearest their **R = 40** column
  ((40−25)/(50−25) = 0.6; R=32 → 0.28, R=48 → 0.92), so both matched panels
  come from R = 40. δ matching by regime: our δ=.90 (cooperation
  supportable) ↔ their δ=¾; our δ=.10 (SPE defect) ↔ their δ=½.
  **Panel values echoed in the seal record:**
  - Table 3, first-round cooperation, last seven interactions:
    δ=¾, R=40 = **61.10%**; δ=½, R=40 = **18.72%**.
  - Table 7, strategy-frequency estimates, R=40 columns (bootstrapped SEs):
    δ=½: AD 0.783 (0.074), AC 0.078 (0.059), G 0.040 (0.040), TFT 0.098
    (0.070), WSLS 0.000 (0.007), T2 0.000, γ 0.541 (1.077).
    δ=¾: AD 0.109 (0.096), AC 0.296 (0.123), G 0.267 (0.202), TFT 0.327
    (0.186), WSLS 0.000 (0.000), T2 0.000, γ 0.435 (0.126).
  - Mechanical map (registered): each strategy's round-1 move is a corner —
    AD → defect; AC, G, TFT, WSLS, T2 → cooperate. Cooperative-start share
    q(δ=¾) = 0.891, q(δ=½) = 0.217. Implied human between-subject round-1
    SD = √(q(1−q)): **0.3116** (δ=¾) and **0.4122** (δ=½).
  - Predicate: per matched rep-PD cell (the four rep cells only; one-shot
    cells have no matched δ panel → **null, not 0**), the persona pool is
    corner-mixture-consistent iff between-persona SD of persona-level
    round-1 cooperation ≥ **ρ × implied human SD** for the matched panel,
    with **ρ = 0.75 (PINNED)** — rationale: within one bootstrap-SE band of
    the human point values; constant chosen before any Phase 5 data exists.

**P5-2 surface-cue dominance hierarchy.** Conflict cells: cooperative-leaning
× S2-absent; defect-leaning × S2-present; each leaning × label-swap.
Estimand: within-conflict-cell share of choices consistent with the task-text
switch direction vs the persona-lean direction. Registered directional
prediction: **task-text dominates** — verdict `task-dominant` iff CP lower
bound of task-consistent share ≥ **0.80**; `persona-dominant` iff upper bound
≤ **0.20**; else `mixed` (the D2 0.80/0.20 convention reused).

**P5-3 within-persona incentive sensitivity (existence).** A persona *passes*
iff, at any registered temperature: (a) both its δ cells (matched S2 level)
have episode means inside the two-sided gate **and** its δ-slope (round-1
coop at δ=.90 − δ=.10) has one-sided 95% LB > 0 — the Phase 4 Family-E assay
reused; **or** (b) it refuses the dominated mislabeled option in the swap
cell with CP LB ≥ **θ₂ = 0.20 (PINNED AT FREEZE, operator 2026-07-28)** (bare subject's
observed rate and human anchors cited at freeze). **Registered operator
prediction: zero of 16 passes** (and zero in the sweep). One passing persona
relocates human-likeness into the conditioning; zero across 16 × 3
temperatures completes the paper's strongest claim.

**P5-4 temperature.** Confirmatory: interior fraction does not increase with
T on the sweep subset — refuted iff LB(interior fraction at T=1.3 − at
T=0.7, matched cells/personas; **CI method PINNED: Newcombe score-based
interval for a difference of proportions, one-sided 95% lower bound**) > 0, **or** a
persona×cell shows δ-slope LB > 0 at T ∈ {1.0, 1.3} where the same
persona×cell shows none at 0.7. Registered secondaries: invalid rate per T,
choice entropy per T; behavioral change decomposed from parse degradation
(invalid-excluded and invalid-inclusive tabulations both reported).

Multiplicity: within-family handling pinned at freeze (Phase 4 convention:
existence claims are one-per-family; fraction predicates are single
pre-registered thresholds, no selective sub-cell testing).

## §5 Subjects, sentinels, entry verification

- **Primary:** gpt-4.1, same pinned revision `gpt-4.1-2025-04-14`. Entry
  battery re-verifies the returned revision on live calls; any provider-side
  change is a disclosed event, never a silent substitution.
- **Secondary:** gemini-2.5-flash at **reduced tier only** (T=0.7, core
  cells, replication framing) given the documented plateau instability.
  Costed separately (Tier C = **1,224 calls**) for a clean drop.
- **Sentinels:** battery from day one includes, per model, one
  persona-conditioned fingerprint cell (registered persona p01) and one bare
  fingerprint cell; 10 checks × 5 episodes × 2 calls; per-window indexing
  armed from check 1; attestation gating exactly as Phase 4.
- **Entry verification (24 infra calls):** revision pin + per-T temperature
  echo assertion, 3 temps × 2 models × 4 calls.

## §6 Cell counts, fraction, aliasing, call table, shedding

Full cross (16 × 3 T × 6 cells) explodes; the registered fraction:

- **Tier A:** all 16 personas × all 6 cells at T=0.7 (rep-PD 6 ep/cell,
  one-shots 20 ep/cell).
- **Tier B:** temperature sweep T ∈ {1.0, 1.3} on the **registered
  4-persona subset {p02, p06, p11, p15}** (seeded draw, seed 20260729;
  balanced 2 coop-leaning + 2 defect-leaning, one per leaning × age band) ×
  3 cells (δ=0.90 pair + swap), **plus a bare-subject T twin** on the same
  3 cells (the bare subject was never run above 0.7; the twin de-aliases
  "temperature effect" from "temperature × persona effect").
- **Tier C:** gemini, T=0.7, registered balanced 8-persona half, δ=0.90 pair
  (4 ep) + swap (10 ep).

**Aliasing consequences (D1-style disclosure):**
1. T main effects are estimable only on the 4-persona subset + bare twin;
   T × persona interaction beyond that subset is **not estimable** — deliberately
   sacrificed, disclosed.
2. T is not crossed with δ=0.10, community, or S2-present one-shot cells:
   P5-4 claims are scoped to the registered sweep cells only.
3. The subset draw is seeded and leaning/age-balanced, so T contrasts are not
   confounded with leaning or age band; occupation/name remain aliased into
   persona identity (as designed — persona is the unit, factors are the
   generative recipe).
4. Tier C (gemini) covers only δ=0.90 + swap at T=0.7: cross-vendor claims
   are replication-framed on those cells, nothing else.

**Call table (ledger prices — `budget.db` per-run actuals; A-OVH-2 rule):**
full table in [`call-table.md`](call-table.md) / [`call-table.json`](call-table.json).
Prices: rep-PD δ=0.90 **14.85** calls/ep (gpt mean; max 44), δ=0.10 **2.05**,
one-shot **2** (gemini 15.36 / 3), sentinel **2**.

| Tier | Calls |
|---|---|
| A (primary, 16 personas, 6 cells) | 4,526 |
| B (T sweep + bare twin) | 2,183 |
| C (gemini, separable) | 1,224 |
| S (sentinels + entry) | 424 |
| Subtotal | **8,357** |
| Headroom 7.5% (from Phase 4 waste actuals) | 627 |
| **Total** | **8,984 ≤ 15,000 cap** |

**Shedding order (registered now):** 1. drop Tier C whole; 2. Tier B rep-PD
6→4 ep; 3. Tier A rep-PD 6→4 ep; 4. one-shots 20→12 ep; 5. freeze. **Never
shed personas** (kills the zero-of-16 claim) **or sentinels** (kills
attestation) — shedding reduces episodes only. Kill-switch: global 15,000 in
the budget ledger, per-tier cap groups, same enforcement as Phase 4.

## §7 Paper integration — sealed material

- [`../paper/discussion-branches.md`](../paper/discussion-branches.md):
  discussion/conclusion pre-committed **verbatim per outcome branch**
  (corners-everywhere / any-interior-persona / temperature-graded / mixed),
  with a registered branch-selection rule and an exhaustive 8-row verdict-
  combination table; P5-2 variant paragraphs pre-written in every branch.
  Hash-anchors with registry v4. Linter check C5 fails the seal if any
  registered verdict combination lacks a branch.
- [`../paper/scope-seal.md`](../paper/scope-seal.md): Phase 5 is the final
  experiment for paper one; no new arms; no Phase 6 before publication;
  future-work routing rule.

## §8 Seal & anchor plan

Registry v4 = registry v3 (immutable) + appended persona entries (per-persona
shas), Phase 5 arms (per-arm shas binding template sha × persona sha × T ×
seeds × model), sealed execution schedule (mulberry32-seeded interleave),
discussion-branches + scope-seal hashes. Seal procedure identical to
`phase4-v3`: freeze-lint gate (must PASS on the full manifest, including
three-layer anchors for the Phase 5 dispatch/enforcement/replay code),
SHA256SUMS, annotated tag + GitHub release + OTS stamp.

## §9 Sign-off record (operator, 2026-07-28) — ALL APPROVED

1. **Pinned:** θ₁ = 0.10 on the amended (bare-twin-restricted) P5-1a set;
   θ₂ = 0.20; P5-1b panel values from Dal Bó & Fréchette (2011 AER) Tables
   3 and 7 with ρ = 0.75 (values echoed in §4 and in the seal record);
   P5-4 CI method = Newcombe one-sided 95% LB.
2. **Persona seed 20260728 approved, no reroll** — operator: rerolling
   without a rule violation is itself selection. The banned-content guard's
   full list is part of the seal record (§1) for the paper.
3. Fraction, four aliasing consequences, call table, shedding order —
   **approved**. Tier B bare-subject temperature twin **approved** (de-alias
   worth its 437 calls).
4. Gemini Tier C **kept** (1,224 calls): cross-vendor twin, replication
   framing + per-window indexing from day one; personas and sentinels never
   shed, as registered.
5. Discussion branches + scope seal **approved as sealed material**; the
   branch-file sha enters registry v4 and the paper's methods section cites
   the sha + anchor timestamp.
6. 24-call entry battery (revision pin + per-T echo) **approved as ledgered
   overhead** immediately post-seal.

**Freeze order:** amended packet re-lints clean → registry v4 seals →
external anchor → entry battery → dispatch.

**Banned-content guard (verbatim, from the persona generator; sealed):**
`["game", "cooperat", "defect", "strateg", "opponent", "payoff", ...]` — the
authoritative list is `bannedContentGuard` in `personas-v4-proposed.json`,
sha-anchored with registry v4; the generator fails closed on any hit.
