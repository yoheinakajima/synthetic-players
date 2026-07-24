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
