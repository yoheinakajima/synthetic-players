#!/usr/bin/env python3
"""Finalize v8 status prose after the independent repository review integration."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "docs" / "paper" / "paper-draft.md"


def main() -> int:
    text = PAPER.read_text(encoding="utf-8")
    old = (
        "This revision incorporates the completed zero-call submission analyses, direct outside "
        "reproduction of the 4,576-run capsule, and Round 4 editorial review."
    )
    new = (
        "This revision incorporates the completed zero-call submission analyses, direct outside "
        "reproduction of the 4,576-run capsule, the Explore Science Round 5 corrections, and an "
        "independent repository review of v7."
    )
    if new not in text:
        if old not in text:
            raise RuntimeError("missing expected v8 revision-summary sentence")
        text = text.replace(old, new, 1)
    PAPER.write_text(text, encoding="utf-8")
    print("finalize_v8_headers: aligned v8 status prose")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
