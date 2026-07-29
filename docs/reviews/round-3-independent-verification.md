# Round 3 — independent anonymous-clone verification

> **SOURCE STATUS:** Reviewer-supplied verification memo, archived 2026-07-29. The reviewer anonymously blobless-cloned `agent/submission-gate-polish` at commit `5858543` (PR #2 head), cross-checked the manuscript against `docs/analysis/submission/submission-analysis-summary.json` and commit history, and relied on the GitHub Actions evidence rather than rerunning the capsule replay.

## What verified clean

Every number reported in the v4 manuscript matched the generated JSON:

- historical-gate family audit: \(p=0.0592\), MC interval [0.0582, 0.0603];
- exact-episode gate: p13 excluded, surviving candidates p04/s2p and p05/s2a, maximum slope +0.0833, \(p=0.7732\);
- 200,000 permutations with fixed seeds;
- interiority census: historical/exact/Dirichlet counts 14/11/19 of 96 and restricted counts 3/2/5 of 32;
- P5-1a's Dirichlet–Jeffreys verdict flip disclosed in the text;
- between-prompt shares 85.5%, 96.1%, 88.8%, and 90.2%;
- corrected SDs 0.418–0.478;
- the registered 0.75×-human-SD threshold reverified rather than replaced with an unregistered “matches humans” claim;
- count reconciliation: 5,505 completed runs, 4,576 replay-contract runs, 108,552 seat-round decisions, 54,276 rounds, 36,251 request events, and 30,530 Phase 4–5 ledger calls.

The reviewer endorsed the audit document's statement that a post hoc family analysis cannot retroactively create a prospectively family-controlled result and agreed that p13 must remain a replication target regardless of the numerical result.

## Finding 1 — a computed variant was omitted

The machine-readable summary also contained a third familywise construction:

- `episodeClusterBootstrapGate`: \(p=0.043455\), MC interval [0.042561, 0.044353].

It was the only construction below 0.05 and appeared in neither the paper nor the final audit prose. The reviewer agreed with the stated reason for rejecting it as primary—the percentile bootstrap degenerates at exact corners—but noted that the manuscript's own commitment to report rather than selectively resolve method sensitivity required publishing it.

**Adopted disposition:** report all three constructions (0.0592 / 0.0435 / 0.7732), designate exact-episode as primary, attach the conservatism and corner-degeneracy rationales, and keep p13 capped at replication-target status because none of the variants was registered at freeze.

## Finding 2 — no seal-before-compute record

The earliest commits touching `docs/analysis/submission/` already contained results. The proposed v3 A.7 registry never entered the repository before computation, and the candidate family was not adjudicated by a panel in a committed pre-analysis record.

**Adopted disposition:** do not imply preregistration or seal-before-compute discipline for the post-adjudication variants. State instead that the variants were specified and executed together after external review, run by GitHub Actions against archived databases with fixed seeds, and committed regardless of direction. Those facts constrain discretion but do not produce prospective confirmation.

## Smaller flags

1. `docs/paper/scope-seal.md` still displayed `PROPOSED — UNSEALED`, although downstream records treated it as a sealed stopping rule. Because the file's exact hash is in the Phase 5 seal, the correct fix is a living addendum rather than editing the sealed bytes.
2. Attribution needed to disclose that the round-2 reviewer role expanded from critique to analysis specification and integration management. Commits were authored by Yohei Nakajima and the Actions bot; this later independent review serves as a separate verification pass.
3. `docs/reviews/` did not exist. Review records and role changes should be archived there.
4. The Dal Bó–Fréchette microdata task remains deferred; “statistical gate complete” should explicitly mean complete with Q5 deferred.
5. Draft v2 and v3 should be committed to `docs/paper/history/` so version references resolve to actual manuscripts.

## Editorial recommendations

The reviewer endorsed:

- replacing “Corner Mixtures” in the load-bearing title because the binary census is interval-method-sensitive;
- correcting the abstract's registration language from “all claims were prospectively registered” to “confirmatory claims were registered before their adjudicating data”;
- replacing “stable policies” with language tied to observed concentration within recorded cells;
- reducing five contributions to three;
- moving Lucas/equifinality analogies to Discussion;
- adding a prompt-indexed \(\Delta_i\) figure with exact non-zero-width corner intervals, the latent-coupling caveat, and an aggregate interval so the ≤0.08 values cannot be mistaken for equivalence;
- retaining only a single caveated parenthetical for the protocol-nonmatched human comparator unless a later reviewer computes or emphasizes a ratio;
- holding the scope against new subject calls;
- canonicalizing the paper history.

## Resulting status

This verification did not identify a mismatch in the headline numerical results. It identified a transparency omission, a chronology overstatement risk, and several final repository/presentation tasks. Those corrections were adopted in v5 without changing sealed artifacts or historical mechanical verdicts.
