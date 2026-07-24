"""Phase 4 Gate 0 — provider & route verification (frozen spec: provider-packet §2).

First post-approval action, before any experimental row. Budget: ≤10 calls,
logged as infrastructure (event types `infra.gate0.*`, run_id namespace
`gate0_*` — structurally excluded from every analysis/extraction path, which
join on experiments), counted against the global kill-switch.

Asserts, per the frozen packet:
  (1) response ID non-empty on both routes;
  (2) returned model string equals expectation
      - gpt-4.1        -> exactly "gpt-4.1-2025-04-14" (the revision on all
        5,830 Phase 3 calls; anything else fires sentinel alert rule (a));
      - claude-haiku-4-5 -> non-empty, must contain "haiku-4-5" (family
        substitution guard). If the provider exposes no finer revision than
        the requested ID, that is disclosed; no finer pinning is claimed.
  (3) finish reason is a clean stop
      - OpenAI: "stop"; Anthropic: "end_turn" (registered cross-vendor
        mapping; "max_tokens" = truncation = FAILURE);
  (4) token accounting present (input+output counts > 0);
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
CLAUDE_REQUESTED = "claude-haiku-4-5"
CLAUDE_FAMILY_GUARD = "haiku-4-5"
PROMPT_ID = "pd-repeated-v1"
PROTOCOL = {"promptId": PROMPT_ID, "temperature": 0.7, "maxTokens": 16, "deltaPct": 90}
MAX_CALLS = 10

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


def route_call_anthropic(client, system: str, user: str) -> dict[str, Any]:
    kwargs = {
        "model": CLAUDE_REQUESTED,
        "system": system,
        "messages": [{"role": "user", "content": user}],
        "temperature": 0.7,
        "max_tokens": 16,
    }
    t0 = time.time()
    resp = client.messages.create(**kwargs)
    ms = int((time.time() - t0) * 1000)
    text = "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")
    return {
        "provider": "anthropic-route",
        "requestedModel": CLAUDE_REQUESTED,
        "requestBodySha256": body_sha(kwargs),
        "responseId": resp.id or "",
        "returnedModel": resp.model or "",
        "stopReason": resp.stop_reason or "",
        "inputTokens": resp.usage.input_tokens or 0,
        "outputTokens": resp.usage.output_tokens or 0,
        "rawText": text.strip(),
        "latencyMs": ms,
    }


def assert_route(rec: dict[str, Any], expect_model_exact: Optional[str], stop_ok: str) -> None:
    rec["assertions"] = [
        check(f"{rec['provider']}: response ID non-empty", bool(rec["responseId"]), rec["responseId"] or "EMPTY"),
        check(
            f"{rec['provider']}: returned model",
            (rec["returnedModel"] == expect_model_exact)
            if expect_model_exact
            else (bool(rec["returnedModel"]) and CLAUDE_FAMILY_GUARD in rec["returnedModel"]),
            f"returned={rec['returnedModel']!r} expected="
            + (repr(expect_model_exact) if expect_model_exact else f"contains {CLAUDE_FAMILY_GUARD!r}"),
        ),
        check(
            f"{rec['provider']}: clean stop",
            rec["stopReason"] == stop_ok,
            f"stopReason={rec['stopReason']!r} (required {stop_ok!r}; max_tokens = truncation = fail)",
        ),
        check(
            f"{rec['provider']}: token accounting",
            rec["inputTokens"] > 0 and rec["outputTokens"] > 0,
            f"in={rec['inputTokens']} out={rec['outputTokens']}",
        ),
    ]


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
        rec = {
            "provider": label,
            "requestedModel": model,
            "requestBodySha256": "(engine path — request-body sha capture ships with §F.3 step 2)",
            "responseId": "(engine path — see route calls; per-call capture ships with §F.3 step 2)",
            "returnedModel": d.get("model") or "",
            "stopReason": d.get("finish_reason") or "",
            "inputTokens": int(d.get("input_tokens") or 0),
            "outputTokens": int(d.get("output_tokens") or 0),
            "rawText": resp.raw_text.strip(),
            "latencyMs": ms,
            "attempt": attempt,
            "parsedAction": action,
            "providerMetaKeys": sorted((d.get("provider_meta") or {}).keys()),
            "assertions": [],
        }
        rec["assertions"].append(
            check(
                f"{label}: LLMResponse fields present",
                bool(resp.raw_text) and rec["inputTokens"] > 0,
                f"raw_text={resp.raw_text!r} in={rec['inputTokens']} out={rec['outputTokens']}",
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
    from anthropic import Anthropic
    from activegraph.llm.anthropic import AnthropicProvider
    from llm_subject import make_provider

    oa_key = os.environ.get("AI_INTEGRATIONS_OPENAI_API_KEY")
    oa_url = os.environ.get("AI_INTEGRATIONS_OPENAI_BASE_URL")
    an_key = os.environ.get("AI_INTEGRATIONS_ANTHROPIC_API_KEY")
    an_url = os.environ.get("AI_INTEGRATIONS_ANTHROPIC_BASE_URL")
    if not (oa_key and oa_url and an_key and an_url):
        print("FATAL: AI Integrations env vars missing on one or both routes")
        return 2
    oa_client = OpenAI(api_key=oa_key, base_url=oa_url)
    an_client = Anthropic(api_key=an_key, base_url=an_url)
    routes = {
        "openai-route": {"host": oa_url.split("//")[-1].split("/")[0], "slug": "ai-integrations:openai"},
        "anthropic-route": {"host": an_url.split("//")[-1].split("/")[0], "slug": "ai-integrations:anthropic"},
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
            assert_route(rec, EXPECT_OPENAI_MODEL, stop_ok="stop")
            calls.append(rec)
        for i in range(2):
            rec = route_call_anthropic(an_client, system, user)
            rec["purpose"] = f"route check {i + 1}/2"
            assert_route(rec, None, stop_ok="end_turn")
            calls.append(rec)

        # --- engine-path verification: 1 call per model (+ ≤1 protocol retry) ---
        for rec in engine_path_call(make_provider(), registry, game_def, "gpt-4.1", "openai-engine-path"):
            rec["purpose"] = "engine path + parser round-trip"
            calls.append(rec)
        an_provider = AnthropicProvider(client=an_client)
        for rec in engine_path_call(an_provider, registry, game_def, CLAUDE_REQUESTED, "anthropic-engine-path"):
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
        f"- Started {started} · verdict **{verdict}** · event-store run `{run_id}` (types `infra.gate0.*`, excluded from analysis, counted against the global kill-switch)",
        f"- Registry at execution: `{registry_sha}` (phase4-v3-proposed; sealing follows in step 3)",
        f"- Provider routes: " + json.dumps(routes),
        f"- Total calls: {len(calls)} (budget ≤ {MAX_CALLS}) · tokens in/out: "
        f"{sum(c.get('inputTokens', 0) for c in calls)}/{sum(c.get('outputTokens', 0) for c in calls)}",
        "- Cross-vendor stop mapping (registered): OpenAI `stop` ↔ Anthropic `end_turn`; `max_tokens` = truncation = failure.",
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
        f"- `provider_meta` keys surfaced by activegraph providers on engine-path calls: "
        + json.dumps({c["provider"]: c.get("providerMetaKeys") for c in calls if "providerMetaKeys" in c}),
        "- Engine-path calls do not yet archive response ID / request-body sha — that is exactly the §F.3 "
        "step-2 work (mandatory before any experimental row).",
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
