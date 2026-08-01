#!/usr/bin/env python3
"""Lint the living paper surface without touching sealed historical records.

The stale-claim scan applies only to current scientific assertions. Literature
maps, correction ledgers, appendices documenting retired language, and sealed
quotations are link-checked but are not treated as live assertions.
"""
from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Every file here receives relative-link validation.
LIVING = [
    ROOT / "README.md",
    ROOT / "docs/paper/paper-draft.md",
    ROOT / "docs/analysis/INDEX.md",
    ROOT / "docs/analysis/program-synthesis-DRAFT.md",
    ROOT / "docs/analysis/novelty-relationships.md",
    ROOT / "docs/analysis/literature-map.md",
    ROOT / "docs/analysis/propositions.md",
    ROOT / "docs/analysis/hierarchy.md",
    ROOT / "docs/analysis/submission-blockers.md",
]

# Only current assertion-bearing prose is scanned for stale claims. The paper
# appendix is intentionally a historical correction ledger and is excluded.
ASSERTION_FILES = [
    ROOT / "README.md",
    ROOT / "docs/paper/paper-draft.md",
    ROOT / "docs/analysis/program-synthesis-DRAFT.md",
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
    # Restrict the p13/confirmatory pairing to one clause. Long Markdown lines
    # can contain the demotion and an unrelated later use of "confirmatory."
    r"p13[^.!?;]*\bconfirmatory\b": "p13 is a replication target only",
}

LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def relative_link_errors(path: Path) -> list[str]:
    errors: list[str] = []
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


def current_assertion_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if path == ROOT / "docs/paper/paper-draft.md":
        # Appendix A is an explicit cutting-room/correction ledger and contains
        # retired language by design. The sealed quotation in §5.2 is permitted
        # only because the immediately adjacent table corrects it.
        text = text.split("\n## Appendix A", 1)[0]
        text = re.sub(
            r'> "The headline of Phase 5.*?The scope of the claim is deliberately narrow\."',
            "[sealed historical quotation omitted from stale-claim scan]",
            text,
            flags=re.DOTALL,
        )
    return text


def stale_claim_errors() -> list[str]:
    errors: list[str] = []
    for path in ASSERTION_FILES:
        if not path.exists():
            errors.append(f"missing assertion document: {path.relative_to(ROOT)}")
            continue
        text = current_assertion_text(path)
        for lineno, line in enumerate(text.splitlines(), 1):
            for pattern, note in STALE.items():
                if re.search(pattern, line, flags=re.IGNORECASE):
                    errors.append(
                        f"{path.relative_to(ROOT)}:{lineno}: "
                        f"stale phrase /{pattern}/ — {note}"
                    )
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
    return [
        f"sealed/data boundary violation: {path}"
        for path in changed
        if path.startswith(forbidden_prefixes)
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="origin/main")
    args = parser.parse_args()

    errors: list[str] = []
    errors.extend(stale_claim_errors())
    for path in LIVING:
        if not path.exists():
            errors.append(f"missing living document: {path.relative_to(ROOT)}")
        else:
            errors.extend(relative_link_errors(path))
    errors.extend(sealed_boundary_errors(args.base))

    if errors:
        print("paper_submission_lint: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1

    print("paper_submission_lint: PASS")
    print(
        f"checked {len(ASSERTION_FILES)} assertion documents, "
        f"{len(LIVING)} link surfaces, and the sealed-file boundary"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
