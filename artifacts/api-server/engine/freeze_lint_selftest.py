"""Acceptance test for the freeze-time completeness linter.

Registered acceptance criterion (process-packet §1): the linter must
reproduce the five Phase 4 sealed-text underspecification instances as seal
failures. Each fixture below is a minimal reconstruction of the failure
condition as it existed in the frozen Phase 4 material, expressed in the
manifest format the Phase 5 seal will use, rendered against the REAL sealed
prompt registry (prompts/registry.json) — not synthetic templates.

  A1 (ledger #10, sealed-text instance 1 — E-dselected registration gap):
     resolution-dependent cell sealed with NO selection rule.
  A2 (sealed-text instance 2 — sentinel third-cell switch absent from
     enforcement/dispatch): sealed conditional rule whose anchor is missing
     from a required layer (three-layer check).
  A3 (ledger #11, instance 3 — X2-confirmation schedule gap): conditional
     confirmation cell absent from the generated schedule.
  A4 (ledger #12, instance 4 — RESOLVED-BY-* dispatch gap): cell whose
     templateId is an unresolved placeholder, not a registry entry.
  A5 (ledger #15, instance 5 — sentinel-switch deltaPct pin): switched cell
     renders a pd-rep template but no sealed text pins `deltaPct`.

  A6: a fully specified control manifest must PASS (no false positives).

Exit 0 iff A1–A5 all FAIL with the expected check class and A6 PASSES.

Usage: uv run python engine/freeze_lint_selftest.py
"""
from __future__ import annotations

import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from freeze_lint import lint  # noqa: E402

ENGINE = os.path.dirname(os.path.abspath(__file__))
REGISTRY = os.path.join(ENGINE, "..", "prompts", "registry.json")

RUNTIME = {"seat": "1", "history": "(none)", "round": "1"}
PD_PARAMS = {"rr": "3", "rs": "0", "rt": "5", "rp": "1"}


def _pd_rep_params() -> dict:
    """Full pinned param set for the sealed pd-rep template, derived from the
    real registry so the control fixture renders byte-for-byte."""
    reg = json.load(open(REGISTRY))
    prompts = reg.get("prompts", reg)
    spec = prompts["pd-rep-w1-neu-cf-ad"]
    import string
    fields = set()
    for part in ("system", "user"):
        for _, f, _, _ in string.Formatter().parse(spec[part]):
            if f:
                fields.add(f.split(".")[0].split("[")[0])
    params = dict(PD_PARAMS)
    for f in fields - set(RUNTIME) - set(params):
        params[f] = "10"  # any pinned literal proves renderability
    return params


def _manifest(**over) -> dict:
    full = _pd_rep_params()
    base = {
        "packet": "selftest",
        "registryPath": os.path.relpath(REGISTRY, tempfile.gettempdir()),
        "runtimeVars": RUNTIME,
        "cells": [{"id": "cell-a", "templateId": "pd-rep-w1-neu-cf-ad",
                   "params": full, "resolution": None}],
        "schedule": ["cell-a"],
        "sealedRules": [],
        "verdictBranches": None,
    }
    base.update(over)
    return base


def _run(m: dict) -> dict:
    fd, path = tempfile.mkstemp(suffix=".json", dir=tempfile.gettempdir())
    with os.fdopen(fd, "w") as f:
        json.dump(m, f)  # keep explicit nulls: absence vs null is meaningful (C0)
    try:
        return lint(path)
    finally:
        os.unlink(path)


def main() -> int:
    full = _pd_rep_params()
    results = []

    # A1 — resolution-dependent cell with no rule and no stand-ins.
    r = _run(_manifest(cells=[{"id": "e-dselected", "templateId": "pd-rep-w1-neu-cf-ad",
                               "params": full,
                               "resolution": {"rule": "", "standIns": []}}],
                       schedule=["e-dselected"]))
    results.append(("A1 E-dselected registration gap", not r["pass"] and
                    any(f["check"] == "C2-resolution" for f in r["failures"]), r))

    # A2 — sealed conditional rule missing from the replay layer.
    r = _run(_manifest(sealedRules=[{
        "id": "sentinel-third-cell-switch",
        "description": "on alert-5 re-baseline, third sentinel cell switches template",
        "layers": {
            "dispatch": {"file": os.path.join(ENGINE, "phase4_driver.py"),
                          "pattern": "SENTINEL"},
            "enforcement": {"file": os.path.join(ENGINE, "phase4.py"),
                             "pattern": "sentinel"},
            "replay": {"file": os.path.join(ENGINE, "phase4.py"),
                        "pattern": "THIS_ANCHOR_DOES_NOT_EXIST_ANYWHERE_XYZZY"},
        }}]))
    results.append(("A2 rule absent from a layer (three-layer)", not r["pass"] and
                    any(f["check"] == "C4-three-layer" for f in r["failures"]), r))

    # A3 — conditional confirmation cell not in the schedule.
    r = _run(_manifest(cells=[
        {"id": "x2-screen", "templateId": "pd-rep-w1-neu-cf-ad", "params": full},
        {"id": "x2-confirm", "templateId": "pd-rep-w1-neu-cf-ad", "params": full,
         "conditionalOn": "screening yields a candidate span"}],
        schedule=["x2-screen"]))
    results.append(("A3 conditional block missing from schedule", not r["pass"] and
                    any(f["check"] == "C3-schedule" and f["cell"] == "x2-confirm"
                        for f in r["failures"]), r))

    # A4 — unresolved RESOLVED-BY-* placeholder template.
    r = _run(_manifest(cells=[{"id": "resolved-arm",
                               "templateId": "RESOLVED-BY-E-SELECTION",
                               "params": full}],
                       schedule=["resolved-arm"]))
    results.append(("A4 RESOLVED-BY-* dispatch gap", not r["pass"] and
                    any(f["check"] == "C1-render" for f in r["failures"]), r))

    # A5 — switched cell with a required template parameter unpinned.
    missing_one = {k: v for k, v in full.items()}
    dropped = next(k for k in missing_one if k not in PD_PARAMS)
    del missing_one[dropped]
    r = _run(_manifest(cells=[{"id": "sentinel-switched",
                               "templateId": "pd-rep-w1-neu-cf-ad",
                               "params": missing_one}],
                       schedule=["sentinel-switched"]))
    results.append((f"A5 unpinned template parameter ({dropped})", not r["pass"] and
                    any(f["check"] == "C1-render" and dropped in f["message"]
                        for f in r["failures"]), r))

    # A6 — control: fully specified manifest passes.
    r = _run(_manifest())
    results.append(("A6 control PASS (no false positives)", r["pass"], r))

    # A7 — empty/structurally incomplete manifest must FAIL (fail-closed shape).
    r = _run({"packet": "selftest",
              "registryPath": os.path.relpath(REGISTRY, tempfile.gettempdir()),
              "cells": [], "schedule": []})
    results.append(("A7 empty manifest fails closed", not r["pass"] and
                    any(f["check"] == "C0-manifest" for f in r["failures"]), r))

    # A8 — duplicate schedule entries must FAIL (exact coverage).
    r = _run(_manifest(schedule=["cell-a", "cell-a"]))
    results.append(("A8 duplicate schedule entries fail", not r["pass"] and
                    any(f["check"] == "C3-schedule" and "duplicate" in f["message"]
                        for f in r["failures"]), r))

    ok = True
    for name, passed, r in results:
        print(f"{'PASS' if passed else 'FAIL'}  {name}")
        if not passed:
            ok = False
            print(json.dumps(r, indent=2))
    print(f"\nacceptance: {'PASS 8/8' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
