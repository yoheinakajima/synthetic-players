"""Phase 5 close-out replay audit — R1–R3 re-derivation over ALL recorded
Phase 5 runs. Read-only against the event store, zero live calls.

For every run whose recorded llm config carries a Phase 5 armId (block P5*),
invokes replay_llm_p5 in-process (the same function behind
POST /phase5/llm-runs/{id}/replay): byte-exact bundle-sha and request-body-sha
recompute, parsed-action re-derivation, R1 persona composition re-derived
from the SEALED persona store, R2/R2e temperature pins (run-level and
per-recorded-request), R3/R3e revision pins (per llm.responded and per
llm.requested), substitution re-derivation from arm bindings.

Any mismatch on any run ⇒ exit 1 (byte-exact or stop — close-out rule).

Run:  cd artifacts/api-server && uv run python engine/phase5_replay_audit.py
Outputs: docs/phase5-close/replay-audit.json + replay-audit.md
"""
from __future__ import annotations

import json
import os
import sqlite3
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.normpath(os.path.join(_HERE, "..", "..", ".."))
DB_PATH = os.path.join(_HERE, "data", "engine.db")
OUT_DIR = os.path.join(REPO_ROOT, "docs", "phase5-close")


def main() -> int:
    from engine import Engine  # same import path server.py uses
    from phase5 import ArmStoreP5, PersonaStore
    from phase5_runner import replay_llm_p5

    engine = Engine(DB_PATH)
    store = ArmStoreP5()
    personas = PersonaStore()  # re-verifies every preamble sha at load (R1)

    db = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    rows = db.execute(
        "SELECT DISTINCT run_id, json_extract(payload,'$.armId'), "
        "json_extract(payload,'$.block') FROM events "
        "WHERE type='llm.requested' AND json_extract(payload,'$.block') LIKE 'P5%'")
    targets = [(rid, arm_id, block) for rid, arm_id, block in rows]
    db.close()
    targets.sort()
    print(f"phase5 replay audit: {len(targets)} runs")

    t0 = time.time()
    per_block: dict[str, dict] = {}
    failures: list[dict] = []
    totals = {"runs": 0, "ok": 0, "invalidTrials": 0, "llmCallsVerified": 0,
              "bundleShasVerified": 0, "requestBodyShasVerified": 0,
              "parsedActionsVerified": 0, "recordedLlmCalls": 0}

    for i, (rid, arm_id, block) in enumerate(targets, 1):
        rep = replay_llm_p5(engine, rid, store=store, personas=personas)
        totals["runs"] += 1
        b = per_block.setdefault(block, {"runs": 0, "ok": 0, "invalidTrials": 0,
                                         "callsVerified": 0})
        b["runs"] += 1
        totals["recordedLlmCalls"] += rep.get("recordedLlmCalls", 0)
        if rep.get("invalidTrial"):
            totals["invalidTrials"] += 1
            b["invalidTrials"] += 1
        if rep["ok"]:
            totals["ok"] += 1
            b["ok"] += 1
        else:
            failures.append({"engineRunId": rid, "armId": arm_id, "block": block,
                             "mismatches": rep["mismatches"]})
        for k in ("llmCallsVerified", "bundleShasVerified",
                  "requestBodyShasVerified", "parsedActionsVerified"):
            totals[k] += rep.get(k, 0)
        b["callsVerified"] += rep.get("llmCallsVerified", 0)
        if i % 250 == 0 or i == len(targets):
            print(f"  {i}/{len(targets)}  ok={totals['ok']} "
                  f"failures={len(failures)}  ({time.time() - t0:.0f}s)")

    verdict = "PASS — CLEAN" if not failures else "FAIL"
    report = {
        "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "verdict": verdict,
        "totals": totals,
        "perBlock": dict(sorted(per_block.items())),
        "failures": failures,
        "checks": ["bundleSha256 byte-recompute", "requestBodySha256 recompute",
                   "parsed-action re-derivation", "R1 persona re-composition from sealed store",
                   "R2 run-level + R2e per-request temperature pin",
                   "R3 per-response + R3e per-request model/revision pin",
                   "substitution re-derivation from arm bindings",
                   "template sha vs sealed manifest"],
        "liveCalls": 0,
    }
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "replay-audit.json"), "w") as f:
        json.dump(report, f, indent=2)

    lines = [
        "# Phase 5 close-out replay audit", "",
        f"- Generated: {report['generatedAt']}  ·  live calls: 0",
        f"- **Verdict: {verdict}**",
        f"- Runs replayed: {totals['runs']} (ok {totals['ok']}, "
        f"invalid-trial runs {totals['invalidTrials']}, failures {len(failures)})",
        f"- Recorded LLM calls: {totals['recordedLlmCalls']}; byte-verified "
        f"{totals['llmCallsVerified']} (bundle shas {totals['bundleShasVerified']}, "
        f"request-body shas {totals['requestBodyShasVerified']}, parsed actions "
        f"{totals['parsedActionsVerified']})", "",
        "| block | runs | ok | invalid trials | calls verified |", "|---|---|---|---|---|",
    ]
    for blk, b in sorted(per_block.items()):
        lines.append(f"| {blk} | {b['runs']} | {b['ok']} | {b['invalidTrials']} | "
                     f"{b['callsVerified']} |")
    if failures:
        lines += ["", "## Failures", ""]
        for fl in failures[:50]:
            lines.append(f"- `{fl['engineRunId']}` {fl['armId']} ({fl['block']}): "
                         + "; ".join(fl["mismatches"][:5]))
    lines += ["", "Checks: " + "; ".join(report["checks"]) + ".", ""]
    with open(os.path.join(OUT_DIR, "replay-audit.md"), "w") as f:
        f.write("\n".join(lines))

    print(f"replay audit: {verdict}  → docs/phase5-close/replay-audit.{{json,md}}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
