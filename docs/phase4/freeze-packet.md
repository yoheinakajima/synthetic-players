# Phase 4 Freeze Packet — submitted for one-line approval

**Status: COMPLETE and INERT.** Everything below is sealed design; **no Phase 4 LLM
call runs until the approval line is given.** Prepared 2026-07-24 against the Phase 4
sign-off response (approved-with-amendments; its amendments are incorporated here in
full). Phase 3 + X1 remain immutable; their report amendments (§B below) are editorial
and evidence-preserving.

**The approval being requested:** *"Approved: run Phase 4 as frozen in
docs/phase4/freeze-packet.md."* — with the open items in §H resolved or explicitly
deferred.

| § | Deliverable | Where | Status |
|---|---|---|---|
| A | Full predicate table (estimand/unit/contrast/direction/threshold/CI method/α/multiplicity/conditionals/degenerate rules/config/arms/verdict branches per claim) | [`predicates.md`](predicates.md) | ✅ frozen |
| B | X1 amendments: prompt disclosure + invariance table; parser audit (all raw completions, zero retries, transcripts); semantic-equivalence instrument; report language (headline softened to the approved sentence, episode-level corners with CP bounds, result-informed-but-prospectively-registered provenance with exact timestamps, no policy-determinism claim, positioning §8, provenance appendix §7) | [`x1-prompt-disclosure.md`](x1-prompt-disclosure.md) · [`x1-parser-audit.md`](x1-parser-audit.md) · [`x1-semantic-equivalence.md`](x1-semantic-equivalence.md) · [`../phase3-report.md`](../phase3-report.md) | ✅ done (human audit + 18 rating calls pending, §H) |
| C | Registry v3: 44 new templates with real sha256s, 250 sealed arms (D1 64×2 models, D2 8×2, D3 36×2, E 4×2, X2 10+2, F 11, sentinels 3), pinned dynamic bindings, disjoint seed plan (2001–3092; X2 screening reuses X1 seeds 1–10 by rule; sentinel pool 9001+), sealed interleaved execution schedule (mulberry32 seed 20260724) | [`registry-v3-manifest.md`](registry-v3-manifest.md) · [`arms.json`](arms.json) · [`execution-schedule.json`](execution-schedule.json) | ✅ built, append-only verified; external anchor pending GitHub (§H) |
| D | X2 diff packet: k=6 span decomposition with byte-verified endpoints, ladders, frozen selection + confirmation rules, ≤2,226 calls | [`x2-diff-packet.md`](x2-diff-packet.md) | ✅ frozen |
| E | F stabilization packet: 30-round gate **FAILED** (\|Δstay\| = 0.0512 > 0.05) → registered reversion to 50 rounds, switcher r26; full trajectory-window evidence | [`f-stabilization.md`](f-stabilization.md) | ✅ sealed (honest fail) |
| F | Provider & provenance: named models (gpt-4.1 / **claude-haiku-4-5**), proxy-condition table, Gate-0 live verification plan, 15-field capture + server-side enforcement design, anchoring plan | [`provider-packet.md`](provider-packet.md) | ✅ frozen (Gate 0 runs first post-approval) |
| G | Budget: per-block calls/tokens/dollars at 50-round F, 30-round alternative shown, retry allowance, sentinel burn, rating calls, Gate-0, hard kill-switch table (global 21,000) | [`budget.md`](budget.md) | ✅ frozen |

## Execution order after approval (sign-off §14, unchanged)

1. Gate 0 provider verification (~10 infra calls) · 2. engine enforcement + capture
(§F.3) with replay extension · 3. seal registry v3 (flip `4-proposed` → sealed) +
GitHub signed tag/release (if connected) · 4. baseline sentinel + X2 screening + D1 →
D2 → D3 per sealed schedule · 5. X2 confirmation (if candidate) · 6. E selection
written to event store → E · 7. F · 8. replay-verify all → mechanical adjudication →
layer-2 companion → interpretation. Human-scaffold comparison stays a separate future
registration ([`../substitution-estimand-preregistration.md`](../substitution-estimand-preregistration.md), ε pending).

## §H Open items needing the user (none block packet review)

1. **GitHub connection** for external anchoring (signed tag + release). Without it:
   local sealing only, honestly labeled.
2. **Cross-vendor model confirmation:** claude-haiku-4-5 as named. (Uses Replit AI
   Integrations — no API key needed, billed to credits.)
3. **Semantic-equivalence third rater** (default: gemini-class small model) and the
   two human readers for the §2.2 instrument.
4. **ε for the substitution estimand** TOST band (human phase; table in that prereg).
5. **The one-line approval.**
