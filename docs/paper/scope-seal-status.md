# Scope-seal status addendum

> **STATUS: LIVING DOCUMENTATION — NOT PART OF THE SEALED ARTIFACT.** This addendum resolves an ambiguity in the header of `scope-seal.md` without changing that file's sealed bytes.

## Why the original header still says “PROPOSED — UNSEALED”

`docs/paper/scope-seal.md` was drafted before Phase 5 dispatch and retained the header:

> `STATUS: PROPOSED — UNSEALED. Seals (hash-anchored with registry v4) before any Phase 5 dispatch.`

The file was subsequently included **verbatim** in the Phase 5 registry-v4 seal. Its SHA-256 is:

```text
a0389d9f3268d686ff2f4f8b93fa65c43aad77a35c52076ed1f365b4d935c0e6
```

That hash is pinned in [`../phase5/seal-record.md`](../phase5/seal-record.md), which records:

- registry v4 sealed on 2026-07-28 before dispatch;
- `scope-seal.md` included among the sealed files;
- annotated tag and release `phase5-v4-seal`;
- OpenTimestamps anchoring of the sealed manifest.

Editing the original header now would destroy the byte identity that establishes the stopping rule's chronology. The apparent status mismatch is therefore preserved and explained rather than silently corrected.

## Operative status

The stopping rule operated as sealed policy for paper one:

1. Phase 5 was the final experiment.
2. No new arm was added after the registry-v4 seal.
3. Post-verdict questions were routed to future work or zero-call reanalysis of archived data.
4. The historical discussion branches remained byte-identical.
5. The final Phase 5 record was replayed, adjudicated, released, and externally anchored.

## Citation rule

Living paper-facing documents should cite this addendum when describing the status of the stopping rule. The original `scope-seal.md` should be quoted only with the clarification that its “PROPOSED” header is itself part of the pre-dispatch sealed byte sequence.
