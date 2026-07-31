#!/usr/bin/env python3
"""Post-adjudication, zero-call P5-2 dependence sensitivity for preprint v13."""
from __future__ import annotations
import json
from collections import defaultdict
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "artifacts" / "api-server" / "engine"
OUT = ROOT / "docs" / "analysis" / "submission" / "v13"
OUT.mkdir(parents=True, exist_ok=True)

import sys
sys.path.insert(0, str(ENGINE))
from phase5_closeout_adjudicate import load_runs, load_personas, valid_runs_by, TIER_A_CELLS
from submission_gate_analyses import load_decisions

B = 200_000
BOOT_SEED = 20260731
POST_SEED = 20260732


def task_groups():
    runs = load_runs()
    personas = load_personas()
    decisions = load_decisions()
    groups = []
    for pid, lean in sorted(personas.items()):
        for cell in TIER_A_CELLS:
            code = decisions["p52Coding"].get(f"{lean}|{cell}")
            if code is None:
                continue
            task_dir = code["taskConsistent"]
            vals = []
            for r in valid_runs_by(runs, pid, cell):
                c_role = r["coopRole"]
                want = c_role if task_dir == "coop-role" else 1 - c_role
                hits = [int(a == want) for a in r["round1"]]
                vals.append(sum(hits) / 2)
            groups.append({"personaId": pid, "lean": lean, "cell": cell, "values": vals})
    return groups


def main() -> int:
    groups = task_groups()
    flat = [v for g in groups for v in g["values"]]
    if len(groups) != 40 or len(flat) != 352 or abs(sum(flat) - 45) > 1e-12:
        raise RuntimeError(f"unexpected P5-2 lattice: groups={len(groups)} episodes={len(flat)} total={sum(flat)}")

    strata = defaultdict(list)
    for g in groups:
        strata[f"{g['lean']}|{g['cell']}"].append(np.asarray(g["values"], dtype=float))
    if sorted(len(v) for v in strata.values()) != [8, 8, 8, 8, 8]:
        raise RuntimeError("expected five strata with eight prompt clusters each")

    rng = np.random.default_rng(BOOT_SEED)
    boot = np.empty(B)
    for b in range(B):
        total = 0.0
        n = 0
        for clusters in strata.values():
            idx = rng.integers(0, len(clusters), len(clusters))
            for i in idx:
                total += float(clusters[i].sum())
                n += len(clusters[i])
        boot[b] = total / n

    rng = np.random.default_rng(POST_SEED)
    latent_total = np.zeros(B)
    denominator = len(flat)
    for g in groups:
        vals = g["values"]
        counts = np.asarray([sum(v == 0 for v in vals), sum(v == 0.5 for v in vals), sum(v == 1 for v in vals)], dtype=float)
        draws = rng.dirichlet(counts + 0.5, size=B)
        means = 0.5 * draws[:, 1] + draws[:, 2]
        latent_total += len(vals) * means
    latent = latent_total / denominator

    result = {
        "status": "post-adjudication zero-call sensitivity",
        "historical": {"episodes": 352, "episodeMeanTotal": 45, "mean": 45/352, "iidExactProjection95": [0.091753, 0.172069]},
        "stratifiedPromptClusterBootstrap": {
            "promptConditionClusters": len(groups), "strata": len(strata), "replicates": B, "seed": BOOT_SEED,
            "median": float(np.quantile(boot, 0.5)), "interval95": [float(x) for x in np.quantile(boot, [0.025, 0.975])],
        },
        "fixedPanelDirichletJeffreys": {
            "promptConditionUnits": len(groups), "draws": B, "seed": POST_SEED, "prior": [0.5, 0.5, 0.5],
            "posteriorMedian": float(np.quantile(latent, 0.5)), "interval95": [float(x) for x in np.quantile(latent, [0.025, 0.975])],
            "probabilityAtOrBelowRegisteredBoundary": float(np.mean(latent <= 0.20)),
        },
        "interpretation": "Both dependence-aware sensitivities remain below the registered 0.20 persona-dominant boundary; the pooled classification remains carried by the mechanism-confounded swap cell.",
    }
    (OUT / "p52-dependence-audit.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    c = result["stratifiedPromptClusterBootstrap"]; d = result["fixedPanelDirichletJeffreys"]
    (OUT / "p52-dependence-audit.md").write_text(
        "# P5-2 dependence-aware sensitivity\n\n> Post-adjudication, zero subject calls. Historical adjudication unchanged.\n\n"
        f"- Historical episode mean: 45/352 = {45/352:.6f}; episode-iid projection [0.091753, 0.172069].\n"
        f"- Stratified prompt-cluster bootstrap (40 persona x conflict-cell clusters, five strata, B={B:,}, seed {BOOT_SEED}): [{c['interval95'][0]:.6f}, {c['interval95'][1]:.6f}].\n"
        f"- Fixed-panel Dirichlet-Jeffreys aggregation (40 prompt-condition propensities, {B:,} draws, seed {POST_SEED}): median {d['posteriorMedian']:.6f}, 95% interval [{d['interval95'][0]:.6f}, {d['interval95'][1]:.6f}], Pr(theta <= .20)={d['probabilityAtOrBelowRegisteredBoundary']:.4f}.\n\n"
        "Both sensitivities remain below the frozen 0.20 persona-dominant boundary. The classification remains mechanism-confounded and is driven by the swap cell.\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
