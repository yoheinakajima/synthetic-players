"""Registry v4 persona generation — seeded, pre-data, no hand-picking.

16 personas from fully crossed trait factors:
  age band {early-30s, early-60s} x disposition triple
  {agreeable|competitive} x {patient|impulsive} x {risk-averse|risk-seeking}
= 2 x 2 x 2 x 2 = 16 cells. Name, exact age within band, and occupation are
drawn WITHOUT REPLACEMENT from registered lists by the seeded program PRNG
(mulberry32, bit-identical to the engine stream) — no author choice touches
any persona after the seed is registered.

Dispositions are trait words only. No game-relevant content: no mention of
games, cooperation, strategy, opponents, or payoffs anywhere in a persona.
A guard below greps every generated preamble for a banned-word list and
fails generation on any hit.

Composition rule (registered): a persona changes ONLY the system-prompt
layer, as persona_system = preamble + "\\n\\n" + <sealed bare system text of
the cell's template, byte-identical>. The user layer stays byte-identical to
the sealed Phase 3/4 templates, so every Phase 5 cell has an exact
bare-subject twin in the prior record.

Leaning classification (registered at generation, never from behavior):
cooperative-leaning iff at least 2 of {agreeable, patient, risk-averse};
defect-leaning otherwise. The full cross makes this exactly 8/8.

Temperature-sweep subset (registered seeded draw): 2 cooperative-leaning +
2 defect-leaning personas, balanced across age bands (one per leaning x age
band cell), drawn by the same PRNG stream.

Usage: uv run python engine/gen_personas.py [--out <path.json>]
Deterministic: same seed => byte-identical output (generatedAt excluded from
per-persona shas; shas cover the preamble text only).
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from strategies import mulberry32  # noqa: E402

SEED = 20260728  # registered generation seed
SUBSET_SEED = 20260729  # registered temperature-subset draw seed

AGE_BANDS = [("early-30s", 30, 35), ("early-60s", 60, 65)]
D1 = ["agreeable", "competitive"]
D2 = ["patient", "impulsive"]
D3 = ["risk-averse", "risk-seeking"]

# Registered lists (neutral, no game-relevant content). Drawn without
# replacement; list order is part of the registration.
NAMES = ["Morgan", "Riley", "Casey", "Jordan", "Avery", "Quinn", "Rowan",
         "Emerson", "Sasha", "Devon", "Harper", "Reese", "Marlow", "Ellis",
         "Tatum", "Arden"]
OCCUPATIONS = ["librarian", "electrician", "nurse", "accountant",
               "landscape gardener", "pharmacist", "carpenter",
               "school teacher", "dental hygienist", "surveyor",
               "physiotherapist", "archivist", "bus driver", "optician",
               "bookkeeper", "veterinary technician"]

BANNED = ["game", "cooperat", "defect", "strateg", "opponent", "payoff",
          "player", "points", "prisoner", "dilemma", "betray", "trust",
          "reciproc", "compete against", "win", "lose"]

PREAMBLE = ("You are {name}, a {age}-year-old {occupation}. People who know "
            "you describe you as {t1}, {t2}, and {t3}.")


def _draw_without_replacement(rng, items: list[str], n: int) -> list[str]:
    pool = list(items)
    out = []
    for _ in range(n):
        i = int(rng() * len(pool))
        out.append(pool.pop(i))
    return out


def generate() -> dict:
    rng = mulberry32(SEED & 0xFFFFFFFF)
    cells = [(ab, d1, d2, d3) for ab in AGE_BANDS for d1 in D1
             for d2 in D2 for d3 in D3]
    names = _draw_without_replacement(rng, NAMES, 16)
    occs = _draw_without_replacement(rng, OCCUPATIONS, 16)
    personas = []
    for i, ((band, lo, hi), d1, d2, d3) in enumerate(cells):
        age = lo + int(rng() * (hi - lo + 1))
        preamble = PREAMBLE.format(name=names[i], age=age, occupation=occs[i],
                                   t1=d1, t2=d2, t3=d3)
        low = preamble.lower()
        for w in BANNED:
            if w in low:
                raise SystemExit(f"banned content {w!r} in persona {i}: {preamble}")
        coop_score = sum([d1 == "agreeable", d2 == "patient", d3 == "risk-averse"])
        personas.append({
            "id": f"p{i + 1:02d}",
            "factors": {"ageBand": band, "d1": d1, "d2": d2, "d3": d3},
            "name": names[i], "age": age, "occupation": occs[i],
            "preamble": preamble,
            "sha256": hashlib.sha256(preamble.encode()).hexdigest(),
            "leaning": "cooperative-leaning" if coop_score >= 2 else "defect-leaning",
            "leaningScore": coop_score,
        })
    coop = [p for p in personas if p["leaning"] == "cooperative-leaning"]
    dfct = [p for p in personas if p["leaning"] == "defect-leaning"]
    assert len(coop) == 8 and len(dfct) == 8, "full cross must split 8/8"

    # Temperature-sweep subset: one per leaning x age-band cell, seeded.
    srng = mulberry32(SUBSET_SEED & 0xFFFFFFFF)
    subset = []
    for leaning_pool in (coop, dfct):
        for band, _, _ in AGE_BANDS:
            pool = [p for p in leaning_pool if p["factors"]["ageBand"] == band]
            subset.append(pool[int(srng() * len(pool))]["id"])

    return {
        "registry": "v4-proposed",
        "status": "PROPOSED — unsealed; seals append-only into registry v4 "
                  "with per-persona shas at freeze",
        "generatedAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "seed": SEED, "subsetSeed": SUBSET_SEED,
        "prng": "mulberry32 (bit-identical engine stream)",
        "compositionRule": "persona_system = preamble + '\\n\\n' + sealed bare "
                           "system text of the cell's template (byte-identical); "
                           "user layer byte-identical to sealed Phase 3/4 "
                           "templates; self-play pairs use the same persona in "
                           "both seats",
        "leaningRule": "cooperative-leaning iff >=2 of {agreeable, patient, "
                       "risk-averse}; fixed at generation, never from behavior",
        "bannedContentGuard": BANNED,
        "temperatureSubset": subset,
        "personas": personas,
    }


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "..", "..", "docs", "phase5",
                       "personas-v4-proposed.json")
    if "--out" in sys.argv:
        out = sys.argv[sys.argv.index("--out") + 1]
    data = generate()
    with open(out, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    print(f"wrote {out}")
    for p in data["personas"]:
        mark = "*" if p["id"] in data["temperatureSubset"] else " "
        print(f"{mark} {p['id']} [{p['leaning'][:4]}] {p['preamble']}")
