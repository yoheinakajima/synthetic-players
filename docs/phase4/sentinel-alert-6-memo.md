# Sentinel alert 6 — rule (c) fires at checks 9 and 10 (v2a × gemini), discovered late

Status: OPEN — awaiting operator decision. No further adjudication finals or
step-8 replay verdicts issue until resolved. Written 2026-07-28.

## Facts (all from the registered evaluator, `phase4_adjudicate.py --sentinel k`, read-only)

- Check 9 (gemini-only cadence): `p4-sent-v2a|gemini-2.5-flash` count **6**
  vs re-baseline@6 **10** → Δ≥3, **ALERT (c)**, exit 2.
- Check 10 (full): same cell count **7** vs 10 → Δ≥3, **ALERT (c)**, exit 2.
  All other cells clean at both checks (v1×gpt 10, v1×gemini 9, v2a×gpt 10,
  fallback×gpt 10, fallback×gemini 9–10 — all within rule).
- Full v2a×gemini trajectory (fingerprint modal count /10):
  check 0: 10 (sealed baseline) → 1: 9 → 2: 9 → 3: 8 → 4: 8 → 5: 7 (alert 5)
  → 6: **10** (re-baseline read) → 7: 6 → 8: 7 → 9: 6 → 10: 7.

## Process lapse (disclosed)

The driver's sentinel action dispatches the cell episodes and enforces rule
(b) (retry/invalid) inline; its "cell X × Y: 10/10" console line is a
**dispatch-completion count, not a rule evaluation**. Rule (c) evaluation is
assigned to the offline evaluator, run manually at each checkpoint. During
the F-block provider-failure recovery churn, the evaluator was **not run**
for checks 9 and 10; both were logged in provenance as clean on the basis of
driver prints. Consequently **F h2 was dispatched after check 9 without the
registered rule-(c) evaluation having been executed.** Under the frozen
STOP-ON-ANOMALY regime a fired check 9 would have frozen dispatch at that
boundary.

Mitigating facts, for the record (not excuses): the F subject cells are
independent of the sentinel cells; F gpt-tier sentinel cells were 10/10
clean at check 10; the drifted cell is the same single cell (v2a × gemini)
that produced alert 5 and the check-6 re-baseline; zero retries/invalids in
all F dispatch (rule (b) never fired); F integrity gauntlet passed in full
(`--f`, 220/220, seeds/models/templates/commit clean).

## Reading of the trajectory

Post-re-baseline the series is 6, 7, 6, 7 — internally stable, centered
≈6.5. The check-6 re-baseline read of **10** is the outlier relative to both
the preceding decay (…8, 8, 7) and the subsequent plateau. The plausible
account: check-6 happened to catch a high draw, and the "drift" alerts at
9–10 measure distance from that unlucky anchor, not new movement. But that
account is post-hoc; the frozen rule fired, and the frozen rule governs.

## Decision items for the operator (batch)

1. **Alert disposition.** Options:
   - (A) Accept the alerts as fired; record the post-rebase plateau reading
     descriptively; **demote the F cross-vendor (gemini) replication tier to
     descriptive-only** in finals (gpt tier unaffected). Cheapest, most
     conservative, no new spend.
   - (B) Registered amendment: evaluate rule (c) for this cell against the
     post-rebase plateau (mean of checks 7–10) rather than the single
     check-6 read, with the amendment disclosed as data-inspected (NOT
     outcome-blind — the trajectory is known). Keeps cvx tier confirmatory
     only if the operator accepts a data-dependent rule change, which the
     pipeline has so far refused on principle.
   - (C) Dispatch sentinel check 11 (gemini-only, ~30 episodes spend) to
     extend the plateau series before deciding. Adds evidence, adds spend,
     does not by itself un-fire checks 9–10.
2. **F h2 admissibility.** F h2 was dispatched past an (unevaluated) fired
   check. Options: admit with disclosure (subject cells independent of
   sentinel cells; recommended if 1A chosen), or quarantine gemini-tier h2.
   Note the F gpt arms were all dispatched in h1+h2 interleaved; a
   quarantine would need the dispatch map, available from the state file.
3. **Process fix (no decision needed, will implement on resume):** driver
   sentinel action will invoke the registered evaluator and freeze on
   exit 2, so rule (c) can never again be skipped by operator/agent lapse.

## Effect on current outputs

- `f-report.{json,md}` remain **interim** (already labeled). The gpt-tier
  claims are unaffected by any option above. The cross-vendor tier's final
  status depends on item 1.
- Step-8 replay audit can proceed mechanically regardless (read-only), but
  no final verdicts issue until items 1–2 are decided.
