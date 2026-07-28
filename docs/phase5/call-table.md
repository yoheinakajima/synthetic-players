| Tier | Block | Model | Episodes | Calls/ep (ledger) | Calls |
|---|---|---|---|---|---|
| A | rep-PD d=0.10 x S2{p,a} (2 cells) — 16 personas x 2 cells x 6 ep | gpt-4.1 | 192 | 2.05 | 394 |
| A | rep-PD d=0.90 x S2{p,a} (2 cells) — 16 personas x 2 cells x 6 ep | gpt-4.1 | 192 | 14.85 | 2852 |
| A | one-shot label-swap — 16 x 20 ep | gpt-4.1 | 320 | 2 | 640 |
| A | one-shot community — 16 x 20 ep | gpt-4.1 | 320 | 2 | 640 |
| B | rep-PD d=0.90 pair, T sweep — 4 personas x 2 cells x 2 temps x 6 ep | gpt-4.1 | 96 | 14.85 | 1426 |
| B | label-swap, T sweep — 4 personas x 2 temps x 20 ep | gpt-4.1 | 160 | 2 | 320 |
| B | bare subject, T sweep, d=0.90 pair — 1 bare x 2 cells x 2 temps x 6 ep | gpt-4.1 | 24 | 14.85 | 357 |
| B | bare subject, T sweep, swap — 1 bare x 2 temps x 20 ep | gpt-4.1 | 40 | 2 | 80 |
| C | rep-PD d=0.90 pair (gemini) — 8-persona registered half x 2 cells x 4 ep | gemini-2.5-flash | 64 | 15.36 | 984 |
| C | label-swap (gemini) — 8 x 10 ep | gemini-2.5-flash | 80 | 3 | 240 |
| S | sentinel battery — 10 checks x 2 models x 2 cells x 5 ep | both | 200 | 2 | 400 |
| S | gate0-style entry verification — revision pin + per-T echo assertion, 3 temps x 2 models x 4 calls | both | 0 | 0 | 24 |
| | **Subtotal** | | | | **8357** |
| | Waste/retry headroom (7.5%, from Phase 4 ledger actuals) | | | | 627 |
| | **Total** (cap 15000) | | | | **8984** |
| | Tier C alone (clean-drop line) | | | | 1224 |
