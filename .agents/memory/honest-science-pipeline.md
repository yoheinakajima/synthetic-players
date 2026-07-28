---
name: Honest science pipeline
description: Lessons from v1→v2 of the game theory lab — how research claims went wrong and the pipeline design that fixed them
---

# Honest science pipeline

**Rule.** In any experiment/claims/paper system: (1) claims are structured,
machine-checkable predicates; (2) verdicts come from an adjudicator that reads
only the predicate and the data, never the prose; (3) any stochastic process
gets a stored RNG seed and N-seed replicates, and claims are judged against
95% CIs, with "inconclusive" as a first-class outcome; (4) refuted claims stay
visible with their evidence — never reworded or re-thresholded after seeing
data (HARKing).

**Why:** v1 of the lab (July 2026) called 11/11 claims "supported". Mechanical
re-adjudication sustained 6, refuted 1, and found 4 inconclusive. The refuted
one had transplanted a literature result (Axelrod tournament aggregate) onto a
dyadic experiment whose own data showed the opposite (2% vs claimed >50%) —
written from memory of the literature instead of from the rounds table.
Author-assigned verdicts drift optimistic; single unseeded runs of stochastic
strategies produced "crisp" claims whose CIs actually straddle the threshold.

**How to apply:** when building anything that generates claims/conclusions from
data (papers, dashboards, reports), push for: predicate encoding at claim
creation time, a mechanical adjudication endpoint, seeds stored on every run,
replicate batches for anything random, and an errata/postmortem section that
ships with the output. Deterministic evidence (sd=0) gets exact comparison;
sampled evidence gets CI-vs-threshold.

**Fork/counterfactual runs are not evidence.** What-if runs (forked histories,
mid-run strategy swaps) have hybrid histories — exclude them from every
evidence surface (analyses, aggregates, leaderboards, adjudication) and study
them via paired parent-vs-fork comparison over the shared post-fork window.

**Merges can silently undo honesty constraints.** A parallel branch's codegen
regenerated from an older spec re-added a removed "author can set verdict"
field; the runtime guard held, but spec and generated types contradicted it.
After any merge, re-verify honesty-critical schema constraints and re-run
codegen from the merged spec.

**Growing evidence after a verdict is legitimate; touching thresholds is not.**
Adding replicates to tighten a straddling CI (inconclusive → supported/refuted)
is the pre-registered predicate doing its job. New experiments that match an
old claim's declared scope also legitimately enter its evidence pool and can
flip its verdict — audit every flip (check evidence id ranges) and disclose it;
a silent flip looks like tampering even when it isn't.

**Refuting your own prediction is the system working.** A "generosity rescues
cooperation ≥80%" claim came back refuted at 62.8% CI [49.3, 76.3] (n=20):
stochastic forgiveness sometimes re-triggers defection spirals. Keep such
refutations prominent — they are the credibility proof of the pipeline.

**Near-identical replicates need an sd epsilon.** Byte-identical runs can leave
sd ≈ 1e-18 from float accumulation; a t-CI over that degenerates and Cohen's d
explodes to ~1e17. Route sd below ~1e-12 to the exact-comparison path and
suppress effect size there.

**Sampled agents (LLM seats) are event-sourced, never seed-reproduced.** When a
decision-maker can't be replayed from a seed (provider pins sampling), record
every decision (action + stated reasoning) and re-materialize it on the
authoritative engine as scripted events, verified byte-exact against the live
loop before persisting. Never leave an event-sourced seat in place on a fork —
replaying its log against a changed history fabricates decisions it never made
for that context. Expect **bimodal** behavior across replicates (e.g. one run
95% cooperative, the next 0%): wide CIs and inconclusive verdicts are honest
outcomes, not pipeline failures.

**Pre-registration must be enforced by the script, not by discipline.** The
study runner's claims step aborts if target batches already contain data and
its runs step aborts if the claims aren't registered — ordering violations
fail loudly instead of silently becoming HARKing.

**Infrastructure duplicates get an outcome-blind exclusion rule.** When a race
creates two replicates for one design slot (same seed/label), decide by a rule
fixed before looking at results — e.g. "first completedAt wins; relabel the
other to an overflow batch with a note". Deleting nothing, disclosing the
relabel, and never choosing by outcome keeps the evidence set defensible.

**Idempotent create must reconcile config, not just return the old row.** A
create-on-conflict path that silently returns the existing row will resurrect a
*stale protocol* (old temperature/prompt version) when a rerun submits a
revised one — the run then executes under parameters nobody registered. Rule:
for rows with no data yet (pending/failed), adopt the newly submitted config
and say so; for rows with data (completed/running/invalid), refuse loudly on
any mismatch instead of picking either side.

**Pre-registration promises must be machine-checked, not procedural.** A
prereg doc that promises adjudicator-level enforcement the code doesn't
implement is an erratum waiting for a reviewer. Now enforced: every
adjudication stamps `postRegistered` (claim createdAt vs earliest cited
evidence createdAt) and predicates lock (409) after first adjudication.
**Why:** post-study review found the gap; fixed + disclosed as an amendment.
**How to apply:** when a protocol doc says "X is enforced", grep for the
enforcement code before running the study.

**Design edge rules — they fire.** A pre-registered ratio predicate hit its
denominator-exactly-zero case in the very first study using it (a framing cell
with 0% cooperation). Without the pre-registered "supported iff numerator ≥
floor" rule the item would have needed a post-hoc decision — which is HARKing.
Any ratio/normalized predicate needs its degenerate cases decided at
registration time. Corollary: subjects can produce *uniform corner solutions*
(every replicate identical, sd = 0), so difference-of-means predicates must
route degenerate variance to exact comparison rather than dividing by zero.

**Spend budgets must count failures and invalid trials.** Recompute spend from
stored per-run call counts (all statuses) rather than trusting the runner's
in-memory tally: invalid trials burn real calls, and any run that fails
*client-side* while the server continues would otherwise spend invisibly. Keep
client timeouts far above worst-case run duration so "failed but still
spending" cannot happen, and make the kill-switch a DB-derived check before
every run, not a counter.

## Paraphrase arms are mandatory for LLM-subject claims

A corner solution observed under one prompt wording is not a behavioral disposition
of the model. Phase 3's universal-defection result (0%, sd=0, 160 supergames) flipped
to universal cooperation (100%, sd=0) under two meaning-preserving paraphrases of the
same game — economics held fixed, only surface text changed.

**Why:** the measured rate of any LLM "behavior" can swing the full [0,1] range under
rewording, so a single-operationalization claim is unidentified. Zero variance at a
corner is a warning sign, not extra certainty.

**How to apply:** any study measuring LLM behavior must include ≥2 registered paraphrase
arms before interpreting a level or a null; write the disclosure commitment for a
refuted robustness prediction into the claim statement itself (pre-authorizes the
interpretive overturn, no scramble later).

## Append-only prompt registries for study extensions

Extending a sealed study's prompt registry: append new templates without touching old
bytes, pin per-arm registry shas (old arms keep old sha), have replay re-render and
hash-compare each prompt actually used (authoritative), and report whole-file registry
growth as an informational drift field rather than a verification failure.

**Why:** a whole-file sha check would falsely fail every sealed run after any append,
forcing a choice between skipping verification and forking the registry; per-prompt
byte checks keep the original evidence bit-exact-verifiable forever.

**How to apply:** when a study needs new prompts post-seal, bump the registry version
string, append templates, record both shas in the prereg amendment, and re-verify the
full old corpus replays green before running new arms.

## Gate-reversion discipline (gate-reversion)
When a pre-set design gate fails by a hair (F stabilization: |Δstay|=0.0512 vs 0.05 threshold), follow the registered reversion rule and report the margin — never round, re-window, or argue the gate away. The near-miss itself goes in the packet.

## Freeze-packet pattern
One generator materializes ALL templates/arms/seeds/schedules with **byte-exact endpoint assertions** (derived artifacts must reproduce sealed originals); manifests are machine-written and prose docs quote manifest values — never hand-copied SHAs, seeds, or counts (a hand-quoted seed range contradicted the sealed manifest and was caught only in review). Append-only guard: hash sealed entries pre/post write with a RECURSIVE canonical serializer (key-whitelist JSON.stringify silently drops nested objects from hashed material) and abort on drift.

## Cross-vendor subject gates (behavioral fit, not just connectivity)
A cross-vendor candidate must pass a Gate-0-style *behavioral* check under the exact
frozen protocol before any experimental row: bare-format compliance at the protocol
token cap on attempt 0, clean stop per a registered cross-vendor stop mapping,
response IDs + token accounting, and (for hybrid-reasoning models) zero hidden
reasoning tokens asserted per call.

**Why:** claude-haiku-4-5 accepted the request parameters but could not complete a
turn at maxTokens=16 (chain-of-thought prose, truncation even at 64 tokens). Its
rescue-by-retry would have injected the retry suffix into nearly every effective
stimulus while the primary subject never saw it — a model×stimulus confound that
silently breaks matched-stimulus designs.

**How to apply:** when a candidate fails behaviorally, escalate with a small logged
diagnostic (natural reply at a larger cap) and switch candidates via a registered
amendment rather than forking the elicitation protocol per vendor. Archive the failed
round's machine report under a new name before rerunning (living report files get
overwritten), run a fresh gate round for the new candidate, and have the amendment
state what changed AND what verifiably did not (prompt registry byte-identical, seeds/
schedule/budgets unchanged), with the verification run before the claim is written.

## Budget projections from ledger prices, never design-unit counts (2026-07-25)
Price every forward projection from the event store's recorded cost per unit
(calls per episode as dispatched), not from design units (episodes, cells,
checks). **Why:** a registered cap amendment was itself mispriced 2× — sentinel
episodes are self-play (two subject seats = two calls each), the driver's
"10/10" tallies count episodes not calls, and the error surfaced only when live
spend outran the projection; no cap was violated purely by ordering luck. A
same-day correcting amendment was required. **How to apply:** before
registering any cap or amendment, query the ledger for the realized unit price
of that exact block type; cross-check that sealed group caps reproduce from
ledger arithmetic (seats × rounds × episodes).

## Failure rules by store signature, not by cause (2026-07-25)
Write data-validity rules against event-store signatures ("attempt without
`run.completed` = disclosed non-observation; the completed re-run is the
observation; duplicate COMPLETED runs still refuse; absence still refuses"),
never against failure causes. **Why:** a rule registered for a provider-429
partial applied unchanged an hour later to a container-death partial — same
signature, different cause, zero amendment needed. Cause-based wording would
have forced a mid-data rule change. Keep failed attempts in the append-only
store as the disclosure trail and surface them in reports; at-most-once
inflight markers + event-store reconcile make killed-mid-episode dispatch
recoverable, with marker clearance as a ledgered manual act.

## Capture honesty: mirror-vs-actual sha seam (2026-07-24)
Provenance shas of provider requests must be computed TWICE from independent code
paths: a runner-side mirror (from protocol fields) recorded in the request event, and
a provider-side actual (from the kwargs really sent) in provider_meta; assert equality
on every call and hard-abort on divergence. **Why:** a single computation can drift
from the wire silently — the seam makes capture self-verifying. **How to apply:** any
new provider adapter must populate `provider_meta.request_body_sha256` from its actual
sent fields (transport/timeout excluded); replay recomputes the mirror side only.

**Console counts are not rule evaluations.** A dispatcher's "N/N" progress
line proves episodes completed, nothing else. Every registered decision rule
must be executed by its registered evaluator at its registered checkpoint,
and the evaluator's exit code — not any log line — is the record. If a rule
evaluation is manual, wire it into the dispatcher so it cannot be skipped
under operational churn (that skip happened once: two fired sentinel checks
were logged as clean from progress prints).

**Every sealed rule must exist in all three layers.** If a registered rule
is implemented at dispatch/enforcement but not in the replay checker (or
vice versa), the audit fails on good data — or worse, passes bad data. When
adding any conditional dispatch behavior (resolutions, switches, donor
substitutions), grep the replay/verification path for the same rule before
sealing. Two instances so far: sentinel third-cell switch deltaPct, and the
1-based schedule ep vs 0-based seeds array.

**Phase 5 packet stage:** entry mechanisms live — `engine/freeze_lint.py`
(seal gate; manifest-driven; acceptance selftest reproduces the 5 sealed-text
instances + fail-closed shape/coverage, 8/8), `engine/watchdog.py`
(auto-resume ONLY for `resume-signatures.json` matches; scientific freezes
stay manual), `engine/phase5_budget.py` (all prices from budget.db per-run
actuals). Personas: seeded mulberry32, full trait cross, banned-word guard,
leaning fixed at generation. Discussion branches pre-committed in
docs/paper/ before dispatch; linter C5 requires branch per verdict combo.

## Seeded call tables must be exact (Phase 5 amendment 1 lesson)
For seeded designs, compute sealed budget/call tables from the EXACT seeded
horizon draws at freeze time — never from per-episode averages of a prior
phase. **Why:** Phase 5 caps were priced from Phase 4 ledger averages (~7.4
rounds mean at δ=0.90) while the actual seed lanes drew 12.4; every cap group
bound at preflight and the registered shed order couldn't clear it, forcing a
pre-data operator amendment. **How to apply:** at freeze, sum 2×drawn horizon
over the schedule per cap group; make the seal linter check the call table
against the schedule's draws.
