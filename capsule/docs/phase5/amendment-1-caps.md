# Phase 5 Amendment 1 — Budget cap correction (pre-data)

- **Approved:** operator, mission UI, 2026-07-28 ("Option 1 … Go."), before any
  Phase 5 live dispatch (ledger at 0 Phase 5 calls at amendment time).
- **What changed:** `GLOBAL_CAP_P5` and `CAP_GROUPS_P5` in
  `artifacts/api-server/engine/phase5.py` only. No template, arm, seed,
  persona, schedule, threshold, or analysis byte changed.

| Cap | Sealed (8,984 packet) | Amended |
|---|---|---|
| P5-A | 4,866 | 5,556 |
| P5-B | 2,347 | 3,627 |
| P5-C | 1,316 | 1,546 |
| P5-overhead | 456 | 456 |
| **Global** | **8,984** | **11,185** (≤ operator standing cap 15,000) |

## Root cause (recorded per operator rider 1)

The sealed call table (`call-table.md`) priced rep-PD episodes from **Phase 4
ledger per-episode averages** (2.05 calls/ep at δ=0.10, 14.85 at δ=0.90 —
i.e. ~7.4 rounds mean drawn horizon), not from the Phase 5 seed lanes. The
Phase 5 horizons are a deterministic pure function of the sealed episode
seeds (`draw_horizon`, mulberry32), and the exact seeded need is:

| Block group | Exact seeded calls |
|---|---|
| P5-A (rep 3,888 + os 1,280) | 5,168 |
| P5-B (rep 2,974 + os 400) | 3,374 |
| P5-C (rep 1,278 + os 160) | 1,438 |
| Overhead (sentinels 400 + entry 24) | 424 |
| **Total** | **10,404** vs sealed global 8,984 |

The driver's preflight projection was **correct** (it sums 2 × the exact
drawn horizon over unfinished scheduled episodes); the sealed call table was
the estimate in error. The registered shed order could not clear the bind
(after all four shed steps P5-B still projected 2,402 > 2,347; step 5 =
freeze), so the freeze escalated to the operator as designed.

## Why this is pre-data, not outcome-contingent

Horizon draws depend only on sealed seeds and were computable at freeze time;
no model output existed when the amendment was approved (Phase 5 ledger:
0 calls). Amended caps = exact seeded need + the same 7.5% waste/retry
headroom the packet already used, per tier. No shedding: the full sealed
design runs.

## Registered rule going forward (operator rider 1)

**For seeded designs, sealed call tables are computed from the exact seeded
horizons at freeze time — never from per-episode averages of a prior phase —
and the seal linter checks the call table against the schedule's drawn
horizons.** (A-OVH-2 lesson at block scale; this is to be the last instance.)

## Clean-path pre-authorization (operator rider 2)

Seal → anchor → 24-call entry battery → dispatch → run the **full plan
without holding**; freeze only on a sentinel fire, a refusal, an attestation
failure, or any anomaly; batch decision items for the operator.
