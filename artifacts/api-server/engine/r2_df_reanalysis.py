#!/usr/bin/env python3
"""R2 item 2 — Dal Bó–Fréchette (2011) microdata reanalysis (EXPLORATORY).

Zero LLM calls; public-data reanalysis only. The AEA/openICPSR
replication package is login-walled from this environment, so this
script is committed FULLY WRITTEN AND SELFTESTED against a synthetic
fixture with the expected schema; the moment the operator drops the
package into data/external/df2011/ it is one command:

    uv run --with pandas --with numpy python engine/r2_df_reanalysis.py

Selftest (synthetic fixture, no external data):

    uv run --with pandas --with numpy python engine/r2_df_reanalysis.py --selftest

Expected input: one or more .dta or .csv files under data/external/df2011/
with (at least, case-insensitive, common aliases handled) columns:
    subject id   : id | subject | subj
    supergame    : match | supergame | sequence
    round        : round | period
    cooperation  : coop | c | action (1=cooperate, 0=defect)
    delta        : delta | dc
    stage payoff : r | r1 (treatment R, if present)
If the real package schema differs, adjust COLMAP below — nothing else.

Outputs docs/analysis/r2/df2011-reanalysis.md + figure-sources CSVs:
  (a) first-supergame-only (first-exposure) view
  (b) experienced view (pooled and last-quarter supergames)
  (c) learning trajectory of round-1 cooperation by supergame index
  plus per-subject first-round frequencies, endpoint mass (p<=0.05 /
  p>=0.95), within-subject variability, between-subject variance, and a
  downsampled panel matched to per-persona opportunity counts (n=12
  seat-trials per persona-cell in our design).

Explicit scope note (also printed into the doc): DF2011's treatment was
BETWEEN-SESSION; the human individual response Delta_i is unobserved in
their design. Our within-persona Delta_i has no direct human analogue in
this data. This reanalysis contextualizes; it cannot create a matched
comparison. Every derived pin is a published, nonmatched comparator.
"""
from __future__ import annotations

import glob
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "..", "..", "..")
DATA = os.path.join(ROOT, "data", "external", "df2011")
OUT = os.path.join(ROOT, "docs", "analysis", "r2")
FIG = os.path.join(OUT, "figure-sources")
PER_PERSONA_N = 12          # seat-trials per persona-cell in our design
RNG_SEED = 20260729

COLMAP = {"id": ["id", "subject", "subj"],
          "match": ["match", "supergame", "sequence"],
          "round": ["round", "period"],
          "coop": ["coop", "c", "action"],
          "delta": ["delta", "dc"],
          "r": ["r", "r1"]}

BANNER = ("> **STATUS: EXPLORATORY — R2 item 2, public-data reanalysis "
          "of the Dal Bó & Fréchette (2011) replication microdata. Zero "
          "LLM calls.**\n>\n"
          "> **Design note (read first):** the DF2011 treatment was "
          "**between-session**, so the human individual response Δᵢ is "
          "unobserved in their design. Our within-persona Δᵢ has **no "
          "direct human analogue** in this data. This reanalysis "
          "contextualizes; it cannot create a matched comparison. Every "
          "number below is a **published, nonmatched comparator**.\n")


def _find(df: pd.DataFrame, key: str) -> str:
    cols = {c.lower(): c for c in df.columns}
    for alias in COLMAP[key]:
        if alias in cols:
            return cols[alias]
    raise SystemExit(f"required column '{key}' not found "
                     f"(aliases {COLMAP[key]}); columns: {list(df.columns)}")


def load() -> pd.DataFrame:
    files = sorted(glob.glob(os.path.join(DATA, "*.dta")) +
                   glob.glob(os.path.join(DATA, "*.csv")))
    if not files:
        raise SystemExit(
            f"no .dta/.csv under {os.path.relpath(DATA, ROOT)} — see "
            "docs/analysis/df-microdata-PENDING.md for download steps")
    frames = []
    for f in files:
        frames.append(pd.read_stata(f) if f.endswith(".dta")
                      else pd.read_csv(f))
    df = pd.concat(frames, ignore_index=True)
    ren = {_find(df, k): k for k in ("id", "match", "round", "coop",
                                     "delta")}
    try:
        ren[_find(df, "r")] = "r"
    except SystemExit:
        df["__r__"] = np.nan
        df = df.rename(columns={"__r__": "r"})
    df = df.rename(columns=ren)
    # fail-closed cooperation recoding: only explicitly known encodings
    raw = df["coop"]
    if raw.dtype == object:
        mapping = {"c": 1, "coop": 1, "cooperate": 1, "1": 1,
                   "d": 0, "defect": 0, "0": 0}
        vals = set(raw.astype(str).str.strip().str.lower().unique())
        unknown = vals - set(mapping)
        if unknown:
            raise SystemExit(
                f"unrecognized cooperation labels {sorted(unknown)} — "
                "refusing to guess; extend the mapping in load() after "
                "checking the package codebook")
        df["coop"] = raw.astype(str).str.strip().str.lower().map(mapping)
    else:
        vals = set(pd.to_numeric(raw, errors="raise").dropna().unique())
        if vals <= {0, 1}:
            df["coop"] = raw.astype(int)
        elif vals <= {1, 2}:
            raise SystemExit(
                "cooperation coded {1,2} — ambiguous (which is cooperate?); "
                "check the package codebook and recode explicitly in load()")
        else:
            raise SystemExit(
                f"unexpected cooperation values {sorted(vals)[:10]} — "
                "refusing to threshold; check the package codebook")
    df = df.dropna(subset=["coop"])
    print("cooperation coding audit: values OK, "
          f"n={len(df)}, coop rate={df['coop'].mean():.3f}")
    return df


def synthetic_fixture() -> pd.DataFrame:
    """Schema-faithful fixture: 2 treatments x 20 subjects x 10
    supergames, round-1 rows only differ from later rounds by 'round'."""
    rng = np.random.default_rng(RNG_SEED)
    rows = []
    for delta, base in ((0.5, 0.25), (0.75, 0.55)):
        for sid in range(20):
            p = np.clip(rng.normal(base + 0.02, 0.25), 0.02, 0.98)
            for m in range(1, 11):
                pm = np.clip(p + 0.015 * m, 0, 1)   # mild learning drift
                nr = 1 + rng.geometric(1 - delta)
                for rd in range(1, int(nr) + 1):
                    rows.append({"id": f"{delta}-{sid}", "match": m,
                                 "round": rd, "coop": int(rng.random() < pm),
                                 "delta": delta, "r": 40})
    return pd.DataFrame(rows)


def analyze(df: pd.DataFrame, fixture: bool) -> None:
    os.makedirs(FIG, exist_ok=True)
    r1 = df[df["round"] == 1].copy()
    tag = "SYNTHETIC-FIXTURE " if fixture else ""
    rng = np.random.default_rng(RNG_SEED)
    L = [f"# DF2011 microdata reanalysis — R2 item 2 {tag}".rstrip(), "",
         BANNER]
    if fixture:
        L.append("> **THIS RUN USED THE SYNTHETIC SELFTEST FIXTURE — "
                 "numbers below are NOT DF2011 values and exist only to "
                 "prove the pipeline end-to-end.**\n")
    a = L.append

    def view(name: str, sub: pd.DataFrame) -> dict:
        per = sub.groupby(["delta", "id"])["coop"].agg(["mean", "count"])
        out = {}
        for d, g in per.groupby(level="delta"):
            m = g["mean"]
            k = int(min(PER_PERSONA_N, g["count"].min()))
            ds_means = []
            for (dd, sid), row in g.iterrows():
                obs = sub[(sub["delta"] == dd) & (sub["id"] == sid)]["coop"]
                take = rng.choice(obs.to_numpy(), size=k, replace=False)
                ds_means.append(take.mean())
            ds = pd.Series(ds_means)
            out[d] = {"nSubjects": len(m), "mean": m.mean(),
                      "betweenSD": m.std(ddof=1),
                      "endpointLo": (m <= 0.05).mean(),
                      "endpointHi": (m >= 0.95).mean(),
                      "withinVar": (m * (1 - m)).mean(),
                      "downsampled_k": k,
                      "downsampledSD": ds.std(ddof=1),
                      "dsEndpointLo": (ds <= 0.05).mean(),
                      "dsEndpointHi": (ds >= 0.95).mean()}
        rows = [{"view": name, "delta": d, **v} for d, v in out.items()]
        pd.DataFrame(rows).round(4).to_csv(
            os.path.join(FIG, f"r2-df2011-{name}.csv"), index=False)
        return out

    def emit(name: str, title: str, out: dict) -> None:
        a(f"## {title}")
        a("")
        a("| δ | n subj | mean coop | between-SD | mass ≤.05 | mass ≥.95 "
          "| within-var | downsampled(k) SD | ds mass ≤.05 / ≥.95 |")
        a("|---|---|---|---|---|---|---|---|---|")
        for d, v in sorted(out.items()):
            a(f"| {d} | {v['nSubjects']} | {v['mean']:.3f} | "
              f"{v['betweenSD']:.3f} | {v['endpointLo']:.2f} | "
              f"{v['endpointHi']:.2f} | {v['withinVar']:.3f} | "
              f"({v['downsampled_k']}) {v['downsampledSD']:.3f} | "
              f"{v['dsEndpointLo']:.2f} / {v['dsEndpointHi']:.2f} |")
        a("")

    emit("first", "(a) First-supergame only (first exposure)",
         view("first", r1[r1["match"] == 1]))
    emit("pooled", "(b1) Experienced: pooled over all supergames",
         view("pooled", r1))
    lastq = r1[r1["match"] > r1["match"].max() * 0.75]
    emit("late", "(b2) Experienced: last-quarter supergames",
         view("late", lastq))

    traj = (r1.groupby(["delta", "match"])["coop"].mean().reset_index())
    traj.round(4).to_csv(os.path.join(FIG, "r2-df2011-trajectory.csv"),
                         index=False)
    a("## (c) Learning trajectory — round-1 cooperation by supergame")
    a("")
    a("| δ | supergame → coop |")
    a("|---|---|")
    for d, g in traj.groupby("delta"):
        seq = " ".join(f"{int(m)}:{c:.2f}"
                       for m, c in zip(g["match"], g["coop"]))
        a(f"| {d} | {seq} |")
    a("")
    a("## Downsampling note")
    a("")
    a(f"The downsampled columns re-estimate each subject from k="
      f"{PER_PERSONA_N} opportunities (matching our per-persona "
      "seat-trial count per cell), seeded; this shows how much of the "
      "human endpoint mass and spread survives at OUR n — the honest "
      "comparison scale for any distribution-shape statement. A "
      "hierarchical (beta-binomial) separation of subject variance from "
      "finite-sample noise is the natural next step once the real "
      "package is in place; it is deliberately not fitted to the "
      "fixture.")
    a("")
    a("Figure sources: `figure-sources/r2-df2011-{first,pooled,late,"
      "trajectory}.csv`. Generated by `engine/r2_df_reanalysis.py` "
      f"(seed {RNG_SEED}).")
    name = ("df2011-reanalysis-FIXTURE-SELFTEST.md" if fixture
            else "df2011-reanalysis.md")
    with open(os.path.join(OUT, name), "w") as f:
        f.write("\n".join(L) + "\n")
    print(f"wrote docs/analysis/r2/{name}")


def main() -> int:
    if "--selftest" in sys.argv:
        df = synthetic_fixture()
        analyze(df, fixture=True)
        # invariants
        r1 = df[df["round"] == 1]
        assert set(df.columns) >= {"id", "match", "round", "coop", "delta"}
        assert r1.groupby("delta")["coop"].mean()[0.75] > \
            r1.groupby("delta")["coop"].mean()[0.5]
        print("selftest PASS")
        return 0
    analyze(load(), fixture=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
