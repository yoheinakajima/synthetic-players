#!/usr/bin/env python3
"""Generate the static project site into site/ from scripts/site_data.py.

Stdlib only. Every item in the content graph gets its own page; relations are
rendered bidirectionally so each page lists everything tied to it. Run:

    python scripts/build_site.py

Outputs are committed; GitHub Pages serves site/ verbatim (workflow copies the
directory and the canonical paper.pdf / arxiv-source.zip beside it).
"""
from __future__ import annotations

import html
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
sys.path.insert(0, str(ROOT / "scripts"))

import site_data as D  # noqa: E402

BASE_URL = "https://yoheinakajima.github.io/synthetic-players/"

TYPE_LABEL = {
    "claim": "Claim",
    "phase": "Phase",
    "figure": "Figure",
    "review": "Review round",
    "version": "Manuscript version",
    "reference": "Reference",
    "analysis": "Analysis",
    "artifact": "Artifact",
    "concept": "Protocol",
    "page": "Page",
}

TYPE_ORDER = [
    "claim", "phase", "analysis", "figure", "review",
    "version", "reference", "artifact", "concept", "page",
]

STATUS_CLASS = {
    "registered-pass": "s-pass",
    "registered-fail": "s-fail",
    "registered-mixed": "s-mixed",
    "method-sensitive": "s-mixed",
    "prior-sensitive": "s-mixed",
    "replication-target": "s-target",
    "withdrawn": "s-fail",
    "descriptive": "s-desc",
    "post-adjudication": "s-desc",
    "procedural": "s-proc",
    "prospective": "s-target",
    "sealed": "s-proc",
    "superseded": "s-desc",
    "final": "s-pass",
    "imprecise": "s-mixed",
}


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def items_by_id() -> dict:
    out = {}
    for it in D.ITEMS:
        if it["id"] in out:
            raise SystemExit(f"duplicate item id: {it['id']}")
        out[it["id"]] = it
    return out


def compute_backlinks(idx: dict) -> dict:
    back: dict[str, set] = {k: set() for k in idx}
    for it in D.ITEMS:
        for rid in it.get("rel", []):
            if rid not in idx:
                raise SystemExit(f"{it['id']}: unknown relation target {rid}")
            back[rid].add(it["id"])
    return back


def status_chip(status: str | None) -> str:
    if not status:
        return ""
    cls = STATUS_CLASS.get(status, "s-desc")
    return f'<span class="chip {cls}">{esc(D.STATUS_LABEL.get(status, status))}</span>'


def page_href(item_id: str) -> str:
    return f"{item_id}.html"


def item_link(idx: dict, item_id: str, with_type: bool = False) -> str:
    it = idx[item_id]
    t = f'<span class="rel-type">{esc(TYPE_LABEL[it["type"]])}</span> ' if with_type else ""
    return f'{t}<a href="{page_href(item_id)}">{esc(it["title"])}</a>'


def related_block(idx: dict, back: dict, it: dict) -> str:
    fwd = list(dict.fromkeys(it.get("rel", [])))
    bwd = sorted(back[it["id"]] - set(fwd) - {it["id"]},
                 key=lambda i: (TYPE_ORDER.index(idx[i]["type"]), i))
    linked = fwd + [b for b in bwd if b not in fwd]
    if not linked:
        return ""
    groups: dict[str, list] = {}
    for lid in linked:
        groups.setdefault(idx[lid]["type"], []).append(lid)
    rows = []
    for t in TYPE_ORDER:
        if t not in groups:
            continue
        links = []
        for lid in groups[t]:
            tgt = idx[lid]
            chip = status_chip(tgt.get("status"))
            links.append(
                f'<li><a href="{page_href(lid)}">{esc(tgt["title"])}</a>'
                f'{chip}<span class="rel-short">{esc(tgt.get("short", ""))}</span></li>'
            )
        rows.append(
            f'<div class="rel-group"><h3>{esc(TYPE_LABEL[t])}s</h3>'
            f'<ul>{"".join(links)}</ul></div>'
        )
    return (
        '<section class="related" aria-label="Linked items">'
        "<h2>Linked in the research graph</h2>"
        '<p class="rel-note">Everything connected to this item, in both directions.</p>'
        + "".join(rows) + "</section>"
    )


def external_links(it: dict) -> str:
    links = it.get("links", [])
    if not links:
        return ""
    parts = "".join(
        f'<a class="ext" href="{esc(l["href"])}">{esc(l["label"])}</a>'
        for l in links
    )
    return f'<p class="ext-row">{parts}</p>'


NAV = [
    ("index.html", "Overview"),
    ("qa.html", "Q&A"),
    ("claims.html", "Claims"),
    ("phases.html", "Phases"),
    ("timeline.html", "Timeline"),
    ("reviews.html", "Reviews"),
    ("related-work.html", "Related work"),
    ("versions.html", "Versions"),
    ("artifacts.html", "Artifacts"),
]


def shell(title: str, body: str, description: str, canonical: str,
          current: str | None = None) -> str:
    nav = "".join(
        f'<a href="{href}"{" class=" + chr(34) + "here" + chr(34) if href == current else ""}>{esc(label)}</a>'
        for href, label in NAV
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{esc(BASE_URL + canonical)}">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="styles.css">
</head>
<body>
<header class="masthead">
<div class="mast-inner">
<a class="wordmark" href="index.html">Synthetic&nbsp;Players</a>
<nav class="mainnav" aria-label="Site">{nav}</nav>
<div class="mast-actions"><a class="pdfbtn" href="paper.pdf">Paper&nbsp;PDF</a></div>
</div>
</header>
<main class="wrap">
{body}
</main>
<footer class="colophon">
<div class="wrap">
<p><b>Synthetic Players</b> — auditable strategic experiments with LLM-controlled agents. Yohei Nakajima, 2026.</p>
<p><a href="https://arxiv.org/abs/2608.00979">arXiv:2608.00979</a> · <a href="https://github.com/yoheinakajima/synthetic-players">Repository</a> · <a href="paper.pdf">Paper PDF</a> · <a href="arxiv-source.zip">arXiv source</a> · Code MIT · Research artifacts CC BY 4.0. Historical records are preserved; corrections are additive.</p>
</div>
</footer>
<script src="script.js"></script>
</body>
</html>
"""


def render_item(idx: dict, back: dict, it: dict) -> str:
    chip = status_chip(it.get("status"))
    kicker = TYPE_LABEL[it["type"]]
    meta = it.get("meta", "")
    meta_html = f'<p class="item-meta">{meta}</p>' if meta else ""
    body = it.get("body", "")
    head = (
        f'<article class="item">'
        f'<p class="kicker">{esc(kicker)}{chip}</p>'
        f'<h1>{esc(it["title"])}</h1>'
        f'<p class="dek">{esc(it.get("short", ""))}</p>'
        f"{meta_html}{external_links(it)}"
        f'<div class="body">{body}</div>'
    )
    return head + related_block(idx, back, it) + "</article>"


def write(path: str, content: str) -> None:
    (SITE / path).write_text(content, encoding="utf-8")


def sitemap(pages: list[str]) -> str:
    urls = "".join(
        f"<url><loc>{esc(BASE_URL + ('' if p == 'index.html' else p))}</loc></url>"
        for p in pages
    )
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
            f"{urls}</urlset>\n")


def check_links(pages: list[str]) -> None:
    """Every local href/src in every generated page must resolve inside site/."""
    ok_missing = {"paper.pdf", "arxiv-source.zip"}
    href_re = re.compile(r'(?:href|src)="([^"]+)"')
    errors = []
    for p in pages:
        text = (SITE / p).read_text(encoding="utf-8")
        for target in href_re.findall(text):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            base = target.split("#", 1)[0]
            if not base or base in ok_missing:
                continue
            if not (SITE / base).exists():
                errors.append(f"{p}: missing target {base}")
    if errors:
        raise SystemExit("link check failed:\n" + "\n".join(errors))


def main() -> None:
    idx = items_by_id()
    back = compute_backlinks(idx)
    pages = []

    for it in D.ITEMS:
        fname = f"{it['id']}.html"
        title = f"{it['title']} — Synthetic Players"
        write(fname, shell(title, render_item(idx, back, it),
                           it.get("short", ""), fname))
        pages.append(fname)

    for fname, title, desc, nav_key, builder in D.SPECIAL_PAGES:
        body = builder(idx, back, {
            "item_link": item_link, "status_chip": status_chip,
            "page_href": page_href, "esc": esc,
        })
        write(fname, shell(title, body, desc, "" if fname == "index.html" else fname,
                           current=nav_key))
        pages.append(fname)

    write("sitemap.xml", sitemap(sorted(pages)))
    check_links(pages)

    required = ["47–71%", "0.205", "4,919", "4,916 confirmatory"]
    index_text = (SITE / "index.html").read_text(encoding="utf-8")
    missing = [r for r in required if r not in index_text]
    if missing:
        raise SystemExit(f"index.html missing required strings: {missing}")

    print(f"generated {len(pages)} pages + sitemap.xml; link check passed")


if __name__ == "__main__":
    main()
