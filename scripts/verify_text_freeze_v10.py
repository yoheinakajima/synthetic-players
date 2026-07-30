#!/usr/bin/env python3
"""Verify that the living manuscript exactly matches the declared v10 source commit."""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FREEZE = ROOT / "docs/paper/text-freeze-v10.json"
SOURCE = ROOT / "docs/paper/paper-draft.md"


def main() -> int:
    record = json.loads(FREEZE.read_text(encoding="utf-8"))
    commit = record["source_commit"]
    path = record["source_path"]
    frozen = subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=ROOT)
    current = SOURCE.read_bytes()
    if frozen != current:
        raise RuntimeError(
            "text-freeze violation: current manuscript differs from "
            f"{commit}:{path}"
        )
    digest = hashlib.sha256(current).hexdigest()
    print(f"verify_text_freeze_v10: PASS source={commit} sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
