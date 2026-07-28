"""Phase 5 live runner + extended replay — persona × temperature extension.

Same §F.3 capture contract as phase4_runner.py (byte-untouched), plus the
three sealed Phase 5 rules, enforced at the runner layer on EVERY call:

  R1-persona-composition (replay layer mirror in replay_llm_p5): the system
      text sent to the provider is compose_persona_system(preamble,
      bare_system) — preamble + "\n\n" + sealed bare system, byte-identical;
      bare arms send the bare system unchanged.
  R2-per-T-echo: assert_temperature_echo(mirror, model, arm_T) runs before
      every dispatch; the mirror is already asserted == the wire body sha.
  R3-revision-pin: assert_revision_pin(model, returned_model) runs on every
      response, after archiving (spend kept), before parsing.
"""
from __future__ import annotations

import json
import time
from typing import Any, Callable, Optional

from activegraph import Event, Graph, Runtime
from activegraph.llm.cache import LLMCache
from activegraph.store import open_store

from engine import Engine, new_run_id, _public_rounds, _summarize
from strategies import CountingRng, get_action
from llm_subject import (
    InvalidTrialError,
    PARSER_VERSION,
    build_prompt,
    load_registry,
    parse_action,
    render_prompt,
)
from provenance import bundle_sha256, engine_commit, provider_route, request_body_sha
from phase4 import BudgetExceededError
from phase4_providers import make_provider_p4
from phase4_runner import _mirror_body, _Counters, LLM_SLUG, TRANSPORT_ATTEMPTS
from phase5 import (
    ArmStoreP5,
    BudgetLedgerP5,
    PHASE5_PROTOCOL,
    PersonaStore,
    assert_revision_pin,
    assert_temperature_echo,
    compose_persona_system,
)


def _render_p5(registry: dict, llm_cfg: dict, *, seat: int, round_number: int,
               history: list[dict], game_def: dict, num_rounds: int,
               retry_raw: Optional[str]) -> tuple[str, str]:
    """Sealed render path: bare Phase 3/4 renderer, then R1 composition.
    The user layer is byte-identical to the bare twin by construction."""
    system, user = render_prompt(
        registry, llm_cfg["promptId"], seat=seat, round_number=round_number,
        history=history, game_def=game_def, num_rounds=num_rounds,
        protocol=llm_cfg, retry_raw=retry_raw,
    )
    if llm_cfg.get("personaPreamble"):
        system = compose_persona_system(llm_cfg["personaPreamble"], system)
    return system, user


def _decide_live_p5(
    *, graph: Graph, provider, provider_kind: str, ledger: BudgetLedgerP5,
    run_id: str, registry: dict, llm_cfg: dict, game_def: dict, seed: int,
    seat: int, round_number: int, num_rounds: int, history: list[dict],
    counters: _Counters, seen_hashes: set[str],
) -> tuple[int, str, int]:
    arm_id = llm_cfg["armId"]
    block = llm_cfg["block"]
    retry_raw: Optional[str] = None
    for attempt in (0, 1):
        system, user = _render_p5(
            registry, llm_cfg, seat=seat, round_number=round_number,
            history=history, game_def=game_def, num_rounds=num_rounds,
            retry_raw=retry_raw)
        prompt = build_prompt(system, user, model=llm_cfg["model"],
                              temperature=llm_cfg["temperature"],
                              max_tokens=llm_cfg["maxTokens"])
        ph = prompt.hash()
        if ph in seen_hashes:
            raise RuntimeError(f"prompt hash collision within run: {ph}")
        seen_hashes.add(ph)

        mirror = _mirror_body(llm_cfg["model"], prompt)
        # R2-per-T-echo: the request body's temperature must equal the arm's
        # pinned temperature — asserted BEFORE dispatch, per call, per T.
        assert_temperature_echo(mirror, llm_cfg["model"], llm_cfg["temperature"])
        mirror_sha = request_body_sha(mirror)
        bundle = bundle_sha256(system, user)

        req_id = graph.ids.event()
        graph.emit(Event(
            id=req_id, type="llm.requested",
            payload={
                "armId": arm_id, "block": block,
                "templateId": llm_cfg["promptId"],
                "templateSha256": llm_cfg["templateSha256"],
                "substitutions": llm_cfg["substitutions"],
                "personaId": llm_cfg.get("personaId"),
                "personaSha256": llm_cfg.get("personaSha256"),
                "bundleSha256": bundle,
                "system": system, "user": user,
                "requestBodySha256": mirror_sha,
                "parserVersion": PARSER_VERSION,
                "engineCommit": engine_commit(),
                "providerRoute": provider_route(provider_kind),
                "model": llm_cfg["model"],
                "temperature": llm_cfg["temperature"],
                "maxTokens": llm_cfg["maxTokens"],
                "topP": PHASE5_PROTOCOL["topP"],
                "registrySha256": llm_cfg["registrySha256"],
                "armsManifestSha256": llm_cfg["armsManifestSha256"],
                "promptId": llm_cfg["promptId"],
                "prompt_hash": ph,
                "seed": seed, "seat": seat, "roundNumber": round_number,
                "episodeIndex": llm_cfg.get("episodeIndex"),
                "sentinelCheckIndex": llm_cfg.get("sentinelCheckIndex"),
                "attempt": attempt,
                "retryCause": "parse_failure" if attempt == 1 else None,
            },
            actor=LLM_SLUG,
        ))

        response = None
        last_err: Optional[Exception] = None
        for t_attempt in range(TRANSPORT_ATTEMPTS):
            counters.transport_attempts += 1
            row_id = ledger.reserve_call(
                run_id=run_id, arm_id=arm_id, block=block, model=llm_cfg["model"],
                run_call_index=counters.transport_attempts,
                note=f"seat{seat} r{round_number} a{attempt} t{t_attempt}")
            try:
                response = provider.complete(
                    system=prompt.system, messages=prompt.messages, model=prompt.model,
                    max_tokens=prompt.max_tokens, temperature=prompt.temperature,
                    top_p=prompt.top_p, output_schema=None, timeout_seconds=60.0)
                break
            except Exception as e:
                last_err = e
                ledger.record_tokens(
                    row_id, 0, 0,
                    note=f"transport-failure seat{seat} r{round_number} a{attempt} t{t_attempt}: {type(e).__name__}")
                if t_attempt < TRANSPORT_ATTEMPTS - 1:
                    time.sleep(1.5 * (t_attempt + 1))
        if response is None:
            raise RuntimeError(
                f"LLM provider failed after {TRANSPORT_ATTEMPTS} attempts: {last_err}")

        counters.llm_calls += 1
        counters.input_tokens += int(response.input_tokens or 0)
        counters.output_tokens += int(response.output_tokens or 0)
        if attempt == 1:
            counters.retried_calls += 1
        ledger.record_tokens(row_id, int(response.input_tokens or 0), int(response.output_tokens or 0))

        actual_sha = (response.provider_meta or {}).get("request_body_sha256")
        if actual_sha != mirror_sha:
            raise RuntimeError(
                f"request-body sha mismatch: mirror {mirror_sha[:16]}… != actual {str(actual_sha)[:16]}… "
                f"(capture would lie about the wire; aborting)")

        resp_id = graph.ids.event()
        graph.emit(Event(
            id=resp_id, type="llm.responded",
            payload={**response.to_dict(),
                     "seat": seat, "roundNumber": round_number, "attempt": attempt,
                     "budgetRowId": row_id},
            actor=LLM_SLUG, caused_by=req_id,
        ))

        # gemini hidden-reasoning assertion, unchanged from Phase 4
        if provider_kind == "gemini":
            meta = response.provider_meta or {}
            if "thoughts_token_count" not in meta:
                raise RuntimeError(
                    "gemini call returned no thoughts_token_count in provider_meta; "
                    "cannot verify thinking stayed disabled (aborting; response archived, spend kept)")
            if int(meta["thoughts_token_count"] or 0) != 0:
                raise RuntimeError(
                    f"gemini call consumed hidden reasoning tokens "
                    f"(thoughts_token_count={meta['thoughts_token_count']}); protocol pins "
                    f"thinking_budget=0 (aborting; response archived, spend kept)")

        # R3-revision-pin: after archiving (spend kept), before parsing.
        assert_revision_pin(llm_cfg["model"], response.to_dict().get("model"))

        action = parse_action(registry, llm_cfg["promptId"], response.raw_text)
        graph.emit(Event(
            id=graph.ids.event(), type="decision.parsed",
            payload={
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
        payload={"seat": seat, "roundNumber": round_number,
                 "rawText": (retry_raw or "")[:500],
                 "reason": "reply unparseable after 1 retry", "armId": arm_id},
        actor="engine",
    ))
    raise InvalidTrialError(seat, round_number, retry_raw or "")


def _llm_cfg_p5(arm: dict, pinned: dict, *, model: str, registry_sha: str,
                store: ArmStoreP5, episode_index: Optional[int],
                sentinel_check_index: Optional[int]) -> dict[str, Any]:
    cfg: dict[str, Any] = {
        "model": model,
        "temperature": pinned["temperature"],
        "maxTokens": PHASE5_PROTOCOL["maxTokens"],
        "promptId": pinned["templateId"],
        "registrySha256": registry_sha,
        "armId": arm["armId"],
        "block": pinned["block"],
        "templateSha256": pinned["templateSha256"],
        "substitutions": pinned["substitutions"],
        "personaId": pinned["personaId"],
        "personaSha256": pinned["personaSha256"],
        "personaPreamble": pinned["personaPreamble"],
        "parserVersion": PARSER_VERSION,
        "engineCommit": engine_commit(),
        "armsManifestSha256": store.manifest_sha,
        "episodeIndex": episode_index,
        "sentinelCheckIndex": sentinel_check_index,
    }
    if pinned["deltaPct"] is not None:
        cfg["deltaPct"] = pinned["deltaPct"]
    if "framing" in pinned["substitutions"]:
        cfg["framing"] = pinned["substitutions"]["framing"]
    return cfg


def run_llm_p5(
    engine: Engine, *, arm: dict, pinned: dict, game_def: dict,
    strategy1_slug: str, strategy2_slug: str, num_rounds: int, seed: int,
    model: str, episode_index: Optional[int],
    sentinel_check_index: Optional[int], store: ArmStoreP5,
    ledger: BudgetLedgerP5,
    provider_factory: Optional[Callable[[str], tuple[Any, str]]] = None,
) -> dict[str, Any]:
    """Execute one Phase 5 run. `pinned` comes from
    phase5.validate_run_request_p5 — enforcement happened BEFORE this call."""
    registry, registry_sha = load_registry()
    ledger.check_caps(pinned["block"])

    provider, provider_kind = (provider_factory or make_provider_p4)(model)
    run_id = new_run_id()
    graph = Graph(run_id=run_id)
    rt = Runtime(graph, behaviors=[], persist_to=engine.url)

    llm_cfg = _llm_cfg_p5(arm, pinned, model=model, registry_sha=registry_sha,
                          store=store, episode_index=episode_index,
                          sentinel_check_index=sentinel_check_index)

    graph.add_object("game", {
        "gameDef": game_def,
        "strategy1Slug": strategy1_slug, "strategy2Slug": strategy2_slug,
        "numRounds": num_rounds, "seed": seed, "llm": llm_cfg, "phase": "5",
    }, actor="engine")

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
                if slug != LLM_SLUG:
                    action, reasoning = get_action(slug, history, player_num, game_def, rng)
                    actions[player_num] = action
                    reasonings[player_num] = reasoning
                    continue
                action, raw, attempt = _decide_live_p5(
                    graph=graph, provider=provider, provider_kind=provider_kind,
                    ledger=ledger, run_id=run_id, registry=registry,
                    llm_cfg=llm_cfg, game_def=game_def, seed=seed, seat=player_num,
                    round_number=n, num_rounds=num_rounds, history=history,
                    counters=counters, seen_hashes=seen_hashes)
                suffix = " (after 1 retry)" if attempt == 1 else ""
                reasonings[player_num] = f"LLM reply: {raw.strip()!r}{suffix}"
                actions[player_num] = action

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
                payload={**round_data, "strategy1Slug": strategy1_slug,
                         "strategy2Slug": strategy2_slug},
                actor="engine"))
            history.append({"p1Action": actions[1], "p2Action": actions[2],
                            "p1Payoff": p1_payoff, "p2Payoff": p2_payoff})
            rounds.append(round_data)

        graph.emit(Event(
            id=graph.ids.event(), type="run.completed",
            payload={"numRounds": num_rounds,
                     "player1TotalPayoff": sum(r["player1Payoff"] for r in rounds),
                     "player2TotalPayoff": sum(r["player2Payoff"] for r in rounds)},
            actor="engine"))
    except InvalidTrialError:
        invalid = True
    except BudgetExceededError as e:
        raise RuntimeError(json.dumps({
            "error": f"BudgetExceededError: {e}", "engineRunId": run_id,
            "llmCalls": counters.llm_calls,
            "transportAttempts": counters.transport_attempts,
            "inputTokens": counters.input_tokens,
            "outputTokens": counters.output_tokens,
            "partial": True, "budgetExceeded": True})) from e
    except Exception as e:
        raise RuntimeError(json.dumps({
            "error": f"{type(e).__name__}: {e}", "engineRunId": run_id,
            "llmCalls": counters.llm_calls,
            "transportAttempts": counters.transport_attempts,
            "inputTokens": counters.input_tokens,
            "outputTokens": counters.output_tokens,
            "partial": True})) from e
    finally:
        rt.save_state()

    meta = {
        "armId": arm["armId"], "block": pinned["block"],
        "templateId": pinned["templateId"], "templateSha256": pinned["templateSha256"],
        "personaId": pinned["personaId"], "personaSha256": pinned["personaSha256"],
        "llmCalls": counters.llm_calls,
        "transportAttempts": counters.transport_attempts,
        "retriedCalls": counters.retried_calls,
        "inputTokens": counters.input_tokens, "outputTokens": counters.output_tokens,
        "model": model,
        "temperature": pinned["temperature"],
        "maxTokens": PHASE5_PROTOCOL["maxTokens"],
        "promptId": pinned["templateId"],
        "promptRegistrySha256": registry_sha,
        "armsManifestSha256": store.manifest_sha,
        "parserVersion": PARSER_VERSION,
        "engineCommit": engine_commit(),
        "episodeIndex": episode_index,
        "spendRows": ledger.run_rows(run_id),
    }
    if invalid:
        return {"engineRunId": run_id, "seed": seed, "invalidTrial": True,
                "rounds": [], "meta": meta}
    return {"engineRunId": run_id, "seed": seed, "invalidTrial": False,
            "rounds": _public_rounds(rounds), **_summarize(rounds, game_def),
            "meta": meta}


def dry_run_p5(*, arm: dict, pinned: dict, game_def: dict, num_rounds: int,
               seed: int, model: str, store: ArmStoreP5) -> dict[str, Any]:
    """Enforcement + round-1 seat-1 render (R1 composition included) + all
    shas + R2 echo assertion. ZERO events, ZERO spend, ZERO providers."""
    registry, registry_sha = load_registry()
    llm_cfg = _llm_cfg_p5(arm, pinned, model=model, registry_sha=registry_sha,
                          store=store, episode_index=None, sentinel_check_index=None)
    system, user = _render_p5(registry, llm_cfg, seat=1, round_number=1,
                              history=[], game_def=game_def,
                              num_rounds=num_rounds, retry_raw=None)
    prompt = build_prompt(system, user, model=model,
                          temperature=llm_cfg["temperature"],
                          max_tokens=llm_cfg["maxTokens"])
    mirror = _mirror_body(model, prompt)
    assert_temperature_echo(mirror, model, llm_cfg["temperature"])
    return {
        "dryRun": True,
        "armId": arm["armId"], "block": pinned["block"],
        "templateId": pinned["templateId"], "templateSha256": pinned["templateSha256"],
        "personaId": pinned["personaId"], "personaSha256": pinned["personaSha256"],
        "temperature": llm_cfg["temperature"],
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


def replay_llm_p5(engine: Engine, run_id: str, *, store: ArmStoreP5,
                  personas: PersonaStore) -> dict[str, Any]:
    """Extended pure replay, Phase 5: everything Phase 4 replay checks, plus
    the R1 composition re-derivation (persona preamble re-fetched from the
    SEALED persona store by recorded personaId, sha re-verified, system re-
    composed byte-identically) and the R2/R3 record checks (recorded request
    temperature == arm pin; recorded returned model == revision pin).
    Zero live calls, structurally."""
    from phase5 import PINNED_REVISIONS, render_substitutions_p5

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
        raise ValueError("not a Phase 5 LLM run (no armId on llm config)")

    mismatches: list[str] = []
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
                f"template sha drift: current {current_sha[:16]}… != recorded "
                f"{str(llm_cfg.get('templateSha256'))[:16]}…")

    # R1 replay mirror: re-fetch the persona from the SEALED store and
    # re-verify the recorded pins — recorded preamble text is never trusted.
    persona_preamble = None
    if llm_cfg.get("personaId") is not None:
        try:
            p = personas.get(llm_cfg["personaId"])
            if p["sha256"] != llm_cfg.get("personaSha256"):
                mismatches.append(
                    f"R1: recorded persona sha {str(llm_cfg.get('personaSha256'))[:16]}… != "
                    f"sealed {p['sha256'][:16]}… for {p['id']}")
            persona_preamble = p["preamble"]
        except Exception as e:
            mismatches.append(f"R1: persona re-fetch failed: {e}")

    # R2/R3 record checks
    if arm is not None and float(llm_cfg.get("temperature", -1)) != float(arm["temperature"]):
        mismatches.append(
            f"R2: recorded temperature {llm_cfg.get('temperature')} != arm pin {arm['temperature']}")
    pin = PINNED_REVISIONS.get(llm_cfg.get("model"))
    for e in events:
        if e.type == "llm.responded":
            returned = e.payload.get("model")
            if pin is not None and returned != pin:
                mismatches.append(
                    f"R3: recorded returned model {returned!r} != revision pin {pin!r}")

    if arm is not None:
        try:
            from provenance import canonical_json as _cj
            re_subs = render_substitutions_p5(arm, tid, registry)
            if _cj(re_subs) != _cj(llm_cfg.get("substitutions")):
                mismatches.append("substitutions re-derived from arm bindings differ from recorded")
        except Exception as e:
            mismatches.append(f"substitution re-derivation failed: {e}")

    registry_file_drift = None
    if llm_cfg.get("registrySha256") != registry_sha:
        registry_file_drift = {
            "recorded": llm_cfg.get("registrySha256"), "current": registry_sha,
            "note": "append-only registry grew since this run; per-prompt byte verification is authoritative"}

    requested = [e for e in events if e.type == "llm.requested"]
    parsed_events = {
        (e.payload["seat"], e.payload["roundNumber"], e.payload["attempt"]): e.payload
        for e in events if e.type == "decision.parsed"}
    invalidated = [e for e in events if e.type == "trial.invalidated"]
    cache = LLMCache.from_events(events)
    req_by_hash = {e.payload["prompt_hash"]: e.payload for e in requested}

    def _base_report(**kw):
        return {"engineRunId": run_id, "ok": len(mismatches) == 0,
                "recordedLlmCalls": len(requested), "liveCalls": 0,
                "promptRegistrySha256": registry_sha,
                "armsManifestSha256": store.manifest_sha,
                "registryFileDrift": registry_file_drift,
                "parserVersion": PARSER_VERSION,
                "mismatches": mismatches[:20], **kw}

    if invalidated:
        return _base_report(invalidTrial=True, llmCallsVerified=0, roundsCompared=0,
                            bundleShasVerified=0, requestBodyShasVerified=0,
                            parsedActionsVerified=0)

    game_def = g["gameDef"]
    strategy1_slug = g["strategy1Slug"]
    strategy2_slug = g["strategy2Slug"]
    num_rounds = g["numRounds"]
    seed = g["seed"]

    stored_rounds = sorted((o.data for o in graph.objects("round")),
                           key=lambda r: r["roundNumber"])
    if len(stored_rounds) != num_rounds:
        mismatches.append(f"stored rounds {len(stored_rounds)} != numRounds {num_rounds}")

    replay_cfg = dict(llm_cfg)
    replay_cfg["personaPreamble"] = persona_preamble

    history: list[dict] = []
    consumed = 0
    verified = bundles_ok = bodies_ok = parses_ok = rebuilt_calls = 0

    for n in range(1, len(stored_rounds) + 1):
        rng = CountingRng(seed, advance=consumed)
        actions: dict[int, int] = {}
        for player_num in (1, 2):
            slug = strategy1_slug if player_num == 1 else strategy2_slug
            if slug != LLM_SLUG:
                action, _reasoning = get_action(slug, history, player_num, game_def, rng)
                actions[player_num] = action
                continue
            retry_raw: Optional[str] = None
            action: Optional[int] = None
            for attempt in (0, 1):
                system, user = _render_p5(
                    registry, replay_cfg, seat=player_num, round_number=n,
                    history=history, game_def=game_def, num_rounds=num_rounds,
                    retry_raw=retry_raw)
                prompt = build_prompt(system, user, model=replay_cfg["model"],
                                      temperature=replay_cfg["temperature"],
                                      max_tokens=replay_cfg["maxTokens"])
                ph = prompt.hash()
                resp = cache.get(ph)
                rebuilt_calls += 1
                if resp is None:
                    mismatches.append(
                        f"round {n} seat {player_num} attempt {attempt}: rebuilt prompt "
                        f"hash {ph[:16]}… not in recorded cache")
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
                    if request_body_sha(_mirror_body(replay_cfg["model"], prompt)) == req.get("requestBodySha256"):
                        bodies_ok += 1
                    else:
                        mismatches.append(f"round {n} seat {player_num} a{attempt}: request-body sha mismatch")
                action = parse_action(registry, tid, resp.raw_text)
                rec = parsed_events.get((player_num, n, attempt))
                if rec is None:
                    mismatches.append(f"round {n} seat {player_num} a{attempt}: no decision.parsed event")
                elif rec.get("action") != action:
                    mismatches.append(
                        f"round {n} seat {player_num} a{attempt}: re-parsed action {action} != recorded {rec.get('action')}")
                else:
                    parses_ok += 1
                if action is not None:
                    break
                retry_raw = resp.raw_text
            if action is None:
                mismatches.append(f"round {n} seat {player_num}: recorded replies unparseable in replay")
                break
            actions[player_num] = action
        if len(actions) != 2:
            break

        stored = stored_rounds[n - 1]
        if rng.calls != stored.get("rngCalls", 0):
            mismatches.append(f"round {n}: rng draws {rng.calls} != stored {stored.get('rngCalls', 0)}")
        p1_payoff, p2_payoff = game_def["payoffMatrix"][actions[1]][actions[2]]
        if actions[1] != stored["player1Action"] or actions[2] != stored["player2Action"]:
            mismatches.append(
                f"round {n}: replayed actions ({actions[1]},{actions[2]}) != stored "
                f"({stored['player1Action']},{stored['player2Action']})")
        elif p1_payoff != stored["player1Payoff"] or p2_payoff != stored["player2Payoff"]:
            mismatches.append(
                f"round {n}: replayed payoffs ({p1_payoff},{p2_payoff}) != stored "
                f"({stored['player1Payoff']},{stored['player2Payoff']})")
        consumed += rng.calls
        history.append({"p1Action": stored["player1Action"], "p2Action": stored["player2Action"],
                        "p1Payoff": stored["player1Payoff"], "p2Payoff": stored["player2Payoff"]})

    if not mismatches and rebuilt_calls != len(requested):
        mismatches.append(
            f"recorded llm.requested events ({len(requested)}) != rebuilt prompts ({rebuilt_calls})")

    return _base_report(
        invalidTrial=False, llmCallsVerified=verified, roundsCompared=len(stored_rounds),
        bundleShasVerified=bundles_ok, requestBodyShasVerified=bodies_ok,
        parsedActionsVerified=parses_ok)
