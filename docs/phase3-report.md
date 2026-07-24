# Phase 3 Report — The LLM as a Behavioral Subject

**Study:** pre-registered in [`phase3-preregistration.md`](phase3-preregistration.md) (claims registered before any data; registry sha pinned).
**Subject:** `gpt-4.1` via Replit AI Integrations, temperature 0.7, maxTokens 16, engine-live event-sourced path.
**Status:** COMPLETE (July 24, 2026). All numbers below are transcribed from the mechanical
adjudication output (`node scripts/run-phase3.mjs adjudicate`); verdicts were never hand-set.
**Corpus:** 280 LLM experiments (160 A + 60 B + 60 C) + 20 zero-LLM baseline runs, 5,184 LLM calls.

## 1. Design summary

Three families, 20 seeded replicates per cell, all claims adjudicated
mechanically against pre-registered predicates (95% Welch CIs unless a point
comparison was pre-registered):

- **A — Shadow of the future.** Random-termination repeated PD (continuation
  probability δ ∈ {.10, .50, .75, .90}), LLM self-play, canonical payoffs
  (3,0,5,1) plus an affine isomorph (×3+2) as a contamination probe. Horizons
  drawn client-side from a seeded geometric (mulberry32, safety cap 120,
  hidden from the subject). Primary statistic: round-1 cooperation.
- **B — Framing.** One-shot PD labeled "Community Game" / "Wall Street Game" /
  neutral, self-play pairs, n=20 per framing.
- **C — Mixed-strategy play.** RPS, 50 rounds: vs pattern-tracker, vs
  nash-mixed, self-play; plus a zero-LLM pattern-tracker-vs-nash-mixed
  baseline for the exploitability comparison.

Reproducibility contract: every completed run replays from the engine event
store with **zero live LLM calls**, byte-exact on every action and payoff, and
its stored metrics are recomputed and byte-compared (`POST
/experiments/:id/replay`).

## 2. Results by predicate

| Claim | Verdict | Key numbers |
|---|---|---|
| P3-A1 shadow of the future (δ=.90 > δ=.10) | **refuted** | Round-1 cooperation 0.000 at **both** δ levels (n=20 each, sd=0 → exact comparison) |
| P3-A2 risk-dominance separation | **refuted** | Pooled high-δ 0.000 vs low-δ 0.000 (n=40 vs 40, sd=0) |
| P3-A3 human-range membership [36%, 63%] | **refuted** | High-δ round-1 cooperation 0.000; human band [0.36, 0.63] |
| P3-A4 isomorph invariance | **refuted** | (a) isomorph separation 0.000 − 0.000 → refuted; (b) \|canonical − isomorph\| = 0.000 ≤ 0.15 → supported. Claim fails on (a) |
| P3-B1 framing direction (community > wallstreet) | **supported** | 0.175 vs 0.000; diff CI [0.061, 0.290], Welch df 19 |
| P3-B2 framing magnitude (ratio ≥ 1.5) | **inconclusive** | Wall Street mean exactly 0 → pre-registered edge rule (supported iff community ≥ 0.30); observed 0.175 |
| P3-B3 neutral interior | **supported** | 0.000 ≤ 0.000 ≤ 0.175 (Wall Street/neutral tie, ties allowed) |
| P3-C1 round-1 RPS distribution | **refuted** | Rock modal ✓ (0.80 vs paper 0.20, scissors 0.00); scissors < ⅓ ✓; **rock 0.80 ∉ [0.33, 0.40]** (n=80 seat decisions) |
| P3-C2 win-stay/lose-shift signature | **supported** | P(stay\|win) 0.683 CI [0.586, 0.780] > ⅓; P(shift\|lose) 0.974 CI [0.958, 0.991] > ⅔ (n=61 decisions with a usable conditional) |
| P3-C3 tracker exploits LLM beyond Nash baseline | **refuted** | **Sign reversal:** tracker per-round −0.103 vs LLM, −0.023 vs Nash baseline; diff CI [−0.133, −0.027] entirely negative |

Phase 3 verdict totals: 3 supported · 6 refuted · 1 inconclusive.

## 3. Study integrity

- Prompt registry sha256: `73e7a6ca…` (pinned; asserted by claims + runs steps; drift = abort)
- Replay verification: **280 of 280** completed runs bit-exact, **0 live calls**, all metric
  recomputations byte-identical to stored analyses
- Invalid trials: **0** of 280 (0%); replacement seeds used: 0
- Truncated horizon draws (cap 120): 0
- Budget: A 1,064/1,800 · B 120/160 · C 4,000/4,400 · global **5,184/6,360** (kill-switch never approached)
- Verdict-flip audit of pre-existing claims: **no pre-existing claim changed verdict** (the
  self-play Focus = mean-of-both-seats semantics introduced for Phase 3 flipped nothing)
- Post-registration machine check: every adjudication stamps `postRegistered` by comparing
  the claim's registration timestamp to the earliest experiment cited as its evidence.
  **All 10 P3 claims: `postRegistered=false`** (registered before any Phase 3 row existed);
  the v1 backfill corpus is honestly flagged `true` (disclosed post-hoc claims). Predicates
  are now immutable once a claim has been adjudicated (HTTP 409 on edit — HARKing guard).

### Amendments (disclosed, post-study)

Post-study code review found two gaps between the pre-registration's promises and the
implementation. Both were fixed the same day (July 24, 2026), re-adjudication after the
fixes flipped **zero** verdicts, and no Phase 3 result is affected:

1. **Post-registration enforcement was procedural, not mechanical.** The prereg (§Procedural
   locks) promised adjudicator-level timestamp enforcement; at study time this ordering was
   enforced only by the study runner (claims step aborts if any `:t3` row predates
   registration — which held, as the timestamps now machine-verify). The adjudicator-level
   check has been implemented as a **disclosed flag on every adjudication** rather than the
   promised refusal-to-adjudicate, because refusal would retroactively suppress the v1
   corpus whose *disclosed* post-hoc status is part of the lab's public record.
2. **Failed-run provider spend could have been invisible to budget accounting.** A run that
   errored mid-way (after live calls) previously persisted no call count on the failed row.
   The engine now embeds `{engineRunId, llmCalls, partial:true}` in structured failure
   errors and the API persists it before marking the row failed. Not exercised in this
   study: 0 of 280 runs failed, so no spend was ever uncounted (audited).

## 4. Findings (interpretation written after adjudication — kept separate from §5's pre-committed notes)

1. **No shadow of the future — at all.** In 160 repeated-PD supergames (320 seat
   decisions) gpt-4.1 defected in round 1 every single time, at every continuation
   probability including δ=0.90, in both payoff arms. Humans in the same designs
   cooperate 19–64% in round 1. This is not noisy under-cooperation; it is a uniform
   corner solution (sd = 0 → the adjudicator's exact-comparison path, no CI needed).
2. **Framing works where δ does not.** The same subject that never cooperates in
   repeated play cooperates in 17.5% of decisions when the *identical* one-shot game
   is labeled "Community Game" (0% under "Wall Street Game" and neutral labels).
   Direction matches Liberman et al.; magnitude is weaker than the human ~2× gap
   (B2 inconclusive via the pre-registered denominator-zero edge rule, which fired
   exactly as designed).
3. **A caricature of the human rock bias.** Round-1 rock 80% (humans ~34–36%), paper
   20%, scissors 0%. The direction of every human asymmetry is preserved but the
   magnitude is ~2× beyond the human band — so C1 correctly refutes on the
   pre-registered range check while both modal-ness items pass.
4. **Strong win-stay/lose-shift.** P(shift|lose) = 0.974 — near-deterministic
   outcome-dependence, far above the human ~⅔ signature; P(stay|win) = 0.683.
5. **The tracker got out-tracked.** The pre-registered exploitability hypothesis
   reversed sign: the first-order pattern tracker *lost* 0.103/round against the LLM
   (vs −0.023 against Nash). gpt-4.1's outcome-conditioned play (finding 4) is not
   first-order action-Markov, and the deterministic tracker was itself predictable.
   A cleanly refuted prediction with an interesting sign reversal — exactly what the
   registry is for.

## 5. Interpretation notes (written before results)

Committed in the pre-registration and repeated here so they cannot drift:

- **Wide CIs and inconclusive verdicts are honest outcomes.** LLM replicates
  are legitimately bimodal; we do not narrow intervals post hoc.
- **A4(b) failing while A4(a) holds** suggests matrix memorization rather than
  incentive reasoning — that is a finding, not a nuisance.
- **C2 null result is human-plausible** (only ~⅓ of humans show
  outcome-dependent RPS play); refutation requires the CI to lie entirely on
  the wrong side of the independence null.
- Self-play pooling for C1/C2 (both seats contribute decisions) was
  pre-registered; within-run seat dependence is disclosed as a limitation.
