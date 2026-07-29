# Identification propositions — what coarse checks and aggregate moments do not establish

> **STATUS: PAPER-FACING CONCEPTUAL NOTE — NOT VERDICT-BEARING.** Updated 2026-07-29 after external review. No new data and zero subject calls. The notation describes the fixed panel of sixteen explicit persona prompts; interpreting a prompt-indexed contrast as a stable synthetic person’s treatment effect additionally requires latent-person invariance across conditions.

## Setup

Let the binary round-one outcome be

\[
Y_{ijd} \in \{0,1\},
\]

where:

- \(i \in \{1,\ldots,16\}\) indexes the complete explicit persona prompt;
- \(j\) indexes repeated episodes or draws under that prompt;
- \(d \in \{0,1\}\) indexes an experimental condition, such as \(\delta=.10\) versus \(\delta=.90\).

Define the prompt-indexed condition mean

\[
p_i(d)=E[Y_{ijd}\mid i,d].
\]

For the fixed prompt panel, define:

\[
\mu(d)=\frac{1}{16}\sum_i p_i(d)
\]

as the pool mean,

\[
B(d)=\operatorname{Var}_i\{p_i(d)\}
\]

as between-prompt dispersion, and

\[
W(d)=\frac{1}{16}\sum_i p_i(d)\{1-p_i(d)\}
\]

as average within-prompt Bernoulli variation.

For a randomly selected prompt from the fixed panel,

\[
\operatorname{Var}(Y_d)=B(d)+W(d).
\]

Define the prompt-indexed response

\[
\Delta_i^{\text{prompt}}=p_i(1)-p_i(0)
\]

and the aggregate response

\[
\bar\Delta=\mu(1)-\mu(0)=\frac{1}{16}\sum_i\Delta_i^{\text{prompt}}.
\]

The superscript is load-bearing: pairing the same explicit prompt across conditions does not by itself prove that the model instantiated the same latent synthetic individual in both conditions.

## Proposition A — broad marginal bands only partially identify the aggregate response

Suppose a validation protocol accepts the synthetic condition means whenever

\[
\mu^S(0)\in[\ell_0,u_0]
\quad\text{and}\quad
\mu^S(1)\in[\ell_1,u_1].
\]

Then the synthetic aggregate response is constrained only to

\[
\Delta^S
=
\mu^S(1)-\mu^S(0)
\in
[\ell_1-u_0,\;u_1-\ell_0].
\]

Equivalently, if each synthetic condition mean is within a tolerance \(\epsilon_d\) of a human reference mean,

\[
|\mu^S(d)-\mu^H(d)|\le \epsilon_d,
\]

then

\[
|\Delta^S-\Delta^H|
\le
\epsilon_0+\epsilon_1.
\]

### Consequence

Broad condition-level bands may leave the aggregate comparative static only weakly constrained. Their identified interval can contain:

- zero;
- a materially attenuated effect;
- the wrong sign.

The qualifier **coarse** is essential. Exact condition-specific mean matching would force exact aggregate-effect matching by the identity

\[
\Delta=\mu(1)-\mu(0).
\]

The empirical result in this project is therefore not that exact moment matching failed. It is that the registered broad-band checks passed while leaving enough slack for a small internal continuation-probability contrast.

Variance checks do not repair this logical gap unless they impose additional cross-condition structural restrictions.

## Proposition B1 — mean and total variance do not identify the between/within decomposition or shape

Knowing only

\[
\mu(d)
\quad\text{and}\quad
\operatorname{Var}(Y_d)
\]

at a condition does not identify:

- \(B(d)\), the amount of dispersion between prompt configurations;
- \(W(d)\), the amount of variation within a prompt configuration;
- the distribution \(F_d(p)\) of prompt-specific propensities;
- the amount of mass near \(p=0\) or \(p=1\);
- modality, skewness, or other shape features.

The same mean and total variance can arise from sharply different mixtures of stable prompt types and within-prompt stochasticity.

## Proposition B2 — even exact variance components do not identify the full propensity distribution

Suppose \(\mu(d)\), \(B(d)\), and \(W(d)\) are known exactly. Their numerical allocation is then known by definition, but the full distribution of \(p_i(d)\) is still not identified. Multiple propensity distributions can share the same first moments and variance components while differing in:

- endpoint concentration;
- modality;
- tail mass;
- which explicit prompts occupy which regions.

Therefore the empirical corner census contains information not recoverable from a mean and variance comparison alone.

## Proposition B3 — condition-specific marginals do not identify cross-condition coupling

Even knowing the complete marginal distributions

\[
F_0(p)
\quad\text{and}\quad
F_1(p)
\]

does not identify the joint coupling

\[
F_{01}(p_0,p_1)
\]

and therefore does not identify the distribution of

\[
\Delta_i^{\text{prompt}}=p_i(1)-p_i(0).
\]

For example, identical condition-specific multisets of propensities can be paired across prompt identities in multiple ways, yielding different response distributions while preserving every within-condition statistic. Fréchet–Hoeffding bounds constrain possible couplings but do not select one.

Repeated measurements of the same explicit prompt under both conditions provide one observed prompt-indexed coupling. Interpreting that as a stable synthetic individual’s potential-outcome coupling requires an additional assumption:

> **Latent-person invariance:** changing the intervention does not change the unobserved attributes of the synthetic person instantiated by the model.

Recent work on intervention-induced user drift shows that this assumption may fail even when the explicit persona text is unchanged. This project does not test latent-person invariance, so its \(\Delta_i\) quantities should be called **prompt-indexed responses**, not individual human-like treatment effects.

## Empirical mapping for this study

The recorded panel supports direct description of:

- the fixed-panel pool means under each registered condition;
- observed between-prompt dispersion;
- observed within-prompt variation and corner classifications under the historical registered rule;
- prompt-indexed condition contrasts for the same explicit persona strings.

It does **not** by itself identify:

- a population-level estimand for all possible personas;
- human microstructure or a human \(\Delta_i\) distribution;
- stable latent synthetic individuals across interventions;
- human–LLM treatment-effect equivalence.

The Dal Bó–Fréchette human comparator is between-session and protocol-nonmatched. It contextualizes the manipulation but cannot supply a matched distribution of individual responses.

## Statistical-estimation caveat

The observed variance of estimated persona means contains finite-opportunity measurement noise:

\[
\operatorname{Var}_i(\widehat p_i)
\approx
\operatorname{Var}_i(p_i)
+
E_i\!\left[\frac{p_i(1-p_i)}{n_i}\right].
\]

Accordingly, raw cross-persona standard deviations should not be interpreted as latent between-prompt heterogeneity without a hierarchical or bias-corrected sensitivity analysis. The strong observed corner concentration makes the qualitative pattern plausible, but the corrected variance comparison remains a submission requirement.
