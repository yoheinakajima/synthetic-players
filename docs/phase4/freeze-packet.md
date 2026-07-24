# Phase 4 Freeze Packet — APPROVED

**Status: APPROVED — EXECUTING.** Approval recorded **2026-07-24T15:18:49Z (UTC)**
via the structured decision form: *freeze approved, Gate 0 authorized*; cross-vendor
subject **claude-haiku-4-5 confirmed**; GitHub anchoring: user will connect the
integration (pending user action; local sealing proceeds and anchoring attaches when
connected). Execution follows the order in §Execution below — nothing outside the
sealed schedule runs.

*(Pre-approval status, kept for provenance: packet prepared 2026-07-24 as COMPLETE
and INERT against the Phase 4 sign-off response, approved-with-amendments, all
amendments incorporated; no Phase 4 LLM call was made before the approval timestamp
above. Phase 3 + X1 remain immutable; their report amendments (§B) are editorial and
evidence-preserving.)*

**Gate 0 (2026-07-24T15:23–15:25Z): EXECUTED — FAIL; phase blocked at step 1, escalated.**
gpt-4.1 verified in full (response IDs, exact revision `gpt-4.1-2025-04-14` on every
call, clean `stop`, token accounting, parser round-trip on attempt 0).
claude-haiku-4-5: IDs / returned revision `claude-haiku-4-5-20251001` / token
accounting verified, **but the model cannot complete a turn at the protocol's
maxTokens=16** — it opens with analysis prose and truncates (`stop_reason=max_tokens`;
a logged 64-token diagnostic still truncated mid-payoff-enumeration). The protocol's
single retry rescues it (exact `'J'`, `end_turn`, parsed) but would inject the retry
suffix into claude's effective stimulus on essentially every decision, while gpt-4.1
saw zero retries in all of Phase 3 — a model×stimulus confound. 8 infrastructure calls
spent (≤10 budget), all event-sourced (`gate0_*`, `gate0diag_*`); full record in
[`gate0-report.md`](gate0-report.md). Per the frozen rule, this failure is escalated
for a registered amendment, not worked around. Experimental rows remain blocked;
step-2 engine work (model-agnostic, zero LLM calls) proceeds; registry sealing (step
3) waits on the amendment because cross-vendor arms bind the model string.

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

## §H Open items — status at approval (2026-07-24)

1. **GitHub connection** for external anchoring: user opted **connect now** — pending
   the user action; until attached, local sealing only, honestly labeled.
2. **Cross-vendor model:** ✅ **claude-haiku-4-5 CONFIRMED** (Replit AI Integrations
   Anthropic route — no API key, billed to credits).
3. **Semantic-equivalence third rater** (default: gemini-class small model) and the
   two human readers for the §2.2 instrument — still open; does not block execution
   (rating calls are a separate 18-call line item).
4. **ε for the substitution estimand** TOST band — still open (human phase; table in
   that prereg).
5. **The one-line approval:** ✅ **GIVEN 2026-07-24T15:18:49Z** (structured form,
   option "Approve — freeze the design and authorize Gate 0").
