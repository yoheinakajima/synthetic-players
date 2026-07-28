"""Close-out §3 — generate the exploratory analysis-pack CSVs.

EXPLORATORY ONLY: nothing here is verdict-bearing; all confirmatory numbers
live in docs/phase5-close/. Emits into docs/analysis/figure-sources/ and
docs/analysis/*-pack/ from the event store and the finished machine records.
"""
from __future__ import annotations

import csv
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

import phase5_closeout_adjudicate as adj  # noqa: E402

REPO = adj.REPO_ROOT
AN = os.path.join(REPO, "docs", "analysis")
FS = os.path.join(AN, "figure-sources")


def w(path: str, header: list[str], rows: list[list]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        cw = csv.writer(f)
        cw.writerow(header)
        cw.writerows(rows)
    print("wrote", os.path.relpath(path, REPO), f"({len(rows)} rows)")


def main() -> int:
    runs = adj.load_runs()
    personas = adj.load_personas()
    col = adj.collect(runs, personas)

    # ---- persona-cell corner map (tier A) + persona pack source
    rows = []
    for (pid, cell), eps in sorted(col["epsA"].items()):
        g = adj.gate_cell(eps)
        rows.append([pid, personas[pid], cell, len(eps), g["k"], g["n"],
                     round(g["mean"], 4), round(g["cp95"][0], 4),
                     round(g["cp95"][1], 4), int(g["interior"])])
    w(os.path.join(FS, "p5-persona-cell-map.csv"),
      ["personaId", "leaning", "cell", "episodes", "k", "n", "meanRound1Coop",
       "cpLo", "cpHi", "interior"], rows)

    # ---- temperature curves (sweep cells, incl. T=0.7 tier-A points + bare)
    rows = []
    for (pid, cell, T), eps in sorted(col["epsBT"].items(),
                                      key=lambda kv: (kv[0][0] or "",
                                                      kv[0][1], kv[0][2])):
        g = adj.gate_cell(eps)
        rows.append([pid or "bare", cell, T, len(eps), round(g["mean"], 4),
                     round(g["cp95"][0], 4), round(g["cp95"][1], 4),
                     int(g["interior"])])
    for (pid, cell), eps in sorted(col["epsA"].items()):
        if pid in adj.SUBSET_B and cell in adj.SWEEP_CELLS:
            g = adj.gate_cell(eps)
            rows.append([pid, cell, 0.7, len(eps), round(g["mean"], 4),
                         round(g["cp95"][0], 4), round(g["cp95"][1], 4),
                         int(g["interior"])])
    w(os.path.join(FS, "p5-temperature-curves.csv"),
      ["personaId", "cell", "temperature", "episodes", "meanRound1Coop",
       "cpLo", "cpHi", "interior"], sorted(rows))

    # ---- swap refusal shares (P5-3b source)
    rows = []
    for (pid, T), (k, n) in sorted(col["refusal"].items()):
        lo, hi = adj._cp_bounds(k, n)
        rows.append([pid, T, k, n, round(k / n, 4), round(lo, 4),
                     round(hi, 4), personas.get(pid, "")])
    w(os.path.join(FS, "p5-swap-refusal.csv"),
      ["personaId", "temperature", "k", "n", "share", "cpLo", "cpHi",
       "leaning"], rows)

    # ---- tier C (gemini) descriptive
    rows = []
    for (pid, cell), eps in sorted(col["tierC"].items()):
        g = adj.gate_cell(eps)
        rows.append([pid, cell, len(eps), round(g["mean"], 4),
                     round(g["cp95"][0], 4), round(g["cp95"][1], 4),
                     int(g["interior"])])
    w(os.path.join(FS, "p5-tierC-gemini.csv"),
      ["personaId", "cell", "episodes", "meanRound1Coop", "cpLo", "cpHi",
       "interior"], rows)

    # ---- bare gate anchors
    bg = adj.bare_gates(runs)
    rows = [[label, g["episodes"], g["k"], g["n"],
             round(g["mean"], 4) if g["mean"] is not None else "",
             round(g["cp95"][0], 4), round(g["cp95"][1], 4),
             int(g["interior"])] for label, g in bg.items()]
    w(os.path.join(FS, "p5-bare-anchors.csv"),
      ["source", "episodes", "k", "n", "mean", "cpLo", "cpHi", "interior"],
      rows)

    # ---- persona-level means per cell (P5-1b source)
    rows = []
    for cell in adj.TIER_A_CELLS:
        for pid in sorted(personas):
            eps = col["epsA"][(pid, cell)]
            rows.append([cell, pid, personas[pid],
                         round(sum(eps) / len(eps), 4)])
    w(os.path.join(FS, "p5-persona-means.csv"),
      ["cell", "personaId", "leaning", "meanRound1Coop"], rows)

    print("analysis-pack CSVs complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
