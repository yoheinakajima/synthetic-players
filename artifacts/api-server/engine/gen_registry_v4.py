"""Registry v4 generator — Phase 5 arms manifest + sealed execution schedule.

Emits, deterministically (no live calls, no data-dependence):
  docs/phase5/personas-v4.json        sealed copy of the approved proposal
  docs/phase5/arms.json               per-arm pins: template sha × persona
                                      sha × temperature × seeds × model
  docs/phase5/execution-schedule.json mulberry32-seeded interleave
and flips prompts/registry.json registryVersion to "phase5-v4-proposed"
with an appended (append-only) "phase5" anchor block: personas file sha,
discussion-branches sha, scope-seal sha. The seal itself is the later
one-line flip "phase5-v4-proposed" → "phase5-v4", exactly like phase4-v3.

Registered constants (freeze packet §§1–6, operator-approved 2026-07-28):
  Tier A: 16 personas × 6 cells, T=0.7, gpt-4.1 (rep 6 ep, one-shot 20 ep)
  Tier B: subset {p02,p06,p11,p15} + bare twin × {δ=.90 pair, swap} ×
          T ∈ {1.0, 1.3} (rep 6 ep, swap 20 ep)
  Tier C: gemini-2.5-flash, T=0.7, balanced 8-persona half (seeded draw,
          seed 20260730) × {δ=.90 pair (4 ep), swap (10 ep)}
  Sentinels: per model, persona-p01 fingerprint + bare fingerprint,
          rep-δ90 w1 horizon-forced-1; pool 46001 + check*10.
  Schedule interleave seed: 20260731. Episode seed lanes: 50001+.
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from provenance import sha256_hex, template_sha  # noqa: E402
from strategies import mulberry32  # noqa: E402

_HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.normpath(os.path.join(_HERE, "..", "..", ".."))
P5 = os.path.join(REPO_ROOT, "docs", "phase5")
REGISTRY_PATH = os.path.join(_HERE, "..", "prompts", "registry.json")

PD = {"rr": 3, "rs": 0, "rt": 5, "rp": 1}
SUBSET_B = ["p02", "p06", "p11", "p15"]  # sealed draw, seed 20260729
SCHEDULE_SEED = 20260731
TIER_C_DRAW_SEED = 20260730
SEED_LANE_BASE = 50_001

CELLS = {
    # cellId: (templateId, deltaPct, bindings-extra, repEp?, block-kind)
    "rep-d10-s2a": ("pd-rep-w1-neu-cf-ad", 10, {}, "rep"),
    "rep-d10-s2p": ("pd-rep-w2a-neu-cf-ad", 10, {}, "rep"),
    "rep-d90-s2a": ("pd-rep-w1-neu-cf-ad", 90, {}, "rep"),
    "rep-d90-s2p": ("pd-rep-w2a-neu-cf-ad", 90, {}, "rep"),
    "os-swap": ("pd-os-w1-sem-cf-ad", None, {"labelRoleMap": "swapped"}, "os"),
    "os-community": ("pd-oneshot-v1", None, {"framing": "community"}, "os"),
}
TIER_B_CELLS = ["rep-d90-s2a", "rep-d90-s2p", "os-swap"]
TIER_C_CELLS = ["rep-d90-s2a", "rep-d90-s2p", "os-swap"]


def tier_c_half(personas: list[dict]) -> list[str]:
    """Registered balanced half: seeded draw (mulberry32, 20260730),
    2 per leaning × age band — 4 coop + 4 defect, 4 early-30s + 4 early-60s."""
    rng = mulberry32(TIER_C_DRAW_SEED)
    chosen: list[str] = []
    for leaning in ("cooperative-leaning", "defect-leaning"):
        for band in ("early-30s", "early-60s"):
            pool = [p["id"] for p in personas
                    if p["leaning"] == leaning and p["factors"]["ageBand"] == band]
            for _ in range(2):
                i = int(rng() * len(pool))
                chosen.append(pool.pop(min(i, len(pool) - 1)))
    return sorted(chosen)


def main() -> None:
    proposed = os.path.join(P5, "personas-v4-proposed.json")
    sealed_personas = os.path.join(P5, "personas-v4.json")
    shutil.copyfile(proposed, sealed_personas)
    with open(sealed_personas, "rb") as f:
        personas_raw = f.read()
    personas_doc = json.loads(personas_raw)
    personas = personas_doc["personas"]
    by_id = {p["id"]: p for p in personas}
    for p in personas:  # fail-closed re-verification before anything binds
        assert sha256_hex(p["preamble"].encode()) == p["sha256"], p["id"]

    with open(REGISTRY_PATH) as f:
        registry = json.load(f)
    prompts = registry["prompts"]
    tids = sorted({c[0] for c in CELLS.values()})
    template_shas = {t: template_sha(prompts[t]) for t in tids}

    half_c = tier_c_half(personas)
    seed_ctr = [SEED_LANE_BASE]

    def seeds(n: int) -> list[int]:
        s = list(range(seed_ctr[0], seed_ctr[0] + n))
        seed_ctr[0] += n
        return s

    arms: list[dict] = []

    def add_arm(arm_id: str, block: str, cell: str, *, persona: str | None,
                model: str, temperature: float, episodes: int) -> None:
        tid, delta, extra, _kind = CELLS[cell]
        arm = {
            "armId": arm_id, "block": block, "cell": cell, "templateId": tid,
            "bindings": {**PD, "labelRoleMap": "aligned", **extra},
            "deltaPct": delta, "temperature": temperature, "model": model,
            "episodes": episodes, "seeds": seeds(episodes),
            "personaId": persona,
            "personaSha256": by_id[persona]["sha256"] if persona else None,
        }
        arms.append(arm)

    # Tier A — all 16 personas × 6 cells, T=0.7, gpt
    for p in personas:
        for cell, (_t, _d, _x, kind) in CELLS.items():
            add_arm(f"p5-a-{p['id']}-{cell}", f"P5A-{kind}", cell,
                    persona=p["id"], model="gpt-4.1", temperature=0.7,
                    episodes=6 if kind == "rep" else 20)

    # Tier B — subset + bare twin, T ∈ {1.0, 1.3}
    for t, tag in ((1.0, "t10"), (1.3, "t13")):
        for pid in SUBSET_B + [None]:
            for cell in TIER_B_CELLS:
                kind = CELLS[cell][3]
                who = pid or "bare"
                add_arm(f"p5-b-{who}-{cell}-{tag}", f"P5B-{kind}", cell,
                        persona=pid, model="gpt-4.1", temperature=t,
                        episodes=6 if kind == "rep" else 20)

    # Tier C — gemini, balanced half, T=0.7
    for pid in half_c:
        for cell in TIER_C_CELLS:
            kind = CELLS[cell][3]
            add_arm(f"p5-c-{pid}-{cell}", f"P5C-{kind}", cell,
                    persona=pid, model="gemini-2.5-flash", temperature=0.7,
                    episodes=4 if kind == "rep" else 10)

    # Entry battery — 3 temps × 2 models × 4 calls, bare, rep-δ90 w1 horizon
    # forced 1; ledgered overhead (operator-approved). Verifies R2 per-T echo
    # and R3 revision pin live at every (model, T) before any tier dispatch.
    for model, mtag in (("gpt-4.1", "gpt"), ("gemini-2.5-flash", "gem")):
        for t, tag in ((0.7, "t07"), (1.0, "t10"), (1.3, "t13")):
            add_arm(f"p5-entry-{mtag}-{tag}", "P5-entry", "rep-d90-s2a",
                    persona=None, model=model, temperature=t, episodes=4)

    # Sentinels — per model: persona-p01 fingerprint + bare fingerprint,
    # rep-δ90 w1, horizon forced 1, windowed seed pool (no seed lanes here).
    for model, mtag in (("gpt-4.1", "gpt"), ("gemini-2.5-flash", "gem")):
        for who in ("p01", "bare"):
            arms.append({
                "armId": f"p5-sent-{who}-{mtag}", "block": "P5-sentinel",
                "cell": "rep-d90-s2a", "templateId": "pd-rep-w1-neu-cf-ad",
                "bindings": {**PD, "labelRoleMap": "aligned"},
                "deltaPct": 90, "temperature": 0.7, "model": model,
                "episodes": None, "seeds": "windowed:46001+check*10",
                "personaId": who if who != "bare" else None,
                "personaSha256": by_id["p01"]["sha256"] if who == "p01" else None,
            })

    branches = open(os.path.join(REPO_ROOT, "docs", "paper", "discussion-branches.md"), "rb").read()
    scope = open(os.path.join(REPO_ROOT, "docs", "paper", "scope-seal.md"), "rb").read()

    manifest = {
        "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "phase": "5",
        "scheduleSeed": SCHEDULE_SEED,
        "models": {"gpt-4.1": {"revisionPin": "gpt-4.1-2025-04-14"},
                   "gemini-2.5-flash": {"revisionPin": "gemini-2.5-flash"}},
        "sealedPhase3Shas": {},
        "templateShas": template_shas,
        "seedPolicy": f"episode seed lanes sequential from {SEED_LANE_BASE}; "
                      "sentinel pool 46001 + checkIndex*10 … +9 (disjoint from Phase 4)",
        "personasFileSha256": sha256_hex(personas_raw),
        "tierCHalf": half_c,
        "tierBSubset": SUBSET_B,
        "discussionBranchesSha256": sha256_hex(branches),
        "scopeSealSha256": sha256_hex(scope),
        "compositionRule": 'persona_system = preamble + "\\n\\n" + sealed bare system text (byte-identical); user layer unchanged',
        "arms": arms,
    }
    arms_path = os.path.join(P5, "arms.json")
    with open(arms_path, "w") as f:
        json.dump(manifest, f, indent=1)

    # Sealed execution schedule: within-block mulberry32 interleave.
    rng = mulberry32(SCHEDULE_SEED)
    blocks = []
    for block in ("P5A-rep", "P5A-os", "P5B-rep", "P5B-os", "P5C-rep", "P5C-os"):
        eps = []
        for a in arms:
            if a["block"] != block:
                continue
            for i, s in enumerate(a["seeds"], 1):
                eps.append({"armId": a["armId"], "model": a["model"], "seed": s, "ep": i})
        for i in range(len(eps) - 1, 0, -1):  # Fisher–Yates with mulberry32
            j = int(rng() * (i + 1))
            eps[i], eps[j] = eps[j], eps[i]
        blocks.append({"block": block, "episodes": eps})
    schedule = {"scheduleSeed": SCHEDULE_SEED, "generatedAt": manifest["generatedAt"],
                "armsManifestSha256": sha256_hex(open(arms_path, "rb").read()),
                "blocks": blocks,
                "sentinelPlan": "10 checks; check k before/after blocks per driver plan; "
                                "4 sentinel arms × 5 episodes each, seeds 46001+k*10 … +4 per cell lane"}
    sched_path = os.path.join(P5, "execution-schedule.json")
    with open(sched_path, "w") as f:
        json.dump(schedule, f, indent=1)

    # Append-only registry anchor + version flip to -proposed.
    if registry.get("registryVersion") == "phase4-v3":
        registry["registryVersion"] = "phase5-v4-proposed"
    registry["phase5"] = {
        "personasFileSha256": manifest["personasFileSha256"],
        "armsManifestSha256": schedule["armsManifestSha256"],
        "executionScheduleSha256": sha256_hex(open(sched_path, "rb").read()),
        "discussionBranchesSha256": manifest["discussionBranchesSha256"],
        "scopeSealSha256": manifest["scopeSealSha256"],
        "note": "Phase 5 anchors, append-only; templates byte-untouched. "
                "Seal = registryVersion flip phase5-v4-proposed -> phase5-v4.",
    }
    with open(REGISTRY_PATH, "w") as f:
        json.dump(registry, f, indent=2)

    n_ep = sum(len(b["episodes"]) for b in blocks)
    print(f"arms: {len(arms)}  scheduled episodes: {n_ep}")
    for b in blocks:
        print(f"  {b['block']}: {len(b['episodes'])}")
    print(f"tier C half: {half_c}")
    print("personas sha:", manifest["personasFileSha256"][:16])


if __name__ == "__main__":
    main()
