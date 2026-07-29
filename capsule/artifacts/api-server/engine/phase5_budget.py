"""Phase 5 call table from LEDGER PRICES (instance-ledger rule 5 / A-OVH-2).

Every per-episode price below is derived from the Phase 4 budget ledger
(budget.db `spend` table) — calls per run as the store recorded them — never
from design-unit counts. Prices are the MAX observed calls/run for the
matching block x model x delta class (conservative: retries included).

Usage: uv run python engine/phase5_budget.py [--json <out>] [--md <out>]
"""
from __future__ import annotations

import json
import math
import os
import sqlite3
import sys

ENGINE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(ENGINE, "data", "budget.db")

GLOBAL_CAP = 15000  # operator-ordered Phase 5 cap
HEADROOM = 0.075    # registered waste/retry headroom, from Phase 4 actuals:
                    # gemini partial/redispatch overhead dominated; gpt retry
                    # rate was ~0. 7.5% > every observed per-block overshoot.


def ledger_prices() -> dict:
    c = sqlite3.connect(DB)
    def q(sql, *a):
        return c.execute(sql, a).fetchall()
    prices = {}
    # one-shot price: D2 (one-shot swap block), per model, max calls/run
    for model in ("gpt-4.1", "gemini-2.5-flash"):
        rows = q("SELECT run_id, SUM(calls) FROM spend WHERE block='D2' AND model=? GROUP BY run_id", model)
        prices[f"oneshot:{model}"] = max(r[1] for r in rows)
    # repeated PD by delta: E arms encode d10/d90
    for model in ("gpt-4.1", "gemini-2.5-flash"):
        for d in ("d10", "d90"):
            rows = q("SELECT run_id, SUM(calls) FROM spend WHERE block='E' AND model=? AND arm_id LIKE ? GROUP BY run_id",
                     model, f"%-{d}-%")
            per_run = [r[1] for r in rows]
            prices[f"rep-{d}:{model}"] = max(per_run)
            prices[f"rep-{d}:{model}:mean"] = round(sum(per_run) / len(per_run), 2)
    # sentinel: 2 calls/run observed both models
    rows = q("SELECT run_id, SUM(calls) FROM spend WHERE block='sentinel' GROUP BY run_id")
    prices["sentinel"] = max(r[1] for r in rows)
    c.close()
    return prices


def build_table(p: dict) -> dict:
    G, X = "gpt-4.1", "gemini-2.5-flash"
    # mean prices for projection; max prices held as per-episode bound
    d90g, d10g = p[f"rep-d90:{G}:mean"], p[f"rep-d10:{G}:mean"]
    d90x = p[f"rep-d90:{X}:mean"]
    osg, osx = p[f"oneshot:{G}"], p[f"oneshot:{X}"]

    rows = []
    def row(tier, block, model, episodes, per_ep, note=""):
        calls = math.ceil(episodes * per_ep)
        rows.append({"tier": tier, "block": block, "model": model,
                     "episodes": episodes, "callsPerEpisode": per_ep,
                     "calls": calls, "note": note})
        return calls

    # Tier A — primary, gpt-4.1, T=0.7, ALL 16 personas, all 6 cells
    row("A", "rep-PD d=0.10 x S2{p,a} (2 cells)", G, 16 * 2 * 6, d10g,
        "16 personas x 2 cells x 6 ep")
    row("A", "rep-PD d=0.90 x S2{p,a} (2 cells)", G, 16 * 2 * 6, d90g,
        "16 personas x 2 cells x 6 ep")
    row("A", "one-shot label-swap", G, 16 * 20, osg, "16 x 20 ep")
    row("A", "one-shot community", G, 16 * 20, osg, "16 x 20 ep")

    # Tier B — temperature sweep, gpt-4.1, T in {1.0, 1.3},
    # registered 4-persona subset x 3 cells (d=.90 pair + swap)
    row("B", "rep-PD d=0.90 pair, T sweep", G, 4 * 2 * 2 * 6, d90g,
        "4 personas x 2 cells x 2 temps x 6 ep")
    row("B", "label-swap, T sweep", G, 4 * 2 * 20, osg,
        "4 personas x 2 temps x 20 ep")
    # Bare-subject temperature twin (de-aliases T from persona conditioning)
    row("B", "bare subject, T sweep, d=0.90 pair", G, 2 * 2 * 6, d90g,
        "1 bare x 2 cells x 2 temps x 6 ep")
    row("B", "bare subject, T sweep, swap", G, 2 * 20, osg,
        "1 bare x 2 temps x 20 ep")

    # Tier C — gemini replication tier, T=0.7, core cells, reduced.
    # Costed separately for clean drop (shedding step 1).
    row("C", "rep-PD d=0.90 pair (gemini)", X, 8 * 2 * 4, d90x,
        "8-persona registered half x 2 cells x 4 ep")
    row("C", "label-swap (gemini)", X, 8 * 10, osx, "8 x 10 ep")

    # Sentinels — persona-conditioned fingerprint cell + bare cell, per model,
    # per-window indexing armed from check 1
    row("S", "sentinel battery", "both", 10 * 2 * 2 * 5, p["sentinel"],
        "10 checks x 2 models x 2 cells x 5 ep")
    # Entry/infra — revision pin + per-T echo assertion battery
    rows.append({"tier": "S", "block": "gate0-style entry verification",
                 "model": "both", "episodes": 0, "callsPerEpisode": 0,
                 "calls": 24, "note": "revision pin + per-T echo assertion, "
                 "3 temps x 2 models x 4 calls"})

    subtotal = sum(r["calls"] for r in rows)
    tierC = sum(r["calls"] for r in rows if r["tier"] == "C")
    headroom = math.ceil(subtotal * HEADROOM)
    total = subtotal + headroom
    return {
        "ledgerPrices": p,
        "rows": rows,
        "subtotal": subtotal,
        "tierC_separable": tierC,
        "headroom": {"rate": HEADROOM, "calls": headroom},
        "total": total, "globalCap": GLOBAL_CAP,
        "underCap": total <= GLOBAL_CAP,
        "sheddingOrder": [
            "1. Drop Tier C (gemini replication) whole — costed separately above",
            "2. Tier B rep-PD episodes 6 -> 4 per cell (both temps equally)",
            "3. Tier A rep-PD episodes 6 -> 4 per cell (all personas kept)",
            "4. One-shot episodes 20 -> 12 (all tiers, all personas kept)",
            "5. Freeze. NEVER shed personas (kills the zero-of-16 claim) or "
            "sentinels (kills attestation) — shedding reduces episodes only.",
        ],
    }


def to_md(t: dict) -> str:
    L = ["| Tier | Block | Model | Episodes | Calls/ep (ledger) | Calls |",
         "|---|---|---|---|---|---|"]
    for r in t["rows"]:
        L.append(f"| {r['tier']} | {r['block']} — {r['note']} | {r['model']} | "
                 f"{r['episodes']} | {r['callsPerEpisode']} | {r['calls']} |")
    L += [f"| | **Subtotal** | | | | **{t['subtotal']}** |",
          f"| | Waste/retry headroom ({t['headroom']['rate']:.1%}, from Phase 4 "
          f"ledger actuals) | | | | {t['headroom']['calls']} |",
          f"| | **Total** (cap {t['globalCap']}) | | | | **{t['total']}** |",
          f"| | Tier C alone (clean-drop line) | | | | {t['tierC_separable']} |"]
    return "\n".join(L)


if __name__ == "__main__":
    t = build_table(ledger_prices())
    print(json.dumps({k: v for k, v in t.items() if k != "rows"}, indent=2))
    print(to_md(t))
    if "--json" in sys.argv:
        with open(sys.argv[sys.argv.index("--json") + 1], "w") as f:
            json.dump(t, f, indent=2); f.write("\n")
    if "--md" in sys.argv:
        with open(sys.argv[sys.argv.index("--md") + 1], "w") as f:
            f.write(to_md(t) + "\n")
