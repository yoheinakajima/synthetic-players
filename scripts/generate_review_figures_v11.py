#!/usr/bin/env python3
"""Generate v11 figures from committed post-adjudication data. Zero calls."""
from __future__ import annotations

import csv
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
SUB = ROOT / "docs/analysis/submission"
SRC = SUB / "figure-sources"
FIG.mkdir(parents=True, exist_ok=True)
COLORS = {"s2a": "#1f77b4", "s2p": "#d95f02"}
ALPHA = 0.05


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def save(fig: plt.Figure, name: str) -> None:
    fig.savefig(FIG / f"{name}.svg", bbox_inches="tight")
    fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(FIG / f"{name}.png", dpi=240, bbox_inches="tight")
    plt.close(fig)


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
    n = len(values)
    count_half = sum(value == 0.5 for value in values)
    count_one = sum(value == 1.0 for value in values)
    component_alpha = alpha / 2
    a_lo, a_hi = cp_two_sided(count_half + count_one, n, component_alpha)
    b_lo, b_hi = cp_two_sided(count_one, n, component_alpha)
    return (a_lo + b_lo) / 2, (a_hi + b_hi) / 2


def prompt_delta_figure() -> None:
    rows = load_csv(FIG / "prompt-indexed-delta.csv")
    per_prompt = [row for row in rows if row["persona"] != "aggregate"]
    aggregate = {row["level"]: row for row in rows if row["persona"] == "aggregate"}
    row_labels = [f"p{index:02d}" for index in range(1, 17)] + ["Fixed-panel aggregate"]
    y = np.arange(len(row_labels), dtype=float)

    fig, ax = plt.subplots(figsize=(7.25, 5.9))
    for level, marker, offset, label in (
        ("s2a", "o", -0.23, "S2 absent"),
        ("s2p", "s", 0.23, "S2 present"),
    ):
        by_prompt = {
            row["persona"]: row for row in per_prompt if row["level"] == level
        }
        records = [by_prompt[prompt] for prompt in row_labels[:-1]]
        delta = np.array([float(row["delta"]) for row in records])
        lo = np.array([float(row["lo95"]) for row in records])
        hi = np.array([float(row["hi95"]) for row in records])
        ax.errorbar(
            delta,
            y[:-1] + offset,
            xerr=[delta - lo, hi - delta],
            fmt=marker,
            color=COLORS[level],
            ecolor=COLORS[level],
            markersize=4.8,
            capsize=2.2,
            elinewidth=0.9,
        )
        summary = aggregate[level]
        point = float(summary["delta"])
        lower = float(summary["lo95"])
        upper = float(summary["hi95"])
        ax.errorbar(
            [point],
            [y[-1] + offset],
            xerr=[[point - lower], [upper - point]],
            fmt="D",
            color=COLORS[level],
            ecolor=COLORS[level],
            markersize=6.4,
            capsize=2.8,
            elinewidth=1.3,
        )

    ax.axvline(0, linewidth=0.9, color="0.35")
    ax.axhline(15.5, linewidth=0.7, color="0.65")
    ax.set_yticks(y, row_labels, fontsize=7.5)
    ax.get_yticklabels()[-1].set_fontweight("bold")
    ax.invert_yaxis()
    ax.set_xlim(-1.05, 1.05)
    ax.set_xlabel(r"Observed prompt-indexed difference $\Delta_i$")
    ax.set_title(
        "Continuation-probability response by prompt configuration",
        loc="left",
        fontweight="bold",
    )
    ax.legend(
        handles=[
            Line2D([0], [0], marker="o", color=COLORS["s2a"], linestyle="none", label="S2 absent"),
            Line2D([0], [0], marker="s", color=COLORS["s2p"], linestyle="none", label="S2 present"),
            Line2D([0], [0], marker="D", color="0.25", linestyle="none", label="Fixed-panel aggregate"),
        ],
        frameon=False,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.10),
        ncol=3,
        fontsize=8,
    )
    ax.grid(axis="x", alpha=0.22)
    fig.subplots_adjust(top=0.92, left=0.15, right=0.985, bottom=0.18)
    save(fig, "prompt-indexed-delta")


def condition_mean_figure() -> None:
    variance = {
        row["cell"]: row for row in load_csv(SRC / "variance-correction.csv")
    }
    episode_rows = load_csv(SRC / "episode-cluster-cells.csv")
    by_cell: dict[str, list[float]] = {}
    for row in episode_rows:
        by_cell.setdefault(row["cell"], []).extend(values_from_episode_row(row))

    fig, ax = plt.subplots(figsize=(6.85, 4.2))
    nominal_x = np.array([0.10, 0.90])
    for level, label, marker, offset in (
        ("s2a", "S2 absent", "o", -0.012),
        ("s2p", "S2 present", "s", 0.012),
    ):
        cells = [f"rep-d10-{level}", f"rep-d90-{level}"]
        values = np.array([float(variance[cell]["poolMean"]) for cell in cells])
        intervals = [condition_interval(by_cell[cell], ALPHA / 2) for cell in cells]
        lo = np.array([interval[0] for interval in intervals])
        hi = np.array([interval[1] for interval in intervals])
        x = nominal_x + offset
        ax.errorbar(
            x,
            values,
            yerr=[values - lo, hi - values],
            marker=marker,
            color=COLORS[level],
            ecolor=COLORS[level],
            linewidth=1.8,
            markersize=6.5,
            capsize=4,
            label=label,
        )
        for x_value, value in zip(x, values):
            ax.annotate(
                f"{100 * value:.1f}%",
                (x_value, value),
                xytext=(7, 6),
                textcoords="offset points",
                fontsize=8,
            )

    ax.set_xlim(0.04, 0.98)
    ax.set_xticks(nominal_x, labels=["0.10", "0.90"])
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


def between_share_figure() -> None:
    rows = load_csv(SRC / "variance-uncertainty-v11.csv")
    labels = [
        "δ=.10\nS2 absent",
        "δ=.10\nS2 present",
        "δ=.90\nS2 absent",
        "δ=.90\nS2 present",
    ]
    x = np.arange(4, dtype=float)
    point = np.array([float(row["pointBetweenShare"]) for row in rows])
    fixed_lo = np.array([float(row["conditionalEpisodeShareLo"]) for row in rows])
    fixed_hi = np.array([float(row["conditionalEpisodeShareHi"]) for row in rows])
    median = np.array([float(row["latentJeffreysShareMedian"]) for row in rows])
    latent_lo = np.array([float(row["latentJeffreysShareLo"]) for row in rows])
    latent_hi = np.array([float(row["latentJeffreysShareHi"]) for row in rows])

    fig, ax = plt.subplots(figsize=(7.1, 4.45))
    ax.errorbar(
        x - 0.08,
        point,
        yerr=[point - fixed_lo, fixed_hi - point],
        fmt="o",
        markersize=6.3,
        capsize=4,
        linewidth=1.2,
        label="Plug-in + conditional episode bootstrap",
    )
    ax.errorbar(
        x + 0.08,
        median,
        yerr=[median - latent_lo, latent_hi - median],
        fmt="s",
        markerfacecolor="white",
        markersize=6.3,
        capsize=4,
        linewidth=1.8,
        label="Fixed-panel latent-propensity posterior",
    )
    ax.set_xticks(x, labels)
    ax.set_ylim(0.40, 1.02)
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    ax.set_ylabel("Between-prompt share")
    ax.set_title(
        "Boundary-policy uncertainty lowers and widens the composition estimate",
        loc="left",
        fontweight="bold",
    )
    ax.grid(axis="y", alpha=0.22)
    ax.legend(frameon=False, fontsize=8, loc="lower right")
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
    for index, value in enumerate(values):
        ax.text(index, value + 0.025, f"{value * 100:.1f}%", ha="center", fontsize=8)
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


def family_audit_figure() -> None:
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
    fig, ax = plt.subplots(figsize=(7.2, 4.25))
    y = np.arange(3)
    for index, (value, interval, marker) in enumerate(
        zip(p_values, intervals, ("o", "o", "^"))
    ):
        ax.errorbar(
            [value],
            [index],
            xerr=[[value - interval[0]], [interval[1] - value]],
            fmt=marker,
            markersize=6.5,
            capsize=4,
            linewidth=1.4,
        )
    ax.axvline(0.05, linestyle="--", linewidth=1, color="0.25")
    ax.text(
        0.05,
        2.48,
        "p = 0.05",
        rotation=90,
        ha="right",
        va="bottom",
        fontsize=7,
        color="0.25",
    )
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
    ax.set_title(
        "Post-adjudication family-audit constructions",
        loc="left",
        fontweight="bold",
    )
    ax.grid(axis="x", alpha=0.20)
    for index, value in enumerate(p_values):
        ax.text(
            value + (0.012 if value < 0.70 else -0.010),
            index,
            f"{value:.3f}",
            va="center",
            ha="left" if value < 0.70 else "right",
            fontsize=8,
        )
    fig.subplots_adjust(left=0.36, right=0.98, top=0.88, bottom=0.16)
    save(fig, "p13-audit")


def main() -> int:
    prompt_delta_figure()
    condition_mean_figure()
    between_share_figure()
    representation_figure()
    family_audit_figure()
    print("generate_review_figures_v11: wrote five figures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
