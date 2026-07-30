# synthetic-players-capsule — public reproduction capsule

**What this is.** The self-contained reproduction capsule for the confirmatory
*​Synthetic Players* research record: the append-only event store, every archived
LLM request/response event, sealed prompt registries and freeze packets, claims
and adjudication records, analysis code, checksum manifests, timestamp proofs,
and a one-command zero-credential verifier.

**What this is not.** It contains no API keys or live-call requirement. The
verifier never contacts a model provider.

## Verify (one command, zero credentials)

```bash
./verify.sh
```

The verifier checks the capsule-wide SHA-256 manifest, stages the archived event
and budget stores, clears provider credentials, and verifies **4,916 Phase 3–5
confirmatory runs**:

- **Phase 3/X1:** 320 LLM runs replayed from recorded completions plus 20
  deterministic pattern-tracker-vs-Nash baselines independently recomputed;
- **Phase 4:** 2,864 runs replayed byte-exact;
- **Phase 5:** 1,712 runs replayed with bundle/request-body hashes, parsed
  actions, temperature and revision pins, and persona reconstruction.

Expected final line:

```text
CAPSULE VERIFICATION PASS — 4,916 Phase 3-5 runs verified
```

The Phase 3 path uses the legacy generic replay implementation: it re-renders
prompts, requires recorded-cache hash hits, reparses raw responses, and
recomputes actions, payoffs, and RNG draw counts. Phase 3 predates the richer
Phase 4–5 response-ID and deterministic request-body-sha capture; that provenance
boundary is stated in the paper.

Timestamp proofs under `verify/` and the phase close-out directories establish
the release and seal chronology. The capsule checksum manifest is verified
before any analysis runs.

## Relationship to the repository

This directory is the portable verification surface within the public source
repository. The full repository adds commit history, living manuscript files,
review records, and post-adjudication analyses; the capsule contains the data and
code needed to verify the archived confirmatory record without relying on a live
endpoint.

## Layout

```text
data/     compressed event store, budget ledger, and driver state

docs/     registrations, freeze packets, seal records, adjudications, analyses

artifacts/api-server/   engine, replay, adjudication, prompts, pinned environment

verify/   timestamped checksum manifests

verify.sh one-command zero-credential verifier

SHA256SUMS.capsule   capsule-wide manifest checked before replay
```
