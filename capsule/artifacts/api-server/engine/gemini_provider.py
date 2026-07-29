"""Gemini provider adapter for the engine (activegraph LLMProvider protocol).

Written for Phase 4's cross-vendor arm after the registered candidate switch
(Gate 0 round 1: claude-haiku-4-5 cannot complete a turn at the protocol's
maxTokens=16 — see docs/phase4/gate0-report-round1-claude-FAIL.md).
activegraph 1.10 ships OpenAI + Anthropic reference providers only, so this
module implements the same narrow contract for the google-genai SDK,
mirroring `activegraph.llm.anthropic.AnthropicProvider`.

Registered vendor-adapter settings (disclosed wherever cross-vendor results
are reported):
  * `thinking_budget=0` — disables Gemini 2.5 hybrid reasoning so the subject
    is a plain non-reasoning completion, the same subject class as gpt-4.1.
    Without it, hidden reasoning tokens would consume the protocol's
    maxTokens=16 budget before any answer token. The adapter surfaces
    `thoughts_token_count` in provider_meta so runs can ASSERT it stayed 0
    rather than trusting the flag.
  * `top_p` is ALWAYS forwarded explicitly (the protocol pins 1.0). Gemini's
    server-side default is not 1.0, so omitting the field — the Anthropic
    convention — would silently change the sampling distribution.
  * No tool use, no native structured output, no streaming: unused by the
    protocol; requesting them fails loudly instead of being ignored.

Route env vars: AI_INTEGRATIONS_GEMINI_BASE_URL / AI_INTEGRATIONS_GEMINI_API_KEY
(Replit AI Integrations proxy; the key is a proxy token, not a vendor key).
Missing env is a loud constructor-time failure, never a silent fallback.
"""
from __future__ import annotations

import os
import time
from decimal import Decimal
from typing import Any, Mapping, Optional

from activegraph.llm.errors import LLMBehaviorError
from activegraph.llm.provider import LLMProvider
from activegraph.llm.types import LLMMessage, LLMResponse

# Per-million-token USD pricing (rates current July 2026; text modality).
# Override via `pricing=`. cost_usd is bookkeeping — budget enforcement
# counts calls, not estimated dollars.
_DEFAULT_PRICING: dict[str, dict[str, str]] = {
    "gemini-2.5-flash": {"input": "0.30", "output": "2.50"},
    "gemini-2.5-pro": {"input": "1.25", "output": "10"},
}


def _pricing_for(model: str, pricing: Mapping[str, Mapping[str, str]]) -> tuple[Decimal, Decimal]:
    """Longest-prefix family lookup. Unknown families raise — silent
    wrong pricing is a quiet lie."""
    best_key: Optional[str] = None
    for key in pricing:
        if model.startswith(key) and (best_key is None or len(key) > len(best_key)):
            best_key = key
    if best_key is None:
        raise ValueError(
            f"GeminiProvider has no pricing entry for model {model!r}; "
            "pass pricing= explicitly."
        )
    entry = pricing[best_key]
    return Decimal(str(entry["input"])), Decimal(str(entry["output"]))


class GeminiProvider(LLMProvider):
    default_model: str = "gemini-2.5-flash"

    def __init__(
        self,
        *,
        client: Any = None,
        api_key_env: str = "AI_INTEGRATIONS_GEMINI_API_KEY",
        base_url_env: str = "AI_INTEGRATIONS_GEMINI_BASE_URL",
        pricing: Optional[Mapping[str, Mapping[str, str]]] = None,
        thinking_budget: int = 0,
    ) -> None:
        self._client_override = client
        self._api_key_env = api_key_env
        self._base_url_env = base_url_env
        self._pricing: dict[str, dict[str, str]] = dict(pricing or _DEFAULT_PRICING)
        self._thinking_budget = int(thinking_budget)
        self._client_cached: Any = None
        self._base_url: Optional[str] = None

    # ---- client lazy-load ----

    def _client(self) -> Any:
        if self._client_override is not None:
            return self._client_override
        if self._client_cached is not None:
            return self._client_cached
        try:
            from google import genai
            from google.genai import types as gtypes
        except ImportError as e:
            raise RuntimeError(
                "GeminiProvider requires the `google-genai` SDK "
                "(`uv add google-genai`)."
            ) from e
        api_key = os.environ.get(self._api_key_env)
        base_url = os.environ.get(self._base_url_env)
        if not api_key or not base_url:
            raise RuntimeError(
                f"GeminiProvider needs {self._api_key_env} and "
                f"{self._base_url_env} in the environment (AI Integrations "
                "route). Refusing to fall back to vendor defaults."
            )
        self._base_url = base_url
        # api_version="" — the AI Integrations proxy serves unversioned paths
        # (/models/...:generateContent, no /v1beta prefix).
        self._client_cached = genai.Client(
            api_key=api_key,
            http_options=gtypes.HttpOptions(base_url=base_url, api_version=""),
        )
        return self._client_cached

    # ---- LLMProvider methods ----

    def complete(
        self,
        *,
        system: str,
        messages: list[LLMMessage],
        model: str,
        max_tokens: int,
        temperature: float,
        top_p: float,
        output_schema: Optional[type],
        timeout_seconds: float,
        tools: Optional[list[dict[str, Any]]] = None,
        structured_output_mode: str = "prompt",
    ) -> LLMResponse:
        if tools:
            raise LLMBehaviorError(
                "llm.invalid_request",
                "GeminiProvider does not implement tool use (unused by the protocol).",
            )
        if structured_output_mode == "native":
            raise LLMBehaviorError(
                "llm.invalid_request",
                "GeminiProvider does not implement native structured output.",
            )
        client = self._client()

        contents: list[dict[str, Any]] = []
        for m in messages:
            if m.role not in ("user", "assistant"):
                raise LLMBehaviorError(
                    "llm.invalid_request",
                    f"GeminiProvider does not map role {m.role!r} (unused by the protocol).",
                )
            contents.append(
                {
                    "role": "model" if m.role == "assistant" else "user",
                    "parts": [{"text": m.content}],
                }
            )

        config: dict[str, Any] = {
            "temperature": float(temperature),
            # Explicit ALWAYS: Gemini's server default is not 1.0 (see module docstring).
            "top_p": float(top_p),
            "max_output_tokens": int(max_tokens),
            "thinking_config": {"thinking_budget": self._thinking_budget},
        }
        if system:
            config["system_instruction"] = system

        # §F.3 field 6: sha over the ACTUAL deterministic request content
        # (transport options excluded), reshaped into the shared canonical
        # body schema. The Phase 4 runner asserts this equals its
        # independently computed mirror on every call.
        from provenance import canonical_json, sha256_hex

        actual_body = {
            "provider": "gemini",
            "model": model,
            "system_instruction": config.get("system_instruction", ""),
            "contents": [
                {"role": c["role"], "text": c["parts"][0]["text"]} for c in contents
            ],
            "generation_config": {
                "max_output_tokens": config["max_output_tokens"],
                "temperature": config["temperature"],
                "top_p": config["top_p"],
                "thinking_budget": self._thinking_budget,
            },
        }
        request_body_sha256 = sha256_hex(canonical_json(actual_body))
        if self._base_url:
            # Per-request http_options REPLACES client-level options, so
            # base_url AND api_version must ride along or the timeout
            # override would silently redirect calls to the vendor endpoint.
            config["http_options"] = {
                "base_url": self._base_url,
                "api_version": "",
                "timeout": int(float(timeout_seconds) * 1000),
            }

        t0 = time.monotonic()
        try:
            raw = client.models.generate_content(
                model=model, contents=contents, config=config
            )
        except Exception as e:
            from activegraph.llm.wire import classify_provider_exception

            raise LLMBehaviorError(
                classify_provider_exception(e),
                str(e),
                payload_extras={
                    "model": model,
                    "exception_type": type(e).__name__,
                    "message": str(e),
                },
            ) from e
        latency = time.monotonic() - t0

        cand = raw.candidates[0] if getattr(raw, "candidates", None) else None
        text = ""
        if cand is not None and getattr(cand, "content", None) is not None:
            parts = getattr(cand.content, "parts", None) or []
            text = "".join(p.text for p in parts if getattr(p, "text", None))
        fr = getattr(cand, "finish_reason", None) if cand is not None else None
        finish = getattr(fr, "name", None) or (str(fr) if fr else "EMPTY")

        um = getattr(raw, "usage_metadata", None)
        in_tok = int(getattr(um, "prompt_token_count", 0) or 0)
        out_tok = int(getattr(um, "candidates_token_count", 0) or 0)
        thoughts = int(getattr(um, "thoughts_token_count", 0) or 0)

        returned_model = getattr(raw, "model_version", "") or model
        cost = self.estimate_cost(input_tokens=in_tok, output_tokens=out_tok + thoughts, model=model)
        return LLMResponse(
            raw_text=text,
            parsed=None,
            input_tokens=in_tok,
            output_tokens=out_tok,
            cost_usd=cost,
            latency_seconds=latency,
            model=returned_model,
            finish_reason=finish,
            seed=None,  # protocol sends unseeded sampling; Gemini seed param unused
            cache_hit=False,
            provider_meta={
                "response_id": getattr(raw, "response_id", "") or "",
                "model_version": getattr(raw, "model_version", "") or "",
                "finish_reason_raw": finish,
                "thoughts_token_count": thoughts,
                "thinking_budget": self._thinking_budget,
                "request_body_sha256": request_body_sha256,
            },
            tool_calls=None,
        )

    def estimate_cost(
        self, *, input_tokens: int, output_tokens: int, model: str
    ) -> Decimal:
        in_price, out_price = _pricing_for(model, self._pricing)
        million = Decimal("1000000")
        return (Decimal(input_tokens) * in_price / million) + (
            Decimal(output_tokens) * out_price / million
        )

    def count_tokens(
        self, *, system: str, messages: list[LLMMessage], model: str
    ) -> int:
        client = self._client()
        contents = [
            {
                "role": "model" if m.role == "assistant" else "user",
                "parts": [{"text": m.content}],
            }
            for m in messages
        ]
        # count_tokens has no system_instruction parameter; fold system into
        # the first user turn for a conservative (over-)estimate.
        if system:
            contents.insert(0, {"role": "user", "parts": [{"text": system}]})
        result = client.models.count_tokens(model=model, contents=contents)
        return int(getattr(result, "total_tokens", 0) or 0)

    def recognizes_model(self, name: str) -> bool:
        return name.startswith("gemini-")

    def supports_native_structured_output(self, model: str) -> bool:
        return False
