#!/usr/bin/env python3
"""Build the line-numbered v7 reviewer PDF from the living Markdown source."""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER_DIR = ROOT / "docs/paper"
SOURCE = PAPER_DIR / "paper-draft.md"
HEADER = PAPER_DIR / "review-draft-header.tex"
OUTPUT = PAPER_DIR / "synthetic-players-review-draft-v7.pdf"
BUILD_DIR = ROOT / ".review-pdf-build"
BUILD_MD = BUILD_DIR / "synthetic-players-review-draft-v7.md"

TITLE_PREFIX = "# "
FIGURES = (
    "prompt-indexed-delta",
    "condition-means",
    "between-prompt-share",
    "representation-effects",
    "p13-audit",
)


def require(program: str) -> None:
    if shutil.which(program) is None:
        raise RuntimeError(f"required program not found: {program}")


def prepare_markdown() -> str:
    source = SOURCE.read_text(encoding="utf-8")
    lines = source.splitlines()
    if not lines or not lines[0].startswith(TITLE_PREFIX):
        raise RuntimeError("paper source must begin with a level-1 title")
    title = lines[0][len(TITLE_PREFIX):].strip().replace('"', '\\"')
    body = "\n".join(lines[1:]).lstrip()

    for figure in FIGURES:
        pattern = rf"!\[[^\]]*\]\(figures/{re.escape(figure)}\.svg\)"
        replacement = f"![](figures/{figure}.pdf){{width=95%}}"
        body, count = re.subn(pattern, replacement, body, count=1)
        if count != 1:
            raise RuntimeError(f"expected one Markdown image for {figure}, found {count}")

    body = re.sub(r"\n\*End of working draft v7\.\*\s*$", "", body)
    if "\n## References\n" not in body:
        raise RuntimeError("formatted reviewer PDF requires a References section")
    body = body.replace(
        "\n## References\n",
        "\n## References\n\n\\begingroup\n\\small\n\\setlength{\\parskip}{0.35em}\n",
        1,
    )
    body = body.rstrip() + "\n\n\\endgroup\n"

    return f'''---
title: "{title}"
author: "Yohei Nakajima"
date: "July 29, 2026"
lang: en-US
documentclass: article
classoption:
  - 11pt
  - letterpaper
geometry:
  - top=0.78in
  - bottom=0.82in
  - left=0.92in
  - right=0.92in
fontsize: 11pt
linestretch: 1.10
colorlinks: true
linkcolor: "1F4E79"
urlcolor: "1F4E79"
---

{body}'''


def main() -> int:
    for program in ("pandoc", "xelatex", "pdfinfo"):
        require(program)
    for figure in FIGURES:
        figure_pdf = PAPER_DIR / "figures" / f"{figure}.pdf"
        if not figure_pdf.exists():
            raise RuntimeError(f"missing generated figure PDF: {figure_pdf}")

    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    BUILD_MD.write_text(prepare_markdown(), encoding="utf-8")

    cmd = [
        "pandoc",
        str(BUILD_MD),
        "--from=markdown+tex_math_dollars+tex_math_single_backslash+raw_tex",
        "--standalone",
        "--pdf-engine=xelatex",
        f"--include-in-header={HEADER}",
        f"--resource-path={PAPER_DIR}:{ROOT}",
        f"--output={OUTPUT}",
    ]
    subprocess.run(cmd, cwd=ROOT, check=True)
    subprocess.run(["pdfinfo", str(OUTPUT)], cwd=ROOT, check=True)
    print(f"build_review_pdf: wrote {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
