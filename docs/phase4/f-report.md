# Family F report (interim, per registered rider: final verdicts in step 8)

Registration: original 2026-07-24; completion amendment 2026-07-28 (f-opponent-specs.md §9.1). Per-arm confirmatory status (architect ruling, verbatim):

- `fo-tracker` — CONFIRMATORY (sealed-complete alias)
- `ngram2` — CONFIRMATORY UNDER COMPLETION AMENDMENT
- `ngram3` — CONFIRMATORY UNDER COMPLETION AMENDMENT
- `wsls-targeter` — CONFIRMATORY (sealed-complete, operational pins only)
- `switcher-r26` — CONFIRMATORY UNDER COMPLETION AMENDMENT
- `shuffled-history` — CONFIRMATORY UNDER COMPLETION AMENDMENT

## Ū_X per arm (adversary mean per-round payoff; n usable episodes)

| arm | n | mean Ū_X |
|---|---|---|
| p4-f-fo-tracker-cvx | 20 | +0.1590 |
| p4-f-fo-tracker-gpt | 20 | -0.1180 |
| p4-f-ngram2-cvx | 20 | +0.0760 |
| p4-f-ngram2-gpt | 20 | +0.2150 |
| p4-f-ngram3-gpt | 20 | +0.0740 |
| p4-f-shuffled-history-cvx | 20 | +0.0230 |
| p4-f-shuffled-history-gpt | 20 | -0.0350 |
| p4-f-switcher-r26-cvx | 20 | -0.0320 |
| p4-f-switcher-r26-gpt | 20 | -0.0270 |
| p4-f-wsls-targeter-cvx | 20 | -0.0900 |
| p4-f-wsls-targeter-gpt | 20 | +0.0080 |

## Claims

- **P4-F-1 (primary conjunction)** — only-first (Δ LB > 0; Ū_wsls LB ≤ 0) — registered branch
  - Δ(wsls−fo): est +0.1260, LB95 +0.0930
  - Ū_wsls: est +0.0080, LB95 -0.0080

### Secondary family (Holm m=6, gpt tier)

| opponent | est Ū_X | p (two-sided) | Holm p | verdict |
|---|---|---|---|---|
| fo-tracker | -0.1180 | 1.00e-04 | 6.00e-04 | supported (Holm-adjusted two-sided p < 0.05) |
| ngram2 | +0.2150 | 1.00e-04 | 6.00e-04 | supported (Holm-adjusted two-sided p < 0.05) |
| ngram3 | +0.0740 | 2.70e-02 | 8.09e-02 | not significant under Holm |
| wsls-targeter | +0.0080 | 3.97e-01 | 3.97e-01 | not significant under Holm |
| switcher-r26 | -0.0270 | 1.09e-01 | 2.18e-01 | not significant under Holm |
| shuffled-history | -0.0350 | 1.72e-02 | 6.88e-02 | not significant under Holm |

- **Directional (shuffled < fo)** — not supported (LB ≤ 0) (Δ(fo−shuffled) est -0.0830, LB95 -0.1160)

### Cross-vendor replication tier (gemini-2.5-flash)

- Conjunction mirror — neither — registered branch

| opponent | est Ū_X | p | Holm p (m=5) | verdict |
|---|---|---|---|---|
| fo-tracker | +0.1590 | 1.00e-04 | 5.00e-04 | replicated-direction (Holm-adjusted two-sided p < 0.05) |
| ngram2 | +0.0760 | 1.18e-02 | 3.55e-02 | replicated-direction (Holm-adjusted two-sided p < 0.05) |
| wsls-targeter | -0.0900 | 1.00e-04 | 5.00e-04 | replicated-direction (Holm-adjusted two-sided p < 0.05) |
| switcher-r26 | -0.0320 | 1.36e-01 | 2.72e-01 | not significant under Holm |
| shuffled-history | +0.0230 | 4.21e-01 | 4.21e-01 | not significant under Holm |

## Provider-failure non-observations (registered rule, disclosed)

- p4-f-switcher-r26-cvx ep9 (runId run_1785197810_ce96bdb0, seed 3061, 0 rounds played)
- p4-f-switcher-r26-cvx ep4 (runId run_1785198107_39264278, seed 3056, 4 rounds played)
- p4-f-ngram2-cvx ep20 (runId run_1785198346_443ff1da, seed 3012, 12 rounds played)
- p4-f-wsls-targeter-cvx ep4 (runId run_1785199909_59bed841, seed 3036, 13 rounds played)
- p4-f-shuffled-history-cvx ep6 (runId run_1785200271_beb7dc20, seed 3078, 1 rounds played)
- p4-f-wsls-targeter-cvx ep1 (runId run_1785200747_28fe72eb, seed 3033, 7 rounds played)
- p4-f-shuffled-history-cvx ep14 (runId run_1785201232_2e9c7129, seed 3086, 1 rounds played)
- p4-f-wsls-targeter-cvx ep13 (runId run_1785201706_38b91ebf, seed 3045, 5 rounds played)
- p4-f-shuffled-history-cvx ep4 (runId run_1785202062_96af36c3, seed 3076, 14 rounds played)
- p4-f-ngram2-cvx ep17 (runId run_1785202305_41e6865a, seed 3009, 10 rounds played)
- p4-f-wsls-targeter-cvx ep2 (runId run_1785202545_f8279225, seed 3034, 9 rounds played)
- p4-f-shuffled-history-cvx ep13 (runId run_1785202785_4aab6b8f, seed 3085, 12 rounds played)
- p4-f-fo-tracker-cvx ep20 (runId run_1785202976_2a00ea3f, seed 2992, 3 rounds played)
- p4-f-ngram2-cvx ep5 (runId run_1785205134_fe92ab1b, seed 2997, 0 rounds played)
- p4-f-fo-tracker-cvx ep8 (runId run_1785206260_44cee688, seed 2980, 30 rounds played)
- p4-f-shuffled-history-cvx ep8 (runId run_1785206547_0c9d6ebe, seed 3080, 49 rounds played)
- p4-f-wsls-targeter-cvx ep16 (runId run_1785206871_f85ebb39, seed 3048, 3 rounds played)
- p4-f-ngram2-cvx ep19 (runId run_1785208122_5454bcc1, seed 3011, 22 rounds played)
- p4-f-switcher-r26-cvx ep7 (runId run_1785210046_81fa69ba, seed 3059, 18 rounds played)
- p4-f-ngram2-cvx ep1 (runId run_1785210651_ff83abe3, seed 2993, 0 rounds played)
- p4-f-ngram2-cvx ep7 (runId run_1785210888_0bec5103, seed 2999, 5 rounds played)
- p4-f-shuffled-history-cvx ep1 (runId run_1785211315_03f6220a, seed 3073, 0 rounds played)

## Sentinel stability: v2a × gemini-2.5-flash, full trajectory (closed at both ends)

| check | modal | count/10 | regime |
|---|---|---|---|
| 0 | 0 | 10 | sealed baseline |
| 1 | 0 | 9 | vs sealed baseline |
| 2 | 0 | 9 | vs sealed baseline |
| 3 | 0 | 8 | vs sealed baseline |
| 4 | 0 | 8 | vs sealed baseline |
| 5 | 0 | 7 | vs sealed baseline |
| 6 | 0 | 10 | re-baseline read |
| 7 | 0 | 6 | vs re-baseline@6 |
| 8 | 0 | 7 | vs re-baseline@6 |
| 9 | 0 | 6 | vs re-baseline@6 |
| 10 | 0 | 7 | vs re-baseline@6 |
