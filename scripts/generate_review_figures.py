#!/usr/bin/env python3
"""Generate the v6 reviewer figures and enrich the machine-readable summary.

All inputs are already committed post-adjudication analysis artifacts. This
script makes no provider calls and does not change historical verdicts.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.ticker import PercentFormatter

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "docs/paper/figures"
SUBMISSION = ROOT / "docs/analysis/submission"
FIG.mkdir(parents=True, exist_ok=True)


def save(fig: plt.Figure, name: str) -> None:
    fig.savefig(FIG / f"{name}.svg", bbox_inches="tight")
    fig.savefig(FIG / f"{name}.pdf", bbox_inches="tight")
    fig.savefig(FIG / f"{name}.png", dpi=240, bbox_inches="tight")
    plt.close(fig)


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def prompt_delta_figure() -> list[dict[str, str]]:
    rows = load_csv(FIG / "prompt-indexed-delta.csv")
    per = [r for r in rows if r["persona"] != "aggregate"]
    aggregate = {r["level"]: r for r in rows if r["persona"] == "aggregate"}
    personas = [f"p{i:02d}" for i in range(1, 17)] + ["Pool"]
    y = np.arange(len(personas), dtype=float)

    fig, ax = plt.subplots(figsize=(7.25, 5.75))
    for level, marker, offset, label in (
        ("s2a", "o", -0.17, "S2 absent"),
        ("s2p", "s", +0.17, "S2 present"),
    ):
        by_persona = {r["persona"]: r for r in per if r["level"] == level}
        series = [by_persona[p] for p in personas[:-1]] + [aggregate[level]]
        delta = np.array([float(r["delta"]) for r in series])
        lo = np.array([float(r["lo95"]) for r in series])
        hi = np.array([float(r["hi95"]) for r in series])
        ax.errorbar(
            delta,
            y + offset,
            xerr=[delta - lo, hi - delta],
            fmt=marker,
            markersize=4.8,
            capsize=2.0,
            elinewidth=0.85,
            label=label,
        )
    ax.axvline(0, linewidth=0.9)
    ax.axhline(15.5, linewidth=0.7)
    ax.set_yticks(y)
    ax.set_yticklabels(personas, fontsize=7.5)
    ax.get_yticklabels()[-1].set_fontweight("bold")
    ax.invert_yaxis()
    ax.set_xlim(-1.05, 1.05)
    ax.set_xlabel(r"Observed prompt-indexed difference $\Delta_i$")
    ax.set_title(
        "Continuation-probability response by prompt configuration",
        loc="left",
        fontweight="bold",
    )
    ax.legend(frameon=False, loc="lower right")
    ax.grid(axis="x", alpha=0.22)
    fig.subplots_adjust(top=0.92, left=0.10, right=0.985, bottom=0.10)
    save(fig, "prompt-indexed-delta")
    return rows


def condition_mean_figure(variance: list[dict[str, str]]) -> None:
    by = {r["cell"]: r for r in variance}
    fig, ax = plt.subplots(figsize=(6.85, 4.15))
    xs = np.array([0.10, 0.90])
    for level, label, marker in (
        ("s2a", "S2 absent", "o"),
        ("s2p", "S2 present", "s"),
    ):
        values = [
            float(by[f"rep-d10-{level}"]["poolMean"]),
            float(by[f"rep-d90-{level}"]["poolMean"]),
        ]
        ax.plot(xs, values, marker=marker, linewidth=1.8, markersize=6.5, label=label)
        ax.annotate(
            f"{values[0]:.3f}",
            (xs[0], values[0]),
            xytext=(-7, 8),
            textcoords="offset points",
            ha="right",
            fontsize=8,
        )
        ax.annotate(
            f"{values[1]:.3f}",
            (xs[1], values[1]),
            xytext=(7, 0),
            textcoords="offset points",
            va="center",
            fontsize=8,
        )
    ax.set_xlim(0.04, 0.98)
    ax.set_xticks(xs, labels=["0.10", "0.90"])
    ax.set_ylim(0, 1)
    ax.yaxis.set_major_formatter(PercentFormatter(1.0))
    ax.set_ylabel("Round-one cooperation")
    ax.set_xlabel("Continuation probability")
    ax.set_title(
        "Fixed-panel cooperation levels across the incentive lever",
        loc="left",
        fontweight="bold",
    )
    ax.legend(frameon=False)
    ax.grid(axis="y", alpha=0.22)
    save(fig, "condition-means")


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
        "Historical seat-level gate",
        "Percentile cluster-bootstrap gate\n(retained, non-primary)",
        "Conservative exact-episode gate\n(primary sensitivity)",
    ]
    p_values = np.array([0.059230, 0.043455, 0.773206])
    intervals = np.array(
        [
            [0.058194, 0.060268],
            [0.042561, 0.044353],
            [0.771363, 0.775039],
        ]
    )
    y = np.arange(3)
    fig, ax = plt.subplots(figsize=(7.2, 4.25))
    ax.errorbar(
        p_values,
        y,
        xerr=[p_values - intervals[:, 0], intervals[:, 1] - p_values],
        fmt="o",
        markersize=6.5,
        capsize=4,
        linewidth=1.4,
    )
    ax.axvline(0.05, linestyle="--", linewidth=1)
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlim(0, 0.82)
    ax.set_xlabel("Familywise permutation p-value (200,000 permutations)")
    ax.set_title("Post-adjudication p13 audit is gate-dependent", loc="left", fontweight="bold")
    ax.grid(axis="x", alpha=0.20)
    for idx, value in enumerate(p_values):
        offset = 0.012 if value < 0.70 else -0.010
        ha = "left" if value < 0.70 else "right"
        ax.text(value + offset, idx, f"{value:.3f}", va="center", ha=ha, fontsize=8)
    fig.subplots_adjust(left=0.31, right=0.98, top=0.88, bottom=0.16)
    save(fig, "p13-audit")


def update_summary(delta_rows: list[dict[str, str]]) -> None:
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
    summary.setdefault("results", {})["promptIndexedDelta"] = {
        "status": "post-adjudication dependence-aware descriptive analysis",
        "unit": (
            "complete episode; prompt-indexed coupling, not a person-level effect "
            "without latent-person invariance"
        ),
        "aggregate": {r["wording"]: r for r in records if r["prompt"] == "aggregate"},
        "perPrompt": [r for r in records if r["prompt"] != "aggregate"],
        "source": "docs/paper/figures/prompt-indexed-delta.csv",
    }
    path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> int:
    delta_rows = prompt_delta_figure()
    variance = load_csv(SUBMISSION / "figure-sources/variance-correction.csv")
    condition_mean_figure(variance)
    between_share_figure(variance)
    representation_figure()
    p13_figure()
    update_summary(delta_rows)
    print("generate_review_figures: wrote five figure sets and promptIndexedDelta summary")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
