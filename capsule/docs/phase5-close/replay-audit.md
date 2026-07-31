# Phase 5 close-out replay audit

- Generated: 2026-07-31T14:18:32Z  ·  live calls: 0
- **Verdict: PASS — CLEAN**
- Runs replayed: 1712 (ok 1712, invalid-trial runs 0, failures 0)
- Recorded LLM calls: 10428; byte-verified 10428 (bundle shas 10428, request-body shas 10428, parsed actions 10428)

| block | runs | ok | invalid trials | calls verified |
|---|---|---|---|---|
| P5-entry | 24 | 24 | 0 | 48 |
| P5-sentinel | 200 | 200 | 0 | 400 |
| P5A-os | 640 | 640 | 0 | 1280 |
| P5A-rep | 384 | 384 | 0 | 3888 |
| P5B-os | 200 | 200 | 0 | 400 |
| P5B-rep | 120 | 120 | 0 | 2974 |
| P5C-os | 80 | 80 | 0 | 160 |
| P5C-rep | 64 | 64 | 0 | 1278 |

Checks: bundleSha256 byte-recompute; requestBodySha256 recompute; parsed-action re-derivation; R1 persona re-composition from sealed store; R2 run-level + R2e per-request temperature pin; R3 per-response + R3e per-request model/revision pin; substitution re-derivation from arm bindings; template sha vs sealed manifest.
