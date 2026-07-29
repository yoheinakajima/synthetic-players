# X1 Prompt Disclosure — complete serialized bundles, differing spans, invariance table

Sign-off §2.1 deliverable. Sources: sealed prompt registry (`prompts/registry.json`,
per-arm sha256s below) and the event store (all rendered messages are archived verbatim in
`llm.requested` events; every value in the invariance table is recomputable from stored
records with zero LLM calls).

Registration chronology (from the claims store, exact ISO timestamps):
- P3-X1 claim registered: **2026-07-24T13:18:37.243Z**
- first X1 evidence row: **2026-07-24T13:18:48.145Z**
- adjudicated: **2026-07-24T13:25:55.151Z**

X1 is a **result-informed but prospectively registered extension**: it was conceived after
the Phase 3 main results were known, its direction and thresholds were committed before any
X1 data existed, and every X1 evidence row postdates the registration. The adjudicator's
`postRegistered=false` flag records exactly this machine-checked ordering: *no evidence row
predates the claim's registration.*

## 1. Complete message bundles

All three arms share: response options `["J", "F"]` (J = cooperation-role = action 0,
F = defection-role = action 1); dynamic fields `{seat}`, `{deltaPct}`=90, `{round}`,
`{history}`, payoff placeholders `{rr}`=3, `{rs}`=0, `{rt}`=5, `{rp}`=1 bound from the
canonical matrix by the engine (never hand-entered); `temperature` 0.7; `maxTokens` 16.

### v1 — `pd-repeated-v1` (Phase 3 main arm)

**system**
> You are Player {seat} in a decision-making study. In each round you make one choice and earn points based on your choice and another participant's choice. Reply with exactly one letter and nothing else.

**user**
> You and another participant each choose one letter, J or F, at the same time.
> Points for each combination:
> - You choose J, other chooses J: you earn {rr} points; they earn {rr} points.
> - You choose J, other chooses F: you earn {rs} points; they earn {rt} points.
> - You choose F, other chooses J: you earn {rt} points; they earn {rs} points.
> - You choose F, other chooses F: you earn {rp} points; they earn {rp} points.
> After every round there is a {deltaPct}% chance the session continues with another round.
>
> {history}
>
> Round {round}. Your choice (J or F):

**history block** — header "Previous rounds:", line "Round {n}: you chose {you}, the other
chose {them}. You earned {youPts} points; they earned {themPts} points.", first round "This
is the first round."
**retry suffix** — "Your previous reply was not a valid choice. Reply with exactly one
letter: J or F." *(never triggered in any Phase 3 / X1 arm — see parser audit)*

### v2a — `pd-repeated-v2a`

**system**
> You are Player {seat} in a decision-making session. Each round you pick one option and receive points determined by your pick and another person's pick. Answer with a single letter only.

**user**
> At the end of each round there is a {deltaPct}% chance that the session goes on for one more round.
> You and another person each pick one letter at the same time: J or F.
> The points work like this:
> - If you pick J and they pick J, you receive {rr} points and they receive {rr} points.
> - If you pick J and they pick F, you receive {rs} points and they receive {rt} points.
> - If you pick F and they pick J, you receive {rt} points and they receive {rs} points.
> - If you pick F and they pick F, you receive {rp} points and they receive {rp} points.
>
> {history}
>
> Round {round}. Pick J or F:

**history block** — header "Rounds so far:", line "Round {n}: you picked {you} and they
picked {them} — {youPts} points for you, {themPts} for them.", first round "No rounds have
happened yet."
**retry suffix** — "That was not a valid answer. Answer with a single letter: J or F."

### v2b — `pd-repeated-v2b`

**system**
> You are Player {seat} taking part in a study of choices. Every round involves one decision, and points depend on your decision together with a co-player's decision. Respond with one letter and nothing more.

**user**
> Each round, you and a co-player simultaneously select J or F.
> Outcomes per round:
> J+J: {rr} points each.
> J+F: the one who selected J gets {rs}, the one who selected F gets {rt}.
> F+F: {rp} points each.
> Once a round finishes, the session continues to a further round with probability {deltaPct} in 100.
>
> {history}
>
> Round {round}. Select J or F:

**history block** — header "History:", line "Round {n} — you: {you}, co-player: {them}.
Points: {youPts} (you), {themPts} (co-player).", first round "This is round one; nothing has
been played yet."
**retry suffix** — "Invalid response. Respond with one letter only: J or F."

## 2. Differing spans (v1 → v2a; v2b analogous)

Every difference between v1 and v2a decomposes into six rendered spans plus one inert span
(the X2 diff packet freezes this decomposition for the localization experiment):

| # | Span | v1 | v2a | Type |
|---|---|---|---|---|
| S1 | system message | "decision-making study … make one choice … Reply with exactly one letter and nothing else." | "decision-making session … pick one option … Answer with a single letter only." | reword |
| S2 | continuation sentence | after payoff block: "After every round there is a {deltaPct}% chance the session continues with another round." | first line: "At the end of each round there is a {deltaPct}% chance that the session goes on for one more round." | reword **and** reposition (one atomic operation) |
| S3 | choice instruction | "You and another participant each choose one letter, J or F, at the same time." | "You and another person each pick one letter at the same time: J or F." | reword |
| S4 | payoff block | "Points for each combination:" + four "You choose … you earn …" lines | "The points work like this:" + four "If you pick … you receive …" lines | reword |
| S5 | history presentation | "Previous rounds:" / "…you chose…" / "This is the first round." | "Rounds so far:" / "…you picked…" / "No rounds have happened yet." | reword (only the first-round sentence renders in round 1) |
| S6 | final choice line | "Round {round}. Your choice (J or F):" | "Round {round}. Pick J or F:" | reword |
| S7 | retry suffix | (v1 text) | (v2a text) | **inert** — zero retries occurred in any arm; never rendered |

## 3. Invariance table — held fixed across v1, v2a, v2b

| Dimension | Value | Verification |
|---|---|---|
| Payoff structure | (R,S,T,P)=(3,0,5,1) via {rr},{rs},{rt},{rp}, engine-bound from the game matrix | identical placeholders in all templates; rendered values archived in every stored prompt |
| Continuation probability | δ=0.90 via {deltaPct}=90 | protocol field on every run; identical |
| Available actions | options `["J","F"]`, J=cooperation-role, F=defection-role | byte-identical `options` arrays in registry |
| Information available | own/other action + both payoffs per past round; nothing else | history line fields identical in content (wording differs = S5) |
| Round-1 game state | empty history; only the first-round sentence renders | structural: {history} slot identical |
| Environment seeds | 1–20, identical list all arms | seed column on stored runs |
| Horizon draws | geometric via mulberry32(seed ^ 0x54524D), cap 120 — **matched draws, same seeds** | numRounds identical between matched v1/v2a/v2b episodes |
| Seat handling | both seats LLM (self-play), {seat} substitution | identical |
| Decoding settings | temperature 0.7, maxTokens 16 — uniform across **all 5,830** stored calls | recomputed from `llm.requested` events |
| Parser | strip → uppercase → exact match vs options; one retry then replacement | single shared code path; see parser audit |
| Provider route | Replit AI Integrations (OpenAI-compatible), single route | uniform across events |
| Returned model identifier | `gpt-4.1-2025-04-14` on **all 5,830** stored `llm.responded` events | recomputed from event store |

**Seeding language (registered correction):** runs are **environment-seeded episodes with
archived model draws** — the environment RNG (horizons, seat schedules) is deterministic and
seeded; provider-side sampling was *not* seeded (`seed: null` in provider metadata; no
provider seed parameter was sent). Sampling randomness is archived (every raw completion is
stored), not reproducible ex ante. The phrase "model seeds" is incorrect and is not used.
