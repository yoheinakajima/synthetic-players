# Phase 4 Freeze Packet — APPROVED

**Status: APPROVED — EXECUTING.** Approval recorded **2026-07-24T15:18:49Z (UTC)**
via the structured decision form: *freeze approved, Gate 0 authorized*; cross-vendor
subject **gemini-2.5-flash** (amendment A1 — was claude-haiku-4-5, Gate 0 round-1 behavioral fail); GitHub anchoring: user will connect the
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
spent (≤10 budget), all event-sourced (`gate0_*`, `gate0diag_*`); full round-1 record
archived at [`gate0-report-round1-claude-FAIL.md`](gate0-report-round1-claude-FAIL.md).
Per the frozen rule, the failure was escalated, not worked around.

**Amendment A1 — registered 2026-07-24, user-selected via structured form: cross-vendor
candidate switched to `gemini-2.5-flash`; Gate 0 round 2 PASS (6 calls, report:
[`gate0-report.md`](gate0-report.md)).** What changed: the cross-vendor model string in
[`arms.json`](arms.json) / [`execution-schedule.json`](execution-schedule.json) /
[`registry-v3-manifest.md`](registry-v3-manifest.md) (regenerated pre-seal from the same
generator — registry still `4-proposed`, sealing follows in step 3); the §F provider
packet (Gemini route + adapter `engine/gemini_provider.py`; registered vendor-adapter
settings `thinking_budget=0` with a per-call `thoughts_token_count == 0` assertion, and
always-explicit `top_p=1.0`); the registered stop mapping (OpenAI `stop` ↔ Gemini
`STOP`); the budget rate note (gemini-2.5-flash rates ≤ haiku's, so every dollar figure
remains an upper bound). What did NOT change: all 49 prompts (prompt registry
byte-identical after regeneration, verified by sha256), templates and template shas,
seeds and seed ranges, episode counts, block structure and the sealed interleaved
schedule order, call budgets, and the kill-switch (21,000). Revision disclosure: the
Gemini route returns `model_version = "gemini-2.5-flash"` (family ID only, no finer
revision exposed). Experimental rows unblock after step-2 capture/enforcement and
step-3 sealing.

| § | Deliverable | Where | Status |
|---|---|---|---|
| A | Full predicate table (estimand/unit/contrast/direction/threshold/CI method/α/multiplicity/conditionals/degenerate rules/config/arms/verdict branches per claim) | [`predicates.md`](predicates.md) | ✅ frozen |
| B | X1 amendments: prompt disclosure + invariance table; parser audit (all raw completions, zero retries, transcripts); semantic-equivalence instrument; report language (headline softened to the approved sentence, episode-level corners with CP bounds, result-informed-but-prospectively-registered provenance with exact timestamps, no policy-determinism claim, positioning §8, provenance appendix §7) | [`x1-prompt-disclosure.md`](x1-prompt-disclosure.md) · [`x1-parser-audit.md`](x1-parser-audit.md) · [`x1-semantic-equivalence.md`](x1-semantic-equivalence.md) · [`../phase3-report.md`](../phase3-report.md) | ✅ done (human audit + 18 rating calls pending, §H) |
| C | Registry v3: 44 new templates with real sha256s, 250 sealed arms (D1 64×2 models, D2 8×2, D3 36×2, E 4×2, X2 10+2, F 11, sentinels 3), pinned dynamic bindings, disjoint seed plan (2001–3092; X2 screening reuses X1 seeds 1–10 by rule; sentinel pool 9001+), sealed interleaved execution schedule (mulberry32 seed 20260724) | [`registry-v3-manifest.md`](registry-v3-manifest.md) · [`arms.json`](arms.json) · [`execution-schedule.json`](execution-schedule.json) | ✅ sealed `phase4-v3` + externally anchored ([`seal-record.md`](seal-record.md)) |
| D | X2 diff packet: k=6 span decomposition with byte-verified endpoints, ladders, frozen selection + confirmation rules, ≤2,226 calls | [`x2-diff-packet.md`](x2-diff-packet.md) | ✅ frozen |
| E | F stabilization packet: 30-round gate **FAILED** (\|Δstay\| = 0.0512 > 0.05) → registered reversion to 50 rounds, switcher r26; full trajectory-window evidence | [`f-stabilization.md`](f-stabilization.md) | ✅ sealed (honest fail) |
| F | Provider & provenance: named models (gpt-4.1 / **gemini-2.5-flash** per amendment A1), proxy-condition table, Gate-0 live verification plan, 15-field capture + server-side enforcement design, anchoring plan | [`provider-packet.md`](provider-packet.md) | ✅ frozen (Gate 0 runs first post-approval) |
| G | Budget: per-block calls/tokens/dollars at 50-round F, 30-round alternative shown, retry allowance, sentinel burn, rating calls, Gate-0, hard kill-switch table (global 21,000) | [`budget.md`](budget.md) | ✅ frozen |

## Execution order after approval (sign-off §14, unchanged)

1. Gate 0 provider verification (~10 infra calls) · 2. engine enforcement + capture
(§F.3) with replay extension · 3. seal registry v3 (flip `4-proposed` → sealed) +
GitHub signed tag/release (if connected) · 4. baseline sentinel + X2 screening + D1 →
D2 → D3 per sealed schedule · 5. X2 confirmation (if candidate) · 6. E selection
written to event store → E · 7. F · 8. replay-verify all → mechanical adjudication →
layer-2 companion → interpretation. Human-scaffold comparison stays a separate future
registration ([`../substitution-estimand-preregistration.md`](../substitution-estimand-preregistration.md), ε pending).

**Execution status (2026-07-24):** 1 ✅ Gate 0 (round 2 PASS, [`gate0-report.md`](gate0-report.md))
· 2 ✅ engine capture/enforcement + replay extension implemented and verified
(implementation note in [`provider-packet.md`](provider-packet.md) §3: PARSER_VERSION,
request-body-sha definition with per-call mirror-vs-actual assertion, D3 render-rule
pinning, budget ledger with exact Gate-0 backfill, 48-check selftest, Phase 3 replay
re-verified byte-exact; live Phase 4 runs mechanically 403-refused until step 3)
· 3 ✅ registry v3 **sealed** (`phase4-v3`, 2026-07-24T18:58:15Z; post-seal registry sha `0c084b73…`) and
**externally anchored**: annotated tag `phase4-v3-seal` + GitHub release published
2026-07-24T19:04:16Z with assets registry.json / arms.json / SHA256SUMS.txt —
https://github.com/yoheinakajima/synthetic-players/releases/tag/phase4-v3-seal
(seal commit `d24ee94e`, full provenance in [`seal-record.md`](seal-record.md); tag
annotated, not GPG-signed — disclosed) · 4–8 pending.

## §H Open items — status at approval (2026-07-24)

1. **GitHub connection** for external anchoring: ✅ **resolved 2026-07-24** — user
   connected and attached the GitHub integration; seal commit `d24ee94e` pushed to
   `main` on `yoheinakajima/synthetic-players`; annotated tag `phase4-v3-seal` +
   release published 2026-07-24T19:04:16Z with checksum-manifest assets
   ([`seal-record.md`](seal-record.md)).
2. **Cross-vendor model:** ✅ resolved by **amendment A1 (2026-07-24)**: claude-haiku-4-5
   failed Gate 0 round 1 (cannot complete a turn at maxTokens=16); user-approved switch to
   **gemini-2.5-flash**, Gate 0 round 2 **PASS** (Replit AI Integrations Gemini route — no
   API key, billed to credits).
3. **Semantic-equivalence third rater** (default: gemini-class small model) and the
   two human readers for the §2.2 instrument — still open; does not block execution
   (rating calls are a separate 18-call line item).
4. **ε for the substitution estimand** TOST band — still open (human phase; table in
   that prereg).
5. **The one-line approval:** ✅ **GIVEN 2026-07-24T15:18:49Z** (structured form,
   option "Approve — freeze the design and authorize Gate 0").
