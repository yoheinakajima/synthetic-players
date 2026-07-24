"""Phase 4 provenance primitives (freeze packet §F.3 / sign-off §10).

Shared, dependency-light helpers used by the enforcement layer, both
providers, the live runner, and replay. Everything here is deterministic:
the same inputs must produce the same bytes in live capture and in replay,
years apart.

Canonical JSON parity: `canonical_json` mirrors the Node builder's
`canonical()` (scripts/build-registry-v3.mjs) — sorted keys at every level,
arrays in order, JSON.stringify-compatible scalar encoding. Parity is not
assumed: the engine self-check recomputes every template sha in arms.json
and refuses Phase 4 traffic on any mismatch.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
from functools import lru_cache
from typing import Any
from urllib.parse import urlparse


def canonical_json(v: Any) -> str:
    """Recursive canonical serializer, byte-compatible with the Node one."""
    if isinstance(v, list):
        return "[" + ",".join(canonical_json(x) for x in v) + "]"
    if isinstance(v, dict):
        return (
            "{"
            + ",".join(
                json.dumps(k, ensure_ascii=False) + ":" + canonical_json(v[k])
                for k in sorted(v.keys())
            )
            + "}"
        )
    # scalars: JSON.stringify semantics (no ASCII escaping of unicode)
    return json.dumps(v, ensure_ascii=False)


def sha256_hex(s: str | bytes) -> str:
    b = s.encode("utf-8") if isinstance(s, str) else s
    return hashlib.sha256(b).hexdigest()


def template_sha(spec: dict) -> str:
    """Per-template sha over canonical JSON — must equal arms.json values."""
    return sha256_hex(canonical_json(spec))


def bundle_sha256(system: str, user: str) -> str:
    """Rendered-bundle sha per the registered rule (registry-v3-manifest.md):
    sha256 of `system + "\\x1e" + user` after dynamic-field substitution."""
    return sha256_hex(system + "\x1e" + user)


# ── request-body mirrors ────────────────────────────────────────────────────
# The sha is over the DETERMINISTIC request fields (stimulus + sampling), not
# transport details (timeout). Each provider ALSO computes the same sha from
# the kwargs it actually sends (provider_meta["request_body_sha256"]); the
# runner asserts mirror == actual on every call, so the mirror can never
# silently drift from what reached the wire.

def openai_request_body(*, model: str, system: str, user: str,
                        max_tokens: int, temperature: float, top_p: float) -> dict:
    """Mirror of activegraph OpenAIProvider.complete() construction for
    non-reasoning chat models: system+user messages, max_tokens, temperature,
    top_p included only when < 1.0 (the provider omits it at 1.0)."""
    body: dict[str, Any] = {
        "provider": "openai",
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "max_tokens": int(max_tokens),
        "temperature": float(temperature),
    }
    if top_p < 1.0:
        body["top_p"] = float(top_p)
    return body


def gemini_request_body(*, model: str, system: str, user: str,
                        max_tokens: int, temperature: float, top_p: float,
                        thinking_budget: int) -> dict:
    """Mirror of engine/gemini_provider.py construction: system_instruction,
    single user content, explicit top_p (registered vendor-adapter setting),
    thinking_budget (registered, 0 = hybrid reasoning off)."""
    return {
        "provider": "gemini",
        "model": model,
        "system_instruction": system,
        "contents": [{"role": "user", "text": user}],
        "generation_config": {
            "max_output_tokens": int(max_tokens),
            "temperature": float(temperature),
            "top_p": float(top_p),
            "thinking_budget": int(thinking_budget),
        },
    }


def request_body_sha(body: dict) -> str:
    return sha256_hex(canonical_json(body))


# ── engine code commit (field 10) ──────────────────────────────────────────

_REPO_ROOT = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")
)


@lru_cache(maxsize=1)
def engine_commit() -> dict:
    """Git identity of the engine code at process start. Captured once;
    'unknown' is a disclosed value, never a crash."""
    try:
        sha = subprocess.run(
            ["git", "-C", _REPO_ROOT, "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=10,
        ).stdout.strip()
        dirty = bool(subprocess.run(
            ["git", "-C", _REPO_ROOT, "status", "--porcelain"],
            capture_output=True, text=True, timeout=10,
        ).stdout.strip())
        if sha:
            return {"sha": sha, "dirty": dirty}
    except Exception:
        pass
    return {"sha": "unknown", "dirty": True}


# ── provider route (field 11) ───────────────────────────────────────────────

def provider_route(kind: str) -> dict:
    """Route identity: base-URL host + integration slug. Loud on missing env."""
    env = {
        "openai": "AI_INTEGRATIONS_OPENAI_BASE_URL",
        "gemini": "AI_INTEGRATIONS_GEMINI_BASE_URL",
    }[kind]
    base = os.environ.get(env)
    if not base:
        raise RuntimeError(f"{env} not set — cannot record provider route")
    return {
        "kind": kind,
        "host": urlparse(base).netloc,
        "integration": f"replit-ai-integrations:{kind}",
    }
