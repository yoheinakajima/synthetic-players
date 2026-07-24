"""Phase 4 providers with full provenance capture (§F.3 fields 11–13).

OpenAIMetaProvider: byte-compatible reimplementation of activegraph 1.10's
OpenAIProvider.complete() for the narrow Phase 4 protocol (plain chat, no
tools, no structured output, non-reasoning model), additionally populating
provider_meta with the response ID, system fingerprint, and the sha of the
request body it ACTUALLY sent. The Phase 3 provider left provider_meta empty
— a disclosed gap; Gate 0 made response-ID capture mandatory thereafter.

Request-byte compatibility with Phase 3 is load-bearing: messages are
[system, user], `max_tokens` + `temperature` are sent, and `top_p` is
OMITTED at 1.0 exactly as the library does. The runner independently
computes a mirror sha of the same body and asserts mirror == actual on
every call, so capture can never drift from the wire silently.
"""
from __future__ import annotations

import os
import time
from typing import Any, Optional

from activegraph.llm.openai import OpenAIProvider
from activegraph.llm.types import LLMMessage, LLMResponse

from provenance import canonical_json, sha256_hex


class OpenAIMetaProvider(OpenAIProvider):
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
        # Narrow-protocol guards: anything outside the frozen subject protocol
        # is a programming error, not a request to accommodate.
        if tools:
            raise RuntimeError("OpenAIMetaProvider: tools are outside the Phase 4 protocol")
        if output_schema is not None or structured_output_mode == "native":
            raise RuntimeError("OpenAIMetaProvider: structured output is outside the Phase 4 protocol")
        if self._is_reasoning_model(model):
            raise RuntimeError(
                f"OpenAIMetaProvider: {model} is a reasoning-family model — Phase 4 subjects are plain chat models"
            )

        client = self._client()
        openai_messages: list[dict[str, Any]] = []
        if system:
            openai_messages.append({"role": "system", "content": system})
        for m in messages:
            if m.role != "user" or not isinstance(m.content, str):
                raise RuntimeError("OpenAIMetaProvider: only plain user text messages are in-protocol")
            openai_messages.append({"role": "user", "content": m.content})

        kwargs: dict[str, Any] = {
            "model": model,
            "messages": openai_messages,
            "timeout": timeout_seconds,
            "max_tokens": int(max_tokens),
            "temperature": float(temperature),
        }
        if top_p < 1.0:  # library omits top_p at 1.0 — preserved byte-for-byte
            kwargs["top_p"] = float(top_p)

        # sha over the ACTUAL deterministic request fields (transport excluded)
        actual_body: dict[str, Any] = {
            "provider": "openai",
            "model": kwargs["model"],
            "messages": kwargs["messages"],
            "max_tokens": kwargs["max_tokens"],
            "temperature": kwargs["temperature"],
        }
        if "top_p" in kwargs:
            actual_body["top_p"] = kwargs["top_p"]
        actual_sha = sha256_hex(canonical_json(actual_body))

        t0 = time.monotonic()
        try:
            raw = client.chat.completions.create(**kwargs)
        except Exception as e:
            from activegraph.llm.errors import LLMBehaviorError
            try:
                from activegraph.llm.openai import _classify_provider_exception
                reason = _classify_provider_exception(e)
            except ImportError:
                reason = "provider_error"
            raise LLMBehaviorError(
                reason, str(e),
                payload_extras={"model": model, "exception_type": type(e).__name__, "message": str(e)},
            ) from e
        latency = time.monotonic() - t0

        choices = getattr(raw, "choices", None) or []
        if not choices:
            raise RuntimeError("OpenAIMetaProvider: response has no choices")
        msg = choices[0].message
        if getattr(msg, "tool_calls", None):
            raise RuntimeError("OpenAIMetaProvider: unexpected tool_calls in a no-tools protocol")
        text = msg.content or ""
        finish = str(getattr(choices[0], "finish_reason", None) or "stop")

        usage = getattr(raw, "usage", None)
        in_tok = int(getattr(usage, "prompt_tokens", 0) or 0)
        out_tok = int(getattr(usage, "completion_tokens", 0) or 0)
        cost = self.estimate_cost(input_tokens=in_tok, output_tokens=out_tok, model=model)

        return LLMResponse(
            raw_text=text,
            parsed=None,
            input_tokens=in_tok,
            output_tokens=out_tok,
            cost_usd=cost,
            latency_seconds=latency,
            model=getattr(raw, "model", model),
            finish_reason=finish,
            seed=None,
            cache_hit=False,
            provider_meta={
                "response_id": getattr(raw, "id", None),
                "system_fingerprint": getattr(raw, "system_fingerprint", None),
                "created": getattr(raw, "created", None),
                "finish_reason_raw": finish,
                "request_body_sha256": actual_sha,
            },
            tool_calls=None,
        )


def make_provider_p4(model: str):
    """Model → provider with provenance capture. Loud on missing env or
    unknown subject model — silent fallbacks would break provenance."""
    if model.startswith("gpt-"):
        from openai import OpenAI

        api_key = os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY")
        base_url = os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL")
        if not api_key or not base_url:
            raise RuntimeError("AI_INTEGRATIONS_OPENAI_API_KEY / _BASE_URL not set")
        return OpenAIMetaProvider(client=OpenAI(api_key=api_key, base_url=base_url)), "openai"
    if model.startswith("gemini-"):
        from gemini_provider import GeminiProvider

        return GeminiProvider(), "gemini"
    raise RuntimeError(f"no Phase 4 provider for model {model}")
