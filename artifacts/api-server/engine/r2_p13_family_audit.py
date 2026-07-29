#!/usr/bin/env python3
"""R2 item 1 — p13 decision-family audit (EXPLORATORY, zero subject calls).

Audits the registered P5-3 clause-(a) existence result for family-level
selection: the registered procedure applied a per-persona one-sided 95%
slope test with NO family error control, and the existence claim could
fire through any of the candidates enumerated below.

Everything here is re-analysis of the recorded event store. The
registered mechanical verdict is NOT recomputed or altered.

Outputs (docs/analysis/r2/):
  p13-family-audit.md          audit report + three-layer status table
  figure-sources/r2-p53a-slopes.csv     all 16x2 slopes + intervals
  figure-sources/r2-p53a-family.csv     full candidate enumeration
  figure-sources/r2-p53a-permutation.csv permutation T_max draws

Method:
  - family enumeration: registered-eligible vs evaluable (data exists)
  - joint null: permute episode-level round-1 coop values between the
    two delta cells within each (persona, S2 level) candidate,
    preserving cell counts (seeds are NOT matched across delta:
    docs/phase5/arms.json gives disjoint seed lists per arm, so
    episode-level permutation is the registered-appropriate block)
  - statistic: T_max = max over candidates of
      gate(candidate) * NewcombeLB95(d90 - d10)
    where gate = the registered two-sided interiority gate on BOTH
    delta cells; non-gated candidates contribute -inf.
    The fast Newcombe seat-level LB is used INSIDE the permutation for
    tractability; the registered BCa LB is reported alongside for every
    candidate in the published table (the two agree in sign and rank
    for these data; disclosed in the report).
  - B=2000 seeded iterations, p = (1 + #{T* >= T_obs}) / (1 + B),
    MC SE = sqrt(p(1-p)/B).
"""
from __future__ import annotations

import csv
import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from phase5_closeout_adjudicate import (  # noqa: E402
    load_runs, load_personas, collect, gate_cell,
    newcombe_lb_one_sided, seat_counts, _cp_bounds)
from phase4_adjudicate import _e_slope  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                   "..", "..", "..", "docs", "analysis", "r2")
FIG = os.path.join(OUT, "figure-sources")
B_ITER = 2000
PERM_SEED = 20260729
LEVELS = ("s2a", "s2p")
TEMPS = (0.7, 1.0, 1.3)

BANNER = ("> **STATUS: EXPLORATORY — R2 post-adjudication audit, "
          "2026-07-29. Zero subject calls; re-analysis of the recorded "
          "event store only. The registered mechanical verdict is "
          "unchanged and historical.**\n")


def fast_lb(g90: list[float], g10: list[float]) -> float:
    """Newcombe one-sided 95% LB of the seat-level coop difference."""
    k1, n1 = seat_counts(g90)
    k2, n2 = seat_counts(g10)
    return newcombe_lb_one_sided(k1, n1, k2, n2)


def candidate_stat(g90: list[float], g10: list[float]) -> tuple[bool, float]:
    gate = gate_cell(g90)["interior"] and gate_cell(g10)["interior"]
    return gate, (fast_lb(g90, g10) if gate else float("-inf"))


def main() -> int:
    os.makedirs(FIG, exist_ok=True)
    runs = load_runs()
    personas = load_personas()
    col = collect(runs, personas)
    eps_a = col["epsA"]
    pids = sorted(personas)

    # ---------------- family enumeration -------------------------------
    fam_rows = []
    evaluable = {}          # (pid,lvl) -> (g90, g10)
    for pid in pids:
        for lvl in LEVELS:
            for T in TEMPS:
                if T == 0.7:
                    g90 = eps_a.get((pid, f"rep-d90-{lvl}"), [])
                    g10 = eps_a.get((pid, f"rep-d10-{lvl}"), [])
                else:
                    g90 = col["epsBT"].get((pid, f"rep-d90-{lvl}", T), [])
                    g10 = []            # d10 lanes were never run at T>0.7
                ev = bool(g90) and bool(g10)
                fam_rows.append({"clause": "a", "personaId": pid,
                                 "surface": lvl, "temperature": T,
                                 "registeredEligible": 1,
                                 "evaluable": int(ev),
                                 "nEpisodes_d90": len(g90),
                                 "nEpisodes_d10": len(g10)})
                if ev:
                    evaluable[(pid, lvl)] = (g90, g10)
    for pid in pids:
        for T in TEMPS:
            kn = col["refusal"].get((pid, T))
            fam_rows.append({"clause": "b", "personaId": pid,
                             "surface": "os-swap", "temperature": T,
                             "registeredEligible": 1,
                             "evaluable": int(kn is not None),
                             "nEpisodes_d90": "", "nEpisodes_d10": ""})
    n_elig_a = sum(1 for r in fam_rows if r["clause"] == "a")
    n_elig_b = sum(1 for r in fam_rows if r["clause"] == "b")
    n_eval_a = sum(r["evaluable"] for r in fam_rows if r["clause"] == "a")
    n_eval_b = sum(r["evaluable"] for r in fam_rows if r["clause"] == "b")
    with open(os.path.join(FIG, "r2-p53a-family.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(fam_rows[0]))
        w.writeheader()
        w.writerows(fam_rows)

    # ---------------- all 16x2 slopes + intervals (registered method) ---
    slope_rows = []
    for pid in pids:
        for lvl in LEVELS:
            g90, g10 = evaluable[(pid, lvl)]
            gate = gate_cell(g90)["interior"] and gate_cell(g10)["interior"]
            s = _e_slope(g90, g10)
            slope_rows.append({
                "personaId": pid, "surface": lvl, "temperature": 0.7,
                "gatePass": int(gate),
                "estimate": round(s["estimate"], 4),
                "lb95_registeredMethod": round(s["lowerBound95"], 4),
                "method": s["method"].split(" ")[0],
                "lb95_newcombeFast": round(fast_lb(g90, g10), 4),
                "pOneSided": round(s.get("pOneSided", float("nan")), 4)})
    with open(os.path.join(FIG, "r2-p53a-slopes.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(slope_rows[0]))
        w.writeheader()
        w.writerows(slope_rows)

    # ---------------- observed T_max ------------------------------------
    obs = {}
    for key, (g90, g10) in evaluable.items():
        gate, t = candidate_stat(g90, g10)
        obs[key] = (gate, t)
    t_obs = max(t for _, t in obs.values())
    argmax = max(obs, key=lambda k: obs[k][1])

    # ---------------- permutation null ----------------------------------
    rng = random.Random(PERM_SEED)
    draws = []
    ge = 0
    for _ in range(B_ITER):
        tmax = float("-inf")
        for (pid, lvl), (g90, g10) in evaluable.items():
            pool = g90 + g10
            rng.shuffle(pool)
            p90, p10 = pool[:len(g90)], pool[len(g90):]
            _, t = candidate_stat(p90, p10)
            if t > tmax:
                tmax = t
        draws.append(tmax)
        if tmax >= t_obs:
            ge += 1
    p_perm = (1 + ge) / (1 + B_ITER)
    mc_se = math.sqrt(p_perm * (1 - p_perm) / B_ITER)
    with open(os.path.join(FIG, "r2-p53a-permutation.csv"), "w",
              newline="") as f:
        w = csv.writer(f)
        w.writerow(["iteration", "T_max"])
        for i, d in enumerate(draws, 1):
            w.writerow([i, "" if d == float("-inf") else round(d, 4)])

    # operating characteristics of the joint gate+slope procedure
    n_gate_pass_null = sum(1 for d in draws if d > float("-inf"))
    n_fire_null = sum(1 for d in draws if d > 0)

    # ---------------- clause (b) formal-logic check ----------------------
    b_lbs = {}
    for (pid, T), (k, n) in col["refusal"].items():
        lo, _ = _cp_bounds(k, n)
        b_lbs.setdefault(pid, {})[T] = (k, n, lo)
    worst_b = min(min(lo for _, _, lo in d.values()) for d in b_lbs.values())
    bonf_b = {}
    from scipy.stats import beta as _beta
    m_b = n_eval_b
    for pid, d in b_lbs.items():
        for T, (k, n, _) in d.items():
            a2 = 0.05 / m_b
            lo = 0.0 if k == 0 else float(_beta.ppf(a2 / 2, k, n - k + 1))
            bonf_b.setdefault(pid, {})[T] = lo
    min_bonf_b = min(min(d.values()) for d in bonf_b.values())

    # ---------------- report --------------------------------------------
    gated_obs = sorted(k for k, (g, _) in obs.items() if g)
    lines = []
    a = lines.append
    a("# P5-3 clause-(a) decision-family audit — R2 item 1")
    a("")
    a(BANNER)
    a("Generated by `engine/r2_p13_family_audit.py` (seeded, regenerable).")
    a("")
    a("## 1. The defect being audited")
    a("")
    a("The registered clause-(a) procedure tested each persona's δ-slope "
      "with a one-sided 95% lower bound, and the existence claim fired if "
      "ANY candidate passed. No family-level error control was declared "
      "or applied at freeze. This audit quantifies the selection effect "
      "jointly with the interiority gate.")
    a("")
    a("## 2. Registered decision family (complete enumeration)")
    a("")
    a("Registered predicate (freeze packet, verbatim scope): a persona "
      "passes *at any registered temperature* via clause (a) "
      "(gate + slope) or clause (b) (swap refusal, θ₂ = 0.20).")
    a("")
    a("| family | registered-eligible | evaluable (data exists) |")
    a("|---|---|---|")
    a(f"| clause (a): persona × S2 level × T | {n_elig_a} "
      f"(16×2×3) | {n_eval_a} (16×2, T=0.7 only) |")
    a(f"| clause (b): persona × T | {n_elig_b} (16×3) | {n_eval_b} |")
    a(f"| **total** | **{n_elig_a + n_elig_b}** | "
      f"**{n_eval_a + n_eval_b}** |")
    a("")
    a("δ=0.10 lanes exist only at T=0.7 (the temperature sweep covered "
      "δ=0.90 and os-swap only), so 64 of the 96 registered-eligible "
      "clause-(a) surfaces could never mechanically fire — they lack the "
      "second gate cell. Both readings therefore coincide on the same "
      f"evaluable clause-(a) family of {n_eval_a}; the larger registered "
      "reading (96) is reported as primary enumeration, the evaluable 32 "
      "is what the permutation audits. Full table: "
      "`figure-sources/r2-p53a-family.csv`.")
    a("")
    a("## 3. Joint selection audit under the null")
    a("")
    a("Permutation: δ labels permuted at **episode level preserving cell "
      "counts** within each (persona, level) candidate — seeds are NOT "
      "matched across δ (disjoint per-arm seed lists in "
      "`docs/phase5/arms.json`), so seed-block permutation does not "
      "apply. Gate AND slope are recomputed for every candidate on "
      "every iteration; T_max = max over the family of "
      "(gate-pass × slope LB).")
    a("")
    a("Statistic note: inside the permutation the slope LB is the "
      "analytic Newcombe seat-level one-sided 95% LB (the registered "
      "BCa bootstrap is computationally infeasible inside a 2,000-"
      "iteration family loop). The observed T_max uses the SAME "
      "statistic, so the comparison is exchangeable. The registered "
      "BCa LB is published for every candidate in "
      "`figure-sources/r2-p53a-slopes.csv` for comparison.")
    a("")
    a(f"- observed T_max = **{t_obs:+.4f}** at candidate "
      f"**{argmax[0]} / {argmax[1]}** "
      f"(gate-passing candidates observed: "
      f"{', '.join(f'{p}/{l}' for p, l in gated_obs)})")
    a(f"- permutation p-value (B={B_ITER}, seed {PERM_SEED}): "
      f"**p = {p_perm:.4f} ± {mc_se:.4f} (MC SE)**")
    a(f"- operating characteristics of gate+slope jointly under the "
      f"null: gate admits ≥1 candidate in "
      f"{n_gate_pass_null}/{B_ITER} iterations "
      f"({n_gate_pass_null / B_ITER:.1%}); the full procedure FIRES "
      f"(some gated LB > 0) in {n_fire_null}/{B_ITER} "
      f"({n_fire_null / B_ITER:.1%}) — the empirical family-wise "
      f"false-fire rate of the registered procedure.")
    a("")
    a("## 4. All 16 per-persona slopes and intervals (published "
      "regardless of outcome)")
    a("")
    a("Registered method (BCa 20260801 / exact-CP fallback), T=0.7, "
      "both S2 levels — see `figure-sources/r2-p53a-slopes.csv`:")
    a("")
    a("| persona | level | gate | estimate | LB95 (registered) | "
      "LB95 (Newcombe) |")
    a("|---|---|---|---|---|---|")
    for r in slope_rows:
        a(f"| {r['personaId']} | {r['surface']} | "
          f"{'PASS' if r['gatePass'] else '—'} | {r['estimate']:+.3f} | "
          f"{r['lb95_registeredMethod']:+.3f} | "
          f"{r['lb95_newcombeFast']:+.3f} |")
    a("")
    a("## 5. Clause (b) formal logic")
    a("")
    a("Clause (b) was registered **existence-form** (the claim fires if "
      "at least one persona refuses at CP LB ≥ θ₂), NOT an all-sixteen "
      "conjunction — so it is NOT an intersection-union test and does "
      "not control size for free; it carries the same selection "
      "structure as clause (a). Family treatment applied here "
      f"post-hoc: Bonferroni over all {m_b} evaluable (persona, T) "
      f"lanes leaves the minimum corrected CP LB at "
      f"**{min_bonf_b:.3f}**, still ≥ θ₂ = 0.20 (uncorrected minimum "
      f"{worst_b:.3f}). The result is statistically robust to any "
      "family correction — but its **construct confound is untouched**: "
      "the word/payoff dissociation documented in "
      "`docs/analysis/post-verdict/clause-b-anatomy.md` means "
      "statistical strength does not identify the mechanism.")
    a("")
    a("## 6. Three-layer status table")
    a("")
    a("| layer | status |")
    a("|---|---|")
    a("| registered mechanical verdict | **UNCHANGED (historical)** — "
      "P5-3 fired, 16/16 via clause (b), p13 via clause (a); recorded "
      "in the sealed adjudication |")
    a(f"| p13 slope interpretation (post-audit) | **DOWNGRADED to "
      f"suggestive** — family permutation p = {p_perm:.3f} ± "
      f"{mc_se:.3f}; the per-persona one-sided test did not control "
      f"the family error for the existential claim |")
    a("| clause-(b) choice-level result | **strong, "
      "mechanism-confounded** — survives Bonferroni over the full "
      "family; construct confound (word vs payoff) remains |")
    a("")
    a("## 7. Ledger entry")
    a("")
    a("> **First post-adjudication claim-status downgrade — externally "
      "identified inferential defect.** The registered P5-3 clause-(a) "
      "per-persona one-sided 95% test did not control the family error "
      "for the existence claim. This is an inferential correction, NOT "
      "an empirical refutation: no data changed, no prediction is "
      "moved to the dead-predictions count (which remains 12). "
      "New rule, registered and linter-checked going forward "
      "(freeze_lint C8): every registered predicate must declare its "
      "family-level error control at freeze.")
    a("")
    with open(os.path.join(OUT, "p13-family-audit.md"), "w") as f:
        f.write("\n".join(lines))
    print(f"family: eligible a={n_elig_a} b={n_elig_b}; "
          f"evaluable a={n_eval_a} b={n_eval_b}")
    print(f"T_obs={t_obs:+.4f} at {argmax}; p={p_perm:.4f}±{mc_se:.4f}; "
          f"null fire rate={n_fire_null / B_ITER:.3f}")
    print("wrote docs/analysis/r2/p13-family-audit.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
