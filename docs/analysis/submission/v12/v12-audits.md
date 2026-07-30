# v12 independent audits

> **STATUS: POST-ADJUDICATION, ZERO-CALL VERIFICATION.** No historical verdict or sealed artifact is changed.

## Independent bootstrap coincidence audit

- Cell: `rep-d10-s2a`; data shape: 16 prompts × 6 episodes.
- Stored lower bound: `0.412198000`.
- Independent mean lower bound across 3 seeds: `0.412128059`; seed-to-seed range `0.000000000`.
- Interpretation: The stored lower bound is independently reproduced. The apparent 0.4122 match is a rounding coincidence: the stored value is 0.412198, whereas the published human reference is reported as 0.4122 and does not enter the bootstrap computation.

| seed | replicates | lower 2.5% | median | upper 97.5% |
|---:|---:|---:|---:|---:|
| 20260812 | 250,000 | 0.412128059 | 0.423417533 | 0.439051482 |
| 20260813 | 250,000 | 0.412128059 | 0.423417533 | 0.439051482 |
| 20260814 | 250,000 | 0.412128059 | 0.423417533 | 0.439051482 |

## Leaning-rule strata

| condition | cooperative-leaning mean | defect-leaning mean | difference | prompts per stratum |
|---|---:|---:|---:|---:|
| `rep-d10-s2a` | 0.615 | 0.083 | +0.531 | 8 |
| `rep-d10-s2p` | 0.760 | 0.094 | +0.667 | 8 |
| `rep-d90-s2a` | 0.688 | 0.177 | +0.510 | 8 |
| `rep-d90-s2p` | 0.865 | 0.146 | +0.719 | 8 |
| `os-community` | 0.688 | 0.019 | +0.669 | 8 |

## Temperature and choice entropy

base-2 Shannon entropy H=-sum_a p(a)log2 p(a) over round-one recorded action indices; the registered secondary pooled all valid seat actions at each temperature.

| T | all pooled entropy | all seats | matched pooled entropy | matched seats | mean within-unit entropy |
|---:|---:|---:|---:|---:|---:|
| 0.7 | 0.9057 | 2752 | 0.8310 | 544 | 0.4484 |
| 1.0 | 0.7868 | 336 | 0.7822 | 284 | 0.2566 |
| 1.3 | 0.7766 | 336 | 0.7698 | 284 | 0.2877 |

The registered pooled entropy decline is partly composition-confounded but its direction survives on the identical sweep lattice. Mean within-unit entropy is reported separately because pooled entropy can remain high when different prompt-cell units occupy opposite boundaries. The observation remains exploratory and does not identify a temperature mechanism.

## Decoding-parameter audit

Inspected 36,251 archived `llm.requested` payloads. Temperature and maxTokens are archived on every request. On the primary OpenAI-compatible path, temperature and max_tokens were supplied explicitly; top_p=1.0 was assembled and intentionally omitted from the wire at 1.0; presence_penalty, frequency_penalty, and logit_bias were not supplied and therefore inherited provider defaults.
