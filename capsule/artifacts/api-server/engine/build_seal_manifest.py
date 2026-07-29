"""Build the FULL Phase 5 seal-lint manifest from the sealed arms manifest.

Every arm becomes a lint cell (C1 render at its own bindings), the schedule
lists every cell exactly once (C3 exact coverage), sealedRules carries the
three-layer regex anchors for R1–R3 + attestation gate + shedding (C4), and
the verdict-branch map is inherited from the approved draft (C5).

Run:  cd artifacts/api-server && uv run python engine/build_seal_manifest.py
      then: uv run python engine/freeze_lint.py ../../docs/phase5/lint-manifest.json
"""
from __future__ import annotations

import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.normpath(os.path.join(_HERE, "..", "..", ".."))
P5 = os.path.join(REPO_ROOT, "docs", "phase5")

FRAMING_LINES = {"community": None}  # filled from the sealed template below


def cell_params(arm: dict, registry: dict) -> dict:
    b = arm["bindings"]
    params = {"rr": str(b["rr"]), "rs": str(b["rs"]),
              "rt": str(b["rt"]), "rp": str(b["rp"])}
    if arm.get("deltaPct") is not None:
        params["deltaPct"] = str(arm["deltaPct"])
    if arm["templateId"] == "pd-oneshot-v1":
        params["framingLine"] = registry["prompts"]["pd-oneshot-v1"]["framings"][b["framing"]]
    return params


def main() -> None:
    arms = json.load(open(os.path.join(P5, "arms.json")))
    registry = json.load(open(os.path.join(_HERE, "..", "prompts", "registry.json")))
    draft = json.load(open(os.path.join(P5, "lint-manifest-draft.json")))

    cells = [{"id": a["armId"], "templateId": a["templateId"],
              "params": cell_params(a, registry)} for a in arms["arms"]]

    eng = "../../artifacts/api-server/engine"
    rules = [
        {"id": "R1-persona-composition",
         "statement": 'persona system = preamble + "\\n\\n" + sealed bare system, '
                      "byte-identical; persona sha pinned in arms manifest and "
                      "re-verified per request",
         "layers": {
             "dispatch": {"file": f"{eng}/phase5_runner.py",
                          "pattern": r"compose_persona_system\(llm_cfg\[\"personaPreamble\"\], system\)"},
             "enforcement": {"file": f"{eng}/phase5.py",
                             "pattern": r"R1-persona-composition: arm .* pins persona sha"},
             "replay": {"file": f"{eng}/phase5_runner.py",
                        "pattern": r"R1 replay mirror: re-fetch the persona from the SEALED store"},
         }},
        {"id": "R2-per-T-echo",
         "statement": "request body temperature field must equal the arm's pinned "
                      "temperature on every call, asserted before dispatch",
         "layers": {
             "dispatch": {"file": f"{eng}/phase5_driver.py",
                          "pattern": r"\"temperature\": float\(arm\[\"temperature\"\]\)"},
             "enforcement": {"file": f"{eng}/phase5.py",
                             "pattern": r"def assert_temperature_echo\("},
             "replay": {"file": f"{eng}/phase5_runner.py",
                        "pattern": r"R2: recorded temperature"},
         }},
        {"id": "R3-revision-pin",
         "statement": "returned model revision string must equal the registered pin; "
                      "mismatch aborts (response archived, spend kept)",
         "layers": {
             "dispatch": {"file": f"{eng}/phase5_runner.py",
                          "pattern": r"assert_revision_pin\(llm_cfg\[\"model\"\], response\.to_dict\(\)\.get\(\"model\"\)\)"},
             "enforcement": {"file": f"{eng}/phase5.py",
                             "pattern": r"def assert_revision_pin\("},
             "replay": {"file": f"{eng}/phase5_runner.py",
                        "pattern": r"R3: recorded returned model"},
         }},
        {"id": "sentinel-attestation-gate",
         "statement": "dispatch past a sentinel check requires a POSITIVE evaluator "
                      "attestation; absence of evaluation fail-closes",
         "layers": {
             "dispatch": {"file": f"{eng}/phase5_driver.py",
                          "pattern": r"block dispatch requires evaluator attestation"},
             "enforcement": {"file": f"{eng}/phase5_adjudicate.py",
                             "pattern": r"ATTESTATION REFUSED"},
             "replay": {"file": f"{eng}/phase5_adjudicate.py",
                        "pattern": r"S1 completeness"},
         }},
        {"id": "registered-shedding-only",
         "statement": "cap-binding projections freeze the driver; shedding applies the "
                      "registered order (whole arms, disclosed) — no discretionary "
                      "mid-data call",
         "layers": {
             "dispatch": {"file": f"{eng}/phase5_driver.py",
                          "pattern": r"preflight projection binds"},
             "enforcement": {"file": f"{eng}/phase5.py",
                             "pattern": r"Phase 5 kill-switch at cap for group"},
             "replay": {"file": "freeze-packet-draft.md",
                        "pattern": r"shed"},
         }},
    ]

    manifest = {
        "packet": "phase5-v4-seal",
        "registryPath": draft["registryPath"],
        "runtimeVars": draft["runtimeVars"],
        "cells": cells,
        "schedule": [c["id"] for c in cells],
        "sealedRules": rules,
        "verdictBranches": draft["verdictBranches"],
    }
    out = os.path.join(P5, "lint-manifest.json")
    with open(out, "w") as f:
        json.dump(manifest, f, indent=1)
    print(f"wrote {out}: {len(cells)} cells, {len(rules)} sealed rules")


if __name__ == "__main__":
    main()
