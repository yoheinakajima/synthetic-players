"""Phase 3 LLM behavioral runs: live execution + pure replay verification.

Live runs use a procedural loop (Runtime with NO behaviors) because subject
decisions are sampled, not deterministic — behaviors must stay pure. Every
decision is event-sourced exactly the way ActiveGraph's own LLM layer records
it (`llm.requested` with prompt_hash → `llm.responded` carrying
LLMResponse.to_dict(), linked by caused_by), so `LLMCache.from_events` can
rebuild the response cache for replay.

Replay is a pure checker: it never constructs a provider (structurally zero
live calls), re-renders every prompt from the registry, requires every hash
to hit the recorded cache, re-parses raw replies, recomputes actions/payoffs,
and compares against the stored rounds.
"""
from __future__ import annotations

import json
import time
from typing import Any, Optional

from activegraph import Event, Graph, Runtime
from activegraph.llm.cache import LLMCache
from activegraph.store import open_store

from engine import Engine, new_run_id, _public_rounds, _summarize
from strategies import STRATEGIES, CountingRng, get_action
from llm_subject import (
    InvalidTrialError,
    build_prompt,
    load_registry,
    make_provider,
    parse_action,
    render_prompt,
)

LLM_SLUG = "llm-subject"
PROVIDER_ATTEMPTS = 3  # transient-failure retries (network/rate-limit), not parse retries


def _validate_seats(strategy1_slug: str, strategy2_slug: str) -> None:
    if LLM_SLUG not in (strategy1_slug, strategy2_slug):
        raise ValueError("an LLM run needs at least one 'llm-subject' seat")
    for slug in (strategy1_slug, strategy2_slug):
        if slug != LLM_SLUG and slug not in STRATEGIES:
            raise ValueError(f"unknown strategy slug: {slug}")


def _complete_with_transient_retries(provider, prompt) -> Any:
    last: Optional[Exception] = None
    for attempt in range(PROVIDER_ATTEMPTS):
        try:
            return provider.complete(
                system=prompt.system,
                messages=prompt.messages,
                model=prompt.model,
                max_tokens=prompt.max_tokens,
                temperature=prompt.temperature,
                top_p=prompt.top_p,
                output_schema=None,
                timeout_seconds=60.0,
            )
        except Exception as e:  # provider/transport errors only reach here
            last = e
            if attempt < PROVIDER_ATTEMPTS - 1:
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"LLM provider failed after {PROVIDER_ATTEMPTS} attempts: {last}")


class _Counters:
    def __init__(self) -> None:
        self.llm_calls = 0
        self.retried_calls = 0
        self.input_tokens = 0
        self.output_tokens = 0


def _llm_decide_live(
    graph: Graph,
    provider,
    registry: dict,
    registry_sha: str,
    llm_cfg: dict,
    game_def: dict,
    seat: int,
    round_number: int,
    num_rounds: int,
    history: list[dict],
    counters: _Counters,
    seen_hashes: set[str],
) -> tuple[int, str, int]:
    """One live subject decision: ≤2 sampled calls (original + 1 parse retry)."""
    retry_raw: Optional[str] = None
    for attempt in (0, 1):
        system, user = render_prompt(
            registry,
            llm_cfg["promptId"],
            seat=seat,
            round_number=round_number,
            history=history,
            game_def=game_def,
            num_rounds=num_rounds,
            protocol=llm_cfg,
            retry_raw=retry_raw,
        )
        prompt = build_prompt(
            system,
            user,
            model=llm_cfg["model"],
            temperature=llm_cfg["temperature"],
            max_tokens=llm_cfg["maxTokens"],
        )
        ph = prompt.hash()
        if ph in seen_hashes:
            # Seat tags + round numbers make this impossible by construction;
            # if it ever fires, replay would cross-wire responses — abort.
            raise RuntimeError(f"prompt hash collision within run: {ph}")
        seen_hashes.add(ph)

        req_id = graph.ids.event()
        graph.emit(
            Event(
                id=req_id,
                type="llm.requested",
                payload={
                    "prompt_hash": ph,
                    "system": system,
                    "user": user,
                    "model": llm_cfg["model"],
                    "temperature": llm_cfg["temperature"],
                    "maxTokens": llm_cfg["maxTokens"],
                    "promptId": llm_cfg["promptId"],
                    "registrySha256": registry_sha,
                    "seat": seat,
                    "roundNumber": round_number,
                    "attempt": attempt,
                },
                actor=LLM_SLUG,
            )
        )
        response = _complete_with_transient_retries(provider, prompt)
        counters.llm_calls += 1
        counters.input_tokens += int(response.input_tokens or 0)
        counters.output_tokens += int(response.output_tokens or 0)
        if attempt == 1:
            counters.retried_calls += 1
        graph.emit(
            Event(
                id=graph.ids.event(),
                type="llm.responded",
                payload={
                    **response.to_dict(),
                    "seat": seat,
                    "roundNumber": round_number,
                    "attempt": attempt,
                },
                actor=LLM_SLUG,
                caused_by=req_id,
            )
        )
        action = parse_action(registry, llm_cfg["promptId"], response.raw_text)
        if action is not None:
            return action, response.raw_text, attempt
        retry_raw = response.raw_text

    graph.emit(
        Event(
            id=graph.ids.event(),
            type="trial.invalidated",
            payload={
                "seat": seat,
                "roundNumber": round_number,
                "rawText": (retry_raw or "")[:500],
                "reason": "reply unparseable after 1 retry",
            },
            actor="engine",
        )
    )
    raise InvalidTrialError(seat, round_number, retry_raw or "")


def run_llm(
    engine: Engine,
    *,
    game_def: dict,
    strategy1_slug: str,
    strategy2_slug: str,
    num_rounds: int,
    seed: int,
    llm: dict,
) -> dict[str, Any]:
    """Execute one LLM behavioral run, event-sourcing every decision.

    Returns rounds + summary + meta. An unparseable subject reply does NOT
    raise out of the endpoint: it returns invalidTrial=True with zero rounds
    (HTTP 200) — the trial is excluded and replaced per pre-registration §0,
    and the spent calls stay on the record.
    """
    registry, registry_sha = load_registry()
    _validate_seats(strategy1_slug, strategy2_slug)
    if llm.get("promptId") not in registry["prompts"]:
        raise ValueError(f"unknown promptId: {llm.get('promptId')}")

    provider = make_provider()
    run_id = new_run_id()
    graph = Graph(run_id=run_id)
    rt = Runtime(graph, behaviors=[], persist_to=engine.url)

    llm_stored = {**llm, "registrySha256": registry_sha}
    graph.add_object(
        "game",
        {
            "gameDef": game_def,
            "strategy1Slug": strategy1_slug,
            "strategy2Slug": strategy2_slug,
            "numRounds": num_rounds,
            "seed": seed,
            "llm": llm_stored,
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
                    action, raw, attempt = _llm_decide_live(
                        graph,
                        provider,
                        registry,
                        registry_sha,
                        llm_stored,
                        game_def,
                        player_num,
                        n,
                        num_rounds,
                        history,
                        counters,
                        seen_hashes,
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
                "player1Action": actions[1],
                "player2Action": actions[2],
                "player1Payoff": p1_payoff,
                "player2Payoff": p2_payoff,
                "player1Reasoning": reasonings[1],
                "player2Reasoning": reasonings[2],
                "isNashOutcome": (actions[1], actions[2]) in nash_set,
                "rngCalls": rng.calls,
            }
            consumed += rng.calls
            graph.add_object("round", round_data, actor="engine")
            graph.emit(
                Event(
                    id=graph.ids.event(),
                    type="round.played",
                    payload={
                        **round_data,
                        "strategy1Slug": strategy1_slug,
                        "strategy2Slug": strategy2_slug,
                    },
                    actor="engine",
                )
            )
            history.append(
                {
                    "p1Action": actions[1],
                    "p2Action": actions[2],
                    "p1Payoff": p1_payoff,
                    "p2Payoff": p2_payoff,
                }
            )
            rounds.append(round_data)

        graph.emit(
            Event(
                id=graph.ids.event(),
                type="run.completed",
                payload={
                    "numRounds": num_rounds,
                    "player1TotalPayoff": sum(r["player1Payoff"] for r in rounds),
                    "player2TotalPayoff": sum(r["player2Payoff"] for r in rounds),
                },
                actor="engine",
            )
        )
    except InvalidTrialError:
        invalid = True
    except Exception as e:
        # Provider/infra failure mid-run. Events for calls already made are
        # persisted by the finally below; surface a STRUCTURED error so the
        # API layer can persist the partial spend — burned provider calls
        # must never become invisible to budget accounting.
        raise RuntimeError(
            json.dumps(
                {
                    "error": f"{type(e).__name__}: {e}",
                    "engineRunId": run_id,
                    "llmCalls": counters.llm_calls,
                    "inputTokens": counters.input_tokens,
                    "outputTokens": counters.output_tokens,
                    "partial": True,
                }
            )
        ) from e
    finally:
        # Persist in every exit path: completed runs, invalid trials (the
        # trial.invalidated event + spent calls are evidence), and provider
        # failures (spent calls stay auditable even though the run errors).
        rt.save_state()

    meta = {
        "llmCalls": counters.llm_calls,
        "retriedCalls": counters.retried_calls,
        "inputTokens": counters.input_tokens,
        "outputTokens": counters.output_tokens,
        "model": llm["model"],
        "temperature": llm["temperature"],
        "maxTokens": llm["maxTokens"],
        "promptId": llm["promptId"],
        "promptRegistrySha256": registry_sha,
    }
    if invalid:
        return {
            "engineRunId": run_id,
            "seed": seed,
            "invalidTrial": True,
            "rounds": [],
            "meta": meta,
        }
    return {
        "engineRunId": run_id,
        "seed": seed,
        "invalidTrial": False,
        "rounds": _public_rounds(rounds),
        **_summarize(rounds, game_def),
        "meta": meta,
    }


def replay_llm(engine: Engine, run_id: str) -> dict[str, Any]:
    """Pure replay verification of a recorded LLM run.

    No provider is constructed — zero live calls is structural, not a flag.
    Re-renders every prompt from the current registry, requires cache hits
    for every hash, re-parses replies, recomputes payoffs, and compares to
    the stored rounds.
    """
    Engine._check_run_id(run_id)
    registry, registry_sha = load_registry()

    store = open_store(engine.url, run_id=run_id)
    events = list(store.iter_events())
    if not events:
        raise KeyError(f"engine run not found: {run_id}")

    rt = Runtime.load(engine.url, run_id=run_id)
    graph = rt.graph
    game_obj = next(iter(graph.objects("game")), None)
    if game_obj is None:
        raise ValueError("run has no game object")
    g = game_obj.data
    llm_cfg = g.get("llm")
    if not llm_cfg:
        raise ValueError("not an LLM run (no llm config on game object)")

    mismatches: list[str] = []
    if llm_cfg.get("registrySha256") != registry_sha:
        mismatches.append(
            f"prompt registry drift: run recorded {llm_cfg.get('registrySha256')}, "
            f"current file is {registry_sha}"
        )

    invalidated = [e for e in events if e.type == "trial.invalidated"]
    requested = [e for e in events if e.type == "llm.requested"]
    cache = LLMCache.from_events(events)

    if invalidated:
        # Aborted trial: no rounds to re-derive. The recorded events remain
        # the audit trail; replay just reports the state.
        return {
            "engineRunId": run_id,
            "ok": len(mismatches) == 0,
            "invalidTrial": True,
            "recordedLlmCalls": len(requested),
            "llmCallsVerified": 0,
            "roundsCompared": 0,
            "liveCalls": 0,
            "promptRegistrySha256": registry_sha,
            "mismatches": mismatches,
        }

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
                        registry,
                        llm_cfg["promptId"],
                        seat=player_num,
                        round_number=n,
                        history=history,
                        game_def=game_def,
                        num_rounds=num_rounds,
                        protocol=llm_cfg,
                        retry_raw=retry_raw,
                    )
                    prompt = build_prompt(
                        system,
                        user,
                        model=llm_cfg["model"],
                        temperature=llm_cfg["temperature"],
                        max_tokens=llm_cfg["maxTokens"],
                    )
                    ph = prompt.hash()
                    resp = cache.get(ph)
                    rebuilt_calls += 1
                    if resp is None:
                        mismatches.append(
                            f"round {n} seat {player_num} attempt {attempt}: "
                            f"rebuilt prompt hash {ph[:16]}… not in recorded cache"
                        )
                        break
                    verified += 1
                    action = parse_action(registry, llm_cfg["promptId"], resp.raw_text)
                    if action is not None:
                        break
                    retry_raw = resp.raw_text
                if action is None:
                    mismatches.append(
                        f"round {n} seat {player_num}: recorded replies unparseable in replay"
                    )
                    break
                actions[player_num] = action
            else:
                action, _reasoning = get_action(slug, history, player_num, game_def, rng)
                actions[player_num] = action
        if len(actions) != 2:
            break

        stored = stored_rounds[n - 1]
        if rng.calls != stored.get("rngCalls", 0):
            mismatches.append(
                f"round {n}: rng draws {rng.calls} != stored {stored.get('rngCalls', 0)}"
            )
        p1_payoff, p2_payoff = game_def["payoffMatrix"][actions[1]][actions[2]]
        if (
            actions[1] != stored["player1Action"]
            or actions[2] != stored["player2Action"]
        ):
            mismatches.append(
                f"round {n}: replayed actions ({actions[1]},{actions[2]}) != "
                f"stored ({stored['player1Action']},{stored['player2Action']})"
            )
        elif (
            p1_payoff != stored["player1Payoff"]
            or p2_payoff != stored["player2Payoff"]
        ):
            mismatches.append(
                f"round {n}: replayed payoffs ({p1_payoff},{p2_payoff}) != "
                f"stored ({stored['player1Payoff']},{stored['player2Payoff']})"
            )
        consumed += rng.calls
        history.append(
            {
                "p1Action": stored["player1Action"],
                "p2Action": stored["player2Action"],
                "p1Payoff": stored["player1Payoff"],
                "p2Payoff": stored["player2Payoff"],
            }
        )

    if not mismatches and rebuilt_calls != len(requested):
        mismatches.append(
            f"recorded llm.requested events ({len(requested)}) != rebuilt prompts ({rebuilt_calls})"
        )

    return {
        "engineRunId": run_id,
        "ok": len(mismatches) == 0,
        "invalidTrial": False,
        "recordedLlmCalls": len(requested),
        "llmCallsVerified": verified,
        "roundsCompared": len(stored_rounds),
        "liveCalls": 0,
        "promptRegistrySha256": registry_sha,
        "mismatches": mismatches[:20],
    }
