"""Phase 4 live runner + extended replay (§F.3 capture, 15 fields per call).

Differences from the sealed Phase 3 runner (llm_runner.py, untouched):
  * every provider call reserves a budget-ledger row transactionally BEFORE
    dispatch (transport retries reserve separately — burned calls are never
    invisible);
  * llm.requested carries the full §F.3 record: arm ID, template ID + sha,
    substitutions, bundle sha, request-body sha (mirror), parser version,
    engine commit, provider route, retry cause;
  * the provider's provider_meta.request_body_sha256 (actual) is asserted
    equal to the mirror on every call — capture cannot drift from the wire;
  * a `decision.parsed` event records the parsed DISPLAYED option per call;
  * replay re-renders and byte-compares bundle sha + request-body sha and
    re-parses raw replies against the recorded parsed action.

Dry runs (enforcement + round-1 render + shas, zero events, zero spend,
zero provider construction) exist so the enforcement layer is testable
before the registry is sealed and before any live row is authorized.
"""
from __future__ import annotations

import json
import time
from typing import Any, Callable, Optional

from activegraph import Event, Graph, Runtime
from activegraph.llm.cache import LLMCache
from activegraph.store import open_store

from engine import Engine, new_run_id, _public_rounds, _summarize
from strategies import STRATEGIES, CountingRng, get_action
from llm_subject import (
    InvalidTrialError,
    PARSER_VERSION,
    build_prompt,
    load_registry,
    parse_action,
    render_prompt,
)
from provenance import (
    bundle_sha256,
    engine_commit,
    gemini_request_body,
    openai_request_body,
    provider_route,
    request_body_sha,
)
from phase4 import (
    PHASE4_PROTOCOL,
    ArmStore,
    BudgetExceededError,
    BudgetLedger,
    render_substitutions,
)
from phase4_providers import make_provider_p4

LLM_SLUG = "llm-subject"
TRANSPORT_ATTEMPTS = 3
GEMINI_THINKING_BUDGET = 0  # registered vendor-adapter setting (amendment A1)


def _mirror_body(model: str, prompt) -> dict:
    system = prompt.system
    user = prompt.messages[0].content
    if model.startswith("gpt-"):
        return openai_request_body(
            model=model, system=system, user=user,
            max_tokens=prompt.max_tokens, temperature=prompt.temperature, top_p=prompt.top_p,
        )
    if model.startswith("gemini-"):
        return gemini_request_body(
            model=model, system=system, user=user,
            max_tokens=prompt.max_tokens, temperature=prompt.temperature, top_p=prompt.top_p,
            thinking_budget=GEMINI_THINKING_BUDGET,
        )
    raise RuntimeError(f"no request-body mirror for model {model}")


class _Counters:
    def __init__(self) -> None:
        self.llm_calls = 0          # responses received
        self.transport_attempts = 0  # ledger reservations (≥ llm_calls)
        self.retried_calls = 0       # parse retries (attempt 1)
        self.input_tokens = 0
        self.output_tokens = 0


def _decide_live_p4(
    *,
    graph: Graph,
    provider,
    provider_kind: str,
    ledger: BudgetLedger,
    run_id: str,
    registry: dict,
    llm_cfg: dict,
    game_def: dict,
    seed: int,
    seat: int,
    round_number: int,
    num_rounds: int,
    history: list[dict],
    counters: _Counters,
    seen_hashes: set[str],
) -> tuple[int, str, int]:
    """One subject decision, ≤2 stimulus attempts (original + 1 parse retry),
    each stimulus attempt ≤TRANSPORT_ATTEMPTS provider calls."""
    arm_id = llm_cfg["armId"]
    block = llm_cfg["block"]
    retry_raw: Optional[str] = None
    for attempt in (0, 1):
        system, user = render_prompt(
            registry, llm_cfg["promptId"],
            seat=seat, round_number=round_number, history=history,
            game_def=game_def, num_rounds=num_rounds, protocol=llm_cfg,
            retry_raw=retry_raw,
        )
        prompt = build_prompt(
            system, user,
            model=llm_cfg["model"], temperature=llm_cfg["temperature"],
            max_tokens=llm_cfg["maxTokens"],
        )
        ph = prompt.hash()
        if ph in seen_hashes:
            raise RuntimeError(f"prompt hash collision within run: {ph}")
        seen_hashes.add(ph)

        mirror = _mirror_body(llm_cfg["model"], prompt)
        mirror_sha = request_body_sha(mirror)
        bundle = bundle_sha256(system, user)

        req_id = graph.ids.event()
        graph.emit(Event(
            id=req_id, type="llm.requested",
            payload={
                # §F.3 fields 1–6, 9–11, 13–15 (7/8/12 land on responded/parsed)
                "armId": arm_id,                              # 1
                "block": block,
                "templateId": llm_cfg["promptId"],            # 2
                "templateSha256": llm_cfg["templateSha256"],  # 2
                "substitutions": llm_cfg["substitutions"],    # 3
                "bundleSha256": bundle,                       # 4
                "system": system, "user": user,               # 5
                "requestBodySha256": mirror_sha,              # 6 (mirror; actual asserted below)
                "parserVersion": PARSER_VERSION,              # 9
                "engineCommit": engine_commit(),              # 10
                "providerRoute": provider_route(provider_kind),  # 11
                "model": llm_cfg["model"],                    # 13 (requested)
                "temperature": llm_cfg["temperature"],
                "maxTokens": llm_cfg["maxTokens"],
                "topP": PHASE4_PROTOCOL["topP"],
                "registrySha256": llm_cfg["registrySha256"],
                "armsManifestSha256": llm_cfg["armsManifestSha256"],
                "promptId": llm_cfg["promptId"],
                "prompt_hash": ph,
                "seed": seed,  # environment seed — exact event-store identity for recovery (additive; disclosed)
                "seat": seat, "roundNumber": round_number,
                "episodeIndex": llm_cfg.get("episodeIndex"),
                "sentinelCheckIndex": llm_cfg.get("sentinelCheckIndex"),
                "attempt": attempt,                           # 15
                "retryCause": "parse_failure" if attempt == 1 else None,  # 15
            },
            actor=LLM_SLUG,
        ))

        response = None
        last_err: Optional[Exception] = None
        for t_attempt in range(TRANSPORT_ATTEMPTS):
            # field: transactional pre-dispatch reservation (every call, incl. retries)
            counters.transport_attempts += 1
            row_id = ledger.reserve_call(
                run_id=run_id, arm_id=arm_id, block=block, model=llm_cfg["model"],
                run_call_index=counters.transport_attempts,
                note=f"seat{seat} r{round_number} a{attempt} t{t_attempt}",
            )
            try:
                response = provider.complete(
                    system=prompt.system, messages=prompt.messages, model=prompt.model,
                    max_tokens=prompt.max_tokens, temperature=prompt.temperature,
                    top_p=prompt.top_p, output_schema=None, timeout_seconds=60.0,
                )
                break
            except Exception as e:
                last_err = e
                ledger.record_tokens(
                    row_id, 0, 0,
                    note=f"transport-failure seat{seat} r{round_number} a{attempt} t{t_attempt}: {type(e).__name__}",
                )
                if t_attempt < TRANSPORT_ATTEMPTS - 1:
                    time.sleep(1.5 * (t_attempt + 1))
        if response is None:
            raise RuntimeError(
                f"LLM provider failed after {TRANSPORT_ATTEMPTS} attempts: {last_err}"
            )

        counters.llm_calls += 1
        counters.input_tokens += int(response.input_tokens or 0)
        counters.output_tokens += int(response.output_tokens or 0)
        if attempt == 1:
            counters.retried_calls += 1
        ledger.record_tokens(row_id, int(response.input_tokens or 0), int(response.output_tokens or 0))

        # capture honesty: the sha of what the provider ACTUALLY sent must
        # equal the mirror recorded in llm.requested — hard abort otherwise.
        actual_sha = (response.provider_meta or {}).get("request_body_sha256")
        if actual_sha != mirror_sha:
            raise RuntimeError(
                f"request-body sha mismatch: mirror {mirror_sha[:16]}… != actual {str(actual_sha)[:16]}… "
                f"(capture would lie about the wire; aborting)"
            )

        resp_id = graph.ids.event()
        graph.emit(Event(
            id=resp_id, type="llm.responded",
            payload={
                **response.to_dict(),  # 7 raw completion, 12 response id (provider_meta), 13 returned model
                "seat": seat, "roundNumber": round_number, "attempt": attempt,
                "budgetRowId": row_id,
            },
            actor=LLM_SLUG, caused_by=req_id,
        ))

        # provider-packet §2 commitment: gemini hidden reasoning must stay OFF —
        # thoughts_token_count is ASSERTED zero on every call, never assumed.
        # Placed after the llm.responded emit so the offending response is
        # archived as evidence, and before parsing so no decision legitimizes it.
        if provider_kind == "gemini":
            meta = response.provider_meta or {}
            if "thoughts_token_count" not in meta:
                raise RuntimeError(
                    "gemini call returned no thoughts_token_count in provider_meta; "
                    "cannot verify thinking stayed disabled (aborting; response archived, spend kept)"
                )
            if int(meta["thoughts_token_count"] or 0) != 0:
                raise RuntimeError(
                    f"gemini call consumed hidden reasoning tokens "
                    f"(thoughts_token_count={meta['thoughts_token_count']}); protocol pins "
                    f"thinking_budget=0 (aborting; response archived, spend kept)"
                )

        action = parse_action(registry, llm_cfg["promptId"], response.raw_text)
        graph.emit(Event(
            id=graph.ids.event(), type="decision.parsed",
            payload={  # 8: parsed action = DISPLAYED option index (role derived in analysis)
                "seat": seat, "roundNumber": round_number, "attempt": attempt,
                "action": action,
                "displayedOption": None if action is None else registry["prompts"][llm_cfg["promptId"]]["options"][action],
                "parserVersion": PARSER_VERSION,
                "valid": action is not None,
            },
            actor="engine", caused_by=resp_id,
        ))
        if action is not None:
            return action, response.raw_text, attempt
        retry_raw = response.raw_text

    graph.emit(Event(
        id=graph.ids.event(), type="trial.invalidated",
        payload={
            "seat": seat, "roundNumber": round_number,
            "rawText": (retry_raw or "")[:500],
            "reason": "reply unparseable after 1 retry",
            "armId": arm_id,
        },
        actor="engine",
    ))
    raise InvalidTrialError(seat, round_number, retry_raw or "")


def run_llm_p4(
    engine: Engine,
    *,
    arm: dict,
    pinned: dict,
    game_def: dict,
    strategy1_slug: str,
    strategy2_slug: str,
    num_rounds: int,
    seed: int,
    model: str,
    episode_index: Optional[int],
    sentinel_check_index: Optional[int],
    store: ArmStore,
    ledger: BudgetLedger,
    provider_factory: Optional[Callable[[str], tuple[Any, str]]] = None,
) -> dict[str, Any]:
    """Execute one Phase 4 run. `pinned` is the validated context from
    phase4.validate_run_request — enforcement happened BEFORE this call."""
    registry, registry_sha = load_registry()
    ledger.check_caps(pinned["block"])

    provider, provider_kind = (provider_factory or make_provider_p4)(model)
    run_id = new_run_id()
    graph = Graph(run_id=run_id)
    rt = Runtime(graph, behaviors=[], persist_to=engine.url)

    llm_cfg: dict[str, Any] = {
        "model": model,
        "temperature": PHASE4_PROTOCOL["temperature"],
        "maxTokens": PHASE4_PROTOCOL["maxTokens"],
        "promptId": pinned["templateId"],
        "registrySha256": registry_sha,
        "armId": arm["armId"],
        "block": pinned["block"],
        "templateSha256": pinned["templateSha256"],
        "substitutions": pinned["substitutions"],
        "resolutionKey": pinned["resolutionKey"],
        "parserVersion": PARSER_VERSION,
        "engineCommit": engine_commit(),
        "armsManifestSha256": store.manifest_sha,
        "episodeIndex": episode_index,
        "sentinelCheckIndex": sentinel_check_index,
    }
    if pinned["deltaPct"] is not None:
        llm_cfg["deltaPct"] = pinned["deltaPct"]
    # rps-sym render params are pinned substitutions, surfaced for the renderer
    for k in ("optList", "beatsLine"):
        if k in pinned["substitutions"]:
            llm_cfg[k] = pinned["substitutions"][k]

    graph.add_object(
        "game",
        {
            "gameDef": game_def,
            "strategy1Slug": strategy1_slug,
            "strategy2Slug": strategy2_slug,
            "numRounds": num_rounds,
            "seed": seed,
            "llm": llm_cfg,
            "phase": "4",
        },
        actor="engine",
    )

    counters = _Counters()
    seen_hashes: set[str] = set()
    history: list[dict] = []
    rounds: list[dict] = []
    consumed = 0
    invalid = False

    try:
        for n in range(1, num_rounds + 1):
            rng = CountingRng(seed, advance=consumed)
            actions: dict[int, int] = {}
            reasonings: dict[int, str] = {}
            for player_num in (1, 2):
                slug = strategy1_slug if player_num == 1 else strategy2_slug
                if slug == LLM_SLUG:
                    action, raw, attempt = _decide_live_p4(
                        graph=graph, provider=provider, provider_kind=provider_kind,
                        ledger=ledger, run_id=run_id, registry=registry,
                        llm_cfg=llm_cfg, game_def=game_def, seed=seed, seat=player_num,
                        round_number=n, num_rounds=num_rounds, history=history,
                        counters=counters, seen_hashes=seen_hashes,
                    )
                    suffix = " (after 1 retry)" if attempt == 1 else ""
                    reasonings[player_num] = f"LLM reply: {raw.strip()!r}{suffix}"
                    actions[player_num] = action
                else:
                    action, reasoning = get_action(slug, history, player_num, game_def, rng)
                    actions[player_num] = action
                    reasonings[player_num] = reasoning

            p1_payoff, p2_payoff = game_def["payoffMatrix"][actions[1]][actions[2]]
            nash_set = {tuple(ne) for ne in game_def["nashEquilibria"]}
            round_data = {
                "roundNumber": n,
                "player1Action": actions[1], "player2Action": actions[2],
                "player1Payoff": p1_payoff, "player2Payoff": p2_payoff,
                "player1Reasoning": reasonings[1], "player2Reasoning": reasonings[2],
                "isNashOutcome": (actions[1], actions[2]) in nash_set,
                "rngCalls": rng.calls,
            }
            consumed += rng.calls
            graph.add_object("round", round_data, actor="engine")
            graph.emit(Event(
                id=graph.ids.event(), type="round.played",
                payload={**round_data, "strategy1Slug": strategy1_slug, "strategy2Slug": strategy2_slug},
                actor="engine",
            ))
            history.append({
                "p1Action": actions[1], "p2Action": actions[2],
                "p1Payoff": p1_payoff, "p2Payoff": p2_payoff,
            })
            rounds.append(round_data)

        graph.emit(Event(
            id=graph.ids.event(), type="run.completed",
            payload={
                "numRounds": num_rounds,
                "player1TotalPayoff": sum(r["player1Payoff"] for r in rounds),
                "player2TotalPayoff": sum(r["player2Payoff"] for r in rounds),
            },
            actor="engine",
        ))
    except InvalidTrialError:
        invalid = True
    except BudgetExceededError as e:
        raise RuntimeError(json.dumps({
            "error": f"BudgetExceededError: {e}",
            "engineRunId": run_id,
            "llmCalls": counters.llm_calls,
            "transportAttempts": counters.transport_attempts,
            "inputTokens": counters.input_tokens,
            "outputTokens": counters.output_tokens,
            "partial": True, "budgetExceeded": True,
        })) from e
    except Exception as e:
        raise RuntimeError(json.dumps({
            "error": f"{type(e).__name__}: {e}",
            "engineRunId": run_id,
            "llmCalls": counters.llm_calls,
            "transportAttempts": counters.transport_attempts,
            "inputTokens": counters.input_tokens,
            "outputTokens": counters.output_tokens,
            "partial": True,
        })) from e
    finally:
        rt.save_state()

    meta = {
        "armId": arm["armId"], "block": pinned["block"],
        "templateId": pinned["templateId"], "templateSha256": pinned["templateSha256"],
        "llmCalls": counters.llm_calls,
        "transportAttempts": counters.transport_attempts,
        "retriedCalls": counters.retried_calls,
        "inputTokens": counters.input_tokens, "outputTokens": counters.output_tokens,
        "model": model,
        "temperature": PHASE4_PROTOCOL["temperature"],
        "maxTokens": PHASE4_PROTOCOL["maxTokens"],
        "promptId": pinned["templateId"],
        "promptRegistrySha256": registry_sha,
        "armsManifestSha256": store.manifest_sha,
        "parserVersion": PARSER_VERSION,
        "engineCommit": engine_commit(),
        "episodeIndex": episode_index,
        "spendRows": ledger.run_rows(run_id),
    }
    if invalid:
        return {"engineRunId": run_id, "seed": seed, "invalidTrial": True, "rounds": [], "meta": meta}
    return {
        "engineRunId": run_id, "seed": seed, "invalidTrial": False,
        "rounds": _public_rounds(rounds), **_summarize(rounds, game_def), "meta": meta,
    }


def dry_run_p4(*, arm: dict, pinned: dict, game_def: dict, num_rounds: int,
               seed: int, model: str, store: ArmStore) -> dict[str, Any]:
    """Enforcement + round-1 seat-1 render + all shas. ZERO events, ZERO
    spend, ZERO provider construction — infrastructure verification only."""
    registry, registry_sha = load_registry()
    llm_cfg: dict[str, Any] = {
        "model": model,
        "temperature": PHASE4_PROTOCOL["temperature"],
        "maxTokens": PHASE4_PROTOCOL["maxTokens"],
        "promptId": pinned["templateId"],
    }
    if pinned["deltaPct"] is not None:
        llm_cfg["deltaPct"] = pinned["deltaPct"]
    for k in ("optList", "beatsLine"):
        if k in pinned["substitutions"]:
            llm_cfg[k] = pinned["substitutions"][k]
    system, user = render_prompt(
        registry, pinned["templateId"], seat=1, round_number=1, history=[],
        game_def=game_def, num_rounds=num_rounds, protocol=llm_cfg, retry_raw=None,
    )
    prompt = build_prompt(system, user, model=model,
                          temperature=llm_cfg["temperature"], max_tokens=llm_cfg["maxTokens"])
    mirror = _mirror_body(model, prompt)
    return {
        "dryRun": True,
        "armId": arm["armId"], "block": pinned["block"],
        "templateId": pinned["templateId"], "templateSha256": pinned["templateSha256"],
        "substitutions": pinned["substitutions"],
        "system": system, "user": user,
        "bundleSha256": bundle_sha256(system, user),
        "requestBodySha256": request_body_sha(mirror),
        "promptHash": prompt.hash(),
        "parserVersion": PARSER_VERSION,
        "engineCommit": engine_commit(),
        "registrySha256": registry_sha,
        "armsManifestSha256": store.manifest_sha,
        "liveCalls": 0,
    }


def write_resolution(
    engine: Engine, *, key: str, template_id: str, note: str,
    ledger: BudgetLedger, store: ArmStore,
) -> dict[str, Any]:
    """Resolve a RESOLVED-BY-* placeholder (E D-selected template, X2
    confirmation minimal pair). Event-sourced FIRST (audit trail), then the
    write-once ledger record the enforcement layer reads. Refuses unknown
    keys, wrong-family templates, unsealed templates, and re-resolution."""
    from phase4 import RESOLUTION_KEYS

    registry, registry_sha = load_registry()
    prefix = RESOLUTION_KEYS.get(key)
    if prefix is None:
        raise ValueError(f"unknown resolution key {key!r}; registered: {sorted(RESOLUTION_KEYS)}")
    if not template_id.startswith(prefix):
        raise ValueError(f"resolution {key} requires a {prefix}* template, got {template_id}")
    spec = registry["prompts"].get(template_id)
    if spec is None:
        raise ValueError(f"template {template_id} not in registry")
    sealed_sha = store.template_shas.get(template_id)
    if sealed_sha is None:
        raise ValueError(f"template {template_id} has no sealed sha in the arms manifest")
    existing = ledger.get_resolution(key)
    if existing is not None:
        raise ValueError(
            f"resolution {key} already written ({existing['templateId']} at {existing['ts']}); "
            "changing it requires a registered amendment"
        )

    run_id = new_run_id()
    graph = Graph(run_id=run_id)
    rt = Runtime(graph, behaviors=[], persist_to=engine.url)
    graph.emit(Event(
        id=graph.ids.event(), type="infra.phase4.resolution",
        payload={
            "key": key, "templateId": template_id, "templateSha256": sealed_sha,
            "note": note, "registrySha256": registry_sha,
            "armsManifestSha256": store.manifest_sha,
            "engineCommit": engine_commit(),
        },
        actor="engine",
    ))
    rt.save_state()
    ledger.put_resolution(key, template_id, run_id, note)
    return {"key": key, "templateId": template_id, "templateSha256": sealed_sha,
            "eventRunId": run_id}


def replay_llm_p4(engine: Engine, run_id: str, *, store: ArmStore) -> dict[str, Any]:
    """Extended pure replay (§F.3): everything Phase 3 replay checks, plus
    per-call bundle-sha byte-compare, request-body-sha recompute, parsed-action
    re-derivation against decision.parsed, template-sha recheck, and a
    budget-ledger cross-check. Zero live calls, structurally."""
    Engine._check_run_id(run_id)
    registry, registry_sha = load_registry()

    events_store = open_store(engine.url, run_id=run_id)
    events = list(events_store.iter_events())
    if not events:
        raise KeyError(f"engine run not found: {run_id}")

    rt = Runtime.load(engine.url, run_id=run_id)
    graph = rt.graph
    game_obj = next(iter(graph.objects("game")), None)
    if game_obj is None:
        raise ValueError("run has no game object")
    g = game_obj.data
    llm_cfg = g.get("llm")
    if not llm_cfg or "armId" not in llm_cfg:
        raise ValueError("not a Phase 4 LLM run (no armId on llm config)")

    mismatches: list[str] = []

    # arm + template integrity against the CURRENT sealed manifest
    arm = store.arms.get(llm_cfg["armId"])
    if arm is None:
        mismatches.append(f"arm {llm_cfg['armId']} no longer in arms manifest")
    tid = llm_cfg["promptId"]
    spec = registry["prompts"].get(tid)
    if spec is None:
        mismatches.append(f"template {tid} not in current registry")
    else:
        from provenance import template_sha as _tsha
        current_sha = _tsha(spec)
        if current_sha != llm_cfg.get("templateSha256"):
            mismatches.append(
                f"template sha drift: current {current_sha[:16]}… != recorded {str(llm_cfg.get('templateSha256'))[:16]}…"
            )
    if arm is not None:
        try:
            replay_arm = arm
            if (arm.get("armId") == "p4-sent-fallback"
                    and tid != arm.get("templateId")):
                # Sealed third-cell switch (validate_run_request /
                # _sentinel_switch_delta): post-switch dispatches render the
                # D-selected pd-rep representation with the sentinel
                # battery's donor deltaPct. The replay re-derivation must
                # apply the identical sealed rule — checker-side mirror of
                # provenance instance 5; fail-closed if the recorded
                # template is not the written E-dselected resolution.
                from phase4 import _sentinel_switch_delta
                res = BudgetLedger().get_resolution("E-dselected")
                res_tid = res["templateId"] if res else None
                if res_tid != tid:
                    mismatches.append(
                        f"sentinel fallback post-switch template {tid} != written "
                        f"E-dselected resolution {res_tid}")
                replay_arm = {**arm, "deltaPct": _sentinel_switch_delta(store)}
            re_subs = render_substitutions(replay_arm, tid, registry)
            from provenance import canonical_json as _cj
            if _cj(re_subs) != _cj(llm_cfg.get("substitutions")):
                mismatches.append("substitutions re-derived from arm bindings differ from recorded")
        except Exception as e:
            mismatches.append(f"substitution re-derivation failed: {e}")

    registry_file_drift = None
    if llm_cfg.get("registrySha256") != registry_sha:
        registry_file_drift = {
            "recorded": llm_cfg.get("registrySha256"), "current": registry_sha,
            "note": "append-only registry grew since this run; per-prompt byte verification is authoritative",
        }

    requested = [e for e in events if e.type == "llm.requested"]
    parsed_events = {
        (e.payload["seat"], e.payload["roundNumber"], e.payload["attempt"]): e.payload
        for e in events if e.type == "decision.parsed"
    }
    invalidated = [e for e in events if e.type == "trial.invalidated"]
    cache = LLMCache.from_events(events)
    req_by_hash = {e.payload["prompt_hash"]: e.payload for e in requested}

    def _base_report(**kw):
        return {
            "engineRunId": run_id, "ok": len(mismatches) == 0,
            "recordedLlmCalls": len(requested), "liveCalls": 0,
            "promptRegistrySha256": registry_sha,
            "armsManifestSha256": store.manifest_sha,
            "registryFileDrift": registry_file_drift,
            "parserVersion": PARSER_VERSION,
            "mismatches": mismatches[:20], **kw,
        }

    if invalidated:
        return _base_report(invalidTrial=True, llmCallsVerified=0, roundsCompared=0,
                            bundleShasVerified=0, requestBodyShasVerified=0, parsedActionsVerified=0)

    game_def = g["gameDef"]
    strategy1_slug = g["strategy1Slug"]
    strategy2_slug = g["strategy2Slug"]
    num_rounds = g["numRounds"]
    seed = g["seed"]

    stored_rounds = sorted((o.data for o in graph.objects("round")), key=lambda r: r["roundNumber"])
    if len(stored_rounds) != num_rounds:
        mismatches.append(f"stored rounds {len(stored_rounds)} != numRounds {num_rounds}")

    history: list[dict] = []
    consumed = 0
    verified = 0
    bundles_ok = 0
    bodies_ok = 0
    parses_ok = 0
    rebuilt_calls = 0

    for n in range(1, len(stored_rounds) + 1):
        rng = CountingRng(seed, advance=consumed)
        actions: dict[int, int] = {}
        for player_num in (1, 2):
            slug = strategy1_slug if player_num == 1 else strategy2_slug
            if slug == LLM_SLUG:
                retry_raw: Optional[str] = None
                action: Optional[int] = None
                for attempt in (0, 1):
                    system, user = render_prompt(
                        registry, tid, seat=player_num, round_number=n, history=history,
                        game_def=game_def, num_rounds=num_rounds, protocol=llm_cfg,
                        retry_raw=retry_raw,
                    )
                    prompt = build_prompt(system, user, model=llm_cfg["model"],
                                          temperature=llm_cfg["temperature"], max_tokens=llm_cfg["maxTokens"])
                    ph = prompt.hash()
                    resp = cache.get(ph)
                    rebuilt_calls += 1
                    if resp is None:
                        mismatches.append(
                            f"round {n} seat {player_num} attempt {attempt}: rebuilt prompt hash {ph[:16]}… not in recorded cache"
                        )
                        break
                    verified += 1

                    req = req_by_hash.get(ph)
                    if req is None:
                        mismatches.append(f"round {n} seat {player_num} attempt {attempt}: no llm.requested for hash")
                    else:
                        if bundle_sha256(system, user) == req.get("bundleSha256"):
                            bundles_ok += 1
                        else:
                            mismatches.append(f"round {n} seat {player_num} a{attempt}: bundle sha mismatch")
                        if request_body_sha(_mirror_body(llm_cfg["model"], prompt)) == req.get("requestBodySha256"):
                            bodies_ok += 1
                        else:
                            mismatches.append(f"round {n} seat {player_num} a{attempt}: request-body sha mismatch")

                    action = parse_action(registry, tid, resp.raw_text)
                    rec = parsed_events.get((player_num, n, attempt))
                    if rec is None:
                        mismatches.append(f"round {n} seat {player_num} a{attempt}: no decision.parsed event")
                    elif rec.get("action") != action:
                        mismatches.append(
                            f"round {n} seat {player_num} a{attempt}: re-parsed action {action} != recorded {rec.get('action')}"
                        )
                    else:
                        parses_ok += 1
                    if action is not None:
                        break
                    retry_raw = resp.raw_text
                if action is None:
                    mismatches.append(f"round {n} seat {player_num}: recorded replies unparseable in replay")
                    break
                actions[player_num] = action
            else:
                action, _reasoning = get_action(slug, history, player_num, game_def, rng)
                actions[player_num] = action
        if len(actions) != 2:
            break

        stored = stored_rounds[n - 1]
        if rng.calls != stored.get("rngCalls", 0):
            mismatches.append(f"round {n}: rng draws {rng.calls} != stored {stored.get('rngCalls', 0)}")
        p1_payoff, p2_payoff = game_def["payoffMatrix"][actions[1]][actions[2]]
        if actions[1] != stored["player1Action"] or actions[2] != stored["player2Action"]:
            mismatches.append(
                f"round {n}: replayed actions ({actions[1]},{actions[2]}) != stored ({stored['player1Action']},{stored['player2Action']})"
            )
        elif p1_payoff != stored["player1Payoff"] or p2_payoff != stored["player2Payoff"]:
            mismatches.append(
                f"round {n}: replayed payoffs ({p1_payoff},{p2_payoff}) != stored ({stored['player1Payoff']},{stored['player2Payoff']})"
            )
        consumed += rng.calls
        history.append({
            "p1Action": stored["player1Action"], "p2Action": stored["player2Action"],
            "p1Payoff": stored["player1Payoff"], "p2Payoff": stored["player2Payoff"],
        })

    if not mismatches and rebuilt_calls != len(requested):
        mismatches.append(f"recorded llm.requested events ({len(requested)}) != rebuilt prompts ({rebuilt_calls})")

    return _base_report(
        invalidTrial=False, llmCallsVerified=verified, roundsCompared=len(stored_rounds),
        bundleShasVerified=bundles_ok, requestBodyShasVerified=bodies_ok,
        parsedActionsVerified=parses_ok,
    )
