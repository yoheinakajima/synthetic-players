#!/usr/bin/env python3
"""Zero-call replay audit for the complete Phase 3 confirmatory record.

The public capsule historically replayed Phase 4 and Phase 5 only, even though
Phase 3 was prospectively registered and supplies several instrument anchors.
This audit closes that gap using the generic Phase 3 replay implementation
(`llm_runner.replay_llm`) already used by the original study runner.

It verifies:
- all 320 completed Phase 3/X1 LLM runs, with zero live calls;
- prompt-by-prompt reconstruction, raw-response cache hits, parsed actions,
  payoffs, RNG draw counts, and recorded call counts;
- the 20 zero-LLM pattern-tracker-vs-Nash baseline runs by independent
  deterministic recomputation from the archived game object and seed.

Read-only against the archived event store. Any mismatch exits nonzero.
"""
from __future__ import annotations

import json
import os
import sqlite3
import sys
import time
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from activegraph import Runtime  # noqa: E402
from engine import Engine  # noqa: E402
from llm_runner import replay_llm  # noqa: E402
from strategies import CountingRng, get_action  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
DB_PATH = os.path.join(HERE, "data", "engine.db")
OUT = os.path.join(REPO, "docs", "analysis", "submission", "v12")

PHASE3_PROMPTS = {
    "pd-repeated-v1": 160,
    "pd-oneshot-v1": 60,
    "rps-v1": 60,
    "pd-repeated-v2a": 20,
    "pd-repeated-v2b": 20,
}
EXPECTED_LLM_RUNS = sum(PHASE3_PROMPTS.values())
EXPECTED_BASELINE_RUNS = 20


def discover_llm_runs() -> tuple[list[str], Counter]:
    db = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    rows = db.execute(
        """SELECT run_id, payload FROM events
           WHERE type='llm.requested' ORDER BY rowid"""
    )
    by_run: dict[str, dict] = {}
    for rid, payload in rows:
        p = json.loads(payload)
        # Phase 4/5 requests carry an armId. The Phase 3 event shape does not.
        if p.get("armId") is not None:
            continue
        prompt_id = p.get("promptId")
        if prompt_id not in PHASE3_PROMPTS:
            continue
        rec = by_run.setdefault(rid, {"promptId": prompt_id, "models": set()})
        if rec["promptId"] != prompt_id:
            raise AssertionError(f"{rid}: multiple promptIds in one Phase 3 run")
        rec["models"].add(p.get("model"))
    completed = {
        rid for (rid,) in db.execute("SELECT DISTINCT run_id FROM events WHERE type='run.completed'")
    }
    invalid = {
        rid for (rid,) in db.execute("SELECT DISTINCT run_id FROM events WHERE type='trial.invalidated'")
    }
    db.close()

    targets = []
    counts: Counter = Counter()
    for rid, rec in sorted(by_run.items()):
        if rec["models"] != {"gpt-4.1"}:
            raise AssertionError(f"{rid}: unexpected model set {rec['models']}")
        if rid in invalid:
            raise AssertionError(f"{rid}: Phase 3 audit unexpectedly found invalid trial")
        if rid not in completed:
            raise AssertionError(f"{rid}: Phase 3 LLM run lacks run.completed")
        targets.append(rid)
        counts[rec["promptId"]] += 1

    if len(targets) != EXPECTED_LLM_RUNS:
        raise AssertionError(f"Phase 3 LLM run count {len(targets)} != expected {EXPECTED_LLM_RUNS}")
    if dict(counts) != PHASE3_PROMPTS:
        raise AssertionError(f"Phase 3 prompt counts {dict(counts)} != expected {PHASE3_PROMPTS}")
    return targets, counts


def discover_baselines() -> list[str]:
    db = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    llm_runs = {
        rid for (rid,) in db.execute("SELECT DISTINCT run_id FROM events WHERE type='llm.requested'")
    }
    completed = {
        rid for (rid,) in db.execute("SELECT DISTINCT run_id FROM events WHERE type='run.completed'")
    }
    rounds: dict[str, list[dict]] = defaultdict(list)
    for rid, payload in db.execute(
        "SELECT run_id, payload FROM events WHERE type='round.played' ORDER BY rowid"
    ):
        p = json.loads(payload)
        if (
            p.get("strategy1Slug") == "pattern-tracker"
            and p.get("strategy2Slug") == "nash-mixed"
        ):
            rounds[rid].append(p)
    db.close()
    targets = [
        rid
        for rid, rs in sorted(rounds.items())
        if rid not in llm_runs and rid in completed and len(rs) == 50
    ]
    if len(targets) != EXPECTED_BASELINE_RUNS:
        raise AssertionError(
            f"Phase 3 zero-LLM baseline count {len(targets)} != expected {EXPECTED_BASELINE_RUNS}"
        )
    return targets


def verify_baseline(engine: Engine, run_id: str) -> list[str]:
    rt = Runtime.load(engine.url, run_id=run_id)
    graph = rt.graph
    game_obj = next(iter(graph.objects("game")), None)
    if game_obj is None:
        return ["missing game object"]
    g = game_obj.data
    if (g.get("strategy1Slug"), g.get("strategy2Slug")) != (
        "pattern-tracker",
        "nash-mixed",
    ):
        return [f"unexpected strategies {g.get('strategy1Slug')}/{g.get('strategy2Slug')}"]
    stored = sorted((o.data for o in graph.objects("round")), key=lambda x: x["roundNumber"])
    if len(stored) != 50:
        return [f"stored rounds {len(stored)} != 50"]

    history: list[dict] = []
    consumed = 0
    mismatches: list[str] = []
    game_def = g["gameDef"]
    for n, observed in enumerate(stored, 1):
        rng = CountingRng(g["seed"], advance=consumed)
        a1, _ = get_action("pattern-tracker", history, 1, game_def, rng)
        a2, _ = get_action("nash-mixed", history, 2, game_def, rng)
        p1, p2 = game_def["payoffMatrix"][a1][a2]
        if (a1, a2) != (observed["player1Action"], observed["player2Action"]):
            mismatches.append(
                f"round {n}: actions {(a1, a2)} != {(observed['player1Action'], observed['player2Action'])}"
            )
        if (p1, p2) != (observed["player1Payoff"], observed["player2Payoff"]):
            mismatches.append(
                f"round {n}: payoffs {(p1, p2)} != {(observed['player1Payoff'], observed['player2Payoff'])}"
            )
        if rng.calls != observed.get("rngCalls", 0):
            mismatches.append(
                f"round {n}: rngCalls {rng.calls} != {observed.get('rngCalls', 0)}"
            )
        consumed += rng.calls
        history.append(
            {
                "p1Action": observed["player1Action"],
                "p2Action": observed["player2Action"],
                "p1Payoff": observed["player1Payoff"],
                "p2Payoff": observed["player2Payoff"],
            }
        )
    return mismatches


def main() -> int:
    os.makedirs(OUT, exist_ok=True)
    engine = Engine(DB_PATH)
    llm_runs, prompt_counts = discover_llm_runs()
    baseline_runs = discover_baselines()

    failures: list[dict] = []
    totals = {
        "llmRuns": len(llm_runs),
        "llmRunsOk": 0,
        "recordedLlmCalls": 0,
        "llmCallsVerified": 0,
        "roundsCompared": 0,
        "baselineRuns": len(baseline_runs),
        "baselineRunsOk": 0,
        "baselineRoundsCompared": 0,
    }
    t0 = time.time()
    for i, rid in enumerate(llm_runs, 1):
        try:
            rep = replay_llm(engine, rid)
        except Exception as exc:  # fail-closed audit
            failures.append({"runId": rid, "kind": "replay-error", "error": str(exc)})
            continue
        totals["recordedLlmCalls"] += int(rep.get("recordedLlmCalls", 0))
        totals["llmCallsVerified"] += int(rep.get("llmCallsVerified", 0))
        totals["roundsCompared"] += int(rep.get("roundsCompared", 0))
        if rep.get("ok") and rep.get("liveCalls") == 0 and not rep.get("invalidTrial"):
            totals["llmRunsOk"] += 1
        else:
            failures.append(
                {
                    "runId": rid,
                    "kind": "llm-replay",
                    "ok": rep.get("ok"),
                    "liveCalls": rep.get("liveCalls"),
                    "invalidTrial": rep.get("invalidTrial"),
                    "mismatches": rep.get("mismatches", [])[:10],
                }
            )
        if i % 50 == 0:
            print(f"phase3 LLM replay {i}/{len(llm_runs)} ({time.time() - t0:.0f}s)", flush=True)

    for rid in baseline_runs:
        mismatches = verify_baseline(engine, rid)
        totals["baselineRoundsCompared"] += 50
        if mismatches:
            failures.append(
                {"runId": rid, "kind": "zero-llm-baseline", "mismatches": mismatches[:10]}
            )
        else:
            totals["baselineRunsOk"] += 1

    verdict = "PASS — CLEAN" if not failures else f"FAIL — {len(failures)} failures"
    report = {
        "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "verdict": verdict,
        "scope": "Phase 3 main study plus X1 and the P3-C3 zero-LLM baseline",
        "expectedPromptCounts": PHASE3_PROMPTS,
        "observedPromptCounts": dict(prompt_counts),
        "totals": totals,
        "checks": [
            "zero live calls by construction",
            "prompt re-render and recorded-cache hash hit",
            "raw completion re-parse",
            "action and payoff recomputation",
            "RNG draw-count verification",
            "recorded request count parity",
            "deterministic pattern-tracker-vs-Nash baseline recomputation",
        ],
        "failures": failures,
    }
    with open(os.path.join(OUT, "phase3-replay-audit.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
        f.write("\n")
    lines = [
        "# Phase 3 zero-call replay audit",
        "",
        f"- Generated: {report['generatedAt']}",
        f"- **Verdict: {verdict}**",
        f"- LLM runs replayed: {totals['llmRuns']} (clean {totals['llmRunsOk']})",
        f"- LLM calls byte/prompt/action verified: {totals['llmCallsVerified']}/{totals['recordedLlmCalls']}",
        f"- LLM-run rounds compared: {totals['roundsCompared']}",
        f"- Zero-LLM baseline runs independently recomputed: {totals['baselineRunsOk']}/{totals['baselineRuns']} ({totals['baselineRoundsCompared']} rounds)",
        "",
        "| prompt | completed runs |",
        "|---|---:|",
    ]
    for prompt, count in sorted(prompt_counts.items()):
        lines.append(f"| `{prompt}` | {count} |")
    lines += [
        "",
        "This closes the former capsule boundary: all prospectively confirmatory Phase 3 LLM runs, the result-informed but prospectively registered X1 runs, and the deterministic P3-C3 baseline are now covered by a public zero-call verifier.",
    ]
    if failures:
        lines += ["", "## Failures", ""]
        lines += [f"- `{json.dumps(x)}`" for x in failures[:50]]
    with open(os.path.join(OUT, "phase3-replay-audit.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(verdict)
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
