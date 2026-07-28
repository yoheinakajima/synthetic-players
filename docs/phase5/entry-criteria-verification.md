# Phase 5 entry-criteria verification record

Verified 2026-07-28, before packet drafting, per the design-sketch §0 order.
The five instance-ledger rules are floor, not aspiration. Each entry gives
the mechanism, its evidence, and how to re-run the check.

## 1. Freeze-time completeness linter — LIVE (built this session)

- Mechanism: `artifacts/api-server/engine/freeze_lint.py` — manifest-driven
  seal gate. Checks: C1 end-to-end render of every dispatchable cell
  (including conditional branches and every resolution stand-in, never just
  the expected one) against the real prompt registry; C2 executable
  resolution rule + registered defaults for every data-dependent cell; C3
  schedule coverage both directions, conditional blocks materialized; C4
  three-layer rule; C5 discussion-branch coverage of every registered
  verdict combination. Any failure ⇒ exit 1 ⇒ no seal.
- **Acceptance test (registered criterion): reproduce the five Phase 4
  sealed-text instances as seal failures.**
  `uv run python engine/freeze_lint_selftest.py` → **PASS 6/6**:
  A1 E-dselected registration gap (ledger #10) ⇒ C2 fail; A2 sealed rule
  absent from a layer (sentinel third-cell switch) ⇒ C4 fail; A3 conditional
  block missing from schedule (ledger #11) ⇒ C3 fail; A4 RESOLVED-BY-*
  dispatch gap (ledger #12) ⇒ C1 fail; A5 unpinned template parameter —
  `deltaPct` on the real sealed pd-rep template (ledger #15) ⇒ C1 fail;
  A6 fully specified control manifest ⇒ PASS (no false positives).
  Fixtures render against the real `prompts/registry.json`, not synthetic
  templates.
- Draft-stage run: `docs/phase5/lint-manifest-draft.json` (all 6 task cells,
  bare + persona-composed system layers, sentinel cells with both
  conditional branches, verdict-branch coverage) — result in
  [`lint-draft-result.json`](lint-draft-result.json). Three-layer anchors for
  Phase 5-specific rules attach when the Phase 5 dispatch/enforcement/replay
  code lands; the seal-time lint (packet §8) is the binding gate.

## 2. Evaluator-attestation dispatch gating — LIVE (unchanged Phase 4 code)

- `engine/phase4_driver.py`: sentinel evaluator invoked as a registered
  subprocess; non-zero evaluator exit ⇒ freeze; block dispatch requires
  positive attestation for every preceding sentinel check
  (`"block dispatch requires evaluator attestation"` freeze path);
  attestations persisted in driver state (`sentinelAttestations`). Produced
  by the alert-6 lapse (ledger #20); carried into Phase 5 as-is.

## 3. Three-layer rule — MECHANIZED (was procedural)

- Now a linter check (C4): every sealed conditional rule registers anchors
  `{dispatch: {file, pattern}, enforcement: {...}, replay: {...}}`; a missing
  anchor or non-matching pattern in ANY layer fails the seal. Acceptance
  fixture A2 proves the failure mode fires. Phase 4's manual grep discipline
  (ledger #21) is thereby removed from human memory and placed in the gate.

## 4. Watchdog auto-resume — LIVE, registered signatures only (built this session)

- `engine/watchdog.py` supervises the driver. Auto-resume (reconcile → clear
  frozen → relaunch) fires **only** when the freeze reason matches
  `engine/resume-signatures.json` (registered, append-only; currently the
  single class `"AMBIGUOUS transport failure on"` — the driver's transport/
  restart signature, which Phase 4 showed is operational noise resolved by
  `--reconcile` in 100% of instances). Sentinel alerts, attestation gaps,
  worktree/commit mismatches, budget binds: **never** auto-resumed — the
  watchdog logs, stays frozen, exits non-zero. Bounded at 5 resumes/hour
  (excess = anomaly ⇒ hard stop). Every action appended to
  `engine/data/watchdog-log.jsonl`.
- Selftest (no dispatch): `uv run python engine/watchdog.py --selftest` →
  **PASS** (signature matching incl. all three refusal classes; end-to-end
  stub freeze → reconcile → resume → clean exit; refusal path stays frozen).
- Container restarts: covered structurally — the workflow relaunches the
  watchdog, the driver's own resume state skips completed actions, and a
  stale inflight marker surfaces as the registered transport freeze.

## 5. Budgeting from ledger prices — LIVE (built this session)

- `engine/phase5_budget.py` derives every per-episode price from the Phase 4
  budget ledger (`budget.db` `spend` per-run actuals): rep-PD δ=0.90 =
  14.85 calls/ep (gpt-4.1 mean; max 44), δ=0.10 = 2.05, one-shot = 2
  (gemini: 15.36 / 3), sentinel = 2. No design-unit arithmetic anywhere in
  the Phase 5 table (A-OVH-2 / ledger #16). Headroom 7.5% is priced from
  Phase 4 waste actuals. Output: `docs/phase5/call-table.{md,json}`.

## Also per §0

- Design sketch committed verbatim: [`design-sketch.md`](design-sketch.md),
  banner-marked PROPOSED.
- Revision pin + per-T temperature echo assertion require **live calls**;
  they run as the 24-call entry battery immediately after seal, before any
  subject dispatch (packet §5) — the environment is quiescent now and stays
  so until sign-off.
