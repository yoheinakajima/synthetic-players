# Phase 5 sealed-predicate adjudication — final record

Generated 2026-07-28 by `engine/phase5_closeout_adjudicate.py --adjudicate`
(verdicts verbatim from code; the author adjudicated nothing). Machine
record: `docs/phase5-close/adjudication-report.json`. Selftests: ALL PASS.
Replay audit precondition: PASS — CLEAN, 1,712 runs, 0 mismatches
(`docs/phase5-close/replay-audit.md`).

Outcome-blind completions of underspecified sealed bits (bare-gate table
computed from bare data only; operator signed before any persona outcome was
disclosed): `docs/phase5-close/adjudication-decisions.json` — D1 exact-twin
only; D2 role-level leanings, defect-leaning × swap only; D3 Axis A =
P5-1a alone. Consistency check recorded there: the sealed 8-row combination
table's Axis A column enumerates exactly {supported, not-supported}.

## Data basis

Tier A: 96 persona-cells (16 personas × 6 cells), gpt-4.1, T=0.7. Sweep:
{p02,p06,p11,p15} × {rep-d90-s2a, rep-d90-s2p, os-swap} × T∈{1.0,1.3}.
Completed runs only; **0 invalid trials at every temperature** (registered
exclusion rule had nothing to exclude). Round-1 cooperation, seat-level
trials; cooperate role derived from the recorded payoff matrix, never from
displayed labels. Interior gate: CP 95% wholly inside open (0.05, 0.95).

## Bare-twin gate table (restricted-set input, bare data only)

| bare source | k/n | CP95 | gate |
|---|---|---|---|
| sentinel bare rep-δ90-w1-neu T0.7 (exact twin, rep-d90-s2a) | 0/100 | [0.000, 0.036] | NOT interior → restricted |
| p4-d2-w1-can-sw-gpt (exact twin, os-swap) | 0/40 | [0.000, 0.088] | NOT interior → restricted |
| P3 community bare (exact twin, os-community) | 7/42 | [0.070, 0.314] | INTERIOR → excluded |
| rep-d90-s2p, rep-d10-s2a, rep-d10-s2p | — | — | **no exact bare T=0.7 run in the record** → dropped from restricted candidacy (D1); flagged in secondaries |

## P5-1a — interior-fraction (primary) — **supported**

Restricted set {rep-d90-s2a, os-swap} = 32 units; interior 3/32 = **0.09375
< θ₁ = 0.10** → supported. Margin disclosure: a single additional interior
unit would have flipped the verdict (4/32 = 0.125).

Secondaries: unrestricted fraction 14/96 = 0.1458. By family: rep-δ90 8/32
(0.250), rep-δ10 4/32 (0.125), os-swap 0/16 (0.000), os-community 2/16
(0.125). Cells without exact bare twin (rep-d90-s2p, rep-d10-s2a,
rep-d10-s2p) appear in these secondaries only.

Interior units (14): p04|rep-d10-s2p, p04|rep-d90-s2p, p05|rep-d10-s2a,
p05|rep-d90-s2a, p05|rep-d90-s2p, p07|rep-d90-s2a, p12|rep-d90-s2p,
p13|os-community, p13|rep-d10-s2a, p13|rep-d90-s2a, p13|rep-d90-s2p,
p15|os-community, p15|rep-d10-s2a, p15|rep-d90-s2p.

## P5-1b — between-persona SD vs human panels — **corner-mixture-consistent, all 4 rep cells**

| cell | SD (n=16) | threshold ρ·humanSD | verdict |
|---|---|---|---|
| rep-d90-s2a | 0.4454 | 0.2337 | corner-mixture-consistent |
| rep-d90-s2p | 0.4362 | 0.2337 | corner-mixture-consistent |
| rep-d10-s2a | 0.4241 | 0.3092 | corner-mixture-consistent |
| rep-d10-s2p | 0.4800 | 0.3092 | corner-mixture-consistent |

One-shot cells: null (predicate defined for matched rep-PD cells only —
never reported as 0). SD = sample SD (ddof=1) of persona-level round-1
cooperation means; human SDs 0.3116 (δ90 pair), 0.4122 (δ10 pair), ρ=0.75.
Not branch-bearing (D3); selects within-branch variant text only.

## P5-2 — surface-cue dominance — **persona-dominant**

Pooled task-consistent share 90/704 = **0.128, CP95 [0.104, 0.155]** — upper
bound ≤ 0.20 → persona-dominant. **The registered directional prediction
(task-text switches dominate personas) failed.**

| conflict cell | task-consistent | CP95 | verdict |
|---|---|---|---|
| coop-leaning × rep-d10-s2a | 37/96 = 0.385 | [0.288, 0.490] | mixed |
| coop-leaning × rep-d90-s2a | 30/96 = 0.312 | [0.222, 0.415] | mixed |
| defect-leaning × rep-d10-s2p | 9/96 = 0.094 | [0.044, 0.171] | persona-dominant |
| defect-leaning × rep-d90-s2p | 14/96 = 0.146 | [0.082, 0.233] | mixed |
| defect-leaning × os-swap | 0/320 = 0.000 | [0.000, 0.011] | persona-dominant |
| coop-leaning × os-swap | — | — | excluded (D2): descriptive word-level dissociation probe only |

## P5-3 — interior-persona existence — **all 16 of 16 personas pass**

**The registered prediction (zero of 16 pass) failed.** Axis B =
at-least-one.

- Clause (b) fires for every persona: in the swap cell every persona
  overwhelmingly chooses the payoff-dominant option displayed under the
  word COOPERATE (per-persona refusal CP LBs 0.55–0.91, all ≥ θ₂=0.20; the
  bare subject chooses it 0/40). Mechanism note (descriptive, not
  verdict-bearing): word-choice and payoff-dominance coincide in this cell
  for personas — the sealed predicate keys on the choice, not the mechanism.
- Clause (a) additionally fires for **p13** (Harper, competitive-patient
  risk-averse, 61): s2a δ-pair both interior AND δ-slope one-sided 95% LB
  = **+0.083 > 0** — the first subject-frame arm in the entire program to
  pass the Family-E human-signature assay.

## P5-4 — temperature grading — **not refuted**

Matched sweep (4 personas × 3 cells): interior fraction 1/12 = 0.083 at
T=0.7 vs 3/12 = 0.250 at T=1.3; Newcombe one-sided 95% LB of the difference
= **−0.095** (not > 0) → clause 1 not refuted. Clause 2 (δ-slope appearing
at high T) non-estimable — registered aliasing disclosure: T is not crossed
with δ=0.10, so the clause cannot fire; disclosed, not adjudicated.
Descriptive T=1.0: 3/12 = 0.250.

Secondaries: invalid rate 0/1376 (T0.7), 0/168 (T1.0), 0/168 (T1.3);
round-1 choice entropy 0.906 (T0.7), 0.787 (T1.0), 0.777 (T1.3) — entropy
*falls* with temperature. The registered operator prediction (T adds
flip-noise and invalids without raising interiority) is consistent with the
confirmatory verdict but its noise mechanism did not appear.

## Axes and branch

| axis | value | source |
|---|---|---|
| A (corner mixture) | supported | P5-1a alone (D3) |
| B (interior persona) | **at-least-one** | P5-3 |
| C (temperature-graded) | no | P5-4 |

Registered selection order: B=at-least-one → **Branch 2** (first rule;
A and C never consulted). P5-2 selects variant-paragraph text only.
