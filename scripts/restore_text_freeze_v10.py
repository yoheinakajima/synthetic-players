#!/usr/bin/env python3
"""Restore the living manuscript byte-for-byte from the declared v10 source commit.

Earlier historical integration scripts are retained for reproducibility and may rewrite the
living manuscript while regenerating other reviewer surfaces. This final step makes the
text freeze authoritative before verification and PDF construction.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FREEZE = ROOT / "docs/paper/text-freeze-v10.json"
PAPER = ROOT / "docs/paper/paper-draft.md"


def main() -> int:
    record = json.loads(FREEZE.read_text(encoding="utf-8"))
    commit = record["source_commit"]
    path = record["source_path"]
    frozen = subprocess.check_output(["git", "show", f"{commit}:{path}"], cwd=ROOT)
    PAPER.write_bytes(frozen)
    print(f"restore_text_freeze_v10: restored {commit}:{path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
