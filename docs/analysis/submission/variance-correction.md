# Finite-opportunity correction for between-prompt dispersion

> **STATUS: POST-ADJUDICATION SENSITIVITY — ZERO SUBJECT CALLS.** Historical P5-1b comparisons are unchanged. The primary estimand is the dispersion among these sixteen fixed prompts. Primary uncertainty therefore resamples episodes within each prompt while retaining all sixteen prompts. A second two-stage bootstrap that also resamples prompts is reported only as exploratory persona-population uncertainty.

## Estimator

For each repeated-game cell, `Var_i(p_hat_i) ≈ B + mean(s_i²/n_i)`. The corrected fixed-panel between-prompt component is `max(0, raw variance − estimated measurement noise)`. `W` is the average within-prompt variance of the episode-level outcome. Bootstrap replicates: **50,000** for each estimand.

| cell | corrected SD | fixed-panel episode-bootstrap 95% | between share B/(B+W) | fixed-panel between-share 95% | historical 0.75×human-SD threshold | point meets? |
|---|---:|---|---:|---|---:|---|
| rep-d10-s2a | 0.4182 | [0.4122, 0.4391] | 0.855 | [0.820, 0.938] | 0.3091 | yes |
| rep-d10-s2p | 0.4784 | [0.4696, 0.4916] | 0.961 | [0.946, 0.989] | 0.3091 | yes |
| rep-d90-s2a | 0.4408 | [0.4279, 0.4654] | 0.888 | [0.867, 0.946] | 0.2337 | yes |
| rep-d90-s2p | 0.4323 | [0.4269, 0.4496] | 0.902 | [0.879, 0.955] | 0.2337 | yes |

## Estimand boundary

The fixed-panel intervals quantify episode-sampling uncertainty for these exact prompts. The wider two-stage intervals in `figure-sources/variance-correction.csv` additionally resample prompts and are exploratory statements about a hypothetical persona generator. Neither is a protocol-matched human latent-variance comparison.

Machine-readable results: `figure-sources/variance-correction.csv` and `.json`.
