> **Machine branch-selection record: axes A/B/C -> Branch 2, variant retained [CONFIRMATORY] (source: engine/phase5_closeout_adjudicate.py)**

# Phase 5 discussion-branch selection — final record

Generated 2026-07-28. Inputs: `docs/phase5-close/adjudication-report.{json,md}`
(verdicts verbatim from `engine/phase5_closeout_adjudicate.py`).

## Sealed branch file integrity

- File: `docs/paper/discussion-branches.md`
- sha256 now: `1f1d7de9c54811962416a43bc5eed05de7fdd99618d39c88e5a8ec2cde9f0356`
- sha256 sealed (docs/phase5/seal-record.md): identical — **byte-diff status:
  IDENTICAL, zero bytes changed since seal.**

## Registered selection rule (applied verbatim, in registered order)

1. If Axis B = at-least-one → Branch 2. **← fires. Selection stops here.**
2. Else if Axis C = yes → Branch 3.
3. Else if Axis A = supported → Branch 1.
4. Else Branch 4.

Axes from the adjudicator: A = supported (P5-1a alone, per outcome-blind
completion D3), B = **at-least-one** (P5-3: 16/16 personas pass; p13 also
via the Family-E signature clause), C = no (P5-4 not refuted).

## Selected: **Branch 2 — an interior persona exists**

Combination-table row (sealed 8-row table, lint-certified):
`| supported | at-least-one | no | Branch 2 |`

P5-2 = persona-dominant selects the corresponding variant paragraph within
Branch 2 (variant selection only; never branch-bearing).

The selected branch text is quoted verbatim, with this sha and the seal
anchor timestamp, in `docs/phase5/final-report.md` (§2 of the close-out
program).
