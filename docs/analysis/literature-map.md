# Literature review map — coarse marginal checks, persona mixtures, and incentive response

> **STATUS: WORKING RESEARCH MAP — NOT A BIBLIOGRAPHY AND NOT VERDICT-BEARING.** Updated 2026-07-29 from the supplied review artifact and a submission-gate verification pass. Recent-preprint metadata must be rechecked at submission. Claims below distinguish established territory, direct collisions, analogical lineages, and the paper’s narrower mechanism-level contribution.

## Bottom line

The broad claim that realistic-looking LLM simulations need not recover human intervention effects is already occupied. The paper’s strongest territory is narrower:

> A fixed panel of lightweight persona prompts can pass **coarse marginal checks** largely through between-prompt composition of empirically corner-concentrated policies, while showing weak response to a registered incentive manipulation.

The design’s auditability makes that mechanism unusually credible, but auditability is a credibility layer rather than the empirical novelty itself.

## 1. Closest modern work

### 1.1 Statistical realism versus effect accuracy

- **Li & Ji (2026), arXiv:2604.02458.** Three LLM families, 11 interventions, 59,508 participants in 62 countries, plus two replication datasets. Descriptive/statistical realism is only weakly related to treatment-effect accuracy, and prompt refinements selected for realism can worsen effect estimates. **Implication:** do not claim the first levels-versus-response demonstration; differentiate on mechanism, strategic interaction, and prospective registration.
- **Xie et al. (2026), PNAS, DOI 10.1073/pnas.2538145123.** SSDataBench evaluates 15 LLMs across cross-sectional and longitudinal social-science datasets. Sparse conditioning often compresses heterogeneity into typological structures, exaggerates associations, and fails to reproduce life-event distributions. **Implication:** use as the strongest population-statistics foil and an adjacent empirical account of distributional collapse.
- **Bisbee et al. (2024), Political Analysis.** Synthetic survey averages can look plausible while variation, regression relationships, and temporal stability fail. **Implication:** close empirical ally; our study extends the concern to incentive-bearing strategic interaction and prompt-indexed response surfaces.

### 1.2 Causal surrogacy and calibration

- **Persson, Schultzberg & Ankargren (2026), arXiv:2606.17165.** Formalizes assumptions and calibration under which effects on LLM outcomes can identify effects on human outcomes. Validity for a novel intervention is not established solely by prior validation. **Implication:** use as the formal causal-inference frame; do not present raw LLM effects as human effects.
- **Hullman, Broska, Sun & Shaw (2026), arXiv:2602.15785.** Distinguishes heuristic interchangeability from statistically calibrated use of synthetic responses. **Implication:** calibration is complementary to this paper’s question of which response surfaces should be measured.
- **Prediction-powered inference and related human-in-the-loop methods.** Relevant as alternative architectures: synthetic data may reduce human sample needs without being treated as interchangeable human observations.

### 1.3 Intervention-induced latent-user drift

- **Lin et al. (2026), arXiv:2605.20767.** Changing the intervention can change the implied latent user even when the explicit persona remains fixed. **Implication:** sealed prompts and matched procedures rule out accidental assignment and execution drift, not latent-person drift. The paper’s corner-mixture pattern and Lin’s mechanism may coexist.

### 1.4 Persona collapse and state blindness

- **Harry et al. (2026), Findings of ACL 2026; arXiv:2601.15395.** Chameleon decomposes psychological variation and reports that most variation is within-person/state, while evaluated LLMs respond weakly to state. **Implication:** direct adjacency for the between/within decomposition and a reason not to interpret trait prompts as complete synthetic people.
- **Xiao et al. (2026), arXiv:2604.24698.** Studies persona collapse and homogenization across LLMs. **Implication:** the general claim that persona diversity can be hollow is occupied; our distinction is the manipulated game-theoretic incentive and registered response decomposition.
- **Batzner et al. (2025/2026), arXiv:2512.00461, _Whose Personae?_** Reviews 63 peer-reviewed persona studies and proposes transparency guidance. **Implication:** supports publishing the complete persona table, construction rule, and prompt provenance.
- **Stable Behavior, Limited Variation (2026), arXiv:2604.28048.** Reports high within-persona convergence and limited cross-persona differentiation in urban sentiment tasks. **Implication:** additional empirical neighbor for stable persona-conditioned behavior; verify final metadata before citation.

## 2. Direct strategic-behavior collisions

### 2.1 Repeated games and economic behavior

- **Akata et al. (2025), Nature Human Behaviour.** LLMs play repeated games against models, fixed strategies, and humans; behavior changes with opponent information and prompting. **Collision:** repeated-game LLM behavior and prompt modulation are established.
- **Pal et al. (2026), arXiv:2601.09849.** Five LLMs in repeated Prisoner’s Dilemma, varying continuation probability, payoffs, horizon knowledge, and framing. **Collision:** nearly the same substantive manipulation set. **Differentiation:** persona panel, coarse-marginal versus response decomposition, exact provenance, prospective registration, and mechanical adjudication.
- **Alympics (COLING 2025).** Framework for empirical game-theory research using LLM agents. **Collision:** direct project-space overlap with agents playing strategic games; do not claim to originate LLM empirical game theory.
- **Mei et al. (2024), PNAS.** Compares LLM and human behavior across economic games and reports both similarities and systematic differences. **Implication:** use carefully; aggregate resemblance is not general substitutability.

### 2.2 Payoff, label, and narrative perturbations

- **Georgousis et al. (2026), arXiv:2603.19167.** Counterfactual PD and RPS variants alter action labels and payoff structures, exposing limitations in incentive sensitivity and structural generalization. **Collision:** D2/D3 are not the first label/payoff counterfactual tests.
- **Mousavi Davoudi et al. (2026), arXiv:2607.19670, _Same Game, Different Story_.** Defines strategic robustness as invariance under payoff-preserving framing changes, using secondary analysis of published aggregates. **Collision:** representation robustness terminology and same-game/different-story framing are occupied. **Differentiation:** primary registered observations, exact prompt hashes, minimal-pair localization, and persona-pool mechanism.
- **Liberman, Samuels & Ross (2004).** Community Game versus Wall Street Game demonstrates strong human framing effects at fixed payoffs. **Implication:** human precedent for semantic framing; does not establish that the LLM effect has the same mechanism or magnitude.

### 2.3 Prompt sensitivity

- **Sclar et al. (2024), ICLR.** Large performance changes under subtle prompt-format variation. **Implication:** the general fact that prompts matter is occupied. X1/X2’s distinction is prospective registration, a formally game-equivalent strategic task, and a held-out minimal-span confirmation.
- **Shanahan, McDonell & Reynolds (2023), Nature.** Role-play/simulacra account of LLM behavior. **Implication:** supports defining the experimental object as a model–prompt–deployment configuration rather than an abstract model personality.
- **Lutz et al. (2025), arXiv:2507.16076.** Persona-prompt sensitivity and sociodemographic simulation. **Implication:** direct adjacent work on persona surface dependence.

## 3. Classical lineages that help frame—but do not establish—novelty

### 3.1 Construct validity and assay sensitivity

- **Cronbach & Meehl (1955).** Construct validity rests on a nomological network, not one matching statistic.
- **Campbell & Fiske (1959).** Convergent and discriminant validity across traits and methods.
- **ICH E10; Temple & Ellenberg (2000).** Assay sensitivity: a design pinned at a floor or ceiling cannot support strong equivalence or no-effect conclusions.
- **Measurement invariance.** Relevant to whether the same experimental construct is measured across humans and LLM configurations.

**Use:** This is the cleanest methodological home for the two-sided interiority gate and for separating marginal resemblance from response validity.

### 3.2 Structural versus reduced-form reasoning

- **Lucas (1976).** Policy changes can invalidate reduced-form relationships because behavior adapts to the regime.
- **Invariant Causal Prediction (Peters, Bühlmann & Meinshausen 2016).** Structural relationships should remain invariant across environments.

**Use:** Present as an analogy—a synthetic-subject version of the structural-versus-reduced-form distinction—not as literal econometric estimation or proof of a Lucas critique.

### 3.3 Causal surrogacy

- **Prentice (1989), Frangakis & Rubin (2002), VanderWeele (2013).** A surrogate may correlate with an outcome yet fail to preserve treatment effects.

**Use:** Connect to Persson et al.’s LLM-specific formalization; avoid loose “surrogate paradox” rhetoric unless the mapping is stated precisely.

### 3.4 Agent-based model validation and equifinality

- **Windrum, Fagiolo & Moneta (2007); Grimm et al. (2005).** Matching one aggregate pattern does not establish the correct generative mechanism; multiple patterns help constrain equifinal models.

**Use:** One concise analogy. Do not let the introduction become a catalog of grand frameworks.

## 4. Behavioral-economics comparator lineage

- **Dal Bó & Fréchette (2011).** Canonical continuation-probability evidence in repeated Prisoner’s Dilemma, but the current project’s published comparator is **protocol-nonmatched**: different δ values, payoffs, monetary incentives, between-session treatment assignment, and repeated-supergame experience.
- **Dal Bó & Fréchette (2018).** Broader repeated-game evidence and treatment heterogeneity.
- **Dal Bó (2005).** Shadow-of-the-future evidence.
- **Fudenberg, Rand & Dreber (2012); related strategy-classification work.** Human behavior can involve stable strategy types, so this paper must not assume human subject-level distributions are smoothly interior.

**Required framing:** The human literature contextualizes the manipulation. It does not supply a matched human effect or a human distribution of individual $\Delta_i$ for this design.

## 5. Metascience and reproducibility lineage

- **Nosek et al. (2018); Registered Reports.** Preregistration and separating prediction from post-result interpretation.
- **Simmons, Nelson & Simonsohn (2011); Gelman & Loken; Kerr (1998).** Researcher degrees of freedom, forking paths, and HARKing.
- **OpenTimestamps / Gipp et al. (2015).** External chronology anchoring.
- **Chen, Zaharia & Zou (2023).** Deployed model behavior can change over time, motivating behavioral sentinels.
- **AI Scientist and critiques.** Adjacent context for autonomous or agentic research pipelines.

**Distinct contribution:** the repository operationalizes these ideas into prompt registries, event sourcing, mechanical predicates, exact replay, and an explicit record of a post-adjudication inference downgrade. The correct claim is not that the pipeline guarantees validity; it makes procedural history and inferential failures inspectable.

## 6. The paper’s defensible novelty triangle

1. **Empirical claim:** a fixed panel of lightweight persona prompts passes preregistered coarse marginal checks while the continuation-probability response remains small.
2. **Mechanism-level pattern:** observed dispersion is carried largely by between-prompt composition of empirically corner-concentrated policies, with low observed within-prompt variation in many cells.
3. **Credibility layer:** prospective registration, exact prompt provenance, event-sourced replay, mechanical adjudication, and public post-adjudication correction.

Do not include the p13 slope as a corner of the novelty triangle. Its current status is a preregistered replication target after a nonfinal family-level audit.

## 7. Terminology map

### Inherit from the literature

- LLM social simulation
- synthetic participants / AI surrogates (for the broader literature)
- persona-conditioned LLM configuration (for this study’s units)
- prompt sensitivity / representation robustness
- counterfactual strategic reasoning
- assay sensitivity
- statistical calibration / causal surrogacy
- between-person and within-person variation
- treatment-effect accuracy

### Use as paper-specific descriptive language, not priority claims

- coarse marginal checks
- comparative-static fidelity
- corner-mixture pattern or corner-mixture failure mode
- prompt-indexed response surface
- control-channel interactions
- procedurally exact, inferentially fallible

### Avoid

- human-like without a declared dimension
- δ-matched human comparator
- fivefold human response failure
- deterministic policy (use zero observed within-cell variation / empirically corner-concentrated)
- fixed, drift-free synthetic population
- “not payoff-determined” (use semantic cues can override payoff dominance in conflict cells)
- trait causality from the sixteen complete persona sentences

## 8. Must-resolve before submission

1. Replace every citation placeholder with verified metadata and a formatted reference.
2. Recheck all 2026 preprint versions and venue status.
3. Attribute empirical distribution-collapse evidence to the primary empirical paper, not secondhand through a surrogacy paper.
4. Keep Li–Ji, Persson, Lin, Xie et al., Harry et al., persona-collapse work, Pal et al., Georgousis et al., and Same Game/Different Story in the explicit collision section.
5. Keep the human comparator labeled nonmatched even after microdata reanalysis.
6. Ensure no related-work sentence implies that matched explicit prompts establish latent-person invariance.
