# Close-out verification transcript (2026-07-28)

Executed per the close-out order: verification BEFORE the final tag. Every
step below was run by the agent on 2026-07-28; commands and outputs are
quoted from the actual session.

## 1. Secret scan — PASS

- Working tree: `git grep` over patterns for OpenAI/AWS/GitHub/Slack keys,
  PEM private keys, bearer tokens → **0 hits** (excluding this prompt's own
  attached text). Only environment-variable *names* (`AI_INTEGRATIONS_*`)
  appear in code, never values.
- Full history: the same pattern scan over every commit reachable from any
  ref (`git rev-list --all` × `git grep`) → **0 hits**. No history rewrite
  needed or performed.

## 2. Data artifacts — exported and hash-locked

Source databases WAL-checkpointed and `VACUUM INTO` snapshots taken, then
xz-compressed:

| asset | bytes (compressed) |
|---|---|
| `engine.db.xz` (append-only event store, all phases) | 5,273,072 |
| `budget.db.xz` (transactional spend ledger + resolutions) | 142,472 |
| `phase4-driver-state.json` (driver at hold, attestations) | 623,455 |
| `phase4-driver-plan.json` | 328 |

sha256s in `DATA-SHA256SUMS.txt` (a release asset, verified below).
In-repo distribution rejected: engine.db is 219 MB uncompressed; release
assets keep the clone light. Restore path: `scripts/restore-data.sh`
(downloads, sha256-verifies, refuses to overwrite existing data).

## 3. Fresh-clone acid test — PASS on all steps

Clone of commit `1a522d2` (== origin/main; anonymous GitHub clone is blocked
because the repository is **private** — disclosed below; the clone used for
the test is byte-identical to the pushed commit, verified by sha).

Data staged exactly as the release ships it, with `sha256sum -c
DATA-SHA256SUMS.txt` → all `OK`.

**Zero-secret, zero-live-call environment**: the engine server was started
with every `AI_INTEGRATIONS_*` variable explicitly unset
(`env -u ... uv run python engine/server.py`, port 8095).

| step | result |
|---|---|
| server start without secrets | PASS (providers are lazily bound at dispatch; replay path never touches them) |
| §F.3 extended replay audit (`phase4_step8_audit.py`) | **PASS — CLEAN**: 2,864/2,864 completed observations byte-exact (bundle-sha, request-body-sha, parsed actions, per-round rng draw counts); 24 provider-failure partials verified as non-observations by signature; all Family-F rngCalls profiles match the sealed specs |
| live-call check | PASS — server log contains **zero** provider-URL hits for the entire audit |
| adjudicate-all (`--x2-screening --x2-confirm --d1 --d2 --d3 --e --f`, scipy modes under `uv run --with numpy --with scipy`) | PASS — all seven exit 0 |
| output comparison vs committed reports | PASS — all seven report JSONs **identical** to the committed record modulo the `generatedAt` timestamp (and `versions` stamp) |

Nothing required a secret or a live call. **Defects found: none** in the
replay/adjudication path.

## 4. Disclosed limitation: repository visibility

The repository is currently **private**. The reproducibility contract
("anyone can clone") is fully true *mechanically* — no secrets, no live
calls, sha256-locked public-format assets — but a stranger cannot reach the
repo or its release assets until the owner flips visibility to public.
That is an owner decision, not an agent action; flipping it requires no
change to any artifact in this record.

## 5. Anchors

- `SHA256SUMS.txt` covers all 29 release assets (reports, registries,
  adjudication records, data artifacts, `DATA-SHA256SUMS.txt`).
- OpenTimestamps proof `SHA256SUMS.txt.ots` created 2026-07-28, submitted to
  four calendars (a.pool.opentimestamps.org, b.pool.opentimestamps.org,
  a.pool.eternitywall.com, ots.btc.catallaxy.com). The proof upgrades to a
  Bitcoin attestation once aggregated; `ots upgrade SHA256SUMS.txt.ots`
  completes it later. This is the second independent anchor; the GitHub
  server timestamp on the annotated `phase4-final` tag is the first — same
  discipline as `phase4-v3-seal`, and the same disclosed deviation: **no
  GPG signature** (no signing key exists in the execution environment).
- Copies of `SHA256SUMS.txt` and `SHA256SUMS.txt.ots` are committed under
  `docs/phase4-close/` so the anchor material survives independently of the
  release.

## 6. Quiescence

The Phase 4 driver is at **hold** with a completed plan and a full sentinel
attestation record; every workflow is stopped. Any new dispatch requires a
new sealed registration (see `docs/phase5/process-packet.md`, PROPOSED).
