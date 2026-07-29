"""Phase 4 Gate 0 — provider & route verification (frozen spec: provider-packet §2).

First post-approval action, before any experimental row. Budget: ≤10 calls
per round, logged as infrastructure (event types `infra.gate0.*`, run_id
namespace `gate0_*` — structurally excluded from every analysis/extraction
path, which join on experiments), counted against the global kill-switch.

ROUND 2 under registered amendment A1 (2026-07-24): cross-vendor candidate
switched claude-haiku-4-5 → gemini-2.5-flash after the round-1 behavioral
gate failure (haiku cannot complete a turn at the protocol's maxTokens=16;
its rescue-by-retry would have injected the retry suffix into nearly every
effective stimulus — a model×stimulus confound). Round-1 record archived at
docs/phase4/gate0-report-round1-claude-FAIL.md. Vendor-adapter settings for
the gemini candidate (registered, disclosed): thinking_budget=0 and always-
explicit top_p — see engine/gemini_provider.py.

Asserts, per the frozen packet:
  (1) response ID non-empty on both routes;
  (2) returned model string equals expectation
      - gpt-4.1          -> exactly "gpt-4.1-2025-04-14" (the revision on all
        5,830 Phase 3 calls; anything else fires sentinel alert rule (a));
      - gemini-2.5-flash -> non-empty `model_version`, must contain
        "gemini-2.5-flash" (family substitution guard). If the provider
        exposes no finer revision than the requested ID, that is disclosed;
        no finer pinning is claimed.
  (3) finish reason is a clean stop
      - OpenAI: "stop"; Gemini: "STOP" (registered cross-vendor mapping;
        "length"/"MAX_TOKENS" = truncation = FAILURE);
  (4) token accounting present (input+output counts > 0), and for gemini:
      thoughts_token_count == 0 (thinking verifiably OFF, not assumed);
  (5) parser round-trip on a fixed known prompt: sealed `pd-repeated-v1`
      round-1 rendering (seat 1, d90, empty history) through the SAME
      engine path experiments use (render_prompt -> build_prompt ->
      provider.complete -> parse_action). One protocol-standard retry
      (retrySuffix) is permitted, exactly as in experimental runs.

ANY persistent failure exits nonzero and BLOCKS the phase (escalated, not
worked around). Output: docs/phase4/gate0-report.md (machine-generated).
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
import urllib.request
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from activegraph import Event, Graph, Runtime  # noqa: E402

from engine import Engine  # noqa: E402
from llm_runner import _complete_with_transient_retries  # noqa: E402
from llm_subject import build_prompt, load_registry, parse_action, render_prompt  # noqa: E402

DB_PATH = os.environ.get(
    "ENGINE_DB_PATH",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "engine.db"),
)
REPO_ROOT = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..")
)
REPORT_PATH = os.path.join(REPO_ROOT, "docs", "phase4", "gate0-report.md")

EXPECT_OPENAI_MODEL = "gpt-4.1-2025-04-14"
GEMINI_REQUESTED = "gemini-2.5-flash"
GEMINI_FAMILY_GUARD = "gemini-2.5-flash"
PROMPT_ID = "pd-repeated-v1"
PROTOCOL = {"promptId": PROMPT_ID, "temperature": 0.7, "maxTokens": 16, "deltaPct": 90}
MAX_CALLS = 10
ROUND_NOTE = (
    "Round 2 under registered amendment A1 (2026-07-24): cross-vendor candidate "
    "switched claude-haiku-4-5 → gemini-2.5-flash after round-1 behavioral gate "
    "failure; round-1 record archived at `gate0-report-round1-claude-FAIL.md`. "
    "Gemini vendor-adapter settings (registered): thinking_budget=0, explicit top_p=1.0."
)

calls: list[dict[str, Any]] = []
failures: list[str] = []


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def check(name: str, ok: bool, detail: str) -> dict[str, Any]:
    if not ok:
        failures.append(f"{name}: {detail}")
    return {"name": name, "ok": ok, "detail": detail}


def body_sha(kwargs: dict[str, Any]) -> str:
    return hashlib.sha256(
        json.dumps(kwargs, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def fetch_pd_game() -> dict[str, Any]:
    """Payoffs come from the same source experiments use (the API's stored
    game), not a hardcoded copy that could drift."""
    with urllib.request.urlopen("http://localhost:80/api/games", timeout=15) as r:
        games = json.load(r)
    g = next(g for g in games if g["slug"] == "prisoners-dilemma")
    pm = g["payoffMatrix"]
    if isinstance(pm, str):  # API serves payoff matrices as JSON text
        pm = json.loads(pm)
    return {"slug": g["slug"], "payoffMatrix": pm}


def render_fixed_prompt(registry: dict, game_def: dict, retry_raw: Optional[str] = None):
    return render_prompt(
        registry,
        PROMPT_ID,
        seat=1,
        round_number=1,
        history=[],
        game_def=game_def,
        num_rounds=100,
        protocol=PROTOCOL,
        retry_raw=retry_raw,
    )


def route_call_openai(client, system: str, user: str) -> dict[str, Any]:
    kwargs = {
        "model": "gpt-4.1",
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.7,
        "max_tokens": 16,
        "top_p": 1.0,
    }
    t0 = time.time()
    resp = client.chat.completions.create(**kwargs)
    ms = int((time.time() - t0) * 1000)
    choice = resp.choices[0]
    usage = resp.usage
    return {
        "provider": "openai-route",
        "requestedModel": "gpt-4.1",
        "requestBodySha256": body_sha(kwargs),
        "responseId": resp.id or "",
        "returnedModel": resp.model or "",
        "stopReason": choice.finish_reason or "",
        "inputTokens": getattr(usage, "prompt_tokens", 0) or 0,
        "outputTokens": getattr(usage, "completion_tokens", 0) or 0,
        "rawText": (choice.message.content or "").strip(),
        "latencyMs": ms,
    }


def route_call_gemini(client, system: str, user: str) -> dict[str, Any]:
    """Raw-SDK route call mirroring the registered adapter settings exactly
    (engine/gemini_provider.py): thinking_budget=0, explicit top_p=1.0."""
    config = {
        "system_instruction": system,
        "temperature": 0.7,
        "top_p": 1.0,
        "max_output_tokens": 16,
        "thinking_config": {"thinking_budget": 0},
    }
    kwargs_for_sha = {"model": GEMINI_REQUESTED, "config": config, "contents": user}
    t0 = time.time()
    resp = client.models.generate_content(
        model=GEMINI_REQUESTED, contents=user, config=config
    )
    ms = int((time.time() - t0) * 1000)
    cand = resp.candidates[0] if getattr(resp, "candidates", None) else None
    text = ""
    if cand is not None and getattr(cand, "content", None) is not None:
        parts = getattr(cand.content, "parts", None) or []
        text = "".join(p.text for p in parts if getattr(p, "text", None))
    fr = getattr(cand, "finish_reason", None) if cand is not None else None
    um = getattr(resp, "usage_metadata", None)
    return {
        "provider": "gemini-route",
        "requestedModel": GEMINI_REQUESTED,
        "requestBodySha256": body_sha(kwargs_for_sha),
        "responseId": getattr(resp, "response_id", "") or "",
        "returnedModel": getattr(resp, "model_version", "") or "",
        "stopReason": getattr(fr, "name", None) or (str(fr) if fr else ""),
        "inputTokens": int(getattr(um, "prompt_token_count", 0) or 0),
        "outputTokens": int(getattr(um, "candidates_token_count", 0) or 0),
        "thoughtsTokens": int(getattr(um, "thoughts_token_count", 0) or 0),
        "rawText": text.strip(),
        "latencyMs": ms,
    }


def assert_route(
    rec: dict[str, Any],
    expect_model_exact: Optional[str],
    family_contains: Optional[str],
    stop_ok: str,
) -> None:
    rec["assertions"] = [
        check(f"{rec['provider']}: response ID non-empty", bool(rec["responseId"]), rec["responseId"] or "EMPTY"),
        check(
            f"{rec['provider']}: returned model",
            (rec["returnedModel"] == expect_model_exact)
            if expect_model_exact
            else (bool(rec["returnedModel"]) and (family_contains or "") in rec["returnedModel"]),
            f"returned={rec['returnedModel']!r} expected="
            + (repr(expect_model_exact) if expect_model_exact else f"contains {family_contains!r}"),
        ),
        check(
            f"{rec['provider']}: clean stop",
            rec["stopReason"] == stop_ok,
            f"stopReason={rec['stopReason']!r} (required {stop_ok!r}; truncation = fail)",
        ),
        check(
            f"{rec['provider']}: token accounting",
            rec["inputTokens"] > 0 and rec["outputTokens"] > 0,
            f"in={rec['inputTokens']} out={rec['outputTokens']}",
        ),
    ]
    if "thoughtsTokens" in rec:
        rec["assertions"].append(
            check(
                f"{rec['provider']}: no hidden reasoning tokens",
                rec["thoughtsTokens"] == 0,
                f"thoughts_token_count={rec['thoughtsTokens']} (thinking_budget=0 must hold empirically)",
            )
        )


def engine_path_call(provider, registry, game_def, model: str, label: str) -> list[dict[str, Any]]:
    """Engine-path verification with the protocol's single parse retry."""
    recs = []
    retry_raw: Optional[str] = None
    for attempt in (0, 1):
        system, user = render_fixed_prompt(registry, game_def, retry_raw)
        prompt = build_prompt(system, user, model=model, temperature=0.7, max_tokens=16)
        t0 = time.time()
        resp = _complete_with_transient_retries(provider, prompt)
        ms = int((time.time() - t0) * 1000)
        d = resp.to_dict()
        action = parse_action(registry, PROMPT_ID, resp.raw_text)
        meta = d.get("provider_meta") or {}
        rec = {
            "provider": label,
            "requestedModel": model,
            "requestBodySha256": "(engine path — request-body sha capture ships with §F.3 step 2)",
            "responseId": meta.get("response_id") or "(engine path — provider_meta capture ships fully with §F.3 step 2)",
            "returnedModel": d.get("model") or "",
            "stopReason": d.get("finish_reason") or "",
            "inputTokens": int(d.get("input_tokens") or 0),
            "outputTokens": int(d.get("output_tokens") or 0),
            "rawText": resp.raw_text.strip(),
            "latencyMs": ms,
            "attempt": attempt,
            "parsedAction": action,
            "providerMeta": meta,
            "providerMetaKeys": sorted(meta.keys()),
            "assertions": [],
        }
        rec["assertions"].append(
            check(
                f"{label}: LLMResponse fields present",
                bool(resp.raw_text) and rec["inputTokens"] > 0,
                f"raw_text={resp.raw_text!r} in={rec['inputTokens']} out={rec['outputTokens']}",
            )
        )
        if "thoughts_token_count" in meta:
            rec["assertions"].append(
                check(
                    f"{label}: no hidden reasoning tokens",
                    int(meta.get("thoughts_token_count") or 0) == 0,
                    f"thoughts_token_count={meta.get('thoughts_token_count')}",
                )
            )
        recs.append(rec)
        if action is not None:
            rec["assertions"].append(
                check(f"{label}: parser round-trip", True, f"raw={resp.raw_text!r} -> action index {action}")
            )
            return recs
        retry_raw = resp.raw_text
    recs[-1]["assertions"].append(
        check(
            f"{label}: parser round-trip",
            False,
            f"unparseable after protocol retry; last raw={retry_raw!r}",
        )
    )
    return recs


def main() -> int:
    started = now_iso()
    registry, registry_sha = load_registry()
    game_def = fetch_pd_game()

    from openai import OpenAI
    from google import genai
    from google.genai import types as gtypes
    from gemini_provider import GeminiProvider
    from llm_subject import make_provider

    oa_key = os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY")
    oa_url = os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL")
    ge_key = os.environ.get("AI_INTEGRATIONS_GEMINI_API_KEY")
    ge_url = os.environ.get("AI_INTEGRATIONS_GEMINI_BASE_URL")
    if not (oa_key and oa_url and ge_key and ge_url):
        print("FATAL: AI Integrations env vars missing on one or both routes")
        return 2
    oa_client = OpenAI(api_key=oa_key, base_url=oa_url)
    ge_client = genai.Client(
        api_key=ge_key,
        http_options=gtypes.HttpOptions(base_url=ge_url, api_version=""),
    )
    routes = {
        "openai-route": {"host": oa_url.split("//")[-1].split("/")[0], "slug": "ai-integrations:openai"},
        "gemini-route": {"host": ge_url.split("//")[-1].split("/")[0], "slug": "ai-integrations:gemini"},
    }

    engine = Engine(DB_PATH)
    run_id = f"gate0_{int(time.time())}_{uuid.uuid4().hex[:8]}"
    graph = Graph(run_id=run_id)
    rt = Runtime(graph, behaviors=[], persist_to=engine.url)
    graph.emit(
        Event(
            id=graph.ids.event(),
            type="infra.gate0.started",
            payload={
                "startedAt": started,
                "round": 2,
                "amendment": "A1: cross-vendor candidate claude-haiku-4-5 → gemini-2.5-flash (2026-07-24)",
                "registrySha256": registry_sha,
                "registryVersion": registry.get("registryVersion"),
                "providerRoutes": routes,
                "spec": "provider-packet.md §2 (frozen)",
            },
            actor="gate0",
        )
    )

    verdict = "FAIL"
    try:
        system, user = render_fixed_prompt(registry, game_def)

        # --- route verification: 2 calls per model (raw SDK) ---
        for i in range(2):
            rec = route_call_openai(oa_client, system, user)
            rec["purpose"] = f"route check {i + 1}/2"
            assert_route(rec, EXPECT_OPENAI_MODEL, None, stop_ok="stop")
            calls.append(rec)
        for i in range(2):
            rec = route_call_gemini(ge_client, system, user)
            rec["purpose"] = f"route check {i + 1}/2"
            assert_route(rec, None, GEMINI_FAMILY_GUARD, stop_ok="STOP")
            calls.append(rec)

        # --- engine-path verification: 1 call per model (+ ≤1 protocol retry) ---
        for rec in engine_path_call(make_provider(), registry, game_def, "gpt-4.1", "openai-engine-path"):
            rec["purpose"] = "engine path + parser round-trip"
            calls.append(rec)
        ge_provider = GeminiProvider(client=ge_client)
        for rec in engine_path_call(ge_provider, registry, game_def, GEMINI_REQUESTED, "gemini-engine-path"):
            rec["purpose"] = "engine path + parser round-trip"
            calls.append(rec)

        if len(calls) > MAX_CALLS:
            check("call budget", False, f"{len(calls)} > {MAX_CALLS}")

        verdict = "PASS" if not failures else "FAIL"
        return 0 if verdict == "PASS" else 1
    finally:
        for rec in calls:
            graph.emit(
                Event(
                    id=graph.ids.event(),
                    type="infra.gate0.call",
                    payload=rec,
                    actor="gate0",
                )
            )
        graph.emit(
            Event(
                id=graph.ids.event(),
                type="infra.gate0.completed",
                payload={
                    "verdict": verdict,
                    "failures": failures,
                    "totalCalls": len(calls),
                    "inputTokens": sum(c.get("inputTokens", 0) for c in calls),
                    "outputTokens": sum(c.get("outputTokens", 0) for c in calls),
                    "finishedAt": now_iso(),
                },
                actor="gate0",
            )
        )
        rt.save_state()
        write_report(started, verdict, run_id, registry_sha, routes)


def write_report(started: str, verdict: str, run_id: str, registry_sha: str, routes: dict) -> None:
    lines = [
        "# Gate 0 — provider & route verification report",
        "",
        "*Machine-generated by `engine/gate0.py`. Do not edit.*",
        "",
        f"- Spec: `provider-packet.md` §2 (frozen); approval 2026-07-24T15:18:49Z",
        f"- {ROUND_NOTE}",
        f"- Started {started} · verdict **{verdict}** · event-store run `{run_id}` (types `infra.gate0.*`, excluded from analysis, counted against the global kill-switch)",
        f"- Registry at execution: `{registry_sha}` (phase4-v3-proposed; sealing follows in step 3)",
        f"- Provider routes: " + json.dumps(routes),
        f"- Total calls: {len(calls)} (budget ≤ {MAX_CALLS} per round) · tokens in/out: "
        f"{sum(c.get('inputTokens', 0) for c in calls)}/{sum(c.get('outputTokens', 0) for c in calls)}",
        "- Cross-vendor stop mapping (registered): OpenAI `stop` ↔ Gemini `STOP`; truncation (`length` / `MAX_TOKENS`) = failure.",
        "",
        "| # | purpose | provider | requested → returned model | response ID | stop | tokens in/out | raw reply | parsed | ms |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for i, c in enumerate(calls, 1):
        rid = c["responseId"]
        rid_short = (rid[:18] + "…") if rid and len(rid) > 18 and not rid.startswith("(") else rid
        parsed = c.get("parsedAction", "—")
        lines.append(
            f"| {i} | {c['purpose']} | {c['provider']} | `{c['requestedModel']}` → `{c['returnedModel']}` "
            f"| `{rid_short}` | {c['stopReason']} | {c['inputTokens']}/{c['outputTokens']} "
            f"| `{c['rawText']!r}` | {parsed} | {c['latencyMs']} |"
        )
    lines += ["", "## Assertions", ""]
    for c in calls:
        for a in c.get("assertions", []):
            lines.append(f"- {'✅' if a['ok'] else '❌'} {a['name']} — {a['detail']}")
    lines += [
        "",
        "## Request-body SHAs (route calls)",
        "",
    ]
    for c in calls:
        if not c["requestBodySha256"].startswith("("):
            lines.append(f"- {c['provider']} ({c['purpose']}): `{c['requestBodySha256']}`")
    lines += [
        "",
        "## Reconnaissance for §F.3 capture (step 2)",
        "",
        f"- `provider_meta` keys surfaced by engine-path providers: "
        + json.dumps({c["provider"]: c.get("providerMetaKeys") for c in calls if "providerMetaKeys" in c}),
        "- OpenAI engine-path calls do not yet archive response ID / request-body sha — that is the §F.3 "
        "step-2 work (mandatory before any experimental row). The gemini adapter already surfaces "
        "response_id / model_version / thoughts_token_count via provider_meta.",
    ]
    if failures:
        lines += ["", "## FAILURES (phase BLOCKED)", ""] + [f"- ❌ {f}" for f in failures]
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"gate0: {verdict} · {len(calls)} calls · report -> {os.path.relpath(REPORT_PATH, REPO_ROOT)}")
    for fmsg in failures:
        print(f"  FAIL: {fmsg}")


if __name__ == "__main__":
    sys.exit(main())
