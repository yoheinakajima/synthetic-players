#!/usr/bin/env python3
"""Build a clean, text-native near-arXiv PDF from the v12 manuscript."""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "docs" / "paper"
SOURCE = PAPER / "paper-draft.md"
HEADER = PAPER / "preprint-v12-header.tex"
OUTPUT = PAPER / "synthetic-players-preprint-v12.pdf"
SHA_FILE = PAPER / "synthetic-players-preprint-v12.sha256"
MANIFEST = PAPER / "synthetic-players-preprint-v12-artifact.json"
BUILD = ROOT / ".preprint-v12-build"
BUILD_MD = BUILD / "synthetic-players-preprint-v12.md"
FIGURES = (
    "prompt-indexed-delta",
    "condition-means",
    "between-prompt-share",
    "representation-effects",
    "p13-audit",
)


def require(name: str) -> None:
    if shutil.which(name) is None:
        raise RuntimeError(f"required program not found: {name}")


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def prepare() -> tuple[str, str]:
    source = SOURCE.read_text(encoding="utf-8")
    lines = source.splitlines()
    if not lines or not lines[0].startswith("# "):
        raise RuntimeError("manuscript must begin with a level-1 title")
    title = lines[0][2:].strip().replace('"', '\\"')
    body = "\n".join(lines[1:]).lstrip()
    body = re.sub(r"^\*\*Preprint v12.*?\n\n", "", body, count=1, flags=re.DOTALL)
    for figure in FIGURES:
        pattern = rf"!\[[^\]]*\]\(figures/{re.escape(figure)}\.svg\)"
        body, count = re.subn(
            pattern,
            f"![](figures/{figure}.pdf){{width=95%}}",
            body,
            count=1,
        )
        if count != 1:
            raise RuntimeError(f"expected one figure reference for {figure}, got {count}")
    if "\n## References\n" not in body:
        raise RuntimeError("References section missing")
    body = body.replace(
        "\n## References\n",
        "\n## References\n\n\\begingroup\n\\small\n\\setlength{\\parskip}{0.32em}\n",
        1,
    )
    body = body.rstrip() + "\n\n\\endgroup\n"
    return title, body


def main() -> int:
    for program in ("pandoc", "xelatex", "pdfinfo", "pdftotext"):
        require(program)
    for figure in FIGURES:
        if not (PAPER / "figures" / f"{figure}.pdf").is_file():
            raise RuntimeError(f"missing figure PDF {figure}")

    title, body = prepare()
    BUILD.mkdir(parents=True, exist_ok=True)
    markdown = f'''---
title: "{title}"
author: "Yohei Nakajima · Untapped Capital"
date: "July 2026"
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
    BUILD_MD.write_text(markdown, encoding="utf-8")
    subprocess.run(
        [
            "pandoc",
            str(BUILD_MD),
            "--from=markdown+tex_math_dollars+tex_math_single_backslash+raw_tex",
            "--standalone",
            "--pdf-engine=xelatex",
            f"--include-in-header={HEADER}",
            f"--resource-path={PAPER}:{ROOT}",
            f"--output={OUTPUT}",
        ],
        cwd=ROOT,
        check=True,
    )
    info = subprocess.check_output(["pdfinfo", str(OUTPUT)], cwd=ROOT, text=True)
    pages = int(next(x.split(":", 1)[1].strip() for x in info.splitlines() if x.startswith("Pages:")))
    digest = hashlib.sha256(OUTPUT.read_bytes()).hexdigest()
    SHA_FILE.write_text(f"{digest}  {OUTPUT.name}\n", encoding="utf-8")
    record = {
        "repository": "yoheinakajima/synthetic-players",
        "source_commit": git("rev-parse", "HEAD"),
        "source": "docs/paper/paper-draft.md",
        "pdf": "docs/paper/synthetic-players-preprint-v12.pdf",
        "pdf_sha256": digest,
        "pages": pages,
        "workflow_run": os.environ.get("GITHUB_RUN_ID", "local"),
        "status": "near-arXiv preprint candidate v12",
    }
    MANIFEST.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print(info)
    print(f"build_preprint_pdf_v12: sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
