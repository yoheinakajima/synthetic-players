#!/usr/bin/env python3
"""Build the canonical PDF and an arXiv-uploadable source archive."""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER_DIR = ROOT / "docs" / "paper"
SOURCE = PAPER_DIR / "paper.md"
ALIAS = PAPER_DIR / "paper-draft.md"
OUTPUT = PAPER_DIR / "synthetic-players.pdf"
SHA_FILE = PAPER_DIR / "synthetic-players.sha256"
ARTIFACT = PAPER_DIR / "synthetic-players-artifact.json"
SOURCE_ZIP = PAPER_DIR / "synthetic-players-arxiv-source.zip"
METADATA = PAPER_DIR / "arxiv-metadata.txt"
ARXIV_DIR = ROOT / "arxiv"
FIGURES = (
    "prompt-indexed-delta",
    "condition-means",
    "between-prompt-share",
    "representation-effects",
    "p13-audit",
)
PHASE6_SENTENCE = (
    "A Phase 6 test will preregister the candidate family, episode-level dependence unit, "
    "interiority gate, maximum statistic, familywise decision rule, and sample size before any data are collected."
)


def require(program: str) -> None:
    if shutil.which(program) is None:
        raise RuntimeError(f"required program not found: {program}")


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def extract_title_and_abstract(text: str) -> tuple[str, str]:
    title_match = re.search(r"^# (.+)$", text, flags=re.M)
    abstract_match = re.search(r"^## Abstract\n\n(.+?)(?=\n\n## 1\. Introduction)", text, flags=re.M | re.S)
    if not title_match or not abstract_match:
        raise RuntimeError("title or abstract missing from paper.md")
    return title_match.group(1).strip(), " ".join(abstract_match.group(1).split())


def prepare_latex_markdown(text: str, title: str, abstract: str, out: Path) -> None:
    intro_at = text.index("## 1. Introduction")
    body = text[intro_at:]
    for figure in FIGURES:
        body, count = re.subn(
            rf"!\[[^\]]*\]\(figures/{re.escape(figure)}\.svg\)",
            lambda _m, f=figure: f"![](figures/{f}.pdf){{width=95%}}",
            body,
            count=1,
        )
        if count != 1:
            raise RuntimeError(f"expected one Markdown reference for figure {figure}; got {count}")
    body = body.replace(
        "\n## References\n",
        "\n## References\n\n\\begingroup\n\\small\n\\setlength{\\parskip}{0.30em}\n",
        1,
    ).rstrip() + "\n\n\\endgroup\n"
    escaped_title = title.replace('"', '\\"')
    out.write_text(
        f'''---
title: "{escaped_title}"
author: "Yohei Nakajima"
date: "Untapped Capital - July 2026"
lang: en-US
documentclass: article
classoption: [11pt]
colorlinks: true
linkcolor: blue
urlcolor: blue
---

\\begin{{abstract}}
{abstract}
\\end{{abstract}}

{body}''',
        encoding="utf-8",
    )


def write_header(path: Path) -> None:
    path.write_text(
        r'''\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern}
\usepackage{microtype}
\usepackage{booktabs,longtable,array,ragged2e,graphicx,float,caption,xcolor,enumitem}
\usepackage{geometry}
\geometry{letterpaper,top=0.82in,bottom=0.86in,left=0.92in,right=0.92in}
\captionsetup{font=small,labelfont=bf}
\setlength{\parindent}{0pt}
\setlength{\parskip}{0.52em}
\setlength{\emergencystretch}{3em}
\setlist{nosep,leftmargin=*}
\AtBeginEnvironment{longtable}{\small}
\usepackage{newunicodechar}
\newunicodechar{δ}{\ensuremath{\delta}}
\newunicodechar{ρ}{\ensuremath{\rho}}
\newunicodechar{×}{\ensuremath{\times}}
\newunicodechar{→}{\ensuremath{\rightarrow}}
\newunicodechar{−}{\ensuremath{-}}
''',
        encoding="utf-8",
    )


def compile_pdf(main_tex: Path, cwd: Path) -> None:
    for _ in range(2):
        completed = subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", main_tex.name],
            cwd=cwd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        if completed.returncode:
            raise RuntimeError("pdflatex failed:\n" + completed.stdout[-12000:])


def deterministic_zip(path: Path, source_root: Path, members: list[Path]) -> None:
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for member in sorted(members, key=lambda p: p.as_posix()):
            relative = member.relative_to(source_root).as_posix()
            info = zipfile.ZipInfo(relative, date_time=(2026, 7, 31, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, member.read_bytes())


def preflight(title: str, abstract: str, pdf: Path, source_zip: Path) -> dict[str, object]:
    info = subprocess.check_output(["pdfinfo", str(pdf)], cwd=ROOT, text=True)
    pages = int(next(line.split(":", 1)[1].strip() for line in info.splitlines() if line.startswith("Pages:")))
    if not 16 <= pages <= 28:
        raise RuntimeError(f"unexpected PDF page count: {pages}")
    extracted = subprocess.check_output(["pdftotext", str(pdf), "-"], cwd=ROOT, text=True, errors="replace")
    normalized = " ".join(extracted.split())
    required = (
        title,
        "4,916",
        "0.071",
        "0.189",
        "Large language models can predict the results of social science experiments",
    )
    errors: list[str] = []
    for marker in required:
        if marker not in normalized:
            errors.append(f"PDF text missing {marker!r}")
    if normalized.count("A Phase 6 test will preregister the candidate family") != 1:
        errors.append("Phase 6 sentence does not occur exactly once in extracted PDF")
    for forbidden in ("Preprint v", "working draft", "review candidate", "arXiv candidate"):
        if forbidden.lower() in normalized.lower():
            errors.append(f"release label remains in PDF: {forbidden!r}")
    if len(abstract) > 1920 or not abstract.isascii():
        errors.append(f"arXiv abstract invalid: {len(abstract)} chars; ascii={abstract.isascii()}")
    fonts = subprocess.check_output(["pdffonts", str(pdf)], cwd=ROOT, text=True)
    for line in fonts.splitlines()[2:]:
        cols = line.split()
        if len(cols) >= 7 and (cols[-5].lower() != "yes" or cols[-4].lower() != "yes"):
            errors.append(f"font not embedded/subset: {line}")
    with zipfile.ZipFile(source_zip) as archive:
        names = sorted(archive.namelist())
        expected = sorted(["main.tex"] + [f"figures/{name}.pdf" for name in FIGURES])
        if names != expected:
            errors.append(f"arXiv source members differ: {names}")
    if errors:
        raise RuntimeError("release preflight failed:\n- " + "\n- ".join(errors))
    return {"pages": pages, "pdfinfo": info, "fonts": fonts}


def main() -> int:
    for program in ("pandoc", "pdflatex", "pdfinfo", "pdftotext", "pdffonts"):
        require(program)
    text = SOURCE.read_text(encoding="utf-8")
    if ALIAS.read_bytes() != SOURCE.read_bytes():
        raise RuntimeError("paper.md and paper-draft.md aliases differ")
    if text.count(PHASE6_SENTENCE) != 1:
        raise RuntimeError(f"Phase 6 sentence count in source is {text.count(PHASE6_SENTENCE)}, expected 1")
    for forbidden in ("Preprint v", "working draft", "review candidate", "arXiv candidate"):
        if forbidden.lower() in text.lower():
            raise RuntimeError(f"release label remains in source: {forbidden}")

    title, abstract = extract_title_and_abstract(text)
    if ARXIV_DIR.exists():
        shutil.rmtree(ARXIV_DIR)
    figures_dir = ARXIV_DIR / "figures"
    figures_dir.mkdir(parents=True)
    for figure in FIGURES:
        shutil.copy2(PAPER_DIR / "figures" / f"{figure}.pdf", figures_dir / f"{figure}.pdf")

    with tempfile.TemporaryDirectory(prefix="synthetic-players-arxiv-") as temp_name:
        temp = Path(temp_name)
        markdown = temp / "manuscript.md"
        header = temp / "header.tex"
        prepare_latex_markdown(text, title, abstract, markdown)
        write_header(header)
        main_tex = ARXIV_DIR / "main.tex"
        subprocess.run(
            [
                "pandoc",
                str(markdown),
                "--from=markdown+tex_math_dollars+tex_math_single_backslash+raw_tex",
                "--to=latex",
                "--standalone",
                "--include-in-header",
                str(header),
                "--metadata",
                "pdfauthor=Yohei Nakajima",
                "-o",
                str(main_tex),
            ],
            cwd=ROOT,
            check=True,
        )
        main_tex.write_text("\\pdfoutput=1\n" + main_tex.read_text(encoding="utf-8"), encoding="utf-8")

    compile_pdf(ARXIV_DIR / "main.tex", ARXIV_DIR)
    shutil.copy2(ARXIV_DIR / "main.pdf", OUTPUT)
    for suffix in (".aux", ".log", ".out", ".toc", ".pdf"):
        candidate = ARXIV_DIR / f"main{suffix}"
        if candidate.exists():
            candidate.unlink()

    deterministic_zip(
        SOURCE_ZIP,
        ARXIV_DIR,
        [ARXIV_DIR / "main.tex"] + [figures_dir / f"{name}.pdf" for name in FIGURES],
    )
    result = preflight(title, abstract, OUTPUT, SOURCE_ZIP)
    digest = hashlib.sha256(OUTPUT.read_bytes()).hexdigest()
    source_digest = hashlib.sha256(SOURCE_ZIP.read_bytes()).hexdigest()
    SHA_FILE.write_text(f"{digest}  {OUTPUT.name}\n", encoding="utf-8")
    METADATA.write_text(
        f"""Title: {title}\nAuthor: Yohei Nakajima\nSuggested primary category: cs.AI\nSuggested cross-list: cs.HC\nComments: {result['pages']} pages, 5 figures. Code, data, registrations, review record, and zero-call replay capsule: https://github.com/yoheinakajima/synthetic-players\n\nAbstract:\n{abstract}\n""",
        encoding="ascii",
    )
    ARTIFACT.write_text(
        json.dumps(
            {
                "repository": "yoheinakajima/synthetic-players",
                "source_commit": git("rev-parse", "HEAD"),
                "source": "docs/paper/paper.md",
                "pdf": "docs/paper/synthetic-players.pdf",
                "pdf_sha256": digest,
                "arxiv_source": "docs/paper/synthetic-players-arxiv-source.zip",
                "arxiv_source_sha256": source_digest,
                "pages": result["pages"],
                "figures": 5,
                "workflow_run": os.environ.get("GITHUB_RUN_ID", "local"),
                "status": "arXiv-ready preprint",
            },
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )
    print(result["pdfinfo"])
    print(f"build_arxiv_release: pdf_sha256={digest} source_sha256={source_digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
