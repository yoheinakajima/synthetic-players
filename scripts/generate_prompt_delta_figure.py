#!/usr/bin/env python3
"""Generate the paper's prompt-indexed continuation-probability response figure.

The figure uses complete episodes as the inferential unit. For each condition,
the three-valued episode outcome Y∈{0,.5,1} is decomposed as
Y=(1[Y>=.5]+1[Y=1])/2. Bonferroni-adjusted Clopper-Pearson intervals are
constructed across both components and both δ conditions, then projected onto
the difference. This keeps intervals non-degenerate at observed corners.
"""
from __future__ import annotations

import csv
import html
from pathlib import Path

from scipy.stats import beta

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs/analysis/submission/figure-sources/episode-cluster-cells.csv"
OUT_DIR = ROOT / "docs/paper/figures"
OUT_CSV = OUT_DIR / "prompt-indexed-delta.csv"
OUT_SVG = OUT_DIR / "prompt-indexed-delta.svg"
ALPHA = 0.05
LEVELS = (("s2a", "S2 absent"), ("s2p", "S2 present"))


def cp_two_sided(k: int, n: int, alpha: float) -> tuple[float, float]:
    lo = 0.0 if k == 0 else float(beta.ppf(alpha / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - alpha / 2, k + 1, n - k))
    return lo, hi


def values_from_row(row: dict[str, str]) -> list[float]:
    return (
        [0.0] * int(row["episodeCounts0"])
        + [0.5] * int(row["episodeCountsHalf"])
        + [1.0] * int(row["episodeCounts1"])
    )


def condition_interval(values: list[float], alpha: float) -> tuple[float, float]:
    n = len(values)
    c1 = sum(v == 0.5 for v in values)
    c2 = sum(v == 1.0 for v in values)
    # This condition receives half the total family error. Its A/B components
    # split that amount again inside two-sided CP intervals.
    component_alpha = alpha / 2
    a_lo, a_hi = cp_two_sided(c1 + c2, n, component_alpha)
    b_lo, b_hi = cp_two_sided(c2, n, component_alpha)
    return (a_lo + b_lo) / 2, (a_hi + b_hi) / 2


def difference_record(persona: str, level: str, v10: list[float], v90: list[float]) -> dict[str, object]:
    # Bonferroni over the two δ conditions: each condition interval gets α/2.
    lo10, hi10 = condition_interval(v10, ALPHA / 2)
    lo90, hi90 = condition_interval(v90, ALPHA / 2)
    m10 = sum(v10) / len(v10)
    m90 = sum(v90) / len(v90)
    return {
        "level": level,
        "persona": persona,
        "n_d10": len(v10),
        "n_d90": len(v90),
        "mean_d10": m10,
        "mean_d90": m90,
        "delta": m90 - m10,
        "lo95": lo90 - hi10,
        "hi95": hi90 - lo10,
    }


def load_records() -> list[dict[str, object]]:
    with SOURCE.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    by_key = {(r["personaId"], r["cell"]): r for r in rows}
    personas = sorted({r["personaId"] for r in rows})
    out: list[dict[str, object]] = []
    for level, _label in LEVELS:
        all10: list[float] = []
        all90: list[float] = []
        for persona in personas:
            v10 = values_from_row(by_key[(persona, f"rep-d10-{level}")])
            v90 = values_from_row(by_key[(persona, f"rep-d90-{level}")])
            all10.extend(v10)
            all90.extend(v90)
            out.append(difference_record(persona, level, v10, v90))
        out.append(difference_record("aggregate", level, all10, all90))
    return out


def write_csv(records: list[dict[str, object]]) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fields = ["level", "persona", "n_d10", "n_d90", "mean_d10", "mean_d90", "delta", "lo95", "hi95"]
    with OUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in records:
            writer.writerow({k: (f"{v:.6f}" if isinstance(v, float) else v) for k, v in row.items()})


def write_svg(records: list[dict[str, object]]) -> None:
    width, height = 1120, 920
    left, right = 150, 55
    plot_left, plot_right = left, width - right
    axis_y = height - 55
    row_h = 22
    panel_top = {"s2a": 92, "s2p": 495}
    panel_color = {"s2a": "#2563eb", "s2p": "#c2410c"}
    labels = dict(LEVELS)

    def x(value: float) -> float:
        return plot_left + (value + 1) / 2 * (plot_right - plot_left)

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<style>text{font-family:Inter,Arial,sans-serif;fill:#17202a}.title{font-size:24px;font-weight:700}.sub{font-size:13px;fill:#566573}.panel{font-size:17px;font-weight:700}.lab{font-size:12px}.tick{font-size:11px;fill:#566573}.agg{font-size:12px;font-weight:700}</style>',
        '<text x="55" y="38" class="title">Prompt-indexed continuation-probability responses</text>',
        '<text x="55" y="61" class="sub">Δ = round-one cooperation at δ=.90 minus δ=.10; bars are conservative exact simultaneous 95% intervals</text>',
    ]
    for tick in (-1, -0.5, 0, 0.5, 1):
        xx = x(tick)
        parts.append(f'<line x1="{xx:.1f}" y1="75" x2="{xx:.1f}" y2="{axis_y}" stroke="#{"8b949e" if tick == 0 else "e5e7eb"}" stroke-width="{2 if tick == 0 else 1}"/>')
        parts.append(f'<text x="{xx:.1f}" y="{axis_y + 22}" text-anchor="middle" class="tick">{tick:+.1f}</text>')

    for level, _ in LEVELS:
        top = panel_top[level]
        color = panel_color[level]
        panel_rows = [r for r in records if r["level"] == level and r["persona"] != "aggregate"]
        aggregate = next(r for r in records if r["level"] == level and r["persona"] == "aggregate")
        parts.append(f'<text x="55" y="{top - 16}" class="panel">{html.escape(labels[level])}</text>')
        for idx, row in enumerate(panel_rows):
            yy = top + idx * row_h
            parts.append(f'<text x="118" y="{yy + 4}" text-anchor="end" class="lab">{html.escape(str(row["persona"]))}</text>')
            lo, hi, point = float(row["lo95"]), float(row["hi95"]), float(row["delta"])
            parts.append(f'<line x1="{x(lo):.1f}" y1="{yy}" x2="{x(hi):.1f}" y2="{yy}" stroke="{color}" stroke-width="2" opacity="0.58"/>')
            parts.append(f'<line x1="{x(lo):.1f}" y1="{yy-4}" x2="{x(lo):.1f}" y2="{yy+4}" stroke="{color}" opacity="0.58"/>')
            parts.append(f'<line x1="{x(hi):.1f}" y1="{yy-4}" x2="{x(hi):.1f}" y2="{yy+4}" stroke="{color}" opacity="0.58"/>')
            parts.append(f'<circle cx="{x(point):.1f}" cy="{yy}" r="4" fill="{color}"/>')
        yy = top + len(panel_rows) * row_h + 7
        parts.append(f'<line x1="55" y1="{yy-12}" x2="{plot_right}" y2="{yy-12}" stroke="#d1d5db"/>')
        parts.append(f'<text x="118" y="{yy+4}" text-anchor="end" class="agg">aggregate</text>')
        lo, hi, point = float(aggregate["lo95"]), float(aggregate["hi95"]), float(aggregate["delta"])
        parts.append(f'<line x1="{x(lo):.1f}" y1="{yy}" x2="{x(hi):.1f}" y2="{yy}" stroke="{color}" stroke-width="4"/>')
        px = x(point)
        parts.append(f'<polygon points="{px:.1f},{yy-7} {px+7:.1f},{yy} {px:.1f},{yy+7} {px-7:.1f},{yy}" fill="{color}"/>')
        parts.append(f'<text x="{plot_right}" y="{yy+4}" text-anchor="end" class="agg">Δ={point:+.3f} [{lo:+.3f}, {hi:+.3f}]</text>')

    parts += [
        f'<text x="{(plot_left + plot_right)/2:.1f}" y="{height-10}" text-anchor="middle" class="lab">Observed prompt-indexed response Δ</text>',
        '</svg>',
    ]
    OUT_SVG.write_text("\n".join(parts) + "\n", encoding="utf-8")


def main() -> int:
    records = load_records()
    write_csv(records)
    write_svg(records)
    for level, label in LEVELS:
        agg = next(r for r in records if r["level"] == level and r["persona"] == "aggregate")
        print(f"{label}: delta={agg['delta']:+.6f} interval=[{agg['lo95']:+.6f}, {agg['hi95']:+.6f}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
