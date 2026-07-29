# Phase 4 sentinel baseline (check 0) — sealed on write

Sealed at 2026-07-24T20:29:10Z. cell = sentinel arm × subject model; episode value = seat-1 round-1 action index; modal action = most frequent episode value across the cell's 10 episodes (tie → lower action index); fingerprint = (modalAction, count of episodes whose value equals it). Rule (c) compares counts: alert iff |count_K − count_baseline| ≥ 3. Modal-action flips at similar counts are disclosed as observations (the frozen rule is count-based). Seat-2 distributions are archived alongside for context.

| cell | modal action | count/10 | seat-1 distribution |
|---|---|---|---|
| p4-sent-v1|gpt-4.1 | 1 | 10 | {1: 10} |
| p4-sent-v1|gemini-2.5-flash | 1 | 8 | {1: 8, 0: 2} |
| p4-sent-v2a|gpt-4.1 | 0 | 10 | {0: 10} |
| p4-sent-v2a|gemini-2.5-flash | 0 | 10 | {0: 10} |
| p4-sent-fallback|gpt-4.1 | 1 | 10 | {1: 10} |
| p4-sent-fallback|gemini-2.5-flash | 1 | 9 | {1: 9, 0: 1} |
