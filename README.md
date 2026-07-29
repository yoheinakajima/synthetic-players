# Synthetic Players: a game-theory research lab that survived its own author

> **STATUS: WORKING DRAFT — PRE-PUBLICATION, NOT FOR CITATION.** The program
> is complete through Phase 5 and closes with **one paper** synthesizing
> v1→Phase 5 (working draft:
> [docs/analysis/program-synthesis-DRAFT.md](docs/analysis/program-synthesis-DRAFT.md)).
> Everything in this repository is citable-in-principle from its sealed
> records, but no document is final until the coordinated public drop.

**Verify everything in one command** (anonymous clone, zero credentials, zero
live model calls — 4,576/4,576 observations replay byte-exact):

```bash
git clone https://github.com/yoheinakajima/synthetic-players && cd synthetic-players/capsule && bash verify.sh
```

This repository is a full research program on how large language models play
games — run end-to-end under pre-registered, mechanically adjudicated,
fail-closed protocol. The central empirical finding: **LLM subject behavior is
driven by local semantic-textual content, not by payoffs and not by display
mechanics — and the cross-vendor twin inverts per channel.** The same subject
that is flatly insensitive to presentation factors (gpt-4.1 primary tier, all
four D1 main effects null) responds massively to role semantics (+0.73 to
+0.79 on the role channel, both vendors), while the secondary vendor is
presentation-sensitive exactly where the primary is not and reverses sign on
labeled-option bias and adversarial exploitability. Payoff structure — the
thing game theory says should matter — moved nothing the machinery could bind
(the δ-sensitivity assay corner-confounded at both vendors' behavioral
extremes).

The second contribution is the protocol itself: every claim was a sealed
machine-checkable predicate adjudicated by code, never by the author; every
observation replays byte-exact from an append-only event store; and every
process failure along the way — 22 of them — is on the record with the rule
it produced. See [docs/instance-ledger.md](docs/instance-ledger.md) (the
protocol contribution) and
[docs/analysis/dead-predictions-final.md](docs/analysis/dead-predictions-final.md)
(**twelve** author predictions the machinery refuted across five phases,
enumerated from the record — including both registered Phase 5 predictions).

## Phase map

| Phase | What it was | Registration | Report |
|---|---|---|---|
| v1 → v2 | 40 algorithmic-strategy experiments; 11 claims; v2 mechanical re-adjudication caught the author's errors | v1 paper preserved with errors | [docs/POSTMORTEM.md](docs/POSTMORTEM.md), [docs/v1/](docs/v1/) |
| Phase 3 | First LLM subject (gpt-4.1): 11 pre-registered claims on cooperation, framing, RPS | [docs/phase3-preregistration.md](docs/phase3-preregistration.md) | [docs/phase3-report.md](docs/phase3-report.md) (3 supported · 6 refuted · 1 inconclusive; X1 extension refuted), [layer-2 robustness](docs/phase3-layer2.md) |
| X1 | Paraphrase fragility: the 0.000 cooperation corner flips to 1.000 under rewording, same seeds | registered in phase3-report §6 | [docs/phase4/x1-semantic-equivalence.md](docs/phase4/x1-semantic-equivalence.md), [parser audit](docs/phase4/x1-parser-audit.md) |
| X2 | Which tokens carry the effect: screening + sealed confirmation | [freeze packet](docs/phase4/freeze-packet.md), [predicates](docs/phase4/predicates.md) | [screening](docs/phase4/x2-screening-report.md), [confirmation](docs/phase4/x2-confirmation-report.md) — supported (+0.925, LB .708) |
| Phase 4 | The main sealed program: D1 presentation factors, D2 role/word decomposition, D3 labeled-option bias, E δ-sensitivity, F adversarial exploitability, cross-vendor twin (gemini-2.5-flash), continuous sentinel monitoring | [freeze packet](docs/phase4/freeze-packet.md) · [predicates](docs/phase4/predicates.md) · [seal record](docs/phase4/seal-record.md) | **[docs/phase4/final-report.md](docs/phase4/final-report.md)** and per-family reports in [docs/phase4/](docs/phase4/) |
| Phase 5 | The conditioning layer: 16 sealed personas × the program's instruments, surface-cue dominance, temperature sweep (0.7/1.0/1.3), pre-committed discussion branches | [freeze packet](docs/phase5/process-packet.md) · [seal record](docs/phase5/seal-record.md) · [amendment 1](docs/phase5/amendment-1-caps.md) | **[docs/phase5/final-report.md](docs/phase5/final-report.md)** · [adjudication](docs/phase5-close/adjudication-report.md) · **Branch 2 selected** ([record](docs/phase5-close/branch-selection.md)) |

## Final verdicts (Phase 4; primary tier gpt-4.1 — details in the final report)

| Family | Claim | Verdict |
|---|---|---|
| X2 | P4-X2-1 token-level carrier | **Supported** (+0.925, LB95 0.708) |
| D1 | four presentation main effects | **All null** on primary; mirror sensitive (replication tier) |
| D2 | role channel (D2-1, D2-4) | **Supported both tiers** (+0.73/+0.79 gpt) |
| D2 | word channel (D2-2) | Null on primary; supported on mirror |
| D3 | first-option bias | **Not supported, sign reversed** (bias toward rock-only) |
| E | δ-sensitivity (4 assays) | **Corner-confounded** (registered branch — not evidence of insensitivity) |
| F | P4-F-1 exploitability conjunction | **Only-first branch**: wsls out-exploits fo (+0.126, LB .093) but does not profit (Ū +0.008) |
| F | secondaries (Holm m=6) | ngram2 exploits subject (+0.215); fo-tracker **negative** (−0.118 — subject beats it); rest n.s. |
| F | shuffled < fo directional | Not supported (−0.083) |
| F | cross-vendor tier | **Descriptive-only** (sentinel alert 6 ruling — see [memo](docs/phase4/sentinel-alert-6-memo.md)) |

## Final verdicts (Phase 5 — details in [docs/phase5/final-report.md](docs/phase5/final-report.md))

| Claim | Verdict |
|---|---|
| P5-1a persona pools are corner mixtures | **Supported** (restricted interior fraction 3/32 = 0.094 < 0.10 — by one unit; disclosed) |
| P5-1b between-persona SD vs human panels | **Corner-mixture-consistent** in all 4 matched cells |
| P5-2 surface-cue dominance | **Persona-dominant** — the author's registered task-dominant prediction failed (pooled task-consistent share 0.128, CP95 [0.104, 0.155]) |
| P5-3 interior-persona existence | **16/16 pass** against a registered prediction of zero; persona p13 passes the Family-E signature (δ-slope LB +0.083 > 0) — the program's only such pass |
| P5-4 temperature refutation | **Not refuted** (Newcombe LB −0.095); descriptively, entropy *fell* with T and invalids stayed 0 |

Axes A=supported · B=at-least-one · C=no select **Branch 2 — "an interior
persona exists"** from the pre-committed, hash-sealed
[discussion branches](docs/paper/discussion-branches.md)
(byte-identical to the sealed sha —
[branch-selection record](docs/phase5-close/branch-selection.md)).

## Reproducibility contract

The citable claim: **anyone can replay every observation byte-exact with zero
live model calls and zero secrets.** The event store (every request, response,
round, seed, and adjudication input) ships as versioned release assets.

```bash
git clone https://github.com/yoheinakajima/synthetic-players && cd synthetic-players
# fetch + verify + restore the data artifacts (sha256-checked):
bash scripts/restore-data.sh          # downloads from the phase4-final release
# start the engine (no secrets needed for replay) and run the full audit:
cd artifacts/api-server && (uv run python engine/server.py &) && sleep 2 \
  && cd engine && uv run python phase4_step8_audit.py
# expected: "CLEAN" — 2,864/2,864 observations byte-exact, all F rng profiles verified
```

Adjudication re-runs (`phase4_adjudicate.py --x2-screening|--x2-confirm|--d1|
--d2|--d3|--e|--f`) are deterministic from the store; scipy modes need
`uv run --with numpy --with scipy`. The verification transcript from a fresh
clone is in [docs/close-out-verification.md](docs/close-out-verification.md).

## Budget actuals (entire LLM program, from the transactional ledger)

- **20,102 provider calls** — gpt-4.1: 11,624 · gemini-2.5-flash: 8,463 · gate-0 mixed: 15
- **9,135,321 input tokens · 33,510 output tokens**
- By block: F 11,322 · D1 2,568 · X2 2,664 · E 1,403 · sentinel 1,200 · D2 641 · D3 289 · infra 15
- Calls were routed through Replit AI-integration proxies; the ledger prices
  in calls/tokens (per-dollar figures are the proxy's, not recorded here).
  Cap: 21,000 calls (never exceeded; every failure counted).

## Anchors

- Seal: annotated tag [`phase4-v3-seal`](https://github.com/yoheinakajima/synthetic-players/releases/tag/phase4-v3-seal) — GitHub server timestamp is the anchor; not GPG-signed (disclosed deviation, [seal record](docs/phase4/seal-record.md)).
- Close: annotated tag `phase4-final` + release with data artifacts,
  `SHA256SUMS.txt`, and an OpenTimestamps proof on the sums file as the second
  independent anchor.

## How to check our claims

Every claim is designed to be checked without trusting the author:

- **Replay the record:** `capsule/verify.sh` (command above) re-derives all
  4,576 observations byte-exact from the committed event store with all
  provider variables unset. First public run transcribed in
  [docs/public-verification.md](docs/public-verification.md).
- **Check the seals:** [phase4 seal record](docs/phase4/seal-record.md) ·
  [phase5 seal record](docs/phase5/seal-record.md) ·
  [branch selection](docs/phase5-close/branch-selection.md) — predicates and
  discussion branches were hash-sealed before data.
- **Check the timestamps:** OpenTimestamps proofs with complete Bitcoin
  attestations (blocks 959483 / 959985 / 960020 / 960086) on the sums
  manifests — `ots info docs/phase5-close/SHA256SUMS-final.txt.ots` etc.;
  proofs also ship in `capsule/verify/`.
- **Check the claim history:** the
  [claims ledger](docs/analysis/claims-ledger.md) records every claim's
  status over time, including the post-adjudication R2 downgrade and the
  [twelve dead predictions](docs/analysis/dead-predictions-final.md).

## Status: program closed, repository public (scope-sealed at one paper)

The repository went **public on 2026-07-29** (flip entry in the
[claims ledger](docs/analysis/claims-ledger.md); no recorded artifact
changed — only access). Phases 4 and 5 are complete; both drivers are at hold ("plan complete") and
any new dispatch requires a new sealed registration. Phase 5 closed clean:
1,712/1,712 runs replay byte-exact, 0 invalid trials, all 10 sentinel checks
positive, 10,428/11,185 budget. The close-out record is in
[docs/phase5-close/](docs/phase5-close/); the exploratory cross-program
analysis pack (claims ledger, dead predictions, human-anchor scorecard,
persona/temperature/distribution packs) starts at
[docs/analysis/INDEX.md](docs/analysis/INDEX.md). Under the
[scope seal](docs/paper/scope-seal.md) the program ends with **paper one**;
no new arms.

## Repository layout

- `artifacts/api-server/engine/` — Python engine: event-store server,
  dispatch driver, adjudicators, replay verifier, step-8 audit
- `artifacts/api-server/` + `artifacts/lab/` — TypeScript lab (v1/v2
  experiments, claims registry, generated papers) and its web UI
- `artifacts/api-server/prompts/registry.json` — sealed prompt registry (v3)
- `docs/` — every registration, report, memo, amendment, and ledger; start at
  [docs/phase4/final-report.md](docs/phase4/final-report.md)

## License & citation

Code is MIT-licensed ([LICENSE](LICENSE)). The data artifacts (event store,
reports, generated text) are released under CC BY 4.0 — cite via
[CITATION.cff](CITATION.cff).
