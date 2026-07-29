#!/usr/bin/env python3
"""Lint the living paper surface without touching sealed historical records."""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

LIVING = [
    ROOT / "README.md",
    ROOT / "docs/paper/paper-draft.md",
    ROOT / "docs/analysis/INDEX.md",
    ROOT / "docs/analysis/program-synthesis-DRAFT.md",
    ROOT / "docs/analysis/novelty-relationships.md",
    ROOT / "docs/analysis/literature-map.md",
    ROOT / "docs/analysis/propositions.md",
    ROOT / "docs/analysis/hierarchy.md",
]

STALE = {
    r"fixed, drift-free": "paired explicit prompts do not establish latent-person invariance",
    r"roughly one-fifth": "N-fold human comparison was retired",
    r"\bone-fifth\b": "N-fold human comparison was retired",
    r"\bfivefold\b": "N-fold human comparison was retired",
    r"\b5×\b": "N-fold human comparison was retired",
    r"not payoff-determined": "use representation-dependent or conditional semantic dominance",
    r"pending a higher-precision family audit": "the final 200,000-permutation audit is complete",
    r"episode-clustered sensitivity (?:is|remains) (?:a )?submission blocker": "episode-level sensitivity is complete",
    r"≈30,500 recorded subject calls": "use reconciled request/call counts and exact scope",
    r"program's only registered incentive-transmission pass": "p13 does not survive exact episode inference",
    r"p13 .*confirmatory": "p13 is a replication target only",
}

LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def relative_link_errors(path: Path) -> list[str]:
    errors = []
    text = path.read_text(encoding="utf-8")
    for match in LINK_RE.finditer(text):
        target = match.group(1).strip()
        if not target or target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        target = target.split("#", 1)[0]
        if not target:
            continue
        resolved = (path.parent / target).resolve()
        try:
            resolved.relative_to(ROOT.resolve())
        except ValueError:
            errors.append(f"{path.relative_to(ROOT)}: link escapes repo: {target}")
            continue
        if not resolved.exists():
            line = text.count("\n", 0, match.start()) + 1
            errors.append(f"{path.relative_to(ROOT)}:{line}: missing link target {target}")
    return errors


def stale_claim_errors() -> list[str]:
    errors = []
    for path in LIVING:
        if not path.exists():
            errors.append(f"missing living document: {path.relative_to(ROOT)}")
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            for pattern, note in STALE.items():
                if re.search(pattern, line, flags=re.IGNORECASE):
                    errors.append(f"{path.relative_to(ROOT)}:{lineno}: stale phrase /{pattern}/ — {note}")
    return errors


def sealed_boundary_errors(base: str) -> list[str]:
    proc = subprocess.run(
        ["git", "diff", "--name-only", f"{base}...HEAD"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    changed = [x.strip() for x in proc.stdout.splitlines() if x.strip()]
    forbidden_prefixes = (
        "docs/phase3",
        "docs/phase4/",
        "docs/phase5/",
        "docs/phase5-close/",
        "docs/v1/",
        "capsule/data/",
        "artifacts/api-server/engine/data/",
    )
    return [f"sealed/data boundary violation: {p}" for p in changed if p.startswith(forbidden_prefixes)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="origin/main")
    args = ap.parse_args()

    errors = []
    errors.extend(stale_claim_errors())
    for path in LIVING + [ROOT / "docs/analysis/submission-blockers.md"]:
        if path.exists():
            errors.extend(relative_link_errors(path))
    errors.extend(sealed_boundary_errors(args.base))

    if errors:
        print("paper_submission_lint: FAIL")
        for err in errors:
            print(f"- {err}")
        return 1
    print("paper_submission_lint: PASS")
    print(f"checked {len(LIVING)} living documents, relative links, and sealed-file boundary")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
