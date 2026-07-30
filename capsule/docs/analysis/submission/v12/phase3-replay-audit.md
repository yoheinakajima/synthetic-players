# Phase 3 zero-call replay audit

- Generated: 2026-07-30T22:58:22Z
- **Verdict: PASS — CLEAN**
- LLM runs replayed: 323 (clean 323)
- LLM calls byte/prompt/action verified: 5830/5830
- LLM-run rounds compared: 3916
- Zero-LLM baseline runs independently recomputed: 20/20 (1000 rounds)

| prompt | completed runs |
|---|---:|
| `pd-oneshot-v1` | 61 |
| `pd-repeated-v1` | 161 |
| `pd-repeated-v2a` | 20 |
| `pd-repeated-v2b` | 20 |
| `rps-v1` | 61 |

This closes the former capsule boundary: the 320 registered Phase 3/X1 LLM runs, three additional completed legacy entry/diagnostic runs, and the deterministic P3-C3 baseline are covered by a public zero-call verifier.
