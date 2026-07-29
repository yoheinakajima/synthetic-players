> **Phase 3 report (as sealed) [CONFIRMATORY] (source: engine records, Phase 3)**

# Can an LLM Serve as a Behavioral Subject? — Phase 3 Report of a Preregistered Validation Study in Strategic Games

**Study:** pre-registered in [`phase3-preregistration.md`](phase3-preregistration.md) (claims registered before any data; registry sha pinned).
**Subject:** `gpt-4.1` via Replit AI Integrations, temperature 0.7, maxTokens 16, engine-live event-sourced path.
**Status:** COMPLETE (July 24, 2026), plus post-review **Extension X1** run the same day (§6) —
its result **overturns the generality of the A-family interpretation** under the extension's own
pre-committed disclosure rule. All numbers below are transcribed from the mechanical adjudication
output (`node scripts/run-phase3.mjs adjudicate`); verdicts were never hand-set.
**Corpus:** 320 LLM experiments (160 A + 60 B + 60 C + 40 X1) + 20 zero-LLM baseline runs, 5,820 LLM calls.

## 1. Design summary

Three families, 20 **environment-seeded episodes with archived model draws** per
cell (environment RNG — horizons, schedules — is seeded and reproducible;
provider-side sampling was not seeded and is archived, not re-drawable), all
claims adjudicated mechanically against pre-registered predicates (95% Welch
CIs unless a point comparison was pre-registered). Each registered verdict now
carries an **estimand-aware statistical companion** —
[`phase3-layer2.md`](phase3-layer2.md), added 2026-07-24 post-hoc and labeled —
that supplies run-level Clopper-Pearson bounds for corner cells, cluster-aware
intervals, and a unit-of-analysis accounting for every claim. Registered
verdicts are never altered by that layer:

- **A — Shadow of the future.** Random-termination repeated PD (continuation
  probability δ ∈ {.10, .50, .75, .90}), LLM self-play, canonical payoffs
  (3,0,5,1) plus an affine isomorph (×3+2) as a contamination probe. Horizons
  drawn client-side from a seeded geometric (mulberry32, safety cap 120,
  hidden from the subject). Primary statistic: round-1 cooperation.
- **B — Framing.** One-shot PD labeled "Community Game" / "Wall Street Game" /
  neutral, self-play pairs, n=20 per framing.
- **C — Mixed-strategy play.** RPS, 50 rounds: vs pattern-tracker, vs
  nash-mixed, self-play; plus a zero-LLM pattern-tracker-vs-nash-mixed
  baseline for the registered comparison of the tracker's performance across
  opponents (all such results are reported as "performance against the
  registered first-order tracker", never as unqualified exploitability).

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

**Headline (finalized after Extension X1): prompt wording dominated the tested
incentive manipulation and rendered single-wording behavioral inference
non-identifiable.** Within the registered wording, no manipulation of *economic
structure* moved behavior at all — continuation probability across an 80-point range
and an affine payoff transform produced identically zero round-1 cooperation — while
the only within-wording treatment effect came from a two-word change in *surface text*
(the game's label). Extension X1 (§6) then showed the zero itself is wording-bound:
under two meaning-preserving paraphrases of the same δ=0.90 game, all 20 recorded
episodes began with cooperation, versus all 20 beginning with defection under v1 on
the same seeds. For this fixed deployment and task, a single prompt therefore
identifies the behavior of that prompt–model configuration, not a
representation-invariant behavioral property of the model. This does **not**
establish that incentives cannot matter under other wordings — X1 tested one
incentive level under two rewordings; whether incentive sensitivity reappears away
from the corners is exactly what Phase 4's D2 and E are registered to test.
Findings 1–5 below stand as data about the v1 operationalization; §6 governs how far
they generalize.

1. **No round-1 cooperation observed under any tested δ in this configuration.** In
   160 repeated-PD supergames (320 seat decisions) gpt-4.1 defected in round 1 every
   single time, at every continuation probability including δ=0.90, in both payoff
   arms. Humans in the same designs cooperate 19–64% in round 1. As a corpus
   statement this is exact (sd = 0 → the adjudicator's exact-comparison path); as a
   policy statement each all-zero cell bounds the true rate at ≤ 16.8% (run-level
   two-sided 95% Clopper-Pearson, 20 episodes; pooled high-δ cells ≤ 8.8% —
   layer 2, §1).
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
5. **The tracker got out-tracked.** The pre-registered hypothesis about performance
   against the registered first-order tracker reversed sign: the tracker *lost* 0.103/round against the LLM
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

**Provenance.** X1 is a **result-informed but prospectively registered extension**: it
was conceived after the Phase 3 main results were known, its direction and thresholds
were committed before any extension data existed, and it was then executed. Exact
chronology (claims store): claim registered **2026-07-24T13:18:37.243Z**; earliest X1
evidence row **2026-07-24T13:18:48.145Z**; adjudicated 13:25:55.151Z. The adjudicator's
machine-stamped `postRegistered=false` means precisely that ordering check passed — *no
evidence row cited by the claim predates the claim's registration* (the flag name refers
to registration-after-evidence, which did not occur). The disclosure of its post-result
conception is part of the registered claim text and of the pre-registration's Extension
X1 section. The claim statement
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
cooperation ≤ 0.05 under both rewordings. Observed: **all 20 recorded episodes began
with cooperation under v2a, and all 20 under v2b** (episode-level rate 1.000, sd = 0;
exact comparison), versus all 20 episodes beginning with defection under v1 on the same
seeds. At the episode level the corners carry two-sided 95% Clopper-Pearson bounds of
[0.832, 1] (20/20) and [0, 0.168] (0/20) on the underlying policy rates — the recorded
corpus is exact, the policy is bounded, not proven degenerate (layer 2, §1). Exploratory
(descriptive, trajectory-level; the 159 within-arm rounds are serially nested within 20
episodes and are not treated as independent observations): **every recorded round of
both v2 arms is mutual cooperation** (all-round cooperation 100.0% vs 0.31% under v1 on
identical seeds; v1 mutual-cooperation rate 0.000).

**What this overturns, per the pre-committed rule.** Any reading of A1–A4 as a
disposition of gpt-4.1 toward the *game* ("never cooperates", "ignores the shadow of the
future" simpliciter). The corner solution is a property of one prompt operationalization.

**What survives.** (i) Every A-family verdict as registered — each is a claim about
behavior under the v1 wording, where δ was swept 0.10→0.90 and nothing moved. (ii) The
δ-communication integrity check (§3): the incentive was demonstrably in the prompt in
every arm, including both v2 arms. (iii) Finding 6, reinforced and now bidirectional:
sd = 0 at *both* corners — every recorded episode is identical within each tested
wording, unlike any human panel. (This is a statement about the recorded corpus; the
underlying stochastic policy is not thereby proven deterministic — its rates are
bounded by the episode-level intervals above.) (iv) The replay/verification
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
every economic variable was held fixed. Any behavioral claim intended to generalize
beyond its exact prompt requires representation-robustness evidence. This retroactively
caveats B1's magnitude (§4, finding 7) and makes paraphrase-robustness arms a standing
requirement for any future phase of this lab.

**X1 disclosure documents** (added per external methods review, 2026-07-24):
complete serialized bundles with differing spans and invariance table —
[`phase4/x1-prompt-disclosure.md`](phase4/x1-prompt-disclosure.md); full parser audit
(every unique raw completion, frequencies, mappings, one complete transcript per arm,
zero retries) — [`phase4/x1-parser-audit.md`](phase4/x1-parser-audit.md);
semantic-equivalence audit instrument and status —
[`phase4/x1-semantic-equivalence.md`](phase4/x1-semantic-equivalence.md).

## 7. Run provenance (machine-extracted from the event store)

- **Model revision:** all **5,830** stored `llm.responded` events across every arm
  (including X1) returned `gpt-4.1-2025-04-14`; finish reason `stop` on all 5,830.
- **Decoding parameters:** temperature 0.7 and maxTokens 16 on all 5,830 stored
  `llm.requested` events; no provider-side seed parameter was sent (`seed: null`) —
  hence "archived model draws", not "seeded generations".
- **Rendered prompts:** the complete system and user messages of every call are archived
  verbatim in `llm.requested` events and byte-verified on replay against the sealed
  registry (per-prompt sha).
- **Raw completions:** archived verbatim (`raw_text`) for all calls; the X1 arms'
  complete inventories are published in the parser audit.
- **Known gap (disclosed):** provider response IDs were not captured in Phase 3
  (`provider_meta` is empty on all events); the provider route is recorded only as the
  single configured Replit AI Integrations endpoint. Response-ID and route capture are
  mandatory engine work before any Phase 4 run (freeze packet, provider section).
- **Parser version:** Phase 3's parser is pinned by code commit (no explicit version
  constant existed); an explicit `PARSER_VERSION` stamp is Phase 4 engine work.

## 8. Positioning and scope of claims

**Related work (descriptors; exact citations to be finalized in the manuscript).** A
2025 Nature Human Behaviour study of repeated-PD play with LLM agents and a 2026
five-model one-shot/repeated-PD preprint report game-theoretic behavioral signatures for
LLMs [REF]; a workshop line on counterfactual game variants probes whether models follow
payoffs or memorized game frames [REF]. This project's contribution is orthogonal to
"how do LLMs play": it is a **validation and audit protocol** — pre-registered
machine-adjudicated claims, sealed prompt registries with per-arm hash pinning,
zero-live-call byte-exact replay, and representation-robustness testing as a
registration requirement — plus a boundary study showing why the protocol is necessary
(X1's full-range corner flip under meaning-preserving rewording).

**What this report claims.** For this fixed GPT-4.1 deployment and these tasks: the
registered verdicts of §2; the layer-2 bounds of `phase3-layer2.md`; and X1's
demonstration that single-wording behavioral inference is non-identifiable here.

**What this report does not claim.** That LLM behavior is incentive-insensitive in
general (untested away from the corners; Phase 4 D2/E); that any specific prior study is
invalid (no such study was audited here — single-wording designs leave
representation-general claims unidentified *unless they provide equivalent robustness
evidence*, which is a property to be checked per study, not presumed absent); and that
any human-substitution question is answered (no human data exists in this project; the
substitution estimand is registered and pending —
[`substitution-estimand-preregistration.md`](substitution-estimand-preregistration.md)).

**Closing claim.** A highly auditable LLM deployment produced stable, interpretable
behavioral signatures, failed the preregistered incentive-sensitivity and
human-reference tests under its registered wording, and revealed through a prospectively
registered extension that the measured corner itself was wording-bound — demonstrating
why subject substitution must be validated per model-policy, task, and estimand, with
the matched human comparison registered and pending, not run.
