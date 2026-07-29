# Drop runbook — coordinated public release

> Checklist for drop day. **No step here executes before drop day.** Each
> step has a verification and a rollback line. Execute top to bottom; stop
> at the first failed verification and roll back that step only.

Prereqs on the day: a machine with `git`, `curl`, `sha256sum`, `uv`, and NO
repo credentials cached beyond the owner account; the repo at tag
`phase5-final`; nothing uncommitted.

## 1. Flip repository visibility → public

- **Do:** GitHub → Settings → General → Danger Zone → Change visibility →
  Public (owner action; the agent never does this).
- **Verify:** from a logged-out browser / `curl -s -o /dev/null -w '%{http_code}'
  https://github.com/yoheinakajima/synthetic-players` → `200`.
- **Rollback:** same menu → Private. (Caches: assume anything public for
  even a minute may have been crawled.)

## 2. Anonymous clone + asset download verification

- **Do (no credentials, e.g. a clean container):**
  ```
  git clone https://github.com/yoheinakajima/synthetic-players.git
  cd synthetic-players && git checkout phase5-final
  curl -fLO https://github.com/yoheinakajima/synthetic-players/releases/download/phase5-final/DATA-SHA256SUMS.txt
  # download every asset listed on the phase5-final release page, then:
  sha256sum -c DATA-SHA256SUMS.txt
  sha256sum -c docs/phase5-close/SHA256SUMS-final.txt
  ```
- **Verify:** clone succeeds anonymously; every asset downloads; both sums
  files check clean.
- **Rollback:** if any asset 404s or mismatches → step 1 rollback (go
  private), fix the release asset, start over.

## 3. `ots upgrade` + verify every stamp

- **Do:**
  ```
  uvx --from opentimestamps-client ots upgrade docs/phase5-close/SHA256SUMS.txt.ots
  uvx --from opentimestamps-client ots upgrade docs/phase5-close/SHA256SUMS-final.txt.ots
  uvx --from opentimestamps-client ots upgrade docs/phase4/SHA256SUMS.txt.ots
  uvx --from opentimestamps-client ots verify  <each .ots against its file>
  ```
  (On Replit, prefix with the libssl `LD_LIBRARY_PATH` workaround if needed;
  see `docs/close-out-verification.md`.)
- **Verify:** every stamp upgrades to a Bitcoin attestation and verifies.
  If a calendar is still pending, note it and re-run later — pending is not
  failure.
- **Rollback:** none needed — upgrades only add attestations. Commit the
  upgraded `.ots` files (they are additive) and push.

## 4. Flip the publication switch

- **Do:** in `artifacts/lab/src/lib/publicationStatus.ts` set
  `PRE_PUBLICATION = false`; commit and push; redeploy the lab if deployed.
- **Verify:** step 5.
- **Rollback:** revert the one-line commit; redeploy.

## 5. Confirm banners cleared only where intended

- **Do:** load the lab Papers list and a paper detail page.
- **Verify:** the DRAFT banner (`data-testid="banner-draft-status"`) is gone
  from both; the README draft-banner blockquote has been removed in the same
  commit (it is manual — check `README.md` top); the EXPLORATORY banners on
  `docs/analysis/**` REMAIN (they are permanent labels, not draft banners).
- **Rollback:** revert the step-4 commit.

## 6. Post-drop smoke

- **Do / verify, from an anonymous environment:**
  - README renders on the GitHub front page with working links (click the
    Phase 5 report, analysis INDEX, dead-predictions links).
  - `https://github.com/yoheinakajima/synthetic-players/releases/tag/phase5-final`
    resolves and lists all assets.
  - Fresh-clone verification rerun, truly anonymous: restore the DBs from
    release assets and run the replay audit + adjudicator selftest +
    `--adjudicate`, per the transcript in `docs/close-out-verification.md`
    (expect: CLEAN 1,712/1,712; ALL PASS; selectedBranch 2; no secrets, no
    live calls — run under `env -u` for all `AI_INTEGRATIONS_*` vars).
- **Rollback:** for a broken link or render, fix-forward with a docs-only
  commit. For a replay/adjudication mismatch: **go private immediately**
  (step 1 rollback) and investigate — that is a record-integrity stop, not
  a cosmetic fix.

## Notes

- Order matters: visibility first, then verification, then the banner flip —
  a public repo with a DRAFT banner is honest; a private repo with cleared
  banners is not a drop.
- Every git push on drop day is owner-credentialed; no agent tokens.
- The seal gate (`engine/close_seal.py`) is for future seals; nothing on
  drop day re-seals anything.
