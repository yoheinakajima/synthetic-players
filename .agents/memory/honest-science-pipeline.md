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
