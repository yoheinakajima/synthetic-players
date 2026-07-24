# Phase 3 Report — The LLM as a Behavioral Subject

**Study:** pre-registered in [`phase3-preregistration.md`](phase3-preregistration.md) (claims registered before any data; registry sha pinned).
**Subject:** `gpt-4.1` via Replit AI Integrations, temperature 0.7, maxTokens 16, engine-live event-sourced path.
**Status:** COMPLETE (July 24, 2026), plus post-review **Extension X1** run the same day (§6) —
its result **overturns the generality of the A-family interpretation** under the extension's own
pre-committed disclosure rule. All numbers below are transcribed from the mechanical adjudication
output (`node scripts/run-phase3.mjs adjudicate`); verdicts were never hand-set.
**Corpus:** 320 LLM experiments (160 A + 60 B + 60 C + 40 X1) + 20 zero-LLM baseline runs, 5,820 LLM calls.

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

A fourth, post-result extension family — **X1, paraphrase robustness** of the
A-family corner at δ=.90 — was registered and run after external review; its
design, provenance, and result are in §6.

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
| P3-A4 isomorph invariance | **refuted** | (a) isomorph separation 0.000 − 0.000 → refuted; (b) \|canonical − isomorph\| = 0.000 ≤ 0.15 → supported, but vacuous at the 0−0 floor (§4, finding 6). Claim fails on (a) |
| P3-B1 framing direction (community > wallstreet) | **supported** | 0.175 vs 0.000; diff CI [0.061, 0.290], Welch df 19 |
| P3-B2 framing magnitude (ratio ≥ 1.5) | **inconclusive** | Wall Street mean exactly 0 → pre-registered edge rule (supported iff community ≥ 0.30); observed 0.175 |
| P3-B3 neutral interior | **supported** | 0.000 ≤ 0.000 ≤ 0.175 (Wall Street/neutral tie, ties allowed) |
| P3-C1 round-1 RPS distribution | **refuted** | Rock modal ✓ (0.80 vs paper 0.20, scissors 0.00); scissors < ⅓ ✓; **rock 0.80 ∉ [0.33, 0.40]** (n=80 seat decisions) |
| P3-C2 win-stay/lose-shift signature | **supported** | P(stay\|win) 0.683 CI [0.586, 0.780] > ⅓; P(shift\|lose) 0.974 CI [0.958, 0.991] > ⅔ (n=61 decisions with a usable conditional) |
| P3-C3 tracker exploits LLM beyond Nash baseline | **refuted** | **Sign reversal:** tracker per-round −0.103 vs LLM, −0.023 vs Nash baseline; diff CI [−0.133, −0.027] entirely negative |
| P3-X1 paraphrase robustness of the A-corner (extension, post-result registration — §6) | **refuted** | Round-1 cooperation **1.000** (sd=0, n=20) under **each** of two rewordings of the δ=.90 game, vs 0.000 under v1 on the same seeds — full corner flip |

Phase 3 verdict totals (main study): 3 supported · 6 refuted · 1 inconclusive. Extension X1: refuted (§6).

## 3. Study integrity

- Prompt registry: main arms pinned to `73e7a6ca…` (phase3-v1); Extension X1 arms pinned to
  `808f205a…` (phase3-v2, **append-only**: v1 prompt bytes unchanged, two paraphrase templates
  added). Replay re-renders every prompt and byte-compares per-prompt hashes (authoritative);
  whole-file registry growth is reported informationally (`registryFileDrift`), never as a
  verification failure
- Replay verification: **320 of 320** completed runs bit-exact (280 main + 40 X1, the main
  arms re-verified under the grown registry), **0 live calls**, all metric recomputations
  byte-identical to stored analyses
- δ-communication check (added in response to external review): the continuation
  probability is part of every round's subject-visible prompt — the registry template
  contains the line "After every round there is a {deltaPct}% chance the session
  continues with another round." Stored `llm.requested` events confirm the rendered
  prompts differ across arms exactly there (d90: "…a 90% chance…", d10: "…a 10%
  chance…"; engine event store, e.g. runs `run_1784875363_e3cd56da` /
  `run_1784875052_48379737`). The A-family refutations therefore measure insensitivity
  to a *communicated* incentive, not a missing information channel.
- Invalid trials: **0** of 280 (0%); replacement seeds used: 0
- Truncated horizon draws (cap 120): 0
- Budget: A 1,064/1,800 · B 120/160 · C 4,000/4,400 · X 636/1,600 · global **5,820/7,960**
  (kill-switch never approached)
- Verdict-flip audit of pre-existing claims: **no pre-existing claim changed verdict** (the
  self-play Focus = mean-of-both-seats semantics introduced for Phase 3 flipped nothing)
- Post-registration machine check: every adjudication stamps `postRegistered` by comparing
  the claim's registration timestamp to the earliest experiment cited as its evidence.
  **All 10 P3 claims and P3-X1: `postRegistered=false`** (each registered before any row it
  cites existed; X1: claim 13:18:37Z, earliest evidence 13:18:48Z);
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
3. **Extension X1 pipeline amendments** (disclosed in the pre-registration's Extension X1
   section): append-only registry versioning with per-arm sha pinning, renderer template-id
   prefix generalization, and demotion of whole-file registry drift to an informational
   replay field. After these changes all 280 original runs still replay bit-exact and no
   pre-existing verdict changed.

## 4. Findings (interpretation written after adjudication — kept separate from §5's pre-committed notes)

**Headline (finalized after Extension X1): behavior is prompt-surface-determined, not
incentive-determined.** Within the registered wording, no manipulation of *economic
structure* moved behavior at all — continuation probability across an 80-point range
and an affine payoff transform produced identically zero round-1 cooperation — while
the only within-wording treatment effect came from a two-word change in *surface text*
(the game's label). Extension X1 (§6) then showed the zero itself is a wording
artifact: two meaning-preserving paraphrases of the same δ=0.90 game flipped
cooperation from 0% to 100% with zero variance. Findings 1–5 below stand as data
about the v1 operationalization; §6 governs how far they generalize.

1. **No shadow of the future — at all.** In 160 repeated-PD supergames (320 seat
   decisions) gpt-4.1 defected in round 1 every single time, at every continuation
   probability including δ=0.90, in both payoff arms. Humans in the same designs
   cooperate 19–64% in round 1. This is not noisy under-cooperation; it is a uniform
   corner solution (sd = 0 → the adjudicator's exact-comparison path, no CI needed).
   Extension X1 (§6) later showed the corner belongs to the *wording*, not to the
   model–game pair: two paraphrases of the same game produce the opposite corner on
   the same seeds.
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
   registry is for. The reversal is structural — a deterministic exploiter is itself
   exploitable — and is not, on this evidence, deliberate opponent modeling by the
   subject.
6. **Zero variance is itself a finding (subject-pool homogeneity).** All 320 repeated-PD
   seat decisions, sampled at temperature 0.7, were identical (sd = 0). Human round-1
   cooperation in the same designs is heterogeneous — the 19–64% cross-study range
   reflects mixtures of types, and every human panel shows within-cell variance. One
   prompted LLM is *one subject replicated n times*, not a subject pool: a mechanical
   measurement of the "silicon sampling" homogeneity critique, independent of whether
   the mean is right. A4(b)'s "supported" item is the same fact wearing a different
   label — at the 0−0 floor, |canonical − isomorph| ≤ 0.15 cannot distinguish
   payoff-scale invariance from total incentive blindness, so it is disclosed as
   vacuous rather than counted as a pass.
7. **Validation consequence (negative validation).** For behavioral-proxy use, this
   configuration of gpt-4.1 is *disqualified* as a human stand-in for
   incentive-structure phenomena: A1–A4 refuted with maximal effect absence, and §6
   shows the measured level itself is a wording artifact (0% ↔ 100% under paraphrase).
   The framing result (B1) survives as a direction-only finding under its registered
   wording, with magnitude presumed wording-contingent (§6). No human response
   *distribution* is reproduced anywhere (finding 6).
8. **Follow-ups.** (a) Paraphrase robustness — run as pre-registered Extension X1;
   prediction refuted; §6. (b) A second subject population (e.g. gpt-4o, identical
   protocol plus paraphrase arms) would establish whether these results are
   model-specific or family-general — future work, not run. (c) A δ sweep under the
   v2 wordings would test whether incentive-insensitivity also holds at the
   cooperative corner — future work, not run.

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

## 6. Extension X1 — paraphrase robustness (registered post-result, pre-data; run July 24, 2026)

**Provenance.** Registered *after* the main results were known and *before* any extension
row existed (claim 13:18:37Z, earliest evidence 13:18:48Z, machine-stamped
`postRegistered=false`); the disclosure of its post-result status is part of the registered
claim text and of the pre-registration's Extension X1 section. The claim statement
pre-committed the interpretation of both outcomes — including that refutation "would
overturn the report's incentive-insensitivity reading of A1–A3; it will be disclosed as
such." That clause is now in force.

**Design.** Two meaning-preserving rewordings of the repeated-PD prompt at δ=0.90:
`pd-repeated-v2a` (continuation rule stated first; "pick"/"another person" register) and
`pd-repeated-v2b` (compact `J+J / J+F / F+F` outcome notation; "probability 90 in 100").
Same payoffs, same J/F action letters, same δ, same seeds 1–20, and horizons matched
draw-for-draw to the canonical δ=.90 arm (identical mulberry32 stream → 159 total rounds
per arm). Registry `phase3-v2` is append-only (v1 prompt bytes unchanged, sha-verified);
40 runs, 636 calls, 0 invalid, 40/40 replay-verified bit-exact with 0 live calls.

**Result — prediction refuted at the opposite corner.** Registered prediction: round-1
cooperation ≤ 0.05 under both rewordings. Observed: **1.000, sd = 0, under each** (n=20
per arm; exact comparison). Exploratory (not adjudicated): the flip is not a round-1
artifact — **all 159 rounds of both arms are mutual cooperation** (overall cooperation
100.0% vs 0.31% under v1 on the identical seeds; v1 mutual-cooperation rate 0.000).

**What this overturns, per the pre-committed rule.** Any reading of A1–A4 as a
disposition of gpt-4.1 toward the *game* ("never cooperates", "ignores the shadow of the
future" simpliciter). The corner solution is a property of one prompt operationalization.

**What survives.** (i) Every A-family verdict as registered — each is a claim about
behavior under the v1 wording, where δ was swept 0.10→0.90 and nothing moved. (ii) The
δ-communication integrity check (§3): the incentive was demonstrably in the prompt in
every arm, including both v2 arms. (iii) Finding 6, reinforced and now bidirectional:
sd = 0 at *both* corners — the subject is behaviorally deterministic at temperature 0.7
under every wording tested, unlike any human panel. (iv) The replay/verification
pipeline itself (320/320 bit-exact).

**Scope note (asymmetry of evidence).** δ-flatness is certified across four δ levels
under v1 but only at δ=.90 under v2a/v2b — the extension registered a single-δ scope.
Whether the cooperative corner is equally δ-flat is an open, registered follow-up
(§4, finding 8c).

**No mechanism claim.** The arms differ simultaneously in ordering, register, and outcome
notation; the design cannot attribute the flip to any single element, and none is claimed.

**Methodological consequence (sharpened validation lesson).** A quantitative behavioral
claim about an LLM subject made under a single prompt operationalization is unidentified:
the measured rate swung the full [0, 1] range under meaning-preserving rewording while
every economic variable was held fixed. This retroactively caveats B1's magnitude (§4,
finding 7) and makes paraphrase-robustness arms a standing requirement for any future
phase of this lab.
