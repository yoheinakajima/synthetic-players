"""Materialize the omitted X2-confirmation block as a schedule AMENDMENT file.

Packaging gap #2 (see provenance-notes.md): the sealed execution-schedule.json
was generated without the conditional X2-confirmation block. Its design is
fully sealed elsewhere — arms.json carries the two conf arms with authoritative
seeds; predicates.md §X2 fixes 20 episodes/side; the engine resolves the
templates via the write-once X2-conf-lo/hi resolutions. This script derives the
block MECHANICALLY from arms.json alone and writes it to a SEPARATE file,
leaving the sealed schedule byte-identical to its anchored sha256.

Derivation rule (zero constructed randomness, disclosed in the ledger):
arms in manifest order (lo before hi as they appear in arms.json), seeds
ascending as sealed, ep = 1..N per arm, model from the arm record, dispatch
order arm-major. All registered X2-confirmation analyses are episode-level and
dispatch-order-invariant.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DOCS = ROOT / "docs" / "phase4"
SEALED = DOCS / "execution-schedule.json"
OUT = DOCS / "execution-schedule-amendments.json"
SEALED_SHA_PIN = "139c1b6d514487ea2412d2ad0fa8bda36f79dffed59f4955b0180452239fa444"


def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    got = sha256(SEALED)
    if got != SEALED_SHA_PIN:
        raise SystemExit(f"REFUSING: sealed schedule sha {got} != seal-record pin {SEALED_SHA_PIN}")

    arms = json.load(open(DOCS / "arms.json"))["arms"]
    conf = [a for a in arms if a.get("block") == "X2-confirmation"]
    if [a["armId"] for a in conf] != ["p4-x2-conf-lo", "p4-x2-conf-hi"]:
        raise SystemExit(f"REFUSING: unexpected conf arms {[a['armId'] for a in conf]}")

    episodes = []
    for a in conf:
        seeds = a["seeds"]
        if a.get("model") != "gpt-4.1":
            raise SystemExit(f"REFUSING: {a['armId']} model {a.get('model')!r} != gpt-4.1 (X2 is GPT-4.1 only)")
        if len(seeds) != 20 or seeds != sorted(seeds) or seeds != list(range(seeds[0], seeds[0] + 20)):
            raise SystemExit(f"REFUSING: {a['armId']} seeds not the sealed contiguous ascending 20: {seeds[:3]}…")
        if seeds[0] != 2953 or seeds[-1] != 2972:
            raise SystemExit(f"REFUSING: {a['armId']} seeds [{seeds[0]}..{seeds[-1]}] != sealed 2953..2972")
        if int(a.get("episodes", 0)) not in (0, 20) and int(a.get("episodes", 20)) != 20:
            raise SystemExit(f"REFUSING: {a['armId']} episodes field {a.get('episodes')!r} != 20")
        for i, s in enumerate(seeds, 1):
            episodes.append({"armId": a["armId"], "block": "X2-confirmation",
                             "model": a["model"], "seed": s, "ep": i})

    doc = {
        "note": ("Amendment: X2-confirmation block omitted by the schedule generator "
                 "(conditional on screening). Derived mechanically from arms.json only; "
                 "sealed execution-schedule.json is byte-identical to its seal-record sha. "
                 "See provenance-notes.md, packaging gap #2."),
        "amendsScheduleSha256": SEALED_SHA_PIN,
        "generatedBy": "engine/phase4_amend_schedule_x2conf.py",
        "blocks": [{"block": "X2-confirmation",
                    "note": "20 eps/side, seeds 2953-2972 per side (matched pairs), gpt-4.1 self-play, "
                            "horizons drawn by runner (geometric, delta=.90, cap-120 truncation excluded per X1 rule)",
                    "episodes": episodes}],
    }
    OUT.write_text(json.dumps(doc, indent=1) + "\n")
    print(json.dumps({"episodes": len(episodes),
                      "sealedScheduleSha256": got,
                      "amendmentsSha256": sha256(OUT)}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
