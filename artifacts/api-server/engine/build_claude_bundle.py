"""Build the Claude analysis bundle — curated, read-ordered handoff package.

Copies the record's key documents into claude-analysis-bundle/ with
read-order numbered names, prepends a one-line self-describing header to
every file (what it is, CONFIRMATORY vs EXPLORATORY, source), writes an
INDEX.md, and produces claude-analysis-bundle.tar.gz.

Token discipline: .md summaries preferred; CSVs included only where the
table IS the content. Target < 2 MB of text total.

Run: cd artifacts/api-server && uv run python engine/build_claude_bundle.py
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(_HERE, "..", "..", ".."))
OUT = os.path.join(REPO, "claude-analysis-bundle")

C, E = "CONFIRMATORY", "EXPLORATORY"
ADJ = "engine/phase5_closeout_adjudicate.py"
PV = "engine/gen_post_verdict.py"

# (bundle name, repo path, kind, one-line description, source)
FILES = [
    # 1. final reports
    ("01-phase5-final-report.md", "docs/phase5/final-report.md", C,
     "Phase 5 final report: sealed predicates P5-1a/1b/2/3/4, axes, Branch 2", ADJ),
    ("02-phase4-final-report.md", "docs/phase4/final-report.md", C,
     "Phase 4 final report: D1-D3/E/F/X1/X2 verdicts (as sealed)", "engine/phase4_adjudicate.py"),
    ("03-phase3-report.md", "docs/phase3-report.md", C,
     "Phase 3 report (as sealed)", "engine records, Phase 3"),
    # 2. branch selection
    ("04-branch-selection.md", "docs/phase5-close/branch-selection.md", C,
     "Machine branch-selection record: axes A/B/C -> Branch 2, variant retained", ADJ),
    ("05-discussion-branches-SEALED.md", "docs/paper/discussion-branches.md", C,
     "Sealed pre-committed discussion branches, byte-identical to registration sha 1f1d7de9...e356; Branch 2 is the selected text", "sealed 2026-07 (pre-outcome)"),
    # 3. ledgers
    ("06-claims-ledger.md", "docs/analysis/claims-ledger.md", C,
     "Every registered claim v1->P5 with verdict and source record", "docs/phase*-close records"),
    ("06b-claims-ledger.csv", "docs/analysis/claims-ledger.csv", C,
     "Machine-readable claims ledger (same content as 06)", "docs/phase*-close records"),
    ("07-dead-predictions-final.md", "docs/analysis/dead-predictions-final.md", C,
     "The 12 registered author predictions that failed, verbatim, with what happened instead", "registered records"),
    ("08-human-anchor-scorecard.md", "docs/analysis/human-anchor-scorecard.md", E,
     "7 human-benchmark anchors vs the pool: levels/SD match, delta-response ~1/5 human", "engine/gen_analysis_pack.py"),
    ("09-corner-map.md", "docs/analysis/corner-map.md", E,
     "Corner/interior map of all 96 persona-cells + bare lanes", "engine/gen_analysis_pack.py"),
    ("09b-persona-cell-map.csv", "docs/analysis/figure-sources/p5-persona-cell-map.csv", E,
     "Per persona-cell: rate, CP95, interior flag (96 rows; the corner-map table)", "engine/gen_analysis_pack.py"),
    # 4. post-verdict analyses
    ("10-pv-clause-b-anatomy.md", "docs/analysis/post-verdict/clause-b-anatomy.md", E,
     "P5-3 clause-(b) word/payoff confound anatomy; what the data cannot decide", PV),
    ("10b-pv-swap-choice.csv", "docs/analysis/post-verdict/figure-sources/pv-swap-choice.csv", E,
     "Per-persona x T swap choice table (refusal + word-choice, CIs)", PV),
    ("11-pv-p13-deep-dive.md", "docs/analysis/post-verdict/p13-deep-dive.md", E,
     "p13 (sole delta-slope pass): card, all cells, trajectories, trait gradient", PV),
    ("12-pv-interior-census.md", "docs/analysis/post-verdict/interior-census.md", E,
     "Corrected census of all 14 interior persona-cells (Branch-2 exhibit)", PV),
    ("12b-pv-interior-census.csv", "docs/analysis/post-verdict/figure-sources/pv-interior-census.csv", E,
     "The 14 interior cells as data (persona, cell, rate, CI)", PV),
    ("13-pv-p52-decomposition.md", "docs/analysis/post-verdict/p52-decomposition.md", E,
     "P5-2 pooled 0.128 split: unconfounded rep subset vs word-confounded swap", PV),
    ("14-pv-entropy-anomaly.md", "docs/analysis/post-verdict/entropy-anomaly.md", E,
     "Falling entropy-vs-T decomposed by lane/family; matched-unit Simpson test", PV),
    # 5. packs
    ("15-persona-pack.md", "docs/analysis/persona-pack/README.md", E,
     "Persona-pack key tables: leaning gaps, interiority factor pattern, p13", "engine/gen_analysis_pack.py"),
    ("16-temperature-pack.md", "docs/analysis/temperature-pack/README.md", E,
     "Temperature sweep summary incl. the entropy-decline observation", "engine/gen_analysis_pack.py"),
    ("17-distribution-pack.md", "docs/analysis/distribution-pack/README.md", E,
     "Pool vs DF2011 human distributions: pins, SDs, bimodality, delta-drop", "engine/gen_analysis_pack.py"),
    ("18-stability-compendium.md", "docs/analysis/stability-compendium.md", E,
     "Every stability/replication check across the program in one place", "engine/gen_analysis_pack.py"),
    # 6. process records
    ("19-adjudication-decisions.json", "docs/phase5-close/adjudication-decisions.json", C,
     "All four outcome-blind completions (D1-D3 + twin table), operator-signed, verbatim rationales", "recorded 2026-07-28, pre-adjudication"),
    ("20-instance-ledger.md", "docs/instance-ledger.md", C,
     "Instance ledger: every process deviation/underspecification across the program", "maintained per process packet"),
    ("21-ops-meta.md", "docs/analysis/ops-meta.md", E,
     "Operational meta: budget, invalids, sentinels, infrastructure notes", "engine/gen_analysis_pack.py"),
    # 7. synthesis
    ("22-program-synthesis-DRAFT.md", "docs/analysis/program-synthesis-DRAFT.md", E,
     "WORKING DRAFT program synthesis — no new claims; the narrative skeleton", "author draft over the ledgers"),
]


def header(name: str, kind: str, desc: str, source: str) -> str:
    return f"{desc} [{kind}] (source: {source})"


def main() -> int:
    if os.path.exists(OUT):
        shutil.rmtree(OUT)
    os.makedirs(OUT)
    index = ["# Claude analysis bundle — INDEX (read in order)",
             "",
             "Handoff package for the pre-final-paper analysis session. The "
             "registered record is CLOSED; files marked CONFIRMATORY are the "
             "record, files marked EXPLORATORY are descriptive re-analysis "
             "and carry no verdict weight. Everything is regenerable from "
             "the event store in the repo (release `phase5-final`).",
             "",
             "| # | file | status | what it is |",
             "|---|---|---|---|"]
    total = 0
    for name, rel, kind, desc, source in FILES:
        src = os.path.join(REPO, rel)
        if not os.path.exists(src):
            print(f"MISSING: {rel}", file=sys.stderr)
            return 1
        body = open(src, encoding="utf-8").read()
        h = header(name, kind, desc, source)
        if name.endswith(".md"):
            out = f"> **{h}**\n\n{body}"
        elif name.endswith(".csv"):
            out = f"# {h}\n{body}"
        else:  # json — cannot comment; sidecar line in INDEX only
            out = body
        with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
            f.write(out)
        total += len(out.encode())
        index.append(f"| {name.split('-')[0]} | `{name}` | {kind} | {desc} |")
    index += ["",
              f"Total bundle size: {total/1e6:.2f} MB of text "
              f"({len(FILES)} files).",
              "",
              "Companion (not in bundle, in repo/release): full adjudication "
              "JSON (`docs/phase5-close/adjudication-report.json`), event-"
              "store snapshots, replay audit, figure-source CSVs."]
    with open(os.path.join(OUT, "INDEX.md"), "w") as f:
        f.write("\n".join(index) + "\n")
    subprocess.run(["tar", "czf", "claude-analysis-bundle.tar.gz",
                    "claude-analysis-bundle"], cwd=REPO, check=True)
    sz = os.path.getsize(os.path.join(REPO, "claude-analysis-bundle.tar.gz"))
    print(f"bundle: {len(FILES)} files + INDEX, {total/1e6:.2f} MB text, "
          f"archive {sz/1e6:.2f} MB")
    if total > 2_000_000:
        print("WARNING: over the 2 MB text target", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
