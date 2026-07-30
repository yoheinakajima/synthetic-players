# Capsule clean-directory verification transcript — R2 item 9

> **STATUS: DOCUMENTATION — 2026-07-29. Zero credentials, zero live
> calls. Commands and outputs quoted from the actual session.**

Procedure: `capsule.tar.gz` (built by `scripts/build-capsule.sh`)
extracted into an empty directory (`/tmp/capver`), then `./verify.sh`
run as shipped — no repo checkout, no environment preparation beyond
`bash/sha256sum/xz/python3/uv/curl`.

```
== 1/4 capsule integrity: SHA256SUMS.capsule
OK
== 2/4 stage data
== 3/4 zero-credential guard
OK (no provider variables set for the audits below)
== 4/4 byte-exact replay audits (no live calls; providers never touched)
[phase4] startup self-check ok=True templatesChecked=49 mismatches=0
[phase5] startup self-check ok=True templatesChecked=4 personas=16 mismatches=0
CLEAN
phase5 replay audit: 1712 runs
  1712/1712  ok=1712 failures=0  (5s)
replay audit: PASS — CLEAN  → docs/phase5-close/replay-audit.{json,md}
CAPSULE VERIFICATION PASS
```

Details:

- Step 4 starts a **local** engine server on port 8123 bound to the
  capsule's own event store (never a pre-existing server on the
  default port); the Phase 4 audit replayed **2,864/2,864** completed
  observations byte-exact (`STEP8_PHASE4_ONLY=1` scopes it to Phase 4;
  the store also holds Phase 5 runs, audited separately), and the
  Phase 5 in-process audit re-derived **1,712/1,712** runs
  (10,428 recorded calls byte-verified). Total: 4,916/4,916.
- Zero-credential guard: every `AI_INTEGRATIONS_*` / provider variable
  unset before the audits; the replay path never touches providers.
- The capsule-wide manifest (`SHA256SUMS.capsule`) verified before
  anything executed.
- One audit-tooling change was needed and is committed:
  `phase4_step8_audit.py` gained the opt-in `STEP8_PHASE4_ONLY` scope
  (the original close-out ran when the store held only Phase 4 runs);
  the sealed record is untouched.

Artifacts (private repo root, gitignored size permitting):
`capsule/` (11 MB), `capsule.bundle` (7.8 MB, fresh single-commit
history), `capsule.tar.gz` (7.7 MB), `capsule-SHA256SUMS.txt`.
Publishing requires two minutes of operator action —
`capsule/OPERATOR-STEPS.md`.
