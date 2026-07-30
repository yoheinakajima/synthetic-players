# Review record

> **STATUS: LIVING TRANSPARENCY RECORD.** These documents archive adversarial review, role changes, verification passes, and adopted corrections to the living manuscript. They are not sealed experimental evidence and do not alter historical verdicts.

## Review rounds

| record | role | effect on paper |
|---|---|---|
| [`round-1-review-summary.md`](round-1-review-summary.md) | Multi-review synthesis | Identified the multiplicity problem, nonmatched comparator, unproven human microstructure, occupied broad thesis, and three-papers problem. |
| [`round-2-methods-review.md`](round-2-methods-review.md) | Adversarial methods and framing review | Specified the zero-call statistical queue and key estimand corrections. |
| [`round-2-editorial-reviews.md`](round-2-editorial-reviews.md) | Editorial and framing synthesis | Resolved title/abstract discipline, main/supplement architecture, scope, and attribution conventions. |
| [`round-3-independent-verification.md`](round-3-independent-verification.md) | Independent anonymous-clone verification of PR #2 at `5858543` | Verified v4 against generated artifacts; identified the omitted favorable audit variant and missing pre-compute seal. |
| [`round-4-independent-review.md`](round-4-independent-review.md) | Independent clone, lint, and full capsule reproduction on `main` at `8772a90` | Reproduced 4,576/4,576 runs, verified v5 numerically, and requested the final uncertainty, novelty, contrary-evidence, JSON, and PDF edits. |
| [`round-5-explore-science-review.md`](round-5-explore-science-review.md) / [`round-5-disposition-matrix.md`](round-5-disposition-matrix.md) | Explore Science review and response | Thirteen minor issues; dynamic-gate, power, provenance, construct, reporting, and figure corrections integrated into v7. |
| [`round-5-explore-science-review.md`](round-5-explore-science-review.md) / [`round-5-disposition-matrix.md`](round-5-disposition-matrix.md) | Explore Science review of v6 and response | Scored the paper 92/100 with no major issues; thirteen minor issues led to dynamic-gate, power, provenance, construct, reporting, and figure corrections integrated into v7. |
| [`round-5-response-plan.md`](round-5-response-plan.md) | Author-side synthesis and disposition plan | Separated immediately correctable issues from controls requiring a new prospectively registered phase and defined the v7 release gate. |
| [`round-6-claude-v7-review.md`](round-6-claude-v7-review.md) | Independent repository review of v7 | Verified the Round 5 audit, corrected artifact-selection provenance, and requested final abstract, interval, power-boundary, cross-vendor, and figure polish integrated into v8. |
| [`round-7-claude-v8-review.md`](round-7-claude-v8-review.md) | Independent review of commit-pinned v8 | Requested the archived-record versus latent-propensity distinction, the evidentiary meaning of “cheap,” composition-first gate reporting, Monte Carlo precision, and count reconciliation integrated into v9. |
| [`round-8-claude-v9-freeze-review.md`](round-8-claude-v9-freeze-review.md) | Mechanical freeze-integrity and citation review of v9 | Confirmed the v8→v9 diff, closed two citation checks, requested three micro-fixes, and recommended freezing scientific text after v10. |

| [`round-9-explore-science-v10-review.md`](round-9-explore-science-v10-review.md) / [`round-9-disposition-matrix.md`](round-9-disposition-matrix.md) | Explore Science review of frozen v10 and v11 response | 97/100, 0 major and 20 minor issues; numerical anchors, latent-policy uncertainty, figures, and construct qualifiers addressed in v11. |

## Role disclosure

The Round 2 methods-review role expanded after critique:

1. it diagnosed inferential and framing defects;
2. it specified several post-adjudication zero-call analyses;
3. GitHub Actions executed those specifications against archived databases with fixed seeds;
4. Yohei Nakajima and the Actions bot committed generated outputs;
5. later reviewers independently checked the branch, and Round 4 directly reproduced the capsule on an outside machine.

Round 5 was performed by Explore Science against the formatted v6 review PDF. The author-side response plan is explicitly separate from the external review record. Rounds 6–8 used artifact-pinned repository or PDF review and introduced a permanent requirement to identify the exact source commit, PDF hash, page count, and build record.

This is not presented as independent replication of the experiment. It is an auditable separation among critique, analysis specification, automated execution, integration, later verification, and external manuscript review.

## Preservation rule

Reviewer text may be summarized for readability, but material criticisms, numerical corrections, and adopted dispositions should remain recoverable. Sealed research files are never edited in response to review; living interpretation documents and explicit addenda carry the corrections.

- [`round-10-explore-science-v11-review.md`](round-10-explore-science-v11-review.md) and [`round-10-disposition-matrix.md`](round-10-disposition-matrix.md): final Explore Science review and v12 disposition.
