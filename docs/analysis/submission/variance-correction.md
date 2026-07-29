# Finite-opportunity correction for between-prompt dispersion

> **STATUS: POST-ADJUDICATION SENSITIVITY — ZERO SUBJECT CALLS.** Historical P5-1b point comparisons are unchanged. This analysis treats complete episodes as repeated measurements, subtracts the estimated sampling contribution from the variance of persona means, and uses a hierarchical bootstrap over personas and episodes.

## Estimator

For each repeated-game cell, the raw variance of estimated persona means is decomposed as `Var_i(p_hat_i) ≈ B + mean(s_i²/n_i)`. The corrected between-prompt component is `max(0, raw variance − estimated measurement noise)`. `W` is the average within-prompt variance of the episode-level outcome. The bootstrap resamples personas and then episodes within persona.

Bootstrap replicates: **50,000**.

| cell | raw SD | corrected SD | bootstrap corrected SD 95% | within variance W | between share B/(B+W) | historical 0.75×human-SD threshold | point meets? |
|---|---:|---:|---|---:|---|---:|---|
| rep-d10-s2a | 0.4241 | 0.4182 | [0.2703, 0.4876] | 0.0297 | 0.85488 | 0.3091 | yes |
| rep-d10-s2p | 0.4800 | 0.4784 | [0.3643, 0.5123] | 0.0094 | 0.960651 | 0.3091 | yes |
| rep-d90-s2a | 0.4454 | 0.4408 | [0.3466, 0.4892] | 0.0245 | 0.888095 | 0.2337 | yes |
| rep-d90-s2p | 0.4362 | 0.4323 | [0.3358, 0.4854] | 0.0203 | 0.901955 | 0.2337 | yes |

## Interpretation

The corrected quantities estimate heterogeneity among these fixed prompt configurations at the episode-outcome level. They are not protocol-matched human latent variances, do not justify a persona-population claim, and do not remove the need to label the Dal Bó–Fréchette comparator as nonmatched.

Machine-readable results: `figure-sources/variance-correction.csv` and `.json`.
