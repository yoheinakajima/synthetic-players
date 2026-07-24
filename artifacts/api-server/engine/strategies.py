"""Strategy implementations, ported 1:1 from the former TypeScript game engine.

Parity contract: for the same (game, strategies, numRounds, seed) inputs these
functions must reproduce the TS engine's action sequences byte-for-byte,
including RNG consumption order (p1 then p2, each round).
"""
from __future__ import annotations

from typing import Callable, TypedDict

MASK = 0xFFFFFFFF


def _imul(a: int, b: int) -> int:
    """32-bit integer multiply matching JS Math.imul (bit pattern)."""
    return (a * b) & MASK


def mulberry32(seed: int) -> Callable[[], float]:
    """Bit-identical port of the TS mulberry32 PRNG."""
    a = seed & MASK

    def rng() -> float:
        nonlocal a
        a = (a + 0x6D2B79F5) & MASK
        t = _imul(a ^ (a >> 15), (1 | a) & MASK)
        t = ((t + _imul(t ^ (t >> 7), (61 | t) & MASK)) & MASK) ^ t
        t &= MASK
        return ((t ^ (t >> 14)) & MASK) / 4294967296

    return rng


class RoundHistory(TypedDict):
    p1Action: int
    p2Action: int
    p1Payoff: float
    p2Payoff: float


def _opp_last(history: list[RoundHistory], player_num: int) -> int:
    last = history[-1]
    return last["p2Action"] if player_num == 1 else last["p1Action"]


def _always_cooperate(history, player_num, game, rng):
    return 0, "Always play action 0 (cooperate/low/first option)."


def _always_defect(history, player_num, game, rng):
    return game["numActions"] - 1, "Always play the last action (defect/high/last option)."


def _tit_for_tat(history, player_num, game, rng):
    if not history:
        return 0, "First round: cooperate."
    opp = _opp_last(history, player_num)
    return opp, f"Mirror opponent's last action: {opp}."


def _grim_trigger(history, player_num, game, rng):
    defect = game["numActions"] - 1
    ever_defected = any(
        (r["p2Action"] if player_num == 1 else r["p1Action"]) == defect for r in history
    )
    if ever_defected:
        return defect, "Opponent defected previously; permanently defecting."
    return 0, "Opponent has always cooperated; cooperating."


def _random(history, player_num, game, rng):
    action = int(rng() * game["numActions"])
    return action, f"Randomly selected action {action}."


def _fmt(x: float) -> str:
    """Match JS Number.toFixed(2): round the exact binary value to the
    nearest hundredth, ties toward +infinity (the 'larger n' rule)."""
    from decimal import Decimal
    import math

    d = Decimal(x) * 100
    floor = math.floor(d)
    n = floor + (1 if d - floor >= Decimal("0.5") else 0)
    return f"{n / 100:.2f}"


def _win_stay_lose_shift(history, player_num, game, rng):
    if not history:
        return 0, "First round: start cooperating."
    last = history[-1]
    my_action = last["p1Action"] if player_num == 1 else last["p2Action"]
    my_payoff = last["p1Payoff"] if player_num == 1 else last["p2Payoff"]
    avg = sum((r["p1Payoff"] if player_num == 1 else r["p2Payoff"]) for r in history) / len(history)
    if my_payoff >= avg:
        return my_action, (
            f"Won last round (payoff {_fmt(my_payoff)} >= avg {_fmt(avg)}); "
            f"staying with action {my_action}."
        )
    new_action = (my_action + 1) % game["numActions"]
    return new_action, (
        f"Lost last round (payoff {_fmt(my_payoff)} < avg {_fmt(avg)}); "
        f"shifting to action {new_action}."
    )


def _nash_mixed(history, player_num, game, rng):
    if game["nashEquilibria"]:
        ne = game["nashEquilibria"][int(rng() * len(game["nashEquilibria"]))]
        action = ne[0]
        return action, f"Playing action from Nash equilibrium: {action}."
    action = int(rng() * game["numActions"])
    return action, f"Nash mixed strategy: uniform random action {action}."


def _generous_tit_for_tat(history, player_num, game, rng):
    if not history:
        return 0, "First round: cooperate."
    opp = _opp_last(history, player_num)
    if opp == game["numActions"] - 1 and rng() < 0.1:
        return 0, "Opponent defected but forgiving with 10% probability."
    return opp, f"Mirror opponent: {opp}."


STRATEGIES = {
    "always-cooperate": _always_cooperate,
    "always-defect": _always_defect,
    "tit-for-tat": _tit_for_tat,
    "grim-trigger": _grim_trigger,
    "random": _random,
    "win-stay-lose-shift": _win_stay_lose_shift,
    "nash-mixed": _nash_mixed,
    "generous-tit-for-tat": _generous_tit_for_tat,
}


class CountingRng:
    """Wraps a mulberry32 stream and counts draws, so behaviors can record
    per-round RNG consumption in the event log (pure replay/fork support)."""

    def __init__(self, seed: int, advance: int = 0):
        self._rng = mulberry32(seed)
        for _ in range(advance):
            self._rng()
        self.calls = 0

    def __call__(self) -> float:
        self.calls += 1
        return self._rng()


def get_action(strategy_slug: str, history: list[RoundHistory], player_num: int, game: dict, rng):
    fn = STRATEGIES.get(strategy_slug, STRATEGIES["random"])
    return fn(history, player_num, game, rng)
