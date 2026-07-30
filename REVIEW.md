# Reviewer entry point

> **CURRENT REVIEW SURFACE:** this repository, beginning with this file and [`docs/paper/paper-draft.md`](docs/paper/paper-draft.md). The manuscript is ready for full scientific review, but remains a working draft and should not be cited.

Thank you for reviewing **Synthetic Players**. Everything needed to evaluate the manuscript, analyses, chronology, corrections, and reproduction claims is public here. No private bundle or outside explanation is required.

## Start here

1. **Formatted review PDF:** [`docs/paper/synthetic-players-review-v11.pdf`](docs/paper/synthetic-players-review-v11.pdf)
2. **Current v11 review-revision Markdown manuscript:** [`docs/paper/paper-draft.md`](docs/paper/paper-draft.md)
3. **Round 4 direct reproduction and review:** [`docs/reviews/round-4-independent-review.md`](docs/reviews/round-4-independent-review.md)
4. **Round 3 artifact verification:** [`docs/reviews/round-3-independent-verification.md`](docs/reviews/round-3-independent-verification.md)
5. **Machine-readable submission-analysis summary:** [`docs/analysis/submission/submission-analysis-summary.json`](docs/analysis/submission/submission-analysis-summary.json)
6. **Review/submission status:** [`docs/analysis/submission-blockers.md`](docs/analysis/submission-blockers.md)
7. **Novelty boundary:** [`docs/analysis/novelty-relationships.md`](docs/analysis/novelty-relationships.md)
8. **Literature map:** [`docs/analysis/literature-map.md`](docs/analysis/literature-map.md)
9. **Identification propositions:** [`docs/analysis/propositions.md`](docs/analysis/propositions.md)
10. **Exact manuscript history:** [`docs/paper/history/`](docs/paper/history/)
11. **Review and role-disclosure record:** [`docs/reviews/`](docs/reviews/)

## What the paper claims

A fixed panel of sixteen lightweight persona prompts passed preregistered **coarse marginal checks**. Finite-opportunity-corrected plug-in estimates assign 85%–96% of observed episode-level variation between prompts; a fixed-panel latent-propensity sensitivity yields posterior median shares of 63%–71% with 95% intervals spanning 49%–81%. The two observed aggregate continuation-probability contrasts are +0.083 and +0.078, with conservative exact intervals [−0.171, +0.330] and [−0.181, +0.330] (rounded to three decimals). The point estimates are small, but the intervals remain compatible with materially larger positive and negative effects; the paper does **not** claim equivalence, a null response, incentive insensitivity, or human substitutability.

The central mechanism-level claim is bounded:

> Coarse marginal checks can be satisfied through substantial between-prompt composition without requiring the represented-treatment response to be estimated; plug-in concentration estimates are reduced and widened when latent boundary-policy uncertainty is propagated.

The paper does not claim that this is the only failure mechanism, that it generalizes to all persona generators, that paired explicit prompts instantiate stable latent people, or that the published human comparator is protocol-matched.

## Corrections reviewers should know before reading

- **Explore Science review of v10:** [`docs/reviews/round-9-explore-science-v10-review.md`](docs/reviews/round-9-explore-science-v10-review.md) identifies reporting-completeness and boundary-uncertainty issues addressed in v11; the scientific change is declared in [`docs/paper/v11-addendum.md`](docs/paper/v11-addendum.md).
- **Claude v9 freeze review:** [`docs/reviews/round-8-claude-v9-freeze-review.md`](docs/reviews/round-8-claude-v9-freeze-review.md) mechanically verifies the v8→v9 delta, closes two citation checks, and recommends freezing scientific text after three micro-fixes integrated into v10.
- **Claude v7 repository review:** [`docs/reviews/round-6-claude-v7-review.md`](docs/reviews/round-6-claude-v7-review.md) verifies the Round 5 audit and motivates the final v8 registration, power, construct, and figure polish.
- **Round 5 audit:** [`docs/analysis/submission/round5/round5-review-audit.md`](docs/analysis/submission/round5/round5-review-audit.md) documents dynamic gate reapplication, exact-gate power, and the completion-provenance boundary.
- The broad realism-versus-effect divergence is occupied by prior work; novelty is positioned around the strategic-interaction decomposition, representation experiments, and audit architecture.
- Strong positive contrary evidence is addressed explicitly: Ashokkumar, Hewitt, Ghezae, and Willer (Nature 2026) predict study-level treatment effects well, a forecasting estimand distinct from subject-level response-surface simulation.
- The Dal Bó–Fréchette comparison is protocol-nonmatched and contextual, not an effect-size benchmark.
- The historical P5-1a binary verdict is interval-method-sensitive: restricted counts are 3/32 under the frozen seat rule, 2/32 under the conservative exact-episode sensitivity, and 5/32 under a Dirichlet–Jeffreys sensitivity.
- The favored p13 interpretation is withdrawn. Three post-review familywise variants are disclosed: historical-gate `p=0.059230`, percentile-bootstrap sensitivity `p=0.043455`, and conservative exact sensitivity `p=0.773206` for p05/s2a after p13 becomes gate-ineligible. None was registered at the original freeze, and the exact n=6 family is underpowered; p13 is neither prospectively confirmed nor decisively disconfirmed and remains a replication target.
- The original scope-seal file retains a pre-seal “PROPOSED” header because that exact byte sequence was later hash-sealed. See [`docs/paper/scope-seal-status.md`](docs/paper/scope-seal-status.md).
- Reviewers first diagnosed several defects, then one reviewer helped specify post-adjudication analyses; GitHub Actions executed them against the archived databases, and a later reviewer independently checked the branch. The role transition is disclosed in [`docs/reviews/README.md`](docs/reviews/README.md).

## Reproduce the archived record

```bash
git clone https://github.com/yoheinakajima/synthetic-players
cd synthetic-players/capsule
bash verify.sh
```

Expected result: **4,576/4,576 Phase 4–5 runs replay byte-exact with zero credentials and zero live model calls.** Round 4 reproduced this end-to-end on an outside machine rather than relying only on Actions evidence.

The zero-call submission analyses are generated from the archived databases by [`.github/workflows/submission-gate-analyses.yml`](.github/workflows/submission-gate-analyses.yml). Their outputs are under [`docs/analysis/submission/`](docs/analysis/submission/), and the current paper figure is under [`docs/paper/figures/`](docs/paper/figures/).

## Highest-value review questions

Please attack these first:

1. **Novelty and framing:** Is the mechanism-level differentiation from Li–Ji, causal-surrogacy work, Lin-style latent drift, persona collapse, state blindness, and direct strategic-game work sufficiently sharp?
2. **Inferential target:** Does the manuscript correctly distinguish fixed-panel, persona-generator, prompt-indexed, and human-substitution estimands?
3. **Response interpretation:** Does Figure 1 make clear that +0.083/+0.078 are small but imprecise point estimates, not equivalence results, null findings, or identified upper bounds?
4. **Composition claim:** Is the three-view uncertainty presentation—plug-in/conditional bootstrap, fixed-panel latent-propensity posterior, and persona-generator bootstrap—appropriately matched to its estimands?
5. **Audit status:** Are all three post-review p13 variants characterized fairly, including the favorable percentile-bootstrap `p=0.043455` sensitivity and the absence of pre-compute sealing?
6. **Scope and cuts:** What should leave the main paper, and what important result has been over-demoted?
7. **Contrary evidence:** What existing paper most directly weakens or duplicates the claimed mechanism-level novelty?

## How to respond

Open a GitHub issue or comment on the review pull request. The most useful order is:

1. novelty and framing;
2. statistics and estimands;
3. missing literature or contrary evidence;
4. structure and cuts;
5. line edits.

Please distinguish a proposed reinterpretation of the living manuscript from a requested change to a sealed historical artifact. Sealed records are preserved; corrections travel beside them.
