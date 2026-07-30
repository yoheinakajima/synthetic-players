# Round 8 — Claude freeze review of v9

> **SOURCE STATUS:** Reviewer-supplied independent review of the July 30 v9 text-freeze candidate. This is a living review artifact, not sealed experimental evidence.

## Artifact reviewed

- PDF: `synthetic-players-review-draft-v9.pdf`
- PDF SHA-256: `ef13d5d18eb18e4365fc4b5d85e87d313f8176003709f311a37819c5df3d8dae`
- Review note: the artifact had initially been mislabeled as v8; the reviewer mechanically confirmed that it was the v9 candidate.

## Mechanical freeze-integrity check

The reviewer word-diffed v8 and v9 after removing typesetting noise. The delta matched the declared change set exactly:

- archived finite-panel contrasts separated from inference about latent configuration propensities;
- “cheap” defined as evidentiary economy;
- the abstract’s representation-versus-treatment-response asymmetry;
- exact-gate composition and Monte Carlo interval detail;
- Phase 4–5 request/response/ledger count reconciliation.

No silent scientific drift was found.

## Citation verification

The reviewer independently confirmed the two remaining load-bearing references:

- Ashokkumar, Hewitt, Ghezae, and Willer (Nature, 2026), including the 469-effects result and DOI used in the paper;
- Harry et al., *Findings of ACL 2026*, pages 26440–26468.

## Final micro-fixes adopted in v10

1. Replace “registered criteria/checks” in the failure-mode and “cheap” statements with the narrower “broad-reference marginal criteria/checks,” because P5-3(a) was itself a registered response criterion.
2. Render the add-one estimator unambiguously as `\(\widehat p=(r+1)/(B+1)\)`.
3. Align Appendix A.4 with §4.4 by describing the 12 of 28 gate-passing episode-value compositions before summarizing their admissible means.

## Freeze recommendation

The reviewer’s verdict was to freeze the scientific text after these three micro-fixes. Future changes should be venue-driven only unless a new scientific error is identified. The freeze publication checklist requested:

- commit the source and built PDF checksum in-tree;
- regenerate the machine-readable audit surface;
- archive review rounds 7–8;
- create and externally timestamp a generic text-freeze tag;
- declare the freeze scope so venue formatting cannot silently alter scientific content.
