#!/usr/bin/env python3
"""Final reviewer-facing polish for the generated v7 package.

Runs after Round 5 integration and figure generation. It removes stale v6 or
pre-Explore-Science wording from living surfaces and regenerates Figure 5
without a redundant annotation. Sealed/history/reviewer-source artifacts are
not edited.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "docs" / "paper" / "paper-draft.md"
PDF_README = ROOT / "docs" / "paper" / "PDF-README.md"
README = ROOT / "README.md"
REVIEW = ROOT / "REVIEW.md"
STATUS = ROOT / "docs" / "analysis" / "submission-blockers.md"
EPISODE = ROOT / "docs" / "analysis" / "submission" / "episode-cluster-sensitivity.md"
FIG = ROOT / "docs" / "paper" / "figures"


def replace_all(path: Path, replacements: list[tuple[str, str]]) -> None:
    text = path.read_text(encoding="utf-8")
    for old, new in replacements:
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")


def polish_paper() -> None:
    replace_all(PAPER, [
        ("the primary exact sensitivity writes", "the conservative exact sensitivity writes"),
        ("The primary exact episode-level interval classifies", "The conservative exact episode-level interval classifies"),
        (
            "Because no length-, punctuation-, and position-matched non-semantic prefix was run, this prefix contrast cannot isolate semantic persona presence from generic sequence-length or displacement effects.",
            "Because no non-semantic prefix matched for length, punctuation, and position was run, this prefix contrast cannot isolate semantic persona presence from generic sequence-length or displacement effects.",
        ),
        (
            "Discovery-forward “One Persona in Sixteen” was rejected because p13 does not survive primary episode-level inference.",
            "Discovery-forward “One Persona in Sixteen” was rejected because the frozen rule lacked prospective family control and the conservative post-adjudication procedure is too underpowered for decisive confirmation or disconfirmation.",
        ),
        (
            "All three 200,000-permutation variants reported: historical seat gate \\(p=0.059230\\); retained percentile cluster-bootstrap gate \\(p=0.043455\\); primary exact-episode gate excludes p13 and yields max \\(p=0.773206\\)",
            "All three 200,000-permutation variants reported: historical seat gate \\(p=0.059230\\); percentile-bootstrap sensitivity \\(p=0.043455\\); conservative exact-episode sensitivity makes p13 ineligible and attributes the maximum eligible result to p05/s2a, \\(p=0.773206\\); none was prospectively family-controlled",
        ),
        (
            "Percentile cluster bootstrap retained but rejected as primary because it degenerates at exact corners",
            "Percentile cluster bootstrap retained as a sensitivity; exact projection used as the conservative finite-sample coverage reference",
        ),
    ])


def polish_navigation() -> None:
    replace_all(PDF_README, [
        ("The first formatted reviewer PDF is:", "The current formatted reviewer PDF is:"),
        ("synthetic-players-review-draft-v6.pdf", "synthetic-players-review-draft-v7.pdf"),
        ("STIX Math", "Latin Modern Math"),
    ])
    replace_all(README, [
        (
            "All three post-review family variants are disclosed; the primary exact-episode gate excludes p13. It is a replication target, not a finding.",
            "All three post-review family variants are disclosed. The conservative exact sensitivity makes p13 gate-ineligible but is underpowered at n=6; p13 is neither prospectively confirmed nor decisively disconfirmed and remains a replication target.",
        ),
    ])
    replace_all(REVIEW, [
        ("under the primary exact-episode sensitivity", "under the conservative exact-episode sensitivity"),
        (
            "Three post-review familywise variants are disclosed: `p=0.059230`, retained non-primary percentile-bootstrap `p=0.043455`, and primary exact-episode `p=0.773206` after p13 is excluded by the gate. None was registered at the original freeze; p13 remains only a replication target.",
            "Three post-review familywise variants are disclosed: historical-gate `p=0.059230`, percentile-bootstrap sensitivity `p=0.043455`, and conservative exact sensitivity `p=0.773206` for p05/s2a after p13 becomes gate-ineligible. None was registered at the original freeze, and the exact n=6 family is underpowered; p13 is neither prospectively confirmed nor decisively disconfirmed and remains a replication target.",
        ),
        (
            "including the favorable but non-primary `p=0.043455` result",
            "including the favorable percentile-bootstrap `p=0.043455` sensitivity",
        ),
    ])
    replace_all(STATUS, [
        ("- primary exact-episode count:", "- conservative exact-episode count:"),
        ("COMPLETE FOR v6 REVIEW DRAFT", "COMPLETE FOR v7 REVIEW DRAFT"),
    ])
    replace_all(EPISODE, [
        (
            "The primary episode-level interval is an exact conservative projection",
            "The conservative reference episode-level interval is an exact projection",
        ),
    ])


def regenerate_p13_figure() -> None:
    labels = [
        "Historical seat gate\np13/s2a max",
        "Percentile-bootstrap sensitivity\np13/s2a max",
        "Exact episode sensitivity\np13 ineligible; p05/s2a max",
    ]
    p_values = np.array([0.059230, 0.043455, 0.773206])
    intervals = np.array([
        [0.058194, 0.060268],
        [0.042561, 0.044353],
        [0.771363, 0.775039],
    ])
    markers = ("o", "o", "^")
    y = np.arange(3)
    fig, ax = plt.subplots(figsize=(7.2, 4.25))
    for idx, (value, interval, marker) in enumerate(zip(p_values, intervals, markers)):
        ax.errorbar(
            [value], [idx],
            xerr=[[value - interval[0]], [interval[1] - value]],
            fmt=marker, markersize=6.5, capsize=4, linewidth=1.4,
        )
    ax.axvline(0.05, linestyle="--", linewidth=1)
    ax.set_yticks(y, labels)
    ax.invert_yaxis()
    ax.set_xlim(0, 0.82)
    ax.set_xlabel("Familywise permutation p-value (200,000 permutations)")
    ax.set_title("Post-adjudication family-audit constructions", loc="left", fontweight="bold")
    ax.grid(axis="x", alpha=0.20)
    for idx, value in enumerate(p_values):
        offset = 0.012 if value < 0.70 else -0.010
        ha = "left" if value < 0.70 else "right"
        ax.text(value + offset, idx, f"{value:.3f}", va="center", ha=ha, fontsize=8)
    fig.subplots_adjust(left=0.36, right=0.98, top=0.88, bottom=0.16)
    for suffix, kwargs in (
        ("svg", {}),
        ("pdf", {}),
        ("png", {"dpi": 240}),
    ):
        fig.savefig(FIG / f"p13-audit.{suffix}", bbox_inches="tight", **kwargs)
    plt.close(fig)


def main() -> int:
    polish_paper()
    polish_navigation()
    regenerate_p13_figure()
    print("polish_v7_outputs: removed stale language and regenerated clean Figure 5")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
