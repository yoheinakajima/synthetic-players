# Budget amendments (additive — budget.md is sealed and stays byte-untouched)

## A-OVH-1 — overhead cap 900 → 1,000 (2026-07-24, registered pre-dispatch)

Trigger: sentinel alert 5 resumption (sentinel-alert-5-memo.md §Decision).

Arithmetic at registration (engine ledger, authoritative): overhead spend
735/900. Remaining base cadence — full checks 6, 8, 10 at 60 calls each = 180
— already projects **915 > 900**: the sealed overhead figure
under-provisioned the realized boundary-check count, independent of the alert.
The operator-approved doubled gemini cadence (memo §Decision rider 2:
gemini-only checks 7 and 9, 30 calls each) adds 60 → projection **975**.

Amended cap: **1,000** (headroom 25 over projection; any further sentinel
spend beyond the registered cadence map is a new operator decision).

Authority: operator sign-off, memo §Decision — rider 1 approves the extra
sentinel spend ("the extra sentinel spend is approved", verbatim); rider 2
specifies the doubled cadence. Engine enforcement (CAP_GROUPS) updated in the
same commit; global cap 21,000 unchanged — projected global worst case
≈ 20,562 (D 3,498 + X2 2,664 + E ≤ 1,800 + F ≤ 11,600 + overhead ≤ 1,000).

## A-OVH-2 — correction of A-OVH-1's projection arithmetic; cap 1,000 → 1,250 (2026-07-24, registered pre-dispatch of check 7 and block E)

A-OVH-1's forward projections priced sentinel checks at 10 calls per cell
(60 per full check). The event store prices them at **20 per cell**: sentinel
episodes are self-play — two subject seats per episode, two LLM calls per
episode. Every historical check cost 120 (full) / 60 (gemini-only), and the
ledger always said so (checks 0–6: 840 sentinel `llm.requested` rows; the
driver's per-cell "10/10" tallies count episodes, not calls — the source of
the error). Only the forward projections in A-OVH-1 (and the decision memo's
"~240 remaining" figure) were 2× under. **No cap was violated at any
dispatch**: check 6 ran under A-OVH-1's registered 1,000 and landed at 855.

Corrected arithmetic at registration: spend 855/1,000 (engine ledger).
Remaining registered cadence: check 7 gemini-only 60 + check 8 full 120 +
check 9 gemini-only 60 + check 10 full 120 = **360** → projection **1,215**.
Amended cap: **1,250** (headroom 35; sentinel spend beyond the registered
cadence map remains a new operator decision). Authority unchanged: memo
§Decision riders 1–2 — the approved cadence is what it always was; only its
price was misstated. A-OVH-1's text stands unedited as registered. Engine
enforcement updated in the same commit; global cap 21,000 unchanged —
projected global worst case ≈ 20,812 (D 3,498 + X2 2,664 + E ≤ 1,800 +
F ≤ 11,600 + overhead ≤ 1,250). Cross-checks confirming the sealed group
caps always priced seats correctly: E cap 1,800 ≈ 160 eps × mean horizon ×
2 seats; F cap 11,600 ≈ 220 eps × 50 rounds × 1 call (adversaries are
programmatic, only the subject seat is a model).
