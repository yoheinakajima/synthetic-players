#!/usr/bin/env python3
"""Phase 4 prep — extract from stored records (NO LLM calls):
1. X1 claim registration + first-evidence timestamps (API)
2. Unique raw completions + frequencies for X1 v2a/v2b arms, one full transcript per arm (engine DB)
3. llm.requested payload structure — are rendered messages stored? (engine DB)
4. Token/cost profile by batch family for the budget packet (engine DB)
5. v1 / v2a / v2b template texts from the sealed registry (for the X2 span diff)
"""
import json, sqlite3, urllib.request, collections, statistics, sys

DB = "artifacts/api-server/engine/data/engine.db"
REG = "artifacts/api-server/prompts/registry.json"
API = "http://localhost:80/api"

out = {}

def api(path):
    with urllib.request.urlopen(API + path) as r:
        return json.load(r)

# ── 1. X1 claim timestamps ───────────────────────────────────────────────────
claims = api("/claims")
x1 = [c for c in claims if "X1" in (c.get("title") or "")]
out["x1_claim"] = [
    {"id": c["id"], "title": c["title"], "createdAt": c.get("createdAt"),
     "adjudicatedAt": c.get("adjudicatedAt"), "verdict": c.get("verdict"),
     "postRegistered": c.get("postRegistered")}
    for c in x1
]

db = sqlite3.connect(DB)

# ── 2/3. events: raw completions for X arms; llm.requested structure ─────────
# find run ids per batch label via API
exps = api("/experiments")
def runs_for(label):
    return [e for e in exps if e.get("batchLabel") == label and e["status"] == "completed"]

xa = runs_for("prisoners-dilemma:llm41-para-v2a:d90:t3x")
xb = runs_for("prisoners-dilemma:llm41-para-v2b:d90:t3x")
v1d90 = runs_for("prisoners-dilemma:llm41-selfplay:d90:t3")
out["arm_run_counts"] = {"v2a": len(xa), "v2b": len(xb), "v1_d90": len(v1d90)}

def engine_run_ids(api_runs):
    ids = []
    for e in api_runs:
        meta = e.get("llmMetaJson") or {}
        if isinstance(meta, str):
            meta = json.loads(meta)
        rid = meta.get("engineRunId") or meta.get("runId")
        if rid:
            ids.append(rid)
    return ids

ids_a, ids_b, ids_v1 = engine_run_ids(xa), engine_run_ids(xb), engine_run_ids(v1d90)
out["engine_id_sample"] = {"v2a": ids_a[:2], "v2b": ids_b[:2]}

def completions_for(run_ids):
    freq = collections.Counter()
    fields = None
    for rid in run_ids:
        for (payload,) in db.execute(
            "SELECT payload FROM events WHERE run_id=? AND type='llm.responded'", (rid,)
        ):
            p = json.loads(payload)
            if fields is None:
                fields = sorted(p.keys())
            raw = p.get("raw") or p.get("content") or p.get("completion") or p.get("text")
            freq[repr(raw)] += 1
    return freq, fields

freq_a, fields_resp = completions_for(ids_a)
freq_b, _ = completions_for(ids_b)
freq_v1, _ = completions_for(ids_v1)
out["responded_fields"] = fields_resp
out["unique_completions"] = {
    "v2a": dict(freq_a.most_common()),
    "v2b": dict(freq_b.most_common()),
    "v1_d90": dict(freq_v1.most_common()),
}

# llm.requested structure — one full payload (truncate long strings for print)
for rid in ids_a[:1]:
    row = db.execute(
        "SELECT payload FROM events WHERE run_id=? AND type='llm.requested' LIMIT 1", (rid,)
    ).fetchone()
    if row:
        p = json.loads(row[0])
        out["requested_fields"] = sorted(p.keys())
        out["requested_sample"] = {
            k: (v[:400] + f"...[{len(v)} chars]" if isinstance(v, str) and len(v) > 400 else v)
            for k, v in p.items()
        }

# one complete transcript per X arm (round, actions, payoffs, raw completions in order)
def transcript(rid):
    rows = db.execute(
        "SELECT type, payload FROM events WHERE run_id=? ORDER BY id", (rid,)
    ).fetchall()
    t = []
    for typ, payload in rows:
        p = json.loads(payload)
        if typ == "llm.responded":
            t.append({"type": typ, "seat": p.get("seat"), "round": p.get("round"),
                      "raw": p.get("raw") or p.get("content") or p.get("completion")})
        elif typ in ("round.resolved", "round.completed"):
            t.append({"type": typ, **{k: p.get(k) for k in ("round", "actions", "payoffs") if k in p}})
    return t

out["transcript_v2a_runid"] = ids_a[0] if ids_a else None
out["transcript_v2a"] = transcript(ids_a[0])[:12] if ids_a else None
out["transcript_v2b_runid"] = ids_b[0] if ids_b else None

# ── 4. token/cost profile by family ─────────────────────────────────────────
fam_of = {}
for e in exps:
    L = e.get("batchLabel") or ""
    meta = e.get("llmMetaJson") or {}
    if isinstance(meta, str):
        meta = json.loads(meta)
    rid = meta.get("engineRunId") or meta.get("runId")
    if not rid:
        continue
    if ":t3x" in L: fam = "X (repeated d90 paraphrase)"
    elif ":llm41-selfplay:d" in L and "iso" not in L: fam = "A canonical repeated"
    elif "iso" in L: fam = "A iso repeated"
    elif "oneshot" in L: fam = "B one-shot"
    elif L.startswith("rock-paper-scissors:llm41"): fam = "C RPS 50-round"
    else: continue
    fam_of[rid] = fam

tok = collections.defaultdict(lambda: {"in": [], "out": [], "cost": []})
for run_id, payload in db.execute(
    "SELECT run_id, payload FROM events WHERE type='llm.responded'"
):
    fam = fam_of.get(run_id)
    if not fam:
        continue
    p = json.loads(payload)
    u = p.get("tokens") or {}
    ti = u.get("prompt") or u.get("input") or u.get("prompt_tokens")
    to = u.get("completion") or u.get("output") or u.get("completion_tokens")
    if ti is not None:
        tok[fam]["in"].append(ti)
        tok[fam]["out"].append(to or 0)
    c = p.get("cost_usd") or p.get("costUsd")
    if c is not None:
        tok[fam]["cost"].append(float(c))

out["token_profile"] = {
    fam: {
        "calls": len(v["in"]),
        "mean_in": round(statistics.mean(v["in"]), 1) if v["in"] else None,
        "mean_out": round(statistics.mean(v["out"]), 1) if v["out"] else None,
        "mean_cost_usd": round(statistics.mean(v["cost"]), 5) if v["cost"] else None,
        "total_cost_usd": round(sum(v["cost"]), 2) if v["cost"] else None,
    }
    for fam, v in tok.items()
}

# ── 5. registry template texts for v1 d90 arm + v2a + v2b ───────────────────
reg = json.load(open(REG))
out["registry_top_keys"] = sorted(reg.keys()) if isinstance(reg, dict) else f"list[{len(reg)}]"
entries = reg.get("prompts") or reg.get("templates") or reg.get("entries") or (reg if isinstance(reg, list) else [])
def summ(e):
    return {k: (v[:200] + f"...[{len(v)}]" if isinstance(v, str) and len(v) > 200 else v)
            for k, v in e.items() if k not in ("template", "system", "user")} | {
            "template_len": len(e.get("template") or e.get("user") or "")}
out["registry_entries"] = [summ(e) for e in entries] if isinstance(entries, list) else str(type(entries))

json.dump(out, open("/tmp/phase4-extract.json", "w"), indent=1)
print(json.dumps({k: out[k] for k in ["x1_claim", "arm_run_counts", "responded_fields",
                                       "requested_fields", "token_profile", "registry_top_keys"]}, indent=1))
print("\nunique completions v2a:", len(out["unique_completions"]["v2a"]),
      "| v2b:", len(out["unique_completions"]["v2b"]),
      "| v1_d90:", len(out["unique_completions"]["v1_d90"]))
print("full detail -> /tmp/phase4-extract.json")
