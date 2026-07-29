# Paper submission gate — unresolved analyses and release polish

> **STATUS: ACTIVE PAPER CHECKLIST — 2026-07-29.** This file governs submission readiness only. It does not reopen the sealed research program, authorize new subject calls, or change historical mechanical verdicts. All tasks below are zero-subject-call unless explicitly moved into a separately registered follow-up.

## Gate rule

The paper is submission-ready only when every **blocking** item below is either:

1. completed with generated artifacts committed;
2. removed from the paper together with every dependent claim; or
3. explicitly accepted as a limitation by the human author, with the corresponding language downgraded before submission.

## A. Statistical inference

### A1. Episode-clustered sensitivity — **BLOCKING**

Historical registered analyses counted seat-level round-one trials even though two seats are nested within one episode.

Recompute, using one method declared before viewing the new classifications:

- every P5-1a interiority cell;
- the restricted 3/32 P5-1a fraction;
- every P5-3 clause-(a) interiority gate;
- every load-bearing P5-2 and clause-(b) choice interval.

Minimum deliverables:

- method note and code;
- complete before/after cell table;
- list of verdict-relevant classifications that change;
- paper-language patch preserving the historical registered result while reporting the sensitivity separately.

### A2. p13 family audit — **BLOCKING if p13 remains in main text; otherwise HIGH PRIORITY**

The existing audit used 2,000 permutations, returned \(p=0.0525\) with Monte Carlo SE 0.0050, and substituted a Newcombe lower bound for the registered BCa statistic.

Required final audit:

- use a statistic that can be recomputed identically in observed and permuted data;
- rerun the full interiority-gate plus candidate-selection procedure;
- preserve episode-level arm sizes and the actual randomization structure;
- use at least 100,000 permutations or a sequential Monte Carlo stopping rule;
- report \((r+1)/(B+1)\) and a Monte Carlo confidence interval;
- state the exact family covered by the test;
- keep p13 as a replication target unless the final rule was specified independently of the observed boundary result.

### A3. Between-persona variance correction — **BLOCKING for latent-heterogeneity claims**

Raw variance across estimated persona means includes finite-opportunity measurement noise.

Fit a hierarchical or bias-corrected model and report uncertainty for:

- true between-prompt variance \(B(d)\);
- average within-prompt variance \(W(d)\);
- the ratio \(B/(B+W)\), if used;
- corner mass under declared thresholds.

If this is not completed, restrict the paper to **observed between-persona dispersion** and do not say the panel matches or exceeds human latent heterogeneity.

## B. Human comparator

### B1. Dal Bó–Fréchette microdata contextualization — **BLOCKING only if quantitative human comparison remains prominent**

The comparator is and will remain protocol-nonmatched. Reanalysis cannot make it matched.

Desired views:

- first-supergame behavior;
- pooled experienced behavior;
- late-supergame behavior;
- learning trajectory;
- per-subject endpoint mass and variability;
- opportunity-count-matched or hierarchical variability comparison.

Required caveats:

- different continuation probabilities and payoffs;
- monetary incentives;
- between-session treatment assignment;
- repeated-supergame experience;
- no observed human distribution of individual \(\Delta_i\).

If the package remains unavailable, remove human variance/magnitude language from the abstract and treat the published values as contextual anchors only.

### B2. Matched human arm — **NOT A BLOCKER FOR THIS PAPER’S NARROW CLAIM**

A matched human arm is required for human–LLM equivalence or substitution claims, but not for the internal counterexample that broad checks and weak response coexist in the fixed prompt panel. The current paper must not claim substitutability, equivalence, or a matched human response deficit.

## C. Theory and terminology

### C1. Identification propositions — **BLOCKING**

Use the corrected proposition note:

- broad bands partially identify the aggregate effect;
- mean plus total variance do not identify between/within decomposition or shape;
- even exact variance components do not identify the full propensity distribution;
- condition-specific marginals do not identify cross-condition coupling;
- explicit prompt pairing does not prove latent-person invariance.

### C2. Lin et al. relationship — **BLOCKING**

No living paper or analysis document may state that sealed or seed-matched conditions rule out intervention-induced latent-user drift. Correct statement:

> explicit assignment and execution drift are controlled; latent-person invariance is untested, and Lin-style drift may coexist with the observed corner-mixture pattern.

### C3. Retired language scan — **BLOCKING**

Remove or qualify in living paper-facing documents:

- “not payoff-determined”;
- “fixed, drift-free population”;
- “δ-matched”;
- “fivefold” or “one-fifth human response”;
- “human interior heterogeneity”;
- “deterministic persona” as a policy claim;
- “no game-relevant instruction”;
- p13 as a confirmatory existence result;
- exact moment matching language.

Sealed historical records are never edited; corrections travel beside quotations.

## D. Counts and reproducibility

### D1. Count reconciliation — **BLOCKING**

Create one generated table reconciling:

- episodes/runs;
- seats;
- seat-round decisions;
- round events;
- provider requests;
- replay observations;
- sentinels and other monitoring calls;
- phase-specific versus full-store scope.

Every public count must state its noun and scope. Do not use “subjects,” “observations,” “decisions,” and “calls” interchangeably.

### D2. Reproduction capsule — **COMPLETE, VERIFY AFTER PAPER PATCH**

The current public capsule replays 4,576/4,576 observations anonymously with zero live calls. After paper-facing files are added:

- rerun internal-link checks;
- rebuild the capsule if those documents are intended to ship inside it;
- verify that no sealed artifact hash changed;
- update SHA manifests only through the project’s declared release process.

## E. Literature and novelty

### E1. Final metadata pass — **BLOCKING**

Verify current versions, authors, and venues for all recent works, especially:

- Li & Ji, arXiv:2604.02458;
- Persson et al., arXiv:2606.17165;
- Lin et al., arXiv:2605.20767;
- Harry et al., Findings ACL 2026 / arXiv:2601.15395;
- Xiao et al., arXiv:2604.24698;
- Pal et al., arXiv:2601.09849;
- Georgousis et al., arXiv:2603.19167;
- Same Game, Different Story, arXiv:2607.19670;
- SSDataBench, PNAS DOI 10.1073/pnas.2538145123;
- Whose Personae?, arXiv:2512.00461.

### E2. Bibliography — **BLOCKING**

Replace all bracketed placeholders and “framework 2026” shorthand with a formatted reference list. Cite primary empirical papers for empirical claims; do not attribute a result secondhand through a theory or surrogacy paper.

## F. Paper architecture and repository polish

### F1. Main-text scope — **BLOCKING**

The paper should retain:

- the fixed-panel coarse-check/weak-response result;
- the corner-mixture and between/within decomposition;
- X1/X2 as the clearest representation-dependence mechanism;
- one label/payoff conflict result;
- a concise auditability section;
- the sealed excerpt with a current-status correction table.

p13 remains a short correction/replication-target case, not an abstract or contribution-level result.

### F2. Public navigation — **BLOCKING FOR RELEASE POLISH**

- Link the current full paper draft from README.
- Link the novelty map, literature map, propositions, hierarchy, and this checklist from the analysis index.
- Ensure all relative links resolve.
- Keep “working draft, not for citation” banners on paper-facing artifacts.

## Final human sign-off

Before submission, the human author should approve:

- final title;
- target venue and paper category;
- whether the nonmatched human comparator remains in the abstract;
- whether p13 remains in the main text at all;
- whether unresolved zero-call sensitivities are completed or converted into explicit claim removals;
- final attribution and AI-assistance statement.
