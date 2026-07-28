"""Freeze-time completeness linter (instance-ledger rule 1; process-packet §1).

A seal gate, not a habit: given a machine-readable seal manifest, mechanically
prove that every dispatchable request implied by the sealed text can be
rendered, that every resolution-dependent cell carries an executable rule plus
registered defaults, that the schedule covers every cell including conditional
branches, that every sealed conditional rule exists in all three layers
(dispatch, enforcement, replay), and that a discussion branch exists for every
registered verdict combination. Any failure fails the seal (exit 1).

Usage:
    uv run python engine/freeze_lint.py <manifest.json> [--json <out.json>]

Manifest schema (all paths relative to the manifest file's directory unless
absolute):
{
  "packet": "phase5-draft",
  "registryPath": "prompts/registry.json",
  "runtimeVars": {"seat": "1", "history": "", "round": "1"},   # engine-supplied
  "cells": [
    {"id": "...", "templateId": "...", "params": {...},
     "systemPrefix": "optional persona preamble (composition rule)",
     "conditionalOn": "optional condition label",               # branch cells
     "resolution": {"rule": "prose of the registered rule",
                    "standIns": [{...param sets...}]} | null }  # data-dependent
  ],
  "schedule": ["cellId", ...],          # must cover every cell exactly
  "sealedRules": [
    {"id": "...", "description": "...",
     "layers": {"dispatch":   {"file": "...", "pattern": "regex"},
                "enforcement":{"file": "...", "pattern": "regex"},
                "replay":     {"file": "...", "pattern": "regex"}}}],
  "verdictBranches": {"docPath": "docs/paper/discussion-branches.md",
                       "requiredHeadings": ["## Branch ...", ...],
                       "combinationTable": {"pattern": "regex that must match",
                                             "requiredRows": ["...", ...]}}
}
"""
from __future__ import annotations

import json
import os
import re
import string
import sys
from typing import Any, Optional


class LintFailure:
    def __init__(self, check: str, cell: Optional[str], message: str):
        self.check, self.cell, self.message = check, cell, message

    def as_dict(self) -> dict:
        return {"check": self.check, "cell": self.cell, "message": self.message}


def _placeholders(template: str) -> set[str]:
    out: set[str] = set()
    for _, field, _, _ in string.Formatter().parse(template):
        if field:
            out.add(field.split(".")[0].split("[")[0])
    return out


def _resolve(base_dir: str, path: str) -> str:
    return path if os.path.isabs(path) else os.path.normpath(os.path.join(base_dir, path))


def _render_cell(cell: dict, spec: dict, runtime: dict, params: dict,
                 failures: list[LintFailure], label: str) -> None:
    """C1: end-to-end render — every placeholder in system+user must be pinned
    by sealed params or the registered runtime var set. Missing => seal fail."""
    env = {**runtime, **params}
    for part in ("system", "user"):
        text = spec.get(part)
        if text is None:
            failures.append(LintFailure("C1-render", cell["id"],
                                        f"{label}: template missing '{part}' text"))
            continue
        if cell.get("systemPrefix") and part == "system":
            text = cell["systemPrefix"] + "\n\n" + text
        missing = _placeholders(text) - set(env)
        if missing:
            failures.append(LintFailure(
                "C1-render", cell["id"],
                f"{label}: unpinned placeholder(s) in {part}: {sorted(missing)} — "
                f"sealed text that cannot be rendered is not sealed"))
            continue
        try:
            text.format(**env)
        except Exception as e:  # format-spec errors, index errors
            failures.append(LintFailure("C1-render", cell["id"],
                                        f"{label}: render error in {part}: {e}"))
    if not spec.get("options"):
        failures.append(LintFailure("C1-render", cell["id"],
                                    f"{label}: template has no 'options' (parser undefined)"))


def lint(manifest_path: str) -> dict:
    base = os.path.dirname(os.path.abspath(manifest_path))
    with open(manifest_path) as f:
        m = json.load(f)
    failures: list[LintFailure] = []

    reg_path = _resolve(base, m["registryPath"])
    try:
        reg = json.load(open(reg_path))
        prompts = reg.get("prompts", reg)
    except Exception as e:
        return {"pass": False, "failures": [LintFailure(
            "C0-manifest", None, f"cannot load registry {reg_path}: {e}").as_dict()]}

    runtime = m.get("runtimeVars", {})
    cells = m.get("cells", [])
    cell_ids = [c["id"] for c in cells]
    if len(set(cell_ids)) != len(cell_ids):
        failures.append(LintFailure("C0-manifest", None, "duplicate cell ids"))

    # --- C1 + C2: render every cell, including every conditional branch and
    # every resolution stand-in (never just the expected one).
    for cell in cells:
        spec = prompts.get(cell.get("templateId", ""))
        if not isinstance(spec, dict):
            failures.append(LintFailure(
                "C1-render", cell["id"],
                f"templateId {cell.get('templateId')!r} not found in registry — "
                f"unresolved placeholder template (RESOLVED-BY-* class)"))
            continue
        res = cell.get("resolution")
        if res is None:
            _render_cell(cell, spec, runtime, cell.get("params", {}), failures, "direct")
        else:
            if not res.get("rule") or not str(res.get("rule")).strip():
                failures.append(LintFailure(
                    "C2-resolution", cell["id"],
                    "resolution-dependent cell has no registered resolution rule"))
            stand_ins = res.get("standIns") or []
            if not stand_ins:
                failures.append(LintFailure(
                    "C2-resolution", cell["id"],
                    "resolution-dependent cell has no registered stand-in/default "
                    "parameter sets — the rule cannot be proven executable"))
            for i, si in enumerate(stand_ins):
                _render_cell(cell, spec, runtime,
                             {**cell.get("params", {}), **si}, failures, f"standIn[{i}]")

    # --- C3: schedule coverage (both directions), conditional branches included.
    sched = m.get("schedule", [])
    missing = [c for c in cell_ids if c not in sched]
    unknown = [s for s in sched if s not in cell_ids]
    for c in missing:
        cond = next((x.get("conditionalOn") for x in cells if x["id"] == c), None)
        failures.append(LintFailure(
            "C3-schedule", c,
            f"cell absent from the sealed schedule"
            + (f" (conditional branch {cond!r} — conditional blocks must be "
               f"materialized in the schedule, not remembered)" if cond else "")))
    for s in unknown:
        failures.append(LintFailure("C3-schedule", s, "scheduled id has no sealed cell"))

    # --- C4: three-layer rule — dispatch, enforcement, replay.
    for rule in m.get("sealedRules", []):
        layers = rule.get("layers", {})
        for layer in ("dispatch", "enforcement", "replay"):
            spec = layers.get(layer)
            if not spec:
                failures.append(LintFailure(
                    "C4-three-layer", rule["id"], f"no {layer} anchor registered"))
                continue
            path = _resolve(base, spec["file"])
            if not os.path.exists(path):
                failures.append(LintFailure(
                    "C4-three-layer", rule["id"], f"{layer} file missing: {spec['file']}"))
                continue
            src = open(path, encoding="utf-8", errors="replace").read()
            if not re.search(spec["pattern"], src):
                failures.append(LintFailure(
                    "C4-three-layer", rule["id"],
                    f"sealed rule not found in {layer} layer "
                    f"({spec['file']} !~ /{spec['pattern']}/)"))

    # --- C5: discussion branch for every registered verdict combination.
    vb = m.get("verdictBranches")
    if vb:
        doc = _resolve(base, vb["docPath"])
        if not os.path.exists(doc):
            failures.append(LintFailure("C5-branches", None,
                                        f"branches doc missing: {vb['docPath']}"))
        else:
            text = open(doc, encoding="utf-8").read()
            for h in vb.get("requiredHeadings", []):
                if h not in text:
                    failures.append(LintFailure(
                        "C5-branches", None,
                        f"missing pre-committed branch heading: {h!r} — a registered "
                        f"verdict combination without a written branch fails the seal"))
            ct = vb.get("combinationTable")
            if ct:
                for row in ct.get("requiredRows", []):
                    if not re.search(re.escape(row), text):
                        failures.append(LintFailure(
                            "C5-branches", None,
                            f"verdict combination unmapped in branch table: {row!r}"))
    return {"pass": not failures, "packet": m.get("packet"),
            "cells": len(cells), "rules": len(m.get("sealedRules", [])),
            "failures": [f.as_dict() for f in failures]}


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 2
    out_json = None
    if "--json" in argv:
        i = argv.index("--json")
        out_json = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    result = lint(argv[0])
    text = json.dumps(result, indent=2)
    print(text)
    if out_json:
        with open(out_json, "w") as f:
            f.write(text + "\n")
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
