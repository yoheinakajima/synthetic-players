# Provider & Provenance Packet (freeze packet §F)

## 1. Named models (sign-off §8: one exact model, no menus)

- **Primary subject:** `gpt-4.1` via Replit AI Integrations (OpenAI-compatible route);
  expected returned revision **`gpt-4.1-2025-04-14`** — the revision returned on all
  5,830 Phase 3 calls. Any other returned identifier triggers the sentinel alert rule.
- **Cross-vendor subject (amendment A1, 2026-07-24):** **`gemini-2.5-flash`** via
  Replit AI Integrations (Gemini route). Replaces `claude-haiku-4-5`, which failed
  Gate 0 round 1 behaviorally: it cannot complete a turn at the protocol's
  maxTokens=16 (opens with analysis prose, truncates at `max_tokens` even in a
  64-token diagnostic; its rescue-by-retry would have injected the retry suffix into
  nearly every effective stimulus — a model×stimulus confound; archived record:
  [`gate0-report-round1-claude-FAIL.md`](gate0-report-round1-claude-FAIL.md)).
  `activegraph` 1.10 ships no Gemini provider, so the engine uses
  `engine/gemini_provider.py`, a narrow adapter implementing the same `LLMProvider`
  protocol as the shipped reference providers. Registered vendor-adapter settings,
  disclosed wherever cross-vendor results are reported: `thinking_budget=0` (hybrid
  reasoning OFF, so the subject is a plain completion — the same subject class as
  gpt-4.1; `thoughts_token_count == 0` is ASSERTED per call, never assumed) and
  always-explicit `top_p=1.0` (Gemini's server-side default is not 1.0, so omitting
  the field would silently change the sampling distribution). Rationale otherwise
  unchanged: small, fast, standard chat model from a second vendor; supports
  temperature 0.7 / maxTokens 16 — verified empirically in Gate 0 round 2 (bare-letter
  reply on attempt 0, 1 output token, clean `STOP`). This route uses Replit AI
  Integrations — no vendor API key is required and usage is billed to workspace
  credits. The exact returned model identifier string is archived on every call and
  reported; revision disclosure: the route returns `model_version = "gemini-2.5-flash"`,
  the family ID only, so no revision-pinning claim is made beyond the returned string.
- **Decoding-equivalence disclosure (frozen limitation):** matching temperature=0.7 /
  maxTokens=16 across vendors equates request parameters, **not** sampling behavior;
  no cross-vendor claim will be phrased as "under identical decoding", only "under
  matched request parameters".

## 2. Proxy conditions (sign-off §8) — status

The Replit AI Integrations endpoint is a managed billing proxy (OpenAI-compatible /
Gemini-compatible). Conditions and verification:

| Condition | Static status | Live verification (Gate 0) |
|---|---|---|
| No prompt rewriting / injection | No rewrite layer is part of the product's documented behavior; engine archives the exact request body it sends | request-body sha archived; returned completion consistent with archived body; any documented-behavior change disclosed |
| No model fallback / substitution | requested model string archived per call | returned model identifier compared to requested on **every** call (alert rule (a)) |
| Provider response IDs preserved | NOT captured in Phase 3 (disclosed gap) | Gate 0 asserts non-empty response ID on both routes; capture mandatory thereafter |
| Full request/response archiving | engine-side (event store), independent of proxy | replay byte-compare extended to request-body sha |
| Routing metadata recorded | base-URL host + integration slug recorded as `providerRoute` | archived per call |

**Gate 0 (first post-approval action, before any experimental row):** ~10 calls total
(≈2 per model per route), logged as infrastructure (excluded from analysis, counted in
budget), asserting: response ID non-empty; returned model string equals expectation;
finish_reason clean per the registered stop mapping (OpenAI `stop` ↔ Gemini `STOP`;
truncation = failure); token accounting present, and for gemini additionally
`thoughts_token_count == 0` (thinking verifiably off); parser round-trip on a fixed
known prompt. Any failure blocks the phase and is escalated, not worked around.

## 3. Engine capture & enforcement design (sign-off §10; implemented post-approval, before any run)

Per-call record (15 fields, extending the current `llm.requested`/`llm.responded`
events, which already archive rendered system/user messages, raw completions, token
counts, and requested/returned model):

1. sealed arm ID · 2. template ID + template sha256 · 3. dynamic substitutions (full
map) · 4. canonical rendered-bundle sha256 · 5. complete rendered messages *(already
stored)* · 6. request-body sha256 · 7. raw completion *(already stored)* · 8. parsed
action + displayed-option index · 9. `PARSER_VERSION` constant · 10. engine code
commit · 11. provider route (host + integration slug) · 12. provider response ID ·
13. requested model + returned model identifiers *(already stored)* · 14. timestamps
(request/response) *(already stored)* · 15. attempt number linked to episode + retry
cause *(attempt already stored; cause added)*.

Server-side enforcement (rejection, not convention): a run request must name a sealed
arm ID; the engine resolves template + bindings from the sealed registry copy, refuses
unknown substitution keys, refuses values outside the arm's pinned bindings, recomputes
the template sha at run start and refuses on mismatch, stamps `PARSER_VERSION`, and
refuses any run while the global or block kill-switch counter is at cap. Replay
verification extends to: re-render → byte-compare bundle sha, request-body sha, and
per-call parsed action. Every provider call (success, retry, failure, sentinel, Gate-0)
increments the budget counters transactionally **before** dispatch.

D2 label-role separation: the per-call record stores the DISPLAYED option chosen
(field 8) and the arm's labelRoleMap; strategic role is derived in analysis only.
D3: the roleMapping, displayOrder, rendered optList/beatsLine are archived per episode.
F shuffled-history control: for every decision, the seed-recorded permutation and the
exact shuffled prefix shown are archived (fields 3/5 cover this via substitutions).

**Implementation status (2026-07-24, step 2 of the frozen execution order): IMPLEMENTED.**
Files: `engine/phase4.py` (arm store, enforcement, transactional budget ledger),
`engine/phase4_runner.py` (capture runner, dry-run, extended replay, write-once
resolutions), `engine/phase4_providers.py` (OpenAI provider subclass adding
response-ID + request-sha provenance; request construction byte-compatible with the
Phase 3 provider — `top_p` still omitted at 1.0), `engine/provenance.py` (canonical
JSON, shas, request-body mirrors), plus additive render branches in
`engine/llm_subject.py` (`pd-os-*`, `pd-rep-*`, `pd-x2-*`, `rps-sym-v1`; sealed
Phase 3 branches untouched — Phase 3 replay re-verified byte-exact after the change).
Engine-pinned values registered at implementation time:

* `PARSER_VERSION = "strip-upper-exact-v1.p4.2026-07-24"` (field 9).
* Request-body sha (field 6) is computed over the DETERMINISTIC request fields only
  (provider tag, model, system + messages, max_tokens, temperature, top_p-if-sent;
  Gemini: generation_config incl. explicit top_p and thinking_budget=0); the
  transport timeout is excluded. Each provider ALSO computes the sha of what it
  actually sent (`provider_meta.request_body_sha256`); the runner asserts
  mirror == actual on EVERY call and hard-aborts the run on divergence, so capture
  can never silently drift from the wire.
* Gemini hidden-reasoning guard (§2 "asserted per call" commitment): every gemini
  call's `provider_meta.thoughts_token_count` must be present and exactly 0. The
  assertion runs after the response event is archived (evidence preserved) and
  before parsing (no decision legitimizes the trial); violation or absence of the
  field hard-aborts the run with spend kept.
* D3 render rule pinned exactly: optList = displayOrder joined with `", "` and final
  `" or "` (`X, Y or Z`); beatsLine = `<winner> beats <loser>.` sentences (trailing
  period) over the three beat relations in DISPLAY order, joined by single spaces
  (`X beats Z. Y beats X. Z beats Y.`). Retry suffixes are now placeholder-formatted
  (rps-sym-v1's `{optList}`); formatting is identity for the sealed Phase 3 suffixes
  (no braces), so recorded Phase 3 runs replay byte-identically.
* Startup self-check: the engine recomputes all 49 template shas (44 v3 + 5 sealed
  Phase 3) from the registry with the Python canonical serializer and compares
  byte-for-byte against `arms.json`; ANY mismatch disables Phase 4 endpoints (503)
  while sealed Phase 3 endpoints stay untouched. Node↔Python canonical parity is
  therefore verified at every boot, never assumed.
* Budget ledger `engine/data/budget.db` (sqlite, BEGIN IMMEDIATE): one row reserved
  BEFORE each provider dispatch, including transport retries — burned calls are never
  invisible. Caps enforced: global 21,000 · D1+D2+D3 4,300 · E 1,800 · X2 2,700 ·
  F 11,600 · overhead (sentinels + ratings + Gate-0) 900 · single-episode runaway
  guard 260. Gate-0 spend backfilled exactly: 15 calls, 2,972 in / 63 out tokens
  (`gate0_1784906629_0933fb21` 7 calls incl. the 64-token diagnostic,
  `gate0_1784908582_1a0189ea` 2 calls from the aborted round-2 start,
  `gate0_1784908630_49d774e7` 6 calls, round-2 PASS).
* Live-run gate: Phase 4 run requests are mechanically REFUSED (HTTP 403) while
  `registryVersion` ends in `-proposed`; only `dryRun` (enforcement + render + shas;
  zero events, zero spend, zero provider construction) is allowed pre-seal.
  RESOLVED-BY-* templates additionally require a write-once resolution record,
  event-sourced before the enforcement copy (`E-dselected`, `X2-conf-lo`,
  `X2-conf-hi`); re-resolution is refused — changing one is an amendment.
* F opponents (fo-tracker, ngram2, ngram3, wsls-targeter, switcher-r26,
  shuffled-history) are NOT yet implemented in the engine; enforcement refuses such
  runs loudly ("not implemented") until the F-block engine work lands (step 4+).
* Verification: `engine/selftest_phase4.py` (48 checks, temp DBs, fake in-process
  provider, zero live calls / zero real spend): Node↔Python sha parity; the full
  enforcement rejection matrix (seed/model/protocol/matrix/seats/sentinel windows);
  ledger caps, backfill, runaway guard; write-once resolutions; dry-run zero-spend;
  end-to-end capture→replay with bundle + request-body shas byte-verified and parsed
  actions re-derived; invalid-trial flow; mirror-vs-actual divergence abort. HTTP
  smoke additionally verified /phase4/status, D1 + D3 dry-runs, the 403 pre-seal
  gate, a 400 tampered-matrix refusal, and a byte-exact Phase 3 replay regression.

## 4. Anchoring (sign-off §11)

External anchoring = GitHub: registry v3 sealing commit gets a **signed tag** and a
release carrying `docs/phase4/arms.json`, the registry file, and a sha256 checksum
manifest; the release URL + tag are then cited in the freeze packet as the public
timestamp. Until the user connects the GitHub integration this remains **PENDING
(user action)** — the packet does not claim external anchoring, only local sealing.
Language rule (standing): "externally anchored", never "cryptographically immutable".

**Execution status: EXECUTED 2026-07-24** (registered plan above kept verbatim for
provenance). Seal commit `d24ee94e` pushed to `main`; annotated tag `phase4-v3-seal`
+ release published 2026-07-24T19:04:16Z with assets registry.json / arms.json /
SHA256SUMS.txt. **One deviation, disclosed:** the plan said "signed tag" — no GPG
signing key exists in the execution environment, so the tag is annotated, not
GPG-signed; the release timestamp is the anchor. Full record:
[`seal-record.md`](seal-record.md).
