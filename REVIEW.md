# Reviewer entry point

> **CURRENT REVIEW SURFACE:** this repository, beginning with this file and [`docs/paper/paper-draft.md`](docs/paper/paper-draft.md). The manuscript is ready for full scientific review, but remains a working draft and should not be cited.

Thank you for reviewing **Synthetic Players**. Everything needed to evaluate the manuscript, analyses, chronology, corrections, and reproduction claims is public here. No private bundle or outside explanation is required.

## Start here

1. **Current manuscript:** [`docs/paper/paper-draft.md`](docs/paper/paper-draft.md)
2. **Independent verification memo:** [`docs/reviews/round-3-independent-verification.md`](docs/reviews/round-3-independent-verification.md)
3. **Machine-readable submission-analysis summary:** [`docs/analysis/submission/submission-analysis-summary.json`](docs/analysis/submission/submission-analysis-summary.json)
4. **Review/submission status:** [`docs/analysis/submission-blockers.md`](docs/analysis/submission-blockers.md)
5. **Novelty boundary:** [`docs/analysis/novelty-relationships.md`](docs/analysis/novelty-relationships.md)
6. **Literature map:** [`docs/analysis/literature-map.md`](docs/analysis/literature-map.md)
7. **Identification propositions:** [`docs/analysis/propositions.md`](docs/analysis/propositions.md)
8. **Exact manuscript history:** [`docs/paper/history/`](docs/paper/history/)
9. **Review and role-disclosure record:** [`docs/reviews/`](docs/reviews/)

## What the paper claims

A fixed panel of sixteen lightweight persona prompts passed preregistered **coarse marginal checks**. Corrected variance estimates attribute approximately 85%–96% of episode-level variation to differences between prompt configurations. The two observed aggregate continuation-probability contrasts are +0.083 and +0.078, with conservative exact intervals wide enough that the paper does **not** claim equivalence, a null response, incentive insensitivity, or human substitutability.

The central mechanism-level claim is bounded:

> Coarse marginal checks can be satisfied largely through composition across prompt-conditioned policies that are highly concentrated within recorded cells, while the observed response to the experimental lever remains small and imprecisely estimated.

The paper does not claim that this is the only failure mechanism, that it generalizes to all persona generators, that paired explicit prompts instantiate stable latent people, or that the published human comparator is protocol-matched.

## Corrections reviewers should know before reading

- The broad realism-versus-effect divergence is occupied by prior work; novelty is positioned around the strategic-interaction decomposition, representation experiments, and audit architecture.
- The Dal Bó–Fréchette comparison is protocol-nonmatched and contextual, not an effect-size benchmark.
- The historical P5-1a binary verdict is interval-method-sensitive: restricted counts are 3/32 under the frozen seat rule, 2/32 under the primary exact-episode sensitivity, and 5/32 under a Dirichlet–Jeffreys sensitivity.
- The favored p13 interpretation is withdrawn. Three post-review familywise variants are disclosed: `p=0.059230`, retained non-primary percentile-bootstrap `p=0.043455`, and primary exact-episode `p=0.773206` after p13 is excluded by the gate. None was registered at the original freeze; p13 remains only a replication target.
- The original scope-seal file retains a pre-seal “PROPOSED” header because that exact byte sequence was later hash-sealed. See [`docs/paper/scope-seal-status.md`](docs/paper/scope-seal-status.md).
- Reviewers first diagnosed several defects, then one reviewer helped specify post-adjudication analyses; GitHub Actions executed them against the archived databases, and a later reviewer independently checked the branch. The role transition is disclosed in [`docs/reviews/README.md`](docs/reviews/README.md).

## Reproduce the archived record

```bash
git clone https://github.com/yoheinakajima/synthetic-players
cd synthetic-players/capsule
bash verify.sh
```

Expected result: **4,576/4,576 Phase 4–5 runs replay byte-exact with zero credentials and zero live model calls.**

The zero-call submission analyses are generated from the archived databases by [`.github/workflows/submission-gate-analyses.yml`](.github/workflows/submission-gate-analyses.yml). Their outputs are under [`docs/analysis/submission/`](docs/analysis/submission/), and the current paper figure is under [`docs/paper/figures/`](docs/paper/figures/).

## Highest-value review questions

Please attack these first:

1. **Novelty and framing:** Is the mechanism-level differentiation from Li–Ji, causal-surrogacy work, Lin-style latent drift, persona collapse, state blindness, and direct strategic-game work sufficiently sharp?
2. **Inferential target:** Does the manuscript correctly distinguish fixed-panel, persona-generator, prompt-indexed, and human-substitution estimands?
3. **Response interpretation:** Does Figure 1 make clear that +0.083/+0.078 are small point estimates, not equivalence results or identified upper bounds?
4. **Composition claim:** Is the corrected between-prompt share an appropriate primary description given the interval sensitivity of the binary boundary census?
5. **Audit status:** Are all three post-review p13 variants characterized fairly, including the favorable but non-primary `p=0.043455` result and the absence of pre-compute sealing?
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
