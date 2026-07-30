#!/usr/bin/env python3
"""Generate reviewer figures and enrich the machine-readable summary.

All inputs are committed post-adjudication analysis artifacts. This script makes
no provider calls and does not change historical verdicts.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.ticker import PercentFormatter
from scipy.stats import beta

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "docs/paper/figures"
SUBMISSION = ROOT / "docs/analysis/submission"
EPISODE_CELLS = SUBMISSION / "figure-sources/episode-cluster-cells.csv"
FIG.mkdir(parents=True, exist_ok=True)

ALPHA = 0.05
COLORS = {"s2a": "#1f77b4", "s2p": "#d95f02"}


def save(fig: plt.Figure, name: str) -> None:
    fig.savefig(FIG / f"{name}.svg", bbox_inches="tight")
    fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(FIG / f"{name}.png", dpi=240, bbox_inches="tight")
    plt.close(fig)


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def cp_two_sided(k: int, n: int, alpha: float) -> tuple[float, float]:
    lo = 0.0 if k == 0 else float(beta.ppf(alpha / 2, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - alpha / 2, k + 1, n - k))
    return lo, hi


def values_from_episode_row(row: dict[str, str]) -> list[float]:
    return (
        [0.0] * int(row["episodeCounts0"])
        + [0.5] * int(row["episodeCountsHalf"])
        + [1.0] * int(row["episodeCounts1"])
    )


def condition_interval(values: list[float], alpha: float) -> tuple[float, float]:
    """Conservative projected interval for Y in {0,.5,1}."""
    n = len(values)
    c1 = sum(v == 0.5 for v in values)
    c2 = sum(v == 1.0 for v in values)
    component_alpha = alpha / 2
    a_lo, a_hi = cp_two_sided(c1 + c2, n, component_alpha)
    b_lo, b_hi = cp_two_sided(c2, n, component_alpha)
    return (a_lo + b_lo) / 2, (a_hi + b_hi) / 2


def prompt_delta_figure() -> list[dict[str, str]]:
    rows = load_csv(FIG / "prompt-indexed-delta.csv")
    per = [r for r in rows if r["persona"] != "aggregate"]
    aggregate = {r["level"]: r for r in rows if r["persona"] == "aggregate"}
    row_labels = [f"p{i:02d}" for i in range(1, 17)] + ["Fixed-panel aggregate"]
    y = np.arange(len(row_labels), dtype=float)

    fig, ax = plt.subplots(figsize=(7.25, 5.75))
    series = (
        ("s2a", "o", -0.17, "S2 absent"),
        ("s2p", "s", +0.17, "S2 present"),
    )
    for level, marker, offset, label in series:
        color = COLORS[level]
        by_persona = {r["persona"]: r for r in per if r["level"] == level}
        records = [by_persona[p] for p in row_labels[:-1]]
        delta = np.array([float(r["delta"]) for r in records])
        lo = np.array([float(r["lo95"]) for r in records])
        hi = np.array([float(r["hi95"]) for r in records])
        ax.errorbar(
            delta,
            y[:-1] + offset,
            xerr=[delta - lo, hi - delta],
            fmt=marker,
            color=color,
            ecolor=color,
            markersize=4.8,
            capsize=2.0,
            elinewidth=0.85,
            label=label,
        )
        agg = aggregate[level]
        point = float(agg["delta"])
        agg_lo = float(agg["lo95"])
        agg_hi = float(agg["hi95"])
        ax.errorbar(
            [point],
            [y[-1] + offset],
            xerr=[[point - agg_lo], [agg_hi - point]],
            fmt="D",
            color=color,
            ecolor=color,
            markersize=6.3,
            capsize=2.5,
            elinewidth=1.25,
        )
    ax.axvline(0, linewidth=0.9, color="0.35")
    ax.axhline(15.5, linewidth=0.7, color="0.65")
    ax.set_yticks(y)
    ax.set_yticklabels(row_labels, fontsize=7.5)
    ax.get_yticklabels()[-1].set_fontweight("bold")
    ax.invert_yaxis()
    ax.set_xlim(-1.05, 1.05)
    ax.set_xlabel(r"Observed prompt-indexed difference $\Delta_i$")
    ax.set_title(
        "Continuation-probability response by prompt configuration",
        loc="left",
        fontweight="bold",
    )
    handles = [
        Line2D([0], [0], marker="o", color=COLORS["s2a"], linestyle="none", label="S2 absent"),
        Line2D([0], [0], marker="s", color=COLORS["s2p"], linestyle="none", label="S2 present"),
        Line2D([0], [0], marker="D", color="0.25", linestyle="none", label="Fixed-panel aggregate"),
    ]
    ax.legend(handles=handles, frameon=False, loc="lower right")
    ax.grid(axis="x", alpha=0.22)
    fig.subplots_adjust(top=0.92, left=0.15, right=0.985, bottom=0.10)
    save(fig, "prompt-indexed-delta")
    return rows


def condition_mean_figure(variance: list[dict[str, str]]) -> list[dict[str, object]]:
    by = {r["cell"]: r for r in variance}
    episode_rows = load_csv(EPISODE_CELLS)
    by_cell: dict[str, list[float]] = {}
    for row in episode_rows:
        by_cell.setdefault(row["cell"], []).extend(values_from_episode_row(row))

    fig, ax = plt.subplots(figsize=(6.85, 4.15))
    xs = np.array([0.10, 0.90])
    output: list[dict[str, object]] = []
    for level, label, marker in (
        ("s2a", "S2 absent", "o"),
        ("s2p", "S2 present", "s"),
    ):
        color = COLORS[level]
        cells = [f"rep-d10-{level}", f"rep-d90-{level}"]
        values = np.array([float(by[cell]["poolMean"]) for cell in cells])
        intervals = [condition_interval(by_cell[cell], ALPHA / 2) for cell in cells]
        lo = np.array([x[0] for x in intervals])
        hi = np.array([x[1] for x in intervals])
        ax.errorbar(
            xs,
            values,
            yerr=[values - lo, hi - values],
            marker=marker,
            color=color,
            ecolor=color,
            linewidth=1.8,
            markersize=6.5,
            capsize=4,
            label=label,
        )
        for idx, value in enumerate(values):
            ax.annotate(
                f"{value:.3f}",
                (xs[idx], value),
                xytext=(-7 if idx == 0 else 7, 8 if idx == 0 else 0),
                textcoords="offset points",
                ha="right" if idx == 0 else "left",
                va="bottom" if idx == 0 else "center",
                fontsize=8,
            )
            output.append(
                {
                    "wording": level,
                    "delta": 0.10 if idx == 0 else 0.90,
                    "n": len(by_cell[cells[idx]]),
                    "mean": float(value),
                    "simultaneous95": [float(lo[idx]), float(hi[idx])],
                }
            )
    ax.set_xlim(0.04, 0.98)
    ax.set_xticks(xs, labels=["0.10", "0.90"])
    ax.set_ylim(0, 1)
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    ax.set_ylabel("Round-one cooperation")
    ax.set_xlabel("Represented continuation probability")
    ax.set_title(
        "Fixed-panel cooperation levels across the represented treatment",
        loc="left",
        fontweight="bold",
    )
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.22)
    save(fig, "condition-means")
    return output


def between_share_figure(variance: list[dict[str, str]]) -> None:
    labels = [
        "δ=.10\nS2 absent",
        "δ=.10\nS2 present",
        "δ=.90\nS2 absent",
        "δ=.90\nS2 present",
    ]
    shares = np.array([float(r["betweenShare"]) for r in variance])
    lo = np.array([float(r["fixedPanelBetweenShareLo"]) for r in variance])
    hi = np.array([float(r["fixedPanelBetweenShareHi"]) for r in variance])
    fig, ax = plt.subplots(figsize=(7.0, 4.15))
    x = np.arange(4)
    ax.errorbar(
        x,
        shares,
        yerr=[shares - lo, hi - shares],
        fmt="o",
        markersize=6.5,
        capsize=4,
        linewidth=1.4,
    )
    ax.set_xticks(x, labels)
    ax.set_ylim(0.70, 1.01)
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    ax.set_ylabel("Corrected between-prompt share")
    ax.set_title(
        "Most recorded episode-level variation lies between prompt configurations",
        loc="left",
        fontweight="bold",
    )
    ax.grid(axis="y", alpha=0.22)
    for idx, value in enumerate(shares):
        ax.text(idx, value + 0.012, f"{value * 100:.1f}%", ha="center", fontsize=8)
    save(fig, "between-prompt-share")


def representation_figure() -> None:
    labels = [
        "S2 absent:\ncooperate",
        "S2 present:\ncooperate",
        "Label conflict:\npayoff-dominant action",
        "Label conflict:\n‘Defect’-worded action",
    ]
    values = [0.0, 0.925, 0.0, 1.0]
    fig, ax = plt.subplots(figsize=(7.2, 4.4))
    x = np.arange(len(values))
    ax.bar(x, values)
    ax.set_xticks(x, labels, fontsize=8)
    ax.set_ylim(0, 1.08)
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    ax.set_ylabel("Observed selection share")
    ax.set_title(
        "Local representation changes can move behavior between opposite corners",
        loc="left",
        fontweight="bold",
    )
    ax.grid(axis="y", alpha=0.20)
    for idx, value in enumerate(values):
        ax.text(idx, value + 0.025, f"{value * 100:.1f}%", ha="center", fontsize=8)
    ax.text(
        0.5,
        -0.22,
        "Repeated-game wording switch",
        transform=ax.get_xaxis_transform(),
        ha="center",
        fontsize=8,
    )
    ax.text(
        2.5,
        -0.22,
        "One-shot semantic-label/payoff conflict",
        transform=ax.get_xaxis_transform(),
        ha="center",
        fontsize=8,
    )
    fig.subplots_adjust(bottom=0.26)
    save(fig, "representation-effects")


def p13_figure() -> None:
    labels = [
        "Historical seat gate\np13/s2a max",
        "Percentile-bootstrap sensitivity\np13/s2a max",
        "Exact episode sensitivity\np13 ineligible; p05/s2a max",
    ]
    p_values = np.array([0.059230, 0.043455, 0.773206])
    intervals = np.array(
        [
            [0.058194, 0.060268],
            [0.042561, 0.044353],
            [0.771363, 0.775039],
        ]
    )
    markers = ("o", "o", "^")
    y = np.arange(3)
    fig, ax = plt.subplots(figsize=(7.2, 4.25))
    for idx, (value, interval, marker) in enumerate(zip(p_values, intervals, markers)):
        ax.errorbar(
            [value],
            [idx],
            xerr=[[value - interval[0]], [interval[1] - value]],
            fmt=marker,
            markersize=6.5,
            capsize=4,
            linewidth=1.4,
        )
    ax.axvline(0.05, linestyle="--", linewidth=1, color="0.25")
    exact_floor = 0.075040
    ax.vlines(exact_floor, 1.62, 2.38, linestyle=":", linewidth=1.4, color="0.42")
    ax.text(
        exact_floor + 0.008,
        2.34,
        "archived exact-gate\nattainable boundary",
        fontsize=7,
        va="bottom",
        color="0.32",
    )
    ax.set_yticks(y, labels)
    ax.set_ylim(2.62, -0.62)
    ax.set_xlim(0, 0.82)
    ax.set_xlabel("Familywise permutation p-value (200,000 permutations)")
    ax.set_title("Post-adjudication family-audit constructions", loc="left", fontweight="bold")
    ax.grid(axis="x", alpha=0.20)
    for idx, value in enumerate(p_values):
        offset = 0.012 if value < 0.70 else -0.010
        ha = "left" if value < 0.70 else "right"
        ax.text(value + offset, idx, f"{value:.3f}", va="center", ha=ha, fontsize=8)
    fig.subplots_adjust(left=0.36, right=0.98, top=0.88, bottom=0.16)
    save(fig, "p13-audit")


def update_summary(
    delta_rows: list[dict[str, str]],
    condition_rows: list[dict[str, object]],
) -> None:
    path = SUBMISSION / "submission-analysis-summary.json"
    summary = json.loads(path.read_text(encoding="utf-8"))
    records = []
    for row in delta_rows:
        records.append(
            {
                "wording": row["level"],
                "prompt": row["persona"],
                "n_d10": int(row["n_d10"]),
                "n_d90": int(row["n_d90"]),
                "mean_d10": float(row["mean_d10"]),
                "mean_d90": float(row["mean_d90"]),
                "delta": float(row["delta"]),
                "simultaneous95": [float(row["lo95"]), float(row["hi95"])],
            }
        )
    results = summary.setdefault("results", {})
    results["promptIndexedDelta"] = {
        "status": "post-adjudication dependence-aware descriptive analysis",
        "unit": (
            "complete episode; prompt-indexed coupling, not a person-level effect "
            "without latent-person invariance"
        ),
        "aggregate": {r["wording"]: r for r in records if r["prompt"] == "aggregate"},
        "perPrompt": [r for r in records if r["prompt"] != "aggregate"],
        "source": "docs/paper/figures/prompt-indexed-delta.csv",
    }
    results["conditionMeansExact"] = {
        "status": "post-adjudication conservative exact condition intervals",
        "unit": "complete episode",
        "records": condition_rows,
        "source": "docs/analysis/submission/figure-sources/episode-cluster-cells.csv",
    }
    path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    delta_rows = prompt_delta_figure()
    variance = load_csv(SUBMISSION / "figure-sources/variance-correction.csv")
    condition_rows = condition_mean_figure(variance)
    between_share_figure(variance)
    representation_figure()
    p13_figure()
    update_summary(delta_rows, condition_rows)
    print("generate_review_figures: wrote v8 figure sets and machine-readable interval summaries")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
