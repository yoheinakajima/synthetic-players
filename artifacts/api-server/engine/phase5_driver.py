"""Phase 5 dispatch driver — sealed-schedule executor (persona × temperature).

Same design contract as the sealed phase4_driver.py (byte-untouched):
- Requests are constructed from the sealed Phase 5 arms manifest + registry
  using the ENGINE'S OWN derivation functions — parity by construction.
- Repeated-block horizons use the registered Phase 3 rule geometric(δ) via
  mulberry32(seed ^ 0x54524D), cap 120; truncated draw EXCLUDES the
  supergame (zero calls, disclosed).
- Plan-file execution: engine/data/phase5-driver-plan.json
      {"actions": ["preflight", "dry-all", "entry-battery", "sentinel:0",
                   "block:P5A-rep", "sentinel:1", ..., "hold"]}
  State: engine/data/phase5-driver-state.json (atomic writes).
- STOP-ON-ANOMALY: any HTTP refusal, sentinel retry/invalid (alert rule
  (b)), evaluator attestation gate failure, engineCommit mismatch, dirty
  worktree, or ambiguous transport failure FREEZES the driver (exit 1).
  The AMBIGUOUS-transport freeze string is byte-identical to Phase 4's so
  the registered watchdog resume signature applies unchanged.
- Shedding is registered-transitions-only: when a cap projection binds the
  driver FREEZES with the arithmetic; the operator applies the registered
  shed order (freeze packet §7, whole arms, disclosed) — no discretionary
  mid-data call.
- Reconcile mode (`--reconcile`) rebuilds completion state from the engine
  event store (read-only); it never dispatches.

Run:  cd artifacts/api-server && uv run python engine/phase5_driver.py
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from phase4 import _pd_expected_matrix, _pure_nash  # noqa: E402
from phase5 import (  # noqa: E402
    ArmStoreP5,
    CAP_GROUPS_P5,
    GLOBAL_CAP_P5,
    SENTINEL_SEED_BASE_P5,
)
from llm_subject import load_registry  # noqa: E402
from strategies import mulberry32  # noqa: E402

ENGINE_URL = os.environ.get("P5_ENGINE_URL", "http://127.0.0.1:8090")
_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.normpath(os.path.join(_HERE, "..", "..", ".."))
SCHEDULE_PATH = os.path.join(REPO_ROOT, "docs", "phase5", "execution-schedule.json")
DATA_DIR = os.path.join(_HERE, "data")
PLAN_PATH = os.path.join(DATA_DIR, "phase5-driver-plan.json")
STATE_PATH = os.path.join(DATA_DIR, "phase5-driver-state.json")

# Sentinel cells (freeze packet §6): per model, persona-p01 fingerprint +
# bare fingerprint. Per check-k window (46001+k*10 … +9): p01 arms take the
# first 5 seeds, bare arms the last 5 — 4 arms × 5 episodes = 20 calls.
SENTINEL_ARMS = ["p5-sent-p01-gpt", "p5-sent-bare-gpt",
                 "p5-sent-p01-gem", "p5-sent-bare-gem"]
ENTRY_ARMS = ["p5-entry-gpt-t07", "p5-entry-gpt-t10", "p5-entry-gpt-t13",
              "p5-entry-gem-t07", "p5-entry-gem-t10", "p5-entry-gem-t13"]
LIVE_TIMEOUT_S = 900
ALL_BLOCKS = ["P5A-rep", "P5A-os", "P5B-rep", "P5B-os", "P5C-rep", "P5C-os"]


class DriverFreeze(Exception):
    """Any condition that must stop dispatch until a human looks."""


def draw_horizon(seed: int, delta_pct: int) -> tuple[int, bool]:
    rng = mulberry32((seed ^ 0x54524D) & 0xFFFFFFFF)
    delta = delta_pct / 100
    rounds = 1
    while rng() < delta:
        rounds += 1
        if rounds >= 120:
            return 120, True
    return rounds, False


def build_game_def(arm: dict, registry: dict) -> dict:
    spec = registry["prompts"].get(arm["templateId"])
    if spec is None:
        raise DriverFreeze(f"template {arm['templateId']} not in registry")
    options = spec["options"]
    matrix = _pd_expected_matrix(arm["bindings"])
    return {"slug": "phase5-pd", "numActions": len(options),
            "actionLabels": list(options), "payoffMatrix": matrix,
            "nashEquilibria": _pure_nash(matrix)}


def num_rounds_for(arm: dict, seed: int) -> tuple[int | None, bool]:
    block = arm["block"]
    if block.endswith("-os") or block in ("P5-sentinel", "P5-entry"):
        return 1, False
    if block.endswith("-rep"):
        rounds, truncated = draw_horizon(seed, int(arm["deltaPct"]))
        if truncated:
            return None, True
        return rounds, False
    raise DriverFreeze(f"no horizon rule for block {block}")


def run_body(arm: dict, registry: dict, *, seed: int, num_rounds: int,
             episode_index: int | None, sentinel_check_index: int | None,
             dry: bool) -> dict:
    body = {
        "armId": arm["armId"],
        "game": build_game_def(arm, registry),
        "strategy1Slug": "llm-subject",
        "strategy2Slug": "llm-subject",
        "numRounds": num_rounds,
        "seed": seed,
        "model": arm["model"],
        # R2: the client states the arm's pinned temperature explicitly;
        # the enforcement layer refuses any mismatch, and the runner
        # asserts the wire body echoes it before every dispatch.
        "temperature": float(arm["temperature"]),
        "maxTokens": 16,
        "dryRun": dry,
    }
    if episode_index is not None:
        body["episodeIndex"] = episode_index
    if sentinel_check_index is not None:
        body["sentinelCheckIndex"] = sentinel_check_index
    return body


def http_json(method: str, path: str, body: dict | None = None,
              timeout: int = LIVE_TIMEOUT_S) -> dict:
    req = urllib.request.Request(
        ENGINE_URL + path,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Content-Type": "application/json"}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:2000]
        raise DriverFreeze(f"HTTP {e.code} on {method} {path}: {detail}") from e
    except Exception as e:  # timeout / connection — AMBIGUOUS, never redispatch
        # NOTE: prefix string is byte-identical to phase4_driver.py — the
        # registered watchdog auto-resume signature keys on it.
        raise DriverFreeze(
            f"AMBIGUOUS transport failure on {method} {path}: {type(e).__name__}: {e} — "
            "run may have completed server-side; use --reconcile before resuming"
        ) from e


def load_json(path: str, default):
    if not os.path.exists(path):
        return default
    with open(path) as f:
        return json.load(f)


def save_state(state: dict) -> None:
    tmp = STATE_PATH + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=1)
    os.replace(tmp, STATE_PATH)


def freeze(state: dict, reason: str) -> None:
    state["frozen"] = {"reason": reason,
                       "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    save_state(state)
    print(f"\n*** DRIVER FROZEN ***\n{reason}", flush=True)
    raise SystemExit(1)


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", REPO_ROOT, *args],
                          capture_output=True, text=True, timeout=15).stdout.strip()


def assert_clean_tree(state: dict) -> str:
    dirty = git("status", "--porcelain")
    if dirty:
        freeze(state, f"worktree not clean at dispatch time:\n{dirty[:1500]}")
    head = git("rev-parse", "HEAD")
    if state.get("head") and state["head"] != head:
        freeze(state, f"HEAD moved since preflight ({state['head'][:12]} → {head[:12]}); "
                      "re-run preflight (new plan) after restarting the engine")
    return head


def check_engine_commit(state: dict, meta: dict) -> None:
    ec = meta.get("engineCommit") or {}
    if ec.get("sha") != state.get("head") or ec.get("dirty") is not False:
        freeze(state, f"engineCommit mismatch on first live run: stamped {ec}, "
                      f"expected {{'sha': {state.get('head')!r}, 'dirty': False}} — "
                      "restart the Engine workflow on a clean tree and reconcile")


def _sent_seeds(arm_id: str, k: int) -> list[int]:
    lo = SENTINEL_SEED_BASE_P5 + k * 10
    return list(range(lo, lo + 5)) if "-p01-" in arm_id else list(range(lo + 5, lo + 10))


# ── actions ──────────────────────────────────────────────────────────────────

def act_preflight(state: dict, store: ArmStoreP5, registry: dict, schedule: dict) -> None:
    status = http_json("GET", "/phase5/status", timeout=30)
    if not status.get("sealed") or not status["selfCheck"]["ok"]:
        freeze(state, f"engine not sealed/self-checked: {json.dumps(status)[:400]}")
    print("budget:", json.dumps(status["budget"]["byGroup"]), flush=True)

    head = assert_clean_tree(state)
    state["head"] = head
    save_state(state)
    print(f"HEAD {head} (clean)", flush=True)

    # Registered shed projection (freeze packet §7): remaining need per tier
    # vs the tier cap and the P5 global kill-switch. Binding ⇒ FREEZE.
    spent = status["budget"]["globalCalls"]
    need = 0
    for block in schedule["blocks"]:
        for e in block["episodes"]:
            key = f"{block['block']}|{e['armId']}|ep{e['ep']}"
            if key in state["runs"] or key in state.get("excluded", {}):
                continue
            nr, truncated = num_rounds_for(store.get(e["armId"]), e["seed"])
            if truncated:
                continue
            need += 2 * nr  # self-play: 2 subject calls per round
    print(f"shed projection: spent {spent} + remaining episode need {need} = "
          f"{spent + need} vs P5 global cap {GLOBAL_CAP_P5} "
          f"(caps {json.dumps(CAP_GROUPS_P5)})", flush=True)
    if spent + need > GLOBAL_CAP_P5:
        freeze(state, f"preflight projection binds: {spent} + {need} > {GLOBAL_CAP_P5} — "
                      "apply the registered shed order (freeze packet §7), whole arms "
                      "only, disclose in provenance, then resume")

    first = schedule["blocks"][0]["episodes"][0]
    arm = store.get(first["armId"])
    nr, _ = num_rounds_for(arm, first["seed"])
    dry = http_json("POST", "/phase5/llm-runs",
                    run_body(arm, registry, seed=first["seed"], num_rounds=nr,
                             episode_index=first["ep"], sentinel_check_index=None,
                             dry=True), timeout=60)
    if dry.get("liveCalls") != 0:
        freeze(state, f"preflight dry run did not report zero live calls: {dry}")
    print(f"preflight dry run ok (bundle {dry.get('bundleSha256', '')[:16]}…)", flush=True)


def act_dry_all(state: dict, store: ArmStoreP5, registry: dict, schedule: dict) -> None:
    """Validate EVERY Phase 5 request against enforcement at zero spend."""
    n = 0
    for arm_id in ENTRY_ARMS:
        arm = store.get(arm_id)
        for i, seed in enumerate(arm["seeds"], 1):
            http_json("POST", "/phase5/llm-runs",
                      run_body(arm, registry, seed=seed, num_rounds=1,
                               episode_index=i, sentinel_check_index=None,
                               dry=True), timeout=60)
            n += 1
    print(f"dry: entry battery ok ({n} requests)", flush=True)
    for k in range(0, 10):
        for arm_id in SENTINEL_ARMS:
            arm = store.get(arm_id)
            for seed in _sent_seeds(arm_id, k):
                http_json("POST", "/phase5/llm-runs",
                          run_body(arm, registry, seed=seed, num_rounds=1,
                                   episode_index=None, sentinel_check_index=k,
                                   dry=True), timeout=60)
                n += 1
    print("dry: sentinel windows 0–9 ok", flush=True)
    for block in schedule["blocks"]:
        m = 0
        for e in block["episodes"]:
            arm = store.get(e["armId"])
            nr, truncated = num_rounds_for(arm, e["seed"])
            if truncated:
                continue
            http_json("POST", "/phase5/llm-runs",
                      run_body(arm, registry, seed=e["seed"], num_rounds=nr,
                               episode_index=e["ep"], sentinel_check_index=None,
                               dry=True), timeout=60)
            m += 1
            if m % 200 == 0:
                print(f"dry: {block['block']} {m}/{len(block['episodes'])}", flush=True)
        n += m
        print(f"dry: block {block['block']} ok ({m} requests)", flush=True)
    print(f"DRY-ALL PASSED — {n} requests validated, zero spend", flush=True)


# Ops constants (analysis-surface-neutral, carried from Phase 4 provenance
# notes): pacing and bounded rate-limit retry affect wall-clock only.
GEMINI_PACE_S = 6.0
RATE_LIMIT_BACKOFF_S = 120.0


def _live(state: dict, body: dict, key: str) -> dict:
    state["inflight"] = {"key": key,
                         "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    save_state(state)
    try:
        resp = http_json("POST", "/phase5/llm-runs", body)
    except DriverFreeze as exc:
        msg = str(exc)
        if msg.startswith("HTTP ") and ("rate_limited" in msg or "RATELIMIT" in msg):
            print(f"  RATE-LIMITED {key}: terminal 429 from provider — backing off "
                  f"{RATE_LIMIT_BACKOFF_S:.0f}s, single re-dispatch (disclosed)", flush=True)
            time.sleep(RATE_LIMIT_BACKOFF_S)
            resp = http_json("POST", "/phase5/llm-runs", body)
        else:
            raise
    meta = resp.get("meta", {})
    if not state.get("_commit_checked"):
        check_engine_commit(state, meta)
        state["_commit_checked"] = True
        print(f"engineCommit verified clean @ {meta['engineCommit']['sha'][:12]}", flush=True)
    state["runs"][key] = {
        "engineRunId": resp.get("engineRunId"),
        "seed": resp.get("seed"),
        "invalidTrial": resp.get("invalidTrial", False),
        "llmCalls": meta.get("llmCalls"),
        "retriedCalls": meta.get("retriedCalls"),
        "inputTokens": meta.get("inputTokens"),
        "outputTokens": meta.get("outputTokens"),
    }
    state.pop("inflight", None)
    save_state(state)
    if str(body.get("model", "")).startswith("gemini"):
        time.sleep(GEMINI_PACE_S)
    return resp


def act_entry_battery(state: dict, store: ArmStoreP5, registry: dict) -> None:
    """24-call entry battery (ledgered overhead, operator-approved): every
    (model, T) cell live-verified for R2 per-T echo + R3 revision pin BEFORE
    any tier dispatch. Any runner abort surfaces as an HTTP refusal here and
    freezes — a mismatch is a stop-the-world event, not a data point."""
    assert_clean_tree(state)
    for arm_id in ENTRY_ARMS:
        arm = store.get(arm_id)
        for i, seed in enumerate(arm["seeds"], 1):
            key = f"P5-entry|{arm_id}|ep{i}"
            if key in state["runs"]:
                continue
            resp = _live(state, run_body(arm, registry, seed=seed, num_rounds=1,
                                         episode_index=i, sentinel_check_index=None,
                                         dry=False), key)
            if resp.get("invalidTrial"):
                freeze(state, f"ENTRY BATTERY invalid trial at {key} — protocol "
                              "viability in doubt; decision memo before dispatch")
        print(f"  entry cell {arm_id}: 4/4 ok (R2 echo + R3 pin held)", flush=True)
    print("ENTRY BATTERY PASSED — 6 cells × 4 calls, pins verified live", flush=True)


def act_sentinel(state: dict, store: ArmStoreP5, registry: dict, k: int) -> None:
    assert_clean_tree(state)
    lo = SENTINEL_SEED_BASE_P5 + k * 10
    print(f"— sentinel check {k} (window {lo}–{lo + 9}; 4 cells × 5) —", flush=True)
    for arm_id in SENTINEL_ARMS:
        arm = store.get(arm_id)
        for seed in _sent_seeds(arm_id, k):
            key = f"sent{k}|{arm_id}|{arm['model']}|{seed}"
            if key in state["runs"]:
                continue
            resp = _live(state, run_body(arm, registry, seed=seed, num_rounds=1,
                                         episode_index=None, sentinel_check_index=k,
                                         dry=False), key)
            meta = resp.get("meta", {})
            # frozen alert rule (b): retry or invalid inside a sentinel cell
            if meta.get("retriedCalls", 0) or resp.get("invalidTrial"):
                freeze(state, f"SENTINEL ALERT (rule b) at check {k}: {key} "
                              f"retried={meta.get('retriedCalls')} "
                              f"invalid={resp.get('invalidTrial')} — block-boundary freeze; "
                              "disclosure + decision memo before resuming")
        print(f"  cell {arm_id}: dispatch-count 5/5 (NOT a rule outcome)", flush=True)
    # Attestation gate (registered): dispatch past a sentinel check requires
    # a POSITIVE evaluator attestation — absence of evaluation fail-closes.
    r = subprocess.run(
        ["uv", "run", "python", os.path.join(_HERE, "phase5_adjudicate.py"),
         "--sentinel", str(k)], capture_output=True, text=True, cwd=_HERE)
    print(r.stdout, flush=True)
    if r.returncode != 0:
        freeze(state, f"SENTINEL check {k}: registered evaluator exit {r.returncode} "
                      f"(rule fired or refused) — attestation gate freeze; "
                      f"stderr: {r.stderr[-500:]}")
    state.setdefault("sentinelAttestations", {})[str(k)] = "evaluator exit 0"
    save_state(state)
    print(f"sentinel check {k} complete — evaluator attestation recorded", flush=True)


def act_block(state: dict, store: ArmStoreP5, registry: dict, schedule: dict, name: str) -> None:
    assert_clean_tree(state)
    # Attestation precondition: identical wording contract to Phase 4.
    dispatched_checks = {int(k.split("|")[0][4:]) for k in state.get("runs", {})
                         if k.startswith("sent")}
    attested = set(map(int, state.get("sentinelAttestations", {})))
    missing = sorted(dispatched_checks - attested)
    if missing:
        freeze(state, f"block dispatch requires evaluator attestation for sentinel "
                      f"check(s) {missing} — run the registered evaluator and record "
                      "the attestation (or a decision entry for a fired check) first")
    half = None
    if name.endswith((":h1", ":h2")):
        name, half = name.rsplit(":", 1)
    try:
        block = next(b for b in schedule["blocks"] if b["block"] == name)
    except StopIteration:
        raise SystemExit(f"block {name!r} not in sealed schedule — refusing")
    eps = block["episodes"]
    if half:
        mid = len(eps) // 2
        eps = eps[:mid] if half == "h1" else eps[mid:]
    done0 = sum(1 for e in eps if f"{name}|{e['armId']}|ep{e['ep']}" in state["runs"])
    print(f"— block {name}{' [' + half + ']' if half else ''}: {len(eps)} episodes "
          f"(resuming past {done0}) —", flush=True)
    t0 = time.time()
    invalids = 0
    for i, e in enumerate(eps, 1):
        key = f"{name}|{e['armId']}|ep{e['ep']}"
        if key in state["runs"] or key in state.get("excluded", {}):
            continue
        arm = store.get(e["armId"])
        nr, truncated = num_rounds_for(arm, e["seed"])
        if truncated:
            state.setdefault("excluded", {})[key] = \
                "horizon draw truncated at cap 120 (X1 rule: excluded, zero calls)"
            save_state(state)
            print(f"  EXCLUDED {key}: truncated horizon draw (disclosed)", flush=True)
            continue
        resp = _live(state, run_body(arm, registry, seed=e["seed"], num_rounds=nr,
                                     episode_index=e["ep"], sentinel_check_index=None,
                                     dry=False), key)
        if resp.get("invalidTrial"):
            invalids += 1
            print(f"  INVALID TRIAL {key} (recorded, spend kept; registered handling at analysis)", flush=True)
        if i % 25 == 0 or i == len(eps):
            st = http_json("GET", "/phase5/status", timeout=30)
            g = st["budget"]["byGroup"]
            rate = (i - done0) / max(time.time() - t0, 1e-9)
            print(f"  {name} {i}/{len(eps)}  spend "
                  + " ".join(f"{grp}={g[grp]['calls']}" for grp in g)
                  + f"  ({rate * 60:.1f} eps/min, invalids {invalids})", flush=True)
    print(f"block {name} complete ({invalids} invalid trials)", flush=True)


def act_hold() -> None:
    print("plan complete — HOLDING (workflow stays up; write a new plan and restart)", flush=True)
    while True:
        time.sleep(300)


def reconcile(state: dict) -> None:
    import sqlite3
    db = sqlite3.connect(f"file:{os.path.join(DATA_DIR, 'engine.db')}?mode=ro", uri=True)
    by_run: dict[str, dict] = {}
    q = ("SELECT run_id, type, payload FROM events WHERE type IN "
         "('llm.requested','llm.responded','run.completed','trial.invalidated')")
    for run_id, typ, payload in db.execute(q):
        p = json.loads(payload)
        rec = by_run.setdefault(run_id, {"completed": False, "invalid": False})
        if typ == "llm.requested" and "armId" in p:
            if not str(p["armId"]).startswith("p5-"):
                rec["foreign"] = True  # Phase 3/4 run — never reconciled here
                continue
            rec.update(armId=p["armId"], block=p.get("block"),
                       episodeIndex=p.get("episodeIndex"),
                       sentinelCheckIndex=p.get("sentinelCheckIndex"),
                       model=p.get("model"))
            if p.get("seed") is not None:
                rec["seed"] = p["seed"]
        elif typ == "run.completed":
            rec["completed"] = True
        elif typ == "trial.invalidated":
            rec["invalid"] = True
    recovered = 0
    for run_id, r in by_run.items():
        if r.get("foreign") or "armId" not in r or not (r["completed"] or r["invalid"]):
            continue
        if r.get("sentinelCheckIndex") is not None:
            key = f"sent{r['sentinelCheckIndex']}|{r['armId']}|{r['model']}|{r['seed']}"
        else:
            key = f"{r['block']}|{r['armId']}|ep{r['episodeIndex']}"
        if key not in state["runs"]:
            state["runs"][key] = {"engineRunId": run_id, "seed": r.get("seed"),
                                  "invalidTrial": r["invalid"], "reconciled": True}
            recovered += 1

    inflight = state.get("inflight")
    if inflight:
        key = inflight["key"]
        if key in state["runs"]:
            print(f"reconcile: inflight {key!r} FOUND completed/invalidated in the "
                  "event store — recorded; marker cleared", flush=True)
            state.pop("inflight", None)
        else:
            def _matches(r: dict) -> bool:
                if r.get("foreign") or "armId" not in r or r["completed"] or r["invalid"]:
                    return False
                if key.startswith("sent"):
                    k, arm_id, model, seed_s = key.split("|")
                    if (r.get("sentinelCheckIndex") != int(k[4:])
                            or r.get("armId") != arm_id or r.get("model") != model):
                        return False
                    return r.get("seed") is None or str(r.get("seed")) == seed_s
                blk, arm_id, ep = key.split("|")
                return (r.get("block") == blk and r.get("armId") == arm_id
                        and f"ep{r.get('episodeIndex')}" == ep)
            partials = [rid for rid, r in by_run.items() if _matches(r)]
            if partials:
                print(f"reconcile: inflight {key!r} matches PARTIAL run(s) {partials} "
                      "(requested but never completed/invalidated) — spend may exist; "
                      "marker KEPT: investigate the engine event store and budget "
                      "ledger manually before clearing", flush=True)
            else:
                print(f"reconcile: inflight {key!r} has no trace in the event store — "
                      "request never reached the engine; marker cleared, safe to resume",
                      flush=True)
                state.pop("inflight", None)
    save_state(state)
    print(f"reconcile: {recovered} runs recovered from the event store "
          f"({len(state['runs'])} total known)", flush=True)


def main() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    state = load_json(STATE_PATH, {"runs": {}, "done": {}})
    state.setdefault("runs", {})
    state.setdefault("done", {})
    state.pop("_commit_checked", None)

    if "--reconcile" in sys.argv:
        reconcile(state)
        return

    if state.get("frozen"):
        print(f"driver is FROZEN: {json.dumps(state['frozen'])}\n"
              "investigate, then remove the 'frozen' key from the state file to resume",
              flush=True)
        raise SystemExit(1)

    if state.get("inflight"):
        print(f"UNRESOLVED INFLIGHT DISPATCH: {json.dumps(state['inflight'])}\n"
              "a live request may have completed server-side without being recorded; "
              "run with --reconcile (event-store recovery) before resuming — never redispatch blindly",
              flush=True)
        raise SystemExit(1)

    plan = load_json(PLAN_PATH, None)
    if not plan or "actions" not in plan:
        print(f"no plan at {PLAN_PATH} — nothing to do; holding", flush=True)
        act_hold()
        return

    store = ArmStoreP5()
    registry, _sha = load_registry()
    schedule = json.load(open(SCHEDULE_PATH))

    try:
        for action in plan["actions"]:
            if state["done"].get(action):
                continue
            print(f"=== action: {action} ===", flush=True)
            if action == "preflight":
                act_preflight(state, store, registry, schedule)
            elif action == "dry-all":
                act_dry_all(state, store, registry, schedule)
            elif action == "entry-battery":
                act_entry_battery(state, store, registry)
            elif action.startswith("sentinel:"):
                act_sentinel(state, store, registry, int(action.split(":")[1]))
            elif action.startswith("block:"):
                act_block(state, store, registry, schedule, action.split(":", 1)[1])
            elif action == "hold":
                act_hold()
            else:
                freeze(state, f"unknown plan action {action!r}")
            state["done"][action] = True
            save_state(state)
    except DriverFreeze as e:
        freeze(state, str(e))
    act_hold()


if __name__ == "__main__":
    main()
