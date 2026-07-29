# Main/supplement cut map — R2 item 8

> **STATUS: DOCUMENTATION — R2, 2026-07-29. Editorial architecture for
> the paper draft; no data, zero subject calls.**

## Architecture

Three load-bearing layers; every candidate section is assigned to
exactly one.

1. **Claim** — *coarse marginal checks pass while incentive sensitivity
   stays weak.* Persona pools clear level/variance bands against
   published human values (nonmatched comparator) while the pool
   δ-response is a fraction of the published human δ-gap and 9–10 of 16
   personas are pure-corner in every cell.
2. **Mechanism** — *corner-mixture composition + control-channel
   interactions.* The variance that passes the bands is a mixture of
   near-deterministic corners split by leaning; the levers that move
   behavior are lexical (paraphrase ladders, label swaps, persona
   frames — semantic cues can dominate payoff incentives in conflict
   cells), while the non-lexical levers (payoff structure δ,
   temperature) do nearly nothing.
3. **Credibility layer** — registration, chronology, adjudication,
   byte-exact replay, and the external-review correction (the R2 p13
   family downgrade is part of the credibility story, not a footnote:
   the pipeline caught and recorded its own inferential defect
   post-adjudication).

## Main text keeps

| section | layer | content |
|---|---|---|
| persona-pool result | claim | P5-1a/P5-1b: bands pass, corners dominate; the three-layer P5-3 status table (registered verdict / p13 suggestive / clause-b confounded) |
| between/within decomposition | claim | μ(d), B(d), W(d), Δᵢ notation (propositions.md), pool vs persona response |
| X1/X2 | mechanism | the paraphrase span ladder (+0.925) and the X2 confirmation — the word channel at full strength |
| one label–payoff conflict | mechanism | ONE representative conflict cell (os-swap) with the word/payoff dissociation stated; the rest to supplement |
| concise provenance | credibility | registration → seal → adjudication chain in one figure; hash-cited excerpt of the sealed branch text + the precommitted-vs-post-review correction table (exact sealed excerpt, sha-cited; corrections listed beside what was precommitted) |

## Supplement

| section | reason |
|---|---|
| temperature inversion (entropy falls with T; matched-unit decomposition) | descriptive; P5-4 primary was null |
| detailed RPS results | secondary game class |
| adversary secondaries (E-family, ngram2 exploits) | mechanism detail beyond the one main-text conflict cell |
| most gemini material (cross-vendor anti-replication, sentinel demotion) | descriptive-only tier by sentinel ruling |
| dead-predictions inventory (12) | credibility depth; main text cites the count |
| freeze/recovery ledger, linter-escape pattern, ops-meta | credibility depth |
| full sealed discussion text (all branches) | main text carries the exact excerpt + correction table, hash-cited |
| DF microdata reanalysis, persona table, hierarchy/estimand table, family-audit detail | audit trail for the main-text claim layer |

## Rules

- The 16/16 P5-3 figure never appears without the mechanism disclosure
  and the three-layer status table.
- Every human number is labeled *published, nonmatched comparator* at
  first use per section.
- Nothing moves from supplement to main without re-checking its
  dependency row in `claim-dependencies.md`.
