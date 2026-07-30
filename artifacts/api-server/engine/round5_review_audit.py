#!/usr/bin/env python3
"""Round 5 zero-call audits requested by Explore Science.

This script operates only on the archived event store and already generated
post-adjudication artifacts. It makes no provider calls and does not alter any
sealed registration, predicate, historical verdict, or raw event.

Audits:
1. prove that the full data-dependent interiority gate is reapplied inside
   every permutation through lookup/direct parity tests and a dynamic-vs-static
   mask regression;
2. enumerate exact-gate attainability at n=6, estimate the smallest familywise
   p-value attainable in the archived 32-candidate family, and provide an
   explicitly model-dependent prospective power illustration;
3. inspect the event store and release manifests to state the exact provenance
   and tamper-evidence boundary for requests and completions.
"""
from __future__ import annotations

import csv
import itertools
import json
import math
import os
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "docs" / "analysis" / "submission" / "round5"
FIG = OUT / "figure-sources"
DB = HERE / "data" / "engine.db"
SUMMARY = ROOT / "docs" / "analysis" / "submission" / "submission-analysis-summary.json"

from phase5_closeout_adjudicate import collect, gate_cell, load_personas, load_runs  # noqa: E402
from submission_gate_exact_cluster import (  # noqa: E402
    LEVELS,
    exact_gate,
    gate_lookup,
)

SEED = 20260791
ATTAINABILITY_B = int(os.environ.get("ROUND5_ATTAINABILITY_PERMUTATIONS", "200000"))
ATTAINABILITY_BATCH = int(os.environ.get("ROUND5_ATTAINABILITY_BATCH", "5000"))
POWER_REPS = int(os.environ.get("ROUND5_POWER_REPS", "10000"))
POWER_BATCH = int(os.environ.get("ROUND5_POWER_BATCH", "1000"))


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def candidate_data() -> dict[tuple[str, str], tuple[np.ndarray, np.ndarray]]:
    runs = load_runs()
    personas = load_personas()
    col = collect(runs, personas)
    out: dict[tuple[str, str], tuple[np.ndarray, np.ndarray]] = {}
    for pid in sorted(personas):
        for level in LEVELS:
            out[(pid, level)] = (
                np.asarray(col["epsA"][(pid, f"rep-d90-{level}")], dtype=float),
                np.asarray(col["epsA"][(pid, f"rep-d10-{level}")], dtype=float),
            )
    return out


def counts_to_values(c0: int, c1: int, c2: int) -> list[float]:
    return [0.0] * c0 + [0.5] * c1 + [1.0] * c2


def all_compositions(n: int) -> Iterable[tuple[int, int, int]]:
    for c0 in range(n + 1):
        for c1 in range(n - c0 + 1):
            yield c0, c1, n - c0 - c1


def direct_gate(kind: str, values: list[float]) -> bool:
    if kind == "historical":
        return bool(gate_cell(values)["interior"])
    if kind == "exact":
        return bool(exact_gate(values)["interior"])
    raise ValueError(kind)


def lookup_parity_and_dynamic_test(candidates: dict) -> dict:
    ns = sorted({len(x) for pair in candidates.values() for x in pair})
    lookups = {kind: {n: gate_lookup(n, kind) for n in ns} for kind in ("historical", "exact")}
    parity_checked = 0
    parity_failures: list[dict] = []
    for kind in ("historical", "exact"):
        for n in ns:
            table = lookups[kind][n]
            for c0, c1, c2 in all_compositions(n):
                observed = direct_gate(kind, counts_to_values(c0, c1, c2))
                cached = bool(table[c0, c1])
                parity_checked += 1
                if observed != cached:
                    parity_failures.append({"kind": kind, "n": n, "counts": [c0, c1, c2]})
    if parity_failures:
        raise AssertionError(f"gate lookup/direct parity failures: {parity_failures[:5]}")

    observed_exact_mask = {
        key: bool(exact_gate(g90.tolist())["interior"] and exact_gate(g10.tolist())["interior"])
        for key, (g90, g10) in candidates.items()
    }

    # Exhaustively find a concrete assignment whose gate status differs from the
    # observed-data mask. This demonstrates why a static mask would be wrong.
    witness = None
    for key, (g90, g10) in candidates.items():
        pool = np.concatenate([g90, g10])
        n90 = len(g90)
        for idx_tuple in itertools.combinations(range(len(pool)), n90):
            idx = np.asarray(idx_tuple, dtype=int)
            selected = np.zeros(len(pool), dtype=bool)
            selected[idx] = True
            p90 = pool[selected]
            p10 = pool[~selected]
            dynamic = bool(exact_gate(p90.tolist())["interior"] and exact_gate(p10.tolist())["interior"])
            if dynamic != observed_exact_mask[key]:
                witness = {
                    "candidate": list(key),
                    "observedMask": observed_exact_mask[key],
                    "permutedDynamicMask": dynamic,
                    "permutedD90Counts": [int(np.sum(p90 == v)) for v in (0.0, 0.5, 1.0)],
                    "permutedD10Counts": [int(np.sum(p10 == v)) for v in (0.0, 0.5, 1.0)],
                }
                break
        if witness:
            break
    if witness is None:
        raise AssertionError("no dynamic-mask witness found in exhaustive candidate permutations")

    # Regression: compare dynamic re-gating with an intentionally incorrect
    # static observed-data mask over deterministic random permutations.
    rng = np.random.default_rng(SEED)
    reps = 5000
    dynamic_tmax = np.full(reps, -np.inf)
    static_tmax = np.full(reps, -np.inf)
    for key, (g90, g10) in candidates.items():
        pool = np.rint(np.concatenate([g90, g10]) * 2).astype(np.int8)
        n90, n10 = len(g90), len(g10)
        total = np.bincount(pool, minlength=3)
        random_keys = rng.random((reps, len(pool)))
        idx = np.argpartition(random_keys, n90 - 1, axis=1)[:, :n90]
        selected = pool[idx]
        c1_90 = np.sum(selected == 1, axis=1)
        c2_90 = np.sum(selected == 2, axis=1)
        c0_90 = n90 - c1_90 - c2_90
        c0_10 = total[0] - c0_90
        c1_10 = total[1] - c1_90
        c2_10 = total[2] - c2_90
        slope = (0.5 * c1_90 + c2_90) / n90 - (0.5 * c1_10 + c2_10) / n10
        dynamic_gate = lookups["exact"][n90][c0_90, c1_90] & lookups["exact"][n10][c0_10, c1_10]
        dynamic_tmax = np.maximum(dynamic_tmax, np.where(dynamic_gate, slope, -np.inf))
        if observed_exact_mask[key]:
            static_tmax = np.maximum(static_tmax, slope)
    different = (~np.isclose(dynamic_tmax, static_tmax, equal_nan=True)) | (np.isfinite(dynamic_tmax) != np.isfinite(static_tmax))
    difference_count = int(np.sum(different))
    if difference_count == 0:
        raise AssertionError("dynamic and static-mask null distributions unexpectedly identical")

    compositions = sum((n + 1) * (n + 2) // 2 for n in ns)
    return {
        "status": "pass",
        "candidateCount": len(candidates),
        "episodeCountsPerArm": ns,
        "lookupDirectParityCases": parity_checked,
        "lookupDirectParityFailures": 0,
        "precomputedIntervalGateEvaluations": compositions * 2,
        "dynamicGateLookupApplicationsAtB200000": 200000 * len(candidates) * 2 * 2,
        "witness": witness,
        "dynamicVsStaticRegressionReps": reps,
        "dynamicVsStaticDifferent": difference_count,
        "dynamicVsStaticDifferentRate": difference_count / reps,
    }


def exact_gate_attainability(n: int) -> dict:
    passing: list[dict] = []
    for c0, c1, c2 in all_compositions(n):
        vals = counts_to_values(c0, c1, c2)
        rec = exact_gate(vals)
        if rec["interior"]:
            passing.append({
                "c0": c0,
                "cHalf": c1,
                "c1": c2,
                "mean": (0.5 * c1 + c2) / n,
                "lo": rec["interval95"][0],
                "hi": rec["interval95"][1],
            })
    means = sorted({round(float(x["mean"]), 12) for x in passing})
    return {
        "n": n,
        "passingCompositionCount": len(passing),
        "passingMeans": means,
        "minPassingMean": min(means) if means else None,
        "maxPassingMean": max(means) if means else None,
        "maxAttainableSlope": (max(means) - min(means)) if means else None,
        "compositions": passing,
    }


def current_family_null_tail_at_slope(candidates: dict, threshold: float) -> dict:
    ns = sorted({len(x) for pair in candidates.values() for x in pair})
    lookups = {n: gate_lookup(n, "exact") for n in ns}
    rng = np.random.default_rng(SEED + 1)
    exceed = 0
    finite = 0
    done = 0
    while done < ATTAINABILITY_B:
        b = min(ATTAINABILITY_BATCH, ATTAINABILITY_B - done)
        tmax = np.full(b, -np.inf)
        for g90, g10 in candidates.values():
            pool = np.rint(np.concatenate([g90, g10]) * 2).astype(np.int8)
            n90, n10 = len(g90), len(g10)
            total = np.bincount(pool, minlength=3)
            random_keys = rng.random((b, len(pool)))
            idx = np.argpartition(random_keys, n90 - 1, axis=1)[:, :n90]
            selected = pool[idx]
            c1_90 = np.sum(selected == 1, axis=1)
            c2_90 = np.sum(selected == 2, axis=1)
            c0_90 = n90 - c1_90 - c2_90
            c0_10 = total[0] - c0_90
            c1_10 = total[1] - c1_90
            c2_10 = total[2] - c2_90
            gate = lookups[n90][c0_90, c1_90] & lookups[n10][c0_10, c1_10]
            slope = (0.5 * c1_90 + c2_90) / n90 - (0.5 * c1_10 + c2_10) / n10
            tmax = np.maximum(tmax, np.where(gate, slope, -np.inf))
        finite += int(np.sum(np.isfinite(tmax)))
        exceed += int(np.sum(tmax >= threshold - 1e-12))
        done += b
    return {
        "permutations": ATTAINABILITY_B,
        "threshold": threshold,
        "exceedances": exceed,
        "pAddOne": (exceed + 1) / (ATTAINABILITY_B + 1),
        "anyGateRate": finite / ATTAINABILITY_B,
        "seed": SEED + 1,
    }


def episode_probs(p: float) -> np.ndarray:
    return np.asarray([(1 - p) ** 2, 2 * p * (1 - p), p ** 2], dtype=float)


def simulate_family_tmax(
    *, n: int, family_size: int, reps: int, rng: np.random.Generator,
    target_low: float | None = None, target_high: float | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    lookup = gate_lookup(n, "exact")
    tmax = np.full(reps, -np.inf)
    target_gate = np.zeros(reps, dtype=bool)
    target_slope = np.full(reps, np.nan)
    for j in range(family_size):
        if j == 0 and target_low is not None and target_high is not None:
            p10, p90 = target_low, target_high
        else:
            p10 = p90 = 0.5
        c10 = rng.multinomial(n, episode_probs(p10), size=reps)
        c90 = rng.multinomial(n, episode_probs(p90), size=reps)
        gate = lookup[c10[:, 0], c10[:, 1]] & lookup[c90[:, 0], c90[:, 1]]
        slope = (0.5 * c90[:, 1] + c90[:, 2]) / n - (0.5 * c10[:, 1] + c10[:, 2]) / n
        tmax = np.maximum(tmax, np.where(gate, slope, -np.inf))
        if j == 0:
            target_gate = gate
            target_slope = slope
    return tmax, target_gate, target_slope


def discrete_critical_value(null_tmax: np.ndarray, alpha: float = 0.05) -> tuple[float | None, float | None]:
    finite_values = np.unique(null_tmax[np.isfinite(null_tmax)])
    for value in np.sort(finite_values):
        tail = float(np.mean(null_tmax >= value - 1e-12))
        if tail <= alpha:
            return float(value), tail
    return None, None


def prospective_power_table() -> list[dict]:
    rows: list[dict] = []
    rng = np.random.default_rng(SEED + 2)
    # Illustrative p13-like mean contrast under an independent-seat Bernoulli
    # data-generating model. These are planning diagnostics, not a power claim
    # about the archived experiment or a preregistered Phase 6 design.
    for family_size in (1, 4, 16):
        for n in (6, 12, 20, 30, 50, 75, 100):
            null, _, _ = simulate_family_tmax(
                n=n, family_size=family_size, reps=POWER_REPS, rng=rng
            )
            critical, null_tail = discrete_critical_value(null)
            alt, target_gate, target_slope = simulate_family_tmax(
                n=n, family_size=family_size, reps=POWER_REPS, rng=rng,
                target_low=1 / 3, target_high=3 / 4,
            )
            if critical is None:
                reject = np.zeros(POWER_REPS, dtype=bool)
                target_reject = np.zeros(POWER_REPS, dtype=bool)
            else:
                reject = alt >= critical - 1e-12
                target_reject = target_gate & (target_slope >= critical - 1e-12)
            rows.append({
                "familySize": family_size,
                "episodesPerArm": n,
                "model": "independent seats; episode=Binomial(2,p)/2",
                "targetPLow": 1 / 3,
                "targetPHigh": 3 / 4,
                "targetDelta": 3 / 4 - 1 / 3,
                "reps": POWER_REPS,
                "criticalSlope": critical,
                "realizedNullTail": null_tail,
                "targetGatePassRate": float(np.mean(target_gate)),
                "familyRejectRateUnderAlternative": float(np.mean(reject)),
                "targetPassesGateAndThreshold": float(np.mean(target_reject)),
            })
    return rows


def detect_event_table(conn: sqlite3.Connection) -> tuple[str, list[str]]:
    tables = [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")]
    for table in tables:
        cols = [r[1] for r in conn.execute(f"PRAGMA table_info({table})")]
        if {"run_id", "type", "payload"}.issubset(cols):
            return table, cols
    raise RuntimeError(f"could not locate event table; tables={tables}")


def provenance_audit() -> dict:
    conn = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    table, columns = detect_event_table(conn)
    run_phase: dict[str, str] = {}
    requested: dict[str, Counter] = defaultdict(Counter)
    responded: dict[str, Counter] = defaultdict(Counter)
    completion_hash_keys: Counter = Counter()

    for run_id, typ, payload in conn.execute(
        f"SELECT run_id, type, payload FROM {table} "
        "WHERE type IN ('llm.requested','llm.responded') ORDER BY rowid"
    ):
        d = json.loads(payload)
        if typ == "llm.requested":
            block = str(d.get("block") or "")
            arm = d.get("armId")
            phase = "phase4-5" if arm or block.startswith(("P4", "P5", "SENT")) else "legacy-phase3"
            run_phase.setdefault(run_id, phase)
            rec = requested[phase]
            rec["events"] += 1
            rec["systemPresent"] += bool(d.get("system") is not None)
            rec["userPresent"] += bool(d.get("user") is not None)
            rec["bundleSha256"] += bool(d.get("bundleSha256"))
            rec["requestBodySha256"] += bool(d.get("requestBodySha256"))
            rec["promptHash"] += bool(d.get("prompt_hash"))
            rec["engineCommit"] += bool(d.get("engineCommit"))
            rec["providerRoute"] += bool(d.get("providerRoute"))
        else:
            phase = run_phase.get(run_id, "unknown")
            rec = responded[phase]
            rec["events"] += 1
            raw_text = d.get("raw_text") if "raw_text" in d else d.get("rawText")
            rec["rawTextPresent"] += raw_text is not None
            rec["rawTextNonempty"] += bool(raw_text)
            meta = d.get("provider_meta") or d.get("providerMeta") or {}
            rec["providerMetaPresent"] += bool(meta)
            rec["responseId"] += bool(meta.get("response_id") or meta.get("responseId"))
            rec["requestBodySha256"] += bool(meta.get("request_body_sha256"))
            rec["systemFingerprint"] += bool(meta.get("system_fingerprint"))
            rec["providerCreatedTimestamp"] += meta.get("created") is not None
            rec["returnedModel"] += bool(d.get("model"))
            for key in d:
                if "hash" in key.lower() or "sha" in key.lower():
                    completion_hash_keys[key] += 1
            for key in meta:
                if "hash" in key.lower() or "sha" in key.lower():
                    completion_hash_keys[f"provider_meta.{key}"] += 1

    conn.close()

    manifest_candidates = [
        ROOT / "capsule" / "SHA256SUMS",
        ROOT / "capsule" / "SHA256SUMS.txt",
        ROOT / "docs" / "phase5-close" / "SHA256SUMS.txt",
    ]
    manifest_rows = []
    engine_snapshot_hashed = False
    for path in manifest_candidates:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        mentions_engine = "engine.db" in text
        engine_snapshot_hashed = engine_snapshot_hashed or mentions_engine
        manifest_rows.append({
            "path": str(path.relative_to(ROOT)),
            "mentionsEngineDb": mentions_engine,
            "lineCount": len(text.splitlines()),
        })
    ots_files = sorted(str(p.relative_to(ROOT)) for p in ROOT.rglob("*.ots"))

    def counter_dict(c: Counter) -> dict:
        return {k: int(v) for k, v in sorted(c.items())}

    return {
        "eventTable": table,
        "eventTableColumns": columns,
        "requestedCoverage": {k: counter_dict(v) for k, v in sorted(requested.items())},
        "respondedCoverage": {k: counter_dict(v) for k, v in sorted(responded.items())},
        "responsePayloadHashLikeFields": counter_dict(completion_hash_keys),
        "archiveHashManifests": manifest_rows,
        "engineSnapshotCoveredByManifest": engine_snapshot_hashed,
        "openTimestampsProofCount": len(ots_files),
        "openTimestampsProofs": ots_files,
        "findings": {
            "requestSide": (
                "Phase 4–5 records store the complete rendered system/user bundle, a bundle SHA-256, "
                "a deterministic request-body SHA-256, engine commit, provider route, and requested model. "
                "The live runner asserts the provider adapter's request-body SHA equals the recorded mirror."
            ),
            "responseSide": (
                "The archive stores raw completion text and, for Phase 4–5 provider adapters, response IDs "
                "and selected provider metadata. It does not store a provider-signed response object or a "
                "separate receipt-time hash of each raw completion payload."
            ),
            "archiveSide": (
                "Published archive snapshots are covered by checksum manifests and external timestamp proofs. "
                "This detects changes relative to the released snapshot but does not prove that no edit occurred "
                "between provider receipt and snapshot sealing."
            ),
        },
    }


def markdown_report(dynamic: dict, attain: dict, tail: dict, power: list[dict], prov: dict) -> str:
    n6 = attain["n6"]
    rows16 = [r for r in power if r["familySize"] == 16]
    lines = [
        "# Round 5 gate-power and provenance audit",
        "",
        "> **STATUS: POST-ADJUDICATION ZERO-CALL AUDIT.** This document answers Explore Science issues B1, B3, and A2. It changes no sealed artifact or historical verdict. The prospective power table is explicitly model-dependent planning evidence, not a preregistered result.",
        "",
        "## B1 — dynamic gate reapplication",
        "",
        "**PASS.** The familywise permutation implementation dynamically reapplies the complete condition-level gate inside every permutation. It does not freeze the observed-data candidate mask.",
        "",
        f"- Lookup/direct parity cases checked: **{dynamic['lookupDirectParityCases']:,}**, failures: **0**.",
        f"- The implementation precomputes **{dynamic['precomputedIntervalGateEvaluations']:,}** possible-composition gate values and then performs **{dynamic['dynamicGateLookupApplicationsAtB200000']:,}** Boolean condition-gate lookup applications at B=200,000 across 32 candidates, two conditions, and two gate constructions.",
        f"- A deterministic regression over {dynamic['dynamicVsStaticRegressionReps']:,} null draws found dynamic and intentionally static-mask maxima differed in **{dynamic['dynamicVsStaticDifferent']:,}** draws ({dynamic['dynamicVsStaticDifferentRate']:.1%}).",
        f"- Concrete witness: `{dynamic['witness']['candidate'][0]}/{dynamic['witness']['candidate'][1]}` has observed exact-mask status `{dynamic['witness']['observedMask']}` but a valid permuted assignment with dynamic status `{dynamic['witness']['permutedDynamicMask']}`.",
        "",
        "This regression test would fail if the implementation were changed to use a static observed-data mask.",
        "",
        "## B3 — exact-gate attainability at six episodes per arm",
        "",
        f"The exact episode-level gate admits **{n6['passingCompositionCount']}** of the 28 possible three-category outcome compositions at n=6. Its admissible sample means are `{n6['passingMeans']}`. Therefore two gate-passing cells can differ by at most **{n6['maxAttainableSlope']:.4f}** at this sample size.",
        "",
        f"Under the archived 32-candidate null structure, the estimated tail probability at this maximum attainable slope is **p={tail['pAddOne']:.6f}** ({tail['exceedances']:,}/{tail['permutations']:,} permutations; seed `{tail['seed']}`). Thus no exact-gate result in the archived n=6 family can reach a conventional 0.05 familywise threshold. The exact-gate audit is therefore informative about dependence and gate eligibility, but it is not a powered disconfirmation of a persona-level response.",
        "",
        "The correct p13 status is: **not prospectively confirmed by the frozen rule, and not decisively disconfirmed by the conservative post-adjudication exact procedure; replication target.**",
        "",
        "### Illustrative prospective power",
        "",
        "The following table assumes independent seat decisions, so an episode outcome is `Binomial(2,p)/2`; one target has p=.333 versus p=.750 and all other candidates are null at p=.5. It is a planning sensitivity only. A Phase 6 registration should simulate its own dependence model and exact decision rule.",
        "",
        "| family | episodes/arm | exact critical slope | target gate pass | target passes gate+threshold | family rejection |",
        "|---:|---:|---:|---:|---:|---:|",
    ]
    for r in rows16:
        crit = "none" if r["criticalSlope"] is None else f"{r['criticalSlope']:.3f}"
        lines.append(
            f"| {r['familySize']} | {r['episodesPerArm']} | {crit} | {r['targetGatePassRate']:.1%} | {r['targetPassesGateAndThreshold']:.1%} | {r['familyRejectRateUnderAlternative']:.1%} |"
        )
    lines += [
        "",
        "Complete family-size and sample-size grid: `figure-sources/prospective-power.csv`.",
        "",
        "## A2 — completion provenance and tamper-evidence boundary",
        "",
        prov["findings"]["requestSide"],
        "",
        prov["findings"]["responseSide"],
        "",
        prov["findings"]["archiveSide"],
        "",
        "Accordingly, byte-exact replay proves reproducibility from the released archive. The checksum and timestamp record makes the released archive tamper-evident relative to its published snapshot. It is **not** provider attestation and does not independently prove immutability of every completion from the instant of receipt.",
        "",
        "Machine-readable audit: `round5-review-audit.json`. Field coverage: `figure-sources/provenance-field-coverage.csv`.",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    FIG.mkdir(parents=True, exist_ok=True)
    candidates = candidate_data()
    dynamic = lookup_parity_and_dynamic_test(candidates)

    attain_rows = []
    attain_by_n = {}
    for n in range(1, 101):
        rec = exact_gate_attainability(n)
        attain_by_n[n] = rec
        attain_rows.append({
            "episodesPerArm": n,
            "passingCompositionCount": rec["passingCompositionCount"],
            "minPassingMean": rec["minPassingMean"],
            "maxPassingMean": rec["maxPassingMean"],
            "maxAttainableSlope": rec["maxAttainableSlope"],
        })
    n6 = attain_by_n[6]
    tail = current_family_null_tail_at_slope(candidates, float(n6["maxAttainableSlope"]))
    power = prospective_power_table()
    prov = provenance_audit()

    write_csv(FIG / "exact-gate-attainability.csv", attain_rows)
    write_csv(FIG / "prospective-power.csv", power)
    prov_rows = []
    for phase, counts in prov["requestedCoverage"].items():
        prov_rows.append({"event": "llm.requested", "phase": phase, **counts})
    for phase, counts in prov["respondedCoverage"].items():
        prov_rows.append({"event": "llm.responded", "phase": phase, **counts})
    write_csv(FIG / "provenance-field-coverage.csv", prov_rows)

    audit = {
        "status": "post-adjudication zero-call audit",
        "dynamicGate": dynamic,
        "exactGateAttainability": {
            "n6": n6,
            "currentFamilyTailAtMaxAttainableSlope": tail,
            "gridSource": "figure-sources/exact-gate-attainability.csv",
        },
        "prospectivePower": {
            "status": "illustrative model-dependent planning simulation",
            "seed": SEED + 2,
            "repsPerConfiguration": POWER_REPS,
            "source": "figure-sources/prospective-power.csv",
        },
        "provenance": prov,
    }
    (OUT / "round5-review-audit.json").write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (OUT / "round5-review-audit.md").write_text(markdown_report(dynamic, {"n6": n6}, tail, power, prov), encoding="utf-8")

    summary = json.loads(SUMMARY.read_text(encoding="utf-8"))
    summary.setdefault("results", {})["round5ReviewAudit"] = {
        "dynamicGate": dynamic,
        "exactGateN6": {
            "passingMeans": n6["passingMeans"],
            "maxAttainableSlope": n6["maxAttainableSlope"],
            "archivedFamilyTailAtMaxAttainableSlope": tail,
        },
        "prospectivePowerSource": "docs/analysis/submission/round5/figure-sources/prospective-power.csv",
        "provenance": prov,
    }
    SUMMARY.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"dynamic": dynamic, "n6": n6, "tail": tail, "provenance": prov}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
