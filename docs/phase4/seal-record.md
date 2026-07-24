# Phase 4 Registry v3 — Seal Record

- **Sealed at:** 2026-07-24T18:58:15Z
- **Sealed by:** user approval (mission UI, 2026-07-24: "Seal now — GitHub is connected,
  anchor externally too"), executed by the agent per the frozen execution order, step 3.
- **What changed:** exactly one line of `artifacts/api-server/prompts/registry.json` —
  `registryVersion` `"phase4-v3-proposed"` → `"phase4-v3"`. Zero template, arm, seed,
  binding, or schedule bytes changed.
- **Pre-seal registry sha256:** `2ef069db5ce28b6837794aea70e09ed77b7a3018963e29bdcaf70c7857536eb4`
  (byte-identical to the sha recorded at Gate 0 execution — `gate0-report.md` — and
  re-verified immediately before the flip; the flip refused to run on any drift.)
- **Post-seal registry sha256:** `0c084b73a38c63ccfc95622a78b21d2a2c34113e0648b1d7037a5a6ce0695f05`
- **arms.json sha256 (unchanged):** `eba6b7f10976598dea719d6ebf7921b1f81d6fc93d4b49e3768753bec1325a62`
  (matches the engine startup self-check `armsManifestSha256`.)
- **execution-schedule.json sha256 (unchanged):** `139c1b6d514487ea2412d2ad0fa8bda36f79dffed59f4955b0180452239fa444`
- **Sealed-name decision:** `phase4-v3`. No sealed-name string was pre-registered; the
  engine's seal predicate is `not registryVersion.endswith("-proposed")`. Recorded here
  as the naming decision.
- **Effect:** the engine live-run gate opens for Phase 4 arms. All other machinery stays
  in force unchanged: server-side enforcement of pins, template-sha self-check at every
  boot, transactional budget caps (global 21,000), sentinel seed windows, write-once
  resolutions, replay verification.
- **Amendment rule:** any subsequent change to registry v3 templates, arms, seeds, or
  schedule requires a registered amendment; this record plus the external anchor below
  is the seal.

## External anchor

Executed 2026-07-24, immediately after the seal:

- **Seal commit:** `d24ee94ea722d817f0382519445c5e9d11a7bb1f` — pushed to `main` on
  https://github.com/yoheinakajima/synthetic-players (user's connected GitHub account).
- **Tag:** `phase4-v3-seal` — annotated tag object `93af9ef1b484440d9a869054b2d80132063d89b0`
  pointing at the seal commit, created via the GitHub API. **Not GPG-signed** — the
  registered plan (provider-packet §4) said "signed tag"; no signing key exists in the
  execution environment, so the tag is annotated-only. Disclosed here as a plan
  deviation; the release timestamp below, not a signature, is the anchor.
- **Release:** https://github.com/yoheinakajima/synthetic-players/releases/tag/phase4-v3-seal
  (id 359492307), **published 2026-07-24T19:04:16Z — GitHub server timestamp, the
  public anchor**.
- **Assets uploaded:** post-seal `registry.json`, `arms.json`, `SHA256SUMS.txt`
  (checksum manifest covering pre/post-seal registry, arms, schedule, and the seal
  commit sha).
- **Verification path for third parties:** download the release assets, hash them
  (sha256), compare against this record, `SHA256SUMS.txt`, and `gate0-report.md`;
  confirm the tag points at the seal commit and the release timestamp.
- **Language rule:** this registry is **externally anchored** (GitHub release
  timestamp as public anchor) — not "cryptographically immutable".
