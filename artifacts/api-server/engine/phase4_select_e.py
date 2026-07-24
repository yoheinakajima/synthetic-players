"""E-dselected mechanical resolution — Rule INTERIOR (operator-chosen by name).

Pre-committed at the D1/D2 boundary, BEFORE being run against real data.
Runs at step 6 of the frozen order (after X2 confirmation, before block E).
Output is disclosed to the operator only after the resolution write.

Rule INTERIOR (provenance-notes.md, registration-gap entry, commit 1424fd5):
among the 16 sealed `pd-rep-{W}-{L}-{O}-{P}` candidates, select the one whose
D1 primary-family (gpt) M=can cell mean Y is closest to 0.5; ties broken by
manifest line order in docs/phase4/arms.json. This matches the selection rule
stated verbatim in the operator's Phase 4 sign-off response: "the D cell whose
round-1 cooperation is nearest 0.5, most interior" — the registration gap was
a transcription failure of documented pre-data intent (operator direction at
the D1/D2 boundary, quoted in the ledger).

Modes:
  --selftest   pure-function unit checks on synthetic values (no data access)
  --resolve    compute selection, POST write-once resolution to the engine,
               write docs/phase4/e-selection-report.{json,md}, then print
  --dry        compute + print WITHOUT posting (step-8 replay only; refuses
               to run unless the resolution already exists, so a dry run can
               never leak the winner ahead of the write)
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.request
from pathlib import Path

ENGINE = os.environ.get("ENGINE_URL", "http://127.0.0.1:8090")
ROOT = Path(__file__).resolve().parents[3]
DOCS = Path(os.environ.get("PHASE4_DOCS") or (ROOT / "docs" / "phase4"))
RULE = "INTERIOR"
KEY = "E-dselected"
FAMILY = "gpt"      # primary family only, per the rule
M_LEVEL = "can"     # candidates are all M=can
EXPECTED_CELLS = 16
EXPECTED_PER_CELL = 10

OPERATOR_QUOTE = (
    "the D cell whose round-1 cooperation is nearest 0.5, most interior"
)


# ── pure selection function ──────────────────────────────────────────────────

def select_interior(cell_means: list[tuple[str, float, int]]) -> dict:
    """cell_means: [(templateId, meanY, manifestIndex)] — all 16 candidates.

    Returns {"templateId", "meanY", "distance", "tieBroken"}.
    Deterministic: min over (|mean − 0.5|, manifestIndex).
    """
    if len(cell_means) != EXPECTED_CELLS:
        raise SystemExit(f"REFUSING: expected {EXPECTED_CELLS} candidate cells, got {len(cell_means)}")
    ids = [t[0] for t in cell_means]
    if len(set(ids)) != EXPECTED_CELLS:
        raise SystemExit("REFUSING: duplicate templateIds in candidate list")
    keyed = sorted(cell_means, key=lambda t: (abs(t[1] - 0.5), t[2]))
    winner = keyed[0]
    runner = keyed[1]
    tie = abs(winner[1] - 0.5) == abs(runner[1] - 0.5)
    return {
        "templateId": winner[0],
        "meanY": winner[1],
        "distance": abs(winner[1] - 0.5),
        "tieBroken": tie,
    }


# ── manifest order ───────────────────────────────────────────────────────────

def manifest_candidates() -> list[str]:
    """The 16 pd-rep-{w1|w2a}-... ids in raw file (line) order from arms.json.
    Excludes pd-rep-community-w1 by pattern. Refuses on any count != 16."""
    raw = (DOCS / "arms.json").read_text()
    ids = re.findall(r'"(pd-rep-(?:w1|w2a)-[a-z0-9]+-[a-z0-9]+-[a-z0-9]+)"\s*:', raw)
    # de-dup preserving first occurrence (hash map may repeat ids in values)
    seen: list[str] = []
    for i in ids:
        if i not in seen:
            seen.append(i)
    if len(seen) != EXPECTED_CELLS:
        raise SystemExit(f"REFUSING: manifest scan found {len(seen)} candidates, expected {EXPECTED_CELLS}: {seen}")
    return seen


# ── D1 cell means (primary family, M=can) ────────────────────────────────────

def compute_cell_means() -> list[tuple[str, float, int]]:
    from phase4_adjudicate import load_phase4_runs, d1_parse_arm  # analysis-only module

    order = manifest_candidates()
    idx = {tid: i for i, tid in enumerate(order)}
    cells: dict[str, list[float]] = {tid: [] for tid in order}

    runs = load_phase4_runs()
    for rid, r in runs.items():
        if r.get("block") != "D1":
            continue
        parsed = d1_parse_arm(r.get("armId", ""))
        if parsed is None:
            raise SystemExit(f"REFUSING: unparseable D1 armId {r.get('armId')!r} ({rid})")
        m, w, l, o, p, fam = parsed
        if fam != FAMILY or m != M_LEVEL:
            continue
        tid = f"pd-rep-{w}-{l}-{o}-{p}"
        if tid not in cells:
            raise SystemExit(f"REFUSING: D1 M=can cell {tid} not among the 16 sealed candidates")
        if r["invalid"] or not r["completed"] or 1 not in r["rounds"]:
            raise SystemExit(f"REFUSING: invalid/incomplete episode in selection slice ({tid}, seed {r.get('seed')})")
        a1, a2 = r["rounds"][1]
        cells[tid].append(((a1 == 0) + (a2 == 0)) / 2.0)

    bad = {t: len(v) for t, v in cells.items() if len(v) != EXPECTED_PER_CELL}
    if bad:
        raise SystemExit(f"REFUSING: cell counts != {EXPECTED_PER_CELL}: {bad}")
    return [(tid, sum(v) / len(v), idx[tid]) for tid, v in cells.items()]


# ── engine I/O ───────────────────────────────────────────────────────────────

def _engine_get(path: str) -> dict:
    with urllib.request.urlopen(f"{ENGINE}{path}", timeout=15) as resp:
        return json.loads(resp.read())


def _engine_post(path: str, body: dict) -> dict:
    req = urllib.request.Request(
        f"{ENGINE}{path}", data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def resolution_note(sel: dict) -> str:
    return (
        f"Rule {RULE} (pre-committed: provenance-notes.md registration-gap entry, commit 1424fd5; "
        f"operator chose it by name at the D1/D2 boundary from family-level aggregates only, with "
        f"per-cell means and template identity undisclosed until this write). Rule: among the 16 "
        f"sealed pd-rep-* candidates, the D1 primary-family M=can cell mean Y closest to 0.5, ties "
        f"by manifest line order. Matches the operator's Phase 4 sign-off response verbatim: "
        f"'{OPERATOR_QUOTE}' — the registration gap was a transcription failure of documented "
        f"pre-data intent. Selected: {sel['templateId']} (mean Y {sel['meanY']:.4f}, distance "
        f"{sel['distance']:.4f}, tieBroken={sel['tieBroken']}). Full 16-cell table: "
        f"docs/phase4/e-selection-report.json."
    )


def run(post: bool) -> int:
    status = _engine_get("/phase4/status")
    if not status.get("sealed"):
        raise SystemExit("REFUSING: engine not sealed")
    existing = (status.get("resolutions") or {}).get(KEY)
    if post and existing:
        raise SystemExit(f"REFUSING: {KEY} already resolved to {existing!r} (write-once)")
    if not post and not existing:
        raise SystemExit("REFUSING: --dry before the resolution write would leak the winner; "
                         "run --resolve, or wait until the resolution exists")

    means = compute_cell_means()
    sel = select_interior(means)
    note = resolution_note(sel)

    engine_resp = None
    if post:
        engine_resp = _engine_post("/phase4/resolutions",
                                   {"key": KEY, "templateId": sel["templateId"], "note": note})

    report = {
        "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "rule": RULE, "key": KEY, "family": FAMILY, "mLevel": M_LEVEL,
        "operatorQuote": OPERATOR_QUOTE,
        "cellMeans": [{"templateId": t, "meanY": m, "manifestIndex": i}
                      for t, m, i in sorted(means, key=lambda x: x[2])],
        "selected": sel, "note": note, "posted": post, "engineResponse": engine_resp,
    }
    out = DOCS / "e-selection-report.json"
    out.write_text(json.dumps(report, indent=1) + "\n")
    md = [f"# E-dselected resolution — Rule {RULE}", "",
          f"Generated {report['generatedAt']}. Posted: {post}.", "",
          f"Operator sign-off quote: \"{OPERATOR_QUOTE}\"", "",
          "| # | template | M=can cell mean Y | |Y − 0.5| |", "|---|---|---|---|"]
    for c in report["cellMeans"]:
        mark = " ← selected" if c["templateId"] == sel["templateId"] else ""
        md.append(f"| {c['manifestIndex']} | {c['templateId']}{mark} | {c['meanY']:.4f} | {abs(c['meanY']-0.5):.4f} |")
    md += ["", f"Selected: **{sel['templateId']}** (tieBroken={sel['tieBroken']})", "", note, ""]
    (DOCS / "e-selection-report.md").write_text("\n".join(md))
    print(json.dumps({"selected": sel, "posted": post, "engineResponse": engine_resp}, indent=1))
    return 0


def selftest() -> int:
    base = [(f"t{i:02d}", 0.9, i) for i in range(16)]
    # unique winner
    cm = list(base); cm[5] = ("t05", 0.52, 5)
    assert select_interior(cm)["templateId"] == "t05"
    # exact tie ±0.1 → earlier manifest index wins
    cm = list(base); cm[7] = ("t07", 0.6, 7); cm[3] = ("t03", 0.4, 3)
    r = select_interior(cm)
    assert r["templateId"] == "t03" and r["tieBroken"] is True, r
    # tie between equal values → earlier index
    cm = list(base); cm[9] = ("t09", 0.45, 9); cm[2] = ("t02", 0.45, 2)
    assert select_interior(cm)["templateId"] == "t02"
    # 0.5 exactly beats everything
    cm = list(base); cm[11] = ("t11", 0.5, 11); cm[0] = ("t00", 0.49, 0)
    assert select_interior(cm)["templateId"] == "t11"
    # degenerate all-equal → manifest index 0
    cm = [(f"t{i:02d}", 0.0, i) for i in range(16)]
    r = select_interior(cm)
    assert r["templateId"] == "t00" and r["tieBroken"] is True
    # wrong count refused
    try:
        select_interior(base[:15]); raise AssertionError("count guard failed")
    except SystemExit:
        pass
    print("selftest OK (5 selection cases + count guard)")
    return 0


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        raise SystemExit(selftest())
    if "--resolve" in sys.argv:
        raise SystemExit(run(post=True))
    if "--dry" in sys.argv:
        raise SystemExit(run(post=False))
    print(__doc__)
    raise SystemExit(2)
