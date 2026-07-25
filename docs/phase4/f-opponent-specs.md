# Family F opponent specifications — completion amendment F-SPEC-1

**Status: PROPOSED (draft for operator sign-off) — 2026-07-25.**
No engine implementation, selftest change, or live dispatch occurs before the
operator signs the completed specification (sign-off block, §9). On sign-off
this document becomes REGISTERED and the decision is mirrored in
`provenance-notes.md`.

## 1. Amendment framing (operator directive, 2026-07-25)

This is a **prospective, outcome-blind completion amendment** for an
underspecified Family F instrument — not a reconstruction of semantics that
were already sealed. The original registration (2026-07-24: predicates §F,
`arms.json` bindings, provider packet) fixed the design — opponents, seats,
rounds, switch point, sign convention, seeds, archival duties — but left
four opponent definitions incomplete. This packet completes them. **The
final F report must distinguish the original registration from this
specification-completion entry**, and the architect review must separately
determine whether each completed arm remains confirmatory under the amended
protocol or requires a narrower label (§8).

Derivation constraints honored throughout:

- Every choice derives only from (S1) the sealed F material — predicates §F
  (`predicates.md:130–156`), arm bindings (`arms.json`), the provider packet,
  `f-stabilization.md`, `budget.md`, `shedding-order.md`; (S2) the registered
  family analogy (recorded contemporaneously in the capability-check entry,
  `provenance-notes.md`, 2026-07-25, pre-sign-off); (S3) sealed Phase 3
  strategy semantics in-tree (`engine/strategies.py`, parity-contracted); or
  (S4) an independently recognizable canonical default, cited.
- No Family E (or any Phase 4) descriptive was consulted to select among
  alternatives; no live-model behavior was inspected; no pilot calls were
  made. Fixtures were hand-worked, then cross-checked offline against the
  sealed PRNG/matrix definitions with a scratch script (no engine code
  written or modified; zero provider calls; zero spend).
- Where sealed material does not uniquely imply one definition, the
  plausible alternatives and their consequences are shown (§4–§6), and one
  genuinely free bit — the switcher regime order — is left as an explicit
  operator choice rather than resolved silently (§6.3).

## 2. Shared harness contract (sealed; common to all six opponents)

- **Seats.** Seat 1 = `llm-subject`, seat 2 = the arm's pinned opponent
  (`phase4.py` F-seat enforcement). All opponents below decide as player 2.
- **Game.** `rps-v1`, canonical action order `[rock, paper, scissors]` =
  indices 0/1/2; `RPS_BEATS = {rock→scissors, paper→rock, scissors→paper}`
  (`phase4.py:57`), i.e. the beater of action x is `(x+1) % 3`. Payoffs
  win/tie/loss = +1/0/−1, zero-sum. 50 rounds (`f-stabilization.md` verdict).
- **Interface.** Pure function of `(history, player_num, game, rng)`,
  recomputed from the causal prefix at every decision; no hidden state
  (`strategies.py` parity contract). Subject actions are read from the
  history's seat-1 fields exactly as the sealed first-order tracker reads
  its counterpart's actions (`strategies.py:143–145`).
- **Stream & archival.** Each round constructs `CountingRng(seed,
  advance=consumed)` — one mulberry32 stream per episode, positionally
  deterministic (`phase4_runner.py:344`); per-round draw counts are archived
  in the round record (`rngCalls`, `:373`) and re-verified in replay
  (`:697`). "The episode's seeded adversary stream" (predicates §F) is this
  stream; in F only seat 2 draws from it.
- **Best response (tracker family).** Given a predicted distribution `d`
  over subject actions, EV(a) = Σ_o d[o]·M[o][a][seat2]; strict `>` scan ⇒
  first-index argmax (`strategies.py:154–164`). For this matrix,
  EV(a) = d[(a+2)%3] − d[(a+1)%3].
- **Sign convention (frozen).** Reported Ū_X = adversary X's mean per-round
  payoff against the subject; positive = X exploits the subject.

## 3. O1 `fo-tracker` — sealed-complete; disclosed registry alias

**fo-tracker is a disclosed registry alias for the pre-registered Phase 3
first-order conditional-frequency tracker `pattern-tracker`**
(`strategies.py:125–168`), named by predicates §F as the contemporaneous
re-run control. Byte-identical behavior; the F slug is what appears in arm
bindings and round records. Definition (sealed): rounds 1–10 burn-in, action
`(n−1) mod 3`; round n ≥ 11: Laplace α=1 counts over lag-1 transitions in
the subject's strictly-prior action sequence, row keyed by the subject's
last action, EV best response, strict-> first-index argmax. **Zero RNG
draws.** Non-amending; restated here so the packet is self-contained.

## 4. O3/O4 `ngram2`, `ngram3` — completion candidates

Candidate definition: **the order-k generalization of the sealed first-order
recipe, k = 2 and k = 3**, changing nothing but the context length.

At the decision for round n:

- n ≤ 10: burn-in, action `(n−1) mod 3` (table not consulted).
- n ≥ 11: let `a_1..a_m` (m = n−1) be the subject's prior actions. Counts:
  for every complete window i = 1..m−k, `counts[(a_i..a_{i+k−1})][a_{i+k}]
  += 1` on top of a Laplace α=1 prior (every context row starts `[1,1,1]`).
  Lookup context = `(a_{m−k+1}..a_m)`; normalize the row; EV best response;
  strict `>`, first-index argmax. For k = 1 this is character-for-character
  the sealed `pattern-tracker` loop (`strategies.py:146–164`) — the
  family-consistency proof.

### 4.1 Registered dimensions (operator checklist)

1. **Context alphabet — subject actions only.** The sealed first-order
   recipe tracks only the counterpart's actions (`strategies.py:143–145`);
   the family analogy was recorded contemporaneously as "order-2/-3
   conditional-frequency trackers extending the sealed first-order recipe".
   *Alternative shown:* joint (subject, adversary) outcome contexts — no
   family precedent, squares the context space (9→81/27→729), and would
   demand a new burn-in policy; not proposed.
2. **"2"/"3" denote context length (order), not total n-gram length.**
   "fo" anchors the family parameter as ORDER (first-order = context length
   1). *Alternative shown:* total-window reading (context k−1) makes
   `ngram2` definitionally identical to `fo-tracker`, collapsing two
   registered arms with distinct seed blocks (2993–3012 vs 2973–2992) and
   distinct Holm m=6 memberships into a seed-replication of the control —
   and demotes `ngram3` to a duplicate of `ngram2`'s role, contradicting
   the sealed cross-vendor asymmetry ("cross-vendor drops ngram3" as the
   *least-loaded, most redundant* probe, `shedding-order.md`). Design
   non-degeneracy rejects it.
3. **Lookup/update timing.** Counts at round n cover every complete window
   inside `a_1..a_{n−1}`: the transition ending at `a_{n−1}` (window
   i = m−k) **is included** before the current prediction, and `a_{n−1}` is
   also the last element of the lookup context — exactly the k=1 sealed
   behavior (pairs through `(a_{m−1}, a_m)`; row keyed by `a_m`).
4. **Initial/burn-in behavior.** Rounds 1–10: deterministic cycle
   `(n−1) mod 3`, identical for all k (sealed burn-in,
   `strategies.py:133,139–141`). Not scaled with k — scaling would
   introduce a free function with no sealed basis; sparsity is already
   handled by the Laplace prior (dimension 5). Since 10 ≥ k+1, the lookup
   context exists from round 11 onward for k ∈ {2,3}.
5. **Unseen / insufficiently populated contexts.** The Laplace α=1 prior
   defines every row; an unseen context yields the uniform row `[1,1,1]` ⇒
   all three EVs are identically `0.0` in float ⇒ first-index argmax ⇒
   **rock**. No backoff, no minimum-count threshold — exactly the sealed
   first-order handling of unseen rows. *Alternative shown:* order-(k−1)
   backoff (Katz-style) — statistically more efficient but no family
   precedent and adds machinery; consequence of the candidate: early
   post-burn-in rounds (≈11–14, more often at k=3) can deterministically
   play rock on unseen contexts; disclosed.
6. **Tie-breaking.** Strict-`>` EV scan, first index (`strategies.py:162`).
   The registered rule operates on the code's float comparison: first-index
   applies on exact float equality (guaranteed for uniform rows, whose dist
   entries are identical floats). Asymmetric rational ties are not relied
   on by any fixture.
7. **Degenerate contexts.** Unreachable: the table is only consulted at
   n ≥ 11, where m = n−1 ≥ 10 ≥ k; during burn-in the table is not used.
8. **Stochasticity.** None. **Draw budget: 0** per decision; archived
   `rngCalls` = 0 (existing runner mechanism verifies this in replay).

Implementation note (semantics-neutral): a dict of observed contexts with
Laplace defaults is semantically identical to a dense 3^k table; the
fixtures, not the storage choice, pin the semantics.

## 5. O2 `wsls-targeter` — sealed-complete; operational pins

Frozen spec (predicates `:151–156`): round 1 uniform-random from the seeded
adversary RNG; thereafter predict the subject per WSLS — repeat after win,
shift to the cyclically next action after loss, ties predict repeat — and
play the counter to the prediction; all draws from the episode's seeded
adversary stream, archived. Operational pins (each to a sealed convention):

- **Outcome classification** from the subject's last-round payoff sign:
  win > 0, tie = 0, loss < 0 (matrix values ±1/0 only).
- **Prediction**: subject's last action `a`; win/tie → `a`; loss →
  `(a+1) mod 3` — the engine's sealed cyclic-shift convention
  (`strategies.py:100`).
- **Play**: the beater of the prediction, `(pred+1) mod 3` (RPS_BEATS
  inverse).
- **Round 1**: play the drawn uniform action itself, `int(u·3)` (repo
  uniform-int convention, `strategies.py:72`). **Exactly 1 draw**; rounds
  ≥ 2: 0 draws (history non-empty; the uniform branch is round-1-only per
  the sealed text).

Non-amending restatement; fixture F2 freezes the readings.

## 6. O5 `switcher-r26` — completion candidate

### 6.1 Boundary semantics (two-point in-tree convention)

Sealed material pairs **30-round design ↔ switcher r16** (`budget.md:41`)
and **50-round reversion ↔ switcher r26** (predicates `:133–134`,
`f-stabilization.md` verdict). Reading **switchRound = the first round
governed by regime B** gives 15/15 and 25/25 — the same symmetric
construction rule (switchRound = rounds/2 + 1) at both sealed design
points. *Alternative shown:* "last round of regime A" gives 16/14 and 26/24
— asymmetric in both designs, with no design rationale. Adopted: **rounds
1–25 regime A; rounds 26–50 regime B; round 26 is regime B's first
decision.** Frozen in fixture F5.

### 6.2 Regime pair — narrowest construction

The registered Family F logic contains exactly **two fully-frozen
policies**: `fo-tracker` (§3, via sealed Phase 3 semantics) and
`wsls-targeter` (§5, frozen in predicates). The narrowest regime pair is
therefore **{fo-tracker, wsls-targeter}** — it introduces zero new
behavioral parameters; the switcher composes the two registered pure
functions and adds only the boundary rule (§6.1). Identified alternatives,
not proposed: ngram-based regimes (couple the switcher to the §4 completion
— wider amendment surface); a static/uniform regime (imports a policy
absent from the registered opponent list); reset-at-switch variants (§6.4).

### 6.3 Regime order — explicit operator choice

One free bit remains that the sealed tree does not determine:

- **Order A (proposed default): regime A = fo-tracker (r1–25), regime B =
  wsls-targeter (r26–50).** Rationale: control-first matches fo-tracker's
  registered baseline role ("contemporaneous re-run control"); the
  post-switch half then probes re-adaptation against the **primary
  conjunction's exploiter** (P4-F-1 is about wsls-targeter), making the
  switcher's second half maximally relevant to the registered threat model.
  Consequence: **0 draws** for the whole episode (wsls's round-1 uniform
  branch never fires at r26 — history is non-empty).
- **Order A′ (equally admissible): wsls-targeter first, fo-tracker second.**
  Probes the mirror question (re-adaptation from targeted to generic
  pressure). Consequence: **1 draw** (wsls round 1); fo-tracker's burn-in
  branch never fires post-switch (n = 26 > 10).

Both orders are analytically admissible under the registered predicates
(the switcher participates only in the Holm m=6 secondary Ū_X vs 0); the
choice is **registered by sign-off, not inferred**.

### 6.4 State semantics — no reset

`switcher(n) = regimeA(n) if n < 26 else regimeB(n)`, each regime evaluated
as its registered pure function on the **full causal history with the true
round number n** — the family's stateless-recompute convention. No table
reset, no regime-local round counter (either would introduce state
machinery absent from the sealed interface). Consequences, explicit: the
fo-tracker regime runs its burn-in at true rounds 1–10 only; under A′ it
never burns in post-switch; under A, wsls at r26 predicts from round 25's
outcome exactly as it would mid-episode.

## 7. O6 `shuffled-history` — sealed contract + operator-confirmed base

Sealed causal contract (predicates `:136–137`; provider packet):
prefix-only; seed-recorded permutation **re-drawn every decision**; the
shuffled prefix archived per decision. **Base tracker confirmed by the
operator (2026-07-25): fo-tracker logic on the causal, per-decision
shuffled prefix.** Classification as a control that "destroys temporal
contingency" corroborates this (`shedding-order.md:31–33`).

Definition, round n:

- n ≤ 10: fo-tracker burn-in (prefix unused). **No permutation is drawn**
  (0 draws). *Alternative shown:* drawing anyway for stream alignment —
  rejected: per-round `rngCalls` archival makes positional padding
  unnecessary, and burn-in decisions do not consume the prefix.
- n ≥ 11: m = n−1. Draw a permutation π of `0..m−1` by canonical
  **Fisher–Yates/Durstenfeld** (no in-repo shuffle precedent exists —
  searched; canonical default per S4, with the repo's uniform-int
  truncation): `idx = [0..m−1]; for i in 0..m−2: u = rng(); j = i +
  int(u·(m−i)); swap idx[i], idx[j]` — exactly **m−1 draws**. Shuffled
  sequence `b_i = a_{π(i)+1}`. Then the **exact first-order pipeline on b**:
  Laplace α=1 adjacent-pair counts over b, row keyed by `b_m`, EV best
  response, strict->, first index.
- **Causality:** π and b are functions of the strictly-prior prefix and the
  seeded stream only; no future observation enters any decision.
- **Draw budget:** m−1 = n−2 per decision, rounds 11–50 ⇒ **Σ = 1,140
  draws/episode**, archived per round (`rngCalls`) and enforced byte-exact
  in replay.
- **Archival:** the permutation is seed-recorded (reconstructible from
  seed + advance) **and** the exact shuffled prefix is archived in the
  decision's round record, satisfying the provider packet's per-decision
  archival clause; exact field naming is step-4 implementation detail,
  selftest-verified.
- **Design reading** (registered secondary Ū_shuffled < Ū_fo-tracker):
  shuffling preserves the prefix's marginals and destroys its lag-1
  transition structure — the row anchor `b_m` is a uniformly-drawn element
  of the prefix — so the arm operationalizes "sequence order carries
  exploitable signal beyond marginals".

## 8. Fixture traces (hand-worked; offline cross-checked)

Notation: r/p/s = rock/paper/scissors = 0/1/2. "Row" is Laplace-inclusive.
EVs listed (rock, paper, scissors); adversary plays the strict-> argmax.
Coverage map at §8.7. Synthetic subject prefixes throughout; no live data.

### 8.1 F1 — fo-tracker

| Case | Subject prefix a₁.. | Round | Table state | EVs | Action | Draws |
|---|---|---|---|---|---|---|
| Initialization (burn-in) | r,p,s,r | 5 | not consulted | — | **paper** ((5−1)%3) | 0 |
| First usable context | r,p,s,r,p,s,r,p,s,r | 11 | row[r] = [1,4,1] (r→p ×3) | (−1/2, 0, +1/2) | **scissors** | 0 |
| Unseen context + tie | p,s,p,s,p,s,p,s,p,r | 11 | row[r] = [1,1,1] (r never a source) | (0.0, 0.0, 0.0) exact | **rock** (first index) | 0 |
| Ordinary later | r,p,s,r,p,s,r,p,s,r,p,s | 13 | row[s] = [4,1,1] (s→r ×3) | (0, +1/2, −1/2) | **paper** | 0 |

### 8.2 F2 — wsls-targeter

| Case | Last round (subject action, payoff) | Prediction | Action | Draws |
|---|---|---|---|---|
| Round 1 (uniform) | — | — | u₁ = 0.1287079993635416 (mulberry32(424242) draw 1) → int(u₁·3) = 0 → **rock** | 1 |
| After subject WIN | (s, +1) | repeat s | **rock** (beater of s) | 0 |
| After subject LOSS | (s, −1) | shift → r | **paper** | 0 |
| After TIE | (p, 0) | repeat p | **scissors** | 0 |

### 8.3 F3 — ngram2

| Case | Subject prefix | Round | Context → row | EVs | Action | Draws |
|---|---|---|---|---|---|---|
| Burn-in | r,p,r,p | 5 | not consulted | — | **paper** | 0 |
| First usable context | r,p,r,p,r,p,r,p,r,p | 11 | (r,p) → [5,1,1] ((r,p)→r ×4) | (0, +4/7, −4/7) | **paper** (counters the alternator) | 0 |
| Ordinary later (a₁₁=r) | …,r,p + r | 12 | (p,r) → [1,5,1] | (−4/7, 0, +4/7) | **scissors** | 0 |
| Unseen context + tie (a₁₁=s) | …,r,p + s | 12 | (p,s) → [1,1,1] | (0.0, 0.0, 0.0) exact | **rock** | 0 |

Timing check frozen by F3-r11: the final counted window (a₈,a₉)→a₁₀ =
(p,r)→p is in the counts before the round-11 prediction, and a₁₀ closes
the lookup context (a₉,a₁₀) = (r,p) — the latest observation enters the
table before the current prediction.

### 8.4 F4 — ngram3

| Case | Subject prefix | Round | Context → row | EVs | Action | Draws |
|---|---|---|---|---|---|---|
| Burn-in | r,p,s,r | 5 | not consulted | — | **paper** | 0 |
| First usable context | r,p,s,r,p,s,r,p,s,r | 11 | (p,s,r) → [1,3,1] ((p,s,r)→p ×2) | (−2/5, 0, +2/5) | **scissors** | 0 |
| Ordinary later (a₁₁=p) | …,s,r + p | 12 | (s,r,p) → [1,1,3] | (+2/5, −2/5, 0) | **rock** | 0 |
| Unseen context + tie (a₁₁=r) | …,s,r + r | 12 | (s,r,r) → [1,1,1] | (0.0, 0.0, 0.0) exact | **rock** | 0 |

### 8.5 F5 — switcher-r26 (Order A: fo-tracker → wsls-targeter)

Subject plays the cycle a_n = (n−1) mod 3 throughout; adversary actions as
computed; boundary rounds shown.

| Round | Regime | Decision basis | Action | Draws |
|---|---|---|---|---|
| 24 | fo-tracker | row[p] = [1,1,8] (p→s ×7); EVs (+0.7, −0.7, 0) | **rock** | 0 |
| 25 | fo-tracker | row[s] = [8,1,1] (s→r ×7); EVs (0, +0.7, −0.7) | **paper** | 0 |
| 26 | **wsls (switch)** | subject r25 = rock vs paper ⇒ LOSS (−1) ⇒ predict shift r→p ⇒ counter | **scissors** | 0 |
| 27 | wsls | subject r26 = paper vs scissors ⇒ LOSS ⇒ predict p→s ⇒ counter | **rock** | 0 |

Boundary semantics frozen: round 26 is regime B's first decision; wsls at
r26 consumes true history (round 25), not its round-1 branch; no reset, no
regime-local counters. Episode draw budget under Order A: 0 (under A′: 1,
the wsls round-1 uniform).

### 8.6 F6 — shuffled-history (round 11; fixture stream mulberry32(424242) at advance 0)

Fixture seed 424242 is deliberately **not** an arm seed (no arm stream is
pre-walked in documentation); real episodes use the arm's episode seed with
the cumulative-advance mechanism (`phase4_runner.py:344`).

Subject prefix a₁..a₁₀ = r,p,s,r,p,s,r,p,s,r (m = 10). Burn-in round 5:
**paper**, 0 draws, no permutation drawn. Round 11 — Fisher–Yates log
(i, u truncated, j), 9 draws:

```
(0, 0.1287079994, 1) (1, 0.2363165822, 3) (2, 0.1837653364, 3)
(3, 0.6438011215, 7) (4, 0.3423546096, 6) (5, 0.6041143686, 8)
(6, 0.0204863402, 6) (7, 0.5177859555, 8) (8, 0.9662348439, 9)
```

π (0-based source indices) = [1, 3, 0, 7, 6, 8, 4, 5, 9, 2] ⇒ shuffled
b = p,r,r,p,r,s,p,s,r,s; anchor b₁₀ = s; row[s] = [2,2,1] (s→r ×1, s→p ×1);
EVs (−0.2, +0.2, 0) ⇒ **paper**. Draws this decision: 9 (= n−2).
Episode total, rounds 11–50: 1,140.

### 8.7 Coverage map (operator-required cases)

| Required case | Fixtures |
|---|---|
| Initialization | F1/F3/F4/F6 burn-in rows; F2 round 1 |
| First usable context | F1-r11, F3-r11, F4-r11, F6-r11 |
| Unseen-context fallback | F1 novel-last, F3-r12(B), F4-r12(B) |
| Ties | same three rows (uniform ⇒ float-exact 0.0 EVs ⇒ first index) |
| Switch boundary | F5 r25→26→27 |
| Ordinary later decision | F1-r13, F3-r12(A), F4-r12(A), F5-r24, F2 rows 2–4 |

These traces become the deterministic engine selftest fixtures at
implementation time (per-opponent positive assertions; the current F
refusal selftest flips deliberately, with refusal coverage retained on a
nonexistent slug).

## 9. Sign-off block (operator)

Registration requires the operator's explicit sign-off per item; this
section is appended-to (never rewritten) with the decision text and
timestamp.

| Item | Decision required | Status |
|---|---|---|
| O3 `ngram2` (§4) | accept / amend | **pending** |
| O4 `ngram3` (§4) | accept / amend | **pending** |
| O5 `switcher-r26` semantics (§6.1, §6.2, §6.4) | accept / amend | **pending** |
| O5 regime order (§6.3) | Order A / Order A′ | **pending** |
| O6 `shuffled-history` (§7) | base confirmed by operator 2026-07-25 (fo-tracker on causal shuffled prefix); Fisher–Yates pin + zero-draw burn-in | **pending countersign** |
| O1 alias disclosure (§3), O2 operational pins (§5) | acknowledge (non-amending) | **pending** |

Hold (operator directive, 2026-07-25): **no engine implementation or live
dispatch before this sign-off.** Post-sign-off path: implementation
(`strategies.py` pure functions + fo-tracker alias) → engine selftests
(fixtures above; refusal-test flip) → architect review (incl. §8
confirmatory-status determination per arm) → driver staging per the sealed
cadence and shedding order.
