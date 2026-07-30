#!/usr/bin/env python3
"""Post-adjudication v11 variance-uncertainty sensitivity.

Uses committed episode-category counts only; zero provider calls. The v10
finite-opportunity point estimates and conditional episode bootstrap remain
unchanged. This script adds a fixed-panel latent-propensity posterior under
independent Dirichlet(1/2,1/2,1/2) priors, directly propagating uncertainty
from boundary-concentrated six-episode cells without resampling the prompt
panel. It also surfaces the existing two-stage prompt+episode bootstrap.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SUB = ROOT / "docs/analysis/submission"
FIG = SUB / "figure-sources"
EP = FIG / "episode-cluster-cells.csv"
VAR_CSV = FIG / "variance-correction.csv"
VAR_JSON = FIG / "variance-correction.json"
OUT_CSV = FIG / "variance-uncertainty-v11.csv"
OUT_JSON = FIG / "variance-uncertainty-v11.json"
OUT_MD = SUB / "variance-uncertainty-v11.md"
DRAWS = int(os.environ.get("V11_LATENT_DRAWS", "100000"))
BASE_SEED = 20260730
CELLS = ("rep-d10-s2a", "rep-d10-s2p", "rep-d90-s2a", "rep-d90-s2p")


def quantiles(values):
    arr = np.asarray(values, dtype=float)
    return [float(x) for x in np.quantile(arr, [0.025, 0.5, 0.975])]


def stable_seed(label: str) -> int:
    digest = hashlib.sha256(label.encode()).digest()
    return (int.from_bytes(digest[:8], "big") ^ BASE_SEED) % (2**63 - 1)


def main() -> int:
    episodes = list(csv.DictReader(EP.open(newline="", encoding="utf-8")))
    counts = {
        (row["personaId"], row["cell"]): np.array(
            [row["episodeCounts0"], row["episodeCountsHalf"], row["episodeCounts1"]],
            dtype=float,
        )
        for row in episodes
    }
    base = {
        row["cell"]: row
        for row in csv.DictReader(VAR_CSV.open(newline="", encoding="utf-8"))
    }
    detail = json.loads(VAR_JSON.read_text(encoding="utf-8"))
    rows = []
    machine = {}
    for cell in CELLS:
        rng = np.random.default_rng(stable_seed(cell))
        sd_draws = []
        share_draws = []
        batch = 2500
        for start in range(0, DRAWS, batch):
            n_batch = min(batch, DRAWS - start)
            probabilities = []
            for index in range(1, 17):
                probabilities.append(
                    rng.dirichlet(
                        counts[(f"p{index:02d}", cell)] + 0.5,
                        size=n_batch,
                    )
                )
            posterior = np.stack(probabilities, axis=1)
            means = 0.5 * posterior[:, :, 1] + posterior[:, :, 2]
            second_moments = 0.25 * posterior[:, :, 1] + posterior[:, :, 2]
            within = second_moments - means**2
            between = np.var(means, axis=1, ddof=1)
            average_within = np.mean(within, axis=1)
            sd_draws.extend(np.sqrt(between).tolist())
            share_draws.extend((between / (between + average_within)).tolist())
        sd_quantiles = quantiles(sd_draws)
        share_quantiles = quantiles(share_draws)
        source = base[cell]
        population = detail[cell]["personaPopulationBootstrapExploratory"]
        row = {
            "cell": cell,
            "pointCorrectedSD": float(source["correctedBetweenSD"]),
            "pointBetweenShare": float(source["betweenShare"]),
            "conditionalEpisodeSDlo": float(source["fixedPanelCorrectedSDlo"]),
            "conditionalEpisodeSDhi": float(source["fixedPanelCorrectedSDhi"]),
            "conditionalEpisodeShareLo": float(source["fixedPanelBetweenShareLo"]),
            "conditionalEpisodeShareHi": float(source["fixedPanelBetweenShareHi"]),
            "latentJeffreysSDlo": sd_quantiles[0],
            "latentJeffreysSDmedian": sd_quantiles[1],
            "latentJeffreysSDhi": sd_quantiles[2],
            "latentJeffreysShareLo": share_quantiles[0],
            "latentJeffreysShareMedian": share_quantiles[1],
            "latentJeffreysShareHi": share_quantiles[2],
            "twoStagePromptSDlo": float(population["correctedSD"]["lo95"]),
            "twoStagePromptSDmedian": float(population["correctedSD"]["median"]),
            "twoStagePromptSDhi": float(population["correctedSD"]["hi95"]),
            "twoStagePromptShareLo": float(population["betweenShare"]["lo95"]),
            "twoStagePromptShareMedian": float(population["betweenShare"]["median"]),
            "twoStagePromptShareHi": float(population["betweenShare"]["hi95"]),
            "historicalThresholdSD": float(source["historicalRhoThresholdSD"]),
        }
        rows.append(row)
        machine[cell] = row

    with OUT_CSV.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    OUT_JSON.write_text(
        json.dumps(
            {"draws": DRAWS, "prior": [0.5, 0.5, 0.5], "rows": machine},
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    lines = [
        "# v11 fixed-panel latent-propensity variance sensitivity",
        "",
        "> **STATUS: POST-v10, POST-ADJUDICATION SENSITIVITY — ZERO SUBJECT CALLS.** The registered P5-1b verdict and v10 point estimates are historical and unchanged. This analysis addresses uncertainty suppressed when empirical boundary cells are resampled as point masses.",
        "",
        f"For each prompt/cell, the three episode-outcome probabilities for `{{0, 0.5, 1}}` receive an independent Dirichlet(0.5, 0.5, 0.5) prior. Across **{DRAWS:,}** posterior draws, the script computes prompt-specific latent means, between-prompt SD, expected within-prompt variance, and the between share `B/(B+W)`. This keeps the exact sixteen-prompt panel fixed; it does not resample a persona generator.",
        "",
        "| cell | observed corrected SD | latent SD 95% (median) | observed between share | latent between-share 95% (median) | historical threshold SD |",
        "|---|---:|---|---:|---|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['cell']} | {row['pointCorrectedSD']:.4f} | "
            f"[{row['latentJeffreysSDlo']:.4f}, {row['latentJeffreysSDhi']:.4f}] "
            f"({row['latentJeffreysSDmedian']:.4f}) | {row['pointBetweenShare']:.3f} | "
            f"[{row['latentJeffreysShareLo']:.3f}, {row['latentJeffreysShareHi']:.3f}] "
            f"({row['latentJeffreysShareMedian']:.3f}) | "
            f"{row['historicalThresholdSD']:.4f} |"
        )
    lines += [
        "",
        "The conditional episode bootstrap, this latent-propensity posterior, and the two-stage prompt+episode bootstrap answer different questions. None is promoted retroactively into the frozen confirmatory rule.",
    ]
    OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"rows": rows}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
