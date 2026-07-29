# Round 4 — independent reproduction and final editorial review

> **SOURCE STATUS:** Reviewer-supplied review, 2026-07-29, summarized for the public archive. The reviewer anonymously blobless-cloned `main` at `8772a90`, read the complete review surface, ran `scripts/paper_submission_lint.py` locally, and ran `capsule/verify.sh` end-to-end with zero credentials.

## Direct verification

The reviewer reproduced the flagship capsule claim on an outside machine:

- Phase 4: 2,864/2,864 runs replayed cleanly, with 24 provider-failure partials disclosed by signature and excluded under the recorded rule;
- Phase 5: 1,712/1,712 runs replayed cleanly;
- total: 4,576/4,576 byte-exact.

The reviewer also cross-checked every load-bearing v5 number against the generated JSON and figure CSVs, including:

- aggregate contrasts +0.083333 and +0.078125 with exact simultaneous intervals;
- all three 200,000-permutation p13 variants;
- 14/11/19 of 96 and 3/2/5 of 32 boundary classifications;
- corrected SDs and 85.5%–96.1% between-prompt shares;
- P5-2, clause-(b), and count-reconciliation outputs.

No mismatch was found among the living manuscript, machine-readable results, lint, and capsule.

## Final requests and adopted dispositions

1. **Uncertainty language.** Replace “weak observed response” with small, imprecisely estimated point differences; explicitly note that intervals extend to approximately +0.33 and moderately negative effects.
2. **Li–Ji re-verification.** Re-read the expanded preprint, which now contains its own mechanism analysis, and narrow novelty to the specific fixed-panel composition mechanism, strategic representation interventions, and public correction architecture.
3. **Strong contrary evidence.** Restore Ashokkumar, Hewitt, Ghezae, and Willer (Nature 2026): strong study-level treatment-effect forecasting is a different estimand from subject-level response-surface simulation and is compatible with this paper's result.
4. **Figure interpretation.** Explain that repeated zero rows in the prompt-indexed response plot often arise from full concentration at the same boundary in both cells; they are not precise evidence of no effect.
5. **Machine-readable completeness.** Add aggregate and per-prompt response estimates and intervals to `submission-analysis-summary.json`.
6. **Gate degeneracy.** State explicitly that percentile interval degeneracy disqualifies the gate because the gate is itself an interval-interiority test.
7. **Review archive.** Add summaries of earlier review rounds so the attribution and preservation claims match the public record.
8. **Bibliography metadata.** Verify recent versions, venues, and author lists before producing the first formatted PDF.

## Verdict

The reviewer judged v5 ready for full scientific review. The remaining issues were editorial and interpretive rather than foundational. The v6 Explore Science draft implements the requests above and retains the scope seal against new subject calls.
