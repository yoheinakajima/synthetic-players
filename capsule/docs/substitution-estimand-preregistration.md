# Substitution Estimand — Registration (registered now, run post-publication)

**Status:** REGISTERED 2026-07-24, **pending one parameter** (equivalence margin ε, set at
sign-off — see §4). No human data exists; none will be collected before paper 1 ships. Paper 1
cites this document as *registered and pending*, never as evidence. Nothing in paper 1 may
depend on this study's outcome.

**Relationship to paper 1:** paper 1's claim is the validation protocol plus a boundary study
of specific model-policy deployments. Whether an LLM can *substitute* for human subjects is
explicitly out of paper-1 scope; this document is the registered follow-on that would answer
it for two specific effects.

## 1. Estimands

Let Δ denote a within-population treatment effect and D the substitution discrepancy:

**D = Δ_agent − Δ_human**, computed for two registered effects:

1. **Framing effect (one-shot PD):**
   Δ = round-1 cooperation(Community label) − round-1 cooperation(Wall Street label),
   identical game, payoffs, and protocol in both populations.
2. **δ slope (repeated PD):**
   Δ = round-1 cooperation(δ=0.90) − round-1 cooperation(δ=0.10),
   under the presentation selected by Phase 4 Experiment E (the highest-cooperation
   representation, frozen before any human session).

Agent-arm quantities come from the sealed, replay-verified corpora (Phase 3/4). Human-arm
quantities come from sessions run on the **same engine and event store** with yoked fixed
opponents identical to the agent arm (byte-verified sessions, no PII in the store).

## 2. Hypotheses and decision rule

For each effect, equivalence is tested by TOST at α = 0.05:

- H0 (non-equivalence): |D| ≥ ε
- H1 (equivalence): |D| < ε

Declare **substitution-valid for that effect** iff both one-sided tests reject (90% CI for D
inside (−ε, +ε)). Declare **substitution-invalid** iff the 90% CI lies entirely outside
[−ε, ε] on either side. Otherwise **inconclusive** (reported as such; no re-margining after
data). The verdicts are per effect — there is no composite "human-equivalent" verdict.

## 3. Units, clustering, and analysis plan

- Unit of analysis: independent session (run) — the cluster level established in the Phase 3
  Layer-2 review. Seat decisions never enter tests as independent observations.
- D's sampling variance: var(Δ_agent) + var(Δ_human) (independent populations). Where an
  agent arm shows zero variance (observed repeatedly in Phase 3), var(Δ_agent) is bounded
  above by its run-level Clopper-Pearson interval width, not assumed 0.
- Human-arm test statistic: difference in proportions across conditions with run-level
  bootstrap CI (10,000 reps, seeded); TOST via the 90% bootstrap CI.
- Exclusion rules, parser policy, and invalid-trial handling: identical to the agent arm's
  registered rules; human non-completion handled by intention-to-treat exclusion, count
  disclosed.

## 4. Equivalence margin ε — PENDING SIGN-OFF

ε is a scientific judgment, not a statistical output; it is set once at sign-off and never
revised after any human data exists. Reference points for the decision:

- ε = 0.05: strict — requires the agent to track humans within 5pp on the effect scale.
- ε = 0.10: one-half of the smaller Phase 3 framing effect bound.
- ε = 0.15: comparable to the cross-study spread of human framing effects.
- ε = 0.20: lenient — sign-and-rough-magnitude agreement only.

## 5. Power analysis (human n per cell at margin ε)

Assumptions (worst-case, disclosed): human proportions at maximal variance (p = 0.5);
Δ_human is a difference of two independent cells of size n → SE(Δ_human) = √(0.5/n);
agent-arm variance treated as negligible relative to human (its corners are deterministic;
its CP bound is folded into sensitivity, §6). TOST power: n satisfies
√(0.5/n) ≤ ε / (z₁₋α + z₁₋β), α = 0.05 one-sided per test.

| ε | n per cell (80% power) | n per cell (90% power) |
|---|---|---|
| 0.05 | 1,238 | 1,714 |
| 0.10 | 310 | 429 |
| 0.15 | 138 | 191 |
| 0.20 | 78 | 108 |

Two effects × two conditions each = 4 human cells (framing: Community, Wall Street;
δ slope: δ=.10, δ=.90 under the frozen presentation). Total human N = 4 × n per cell.
Numbers shrink if literature-informed p's (0.2–0.5) replace the worst case; the worst case
is registered as the floor.

## 6. Sensitivity disclosures (registered)

- If the agent arm's relevant cell sits at a Clopper-Pearson-bounded corner, the analysis
  reports D's CI both with var(Δ_agent) = 0 and with the CP-bound-implied variance; if the
  verdicts differ, the study is inconclusive for that effect.
- The agent arm is re-run through the drift sentinel window overlapping human data
  collection; if the sentinel flags distributional drift beyond its registered threshold,
  the agent-arm quantities are re-estimated on a fresh sealed batch before D is computed.

## 7. What is frozen now vs later

| Item | Frozen now | Frozen at sign-off | Frozen before human run |
|---|---|---|---|
| Estimands (both D's) | ✔ | | |
| TOST decision rule, α, CI method | ✔ | | |
| Cluster level / units | ✔ | | |
| ε | | ✔ | |
| E-selected presentation (δ-slope arm) | | | ✔ (from Experiment E, before any human session) |
| Human protocol details (consent, session codes, yoking schedule) | | | ✔ |
