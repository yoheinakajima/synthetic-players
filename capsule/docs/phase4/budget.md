# Phase 4 Budget (freeze packet §G) — calls, tokens, dollars, kill-switches

> **STATUS: WORKING DRAFT — PRE-PUBLICATION, NOT FOR CITATION.**


Token/cost basis: measured Phase 3 means from the event store (5,830 calls):
one-shot PD ≈ 172 in / 1 out tok, $0.0052/call · repeated PD ≈ 306–358 in / 1 out,
$0.0093–0.0108/call · RPS 50-round ≈ 597 in (max 1,103) / 2.35 out, $0.0181/call —
all at gpt-4.1 rates via Replit AI Integrations. Cross-vendor calls are token-matched;
`gemini-2.5-flash` per-token rates ($0.30/M input, $2.50/M output; amendment A1 — same bound held for the original haiku candidate) are at or below gpt-4.1's, so gpt-4.1-rate figures
are used as an **upper bound** for both models (billed to workspace credits).
Repeated-PD δ=.90 episodes: measured 15.9 calls/episode (X1, matched horizons);
δ=.10: ≈ 2.2 calls/episode (Phase 3 d10).

## Expected calls and cost by block (F at 50 rounds — gate failed, registered reversion)

| Block | Cells × eps | Expected calls (primary) | Expected calls (cross) | Est. cost (both, upper bound) |
|---|---|---|---|---|
| D1 one-shot factorial | 64 × 10 | 1,280 | 1,280 | $13.4 |
| D2 decoupling | 8 × 20 | 320 | 320 | $3.4 |
| D3 symbols | 36 × 2 | 144 | 144 | $1.8 |
| E gate+slope | 4 × 20 | ≈ 724 | ≈ 724 | $13.5 |
| X2 screening (10 rungs × 10 eps, δ=.90) | primary only | ≈ 1,590 | — | $16.6 |
| X2 confirmation (2 × 20, runs only on candidate) | primary only | ≤ 636 | — | $6.7 |
| F adversarial (50 rounds) | 6/5 opp × 20 | 6,000 | 5,000 | $199.1 |
| **Experimental subtotal** | | **10,694** | **7,468** | **≈ $254.5** |
| Sentinels (~8 boundary checks + ~2 weekly, 60/check across both models) | shared | ≈ 600 | | $5.6 |
| Semantic-equivalence ratings (§2.2) | shared | 18 | | $0.4 |
| Gate-0 provider verification (infra, excluded from analysis) | shared | ≈ 10 | | $0.1 |
| **Grand total** | | **≈ 18,790** | | **≈ $261** |

Experimental subtotal check: primary 1,280 + 320 + 144 + 724 + 1,590 + 636 + 6,000 =
10,694; cross 1,280 + 320 + 144 + 724 + 5,000 = 7,468; shared overhead ≈ 628.
Combined expected ≈ **18,790 calls / ≈ $261** (upper bound at gpt-4.1 rates; actual
cross-vendor spend lower). Retry allowance: registered 1 retry per invalid completion
+ seed-pool replacement; Phase 3 invalid rate was 0/5,820 — buffer **2%** ≈ 380 calls.
Every provider call (including retries, sentinels, ratings, Gate-0, failed/partial
runs) counts against the caps; retries are linked to their episode in the event store.

## 30-round F alternative (NOT chosen — shown per sign-off §12)

| | Calls (primary) | Calls (cross) | Δcost vs 50-round |
|---|---|---|---|
| F at 30 rounds, switcher r16 | 3,600 | 3,000 | −$79.7 |

The 30-round stabilization gate failed by 0.0012 on |Δstay| (0.0512 > 0.05;
`f-stabilization.md`); the registered rule reverts to 50 rounds. No discretion applied.

## Kill-switches (hard caps; engine-enforced, per sign-off §10)

| Scope | Cap |
|---|---|
| Global Phase 4 | **21,000 calls** |
| D1+D2+D3 combined | 4,300 |
| E | 1,800 |
| X2 total | 2,700 |
| F total | 11,600 |
| Sentinels + ratings + Gate-0 | 900 |
| Single episode (runaway guard) | 260 calls (2 × cap-120 horizon + retries) |

Cap breach ⇒ hard stop of the block, disclosure in the run log, and a decision memo —
never a silent trim. Weekly sentinel burn while idle between blocks: 60 calls/week
(both models), $0.6/week, drawn from the sentinel cap.
