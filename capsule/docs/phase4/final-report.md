# Phase 4 final report

Issued 2026-07-28, at the completion of freeze-packet step 8 (replay-verify
all → mechanical adjudication → finals). Every verdict below is the
registered interim adjudicator's output, promoted to FINAL because the
step-8 replay audit is **CLEAN** (`step8-replay-audit.md`): 2,864/2,864
completed observations replay byte-exact under the §F.3 extended verifier
(bundle-sha byte-compare, request-body-sha recompute, parsed-action
re-derivation, per-round rng draw-count re-verification), 0 invalid trials
store-wide, 24 provider-failure partials verified as non-observations by
signature, and every Family-F adversary's per-round `rngCalls` profile
matches its sealed spec exactly (fo/ngram/switcher-Order-A: 0;
wsls: 1 at r1; shuffled-history: n−2 for r≥11 — Σ 1,140/episode).

No claim, threshold, tier, or branch below was chosen, changed, or dropped
after data became visible; the amendments that did occur are listed with
their registration character in §Amendments. Numbers are quoted verbatim
from the per-family reports, which remain the detailed record.

## Verdicts by family (primary tier = gpt-4.1 unless noted)

### X2 — screening + confirmation (`x2-*-report.md`)
- **P4-X2-1: SUPPORTED.** Confirmation estimate +0.925, LB95 +0.708 > 0.50
  with screening-matched sign (exact CP fallback, Bonferroni, conservative).

### D1 — presentation main effects (`d1-report.md`)
- gpt (primary): **all four claims NOT SUPPORTED** (grand mean Y = 0.2547;
  all Holm-p ≥ 0.766). Presentation factors move nothing detectable in the
  primary tier.
- cvx (secondary mirror): W, WL, ML **supported** — the secondary vendor is
  presentation-sensitive where the primary is not (replication tier only).

### D2 — role/word decomposition (`d2-report.md`)
- gpt: **P4-D2-1 and P4-D2-4 SUPPORTED** (+0.725, +0.7875); P4-D2-2 not
  supported (word channel null); P4-D2-3 payoff-dominant branch.
- cvx: D2-1/2/4 all supported; D2-3 payoff-dominant.

### D3 — labeled-option bias (`d3-report.md`)
- gpt (primary): **P4-D3-1 NOT SUPPORTED** (mean D_ep −0.1806, LB −0.2778);
  support-only Dirichlet P(first-only > rock-only) = 0.0001 — the bias runs
  toward rock-only, opposite the registered direction.
- cvx: supported (+0.2431, LB +0.1389; P = 1.0000) — vendors disagree in
  sign; replication tier only.

### E — δ-sensitivity (`e-report.md`)
- **All four assays: CORNER-CONFOUNDED (registered branch i)** — occupancy
  gates invalid at ceiling/floor; explicitly NOT evidence of
  δ-insensitivity. Holm placeholders p=1 as registered. 160/160 usable
  episodes; 2 provider-failure non-observations disclosed.

### F — adversarial exploitability (`f-report.md`)
- **P4-F-1 (primary conjunction): ONLY-FIRST registered branch.**
  Δ(wsls−fo) = +0.126, LB95 +0.093 > 0; but Ū_wsls = +0.008, LB95 −0.008.
  The WSLS-targeter decisively out-exploits first-order tracking, yet does
  not itself profit against the subject.
- Holm m=6 secondaries: **ngram2 exploits the subject** (+0.215,
  supported); **fo-tracker is significantly NEGATIVE** (−0.118 — the
  subject beats first-order tracking); ngram3/wsls/switcher/shuffled n.s.
- Directional (shuffled < fo): **NOT SUPPORTED** (Δ(fo−shuffled) −0.083,
  LB −0.116) — order carried no exploitable signal beyond marginals here;
  indeed the shuffled control did (nominally) better.
- Cross-vendor gemini tier: **DESCRIPTIVE-ONLY** (demoted; sentinel alert
  6, operator ruling 2026-07-28 — see §Sentinel). Descriptively: fo-tracker
  +0.159 exploits gemini (sign opposite gpt), wsls −0.090.
- Per-arm confirmatory status (architect ruling, verbatim): fo-tracker
  CONFIRMATORY (sealed-complete alias); wsls-targeter CONFIRMATORY
  (sealed-complete, operational pins only); ngram2, ngram3, switcher-r26,
  shuffled-history CONFIRMATORY UNDER COMPLETION AMENDMENT.

## Sentinel stability (v2a × gemini; full trajectory, both ends)

10 → 9 → 9 → 8 → 8 → 7* → [re-baseline 10] → 6* → 7* → 6* → 7*
(* = rule (c) fired; checks 5/7/8 dispositioned contemporaneously — alert-5
memo, check-7/8 decision entries; checks 9/10 evaluated LATE — alert-6
memo). The series does NOT close clean; earlier "closes 10/10" statements
were dispatch-count console lines and are struck. The check-6 re-baseline
read of 10/10 is descriptively the probable outlier (post-hoc,
non-decisional). All gpt sentinel cells 10/10 throughout; v1 and fallback
gemini cells in band.

## Amendments and disclosures (registration character)

- Original registration 2026-07-24 (freeze packet, predicates.md, sealed
  schedule). F completion amendment 2026-07-28 (f-opponent-specs.md §9.1):
  outcome-blind, zero-spend, fixtures-as-selftests; per-arm status above.
- Sentinel alert 5 (check 5) → operator re-baseline decision + riders;
  alert 6 (checks 9–10, evaluated late) → Option A: alerts stand, gemini F
  tier descriptive-only, F h2 admitted with disclosure. Option B
  (re-evaluate the rule on the data it fired on) rejected on principle.
- Provider-failure non-observations: 24 total (2 E, 22 F), signature-based
  registered rule, spend counted, never mapped to episodes. The mechanical
  scan is the ledger of record (supersedes the in-run narrative count of 3).
- Replay-checker corrections during step 8 (checker-side only, no sealed
  artifact or stored byte touched): the sentinel third-cell switch donor
  deltaPct is now mirrored in the replay re-derivation (it was applied at
  dispatch/enforcement but missing from the checker — provenance instance
  5's class); the earlier `_e_sched_seed` 1-based/0-based indexing fix is
  the same class.

## Limitations (registered for the paper and Phase 5)

1. **Promised-control-not-mechanically-coupled** (strongest instance:
   sentinel checks 9–10 evaluated late while dispatch proceeded). Phase 5
   requirement: dispatch gates demand a positive evaluator attestation for
   the preceding check — absence of evaluation fail-closes; "no fire seen"
   is never "no fire". Implemented for this repo in the driver's sentinel
   attestation gate; console dispatch counts renamed so they cannot read as
   rule outcomes.
2. E's corner-confounded branch leaves δ-sensitivity unmeasured, not
   refuted; the assay design needs interior occupancy to bind.
3. Cross-vendor tiers are replication commentary, not confirmatory
   evidence, and disagreed in sign twice (D3, F fo-tracker).
4. The gemini sentinel cell drifted throughout; all gemini-tier F numbers
   carry that caveat even descriptively.
