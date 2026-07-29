#!/usr/bin/env python3
"""Separate fixed-panel measurement uncertainty from persona-population uncertainty.

The point estimand in paper one is the dispersion among these sixteen fixed
prompts. Therefore the primary bootstrap keeps all sixteen prompts and resamples
only episodes within each prompt. A two-stage bootstrap that also resamples
prompts is reported separately as an exploratory persona-population interval.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))

from phase5_closeout_adjudicate import (  # noqa: E402
    HUMAN_SD,
    RHO,
    TIER_A_CELLS,
    collect,
    load_personas,
    load_runs,
)

OUT = ROOT / "docs" / "analysis" / "submission"
FIG = OUT / "figure-sources"
BOOTSTRAPS = int(os.environ.get("SUBMISSION_VARIANCE_BOOTSTRAPS", "50000"))
REP_CELLS = tuple(c for c in TIER_A_CELLS if c.startswith("rep-"))
BASE_SEED = 20260729


def seed(label: str) -> int:
    h = hashlib.sha256(label.encode()).digest()
    return (int.from_bytes(h[:8], "big") ^ BASE_SEED) % (2**63 - 1)


def components(data: np.ndarray) -> dict[str, float]:
    means = data.mean(axis=1)
    raw_b = float(np.var(means, ddof=1))
    within_by_prompt = np.var(data, axis=1, ddof=1)
    measurement_noise = float(np.mean(within_by_prompt / data.shape[1]))
    corrected_b = max(0.0, raw_b - measurement_noise)
    w = float(np.mean(within_by_prompt))
    ratio = corrected_b / (corrected_b + w) if corrected_b + w > 0 else float("nan")
    return {
        "rawB": raw_b,
        "measurementNoise": measurement_noise,
        "B": corrected_b,
        "correctedSD": math.sqrt(corrected_b),
        "W": w,
        "betweenShare": ratio,
    }


def summarize(draws: dict[str, list[float]]) -> dict:
    out = {}
    for key, vals in draws.items():
        arr = np.asarray(vals, dtype=float)
        arr = arr[np.isfinite(arr)]
        out[key] = {
            "median": float(np.median(arr)),
            "lo95": float(np.quantile(arr, 0.025)),
            "hi95": float(np.quantile(arr, 0.975)),
        }
    return out


def bootstrap(data: np.ndarray, *, resample_prompts: bool, rng: np.random.Generator) -> dict:
    n_prompt, n_ep = data.shape
    draws = {k: [] for k in ("rawB", "measurementNoise", "B", "correctedSD", "W", "betweenShare")}
    batch = 1000
    done = 0
    while done < BOOTSTRAPS:
        b = min(batch, BOOTSTRAPS - done)
        if resample_prompts:
            pidx = rng.integers(0, n_prompt, size=(b, n_prompt))
            selected = data[pidx]
        else:
            selected = np.broadcast_to(data, (b, n_prompt, n_ep))
        eidx = rng.integers(0, n_ep, size=(b, n_prompt, n_ep))
        sampled = np.take_along_axis(selected, eidx, axis=2)
        means = sampled.mean(axis=2)
        raw = np.var(means, axis=1, ddof=1)
        within = np.var(sampled, axis=2, ddof=1)
        noise = np.mean(within / n_ep, axis=1)
        bcorr = np.maximum(raw - noise, 0)
        w = np.mean(within, axis=1)
        ratio = np.divide(bcorr, bcorr + w, out=np.full_like(bcorr, np.nan), where=(bcorr + w) > 0)
        arrays = {
            "rawB": raw,
            "measurementNoise": noise,
            "B": bcorr,
            "correctedSD": np.sqrt(bcorr),
            "W": w,
            "betweenShare": ratio,
        }
        for key, arr in arrays.items():
            draws[key].extend(arr.tolist())
        done += b
    return summarize(draws)


def write_csv(path: Path, rows: list[dict]) -> None:
    fields = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    runs = load_runs()
    personas = load_personas()
    col = collect(runs, personas)
    rows = []
    details = {}
    for cell in REP_CELLS:
        series = [np.asarray(col["epsA"][(pid, cell)], dtype=float) for pid in sorted(personas)]
        lengths = sorted({len(x) for x in series})
        if len(lengths) != 1:
            raise RuntimeError(f"unequal episode counts in {cell}: {lengths}")
        data = np.vstack(series)
        point = components(data)
        fixed = bootstrap(data, resample_prompts=False, rng=np.random.default_rng(seed(f"fixed:{cell}")))
        population = bootstrap(data, resample_prompts=True, rng=np.random.default_rng(seed(f"population:{cell}")))
        human_key = "d90" if "d90" in cell else "d10"
        threshold = RHO * HUMAN_SD[human_key]
        row = {
            "cell": cell,
            "personas": data.shape[0],
            "episodesPerPersona": data.shape[1],
            "poolMean": round(float(data.mean()), 6),
            "rawBetweenSD": round(math.sqrt(point["rawB"]), 6),
            "correctedBetweenSD": round(point["correctedSD"], 6),
            "averageWithinEpisodeVariance": round(point["W"], 8),
            "betweenShare": round(point["betweenShare"], 6),
            "historicalRhoThresholdSD": round(threshold, 6),
            "pointMeetsHistoricalThreshold": int(point["correctedSD"] >= threshold),
            "fixedPanelCorrectedSDlo": round(fixed["correctedSD"]["lo95"], 6),
            "fixedPanelCorrectedSDmedian": round(fixed["correctedSD"]["median"], 6),
            "fixedPanelCorrectedSDhi": round(fixed["correctedSD"]["hi95"], 6),
            "fixedPanelBetweenShareLo": round(fixed["betweenShare"]["lo95"], 6),
            "fixedPanelBetweenShareMedian": round(fixed["betweenShare"]["median"], 6),
            "fixedPanelBetweenShareHi": round(fixed["betweenShare"]["hi95"], 6),
            "personaPopulationCorrectedSDlo": round(population["correctedSD"]["lo95"], 6),
            "personaPopulationCorrectedSDmedian": round(population["correctedSD"]["median"], 6),
            "personaPopulationCorrectedSDhi": round(population["correctedSD"]["hi95"], 6),
        }
        rows.append(row)
        details[cell] = {"point": point, "fixedPanelBootstrap": fixed, "personaPopulationBootstrapExploratory": population}

    write_csv(FIG / "variance-correction.csv", rows)
    (FIG / "variance-correction.json").write_text(json.dumps(details, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Finite-opportunity correction for between-prompt dispersion",
        "",
        "> **STATUS: POST-ADJUDICATION SENSITIVITY — ZERO SUBJECT CALLS.** Historical P5-1b comparisons are unchanged. The primary estimand is the dispersion among these sixteen fixed prompts. Primary uncertainty therefore resamples episodes within each prompt while retaining all sixteen prompts. A second two-stage bootstrap that also resamples prompts is reported only as exploratory persona-population uncertainty.",
        "",
        "## Estimator",
        "",
        "For each repeated-game cell, `Var_i(p_hat_i) ≈ B + mean(s_i²/n_i)`. The corrected fixed-panel between-prompt component is `max(0, raw variance − estimated measurement noise)`. `W` is the average within-prompt variance of the episode-level outcome. Bootstrap replicates: **50,000** for each estimand.",
        "",
        "| cell | corrected SD | fixed-panel episode-bootstrap 95% | between share B/(B+W) | fixed-panel between-share 95% | historical 0.75×human-SD threshold | point meets? |",
        "|---|---:|---|---:|---|---:|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['cell']} | {r['correctedBetweenSD']:.4f} | [{r['fixedPanelCorrectedSDlo']:.4f}, {r['fixedPanelCorrectedSDhi']:.4f}] | {r['betweenShare']:.3f} | [{r['fixedPanelBetweenShareLo']:.3f}, {r['fixedPanelBetweenShareHi']:.3f}] | {r['historicalRhoThresholdSD']:.4f} | {'yes' if r['pointMeetsHistoricalThreshold'] else 'no'} |"
        )
    lines += [
        "",
        "## Estimand boundary",
        "",
        "The fixed-panel intervals quantify episode-sampling uncertainty for these exact prompts. The wider two-stage intervals in `figure-sources/variance-correction.csv` additionally resample prompts and are exploratory statements about a hypothetical persona generator. Neither is a protocol-matched human latent-variance comparison.",
        "",
        "Machine-readable results: `figure-sources/variance-correction.csv` and `.json`.",
    ]
    (OUT / "variance-correction.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"rows": rows}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
