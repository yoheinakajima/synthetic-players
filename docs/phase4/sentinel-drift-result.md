# Sentinel catch — behavioral drift of an unversioned endpoint (first-class result)

Registered 2026-07-24 at the alert-5 resumption (sentinel-alert-5-memo.md
§Decision, rider 4). Descriptive/monitoring result, outside the confirmatory
families and never pooled with experimental inference; all numbers re-verified
at step-8 replay.

## Result

Between the sealed baseline (check 0, pre-X2-screening) and check 5
(post-X2-confirmation), gemini-2.5-flash's round-1 cooperation in sentinel cell
`p4-sent-v2a` (repeated-PD v2a wording, horizon forced to 1, canonical payoffs,
temperature 0.7, seat 1) eroded monotonically:

| check | 0 | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|---|
| cooperate /10 | 10 | 9 | 9 | 8 | 8 | **7 → ALERT** |

crossing the frozen alert threshold (rule (c), |Δcount| ≥ 3 vs sealed baseline)
at check 5. Same-window companions were flat: gpt-4.1 at 10/10 in all three
cells at every check; gemini v1 and third cells at baseline throughout. Every
deviant episode is a clean, valid, single-token defect choice (finish_reason
`stop`, zero retries, zero parse anomalies): a distributional behavior change,
not an infrastructure change.

## Why this is the mechanism the protocol exists to demonstrate

- **The endpoint is unversioned.** The returned model identifier never changed,
  so version pinning (rule (a)) was structurally blind to whatever changed
  provider-side; finish/retry surveillance (rule (b)) saw nothing either.
- **The behavioral fingerprint (rule (c)) caught it** — 60 low-cost calls per
  boundary against a sealed baseline — and froze the study AT a block boundary,
  before either exposed block (E: 80 gemini episodes; F: 100) dispatched.
  Contaminated confirmatory spend: zero.
- **Detection latency is quantified and disclosed.** The drift was ongoing from
  check 1 but sub-threshold for four checks; the frozen count rule
  (deliberately insensitive to single-episode noise at n=10) fired on
  cumulative erosion. Each intermediate check individually passed — the full
  trajectory above is part of the record.
- **Consequence handling was pre-committed, not improvised.** Sealed rule:
  freeze → disclose → decision memo → operator decision. Adopted: re-baseline
  at a fresh pre-E read (not the alert-check snapshot), doubled gemini cadence
  through E/F with the same tripwire armed on the new baseline,
  regime-indexed reporting (R1 = D/X2 era, R2 = post-re-baseline), and this
  write-up. Completed blocks stand on within-block randomization; nothing was
  excluded, re-run, or silently pooled.

## Boundaries of the claim

Monitoring cells are never pooled into experimental inference; n=10 per cell
per check bounds precision; the cause of the drift (provider model update,
decoding change, upstream infrastructure) is unidentifiable from behavior alone
and no causal attribution is claimed. What is claimed: a reproducible,
mechanically adjudicated detection record showing that behavioral
fingerprinting catches subject drift that version pinning cannot see, on a live
provider endpoint, mid-study, with the freeze landing before any contaminated
spend.
