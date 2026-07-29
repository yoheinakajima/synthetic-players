# Novelty relationships — occupied territory and precise differentiation

> **STATUS: WORKING LITERATURE NOTE — NOT VERDICT-BEARING.** Updated 2026-07-29 for the paper-facing submission audit. Metadata for recent preprints must be rechecked at submission. This note distinguishes prior claims from this project's narrower contribution; it does not establish priority by itself.

## 1. Closest occupied territory

| Work | What it establishes | Relationship to this paper | Safe differentiation sentence |
|---|---|---|---|
| **Li & Ji (2026), _When simulations look right but causal effects go wrong: Large language models as behavioral simulators_, arXiv:2604.02458.** Three model families, 11 climate-psychology interventions, 59,508 participants in 62 countries, plus two replication datasets. | Descriptive/statistical realism and treatment-effect accuracy are only weakly related; prompt refinements that improve realism need not improve intervention-effect accuracy. | Occupies the broad “realism does not imply effect accuracy” thesis at much larger scale. Our contribution must therefore be mechanism-level and task-specific rather than a first-demonstration claim. | “Li and Ji establish the realism–effect divergence at survey scale; we identify one concrete strategic-interaction pattern through which a lightweight persona panel can pass coarse marginal checks while showing weak response to the registered incentive manipulation.” |
| **Persson, Schultzberg & Ankargren (2026), _Statistical Foundations of LLM-based A/B Testing: A Surrogacy Framework for Human Causal Inference_, arXiv:2606.17165.** | Formalizes assumptions and calibration requirements under which effects on LLM outcomes can identify effects on human outcomes; prior validation does not verify validity for an unobserved intervention. | Supplies the causal-estimand framework. Our propositions are a design-side complement about what broad marginal checks and condition-specific moments do and do not identify. Do not attribute “peaky profiles” to Persson et al. as their own empirical discovery unless the underlying source is cited directly. | “Persson et al. formalize when LLM outcomes can serve as causal surrogates; we provide a registered empirical example in which coarse marginal validation leaves the incentive-response estimand weakly constrained and the microstructure unidentified.” |
| **Lin, Yun, Matarić, Canny, Gretton & D’Amour (2026), _The Illusion of Intervention: Your LLM-Simulated Experiment is an Observational Study_, arXiv:2605.20767.** | Changing an intervention prompt can shift latent attributes of the implied simulated user even when the explicit persona is held fixed, inducing treatment-dependent population drift. | Potentially overlapping rather than excluded. Sealed templates and paired explicit personas rule out accidental assignment/procedure drift, but they do **not** establish latent-person invariance across interventions. | “Lin et al. show that fixed explicit personas need not imply a stable latent synthetic population. We directly decompose behavior in a fixed prompt panel into between-prompt dispersion, within-prompt variation, and incentive response; latent-user drift may coexist with the observed corner-mixture pattern.” |
| **Xie et al. (2026), _Evaluating the statistical realism of LLM-generated social science data_, PNAS 123(19):e2538145123.** | Introduces SSDataBench and shows that sparse-conditioned LLM populations often compress heterogeneity into typological structures, exaggerate associations, and fail to reproduce life-course distributions. | A strong empirical neighbor for distributional collapse and a useful foil: population-level realism is a richer target than simple means, but statistical realism alone is still not human causal surrogacy. | “SSDataBench documents typological compression across social-science variables; we connect an analogous concentration pattern to weak comparative-static response in a preregistered strategic game.” |
| **Harry, Ngong, Nweke, Feng & Near (2026), _Beyond Fixed Psychological Personas: State Beats Trait, but Language Models are State-Blind_, Findings of ACL 2026; arXiv:2601.15395.** | In the Chameleon data, most psychological variation is within-person/state rather than between-person/trait; evaluated LLMs respond weakly to state information. | Strong adjacency for the between/within decomposition. It does not study game-theoretic incentive response or this panel’s corner-mixture construction. | “Harry et al. show that trait-only persona models can miss dominant within-person state variation; we show how a lightweight trait-persona panel can place most observed variation between prompt configurations while remaining weakly responsive to an economic lever.” |
| **Xiao et al. (2026), _The Chameleon’s Limit: Investigating Persona Collapse and Homogenization in Large Language Models_, arXiv:2604.24698.** | Studies persona collapse: nominally distinct persona prompts can converge toward narrow behavioral modes. | Occupies the broad claim that persona diversity can be structurally hollow. Our distinct combination is strategic interaction, a manipulated incentive, quantitative between/within decomposition, prospective registration, and mechanical adjudication. | “Persona-collapse work establishes convergence across nominally diverse profiles; we link a related concentration pattern to a failed incentive-response validation test.” |

## 2. Direct strategic-behavior collisions

| Work | Collision | Differentiation |
|---|---|---|
| **Akata et al. (2025), _Playing repeated games with large language models_, Nature Human Behaviour.** | Repeated strategic games, multiple opponents, and prompt-modulated behavior. | Our paper is not first to place LLMs in repeated games. It adds a fixed persona panel, response-vs-marginal decomposition, prompt-level provenance, prospective registration, and mechanical adjudication. |
| **Pal et al. (2026), _Strategies of cooperation and defection in five large language models_, arXiv:2601.09849.** | Varies continuation probability, payoffs, horizon knowledge, and framing across five LLMs. | Near-direct substantive collision on the manipulation set. Our strongest differentiation is the corner-mixture mechanism in a persona panel and the audit architecture, not the games themselves. |
| **Georgousis et al. (2026), _Evaluating Counterfactual Strategic Reasoning in Large Language Models_, arXiv:2603.19167.** | Alters payoff structures and action labels in PD and RPS to test incentive sensitivity and structural generalization. | D2/D3 should be positioned as a preregistered extension and decomposition, not as the invention of label/payoff counterfactual testing. |
| **Mousavi Davoudi et al. (2026), _Same Game, Different Story_, arXiv:2607.19670.** | Defines strategic robustness as invariance under payoff-preserving narrative changes; secondary analysis reconstructed from published aggregates. | Cite for terminology and the importance of representation families. Our contribution supplies primary registered data, exact prompt provenance, and a persona-pool mechanism. |

## 3. Persona-method and transparency context

- **Batzner et al. (2025/2026), _Whose Personae? A Review of Persona-Based Experiments with Large Language Models_, arXiv:2512.00461.** Reviews 63 peer-reviewed studies and motivates complete persona disclosure and reporting standards.
- **Sclar et al. (2024).** Establishes strong prompt-format sensitivity; cite for the general phenomenon, while presenting X1/X2 as a strategic-game, prospectively registered localization.
- **Shanahan, McDonell & Reynolds (2023).** Role-play/simulacra framing; supports treating the induced policy as configuration-conditional rather than as a stable person.
- **Bisbee et al. (2024).** Survey means can look plausible while variance, regression relationships, and temporal stability fail; a close empirical ally.
- **Hullman et al. (2026), arXiv:2602.15785.** Distinguishes heuristic interchangeability from statistically calibrated use of LLM responses; complementary to this paper’s emphasis on the response surface that must be validated.

## 4. What this paper can and cannot claim as novel

### Defensible novelty

1. A preregistered strategic-interaction demonstration in which a fixed panel of lightweight persona prompts passes **coarse marginal checks** while the registered continuation-probability comparative static remains small.
2. A quantitative decomposition of the observed spread into **between-prompt dispersion**, **within-prompt variation**, and prompt-indexed condition response, revealing widespread empirical corner concentration.
3. A combined representation-and-incentive program that localizes a single-sentence switch and tests semantic-label/payoff conflicts with exact prompt provenance.
4. A research protocol in which predicates, prompt registries, chronology, dispatch, adjudication, replay, and post-adjudication claim downgrades are publicly auditable.

### Claims to avoid

- “First demonstration that realism does not imply treatment-effect accuracy.”
- “The fixed panel is drift-free” or “Lin-style latent-user drift is ruled out.”
- “The human distribution is interior” without matched human microdata and harmonized opportunity counts.
- “Trait factors caused the behavior”; the manipulated confirmatory unit is the complete persona sentence.
- “Exact moment matching failed to recover the aggregate effect”; exact condition-specific mean matching would recover the aggregate difference by identity.
- “One persona proves incentive sensitivity exists in the model”; the p13 slope is a replication target after the nonfinal family audit.

## 5. Suggested related-work paragraph

> Recent work establishes several distinct limits on LLM-based behavioral simulation. Li and Ji show at scale that descriptive realism does not reliably predict treatment-effect accuracy. Persson and colleagues formalize the assumptions and calibration required for LLM outcomes to serve as causal surrogates. Lin and colleagues show that an intervention can alter the implied latent population even when explicit personas are fixed. Statistical-realism and persona-collapse studies further document typological compression and structurally hollow diversity. We contribute a complementary mechanism-level result in strategic interaction: under prospective registration, a fixed explicit panel of lightweight persona prompts passes broad marginal criteria largely through between-prompt composition of empirically corner-concentrated policies, while its response to continuation probability remains weak. This pattern does not exclude latent-user drift; it identifies what is directly visible in the archived prompt-indexed response surface.

## 6. Submission verification checklist

- Reconfirm current versions, author lists, venues, and titles for every 2026 preprint.
- Cite the primary empirical source for any “peaky/stereotyped” profile claim rather than attributing it secondhand through a surrogacy paper.
- Replace placeholder references in the manuscript with a formatted bibliography.
- Keep priority claims tied to externally anchored dates, while acknowledging concurrent work regardless of posting chronology.
