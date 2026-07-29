# Public verification transcript — anonymous, zero-credential (2026-07-29)

> **STATUS: WORKING DRAFT — PRE-PUBLICATION, NOT FOR CITATION.**
> Banner note: this transcript documents a process, not a scientific claim.

The repository `yoheinakajima/synthetic-players` was made **public** on
2026-07-29 (flip performed by the operator in the GitHub UI; commit at flip:
`ddf4e8d`). This document records the first end-to-end verification performed
*after* the flip, from an environment configured to look like an arbitrary
member of the public:

- fresh scratch directory, `HOME` pointed away from any real profile
- **no git identity**, no credential helper, no `GITHUB_TOKEN`/`GH_TOKEN`
- **no provider variables** (`AI_INTEGRATIONS_*` all unset for the audits)
- plain `git clone https://github.com/yoheinakajima/synthetic-players.git`
- release assets fetched via public `browser_download_url` raw URLs only

## 1. Anonymous clone

```
git -c credential.helper= clone https://github.com/yoheinakajima/synthetic-players.git
→ HEAD = ddf4e8d (main)   CLONE-OK
```

## 2. Release-asset raw-URL spot checks (`phase5-final`, 15 assets)

All 15 assets downloaded anonymously from
`https://github.com/yoheinakajima/synthetic-players/releases/download/phase5-final/…`.

- `sha256sum -c DATA-SHA256SUMS.txt` → **5/5 OK**
  (engine.db.xz, budget.db.xz, phase5-driver-state.json,
  phase5-driver-plan.json, analysis-pack.tar.gz)
- `sha256sum -c SHA256SUMS-final.txt` (31 entries; run against the release
  assets plus the anonymous clone's `docs/` tree) → **24/31 OK**, including
  every sealed-record file: adjudication-decisions.json,
  adjudication-report.{json,md}, replay-audit.{json,md}, branch-selection.md,
  phase5/final-report.md, and both data manifests.
- The **7 mismatches are expected and disclosed**: they are exactly the
  *living* analysis docs amended in the post-adjudication R2 revision round
  (INDEX.md, claims-ledger.md, dead-predictions-final.md,
  human-anchor-scorecard.md, program-synthesis-DRAFT.md,
  persona-pack/README.md, distribution-pack/README.md — see the
  claims-ledger R2 entry for the p13 status downgrade). `SHA256SUMS-final.txt`
  pins the tree at the moment of the `phase5-final` release; sealed documents
  are never edited, corrections travel alongside. No sealed file mismatched.

## 3. Full capsule verification (`capsule/verify.sh`)

Run from the anonymous clone's committed `capsule/` directory with all
provider variables unset (fail-closed zero-credential guard is part of the
script). Result:

```
== 1/4 capsule integrity: SHA256SUMS.capsule            OK
== 2/4 stage data                                       OK
== 3/4 zero-credential guard                            OK (no provider variables set)
== 4/4 byte-exact replay audits (no live calls)
[phase4] self-check ok templatesChecked=49 mismatches=0
[phase5] self-check ok templatesChecked=4 personas=16 mismatches=0
phase4 step-8 audit:  2,864/2,864 byte-exact            CLEAN
phase5 replay audit:  1,712/1,712 ok, 0 failures        PASS — CLEAN
CAPSULE VERIFICATION PASS
```

Total: **4,576/4,576 observations replay byte-exact, zero credentials, zero
live model calls.** The claim "anyone can verify" is now literally true on
the record.

## 4. OpenTimestamps status (upgraded 2026-07-29)

All four stamps were upgraded (`ots upgrade`) and now carry **complete
Bitcoin block-header attestations**; the upgraded proofs are committed (and
mirrored into `capsule/verify/`):

| Proof | Target | Bitcoin block |
|---|---|---|
| `docs/phase4/SHA256SUMS.txt.ots` | `phase4-v3-seal` release asset `SHA256SUMS.txt` (file-match verified) | **959483** |
| `docs/phase5-close/SHA256SUMS.txt.ots` | `docs/phase5-close/SHA256SUMS.txt` | **959985** |
| `docs/phase4-close/SHA256SUMS.txt.ots` | `docs/phase4-close/SHA256SUMS.txt` | **960020** |
| `docs/phase5-close/SHA256SUMS-final.txt.ots` | `docs/phase5-close/SHA256SUMS-final.txt` | **960086** |

`ots verify` in this environment confirms file↔proof match and stops at
"Could not connect to Bitcoin node" — final chain confirmation requires a
local Bitcoin node (or `ots verify` on a machine that has one); the attested
block heights above are extractable by anyone via `ots info <proof>`. No
calendar is still pending; the Bitcoin-attestation task is closed.
(Tooling note: the OTS client needs a working libcrypto for its
python-bitcoinlib import; this does not affect proof bytes.)

## 5. Provenance note

The visibility flip changes **no recorded artifact** — every sha, seal, tag,
and release asset is byte-identical before and after; only repository access
changed. See the flip entry in
[docs/analysis/claims-ledger.md](analysis/claims-ledger.md).
