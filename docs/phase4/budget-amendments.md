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
