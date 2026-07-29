# Review record

> **STATUS: LIVING TRANSPARENCY RECORD.** These documents archive adversarial review, role changes, verification passes, and adopted corrections to the living manuscript. They are not sealed experimental evidence and do not alter historical verdicts.

## Review rounds

| record | role | effect on paper |
|---|---|---|
| [`round-2-methods-review.md`](round-2-methods-review.md) | Adversarial methods and framing review | Identified the nonmatched human comparator, family-error defect, seat/episode dependence issue, exact-mean identity, latent-person-invariance caveat, and three-papers problem; specified the zero-call submission queue. |
| [`round-3-independent-verification.md`](round-3-independent-verification.md) | Independent anonymous-clone verification of PR #2 at `5858543` | Cross-checked the v4 manuscript against generated JSON and commit history; verified all reported numbers, identified the omitted `p=0.043455` variant and missing pre-compute seal, and requested final canonicalization/attribution edits. |

## Role disclosure

The round-2 reviewer role expanded after critique:

1. it diagnosed inferential and framing defects;
2. it specified several post-adjudication zero-call analyses;
3. GitHub Actions executed those specifications against archived databases with fixed seeds;
4. Yohei Nakajima and the Actions bot committed generated outputs;
5. a separate round-3 reviewer then independently checked the branch through an anonymous blobless clone.

This is not presented as independent replication of the experiment. It is an auditable separation among critique, analysis specification, automated execution, integration, and later verification.

## Preservation rule

Reviewer text may be summarized for readability, but material criticisms, numerical corrections, and adopted dispositions should remain recoverable. Sealed research files are never edited in response to review; living interpretation documents and explicit addenda carry the corrections.
