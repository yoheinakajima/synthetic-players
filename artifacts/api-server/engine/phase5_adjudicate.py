"""Phase 5 registered sentinel evaluator — attestation gate (fail-closed).

Called by phase5_driver.act_sentinel after each check's dispatch:
    uv run python engine/phase5_adjudicate.py --sentinel <k>

Adjudicates machine-checkable predicates ONLY (honest-pipeline rule: code
adjudicates, never the author). Exit 0 = positive attestation; any nonzero
exit freezes the driver at the block boundary. Absence of data fail-closes.

Predicates per check k (registered, freeze packet §6):
  S1 completeness: all 20 sentinel episodes (4 cells × 5 seeds) present in
     the event store with run.completed, none invalidated.
  S2 alert rule (b) recheck: zero parse retries (attempt==1 events) and
     zero trial.invalidated inside the check's sentinel cells.
  S3 R3-revision-pin recheck: every llm.responded model string equals the
     registered pin for its arm's model.
  S4 R2 record recheck: every llm.requested temperature equals 0.7 (all
     sentinel arms pin T=0.7).
  S5 seed-window recheck: every recorded seed lies in the check-k window.
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from phase5 import PINNED_REVISIONS, SENTINEL_SEED_BASE_P5  # noqa: E402

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "engine.db")
SENTINEL_ARMS = {"p5-sent-p01-gpt": "gpt-4.1", "p5-sent-bare-gpt": "gpt-4.1",
                 "p5-sent-p01-gem": "gemini-2.5-flash", "p5-sent-bare-gem": "gemini-2.5-flash"}


def fail(msg: str) -> None:
    print(f"ATTESTATION REFUSED: {msg}")
    raise SystemExit(1)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sentinel", type=int, required=True)
    k = ap.parse_args().sentinel
    lo = SENTINEL_SEED_BASE_P5 + k * 10
    window = range(lo, lo + 10)

    if not os.path.exists(DB):
        fail(f"engine event store not found at {DB} (no data = no attestation)")
    db = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)

    runs: dict[str, dict] = {}
    q = ("SELECT run_id, type, payload FROM events WHERE type IN "
         "('llm.requested','llm.responded','run.completed','trial.invalidated')")
    for run_id, typ, payload in db.execute(q):
        p = json.loads(payload)
        if typ == "llm.requested":
            if p.get("sentinelCheckIndex") != k or p.get("armId") not in SENTINEL_ARMS:
                continue
            r = runs.setdefault(run_id, {"requested": [], "responded": [],
                                         "completed": False, "invalid": False})
            r["requested"].append(p)
            r.update(armId=p["armId"], model=p.get("model"), seed=p.get("seed"))
        elif run_id in runs:
            r = runs[run_id]
            if typ == "llm.responded":
                r["responded"].append(p)
            elif typ == "run.completed":
                r["completed"] = True
            else:
                r["invalid"] = True

    # S1 completeness (4 cells × 5 seeds; per-model lanes share the window)
    seen = {(r["armId"], r["seed"]) for r in runs.values() if r["completed"]}
    expected = set()
    for arm_id in SENTINEL_ARMS:
        lane = range(lo, lo + 5) if "-p01-" in arm_id else range(lo + 5, lo + 10)
        expected |= {(arm_id, s) for s in lane}
    missing = expected - seen
    if missing:
        fail(f"S1: {len(missing)} sentinel episodes missing/incomplete for check {k}: "
             f"{sorted(missing)[:6]}")

    for run_id, r in runs.items():
        # S2 alert rule (b)
        if r["invalid"]:
            fail(f"S2: invalid trial in sentinel cell {r['armId']} seed {r['seed']} ({run_id})")
        if any(req.get("attempt") == 1 for req in r["requested"]):
            fail(f"S2: parse retry in sentinel cell {r['armId']} seed {r['seed']} ({run_id})")
        # S3 revision pin
        pin = PINNED_REVISIONS[SENTINEL_ARMS[r["armId"]]]
        for resp in r["responded"]:
            if resp.get("model") != pin:
                fail(f"S3: returned model {resp.get('model')!r} != pin {pin!r} ({run_id})")
        # S4 temperature record
        for req in r["requested"]:
            if float(req.get("temperature", -1)) != 0.7:
                fail(f"S4: recorded temperature {req.get('temperature')} != 0.7 ({run_id})")
        # S5 seed window
        if r["seed"] not in window:
            fail(f"S5: seed {r['seed']} outside window {lo}–{lo + 9} ({run_id})")

    print(f"ATTESTATION POSITIVE: sentinel check {k} — S1–S5 hold "
          f"({len(seen)} episodes, window {lo}–{lo + 9})")


if __name__ == "__main__":
    main()
