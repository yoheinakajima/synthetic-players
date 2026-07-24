---
name: ActiveGraph engine sidecar
description: Quirks of the activegraph package (v1.10.x) and the Python game engine sidecar design
---

# ActiveGraph (v1.10.0, pinned) quirks
- `Event` is importable from top-level `activegraph`; the module is `activegraph.core.event` (singular).
- Inside behaviors you get a restricted `BehaviorGraph`: only `add_object(type, data)`, `emit(event_type, payload)`, `patch_object(target, updates)`, `get_object`, relations. **No** `objects()` query and no actor/caused_by kwargs — the runtime fills provenance. Read state via `ctx.view.objects(type)`.
- Outside behaviors, `graph.emit` requires a full `Event(id=graph.ids.event(), type=..., payload=..., actor=...)`.
- Forking: `SQLiteEventStore.fork_run(...)` (copy prefix, inclusive cutoff) + `Runtime.load` of the fork is simpler than `rt.fork` (avoids strict-replay behavior re-firing).
- **Why:** behaviors must be deterministic; RNG stream position is stored per round (`rngCalls`) so replay/fork re-derives the exact stream offset.

# Determinism / TS parity
- Python port of mulberry32 must mask to 32 bits and mimic `Math.imul` / `>>>`.
- JS `Number.toFixed(2)` rounds the exact binary value with ties toward +infinity ("larger n" rule) — Python's `f"{x:.2f}"` uses banker's rounding and diverges (e.g. 1.625 → "1.62" vs "1.63"). See `_fmt` in `engine/strategies.py`.
- Parity verified: all 64 strategy matchups byte-identical between TS and the engine.

# How to apply
- Engine is internal-only: second service in api-server artifact.toml with `paths = []`, dev cwd is the artifact dir (`uv run python engine/server.py`), prod cwd is repo root. Express reaches it via ENGINE_URL.
- Any new strategy must go in engine/strategies.py and consume RNG in a fixed order (p1 then p2 per round).

# Engine-live LLM seats (Phase 3 pattern)
- Every live model call is event-sourced as an `LLMCache` event keyed by prompt
  hash; replay reads the cache instead of the provider and must report
  `liveCalls: 0`. **Prompt hashes must be unique per seat+round context** — in
  self-play both seats can see byte-identical histories, so bake an explicit
  seat tag into the prompt text or the two seats collide on one cache entry.
- OpenAI-compatible calls go through a client whose base URL/key come from the
  AI-Integrations env; gpt-4.1 is a non-reasoning model — tiny `maxTokens`
  (16) is safe for single-token action answers, and `temperature`/`seed` are
  honored (unlike the gpt-5 family, which pins sampling).
- **Node→engine calls for LLM runs need a long-timeout undici dispatcher.**
  Default fetch aborts when response headers take >5 min; a 100-call self-play
  run near that edge gets marked failed client-side while the engine keeps
  burning real provider calls — and failed rows carry no runMeta, so the burned
  calls become invisible to budget accounting. Give the LLM-run route its own
  `Agent({ headersTimeout, bodyTimeout })` of an hour+.
