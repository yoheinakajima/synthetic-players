# synthetic-players-capsule — public reproduction capsule

The capsule is the portable, zero-credential verification surface for the
*​Synthetic Players* confirmatory record. It contains the archived event and
budget stores, prompt registries, freeze packets, claims and adjudications,
replay code, checksum manifests, and timestamp proofs. It contains no API keys
and never calls a live model provider.

## Verify

From `capsule/`:

```bash
./verify.sh
```

The command verifies the capsule checksum manifest and then checks **4,916 Phase
3–5 confirmatory runs**:

- 320 Phase 3/X1 LLM runs replayed from archived completions;
- 20 deterministic Phase 3 baselines independently recomputed;
- 2,864 Phase 4 runs replayed byte-exact;
- 1,712 Phase 5 runs replayed with the richer provenance pins introduced after
  Phase 3.

Expected final line:

```text
CAPSULE VERIFICATION PASS — 4,916 Phase 3-5 runs verified
```

The Phase 3 replay path reconstructs prompts, reparses raw completions, and
recomputes actions, payoffs, and RNG draw counts. Phase 3 predates the Phase 4–5
response-ID and deterministic request-body-sha fields, a boundary documented in
the manuscript.

The full public repository adds commit history, manuscript versions, review
records, and post-adjudication analyses. The capsule alone is sufficient to
verify the archived confirmatory computations without credentials or a live
endpoint.
