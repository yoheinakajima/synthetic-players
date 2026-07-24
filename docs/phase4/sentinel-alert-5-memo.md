# Sentinel alert — check 5, decision memo (frozen rule: freeze → disclose → memo → operator decision before resuming)

**Status: FROZEN at the X2-confirmation → E boundary.** No E-resolution write, no
block E dispatch, no further subject calls until the operator records a decision
in §Decision below. Written 2026-07-24, before any resumption.

## The alert (frozen rule c)

Check 5 (after X2-confirmation / before E, pre-resolution): cell
`p4-sent-v2a × gemini-2.5-flash` modal-action (cooperate, index 0) count **7/10**
vs sealed baseline **10/10** — Δ = 3 ≥ 3. All other cells at baseline
(gpt-4.1: 10/10 in all three cells; gemini v1 and fallback: 10/10). No rule (a)
alerts (returned model identifier unchanged) and no rule (b) alerts (all
finish_reason=stop, zero retries, zero invalid trials) — in check 5 or any
earlier check.

## Trajectory (retrospective; each prior check individually passed the frozen Δ≥3 rule)

| check | boundary | v2a×gemini seat-1 cooperate |
|---|---|---|
| 0 | baseline (sealed) | 10/10 |
| 1 | post-X2-screening | 9/10 |
| 2 | post-D1 | 9/10 |
| 3 | post-D2 | 8/10 |
| 4 | post-D3 | 8/10 |
| 5 | post-X2-confirmation | **7/10 → ALERT** |

Monotone erosion, ~1 episode per two checks — a gradual behavioral drift, not a
step change. The three check-5 deviants (seeds 9052, 9054, 9060) are clean,
valid, single-token defect choices (raw text `F`, parsed valid, displayedOption
consistent, seat 2 cooperative in all three) — not parse artifacts, not decoding
anomalies. Because the Gemini endpoint is **unversioned**, rule (a) cannot see a
silent provider-side update; the behavioral fingerprint is the only detector,
and it behaved exactly as designed.

## Contamination analysis

- **Completed blocks stand.** Checks 0–4 all passed the frozen rule; the D
  battery (D1/D2/D3 + cvx mirrors), X2 screening, and X2 confirmation closed
  under clean gates. Within-block contrasts are internally randomized and
  single-epoch; their interim verdicts are unaffected.
- **Cross-check comparability for cvx is now qualified.** The cvx subject was
  not one fixed provider state across the phase; final reporting (step 8) must
  carry this trajectory descriptively wherever cvx results are compared across
  blocks or to Phase 3. gpt-4.1 shows zero drift on any cell.
- **Pending blocks are exposed.** E contains 80 gemini episodes (of 160), F
  contains 100 (of 220). Dispatching cvx arms now samples a subject that is
  measurably not the D-battery-era subject. Within-block internal validity of
  E/F cvx contrasts is preserved by design (randomization within a single
  epoch); cross-block cvx narratives require the caveat regardless.
- **The E-resolution (Rule INTERIOR) is unaffected**: it reads only D1 gpt-4.1
  M=can cell means, and gpt-4.1 is drift-free on every sentinel cell.

## Options

1. **Resume in full, re-baselined (recommended).** Write the E-resolution and
   dispatch E per the sealed schedule, both models. Before the first post-freeze
   check, register a re-baseline record fixing the check-5 fingerprint
   (7/10) as the new reference for `p4-sent-v2a × gemini-2.5-flash` (frozen Δ≥3
   rule then applies against the new reference for E/F monitoring; the original
   trajectory continues to be reported descriptively at every subsequent check).
   Register a standing caveat: all cross-block cvx comparisons in interim and
   final reports disclose the drift trajectory. Rationale: within-block validity
   is the confirmatory unit everywhere in the registration; halting cvx would
   discard the sealed secondary-subject mirrors to protect a comparability the
   registration never claims.
2. **Resume gpt-only.** Dispatch only the gpt-4.1 episodes of E/F; the sealed
   cvx episodes are abandoned (a substantially larger deviation from the sealed
   schedule than option 1's caveat, and it forfeits the E/F secondary mirrors).
3. **Extend the freeze.** Spend additional sentinel budget re-checking the cell
   before deciding. The drift is monotone across five checks; further checks
   characterize the slope but cannot restore the earlier provider state, and E/F
   grow no more comparable by waiting.

## Decision

*(recorded verbatim on operator sign-off; the freeze stands until then)*
