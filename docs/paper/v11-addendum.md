# v11 addendum to the v10 scientific text freeze

> **STATUS: POST-FREEZE REVIEW ADDENDUM.** The immutable v10 artifact remains tagged `paper-text-freeze-v10`. v11 is a new manuscript version created in response to the subsequent Explore Science review. It does not revise any sealed experimental artifact or historical mechanical verdict.

## Why a new version was required

Most review items were reporting and figure changes, but one critique identified a genuine uncertainty-model boundary: the v10 fixed-panel episode bootstrap resampled empirically unanimous six-episode cells as point masses. That interval is valid for a conditional empirical-distribution estimand, but it is not a complete uncertainty statement about latent prompt policies.

v11 therefore adds a **fixed-panel latent-propensity sensitivity**. Each prompt/cell’s probabilities over episode outcomes `{0, 0.5, 1}` receive an independent Dirichlet(0.5, 0.5, 0.5) prior. Posterior draws propagate uncertainty from boundary-concentrated cells while retaining the exact sixteen-prompt panel. The analysis is post-adjudication and cannot alter the frozen P5-1b verdict.

## Scientific interpretation change

- v10 plug-in point estimates assign 85%–96% of observed episode-level variation between prompt configurations.
- v11 latent-propensity posterior medians are 63%–71%, with 95% intervals spanning approximately 49%–81%.
- The revised claim is therefore: **between-prompt composition is substantial and likely dominant in this fixed panel; 85%–96% are conditional plug-in point estimates, not fully uncertainty-adjusted population facts.**

## Reporting changes

v11 also makes every load-bearing denominator and anchor self-contained in the paper: human SD references and thresholds, the cooperation band and failing cell, all six conditions, the restricted 32-cell set, P5-2 counts, the 24 temperature lanes, the S2 sentence, and the exact Dirichlet prior.

## Freeze rule

The v10 tag and files remain unchanged. The v11 source, PDF, checksum, analysis outputs, review report, and validation record form a separate review package. Any later scientific change requires v12 or an explicit addendum.