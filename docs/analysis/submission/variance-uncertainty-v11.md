# v11 fixed-panel latent-propensity variance sensitivity

> **STATUS: POST-v10, POST-ADJUDICATION SENSITIVITY — ZERO SUBJECT CALLS.** The registered P5-1b verdict and v10 point estimates are historical and unchanged. This analysis addresses uncertainty suppressed when empirical boundary cells are resampled as point masses.

For each prompt/cell, the three episode-outcome probabilities for `{0, 0.5, 1}` receive an independent Dirichlet(0.5, 0.5, 0.5) prior. Across **100,000** posterior draws, the script computes prompt-specific latent means, between-prompt SD, expected within-prompt variance, and the between share `B/(B+W)`. This keeps the exact sixteen-prompt panel fixed; it does not resample a persona generator.

| cell | observed corrected SD | latent SD 95% (median) | observed between share | latent between-share 95% (median) | historical threshold SD |
|---|---:|---|---:|---|---:|
| rep-d10-s2a | 0.4182 | [0.3090, 0.3886] (0.3543) | 0.855 | [0.494, 0.745] (0.631) | 0.3091 |
| rep-d10-s2p | 0.4784 | [0.3521, 0.4308] (0.3959) | 0.961 | [0.573, 0.813] (0.705) | 0.3091 |
| rep-d90-s2a | 0.4408 | [0.3253, 0.4060] (0.3698) | 0.888 | [0.528, 0.770] (0.661) | 0.2337 |
| rep-d90-s2p | 0.4323 | [0.3179, 0.3970] (0.3620) | 0.902 | [0.528, 0.777] (0.665) | 0.2337 |

The conditional episode bootstrap, this latent-propensity posterior, and the two-stage prompt+episode bootstrap answer different questions. None is promoted retroactively into the frozen confirmatory rule.
