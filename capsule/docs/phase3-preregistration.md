# Phase 3 Pre-Registration — LLM as Behavioral Subject (DRAFT — PENDING SIGN-OFF)

**Status: NOT REGISTERED. No predicates inserted, no code written, no runs executed.**
Per the Phase 3 spec (line 29), this document presents (1) total call-count estimates per experiment and (2) the full locked predicate list with human-anchored thresholds and sources, for user sign-off. Upon sign-off, predicates are inserted into the claims registry with timestamps **before** any Phase 3 experiment row is created; the adjudicator enforces timestamp ordering and flags any claim postdating its evidence as `postRegistered` (never adjudicated).

---

## 0. Design constants (verified against our DB, not assumed)

- PD payoff matrix (existing `prisoners-dilemma`): R=3, S=0, T=5, P=1 (`[[[3,3],[0,5]],[[5,0],[1,1]]]`).
  - Cooperation supportable in SPE (grim) iff δ ≥ (T−R)/(T−P) = 2/4 = **0.50**.
  - Cooperation risk-dominant (grim vs always-defect supergame) iff (R−P)/(1−δ) ≥ T−S ⟺ δ ≥ **0.60** (= δ*).
  - δ grid {0.10, 0.50, 0.75, 0.90}: two cells below δ* (0.10 no-SPE; 0.50 SPE-boundary, not RD), two above (0.75, 0.90 SPE+RD).
- Isomorph arm (Exp A contamination probe): affine transform ×3+2 → payoffs (R,S,T,P) = (11,2,17,5). Preserves δ_SPE = 0.50 and δ* = 0.60 exactly. Both arms use neutral action labels (e.g. "J"/"F"), never "cooperate"/"defect".
- RPS: zero-sum matrix exists; metrics `avgPayoffPerRound*`, `marginalExploitability*`, `conditionalExploitability*`, `tvFromUniform*`, `lag1RepeatDeviation*` already implemented. New per-run metrics required: round-1 action, lag-1 transition matrix, win-stay/lose-shift conditionals.
- New engine strategy required: `pattern-tracker` (first-order conditional-frequency tracker, deterministic given seed). New baseline batch `rock-paper-scissors:pattern-tracker-vs-nash-mixed:t3-baseline` (20 × 50 rounds, **zero LLM calls**) is pre-registered here as the comparator for P3-C3.
- Subject protocol: one sampled completion per decision; temperature configurable and stored per experiment (see §3 decision); minimal behavioral prompts (no game-theory vocabulary), versioned + SHA-256 hashed in the prompt registry; deterministic parser; 1 retry on parse failure, then `invalid_trial` event → participant excluded from that cell and replaced from reserved seed pool (seeds 1000+k), all recorded.
- All LLM calls flow through ActiveGraph's LLM layer (`RecordingLLMProvider` → prompt/completion/model/temperature/tokens/latency as graph events). Replay mode (`RecordedLLMProvider` + `LLMCache.from_events`, `POST /api/experiments/{id}/replay`) must verify prompt hashes, make zero live calls, and reproduce metrics bit-exactly.

## 1. Call-count estimates (deliverable 1)

LLM calls = one per subject decision. Expected supergame length under random termination = 1/(1−δ).

| Experiment | Cells | Expected calls | Hard cap |
|---|---|---|---|
| A: repeated PD, random termination, LLM vs LLM | 4 δ × 20 supergames × 2 seats × E[len]={1.11,2,4,10} → 684.4/arm × 2 arms (canonical + isomorph) | **1,369** | **1,800** |
| B: one-shot PD framing | 3 labels × 20 participants × 2 seats × 1 round | **120** | **160** |
| C: RPS, 50 rounds × 20 runs | vs pattern-tracker 1,000; vs nash-mixed 1,000; vs LLM (2 seats) 2,000 | **4,000** | **4,400** |
| **Total** | | **≈ 5,490** | **6,360** |

- Variance note (A): total δ=0.90 rounds have sd ≈ 42 rounds (≈ 85 calls both seats); cap gives >4 sd headroom. Per-supergame safety cap 120 rounds (P(hit) ≈ 3×10⁻⁶ at δ=0.90); if hit, supergame marked `truncated`, excluded, disclosed.
- Parse retries: ≤1 per decision; Track 2 measured 0 retries in 360 calls; caps include ~10% retry headroom.
- Termination coin: seeded mulberry32 stream recorded per supergame → horizon replays deterministically.
- Cost guard: batch runner enforces the per-experiment hard caps above and a global kill-switch at 6,360 calls; batches resumable (in-flight slot claiming per the v2 runner pattern).
- Token projection: input ≈ 400 avg/call → ~2.2M input tokens total. Output depends on model choice (§3): gpt-4.1-class ≈ 10–20 tokens/call (~0.1M total) vs gpt-5-mini ≈ 620/call measured in Track 2 (~3.4M total).

## 2. Locked predicate list (deliverable 2)

Adjudication mechanics: cluster-level 95% normal-approx CIs (cluster = supergame / participant / run), consistent with the v2 adjudicator. Verdicts: supported / refuted / inconclusive. All bands and tolerances below are fixed now; any change after sign-off requires a disclosed amendment event before runs begin.

### Experiment A — random-termination repeated PD (canonical arm unless stated)

Round-1 cooperation = first-round action of each supergame, both seats pooled (n = 40 decisions/δ/arm).

- **P3-A1 (shadow-of-future direction).** Round1Coop(δ=0.90) − Round1Coop(δ=0.10) > 0, 95% CI excludes 0.
  *Human anchor:* Roth & Murnighan 1978: 19.0% (δ=0.105) → 36.36% (δ=0.895), +17.4pp; Murnighan & Roth 1983: 17.83% → 29.07%, +11.2pp. (Dal Bó & Fréchette 2018, JEL 56(1), Table 2 "Percentage of Cooperation (first rounds)".)
- **P3-A2 (risk-dominance separation).** Pooled Round1Coop(δ>δ*: 0.75,0.90) − Round1Coop(δ<δ*: 0.10,0.50) > 0, CI excludes 0 (n=80 per side).
  *Human anchor:* DBF 2018 meta, first supergame: 54.22% when cooperation risk-dominant vs 35.64% when not (+18.6pp, p<.01).
- **P3-A3 (human-range membership at high δ).** Pooled Round1Coop(δ ∈ {0.75,0.90}) point estimate ∈ **[0.36, 0.63]**.
  *Band construction (disclosed):* lower = R&M 1978 δ=0.895 inexperienced rate (36.36%); upper = DBF meta supergame-15 risk-dominant cell (63.06%); central reference = DBF first-supergame RD cell (54.22%). n=80 → max CI half-width ≈ 11pp.
- **P3-A4 (isomorph invariance — contamination probe).** In the payoff-perturbed arm: (a) A2-style separation > 0 with CI excluding 0, AND (b) |high-δ Round1Coop(canonical) − high-δ Round1Coop(isomorph)| ≤ **15pp** (equivalence margin, design choice, disclosed). Failure of (b) with (a) holding suggests matrix-memorization rather than incentive reasoning.
- *Non-monotonicity disclosure:* human data itself wobbles between adjacent δ (M&R 1983 is non-monotone: 37.48% at δ=0.5 > 29.07% at δ=0.895), so no strict-monotonicity predicate is registered; the full δ-curve is reported descriptively.

### Experiment B — one-shot PD framing (n = 40 decisions/condition)

- **P3-B1 (label direction).** Coop(Community) − Coop(WallStreet) > 0, 95% CI excludes 0.
- **P3-B2 (label magnitude).** Coop(Community)/Coop(WallStreet) ≥ **1.5** (point estimate) AND B1's CI excludes 0. Edge rule (fixed now): if Coop(WS)=0 → supported iff Coop(Community) ≥ 0.30, else inconclusive.
- **P3-B3 (neutral interior).** Coop(WS) ≤ Coop(Neutral) ≤ Coop(Community) (point estimates, ties allowed).
- *Source disclosure:* Liberman, Samuels & Ross 2004 (PSPB 30(9)) is paywalled; the primary's exact percentages could not be verbatim-verified. Direction and ≈2× magnitude are anchored via secondary sources: Zhong, Loewenstein & Murnighan 2007 (JCR) — "people cooperated more in PD games that were labeled a 'Community Game' rather than a 'Wall Street Game' (Liberman, Samuels, and Ross 2004)" — and The Atlantic (2013): students "twice as likely to betray" under the Wall Street label. The 1.5× threshold is deliberately conservative (¾ of the reported ~2× gap).

### Experiment C — RPS (50 rounds × 20 runs per opponent; LLM seat decisions pooled)

- **P3-C1 (round-1 distribution).** Across all LLM-seat round-1 actions (n=80): (a) modal action = rock; (b) rock share ∈ **[0.33, 0.40]**; (c) scissors share < 1/3.
  *Human anchors:* Batzilis et al. 2019 (Games 10(2):18, ~1M Facebook games) first-throw: rock 33.99%, paper 34.82%, scissors 31.20%; Wang, Xu & Zhou 2014 (Sci. Rep. 4:5830) overall: R 0.36±0.08, P 0.33±0.07, S 0.32±0.06. Band spans both rock point estimates; scissors-deficit is the robust cross-study signature.
- **P3-C2 (win-stay/lose-shift signature).** Pooled LLM decisions with a previous round: P(stay|win) 95% CI entirely above **1/3** AND P(shift|lose) CI entirely above **2/3** (independence nulls). Both present → supported; either CI entirely below its null → refuted; otherwise inconclusive.
  *Human anchors:* WXZ 2014 document win-stay/lose-shift conditional response in humans (their Fig. 2; "win-stay lose-shift (also called Pavlov)" framing); Zhang, Moisan & Gonzalez 2021 (Games 12:52) caveat: only ~1/3 of participants were outcome-dependent — absence in the LLM is a publishable, human-plausible outcome.
- **P3-C3 (tracker exploitability).** TrackerPayoffPerRound(vs LLM) − TrackerPayoffPerRound(vs nash-mixed baseline, new zero-LLM batch) > 0, CI excludes 0 (run-level clusters, n=20 vs 20).
  *Anchor:* against a true mixed-strategy Nash player the tracker's edge is 0 in expectation; any CI-positive edge over the LLM demonstrates exploitable sequential dependence (existing `marginalExploitability`/`conditionalExploitability` metrics reported descriptively alongside).

### Procedural locks (registered with the predicates)

1. Predicates inserted with adjudicator timestamps **before** the first `*:t3` experiment row; `postRegistered` enforcement stays on.
2. Prompt registry: each prompt template versioned + SHA-256 hashed before runs; hash stored on every experiment; replay verifies hash equality.
3. Invalid-trial rule and replacement-seed pool as in §0; invalid rates reported per cell.
4. Exploratory analyses (lag-1 transition heatmaps, δ-curve shape, self-play cycling) are labeled exploratory and never adjudicated.
5. Existing v2/Track-2 rows are immutable; Phase 3 is additive (`:t3` batch labels only).

## 3. Open decision required at sign-off — subject model & temperature

Spec requires temperature 0.7 (configurable, stored). Constraint discovered in Track 2: **gpt-5-family models pin temperature = 1** (parameter not specifiable) and emit hidden reasoning tokens (measured 620 completion tokens/call average in Track 2).

| Option | Temp 0.7 honored? | Output tokens/call | Notes |
|---|---|---|---|
| **gpt-4.1 (recommended)** | Yes | ~10–20 | True sampling control; no reasoning-token inflation; different model family than Track 2 (which is fine — Phase 3 is a new subject pool, and model is stored per experiment) |
| gpt-5-mini | No (pinned 1.0) | ~620 measured | Continuity with Track 2 subject; violates the spec's temperature requirement; ~30× output tokens |
| gpt-4o | Yes | ~10–20 | Alternative non-reasoning subject; slightly costlier family than 4.1 |

All options run through the existing Replit AI Integrations proxy (no new keys; billed to credits).

---

## Amendments (disclosed — added July 24, 2026, after study completion; original text above is unmodified)

1. **Procedural lock #1 deviation.** "The adjudicator enforces timestamp ordering… (never
   adjudicated)" was not implemented in the adjudicator at study time; the ordering was
   enforced by the study runner only (claims step refuses to register if any `:t3` row
   exists; runs step refuses to run without all 10 claims). Post-study, adjudicator-level
   enforcement was added as a **disclosed `postRegistered` flag stamped on every
   adjudication** (claim registration time vs earliest cited evidence row), not as
   refusal-to-adjudicate — refusal would suppress the v1 corpus whose disclosed post-hoc
   status is intentional. Machine check result: all 10 P3 claims `postRegistered=false`;
   re-adjudication flipped no verdict. Additionally, predicates are now immutable after
   first adjudication (HTTP 409).
2. **Failed-run spend accounting hardened.** Mid-run engine failures now persist partial
   provider-call counts on the failed row. Not exercised: 0/280 failures in this study.

---

## Extension X1 — paraphrase robustness (registered July 24, 2026: AFTER main-study results, BEFORE any extension data)

**Status disclosure.** This extension is registered with full knowledge of the main-study
results (round-1 cooperation exactly 0 in all 160 repeated-PD supergames). It is therefore
*not* blind to the main effect; what is pre-committed here, before any extension row
exists, is the **direction, thresholds, design, and budget** of the robustness test.
Motivation: external review of `docs/phase3-report.md` — a corner solution measured under
a single prompt wording invites the "one paraphrase away" objection; robustness (or
brittleness) under semantically equivalent rewordings is decision-relevant either way.

### Design

- **Templates.** Two paraphrases of `pd-repeated-v1`, appended to the prompt registry as
  `pd-repeated-v2a` (reordered structure: continuation rule first; "pick"/"another person"
  register; conditional-sentence payoff lines) and `pd-repeated-v2b` (compact outcome
  notation `J+J / J+F / F+F`; "co-player"; probability phrased "{δ} in 100"). Invariants
  preserved in both: neutral labels J and F, no game-theory vocabulary, full payoff
  disclosure for both players, continuation probability disclosed, realized horizon
  hidden, exact-letter reply contract, identical parser and retry rule.
- **Registry policy (append-only).** phase3-v1 prompt specs are byte-identical in
  phase3-v2; only the two new templates and the version/notes fields differ.
  - phase3-v1 sha256: `73e7a6cac07c83b49985ab3e36edd9d83a4916a41eade624c807ae0307bdc262`
  - phase3-v2 sha256: `808f205a192909e8c2ac1c1ec6210c650017c297978afeb0b899873ea9ae1fc2`
- **Cells.** δ = 0.90 only (canonical payoffs), self-play, 2 variants × seeds 1–20,
  batch labels `prisoners-dilemma:llm41-para-{v2a|v2b}:d90:t3x`. Subject, temperature,
  maxTokens, invalid-trial and replacement rules identical to Experiment A.
- **Horizon matching.** Same seeds and same `mulberry32(seed ^ 0x54524D)` horizon draw as
  the canonical δ=0.90 arm → identical realized horizons per seed; differences are
  attributable to prompt surface alone.
- **Budget.** Expected ≈ 800 calls (2 × the canonical d90 arm's 404). Family-X cap
  **1,600**; global kill-switch amended 6,360 → **7,960** (the sealed main-study families
  keep their original caps; the runner refuses new original-arm rows outright now that
  the registry sha has moved).

### Registered claim (inserted via the `xclaims` step before any `:t3x` row)

- **P3-X1 (paraphrase robustness).** Mean round-1 cooperation at δ=0.90 is **≤ 0.05 under
  each paraphrase separately** (`round1CoopFocus`, n=20 supergames per variant; standard
  CI semantics, sd=0 → exact comparison, as in the main study). Both items must hold.
  Refutation under any paraphrase is reported as prompt-surface brittleness — itself a
  finding that would overturn the report's "incentive-insensitive" reading of A1–A3 and
  be disclosed as such.

### Pipeline amendments bundled with this extension (disclosed)

3. **Replay registry check made append-tolerant.** Replay previously failed any run whose
   stored whole-file registry sha ≠ current file sha, which would have rendered all 280
   sealed runs "unverifiable" the moment any later arm added a template. The whole-file
   comparison is now reported as an informational `registryFileDrift` field; the
   **authoritative check is unchanged and per-prompt**: every prompt is re-rendered from
   the current registry and must hash-match the recorded call cache byte-exactly, so any
   edit to a template a run actually used still fails its replay. Existing prompt specs
   remain immutable by policy.
4. **Renderer generalization.** The δ-interpolation branch now matches the
   `pd-repeated-*` prefix instead of the literal id `pd-repeated-v1` (no behavior change
   for v1; required for v2a/v2b).
5. **Per-arm sha pinning in the runner.** Each pipeline step asserts the registry sha
   registered for *its* arm; verification requires each stored run's recorded sha to
   equal its arm's pinned sha.
