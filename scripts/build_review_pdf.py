#!/usr/bin/env python3
"""Build the line-numbered v10 text-freeze reviewer PDF."""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER_DIR = ROOT / "docs/paper"
SOURCE = PAPER_DIR / "paper-draft.md"
HEADER = PAPER_DIR / "review-draft-header.tex"
FREEZE_RECORD = PAPER_DIR / "text-freeze-v10.json"
OUTPUT = PAPER_DIR / "synthetic-players-review-v10.pdf"
SHA_FILE = PAPER_DIR / "synthetic-players-review-v10.sha256"
MANIFEST = PAPER_DIR / "synthetic-players-review-v10-artifact.json"
SUMMARY = ROOT / "docs/analysis/submission/submission-analysis-summary.json"
BUILD_DIR = ROOT / ".review-pdf-build"
BUILD_MD = BUILD_DIR / "synthetic-players-review-v10.md"

TITLE_PREFIX = "# "
SOURCE_DATE_EPOCH = "1785369600"  # 2026-07-30T00:00:00Z
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


def git_text(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def artifact_identity() -> dict[str, str]:
    freeze = json.loads(FREEZE_RECORD.read_text(encoding="utf-8"))
    branch = os.environ.get("GITHUB_HEAD_REF") or os.environ.get("GITHUB_REF_NAME") or git_text("branch", "--show-current")
    run_id = os.environ.get("GITHUB_RUN_ID", "local")
    run_url = (
        f"https://github.com/yoheinakajima/synthetic-players/actions/runs/{run_id}"
        if run_id.isdigit()
        else "local build"
    )
    return {
        "repository": "yoheinakajima/synthetic-players",
        "branch": branch,
        "source_commit": freeze["source_commit"],
        "freeze_tag": freeze["intended_tag"],
        "workflow_run": run_id,
        "workflow_url": run_url,
        "build_commit": git_text("rev-parse", "HEAD"),
        "manuscript": freeze["source_path"],
        "freeze_scope": freeze["freeze_scope_path"],
    }


def prepare_markdown(identity: dict[str, str]) -> str:
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

    body = re.sub(r"\n\*End of text-freeze review copy v10\.\*\s*$", "", body)
    if "\n## References\n" not in body:
        raise RuntimeError("formatted reviewer PDF requires a References section")
    body = body.replace(
        "\n## References\n",
        "\n## References\n\n\\begingroup\n\\small\n\\setlength{\\parskip}{0.35em}\n",
        1,
    )
    body = body.rstrip() + "\n\n\\endgroup\n"

    identity_block = (
        "> **Review artifact identity.** Repository `"
        + identity["repository"]
        + "`; branch `"
        + identity["branch"]
        + "`; text-freeze source commit `"
        + identity["source_commit"]
        + "`; freeze tag `"
        + identity["freeze_tag"]
        + "`; source `"
        + identity["manuscript"]
        + "`. The PDF SHA-256 and OpenTimestamps proof are committed beside the generated file.\n\n"
    )

    return f'''---
title: "{title}"
author: "Yohei Nakajima"
date: "July 30, 2026"
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

{identity_block}{body}'''


def update_machine_readable(identity: dict[str, str], digest: str, pages: int) -> None:
    source_digest = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    artifact = {
        **identity,
        "pdf": str(OUTPUT.relative_to(ROOT)),
        "pdf_sha256": digest,
        "source_sha256": source_digest,
        "pages": pages,
        "build_markdown": str(BUILD_MD.relative_to(ROOT)),
        "status": "text-frozen external-review copy; not for citation",
        "ots_proof": str((SHA_FILE.with_suffix(SHA_FILE.suffix + ".ots")).relative_to(ROOT)),
    }
    MANIFEST.write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")

    freeze = json.loads(FREEZE_RECORD.read_text(encoding="utf-8"))
    freeze.update({
        "pdf_sha256": digest,
        "source_sha256": source_digest,
        "pages": pages,
        "artifact_manifest": str(MANIFEST.relative_to(ROOT)),
        "build_commit": identity["build_commit"],
        "workflow_run": identity["workflow_run"],
    })
    FREEZE_RECORD.write_text(json.dumps(freeze, indent=2) + "\n", encoding="utf-8")

    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    summary["textFreeze"] = {
        "version": "v10",
        "status": "scientific text frozen for external review",
        "sourceCommit": identity["source_commit"],
        "freezeTag": identity["freeze_tag"],
        "sourceSha256": source_digest,
        "pdf": str(OUTPUT.relative_to(ROOT)),
        "pdfSha256": digest,
        "pages": pages,
        "scope": identity["freeze_scope"],
    }
    SUMMARY.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    for program in ("pandoc", "xelatex", "pdfinfo"):
        require(program)
    if not FREEZE_RECORD.exists():
        raise RuntimeError(f"missing freeze record: {FREEZE_RECORD}")
    for figure in FIGURES:
        figure_pdf = PAPER_DIR / "figures" / f"{figure}.pdf"
        if not figure_pdf.exists():
            raise RuntimeError(f"missing generated figure PDF: {figure_pdf}")

    identity = artifact_identity()
    BUILD_DIR.mkdir(parents=True, exist_ok=True)
    BUILD_MD.write_text(prepare_markdown(identity), encoding="utf-8")

    env = os.environ.copy()
    env["SOURCE_DATE_EPOCH"] = SOURCE_DATE_EPOCH
    env["TZ"] = "UTC"
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
    subprocess.run(cmd, cwd=ROOT, check=True, env=env)
    info = subprocess.check_output(["pdfinfo", str(OUTPUT)], cwd=ROOT, text=True)
    pages = next((int(line.split(":", 1)[1].strip()) for line in info.splitlines() if line.startswith("Pages:")), None)
    if pages is None:
        raise RuntimeError("could not parse PDF page count")

    digest = hashlib.sha256(OUTPUT.read_bytes()).hexdigest()
    SHA_FILE.write_text(f"{digest}  {OUTPUT.name}\n", encoding="utf-8")
    update_machine_readable(identity, digest, pages)

    print(info)
    print(f"build_review_pdf: wrote {OUTPUT.relative_to(ROOT)} ({pages} pages, sha256={digest})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
