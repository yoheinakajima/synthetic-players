# Sample hierarchy, counting units, and estimands

> **STATUS: DOCUMENTATION — PAPER-FACING REVISION, 2026-07-29.** Zero subject calls. Counts are generated from the recorded event store and sealed arm/persona files. Historical registered analyses are not rewritten; this document separates their counting unit from the dependence cluster and names the outstanding submission sensitivities.

## Hierarchy (Phase 5 exact recorded counts)

| level | definition | count |
|---|---|---:|
| deployment | model × provider configuration; GPT-4.1 is the primary confirmatory deployment and the cross-vendor lane is descriptive | 1 primary |
| explicit persona prompt | one complete sealed sentence prepended as a system prefix | 16, plus bare/no-prefix control |
| condition/cell | game × continuation probability × wording × swap surface | 6 distinct cells; 160 arms after persona and temperature expansion |
| episode/run | one seeded game execution | 1,712 valid completed Phase 5 episodes |
| seat | one player position within an episode | 2 per episode; both seats use the subject configuration |
| round | one simultaneous move pair | 54,276 round events recorded across the current store |
| provider request/call | one archived LLM request | 36,251 `llm.requested` events recorded across the current store |
| replay observation | one archived observation included in the public full-program replay contract | 4,576 |

These nouns are not interchangeable. Calls and seat-round decisions describe operational scale; they are not independent subjects.

## Counting unit versus dependence cluster

The historical registered rules sometimes counted seat-level binary trials because both seats produced choices. Two seats nevertheless share an episode-level game instance and may be dependent. The public paper must distinguish:

1. **Registered counting unit:** the observations used by the frozen historical predicate.
2. **Dependence cluster:** the unit resampled or modeled together in a sensitivity analysis.
3. **Target estimand:** fixed configuration, fixed persona panel, or a wider persona population.

| claim/family | historical registered calculation | plausible dependence cluster | paper status / required sensitivity |
|---|---|---|---|
| P5-1a interiority | Clopper–Pearson interval on seat-level round-one trials, \(n=2\times\)episodes | episode | Historical verdict retained. Reclassify all load-bearing cells using an episode-clustered method before submission; report whether the fragile 3/32 result changes. |
| P5-1b dispersion | standard deviation of estimated persona–cell means | complete persona prompt, with each mean estimated from finite episodes | Historical descriptive comparison retained. Fit a hierarchical or bias-corrected model to separate true between-prompt dispersion from estimation noise before interpreting latent heterogeneity. |
| P5-2 conflict cells | pooled seat-level round-one choice share | episode within conflict cell | Publish historical result plus episode-clustered intervals; mechanism remains word/payoff-confounded regardless of sampling precision. |
| P5-3 clause (a) | two-sided seat-level interiority gate followed by a one-sided slope lower bound for each candidate; existence claim fires on any pass | episode within persona × wording × δ cell; candidate family above it | Historical mechanical verdict retained. Final family audit must rerun the full gate-and-selection rule with an episode-aware statistic and adequate Monte Carlo precision. |
| P5-3 clause (b) | seat-level Clopper–Pearson lower bound on refusal share; existence form over persona × temperature lanes | episode within lane | Bonferroni sensitivity is statistically strong under the historical count, but an episode-clustered interval is still required. Construct confound is independent of this sensitivity. |
| P5-4 temperature | changes in interiority across persona–cell units | persona × cell at fixed temperature, with repeated episodes beneath it | Treat confirmatory verdict as fixed-panel. Population-level trait claims remain exploratory at \(n=16\). |

## Recommended episode-level outcome

For one-shot or round-one self-play, define

\[
Y_e=\frac{Y_{e1}+Y_{e2}}{2}\in\{0,0.5,1\}.
\]

Episode-aware inference can then use one of the following declared methods:

- nonparametric bootstrap resampling complete episodes;
- randomization/permutation at the episode level while preserving arm sizes;
- a generalized estimating equation or hierarchical model with episode as a cluster;
- exact analysis on the three-valued episode outcome when feasible.

The sensitivity method should be chosen before inspecting whether it preserves the fragile classification.

## The two estimands

### 1. Conditional finite-panel estimand

Properties of **these sixteen complete explicit persona prompts** under the registered deployment, task representations, and execution windows. All historical Phase 5 predicates attach here. Personas are fixed configurations; names, ages, occupations, and trait descriptors are all part of the treatment bundle.

Safe language:

> “In the fixed panel of sixteen registered persona prompts…”

### 2. Persona-population estimand

Properties of a wider persona generator or class of lightweight trait-persona prompts. Here the persona prompt is the higher-level sampling unit and \(n=16\) is small; three binary trait factors are aliased with names, ages, occupations, and wording. Claims about “persona pools” in general are exploratory unless separately sampled and powered.

Safe language:

> “The fixed panel illustrates one failure mode that a lightweight persona-pool construction can exhibit.”

## Prompt identity versus latent-person identity

The same explicit persona prompt is reused across conditions, enabling a **prompt-indexed response**:

\[
\Delta_i^{\text{prompt}}=p_i(1)-p_i(0).
\]

This does not prove that the LLM instantiated the same latent synthetic individual under both interventions. A person-level causal reading requires latent-person invariance, which this study does not test. Accordingly, the paper should use **prompt-indexed response** rather than individual treatment effect when discussing personas.

## Reporting rule

Every paper table and figure should state:

- deployment/model configuration;
- explicit prompt or persona unit;
- number of independent episodes;
- seat and round counts, if shown descriptively;
- historical counting unit;
- dependence cluster used for inference;
- fixed-panel versus persona-population estimand;
- whether the result is historical confirmatory, post-adjudication sensitivity, or exploratory.
