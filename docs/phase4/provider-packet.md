# Provider & Provenance Packet (freeze packet §F)

## 1. Named models (sign-off §8: one exact model, no menus)

- **Primary subject:** `gpt-4.1` via Replit AI Integrations (OpenAI-compatible route);
  expected returned revision **`gpt-4.1-2025-04-14`** — the revision returned on all
  5,830 Phase 3 calls. Any other returned identifier triggers the sentinel alert rule.
- **Cross-vendor subject:** **`claude-haiku-4-5`** via Replit AI Integrations
  (Anthropic route; `activegraph` 1.10 ships a native `anthropic` provider, so the
  engine uses a first-class provider class, not an adapter shim). Rationale: small,
  fast, standard chat model from a second vendor; no extended-reasoning mode engaged;
  supports temperature 0.7 / maxTokens 16. This route uses Replit AI Integrations —
  no vendor API key is required and usage is billed to workspace credits. The exact
  returned model identifier string will be archived on every call and reported; if the
  provider does not expose a finer revision string than the requested ID, that is
  disclosed and no revision-pinning claim is made beyond the returned string.
- **Decoding-equivalence disclosure (frozen limitation):** matching temperature=0.7 /
  maxTokens=16 across vendors equates request parameters, **not** sampling behavior;
  no cross-vendor claim will be phrased as "under identical decoding", only "under
  matched request parameters".

## 2. Proxy conditions (sign-off §8) — status

The Replit AI Integrations endpoint is a managed billing proxy (OpenAI-compatible /
Anthropic-compatible). Conditions and verification:

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
finish_reason `stop`; token accounting present; parser round-trip on a fixed known
prompt. Any failure blocks the phase and is escalated, not worked around.

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

## 4. Anchoring (sign-off §11)

External anchoring = GitHub: registry v3 sealing commit gets a **signed tag** and a
release carrying `docs/phase4/arms.json`, the registry file, and a sha256 checksum
manifest; the release URL + tag are then cited in the freeze packet as the public
timestamp. Until the user connects the GitHub integration this remains **PENDING
(user action)** — the packet does not claim external anchoring, only local sealing.
Language rule (standing): "externally anchored", never "cryptographically immutable".
