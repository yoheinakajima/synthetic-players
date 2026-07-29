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


def _pattern_tracker(history, player_num, game, rng):
    """First-order conditional-frequency tracker (Phase 3, pre-registered).

    Deterministic, zero RNG draws. Mirrors the metrics.ts conditional-
    exploitability tracker exactly: Laplace alpha=1 transition counts over the
    opponent's action pairs, 10-round burn-in, first-index argmax best
    response against the predicted distribution.

    Rounds 1..10 (burn-in): deterministic cycle (n-1) % numActions.
    Round n >= 11: predict opponent's next action from their lag-1 transition
    row (strictly prior rounds only), best-respond via expected payoff.
    """
    n_actions = game["numActions"]
    n = len(history) + 1  # current round number, 1-based
    if n <= 10:
        action = (n - 1) % n_actions
        return action, f"Burn-in round {n}: cycling action {action}."

    opp_actions = [
        (r["p2Action"] if player_num == 1 else r["p1Action"]) for r in history
    ]
    # Laplace alpha=1 over lag-1 transitions from strictly prior rounds.
    counts = [[1] * n_actions for _ in range(n_actions)]
    for i in range(len(opp_actions) - 1):
        counts[opp_actions[i]][opp_actions[i + 1]] += 1
    row = counts[opp_actions[-1]]
    total = sum(row)
    dist = [c / total for c in row]

    matrix = game["payoffMatrix"]
    best_action = 0
    best_ev = None
    for a in range(n_actions):
        ev = 0.0
        for o in range(n_actions):
            payoff = matrix[a][o][0] if player_num == 1 else matrix[o][a][1]
            ev += dist[o] * payoff
        if best_ev is None or ev > best_ev:  # strict > keeps first-index argmax
            best_ev = ev
            best_action = a
    return best_action, (
        f"Tracker: opp last {opp_actions[-1]}, row counts {row}; "
        f"best response {best_action} (EV {_fmt(best_ev)})."
    )


# --- Family F opponents (Phase 4, F-SPEC-1 registered completion) ----------
# Registered in docs/phase4/f-opponent-specs.md (signed 2026-07-28); fixtures
# §8 are asserted verbatim in selftest_phase4.py. All are pure functions of
# (history, player_num, game, rng) — no hidden state, recomputed per decision.


def _subject_actions(history: list[RoundHistory], player_num: int) -> list[int]:
    """Counterpart (subject) actions, read exactly as the sealed first-order
    tracker reads them (F-SPEC-1 §2)."""
    return [(r["p2Action"] if player_num == 1 else r["p1Action"]) for r in history]


def _ev_best_response(dist: list[float], player_num: int, game: dict) -> tuple[int, float]:
    """Strict-> first-index EV argmax over the game matrix — the sealed
    best-response scan (F-SPEC-1 §2; parity with _pattern_tracker's loop)."""
    n_actions = game["numActions"]
    matrix = game["payoffMatrix"]
    best_action = 0
    best_ev = None
    for a in range(n_actions):
        ev = 0.0
        for o in range(n_actions):
            payoff = matrix[a][o][0] if player_num == 1 else matrix[o][a][1]
            ev += dist[o] * payoff
        if best_ev is None or ev > best_ev:  # strict > keeps first-index argmax
            best_ev = ev
            best_action = a
    return best_action, best_ev


def _ngram_tracker(history, player_num, game, rng, k: int):
    """Order-k conditional-frequency tracker (F-SPEC-1 §4): the sealed
    first-order recipe with context length k. Zero RNG draws."""
    n_actions = game["numActions"]
    n = len(history) + 1
    if n <= 10:
        action = (n - 1) % n_actions
        return action, f"Burn-in round {n}: cycling action {action}."

    a = _subject_actions(history, player_num)
    m = len(a)
    counts: dict[tuple, list[int]] = {}
    for i in range(m - k):  # every complete window in the strictly-prior prefix
        ctx = tuple(a[i:i + k])
        row = counts.get(ctx)
        if row is None:
            row = [1] * n_actions  # Laplace alpha=1 prior
            counts[ctx] = row
        row[a[i + k]] += 1
    ctx = tuple(a[m - k:])
    row = counts.get(ctx, [1] * n_actions)  # unseen context -> uniform row
    total = sum(row)
    dist = [c / total for c in row]
    best_action, best_ev = _ev_best_response(dist, player_num, game)
    return best_action, (
        f"ngram{k}: context {ctx}, row counts {row}; "
        f"best response {best_action} (EV {_fmt(best_ev)})."
    )


def _ngram2(history, player_num, game, rng):
    return _ngram_tracker(history, player_num, game, rng, 2)


def _ngram3(history, player_num, game, rng):
    return _ngram_tracker(history, player_num, game, rng, 3)


def _wsls_targeter(history, player_num, game, rng):
    """WSLS-model targeter (F-SPEC-1 §5, frozen in predicates §F): predict the
    subject via win-stay/lose-shift on its payoff sign, play the beater of the
    prediction. Round 1: uniform draw (exactly 1 draw); thereafter 0 draws."""
    n_actions = game["numActions"]
    if not history:
        action = int(rng() * n_actions)
        return action, f"Round 1: uniform seeded draw -> action {action}."
    last = history[-1]
    subj_action = last["p2Action"] if player_num == 1 else last["p1Action"]
    subj_payoff = last["p2Payoff"] if player_num == 1 else last["p1Payoff"]
    if subj_payoff >= 0:  # win or tie -> predict repeat
        pred = subj_action
        why = "win" if subj_payoff > 0 else "tie"
    else:  # loss -> predict cyclic shift (sealed convention)
        pred = (subj_action + 1) % n_actions
        why = "loss"
    action = (pred + 1) % n_actions  # beater of the prediction
    return action, (
        f"WSLS-targeter: subject last action {subj_action} ({why}) -> "
        f"predict {pred}; playing beater {action}."
    )


def _switcher_r26(history, player_num, game, rng):
    """Mid-episode regime switcher (F-SPEC-1 §6, Order A signed 2026-07-28):
    fo-tracker rounds 1-25, wsls-targeter rounds 26-50. Round 26 is regime B's
    first decision; no reset — each regime is its registered pure function on
    the full causal history with the true round number."""
    n = len(history) + 1
    if n < 26:
        action, reasoning = _pattern_tracker(history, player_num, game, rng)
        return action, f"[regime A: fo-tracker] {reasoning}"
    action, reasoning = _wsls_targeter(history, player_num, game, rng)
    return action, f"[regime B: wsls-targeter] {reasoning}"


def _shuffled_history(history, player_num, game, rng):
    """Shuffled-history control (F-SPEC-1 §7): first-order tracker on a
    per-decision Fisher-Yates shuffle of the causal subject prefix. Burn-in
    rounds 1-10 draw nothing; round n>=11 draws exactly m-1 = n-2 times.
    The permutation and the exact shuffled prefix are archived in the round
    record via the reasoning string (round records are sealed per decision)."""
    n_actions = game["numActions"]
    n = len(history) + 1
    if n <= 10:
        action = (n - 1) % n_actions
        return action, f"Burn-in round {n}: cycling action {action}."

    a = _subject_actions(history, player_num)
    m = len(a)
    idx = list(range(m))
    for i in range(m - 1):  # canonical Fisher-Yates/Durstenfeld, m-1 draws
        u = rng()
        j = i + int(u * (m - i))
        idx[i], idx[j] = idx[j], idx[i]
    b = [a[idx[i]] for i in range(m)]
    counts = [[1] * n_actions for _ in range(n_actions)]  # Laplace alpha=1
    for i in range(m - 1):
        counts[b[i]][b[i + 1]] += 1
    row = counts[b[-1]]
    total = sum(row)
    dist = [c / total for c in row]
    best_action, best_ev = _ev_best_response(dist, player_num, game)
    return best_action, (
        f"Shuffled-history: perm={idx} shuffled={b} anchor {b[-1]}, "
        f"row counts {row}; best response {best_action} (EV {_fmt(best_ev)})."
    )


STRATEGIES = {
    "always-cooperate": _always_cooperate,
    "always-defect": _always_defect,
    "tit-for-tat": _tit_for_tat,
    "grim-trigger": _grim_trigger,
    "random": _random,
    "win-stay-lose-shift": _win_stay_lose_shift,
    "nash-mixed": _nash_mixed,
    "generous-tit-for-tat": _generous_tit_for_tat,
    "pattern-tracker": _pattern_tracker,
    # Family F (F-SPEC-1, registered 2026-07-28):
    "fo-tracker": _pattern_tracker,  # disclosed registry alias, byte-identical (§3)
    "ngram2": _ngram2,
    "ngram3": _ngram3,
    "wsls-targeter": _wsls_targeter,
    "switcher-r26": _switcher_r26,
    "shuffled-history": _shuffled_history,
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
    fn = STRATEGIES.get(strategy_slug)
    if fn is None:
        # Never fall back silently (e.g. to random): an unknown slug playing
        # fabricated moves would corrupt the scientific record.
        raise ValueError(f"unknown strategy slug: {strategy_slug}")
    return fn(history, player_num, game, rng)
