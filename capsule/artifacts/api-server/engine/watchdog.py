"""Driver watchdog: auto-resume for REGISTERED freeze signatures only.

Instance-ledger rule context: the Phase 4 driver fail-closes on everything —
protocol violations, attestation gaps, AND ambiguous transport failures. The
first two must stay manual forever. The third class (transport blips,
container restarts) proved to be pure operational noise in Phase 4: every one
was resolved by `--reconcile` + resume with zero scientific content. The
watchdog automates exactly that class and nothing else.

Behavior:
- Runs the driver as a supervised subprocess in a loop.
- On driver exit: read the state file. If `frozen` is present and its reason
  matches a signature in `resume-signatures.json` (substring match, registered
  list), the watchdog (1) appends the event to `watchdog-log.jsonl`,
  (2) runs `--reconcile` to rebuild completion state from the event store,
  (3) deletes ONLY the `frozen` key, (4) relaunches the driver.
- Any freeze whose reason does not match a registered signature is left
  frozen; the watchdog logs and exits non-zero. No signature match = no
  resume — the manual-unfreeze discipline is unchanged for scientific
  freezes.
- Bounded: at most MAX_RESUMES_PER_HOUR auto-resumes; exceeding the bound is
  itself an anomaly and hard-stops the watchdog (frozen state preserved).
- A driver that exits 0 (plan complete / hold) ends the loop normally.
- Container restarts need no special case: the workflow relaunches the
  watchdog, which relaunches the driver; completed actions are skipped by the
  driver's own resume state, and a stale inflight marker surfaces as the
  registered ambiguous-transport freeze handled above.

Usage:
    uv run python engine/watchdog.py                 # supervise the real driver
    uv run python engine/watchdog.py --selftest      # no driver, no dispatch
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time

ENGINE = os.path.dirname(os.path.abspath(__file__))
SIGNATURES_PATH = os.path.join(ENGINE, "resume-signatures.json")
STATE_PATH = os.path.join(ENGINE, "data", "phase4-driver-state.json")
LOG_PATH = os.path.join(ENGINE, "data", "watchdog-log.jsonl")
DRIVER_CMD = [sys.executable, os.path.join(ENGINE, "phase4_driver.py")]
RECONCILE_CMD = DRIVER_CMD + ["--reconcile"]
MAX_RESUMES_PER_HOUR = 5


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _log(event: dict) -> None:
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(json.dumps({"at": _now(), **event}) + "\n")


def load_signatures(path: str = SIGNATURES_PATH) -> list[str]:
    with open(path) as f:
        data = json.load(f)
    sigs = data["signatures"]
    if not isinstance(sigs, list) or not all(isinstance(s, str) and s for s in sigs):
        raise ValueError("resume-signatures.json: 'signatures' must be non-empty strings")
    return sigs


def match_signature(reason: str, signatures: list[str]) -> str | None:
    """Registered substring match. Returns the matching signature or None."""
    for s in signatures:
        if s in reason:
            return s
    return None


def read_frozen(state_path: str) -> dict | None:
    if not os.path.exists(state_path):
        return None
    with open(state_path) as f:
        state = json.load(f)
    return state.get("frozen")


def clear_frozen(state_path: str) -> None:
    with open(state_path) as f:
        state = json.load(f)
    frozen = state.pop("frozen", None)
    state.setdefault("watchdogResumes", []).append(
        {"at": _now(), "clearedFrozen": frozen})
    tmp = state_path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, state_path)


def supervise(state_path: str = STATE_PATH,
              driver_cmd: list[str] | None = None,
              reconcile_cmd: list[str] | None = None) -> int:
    driver_cmd = driver_cmd or DRIVER_CMD
    reconcile_cmd = reconcile_cmd or RECONCILE_CMD
    signatures = load_signatures()
    resumes: list[float] = []
    while True:
        rc = subprocess.call(driver_cmd)
        if rc == 0:
            _log({"event": "driver-exit-clean"})
            return 0
        frozen = read_frozen(state_path)
        if not frozen:
            _log({"event": "driver-exit-nonzero-unfrozen", "rc": rc})
            return rc  # crash without a freeze record: not ours to fix
        sig = match_signature(str(frozen.get("reason", "")), signatures)
        if sig is None:
            _log({"event": "freeze-not-registered", "frozen": frozen})
            print(f"watchdog: freeze reason is NOT a registered resume signature; "
                  f"staying frozen (manual investigation required):\n"
                  f"  {frozen.get('reason', '')[:400]}", file=sys.stderr)
            return 1
        now = time.time()
        resumes = [t for t in resumes if now - t < 3600]
        if len(resumes) >= MAX_RESUMES_PER_HOUR:
            _log({"event": "resume-bound-exceeded", "frozen": frozen,
                  "bound": MAX_RESUMES_PER_HOUR})
            print("watchdog: auto-resume bound exceeded — repeated transport "
                  "freezes are an anomaly, not noise. Staying frozen.",
                  file=sys.stderr)
            return 1
        _log({"event": "auto-resume", "signature": sig, "frozen": frozen})
        rrc = subprocess.call(reconcile_cmd)
        if rrc != 0:
            _log({"event": "reconcile-failed", "rc": rrc})
            print("watchdog: --reconcile failed; staying frozen.", file=sys.stderr)
            return 1
        clear_frozen(state_path)
        resumes.append(now)
        time.sleep(5)


# ----------------------------------------------------------------- selftest
def selftest() -> int:
    """No driver, no dispatch: exercises signature matching, bounded resume,
    and the refusal path against stub state files and a stub 'driver'."""
    import tempfile
    sigs = load_signatures()
    ok = True

    def check(name: str, cond: bool) -> None:
        nonlocal ok
        print(f"{'PASS' if cond else 'FAIL'}  {name}")
        ok = ok and cond

    check("registered signatures load and are non-empty", len(sigs) >= 1)
    check("transport freeze matches",
          match_signature("AMBIGUOUS transport failure on POST /phase4/run: "
                          "TimeoutError: timed out — run may have completed "
                          "server-side; use --reconcile before resuming", sigs)
          is not None)
    check("attestation freeze does NOT match",
          match_signature("block dispatch requires evaluator attestation for "
                          "sentinel check 9", sigs) is None)
    check("sentinel alert freeze does NOT match",
          match_signature("SENTINEL ALERT (rule b) at check 5: gemini v2a "
                          "fingerprint moved", sigs) is None)
    check("worktree freeze does NOT match",
          match_signature("worktree not clean at dispatch time: M engine.py",
                          sigs) is None)

    with tempfile.TemporaryDirectory() as td:
        st = os.path.join(td, "state.json")
        marker = os.path.join(td, "resumed")
        # Stub driver: exits 1 with a transport freeze on first run; exits 0
        # once the marker shows reconcile+resume happened.
        drv = os.path.join(td, "drv.py")
        with open(drv, "w") as f:
            f.write(f"""
import json, os, sys
st, marker = {st!r}, {marker!r}
if os.path.exists(marker):
    sys.exit(0)
json.dump({{"frozen": {{"reason": "AMBIGUOUS transport failure on GET /x: "
    "ConnectionResetError: peer reset", "at": "t"}}}}, open(st, "w"))
sys.exit(1)
""")
        rec = os.path.join(td, "rec.py")
        with open(rec, "w") as f:
            f.write(f"open({marker!r}, 'w').write('1')\n")
        rc = supervise(state_path=st, driver_cmd=[sys.executable, drv],
                       reconcile_cmd=[sys.executable, rec])
        check("end-to-end: transport freeze -> reconcile -> resume -> clean exit",
              rc == 0 and os.path.exists(marker)
              and read_frozen(st) is None
              and json.load(open(st)).get("watchdogResumes"))

        # Refusal path: non-registered freeze stays frozen, exit 1.
        st2 = os.path.join(td, "state2.json")
        drv2 = os.path.join(td, "drv2.py")
        with open(drv2, "w") as f:
            f.write(f"""
import json, sys
json.dump({{"frozen": {{"reason": "SENTINEL ALERT (rule b) at check 3", "at": "t"}}}},
          open({st2!r}, "w"))
sys.exit(1)
""")
        rc2 = supervise(state_path=st2, driver_cmd=[sys.executable, drv2],
                        reconcile_cmd=[sys.executable, rec])
        check("refusal: scientific freeze stays frozen, watchdog exits 1",
              rc2 == 1 and read_frozen(st2) is not None)

    print(f"\nselftest: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    if "--phase5" in sys.argv:
        p5_state = os.path.join(ENGINE, "data", "phase5-driver-state.json")
        p5_cmd = [sys.executable, os.path.join(ENGINE, "phase5_driver.py")]
        sys.exit(supervise(state_path=p5_state, driver_cmd=p5_cmd,
                           reconcile_cmd=p5_cmd + ["--reconcile"]))
    sys.exit(supervise())
