# Reviewer entry point

> **CURRENT REVIEW SURFACE:** PR #2, branch `agent/submission-gate-polish`. The manuscript is ready for full scientific review, but remains a working draft and should not be cited.

Thank you for reviewing **Synthetic Players**. Everything needed to evaluate the manuscript, analyses, chronology, and reproduction claims is public in this repository. No private bundle or outside explanation is required.

## Start here

1. **Manuscript:** [`docs/paper/paper-draft.md`](docs/paper/paper-draft.md)
2. **Independent verification memo:** [`docs/reviews/round-3-independent-verification.md`](docs/reviews/round-3-independent-verification.md)
3. **Machine-readable submission-analysis summary:** [`docs/analysis/submission/submission-analysis-summary.json`](docs/analysis/submission/submission-analysis-summary.json)
4. **Submission status:** [`docs/analysis/submission-blockers.md`](docs/analysis/submission-blockers.md)
5. **Novelty boundary:** [`docs/analysis/novelty-relationships.md`](docs/analysis/novelty-relationships.md)
6. **Literature map:** [`docs/analysis/literature-map.md`](docs/analysis/literature-map.md)
7. **Identification propositions:** [`docs/analysis/propositions.md`](docs/analysis/propositions.md)

## What the paper now claims

A fixed panel of sixteen lightweight persona prompts passed preregistered **coarse marginal checks**. Corrected variance estimates attribute approximately 85%–96% of episode-level variation to differences between prompt configurations. The two observed aggregate continuation-probability contrasts are +0.083 and +0.078, with conservative exact intervals wide enough that the paper does **not** claim equivalence, a null response, or human substitutability.

The central mechanism-level claim is therefore bounded:

> Coarse marginal checks can be satisfied largely through composition across prompt-conditioned policies that are highly concentrated within recorded cells, while the observed response to the experimental lever remains small.

The paper does not claim that this is the only failure mechanism, that it generalizes to all persona generators, or that paired explicit prompts instantiate stable latent people.

## Corrections reviewers should know before reading

- The broad realism-versus-effect divergence is occupied by prior work; novelty is positioned around the strategic-interaction decomposition, representation experiments, and audit architecture.
- The protocol-nonmatched Dal Bó–Fréchette comparison is contextual, not an effect-size benchmark.
- The historical P5-1a binary verdict is interval-method-sensitive: restricted counts are 3/32 under the frozen seat rule, 2/32 under the primary exact-episode sensitivity, and 5/32 under a Dirichlet–Jeffreys sensitivity.
- The favored p13 interpretation is withdrawn. Three post-review familywise variants are all disclosed: `p=0.059230`, retained non-primary percentile-bootstrap `p=0.043455`, and primary exact-episode `p=0.773206` after p13 is excluded by the gate. None was registered at the original freeze; p13 remains only a replication target.
- The original scope-seal file retains a pre-seal “PROPOSED” header because that exact byte sequence was subsequently hash-sealed. See [`docs/paper/scope-seal-status.md`](docs/paper/scope-seal-status.md).

## Reproduce the archived record

```bash
git clone https://github.com/yoheinakajima/synthetic-players
cd synthetic-players/capsule
bash verify.sh
```

Expected result: **4,576/4,576 Phase 4–5 runs replay byte-exact with zero credentials and zero live model calls.**

The zero-call submission analyses are generated from the archived databases by [`.github/workflows/submission-gate-analyses.yml`](.github/workflows/submission-gate-analyses.yml). Their outputs are under [`docs/analysis/submission/`](docs/analysis/submission/).

## Highest-value review questions

Please attack these first:

1. **Novelty and framing:** Is the mechanism-level differentiation from Li–Ji, causal-surrogacy work, Lin-style latent drift, persona collapse, and state blindness sufficiently sharp?
2. **Inferential target:** Does the manuscript correctly distinguish fixed-panel, persona-generator, prompt-indexed, and human-substitution estimands?
3. **Response interpretation:** Does Figure 1 make clear that the observed +0.083/+0.078 differences are small point estimates, not equivalence results?
4. **Composition claim:** Is the corrected between-prompt share an appropriate primary description given the interval sensitivity of the binary boundary census?
5. **Audit status:** Are all three post-review p13 variants characterized fairly, including the favorable but non-primary `p=0.043455` result and the absence of pre-compute sealing?
6. **Scope:** What should be cut from the main paper, and what important result has been over-demoted?

## How to respond

Review the pull request directly or open an issue. The most useful order is:

1. novelty/framing;
2. statistics and estimands;
3. missing literature or contrary evidence;
4. structure and cuts;
5. line edits.

Please distinguish a proposed reinterpretation of the living manuscript from a requested change to a sealed historical artifact. Sealed records are preserved; corrections travel beside them.
