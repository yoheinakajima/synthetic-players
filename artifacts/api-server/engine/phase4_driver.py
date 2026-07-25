"""Phase 4 dispatch driver — sealed-schedule executor (step 4+).

Design contract (committed BEFORE any live dispatch):
- Requests are constructed from the sealed arms manifest + registry using the
  ENGINE'S OWN derivation functions (phase4._pd_expected_matrix,
  _rps_sym_expected_matrix, _pure_nash, registry options) — byte-parity with
  the enforcement layer by construction, not by reimplementation.
- Horizons for E / X2 blocks use the registered Phase 3 rule
  geometric(δ) via mulberry32(seed ^ 0x54524D), cap 120; a truncated draw
  EXCLUDES the supergame (zero calls, disclosed) — port of
  scripts/run-phase3.mjs drawHorizon, RNG imported from engine strategies.
- Plan-file execution: engine/data/phase4-driver-plan.json (gitignored)
      {"actions": ["preflight", "dry-all", "sentinel:0",
                   "block:X2-screening", "sentinel:1", "hold"]}
  Completed actions are skipped on restart; per-run resume state lives in
  engine/data/phase4-driver-state.json (gitignored, atomic writes).
- STOP-ON-ANOMALY: any HTTP refusal (enforcement/budget), sentinel retry or
  invalid trial (frozen alert rule (b)), engineCommit sha/dirty mismatch
  (first live run is asserted {sha: recorded HEAD, dirty: false}), dirty
  worktree at dispatch time, or ambiguous transport failure FREEZES the
  driver: state["frozen"] is written and the process exits 1. Unfreezing is
  a manual act (delete the "frozen" key) after investigation — never silent.
- Reconcile mode (`--reconcile`) rebuilds completion state from the engine
  event store (read-only) after an ambiguous failure; it never dispatches.

Run:  cd artifacts/api-server && uv run python engine/phase4_driver.py
      (workflow "Phase 4 Driver"; plan file controls what happens)
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

from phase4 import (  # noqa: E402
    ArmStore,
    _pd_expected_matrix,
    _pure_nash,
    _rps_standard_matrix,
    _rps_sym_expected_matrix,
)
from llm_subject import load_registry  # noqa: E402
from strategies import mulberry32  # noqa: E402

ENGINE_URL = os.environ.get("P4_ENGINE_URL", "http://127.0.0.1:8090")
_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.normpath(os.path.join(_HERE, "..", "..", ".."))
SCHEDULE_PATH = os.path.join(REPO_ROOT, "docs", "phase4", "execution-schedule.json")
DATA_DIR = os.path.join(_HERE, "data")
PLAN_PATH = os.path.join(DATA_DIR, "phase4-driver-plan.json")
STATE_PATH = os.path.join(DATA_DIR, "phase4-driver-state.json")

SUBJECT_MODELS = ["gpt-4.1", "gemini-2.5-flash"]
SENTINEL_ARMS = ["p4-sent-v1", "p4-sent-v2a", "p4-sent-fallback"]
LIVE_TIMEOUT_S = 900  # X2 horizons reach 120 rounds (240 calls) worst-case
STEP4_BLOCKS = ["X2-screening", "D1", "D2", "D3"]  # dry-all scope


class DriverFreeze(Exception):
    """Any condition that must stop dispatch until a human looks."""


# ── deterministic horizon draw (byte-parity with scripts/run-phase3.mjs) ────

def draw_horizon(seed: int, delta_pct: int) -> tuple[int, bool]:
    rng = mulberry32((seed ^ 0x54524D) & 0xFFFFFFFF)
    delta = delta_pct / 100
    rounds = 1
    while rng() < delta:
        rounds += 1
        if rounds >= 120:
            return 120, True
    return rounds, False


# ── request construction (engine-derivation reuse) ──────────────────────────

_RESOLUTIONS_CACHE: dict | None = None


def sealed_resolution_tid(arm: dict) -> str:
    """Concrete template for a RESOLVED-BY-* arm via the engine's sealed
    write-once resolutions. The driver only SUBSTITUTES; the engine remains
    the enforcement point (resolve_template_id + template-sha recheck on
    every request). Fails closed if the resolution is not yet written."""
    global _RESOLUTIONS_CACHE
    if _RESOLUTIONS_CACHE is None:
        _RESOLUTIONS_CACHE = http_json("GET", "/phase4/status").get("resolutions") or {}
    if arm["block"] == "E":
        key = "E-dselected"
    elif arm["block"] == "X2-confirmation":
        key = "X2-conf-lo" if arm["armId"].endswith("-lo") else "X2-conf-hi"
    else:
        raise DriverFreeze(
            f"arm {arm['armId']} has RESOLVED-BY template but no resolution-key rule — refusing")
    res = _RESOLUTIONS_CACHE.get(key)
    tid = res.get("templateId") if isinstance(res, dict) else res
    if not tid:
        raise DriverFreeze(
            f"arm {arm['armId']} requires resolution {key!r} — not yet written to the event store (refusing)")
    return tid


def sentinel_fallback_tid(arm: dict) -> str:
    """Sealed sentinel spec: the third cell 'switches to the D-selected
    representation once written to the event store; sealed fallback before'.
    Ledger-state-driven via the engine's write-once resolutions; the engine
    enforces the identical rule in resolve_template_id (memo §Decision,
    provenance instance 5)."""
    global _RESOLUTIONS_CACHE
    if _RESOLUTIONS_CACHE is None:
        _RESOLUTIONS_CACHE = http_json("GET", "/phase4/status").get("resolutions") or {}
    res = _RESOLUTIONS_CACHE.get("E-dselected")
    tid = res.get("templateId") if isinstance(res, dict) else res
    return tid if tid else arm["templateId"]


def build_game_def(arm: dict, registry: dict) -> dict:
    tid = arm["templateId"]
    if tid.startswith("RESOLVED-BY"):
        tid = sealed_resolution_tid(arm)
    elif arm["armId"] == "p4-sent-fallback":
        tid = sentinel_fallback_tid(arm)
    spec = registry["prompts"].get(tid)
    if spec is None:
        raise DriverFreeze(f"template {tid} not in registry")
    options = spec["options"]
    if tid == "rps-sym-v1":
        matrix, slug = _rps_sym_expected_matrix(arm["bindings"]["roleMapping"]), "phase4-rps"
    elif tid == "rps-v1":
        matrix, slug = _rps_standard_matrix(), "phase4-rps"
    else:
        matrix, slug = _pd_expected_matrix(arm["bindings"]), "phase4-pd"
    return {
        "slug": slug,
        "numActions": len(options),
        "actionLabels": list(options),
        "payoffMatrix": matrix,
        "nashEquilibria": _pure_nash(matrix),
    }


def num_rounds_for(arm: dict, seed: int) -> tuple[int | None, bool]:
    """(numRounds, truncated). None ⇒ excluded supergame (no call)."""
    block = arm["block"]
    if block in ("D1", "D2", "D3", "sentinel"):
        return 1, False
    if block == "F":
        return int(arm["bindings"]["rounds"]), False
    if block in ("E", "X2-screening", "X2-confirmation"):
        rounds, truncated = draw_horizon(seed, int(arm["deltaPct"]))
        if truncated:
            return None, True
        return rounds, False
    raise DriverFreeze(f"no horizon rule for block {block}")


def run_body(arm: dict, registry: dict, *, seed: int, model: str,
             num_rounds: int, episode_index: int | None,
             sentinel_check_index: int | None, dry: bool) -> dict:
    body = {
        "armId": arm["armId"],
        "game": build_game_def(arm, registry),
        "strategy1Slug": "llm-subject",
        "strategy2Slug": "llm-subject",
        "numRounds": num_rounds,
        "seed": seed,
        "model": model,
        "temperature": 0.7,
        "maxTokens": 16,
        "dryRun": dry,
    }
    if episode_index is not None:
        body["episodeIndex"] = episode_index
    if sentinel_check_index is not None:
        body["sentinelCheckIndex"] = sentinel_check_index
    return body


# ── HTTP ─────────────────────────────────────────────────────────────────────

def http_json(method: str, path: str, body: dict | None = None,
              timeout: int = LIVE_TIMEOUT_S) -> dict:
    req = urllib.request.Request(
        ENGINE_URL + path,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Content-Type": "application/json"},
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:2000]
        raise DriverFreeze(f"HTTP {e.code} on {method} {path}: {detail}") from e
    except Exception as e:  # timeout / connection — AMBIGUOUS, never redispatch
        raise DriverFreeze(
            f"AMBIGUOUS transport failure on {method} {path}: {type(e).__name__}: {e} — "
            "run may have completed server-side; use --reconcile before resuming"
        ) from e


# ── state ────────────────────────────────────────────────────────────────────

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
    state["frozen"] = {"reason": reason, "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    save_state(state)
    print(f"\n*** DRIVER FROZEN ***\n{reason}", flush=True)
    raise SystemExit(1)


# ── git hygiene (engineCommit discipline, rider 2) ──────────────────────────

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
    """Asserted on the FIRST live run of each driver process (the engine
    lru-caches its commit at first stamp — this catches a stale cache)."""
    ec = meta.get("engineCommit") or {}
    if ec.get("sha") != state.get("head") or ec.get("dirty") is not False:
        freeze(state, f"engineCommit mismatch on first live run: stamped {ec}, "
                      f"expected {{'sha': {state.get('head')!r}, 'dirty': False}} — "
                      "restart the Engine workflow on a clean tree and reconcile")


# ── actions ──────────────────────────────────────────────────────────────────

def act_preflight(state: dict, store: ArmStore, registry: dict, schedule: dict) -> None:
    status = http_json("GET", "/phase4/status", timeout=30)
    if not status.get("sealed") or not status["selfCheck"]["ok"]:
        freeze(state, f"engine not sealed/self-checked: {json.dumps(status)[:400]}")
    print("budget:", json.dumps(status["budget"]["byGroup"]), flush=True)

    head = assert_clean_tree(state)
    state["head"] = head
    save_state(state)
    print(f"HEAD {head} (clean)", flush=True)

    # projected X2 screening horizons (registered draw, seeds 1–10, δ=.90)
    hs = {s: draw_horizon(s, 90) for s in range(1, 11)}
    total = sum(2 * r for r, t in hs.values() if r is not None)
    print("X2 horizons per seed:", {s: r for s, (r, _t) in hs.items()},
          f"→ calls/rung {total}, screening total {10 * total}", flush=True)
    if any(t for _r, t in hs.values()):
        freeze(state, f"truncated X2 horizon draw in seeds 1–10: {hs} — "
                      "X1 exclusion rule applies; verify against X1 records first")

    first = schedule["blocks"][0]["episodes"][0]
    arm = store.get(first["armId"])
    nr, _ = num_rounds_for(arm, first["seed"])
    dry = http_json("POST", "/phase4/llm-runs",
                    run_body(arm, registry, seed=first["seed"], model=first["model"],
                             num_rounds=nr, episode_index=first["ep"],
                             sentinel_check_index=None, dry=True), timeout=60)
    if dry.get("liveCalls") != 0:
        freeze(state, f"preflight dry run did not report zero live calls: {dry}")
    print(f"preflight dry run ok (bundle {dry.get('bundleSha256', '')[:16]}…)", flush=True)


def act_dry_all(state: dict, store: ArmStore, registry: dict, schedule: dict) -> None:
    """Validate EVERY step-4 request against enforcement at zero spend."""
    n = 0
    for k in range(0, 5):  # sentinel windows for checks 0–4 (step-4 scope)
        lo = 9001 + k * 10
        for arm_id in SENTINEL_ARMS:
            arm = store.get(arm_id)
            for model in SUBJECT_MODELS:
                for seed in range(lo, lo + 10):
                    http_json("POST", "/phase4/llm-runs",
                              run_body(arm, registry, seed=seed, model=model,
                                       num_rounds=1, episode_index=None,
                                       sentinel_check_index=k, dry=True), timeout=60)
                    n += 1
    print(f"dry: sentinel windows 0–4 ok ({n} requests)", flush=True)
    for block in schedule["blocks"]:
        if block["block"] not in STEP4_BLOCKS:
            continue
        m = 0
        for e in block["episodes"]:
            arm = store.get(e["armId"])
            nr, truncated = num_rounds_for(arm, e["seed"])
            if truncated:
                continue  # excluded supergame — no request exists to validate
            http_json("POST", "/phase4/llm-runs",
                      run_body(arm, registry, seed=e["seed"], model=e["model"],
                               num_rounds=nr, episode_index=e["ep"],
                               sentinel_check_index=None, dry=True), timeout=60)
            m += 1
            if m % 200 == 0:
                print(f"dry: {block['block']} {m}/{len(block['episodes'])}", flush=True)
        n += m
        print(f"dry: block {block['block']} ok ({m} requests)", flush=True)
    print(f"DRY-ALL PASSED — {n} requests validated, zero spend", flush=True)


# Ops constants (analysis-surface-neutral; provenance-notes.md 2026-07-25):
# pacing and bounded rate-limit retry affect wall-clock only — never prompts,
# seeds, templates, or decision rules. δ=90 gemini episodes are a sustained
# ~2-calls/round burst that D/X2 never produced; check 429 freeze at E ep 26.
GEMINI_PACE_S = 6.0
RATE_LIMIT_BACKOFF_S = 120.0


def _live(state: dict, body: dict, key: str) -> dict:
    # At-most-once guard: persist an inflight marker BEFORE the POST. If the
    # process dies between response receipt and state save, startup sees the
    # marker and demands --reconcile instead of silently re-dispatching.
    state["inflight"] = {"key": key,
                         "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    save_state(state)
    try:
        resp = http_json("POST", "/phase4/llm-runs", body)
    except DriverFreeze as exc:
        msg = str(exc)
        if msg.startswith("HTTP ") and ("rate_limited" in msg or "RATELIMIT" in msg):
            # The engine returned a terminal rate-limit refusal: the response
            # WAS received, the failed attempt is disclosed in the event store
            # (llm.* events without run.completed), and its spend is counted.
            # One paced re-dispatch of the same scheduled episode is the
            # registered ops response; a second failure freezes as designed.
            # The inflight marker stays up through the backoff.
            print(f"  RATE-LIMITED {key}: terminal 429 from provider — backing off "
                  f"{RATE_LIMIT_BACKOFF_S:.0f}s, single re-dispatch (disclosed)", flush=True)
            time.sleep(RATE_LIMIT_BACKOFF_S)
            resp = http_json("POST", "/phase4/llm-runs", body)
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
        time.sleep(GEMINI_PACE_S)  # inter-run pacing, wall-clock only
    return resp


def act_sentinel(state: dict, store: ArmStore, registry: dict, k: int,
                 models: list[str] | None = None) -> None:
    assert_clean_tree(state)
    models = models or SUBJECT_MODELS
    lo = 9001 + k * 10
    scope = (f"3 arms × {models[0]} only × 10 — doubled gemini cadence, "
             "sentinel-alert-5-memo.md §Decision rider 2"
             if len(models) == 1 else "3 arms × 2 models × 10")
    print(f"— sentinel check {k} (seeds {lo}–{lo + 9}; {scope}) —", flush=True)
    for arm_id in SENTINEL_ARMS:
        arm = store.get(arm_id)
        for model in models:
            for seed in range(lo, lo + 10):
                key = f"sent{k}|{arm_id}|{model}|{seed}"
                if key in state["runs"]:
                    continue
                resp = _live(state, run_body(arm, registry, seed=seed, model=model,
                                             num_rounds=1, episode_index=None,
                                             sentinel_check_index=k, dry=False), key)
                meta = resp.get("meta", {})
                # frozen alert rule (b): retry or invalid inside a sentinel cell
                if meta.get("retriedCalls", 0) or resp.get("invalidTrial"):
                    freeze(state, f"SENTINEL ALERT (rule b) at check {k}: {key} "
                                  f"retried={meta.get('retriedCalls')} "
                                  f"invalid={resp.get('invalidTrial')} — block-boundary freeze; "
                                  "disclosure + decision memo before resuming")
            print(f"  cell {arm_id} × {model}: 10/10", flush=True)
    print(f"sentinel check {k} complete", flush=True)


def act_block(state: dict, store: ArmStore, registry: dict, schedule: dict, name: str) -> None:
    assert_clean_tree(state)
    half = None
    if name.endswith((":h1", ":h2")):
        name, half = name.rsplit(":", 1)  # dispatch partition only: sealed
        # episode order and keys are unchanged; h1 = first half, h2 = rest
        # (mid-block gemini sentinel cadence, sentinel-alert-5-memo.md rider 2)
    try:
        block = next(b for b in schedule["blocks"] if b["block"] == name)
    except StopIteration:
        # Packaging gap #2 (provenance-notes.md): conditional blocks live in the
        # amendments file; the sealed schedule stays byte-identical to its anchor.
        amend_path = os.path.join(REPO_ROOT, "docs", "phase4", "execution-schedule-amendments.json")
        if not os.path.exists(amend_path):
            raise SystemExit(f"block {name!r} not in sealed schedule and no amendments file — refusing")
        block = next((b for b in json.load(open(amend_path))["blocks"] if b["block"] == name), None)
        if block is None:
            raise SystemExit(f"block {name!r} not in sealed schedule or amendments — refusing")
        print(f"— block {name} sourced from execution-schedule-amendments.json "
              f"(sealed schedule untouched) —", flush=True)
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
            state.setdefault("excluded", {})[key] = "horizon draw truncated at cap 120 (X1 rule: excluded, zero calls)"
            save_state(state)
            print(f"  EXCLUDED {key}: truncated horizon draw (disclosed)", flush=True)
            continue
        resp = _live(state, run_body(arm, registry, seed=e["seed"], model=e["model"],
                                     num_rounds=nr, episode_index=e["ep"],
                                     sentinel_check_index=None, dry=False), key)
        if resp.get("invalidTrial"):
            invalids += 1
            print(f"  INVALID TRIAL {key} (recorded, spend kept; registered handling at analysis)", flush=True)
        if i % 25 == 0 or i == len(eps):
            st = http_json("GET", "/phase4/status", timeout=30)
            g = st["budget"]["byGroup"]
            rate = (i - done0) / max(time.time() - t0, 1e-9)
            print(f"  {name} {i}/{len(eps)}  spend D={g['D']['calls']} X2={g['X2']['calls']} "
                  f"E={g['E']['calls']} ovh={g['overhead']['calls']}  "
                  f"({rate * 60:.1f} eps/min, invalids {invalids})", flush=True)
    print(f"block {name} complete ({invalids} invalid trials)", flush=True)


def act_hold() -> None:
    print("plan complete — HOLDING (workflow stays up; write a new plan and restart)", flush=True)
    while True:
        time.sleep(300)


# ── reconcile (read-only event-store recovery) ──────────────────────────────

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
            rec.update(armId=p["armId"], block=p.get("block"),
                       episodeIndex=p.get("episodeIndex"),
                       sentinelCheckIndex=p.get("sentinelCheckIndex"),
                       model=p.get("model"))
            if p.get("seed") is not None:
                rec["seed"] = p["seed"]  # authoritative scheduled seed (requested-side)
        elif typ == "llm.responded":
            if rec.get("seed") is None:
                rec["seed"] = p.get("seed")  # legacy fallback (phase-3 event shape)
        elif typ == "run.completed":
            rec["completed"] = True
        elif typ == "trial.invalidated":
            rec["invalid"] = True
    recovered = 0
    for run_id, r in by_run.items():
        if "armId" not in r or not (r["completed"] or r["invalid"]):
            continue
        if r.get("sentinelCheckIndex") is not None:
            key = f"sent{r['sentinelCheckIndex']}|{r['armId']}|{r['model']}|{r['seed']}"
        else:
            key = f"{r['block']}|{r['armId']}|ep{r['episodeIndex']}"
        if key not in state["runs"]:
            state["runs"][key] = {"engineRunId": run_id, "seed": r.get("seed"),
                                  "invalidTrial": r["invalid"], "reconciled": True}
            recovered += 1

    # Resolve an unresolved inflight marker (at-most-once recovery).
    inflight = state.get("inflight")
    if inflight:
        key = inflight["key"]
        if key in state["runs"]:
            print(f"reconcile: inflight {key!r} FOUND completed/invalidated in the "
                  "event store — recorded; marker cleared", flush=True)
            state.pop("inflight", None)
        else:
            # A partial run (llm.requested without run.completed/trial.invalidated)
            # matching the inflight identity means spend may exist server-side.
            # Sentinel keys lack the seed until llm.responded, so match on cell.
            def _matches(r: dict) -> bool:
                if "armId" not in r or r["completed"] or r["invalid"]:
                    return False
                if key.startswith("sent"):
                    k, arm_id, model, seed_s = key.split("|")
                    if (r.get("sentinelCheckIndex") != int(k[4:])
                            or r.get("armId") != arm_id or r.get("model") != model):
                        return False
                    # exact when the partial recorded its seed (llm.requested now
                    # carries it); conservative cell-level match otherwise
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


# ── main ─────────────────────────────────────────────────────────────────────

def main() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    state = load_json(STATE_PATH, {"runs": {}, "done": {}})
    state.setdefault("runs", {})
    state.setdefault("done", {})
    state.pop("_commit_checked", None)  # per-process assertion

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

    store = ArmStore()
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
            elif action.startswith("sentinelg:"):
                act_sentinel(state, store, registry, int(action.split(":")[1]),
                             models=["gemini-2.5-flash"])
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
        # Every anomaly path must PERSIST the frozen flag (freeze() raises
        # SystemExit, which this except does not swallow).
        freeze(state, str(e))
    act_hold()


if __name__ == "__main__":
    main()
