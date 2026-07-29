# Round 2 — adversarial methods and framing review

> **STATUS: REVIEW SUMMARY, 2026-07-29.** This is a faithful summary of the review that generated the zero-call submission queue. It is not a sealed registration and does not imply that the resulting post-adjudication analyses were preregistered.

## Principal findings

### 1. The broad novelty claim was occupied

The review verified that Li and Ji had already demonstrated at scale that statistical realism need not predict treatment-effect accuracy. Persson and colleagues formalized the causal-surrogacy assumptions, and Lin and colleagues showed that interventions can change the implied latent user even when an explicit persona is fixed.

**Disposition:** reposition around one concrete mechanism-level pattern in strategic interaction rather than a first-demonstration claim. Treat latent-user drift as potentially coexisting, not ruled out.

### 2. The published human comparator was not protocol-matched

Dal Bó–Fréchette used different continuation probabilities, payoffs, monetary incentives, between-session assignment, and repeated-supergame experience. The pooled human contrast could not serve as a matched response target, and first-supergame ordering reversed.

**Disposition:** retire “δ-matched,” “fivefold,” and “one-fifth human response.” Keep the comparator contextual and make the internal fixed-panel contrast load-bearing.

### 3. The p13 existence claim lacked family-level error control

The frozen rule tested many persona × wording candidates and fired on any pass using per-candidate inference. Preregistration prevented outcome-driven choice of p13 but did not control the existence claim's family error.

**Disposition:** preserve the historical mechanical verdict, downgrade p13 to a replication target, publish every candidate, and run post-adjudication family sensitivities without treating them as prospective confirmation.

### 4. Seat-level intervals were nested within episodes

Several historical intervals counted two seat choices per episode even though the seats share an episode-level environment. That could be anti-conservative under positive dependence.

**Disposition:** preserve the registered seat-level calculation as history and recompute all load-bearing quantities using complete episodes as the unit. Report interval-method sensitivity rather than selecting the favorable construction.

### 5. The moment argument needed an identity correction

Exact condition-specific mean matching necessarily recovers the aggregate mean difference by the identity \(\Delta=\mu_1-\mu_0\). The empirical critique therefore applies to broad bands and other coarse checks, not exact mean matching.

**Disposition:** formalize partial identification under accepted bands; separately formalize what condition-specific moments and marginals fail to identify about decomposition, shape, and cross-condition coupling.

### 6. Raw between-persona variance included estimation noise

Variance across estimated prompt means combines genuine between-prompt dispersion with finite-opportunity noise.

**Disposition:** perform a fixed-panel correction and episode bootstrap; reserve persona-population language for an exploratory prompt-resampling sensitivity.

### 7. The manuscript contained three competing papers

The draft mixed a synthetic-subject validity paper, a behavioral control-channel paper, and an autonomous-research pipeline paper.

**Disposition:** one claim, one mechanism, one credibility layer:

- claim: coarse checks pass while observed incentive response is small;
- mechanism: composition across concentrated prompt-conditioned policies plus representation dependence;
- credibility: registration, event sourcing, adjudication, replay, and correction.

## Zero-call analysis queue specified by the review

1. Episode-level sensitivity for P5-1a, the p13 gates, P5-2, and clause (b).
2. A high-precision familywise p13 audit with identical observed/permuted statistics.
3. A between-prompt variance correction with fixed-panel and persona-population uncertainty separated.
4. Full count reconciliation.
5. Dal Bó–Fréchette microdata contextualization if licensed data became available.

The first four were later executed against archived databases by GitHub Actions. The fifth remains deferred because the official package is login-gated and is nonblocking under the narrowed internal claim.

## Enduring methods lesson

> Exact enforcement of a registered predicate is not proof that the predicate defines a valid estimand, family, or construct.

The review's highest-value contribution was not changing a number. It located where procedural exactness stopped short of statistical validity and left enough provenance for the correction to be made without rewriting history.
