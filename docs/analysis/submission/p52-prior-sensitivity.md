# P5-2 fixed-panel prior sensitivity

> **STATUS: POST-ADJUDICATION, ZERO-CALL SENSITIVITY.** Historical adjudication unchanged.

Each of the 40 sparse persona × conflict-cell clusters receives an independent symmetric Dirichlet(alpha, alpha, alpha) prior over episode outcomes {0, 0.5, 1}. The aggregation weights each cluster by its archived episode count. At alpha=0.5, total prior concentration is 1.5 per cluster, or 60 category-count units across 40 clusters; because cluster sizes are unequal, this is not literally equivalent to adding 60 pooled episodes, but it is non-negligible relative to 352 observed episodes.

| alpha | posterior median | 95% interval | Pr(theta <= 0.20) |
|---:|---:|---:|---:|
| 0.10 | 0.138 | [0.124, 0.153] | 1.000 |
| 0.25 | 0.152 | [0.135, 0.171] | 1.000 |
| 0.50 | 0.172 | [0.152, 0.195] | 0.991 |
| 1.00 | 0.205 | [0.182, 0.231] | 0.329 |

The Jeffreys alpha=0.5 result (median 0.172) is pulled upward from the empirical 45/352 = 0.128, and the alpha=1 posterior crosses the registered 0.20 boundary. Proximity to 0.20 is therefore prior-dependent rather than an independent data signal. The stratified prompt-cluster bootstrap [0.071, 0.189] remains the principal dependence-aware sensitivity.
