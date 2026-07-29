"""Step-8 replay audit (freeze packet step 8): byte-exact replay of every
Phase 4 run via the engine's §F.3 extended replay endpoint (zero live
calls), plus the F-family rngCalls profile audit required by the architect
review ruling (2026-07-28). Read-only against the event store; writes
docs/phase4/step8-replay-audit.{json,md}. Fail-closed: any replay mismatch
or profile deviation → nonzero exit and STOP-ON-ANOMALY.

Registered expected draw profiles (f-opponent-specs.md, sealed):
  fo-tracker            0 draws every round
  ngram2 / ngram3       0 draws every round
  wsls-targeter         exactly 1 draw at round 1, 0 thereafter
  switcher-r26 (Order A) 0 draws every round
  shuffled-history      0 draws rounds 1–10; n−2 draws at round n ≥ 11
"""
from __future__ import annotations

import json
import os
import sqlite3
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from phase4_adjudicate import DB_PATH, DOCS, load_phase4_runs

ENGINE = os.environ.get("ENGINE_URL", "http://127.0.0.1:8090")

F_EXPECTED = {
    "fo-tracker": lambda n: 0,
    "ngram2": lambda n: 0,
    "ngram3": lambda n: 0,
    "wsls-targeter": lambda n: 1 if n == 1 else 0,
    "switcher-r26": lambda n: 0,  # Order A (completion amendment §9.1)
    "shuffled-history": lambda n: 0 if n <= 10 else n - 2,
}


def _replay(rid: str) -> dict:
    req = urllib.request.Request(f"{ENGINE}/phase4/llm-runs/{rid}/replay",
                                 method="POST", data=b"")
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read())


def main() -> int:
    runs = load_phase4_runs()
    if os.environ.get("STEP8_PHASE4_ONLY") == "1":
        # capsule/verifier mode: the event store now also holds Phase 5
        # runs (armId prefix 'p5-'), which are audited separately by
        # phase5_replay_audit.py; scope this audit to Phase 4 runs.
        runs = {rid: r for rid, r in runs.items()
                if not str(r.get("armId", "")).startswith("p5-")}
    to_replay, invalids, partials = [], [], []
    for rid, r in runs.items():
        if not r["completed"]:
            partials.append(rid)
        elif r["invalid"]:
            invalids.append(rid)
        else:
            to_replay.append(rid)
    print(f"runs: {len(runs)} total — {len(to_replay)} completed observations, "
          f"{len(invalids)} invalid trials, {len(partials)} provider-failure "
          f"partials (non-observations; not replayed — no run.completed to "
          f"verify against; disclosed by signature)", flush=True)

    failures: list[dict] = []
    done = 0
    t0 = time.time()

    def one(rid: str) -> None:
        nonlocal done
        try:
            rep = _replay(rid)
            if not rep.get("ok") or rep.get("mismatches"):
                failures.append({"runId": rid, "kind": "replay",
                                 "mismatches": rep.get("mismatches"),
                                 "ok": rep.get("ok")})
        except Exception as exc:  # noqa: BLE001 — recorded, fail-closed below
            failures.append({"runId": rid, "kind": "replay-error", "error": str(exc)})
        done += 1
        if done % 250 == 0:
            print(f"  replayed {done}/{len(to_replay) + len(invalids)} "
                  f"({time.time() - t0:.0f}s)", flush=True)

    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(one, to_replay))
        # invalid trials: replay must classify them as invalid, nothing more
        for rid in invalids:
            try:
                rep = _replay(rid)
                if not rep.get("invalidTrial") or not rep.get("ok"):
                    failures.append({"runId": rid, "kind": "invalid-replay",
                                     "report": {k: rep.get(k) for k in
                                                ("ok", "invalidTrial", "mismatches")}})
            except Exception as exc:  # noqa: BLE001
                failures.append({"runId": rid, "kind": "replay-error", "error": str(exc)})

    # F rngCalls profile audit (architect ruling)
    db = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    rng_rows: dict[str, dict[int, int]] = {}
    for rid, n, calls in db.execute(
            """SELECT run_id, json_extract(payload,'$.roundNumber'),
                      json_extract(payload,'$.rngCalls')
               FROM events WHERE type='round.played'"""):
        rng_rows.setdefault(rid, {})[n] = calls
    db.close()
    profile_checked = 0
    for rid, r in runs.items():
        if r.get("block") != "F" or not r["completed"] or r["invalid"]:
            continue
        opp = r["armId"].removeprefix("p4-f-").rsplit("-", 1)[0]
        exp = F_EXPECTED[opp]
        for n in range(1, 51):
            got = rng_rows.get(rid, {}).get(n)
            if got != exp(n):
                failures.append({"runId": rid, "kind": "rng-profile", "opponent": opp,
                                 "round": n, "expected": exp(n), "got": got})
        profile_checked += 1

    doc = {
        "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "engine": ENGINE, "liveCalls": 0,
        "totals": {"runs": len(runs), "replayedObservations": len(to_replay),
                   "invalidTrialsVerified": len(invalids),
                   "partialsSkippedBySignature": len(partials),
                   "fRngProfilesChecked": profile_checked},
        "fRngProfileSpec": {k: ("1 draw at r1, else 0" if k == "wsls-targeter"
                                else "0 for r<=10, n-2 for r>=11" if k == "shuffled-history"
                                else "0 every round") for k in F_EXPECTED},
        "failures": failures,
        "verdict": "CLEAN" if not failures else f"{len(failures)} FAILURES — STOP-ON-ANOMALY",
    }
    with open(os.path.join(DOCS, "step8-replay-audit.json"), "w") as fh:
        json.dump(doc, fh, indent=1)
    lines = ["# Step-8 replay audit", "",
             f"Generated {doc['generatedAt']} — zero live calls; §F.3 extended "
             "replay (bundle-sha byte-compare, request-body-sha recompute, "
             "parsed-action re-derivation, rng draw-count re-verification) "
             "for every completed Phase 4 observation.", "",
             f"- runs in store: {len(runs)}",
             f"- completed observations replayed: {len(to_replay)}",
             f"- invalid trials verified as invalid: {len(invalids)}",
             f"- provider-failure partials (non-observations, signature-verified, "
             f"not replayed): {len(partials)}",
             f"- F rngCalls profiles checked against sealed spec: {profile_checked} runs × 50 rounds",
             "", f"**Verdict: {doc['verdict']}**"]
    if failures:
        lines += ["", "## Failures (first 50)", ""]
        lines += [f"- `{json.dumps(f)}`" for f in failures[:50]]
    with open(os.path.join(DOCS, "step8-replay-audit.md"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    print(doc["verdict"], flush=True)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
