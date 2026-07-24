"""Phase 4 infrastructure selftest — zero LLM calls, zero real spend.

Exercises the §F.3 capture/enforcement/replay machinery end-to-end against
TEMP databases with a fake in-process provider (deterministic canned
replies, provider_meta built the same way the real providers build it).
This is infrastructure verification, not subject exposure: no stimulus
reaches any live model, and the real budget ledger is never touched.

Run:  cd artifacts/api-server/engine && uv run python selftest_phase4.py
"""
from __future__ import annotations

import os
import sys
import tempfile
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

_TMP = tempfile.mkdtemp(prefix="p4selftest_")
os.environ["BUDGET_DB_PATH"] = os.path.join(_TMP, "budget.db")  # before imports

from engine import Engine  # noqa: E402
from llm_subject import PARSER_VERSION, load_registry  # noqa: E402
from strategies import STRATEGIES  # noqa: E402
from activegraph.llm.types import LLMResponse  # noqa: E402

import phase4  # noqa: E402
from phase4 import (  # noqa: E402
    ArmStore,
    BudgetExceededError,
    BudgetLedger,
    EnforcementError,
    PHASE4_PROTOCOL,
    self_check,
    validate_run_request,
)
from phase4_runner import dry_run_p4, replay_llm_p4, run_llm_p4, write_resolution  # noqa: E402
from provenance import canonical_json, request_body_sha, sha256_hex  # noqa: E402

PASS = 0


def ok(label: str, cond: bool, detail: str = "") -> None:
    global PASS
    if not cond:
        print(f"  FAIL  {label}  {detail}")
        raise SystemExit(1)
    PASS += 1
    print(f"  ok    {label}")


def expect_reject(label: str, fn, needle: str) -> None:
    try:
        fn()
    except (EnforcementError, ValueError) as e:
        ok(label, needle.lower() in str(e).lower(), f"got: {e}")
        return
    print(f"  FAIL  {label}  — was ACCEPTED, expected rejection containing {needle!r}")
    raise SystemExit(1)


class FakeProvider:
    """Deterministic canned provider; builds provider_meta exactly like the
    real OpenAIMetaProvider (actual request-body sha from sent kwargs)."""

    def __init__(self, replies: list[str]):
        self.replies = list(replies)
        self.calls = 0

    def complete(self, *, system, messages, model, max_tokens, temperature,
                 top_p, output_schema, timeout_seconds, tools=None,
                 structured_output_mode="prompt"):
        body = {
            "provider": "openai",
            "model": model,
            "messages": [{"role": "system", "content": system}]
            + [{"role": m.role, "content": m.content} for m in messages],
            "max_tokens": int(max_tokens),
            "temperature": float(temperature),
        }
        if top_p < 1.0:
            body["top_p"] = float(top_p)
        text = self.replies[min(self.calls, len(self.replies) - 1)]
        self.calls += 1
        return LLMResponse(
            raw_text=text, parsed=None, input_tokens=120, output_tokens=1,
            cost_usd=Decimal("0"), latency_seconds=0.01, model=model,
            finish_reason="stop", seed=None, cache_hit=False,
            provider_meta={
                "response_id": f"fake-{self.calls}",
                "system_fingerprint": "fp_selftest",
                "created": 0,
                "finish_reason_raw": "stop",
                "request_body_sha256": sha256_hex(canonical_json(body)),
            },
            tool_calls=None,
        )


class FakeGeminiProvider:
    """Gemini-kind canned provider: mirrors the registered gemini request-body
    sha and reports a configurable thoughts_token_count (or omits the key)."""

    def __init__(self, replies: list[str], thoughts: int = 0, omit_thoughts: bool = False):
        self.replies = list(replies)
        self.thoughts = thoughts
        self.omit_thoughts = omit_thoughts
        self.calls = 0

    def complete(self, *, system, messages, model, max_tokens, temperature,
                 top_p, output_schema, timeout_seconds, tools=None,
                 structured_output_mode="prompt"):
        from provenance import gemini_request_body
        body = gemini_request_body(
            model=model, system=system, user=messages[0].content,
            max_tokens=int(max_tokens), temperature=float(temperature),
            top_p=float(top_p), thinking_budget=0,
        )
        meta = {
            "response_id": f"fake-gem-{self.calls}",
            "model_version": model,
            "finish_reason_raw": "STOP",
            "request_body_sha256": sha256_hex(canonical_json(body)),
        }
        if not self.omit_thoughts:
            meta["thoughts_token_count"] = int(self.thoughts)
        text = self.replies[min(self.calls, len(self.replies) - 1)]
        self.calls += 1
        return LLMResponse(
            raw_text=text, parsed=None, input_tokens=110, output_tokens=1,
            cost_usd=Decimal("0"), latency_seconds=0.01, model=model,
            finish_reason="stop", seed=None, cache_hit=False,
            provider_meta=meta, tool_calls=None,
        )


def pd_game(rr, rs, rt, rp, swapped=False, labels=("J", "F")):
    m = ([[[rp, rp], [rt, rs]], [[rs, rt], [rr, rr]]] if swapped
         else [[[rr, rr], [rs, rt]], [[rt, rs], [rp, rp]]])
    return {
        "slug": "phase4-pd", "numActions": 2, "actionLabels": list(labels),
        "payoffMatrix": m,
        "nashEquilibria": phase4._pure_nash(m),
    }


def main() -> None:
    registry, registry_sha = load_registry()
    store = ArmStore()
    ledger = BudgetLedger()  # temp path via env override

    print("— self-check —")
    check = self_check(registry, store)
    ok("template-sha parity (Node ↔ Python canonical)", check["ok"], str(check["mismatches"][:3]))
    ok("49 templates checked", check["templatesChecked"] == 49, str(check["templatesChecked"]))

    print("— ledger backfill + caps —")
    t = ledger.totals()
    ok("gate-0 backfill present (15 calls overhead)", t["byGroup"]["overhead"]["calls"] == 15, str(t))
    ok("gate-0 tokens backfilled", t["byGroup"]["overhead"]["inputTokens"] == 2972
       and t["byGroup"]["overhead"]["outputTokens"] == 63, str(t["byGroup"]["overhead"]))
    row = ledger.reserve_call(run_id="test_r1", arm_id="x", block="D1", model="gpt-4.1", run_call_index=1)
    ledger.record_tokens(row, 100, 1)
    ok("reserve + record", ledger.totals()["byGroup"]["D"]["calls"] == 1)
    try:
        ledger.reserve_call(run_id="test_r1", arm_id="x", block="D1", model="gpt-4.1",
                            run_call_index=phase4.EPISODE_RUNAWAY_CAP + 1)
        ok("runaway guard", False)
    except BudgetExceededError:
        ok("episode runaway guard trips at 261", True)
    saved = phase4.CAP_GROUPS["D"]
    phase4.CAP_GROUPS["D"] = 1
    try:
        ledger.reserve_call(run_id="test_r2", arm_id="x", block="D2", model="gpt-4.1", run_call_index=1)
        ok("block cap", False)
    except BudgetExceededError:
        ok("block kill-switch refuses at cap", True)
    finally:
        phase4.CAP_GROUPS["D"] = saved

    print("— enforcement rejection matrix —")
    d1 = store.get("p4-d1-can-w1-neu-cf-ad-gpt")
    good = dict(
        arm=d1, registry=registry, store=store, ledger=ledger,
        game_def=pd_game(3, 0, 5, 1), strategy1_slug="llm-subject",
        strategy2_slug="llm-subject", num_rounds=1, seed=2001, model="gpt-4.1",
        temperature=0.7, max_tokens=16, episode_index=1,
        sentinel_check_index=None, known_strategies=set(STRATEGIES),
    )
    pinned = validate_run_request(**good)
    ok("valid D1 request accepted", pinned["templateId"] == "pd-os-w1-neu-cf-ad")
    ok("D1 substitutions derived", pinned["substitutions"] == {"rr": 3, "rs": 0, "rt": 5, "rp": 1})
    expect_reject("unknown arm", lambda: store.get("p4-nope"), "unknown sealed arm")
    expect_reject("wrong seed", lambda: validate_run_request(**{**good, "seed": 1999}), "not in arm seed list")
    expect_reject("episode/seed mismatch", lambda: validate_run_request(**{**good, "episode_index": 2}), "pins seed")
    expect_reject("wrong model", lambda: validate_run_request(**{**good, "model": "gemini-2.5-flash"}), "arm pin")
    expect_reject("wrong temperature", lambda: validate_run_request(**{**good, "temperature": 0.0}), "pinned")
    expect_reject("wrong maxTokens", lambda: validate_run_request(**{**good, "max_tokens": 64}), "pinned")
    expect_reject("multi-round one-shot", lambda: validate_run_request(**{**good, "num_rounds": 5}), "one-shot")
    expect_reject("tampered payoff matrix",
                  lambda: validate_run_request(**{**good, "game_def": pd_game(4, 0, 5, 1)}), "gamedef")
    expect_reject("non-self-play seats",
                  lambda: validate_run_request(**{**good, "strategy2_slug": "always-defect"}), "self-play")

    d2 = next(a for a in store.arms.values()
              if a["block"] == "D2" and a["bindings"].get("labelRoleMap") == "swapped")
    d2_vals = [d2["bindings"][k] for k in ("rr", "rs", "rt", "rp")]
    sem = ("COOPERATE", "DEFECT")  # D2 templates are the semantic-label family
    g_sw = dict(good, arm=d2, game_def=pd_game(*d2_vals, swapped=True, labels=sem),
                seed=d2["seeds"][0], episode_index=1, model=d2["model"])
    p_sw = validate_run_request(**g_sw)
    ok("D2 swapped matrix derived (displayed C carries defect role)",
       p_sw["substitutions"]["rr"] == d2["bindings"]["rp"]
       and p_sw["substitutions"]["labelRoleMap"] == "swapped", str(p_sw["substitutions"]))
    expect_reject("D2 swapped arm refuses aligned matrix",
                  lambda: validate_run_request(**{**g_sw, "game_def": pd_game(*d2_vals, labels=sem)}),
                  "gamedef")

    d3 = store.get("p4-d3-map1-ord1-gpt")
    rps_m = phase4._rps_sym_expected_matrix(d3["bindings"]["roleMapping"])
    g_d3 = dict(good, arm=d3, seed=d3["seeds"][0], model=d3["model"], episode_index=1,
                game_def={"slug": "phase4-rps", "numActions": 3, "actionLabels": ["X", "Y", "Z"],
                          "payoffMatrix": rps_m, "nashEquilibria": []})
    p_d3 = validate_run_request(**g_d3)
    ok("D3 optList pinned", p_d3["substitutions"]["optList"] == "X, Y or Z", str(p_d3["substitutions"]))
    ok("D3 beatsLine pinned (winners in display order)",
       p_d3["substitutions"]["beatsLine"] == "X beats Z. Y beats X. Z beats Y.", str(p_d3["substitutions"]))

    e_arm = store.get("p4-e-dselected-d90-gpt")
    expect_reject("RESOLVED-BY template without resolution",
                  lambda: validate_run_request(**dict(good, arm=e_arm, seed=e_arm["seeds"][0],
                                                      num_rounds=10, episode_index=1)),
                  "resolution")

    sent = store.get("p4-sent-v1")
    g_sent = dict(good, arm=sent, seed=9001, episode_index=None, sentinel_check_index=0,
                  game_def=pd_game(3, 0, 5, 1))
    ok("sentinel check-0 window accepts 9001", validate_run_request(**g_sent)["block"] == "sentinel")
    expect_reject("sentinel seed outside check window",
                  lambda: validate_run_request(**{**g_sent, "seed": 9012}), "window")
    expect_reject("sentinel without checkIndex",
                  lambda: validate_run_request(**{**g_sent, "sentinel_check_index": None}), "sentinelcheckindex")
    expect_reject("checkIndex on non-sentinel",
                  lambda: validate_run_request(**{**good, "sentinel_check_index": 0}), "sentinel-only")

    f_arm = store.get("p4-f-fo-tracker-gpt")
    rps_std = phase4._rps_standard_matrix()
    expect_reject("F opponent not implemented yet (step-4 work)",
                  lambda: validate_run_request(**dict(
                      good, arm=f_arm, seed=f_arm["seeds"][0], episode_index=1, num_rounds=50,
                      strategy2_slug="fo-tracker",
                      game_def={"slug": "phase4-rps", "numActions": 3,
                                "actionLabels": ["rock", "paper", "scissors"],
                                "payoffMatrix": rps_std, "nashEquilibria": []})),
                  "not implemented")

    print("— resolutions (write-once) —")
    eng_tmp = Engine(os.path.join(_TMP, "engine.db"))
    res = write_resolution(eng_tmp, key="E-dselected", template_id="pd-rep-w1-neu-cf-ad",
                           note="selftest", ledger=ledger, store=store)
    ok("resolution written + event-sourced", res["eventRunId"].strip() != "")
    expect_reject("re-resolution refused",
                  lambda: write_resolution(eng_tmp, key="E-dselected", template_id="pd-rep-w1-neu-cf-ad",
                                           note="again", ledger=ledger, store=store), "already written")
    expect_reject("wrong-family template refused",
                  lambda: write_resolution(eng_tmp, key="X2-conf-lo", template_id="pd-rep-w1-neu-cf-ad",
                                           note="", ledger=ledger, store=store), "pd-x2-")
    p_res = validate_run_request(**dict(good, arm=e_arm, seed=e_arm["seeds"][0], num_rounds=10, episode_index=1))
    ok("E arm resolves through written resolution", p_res["templateId"] == "pd-rep-w1-neu-cf-ad")

    print("— dry run (zero events, zero spend) —")
    before = ledger.totals()["globalCalls"]
    dry = dry_run_p4(arm=d2, pinned=p_sw, game_def=g_sw["game_def"], num_rounds=1,
                     seed=d2["seeds"][0], model=d2["model"], store=store)
    ok("dry run renders + hashes", len(dry["bundleSha256"]) == 64 and dry["liveCalls"] == 0)
    ok("dry run swapped payoff text (C-cell shows rp)",
       f"you earn {d2['bindings']['rp']} points" in dry["user"].split("\n")[2], dry["user"][:200])
    ok("dry run spends nothing", ledger.totals()["globalCalls"] == before)

    print("— fake-provider live capture + replay (temp DBs) —")
    x2 = store.get("p4-x2-f1")
    fake = FakeProvider(["J", "F", "J", "F", "J", "F"])
    g_x2 = pd_game(3, 0, 5, 1)
    p_x2 = validate_run_request(**dict(good, arm=x2, seed=1, episode_index=1, num_rounds=3,
                                       game_def=g_x2))
    result = run_llm_p4(
        eng_tmp, arm=x2, pinned=p_x2, game_def=g_x2,
        strategy1_slug="llm-subject", strategy2_slug="llm-subject",
        num_rounds=3, seed=1, model="gpt-4.1", episode_index=1,
        sentinel_check_index=None, store=store, ledger=ledger,
        provider_factory=lambda m: (fake, "openai"),
    )
    ok("X2 run completed (3 rounds, 6 calls)",
       result["meta"]["llmCalls"] == 6 and not result["invalidTrial"], str(result["meta"]))
    ok("spend rows written per call", len(result["meta"]["spendRows"]) == 6)
    ok("parser version stamped", result["meta"]["parserVersion"] == PARSER_VERSION)
    rep = replay_llm_p4(eng_tmp, result["engineRunId"], store=store)
    ok("replay ok (no mismatches)", rep["ok"], str(rep["mismatches"][:5]))
    ok("replay verified 6 calls", rep["llmCallsVerified"] == 6, str(rep))
    ok("bundle shas byte-verified", rep["bundleShasVerified"] == 6, str(rep))
    ok("request-body shas verified", rep["requestBodyShasVerified"] == 6, str(rep))
    ok("parsed actions re-derived", rep["parsedActionsVerified"] == 6, str(rep))

    d3_fake = FakeProvider(["Y", "Z"])
    p_d3b = validate_run_request(**g_d3)
    r_d3 = run_llm_p4(
        eng_tmp, arm=d3, pinned=p_d3b, game_def=g_d3["game_def"],
        strategy1_slug="llm-subject", strategy2_slug="llm-subject",
        num_rounds=1, seed=d3["seeds"][0], model="gpt-4.1", episode_index=1,
        sentinel_check_index=None, store=store, ledger=ledger,
        provider_factory=lambda m: (d3_fake, "openai"),
    )
    ok("D3 rps-sym run (1 round self-play)", r_d3["meta"]["llmCalls"] == 2, str(r_d3["meta"]))
    rep3 = replay_llm_p4(eng_tmp, r_d3["engineRunId"], store=store)
    ok("D3 replay ok incl. optList/beatsLine re-render", rep3["ok"], str(rep3["mismatches"][:5]))

    bad = FakeProvider(["banana", "still banana"])
    r_bad = run_llm_p4(
        eng_tmp, arm=d1, pinned=pinned, game_def=good["game_def"],
        strategy1_slug="llm-subject", strategy2_slug="llm-subject",
        num_rounds=1, seed=2001, model="gpt-4.1", episode_index=1,
        sentinel_check_index=None, store=store, ledger=ledger,
        provider_factory=lambda m: (bad, "openai"),
    )
    ok("unparseable → invalid trial (recorded, spend kept)",
       r_bad["invalidTrial"] and bad.calls == 2, str(r_bad))
    rep_bad = replay_llm_p4(eng_tmp, r_bad["engineRunId"], store=store)
    ok("invalid-trial replay reports invalidTrial", rep_bad["invalidTrial"] and rep_bad["ok"], str(rep_bad))

    lying = FakeProvider(["J"])
    _orig = lying.complete

    def _tampered(**kw):
        r = _orig(**kw)
        r.provider_meta["request_body_sha256"] = "0" * 64
        return r

    lying.complete = _tampered
    try:
        run_llm_p4(
            eng_tmp, arm=d1, pinned=pinned, game_def=good["game_def"],
            strategy1_slug="llm-subject", strategy2_slug="llm-subject",
            num_rounds=1, seed=2002, model="gpt-4.1", episode_index=2,
            sentinel_check_index=None, store=store, ledger=ledger,
            provider_factory=lambda m: (lying, "openai"),
        )
        ok("mirror/actual sha divergence aborts", False)
    except RuntimeError as e:
        ok("mirror/actual sha divergence aborts", "request-body sha mismatch" in str(e), str(e)[:200])

    print("— gemini thoughts-token guard (asserted per call, never assumed) —")
    gem = next(a for a in store.arms.values()
               if a["block"] == "D1" and a["model"] == "gemini-2.5-flash"
               and "-neu-" in a["templateId"])

    g_gem = pd_game(*[gem["bindings"][k] for k in ("rr", "rs", "rt", "rp")])

    def gem_req(i):
        return dict(good, arm=gem, game_def=g_gem, seed=gem["seeds"][i],
                    episode_index=i + 1, model="gemini-2.5-flash")

    clean = FakeGeminiProvider(["J", "F"])
    r_gem = run_llm_p4(
        eng_tmp, arm=gem, pinned=validate_run_request(**gem_req(0)), game_def=g_gem,
        strategy1_slug="llm-subject", strategy2_slug="llm-subject",
        num_rounds=1, seed=gem["seeds"][0], model="gemini-2.5-flash", episode_index=1,
        sentinel_check_index=None, store=store, ledger=ledger,
        provider_factory=lambda m: (clean, "gemini"),
    )
    ok("gemini-kind run passes with thoughts=0", not r_gem["invalidTrial"], str(r_gem["meta"]))
    rep_gem = replay_llm_p4(eng_tmp, r_gem["engineRunId"], store=store)
    ok("gemini-kind replay ok (gemini mirror-sha path)", rep_gem["ok"], str(rep_gem["mismatches"][:5]))

    before_g = ledger.totals()["globalCalls"]
    thinky = FakeGeminiProvider(["J", "F"], thoughts=7)
    try:
        run_llm_p4(
            eng_tmp, arm=gem, pinned=validate_run_request(**gem_req(1)), game_def=g_gem,
            strategy1_slug="llm-subject", strategy2_slug="llm-subject",
            num_rounds=1, seed=gem["seeds"][1], model="gemini-2.5-flash", episode_index=2,
            sentinel_check_index=None, store=store, ledger=ledger,
            provider_factory=lambda m: (thinky, "gemini"),
        )
        ok("nonzero thoughts_token_count aborts", False)
    except RuntimeError as e:
        ok("nonzero thoughts_token_count aborts", "hidden reasoning tokens" in str(e), str(e)[:200])
    ok("aborted thoughts run kept its spend row", ledger.totals()["globalCalls"] == before_g + 1)

    headless = FakeGeminiProvider(["J", "F"], omit_thoughts=True)
    try:
        run_llm_p4(
            eng_tmp, arm=gem, pinned=validate_run_request(**gem_req(2)), game_def=g_gem,
            strategy1_slug="llm-subject", strategy2_slug="llm-subject",
            num_rounds=1, seed=gem["seeds"][2], model="gemini-2.5-flash", episode_index=3,
            sentinel_check_index=None, store=store, ledger=ledger,
            provider_factory=lambda m: (headless, "gemini"),
        )
        ok("missing thoughts_token_count aborts", False)
    except RuntimeError as e:
        ok("missing thoughts_token_count aborts", "no thoughts_token_count" in str(e), str(e)[:200])

    print(f"\nALL {PASS} CHECKS PASSED — temp dir {_TMP} (real ledger untouched)")


if __name__ == "__main__":
    main()
