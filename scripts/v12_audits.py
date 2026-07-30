#!/usr/bin/env python3
"""Independent zero-call audits for the near-arXiv v12 manuscript.

This script intentionally does not import the original variance-bootstrap
implementation or its human-reference constants. It uses committed episode
counts and the archived event store to answer the remaining v11 review issues:

1. independently reproduce the suspicious-looking `0.4122` bootstrap bound;
2. publish all cooperative- versus defect-leaning stratum means;
3. define and recompute temperature/choice entropy on a matched sweep lattice;
4. inventory supplied versus omitted decoding parameters;
5. enrich the machine-readable submission summary.

No provider calls; no changes to sealed records or historical verdicts.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import sqlite3
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SUB = ROOT / "docs" / "analysis" / "submission"
OUT = SUB / "v12"
FIG = SUB / "figure-sources"
EPISODE_CELLS = FIG / "episode-cluster-cells.csv"
VARIANCE = FIG / "variance-correction.csv"
TEMPERATURE = ROOT / "docs" / "analysis" / "figure-sources" / "p5-temperature-curves.csv"
SUMMARY = SUB / "submission-analysis-summary.json"
DB = ROOT / "artifacts" / "api-server" / "engine" / "data" / "engine.db"
BOOT_REPS = int(os.environ.get("V12_BOOTSTRAP_REPS", "250000"))
BOOT_SEEDS = (20260812, 20260813, 20260814)
TARGET_CELL = "rep-d10-s2a"
HUMAN_REFERENCES_DISPLAYED = (0.4122, 0.3116, 0.3092, 0.2337)
COOP_IDS = {"p01", "p02", "p03", "p05", "p09", "p10", "p11", "p13"}
NON_SWAP = (
    "rep-d10-s2a",
    "rep-d10-s2p",
    "rep-d90-s2a",
    "rep-d90-s2p",
    "os-community",
)


def load_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def values_from_counts(row: dict[str, str]) -> np.ndarray:
    return np.asarray(
        [0.0] * int(row["episodeCounts0"])
        + [0.5] * int(row["episodeCountsHalf"])
        + [1.0] * int(row["episodeCounts1"]),
        dtype=float,
    )


def independent_components(data: np.ndarray) -> dict[str, float]:
    prompt_means = data.mean(axis=1)
    raw_between = float(np.var(prompt_means, ddof=1))
    within_prompt = np.var(data, axis=1, ddof=1)
    measurement_noise = float(np.mean(within_prompt / data.shape[1]))
    corrected_between = max(0.0, raw_between - measurement_noise)
    within = float(np.mean(within_prompt))
    return {
        "rawBetweenVariance": raw_between,
        "measurementNoise": measurement_noise,
        "correctedBetweenVariance": corrected_between,
        "correctedSD": math.sqrt(corrected_between),
        "averageWithinVariance": within,
        "betweenShare": corrected_between / (corrected_between + within)
        if corrected_between + within > 0
        else float("nan"),
    }


def bootstrap_lower(data: np.ndarray, seed: int, reps: int) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    n_prompt, n_ep = data.shape
    corrected: list[float] = []
    batch = 2500
    for start in range(0, reps, batch):
        b = min(batch, reps - start)
        eidx = rng.integers(0, n_ep, size=(b, n_prompt, n_ep))
        selected = np.broadcast_to(data, (b, n_prompt, n_ep))
        sampled = np.take_along_axis(selected, eidx, axis=2)
        means = sampled.mean(axis=2)
        raw = np.var(means, axis=1, ddof=1)
        within = np.var(sampled, axis=2, ddof=1)
        noise = np.mean(within / n_ep, axis=1)
        corrected.extend(np.sqrt(np.maximum(raw - noise, 0)).tolist())
    arr = np.asarray(corrected, dtype=float)
    return {
        "seed": seed,
        "reps": reps,
        "lo025": float(np.quantile(arr, 0.025)),
        "median": float(np.quantile(arr, 0.5)),
        "hi975": float(np.quantile(arr, 0.975)),
        "minimum": float(np.min(arr)),
        "uniqueRounded6": int(len(np.unique(np.round(arr, 6)))),
    }


def bootstrap_audit(rows: list[dict[str, str]]) -> dict:
    target_rows = sorted(
        (r for r in rows if r["cell"] == TARGET_CELL), key=lambda r: r["personaId"]
    )
    if len(target_rows) != 16:
        raise AssertionError(f"{TARGET_CELL}: expected 16 prompt rows, got {len(target_rows)}")
    data = np.vstack([values_from_counts(r) for r in target_rows])
    if data.shape != (16, 6):
        raise AssertionError(f"{TARGET_CELL}: expected 16x6, got {data.shape}")
    point = independent_components(data)
    runs = [bootstrap_lower(data, seed, BOOT_REPS) for seed in BOOT_SEEDS]
    stored = next(r for r in load_csv(VARIANCE) if r["cell"] == TARGET_CELL)
    stored_lo = float(stored["fixedPanelCorrectedSDlo"])
    mean_lo = float(np.mean([x["lo025"] for x in runs]))
    spread = float(max(x["lo025"] for x in runs) - min(x["lo025"] for x in runs))
    collisions = []
    for result in runs:
        for reference in HUMAN_REFERENCES_DISPLAYED:
            if round(result["lo025"], 4) == round(reference, 4):
                collisions.append(
                    {
                        "seed": result["seed"],
                        "bootstrapLower": result["lo025"],
                        "displayReference": reference,
                        "matchAtDecimals": 4,
                    }
                )
    if abs(point["correctedSD"] - float(stored["correctedBetweenSD"])) > 2e-6:
        raise AssertionError("independent point estimator does not reproduce stored corrected SD")
    if abs(mean_lo - stored_lo) > 0.0015:
        raise AssertionError(
            f"independent bootstrap lower bound {mean_lo} too far from stored {stored_lo}"
        )
    return {
        "status": "verified independent recomputation",
        "cell": TARGET_CELL,
        "dataShape": list(data.shape),
        "point": point,
        "storedLowerBound": stored_lo,
        "independentRuns": runs,
        "meanIndependentLowerBound": mean_lo,
        "rangeAcrossSeeds": spread,
        "displayedCoincidences": collisions,
        "interpretation": (
            "The stored lower bound is independently reproduced. The apparent 0.4122 "
            "match is a rounding coincidence: the stored value is 0.412198, whereas the "
            "published human reference is reported as 0.4122 and does not enter the "
            "bootstrap computation."
        ),
    }


def leaning_table(rows: list[dict[str, str]]) -> list[dict]:
    by = {(r["personaId"], r["cell"]): float(r["mean"]) for r in rows}
    output = []
    for cell in NON_SWAP:
        coop = [by[(pid, cell)] for pid in sorted(COOP_IDS)]
        defect_ids = sorted({f"p{i:02d}" for i in range(1, 17)} - COOP_IDS)
        defect = [by[(pid, cell)] for pid in defect_ids]
        output.append(
            {
                "cell": cell,
                "cooperativeLeaningPrompts": len(coop),
                "defectLeaningPrompts": len(defect),
                "cooperativeLeaningMean": float(np.mean(coop)),
                "defectLeaningMean": float(np.mean(defect)),
                "difference": float(np.mean(coop) - np.mean(defect)),
                "episodesPerPrompt": 20 if cell == "os-community" else 6,
            }
        )
    gaps = [x["difference"] for x in output]
    if min(gaps) < 0.49 or max(gaps) > 0.75:
        raise AssertionError(f"leaning gap outside plausible audit range: {gaps}")
    return output


def h2(p: float) -> float:
    if p <= 0 or p >= 1:
        return 0.0
    return -(p * math.log2(p) + (1 - p) * math.log2(1 - p))


def entropy_audit() -> dict:
    rows = load_csv(TEMPERATURE)
    parsed = []
    for r in rows:
        t = float(r["temperature"])
        eps = int(r["episodes"])
        p = float(r["meanRound1Coop"])
        seats = 2 * eps
        coop = int(round(p * seats))
        parsed.append(
            {
                "key": (r["personaId"], r["cell"]),
                "temperature": t,
                "episodes": eps,
                "seats": seats,
                "cooperate": coop,
                "defect": seats - coop,
                "rate": coop / seats,
                "unitEntropyBits": h2(coop / seats),
            }
        )
    temperatures = sorted({x["temperature"] for x in parsed})
    keys_by_t = {t: {x["key"] for x in parsed if x["temperature"] == t} for t in temperatures}
    matched_keys = set.intersection(*(keys_by_t[t] for t in temperatures))
    matched = [x for x in parsed if x["key"] in matched_keys]
    output = []
    for t in temperatures:
        all_t = [x for x in parsed if x["temperature"] == t]
        matched_t = [x for x in matched if x["temperature"] == t]
        for label, subset in (("all-recorded-units", all_t), ("matched-sweep-units", matched_t)):
            coop = sum(x["cooperate"] for x in subset)
            seats = sum(x["seats"] for x in subset)
            output.append(
                {
                    "temperature": t,
                    "scope": label,
                    "units": len(subset),
                    "seats": seats,
                    "cooperate": coop,
                    "pooledShannonBits": h2(coop / seats) if seats else None,
                    "meanUnitShannonBits": float(np.mean([x["unitEntropyBits"] for x in subset]))
                    if subset
                    else None,
                    "medianUnitShannonBits": float(np.median([x["unitEntropyBits"] for x in subset]))
                    if subset
                    else None,
                }
            )
    matched_pooled = [x["pooledShannonBits"] for x in output if x["scope"] == "matched-sweep-units"]
    return {
        "definition": (
            "base-2 Shannon entropy H=-sum_a p(a)log2 p(a) of round-one payoff-role "
            "choices; pooled entropy aggregates cooperate/defect seat counts, while mean-unit "
            "entropy averages the empirical binary entropy within each persona-cell lane"
        ),
        "matchedUnitCount": len(matched_keys),
        "matchedKeys": [list(x) for x in sorted(matched_keys)],
        "records": output,
        "directionSurvivesMatchedPooled": bool(
            len(matched_pooled) == 3
            and matched_pooled[0] > matched_pooled[1] > matched_pooled[2]
        ),
        "interpretation": (
            "The historical pooled statistic mixes different unit sets. On the identical "
            "persona-cell sweep observed at all three temperatures, pooled entropy still "
            "declines, but pooled and mean-within-unit entropy answer different questions."
        ),
    }


def decoding_audit() -> dict:
    db = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    payloads = [json.loads(p) for (p,) in db.execute("SELECT payload FROM events WHERE type='llm.requested'")]
    db.close()
    keys = ("temperature", "maxTokens", "top_p", "topP", "presence_penalty", "frequency_penalty", "logit_bias")
    key_counts = {key: sum(key in p for p in payloads) for key in keys}
    temperatures = sorted({p.get("temperature") for p in payloads if p.get("temperature") is not None})
    max_tokens = sorted({p.get("maxTokens") for p in payloads if p.get("maxTokens") is not None})
    llm_subject = (ROOT / "artifacts" / "api-server" / "engine" / "llm_subject.py").read_text(encoding="utf-8")
    provider = (ROOT / "artifacts" / "api-server" / "engine" / "phase4_providers.py").read_text(encoding="utf-8")
    if "top_p=1.0" not in llm_subject:
        raise AssertionError("build_prompt no longer explicitly sets top_p=1.0")
    if 'if top_p < 1.0' not in provider or 'kwargs["top_p"]' not in provider:
        raise AssertionError("wire omission rule for top_p=1.0 not found")
    forbidden = ("presence_penalty", "frequency_penalty", "logit_bias")
    code_uses = {name: (name in llm_subject or name in provider) for name in forbidden}
    if any(code_uses.values()):
        raise AssertionError(f"unexpected explicit penalty/bias field in primary provider path: {code_uses}")
    return {
        "requestEventsInspected": len(payloads),
        "eventPayloadKeyCounts": key_counts,
        "temperaturesRecorded": temperatures,
        "maxTokensRecorded": max_tokens,
        "primaryOpenAIPath": {
            "temperature": "explicitly supplied per request",
            "max_tokens": "explicitly supplied; primary protocol 16",
            "top_p": "assembled as 1.0 and intentionally omitted from the wire at 1.0",
            "presence_penalty": "not supplied; provider default applies",
            "frequency_penalty": "not supplied; provider default applies",
            "logit_bias": "not supplied; provider default applies",
        },
        "interpretation": (
            "Temperature was the only decoding parameter intentionally varied in the sweep. "
            "The manuscript should distinguish explicit fixed fields from omitted fields that "
            "therefore inherit provider defaults."
        ),
    }


def write_outputs(audit: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "v12-audits.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    leaning = audit["leaningStrata"]
    with (OUT / "leaning-strata.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(leaning[0]))
        writer.writeheader()
        writer.writerows(leaning)
    entropy = audit["entropy"]["records"]
    with (OUT / "temperature-entropy.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(entropy[0]))
        writer.writeheader()
        writer.writerows(entropy)

    b = audit["bootstrapCoincidence"]
    lines = [
        "# v12 independent audits",
        "",
        "> **STATUS: POST-ADJUDICATION, ZERO-CALL VERIFICATION.** No historical verdict or sealed artifact is changed.",
        "",
        "## Independent bootstrap coincidence audit",
        "",
        f"- Cell: `{b['cell']}`; data shape: {b['dataShape'][0]} prompts × {b['dataShape'][1]} episodes.",
        f"- Stored lower bound: `{b['storedLowerBound']:.9f}`.",
        f"- Independent mean lower bound across {len(b['independentRuns'])} seeds: `{b['meanIndependentLowerBound']:.9f}`; seed-to-seed range `{b['rangeAcrossSeeds']:.9f}`.",
        f"- Interpretation: {b['interpretation']}",
        "",
        "| seed | replicates | lower 2.5% | median | upper 97.5% |",
        "|---:|---:|---:|---:|---:|",
    ]
    for r in b["independentRuns"]:
        lines.append(f"| {r['seed']} | {r['reps']:,} | {r['lo025']:.9f} | {r['median']:.9f} | {r['hi975']:.9f} |")
    lines += [
        "",
        "## Leaning-rule strata",
        "",
        "| condition | cooperative-leaning mean | defect-leaning mean | difference | prompts per stratum |",
        "|---|---:|---:|---:|---:|",
    ]
    for r in leaning:
        lines.append(
            f"| `{r['cell']}` | {r['cooperativeLeaningMean']:.3f} | {r['defectLeaningMean']:.3f} | {r['difference']:+.3f} | {r['cooperativeLeaningPrompts']} |"
        )
    lines += [
        "",
        "## Temperature and choice entropy",
        "",
        audit["entropy"]["definition"] + ".",
        "",
        "| T | scope | units | seats | pooled Shannon bits | mean within-unit bits |",
        "|---:|---|---:|---:|---:|---:|",
    ]
    for r in entropy:
        lines.append(
            f"| {r['temperature']:.1f} | {r['scope']} | {r['units']} | {r['seats']} | {r['pooledShannonBits']:.4f} | {r['meanUnitShannonBits']:.4f} |"
        )
    lines += [
        "",
        "## Decoding-parameter audit",
        "",
        f"Inspected {audit['decoding']['requestEventsInspected']:,} archived `llm.requested` payloads. `temperature` and `maxTokens` are archived; the primary OpenAI adapter explicitly supplies temperature and max_tokens, assembles top_p=1.0 but omits it from the wire at 1.0, and does not supply presence_penalty, frequency_penalty, or logit_bias.",
        "",
    ]
    (OUT / "v12-audits.md").write_text("\n".join(lines), encoding="utf-8")

    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    summary.setdefault("results", {})["v12IndependentAudits"] = audit
    SUMMARY.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    rows = load_csv(EPISODE_CELLS)
    audit = {
        "status": "complete",
        "bootstrapCoincidence": bootstrap_audit(rows),
        "leaningStrata": leaning_table(rows),
        "entropy": entropy_audit(),
        "decoding": decoding_audit(),
    }
    write_outputs(audit)
    __import__("subprocess").run([__import__("sys").executable, str(ROOT / "scripts" / "v12_entropy_audit.py")], check=True)
    print(json.dumps(json.loads((OUT / "v12-audits.json").read_text(encoding="utf-8")), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
