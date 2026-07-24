# Phase 4 provenance notes (running; feeds the step-8 provenance appendix)

Working disclosures recorded at the moment they arise so the final appendix
cannot omit them. Interim per-block reports are working documents; **final
verdicts issue only from the step-8 full replay + adjudication pass.**

1. **"for 1 rounds" grammar (registered rider, 2026-07-24).** The sealed
   one-shot templates render the literal string "for 1 rounds". The template
   bytes are frozen; the oddity is disclosed rather than repaired. No
   evidence of differential effect; any reader can byte-verify against the
   sealed registry.

2. **Sentinel cadence reading.** The sealed schedule notes say "sentinel
   immediately before and after this block" per block. At adjacent block
   boundaries one check serves both notes (the check *after* block N *is*
   the check *before* block N+1). Check indices: 0 = before X2-screening,
   1 = X2/D1 boundary, 2 = D1/D2, 3 = D2/D3, 4 = D3/E, 5 = E/F, 6 = after F.
   Arithmetic: a full check = 3 arms × 2 models × 10 episodes × 2 self-play
   calls = 120 calls; 7 checks = 840, plus 15 Gate-0 calls and 18 planned
   rating calls = 873 of the 900 overhead cap. Any additional check (e.g.
   the weekly rule during a block spanning >7 days) would exceed the cap and
   therefore requires a decision memo first, per the registered cap-breach
   process. The budget document's "60 calls/week" idle line corresponds to a
   half-check; the enforced seat rule (self-play, both seats live) makes a
   full check 120 calls — disclosed here as a budget-note discrepancy.

3. **Sentinel fingerprint definition (sealed with the check-0 baseline).**
   Cell = arm × model. Episode value = seat-1 round-1 action index. Modal
   action = most frequent episode value (tie → lower index). Fingerprint =
   modal count out of 10. Frozen rule (c) compares counts (alert iff Δ ≥ 3
   episodes vs baseline). Modal-action *flips* at similar counts are outside
   the frozen rule's letter and are disclosed as observations. Seat-2
   distributions are archived alongside.

4. **X2 ladder endpoints are the sealed Phase 3 X1 arms** (pd-repeated-v1 /
   v2a, δ=.90, seeds 1–10, matched horizon draws) — reused evidence, no new
   calls. Consequence: if screening selects span 1 or span 6, the minimal
   pair includes a Phase 3 endpoint template, and the write-once resolution
   layer (which requires `pd-x2-*` templates for X2-conf-lo/hi) would refuse
   it. Confirmation in that case requires a registered amendment before
   dispatch. Interior spans (2–5) resolve without amendment.

5. **Horizon rule.** numRounds for E / X2 blocks is drawn client-side by the
   registered Phase 3 rule: geometric(δ) via mulberry32(seed ^ 0x54524D),
   cap 120; a truncated draw excludes the supergame (zero calls, disclosed).
   The driver imports the engine's mulberry32 port; realized-rounds ==
   drawn-horizon parity is machine-checked per episode by the adjudicator's
   integrity scan.

6. **engineCommit discipline (registered rider 2).** The dispatch driver
   refuses to run unless the worktree is clean and HEAD equals the recorded
   preflight commit; the first live run of every driver process asserts the
   engine-stamped commit is {sha: HEAD, dirty: false} and freezes otherwise.
   Driver and adjudicator are committed before first dispatch; their commit
   is the one stamped on every run they dispatch.

7. **Request-construction parity.** The driver builds game definitions with
   the engine's own derivation functions (`_pd_expected_matrix`,
   `_rps_sym_expected_matrix`, `_pure_nash`, registry `options`) rather than
   a reimplementation, and every scheduled step-4 request was validated
   against the enforcement layer via zero-spend dry runs before any live
   dispatch ("dry-all" pass).

8. **Anchoring.** The step-3 seal is externally anchored (GitHub release
   `phase4-v3-seal`, published 2026-07-24T19:04:16Z); the annotated tag is
   NOT GPG-signed (no signing key in the environment) — disclosed deviation,
   see `seal-record.md`. A second, independent timestamp (OpenTimestamps on
   the release's SHA256SUMS.txt) is planned; its outcome (or network
   failure) will be recorded here.

9. **Per-block reporting (registered rider 3).** Blocks are dispatched in
   the sealed order with adjudication + a report to the researcher at each
   block boundary. These interim reports never substitute for the step-8
   full pass.

## OpenTimestamps second anchor (2026-07-24)
- Stamped: `SHA256SUMS.txt` asset of release `phase4-v3-seal`, fetched from GitHub and verified sha256 `082942c06faf6df88dc5cc74960f0d9eaeb53a8485731ffdae924d02a0706fb9`.
- Calendars accepting the digest: a.pool.opentimestamps.org, b.pool.opentimestamps.org, a.pool.eternitywall.com, ots.btc.catallaxy.com.
- Proof committed at `docs/phase4/SHA256SUMS.txt.ots` and attached to the release as an additional asset (addition only; no sealed asset modified). Status: **pending** Bitcoin attestation — run `ots upgrade docs/phase4/SHA256SUMS.txt.ots` after ~24h, then `ots verify` against the release asset. Tooling note: client run with an OpenSSL-3 `LD_PRELOAD` workaround (does not affect proof bytes).

## Pre-dispatch code review (2026-07-24, before any live call)
An independent reviewer audited the dispatch driver and adjudicator against the
frozen predicates before first live dispatch. Findings fixed (no live data
existed yet, so no result is affected): (1) anomaly freezes now always persist
the frozen flag; (2) at-most-once dispatch guard — an inflight marker is
persisted before every live POST and must be resolved via event-store
reconciliation after any ambiguous interruption; (3) finish_reason comparison
made case-insensitive (Gemini reports the enum name `STOP`; OpenAI `stop`);
(4) reverse-ladder span indexing corrected to the sealed definition (R_i =
spans 1..i reverted ⇒ the gap at position i isolates span i in both ladders —
the earlier draft inverted reverse indices; screening had not yet run);
(5) sentinel check-0 baseline made write-once on disk. Dry-all re-validated
after these fixes.
