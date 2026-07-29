"""ActiveGraph-backed game simulation engine.

A run models one experiment execution:
- a `game` object on the graph holds the game definition, both strategy
  slugs, the round count, and the RNG seed;
- each round lands as a `round` object plus a custom `round.played` event
  in the append-only log;
- the `round_player` behavior reacts to `round.requested` events, computes
  both players' actions deterministically (seeded mulberry32 stream, p1
  then p2), and schedules the next round.

Determinism contract: the behavior body is a pure function of the graph
state. The RNG stream position is reconstructed from the per-round
`rngCalls` counters stored on round objects, so replaying or forking a run
reproduces the exact same stream without any hidden state.
"""
from __future__ import annotations

import os
import re
import time
import uuid
from typing import Any, Optional

from activegraph import Graph, Runtime, behavior
from activegraph import Event
from activegraph.store.sqlite import SQLiteEventStore
from activegraph.store import open_store

from strategies import CountingRng, get_action

RUN_ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,80}$")


def new_run_id() -> str:
    return f"run_{int(time.time())}_{uuid.uuid4().hex[:8]}"


def _rounds_from_graph(graph: Graph) -> list[dict[str, Any]]:
    rounds = [o.data for o in graph.objects("round")]
    rounds.sort(key=lambda r: r["roundNumber"])
    return rounds


def _seat_action(g: dict, player_num: int, n: int, history, game_def: dict, rng):
    """Resolve one seat's action for round n.

    The special slug "scripted" reads the move from an externally supplied
    list stored on the game object (`scripted1`/`scripted2`) — used for
    event-sourcing LLM decisions. Everything else goes through the normal
    deterministic strategy table. Scripted seats consume no RNG draws.
    """
    slug = g["strategy1Slug"] if player_num == 1 else g["strategy2Slug"]
    if slug == "scripted":
        script = g.get("scripted1" if player_num == 1 else "scripted2") or []
        # These are client-supplied (via the Express layer); a bad script is a
        # 400-class error, so raise ValueError (mapped to 400) not RuntimeError.
        if len(script) < n:
            raise ValueError(
                f"scripted seat p{player_num} has no move for round {n} "
                f"(script covers {len(script)} rounds)"
            )
        entry = script[n - 1]
        action = int(entry["action"])
        if not 0 <= action < game_def["numActions"]:
            raise ValueError(
                f"scripted seat p{player_num} action {action} out of range at round {n}"
            )
        reasoning = entry.get("reasoning") or f"External scripted decision: action {action}."
        return action, reasoning
    return get_action(slug, history, player_num, game_def, rng)


def _make_round_player():
    @behavior(name="round_player", on=["round.requested"])
    def round_player(event, graph, ctx):
        game_obj = next(iter(ctx.view.objects("game")), None)
        if game_obj is None:
            return
        g = game_obj.data
        game_def = g["gameDef"]
        n = event.payload["roundNumber"]
        num_rounds = g["numRounds"]

        prior = sorted((o.data for o in ctx.view.objects("round")), key=lambda r: r["roundNumber"])
        prior = [r for r in prior if r["roundNumber"] < n]
        history = [
            {
                "p1Action": r["player1Action"],
                "p2Action": r["player2Action"],
                "p1Payoff": r["player1Payoff"],
                "p2Payoff": r["player2Payoff"],
            }
            for r in prior
        ]
        consumed = sum(r.get("rngCalls", 0) for r in prior)
        rng = CountingRng(g["seed"], advance=consumed)

        p1_action, p1_reasoning = _seat_action(g, 1, n, history, game_def, rng)
        p2_action, p2_reasoning = _seat_action(g, 2, n, history, game_def, rng)

        p1_payoff, p2_payoff = game_def["payoffMatrix"][p1_action][p2_action]
        nash_set = {tuple(ne) for ne in game_def["nashEquilibria"]}
        is_nash = (p1_action, p2_action) in nash_set

        round_data = {
            "roundNumber": n,
            "player1Action": p1_action,
            "player2Action": p2_action,
            "player1Payoff": p1_payoff,
            "player2Payoff": p2_payoff,
            "player1Reasoning": p1_reasoning,
            "player2Reasoning": p2_reasoning,
            "isNashOutcome": is_nash,
            "rngCalls": rng.calls,
        }
        graph.add_object("round", round_data)
        graph.emit(
            "round.played",
            {
                **round_data,
                "strategy1Slug": g["strategy1Slug"],
                "strategy2Slug": g["strategy2Slug"],
            },
        )
        if n < num_rounds:
            graph.emit("round.requested", {"roundNumber": n + 1})
        else:
            rounds = prior + [round_data]
            p1_total = sum(r["player1Payoff"] for r in rounds)
            p2_total = sum(r["player2Payoff"] for r in rounds)
            graph.emit(
                "run.completed",
                {
                    "numRounds": num_rounds,
                    "player1TotalPayoff": p1_total,
                    "player2TotalPayoff": p2_total,
                },
            )

    return round_player


def _summarize(rounds: list[dict[str, Any]], game_def: dict) -> dict[str, Any]:
    n = len(rounds)
    p1_total = sum(r["player1Payoff"] for r in rounds)
    p2_total = sum(r["player2Payoff"] for r in rounds)
    coop = sum(1 for r in rounds if r["player1Action"] == 0 and r["player2Action"] == 0)
    nash_p1 = nash_p2 = 0.0
    if game_def["nashEquilibria"]:
        ne = game_def["nashEquilibria"][0]
        nash_p1, nash_p2 = game_def["payoffMatrix"][ne[0]][ne[1]]
    nash_dev = 0.0
    if n:
        nash_dev = (abs(p1_total / n - nash_p1) + abs(p2_total / n - nash_p2)) / 2
    return {
        "player1TotalPayoff": p1_total,
        "player2TotalPayoff": p2_total,
        "cooperationRate": (coop / n) if n else 0.0,
        "nashDeviationScore": nash_dev,
    }


def _public_rounds(rounds: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [{k: v for k, v in r.items() if k != "rngCalls"} for r in rounds]


class Engine:
    """Owns the SQLite event store and executes runs, forks, diffs, traces."""

    def __init__(self, db_path: str):
        parent = os.path.dirname(os.path.abspath(db_path))
        os.makedirs(parent, exist_ok=True)
        self.db_path = db_path
        self.url = f"sqlite:///{db_path}"

    # ── run ────────────────────────────────────────────────────────────────
    def run(
        self,
        *,
        game_def: dict,
        strategy1_slug: str,
        strategy2_slug: str,
        num_rounds: int,
        seed: int,
        scripted1: Optional[list[dict]] = None,
        scripted2: Optional[list[dict]] = None,
    ) -> dict[str, Any]:
        for slug, script, name in (
            (strategy1_slug, scripted1, "scripted1"),
            (strategy2_slug, scripted2, "scripted2"),
        ):
            if slug == "scripted" and (not script or len(script) != num_rounds):
                raise ValueError(
                    f"{name} must supply exactly {num_rounds} moves for a scripted seat"
                )
            if slug != "scripted" and script:
                raise ValueError(f"{name} provided but that seat plays '{slug}', not 'scripted'")

        run_id = new_run_id()
        graph = Graph(run_id=run_id)
        rt = Runtime(graph, behaviors=[_make_round_player()], persist_to=self.url)
        game_data: dict[str, Any] = {
            "gameDef": game_def,
            "strategy1Slug": strategy1_slug,
            "strategy2Slug": strategy2_slug,
            "numRounds": num_rounds,
            "seed": seed,
        }
        if scripted1 is not None:
            game_data["scripted1"] = scripted1
        if scripted2 is not None:
            game_data["scripted2"] = scripted2
        graph.add_object("game", game_data, actor="engine")
        graph.emit(
            Event(
                id=graph.ids.event(),
                type="round.requested",
                payload={"roundNumber": 1},
                actor="engine",
            )
        )
        rt.run_until_idle()
        rt.save_state()

        rounds = _rounds_from_graph(graph)
        if len(rounds) != num_rounds:
            raise RuntimeError(
                f"engine produced {len(rounds)} rounds, expected {num_rounds}"
            )
        return {
            "engineRunId": run_id,
            "seed": seed,
            "rounds": _public_rounds(rounds),
            **_summarize(rounds, game_def),
        }

    # ── fork ───────────────────────────────────────────────────────────────
    def fork(
        self,
        *,
        parent_run_id: str,
        fork_round: int,
        strategy1_slug: Optional[str] = None,
        strategy2_slug: Optional[str] = None,
        scripted1: Optional[list[dict]] = None,
        scripted2: Optional[list[dict]] = None,
    ) -> dict[str, Any]:
        self._check_run_id(parent_run_id)
        parent_store = open_store(self.url, run_id=parent_run_id)
        cutoff_id = None
        parent_events = list(parent_store.iter_events())
        if not parent_events:
            raise KeyError(f"engine run not found: {parent_run_id}")
        for e in parent_events:
            if e.type == "round.played" and e.payload.get("roundNumber") == fork_round:
                cutoff_id = e.id
                break
        if cutoff_id is None:
            raise ValueError(f"parent run has no round {fork_round}")

        fork_run_id = new_run_id()
        SQLiteEventStore.fork_run(
            self.db_path,
            parent_run_id=parent_run_id,
            new_run_id=fork_run_id,
            at_event_id=cutoff_id,
            label=f"fork@round{fork_round}",
            created_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        )

        rt = Runtime.load(self.url, run_id=fork_run_id, behaviors=[_make_round_player()])
        graph = rt.graph
        game_obj = next(iter(graph.objects("game")), None)
        if game_obj is None:
            raise RuntimeError("fork replay produced no game object")

        patch: dict[str, Any] = {}
        if strategy1_slug and strategy1_slug != game_obj.data["strategy1Slug"]:
            patch["strategy1Slug"] = strategy1_slug
        if strategy2_slug and strategy2_slug != game_obj.data["strategy2Slug"]:
            patch["strategy2Slug"] = strategy2_slug
        if scripted1 is not None:
            patch["scripted1"] = scripted1
        if scripted2 is not None:
            patch["scripted2"] = scripted2
        if patch:
            graph.patch_object(game_obj.id, patch, actor="engine")

        game_def = game_obj.data["gameDef"]
        num_rounds = game_obj.data["numRounds"]
        merged = {**game_obj.data, **patch}
        for player_num, key in ((1, "scripted1"), (2, "scripted2")):
            slug = merged["strategy1Slug"] if player_num == 1 else merged["strategy2Slug"]
            # Mirror run()'s validation: a scripted payload only belongs on a
            # scripted seat, and a scripted seat must be fully covered.
            if slug != "scripted" and patch.get(key):
                raise ValueError(
                    f"{key} provided but fork seat p{player_num} plays '{slug}', not 'scripted'"
                )
            if slug == "scripted" and len(merged.get(key) or []) < num_rounds:
                raise ValueError(
                    f"fork leaves seat p{player_num} scripted but {key} covers fewer than "
                    f"{num_rounds} rounds"
                )
        if fork_round < num_rounds:
            graph.emit(
                Event(
                    id=graph.ids.event(),
                    type="round.requested",
                    payload={"roundNumber": fork_round + 1},
                    actor="engine",
                )
            )
            rt.run_until_idle()
        rt.save_state()

        rounds = _rounds_from_graph(graph)
        if len(rounds) != num_rounds:
            raise RuntimeError(
                f"fork produced {len(rounds)} rounds, expected {num_rounds}"
            )
        return {
            "engineRunId": fork_run_id,
            "parentEngineRunId": parent_run_id,
            "forkRound": fork_round,
            "seed": game_obj.data["seed"],
            "rounds": _public_rounds(rounds),
            **_summarize(rounds, game_def),
        }

    # ── diff ───────────────────────────────────────────────────────────────
    def diff(self, parent_run_id: str, fork_run_id: str) -> dict[str, Any]:
        self._check_run_id(parent_run_id)
        self._check_run_id(fork_run_id)
        parent_rt = Runtime.load(self.url, run_id=parent_run_id)
        fork_rt = Runtime.load(self.url, run_id=fork_run_id)
        d = parent_rt.diff(fork_rt)

        parent_rounds = _rounds_from_graph(parent_rt.graph)
        fork_rounds = _rounds_from_graph(fork_rt.graph)
        divergence_round = None
        for pr, fr in zip(parent_rounds, fork_rounds):
            if (
                pr["player1Action"] != fr["player1Action"]
                or pr["player2Action"] != fr["player2Action"]
            ):
                divergence_round = pr["roundNumber"]
                break

        game_def = next(iter(parent_rt.graph.objects("game"))).data["gameDef"]
        fork_game_def = next(iter(fork_rt.graph.objects("game"))).data["gameDef"]
        return {
            "parentEngineRunId": parent_run_id,
            "forkEngineRunId": fork_run_id,
            "sharedEvents": len(d.shared_events),
            "parentOnlyEvents": len(d.parent_only_events),
            "forkOnlyEvents": len(d.fork_only_events),
            "divergentObjects": len(d.divergent_objects),
            "divergentRelations": len(d.divergent_relations),
            "isIdentical": d.is_identical,
            "divergenceRound": divergence_round,
            "parentRounds": _public_rounds(parent_rounds),
            "forkRounds": _public_rounds(fork_rounds),
            "parentSummary": _summarize(parent_rounds, game_def),
            "forkSummary": _summarize(fork_rounds, fork_game_def),
        }

    # ── trace ──────────────────────────────────────────────────────────────
    def trace(self, run_id: str) -> dict[str, Any]:
        self._check_run_id(run_id)
        store = open_store(self.url, run_id=run_id)
        events = list(store.iter_events())
        if not events:
            raise KeyError(f"engine run not found: {run_id}")
        out = []
        for e in events:
            out.append(
                {
                    "eventId": e.id,
                    "type": e.type,
                    "actor": e.actor,
                    "causedBy": e.caused_by,
                    "timestamp": e.timestamp,
                    "roundNumber": (
                        e.payload.get("roundNumber")
                        if isinstance(e.payload, dict)
                        else None
                    ),
                    "payload": e.payload if isinstance(e.payload, dict) else {},
                }
            )
        return {"engineRunId": run_id, "events": out}

    @staticmethod
    def _check_run_id(run_id: str) -> None:
        if not RUN_ID_RE.match(run_id):
            raise ValueError(f"invalid run id: {run_id}")
