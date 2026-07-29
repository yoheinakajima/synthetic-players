# Passing Coarse Marginal Checks Can Be Cheap: Corner Mixtures and Weak Incentive Response in Persona-Conditioned LLMs

**STATUS: WORKING DRAFT v4 — PRE-PUBLICATION, NOT FOR CITATION.** This paper-facing revision incorporates the completed zero-call submission analyses while leaving every sealed registration, adjudication, report, and precommitted discussion artifact unchanged. §5.2 quotes an exact excerpt of a discussion text sealed and externally timestamped before the final experiment's data existed (sha `1f1d7de9…e356`); the full sealed text remains in the supplement and is not edited. Appendix A documents material cut or demoted and the correction ledger.

**Author:** Yohei Nakajima (Untapped Capital). Experiments executed by an autonomous pipeline (Replit Agent + ActiveGraph event-sourced engine). Attribution: §8.

**Artifacts (public):** github.com/yoheinakajima/synthetic-players — anonymous clone + one-command zero-credential verifier; 4,576/4,576 Phase 4–5 runs replay byte-exact; registries hashed and externally anchored (GitHub timestamps + OpenTimestamps/Bitcoin).

---

## Abstract

Large language models are increasingly used as synthetic research participants, but they are often validated by whether their marginal responses resemble published human data. We report a five-phase prospectively registered program using a fixed panel of sixteen lightweight persona-conditioned GPT-4.1 configurations in strategic games. The panel passed preregistered broad-reference checks for condition-level cooperation in three of four repeated-game cells, yet changing continuation probability from 0.10 to 0.90 changed aggregate round-one cooperation by at most 0.08. Correcting raw cross-persona dispersion for finite episode counts leaves estimated between-prompt standard deviations of 0.418–0.478 and attributes approximately 85%–96% of episode-level variation to differences between prompt configurations. Cell-level corner classification is method-sensitive: the historical seat-level rule classified 14/96 cells interior, a conservative exact episode-level interval classified 11/96, and a Dirichlet–Jeffreys sensitivity classified 19/96. Thus the threshold verdict is not invariant, but every analysis finds that most observed variation lies between prompt configurations rather than within them. Separate representation experiments showed that one continuation sentence shifted cooperation from 0/40 to 37/40 on held-out decisions and that semantic action labels could override payoff dominance in a registered conflict condition. These findings identify a concrete failure mode: coarse marginal checks can be satisfied largely through composition across stable prompt-conditioned policies while response to the experimental lever remains weak. All claims were prospectively registered and mechanically adjudicated from an event-sourced record; external review later exposed a family-error defect and a seat-dependence problem, both now analyzed without changing the historical record. Human references are published and protocol-nonmatched, the results concern one fixed model–persona panel, and we do not claim human substitutability.

## 1. Introduction

Human behavioral experiments are slow and expensive; LLM calls are fast and nearly free. A growing literature reports that suitably conditioned LLMs produce data resembling human data — "algorithmic fidelity" [Argyle et al. 2023], "homo silicus" [Horton 2023], behavior "statistically indistinguishable from a random human" [Mei et al. 2024] — and a flagship formalization of *statistical realism* as the validation target now exists [Xie et al. 2026]. Much of this evidence validates marginals: means, distributions, and aggregate replication.

Recent work shows that descriptive realism and causal fidelity can diverge at scale [Li & Ji 2026], that treating LLM outcomes as surrogates for human outcomes requires assumptions that marginal equivalence does not supply [Persson et al. 2026], and that intervention prompts can shift the model's implied latent user even when explicit persona text is held fixed [Lin et al. 2026]. Our contribution is not the divergence itself but a controlled mechanism-level decomposition in strategic interaction: **a commonly used lightweight persona construction passes coarse marginal checks while the incentive comparative static stays weak, and its observed dispersion is carried primarily by differences among prompt-conditioned policies concentrated near behavioral boundaries.** Sealed templates and matched procedures rule out accidental changes in explicit persona assignment, environment randomization, and execution. They do not establish latent-person invariance across interventions; Lin-style user drift and the observed composition pattern can coexist.

The failure pattern has formal ancestors worth naming as analogues rather than identities. In econometrics it resembles the reduced-form/structural distinction sharpened by the **Lucas critique** [Lucas 1976]: a fit to aggregates need not survive movement of a policy lever. Here, continuation probability is the lever, and persona conditioning produces the coarse fit. In psychometrics it is a **construct-validity** problem [Cronbach & Meehl 1955]: a synthetic subject is not validated by one resemblance statistic but by behaving correctly across a nomological network, with **assay sensitivity** [ICH E10; Temple & Ellenberg 2000] naming the precondition enforced by an interiority gate. In causal inference it connects to the **surrogate-outcome** problem [Prentice 1989; VanderWeele 2013], now formalized for LLM outcomes [Persson et al. 2026]. Agent-based modeling's equifinality provides a related aggregate-pattern analogy [Windrum et al. 2007; Grimm et al. 2005].

**Contributions.** (1) A fixed persona panel passes preregistered coarse marginal checks while its continuation-probability comparative static stays ≤0.08 (§4.1). (2) A corrected decomposition shows that 85%–96% of observed episode-level variation lies between prompt configurations; the binary corner census is interval-method-sensitive, which we report rather than resolve selectively (§4.1–4.2). (3) We formalize what broad marginal bands, variance components, and condition-specific distributions do and do not identify (§4.2). (4) We map control-channel interactions through a single-sentence switch and a semantic-label/payoff conflict (§4.3). (5) We demonstrate a reliability protocol that is procedurally exact, extensively auditable, and inferentially fallible: external review overturns the paper's favored persona-level interpretation without rewriting the frozen record (§4.4–4.5).

## 2. Related work

**Occupied territory, and where we sit.** Li and Ji [2026] establish across three model families, eleven interventions, and 59,508 participants that descriptive fit and intervention-effect accuracy can diverge, and that prompt refinements improving realism do not reliably improve effect accuracy. Persson, Schultzberg, and Ankargren [2026] formalize when LLM outcomes can serve as causal surrogates and why novel interventions still require human evidence. Lin et al. [2026] show that intervention prompts can change the implicit simulated population even when explicit personas are fixed. Statistical-realism, persona-collapse, and state-versus-trait work further show that persona-conditioned populations can compress or misallocate heterogeneity [Xie et al. 2026; Harry et al. 2026; Xiao et al. 2026]. Our differentiation is narrower: in incentive-bearing strategic interaction, under prospective registration, we decompose a fixed explicit prompt panel into between-prompt dispersion, within-prompt variation, and incentive response. The observed composition pattern is complementary to, not exclusive of, latent-user drift.

**LLM strategic behavior (direct collisions).** Akata et al. [2025] characterize repeated-game play modulated by prompts; Pal et al. [2026] elicit strategies from five models while varying continuation probability, payoffs, horizon knowledge, and framing; counterfactual-reasoning evaluations alter labels and payoff structures [Georgousis et al. 2026]; and "strategic robustness" has been defined as payoff-preserving invariance across narratives [Mousavi Davoudi et al. 2026]. These works establish that neither repeated games nor prompt/payoff perturbations are new. Our distinct combination is a fixed persona panel, an explicit between/within/response decomposition, prospective registration, exact prompt provenance, and mechanical adjudication followed by public inferential correction.

**Synthetic participants and personas.** Bisbee et al. [2024] find plausible survey averages alongside compressed variance, distorted coefficients, and temporal drift; Boelaert et al. [2025] report excess homogeneity; Anthis et al. [2025] catalog diversity and generalization challenges; Hullman et al. [2026] propose statistical calibration for confirmatory use; and Park et al. [2024] show that rich interview conditioning can substantially outperform lightweight demographic/persona descriptions. Format sensitivity [Sclar et al. 2024], role-play framing [Shanahan et al. 2023], persona collapse [Xiao et al. 2026], state blindness [Harry et al. 2026], and reviews of persona-experiment transparency [Batzner et al. 2025] all caution against treating a persona string as a stable human analogue. RLHF-related diversity reduction is a possible mechanism for concentrated policies, not a mechanism identified by this design. Full map: `docs/analysis/literature-map.md`; differentiation table: `docs/analysis/novelty-relationships.md`.

## 3. Instrument and inferential units

The primary deployment is gpt-4.1 at temperature 0.7 with 16-token outputs and a fixed minimal behavioral-subject prompt containing no game-theory vocabulary or reasoning scaffold. Phase 5 prepends one sealed persona sentence to byte-identical task text, giving every persona cell an exact bare twin. The cross-vendor Gemini tier is descriptive; the original Claude Haiku candidate failed a registered entry gate and was replaced under an archived amendment. Environment randomness is seeded; provider-side generation is not claimed to be seeded. Every request, rendered prompt, completion, decoding configuration, round, and provenance record is archived.

The full event store contains 5,505 completed runs, 54,276 round events, 108,552 seat-round decisions, and 36,251 archived provider-request events. The public Phase 4–5 replay contract covers 4,576 completed runs. A separate transactional ledger records 30,530 Phase 4–5 calls, 13,141,675 input tokens, and 45,247 output tokens; it excludes earlier phases and therefore must not be conflated with the full event-store request count. Counts and definitions are reconciled in `docs/analysis/submission/count-reconciliation.md`.

Claims were structured predicates registered before their evidence and mechanically adjudicated in a fixed vocabulary. The historical two-sided interiority rule used Clopper–Pearson bounds on seat-level round-one trials. Because two seats share an episode, the submission analysis additionally treats the complete episode as the independence unit. For an episode outcome \(Y\in\{0,0.5,1\}\), the primary exact sensitivity writes

\[
Y=\tfrac12\{\mathbf 1(Y\ge0.5)+\mathbf 1(Y=1)\},
\]

constructs simultaneous Clopper–Pearson intervals for the two episode-level binary components, and projects them onto \(E[Y]\). This is conservative but does not assume independence between seats and does not collapse to zero uncertainty when all observed episodes agree. A Dirichlet–Jeffreys interval is reported as a Bayesian sensitivity. The initially generated percentile cluster bootstrap is preserved in the audit trail but rejected as primary because it becomes degenerate at exact corners.

The hierarchy is deployment → explicit persona prompt → condition → episode → seat → round → provider request. Phase 5's confirmatory unit is the complete persona sentence; name, age, occupation, and traits are all bundled semantic treatments. Registered claims attach to the conditional finite-panel estimand for these sixteen prompts. Claims about the wider persona generator are exploratory at \(n=16\). Pairing the same explicit prompt across conditions identifies a prompt-indexed contrast, not necessarily a stable latent person's treatment effect.

The machinery's boundary is explicit:

> **The pipeline can enforce a registered predicate exactly; it cannot guarantee that the predicate represents a valid estimand, test family, or construct.**

## 4. Results

### 4.1 Coarse marginal checks pass while the incentive response stays weak

The preregistered leaning rule (at least two of agreeable, patient, and risk-averse) separates round-one cooperation by 0.5–0.7 in every non-swap cell. Because names, ages, occupations, and all trait descriptors vary in the complete sentence, this is a property of the registered prompts rather than a causal trait estimate. Pool means of 0.349–0.505 enter the published cooperation band in three of four repeated-game cells.

Raw cross-persona standard deviations range from 0.4241 to 0.4800. Correcting for finite episode counts leaves fixed-panel between-prompt SD estimates of 0.4182, 0.4784, 0.4408, 0.4323 across the four repeated cells. The primary bootstrap retains all sixteen registered prompts and resamples episodes within prompt; its 95% intervals are [0.4122, 0.4391], [0.4696, 0.4916], [0.4279, 0.4654], [0.4269, 0.4496]. The corrected between-prompt component accounts for 85.5%, 96.1%, 88.8%, 90.2% of total episode-level variation, with fixed-panel 95% intervals [82.0%, 93.8%], [94.6%, 98.9%], [86.7%, 94.6%], [87.9%, 95.5%]. All four fixed-panel lower bounds exceed the historical registered threshold of 0.75 times the published human SD. An exploratory two-stage bootstrap that additionally resamples prompts produces wider corrected-SD intervals of [0.2724, 0.4879], [0.3696, 0.5123], [0.3457, 0.4890], [0.3345, 0.4847]; 3/4 lower bounds exceed the historical threshold. These are fixed-panel prompt-heterogeneity estimates and exploratory persona-generator sensitivities, not matched human latent variances.

Across the continuation-probability manipulation, aggregate round-one cooperation moves by no more than 0.08 in any wording family. Dal Bó and Fréchette [2011] provide a useful but protocol-nonmatched comparator: their treatments use different continuation probabilities and payoffs, monetary incentives, between-session assignment, and repeated supergames through which human behavior changes with experience. Their pooled experienced contrast is substantially larger, while first-supergame ordering reverses. We therefore make no matched magnitude or human-equivalence claim. The load-bearing result is internal: **the same fixed prompt panel that passes the registered coarse checks exhibits only a small response to the registered incentive manipulation.**

The historical seat-level interiority rule classified 14/96 persona–condition cells as interior and 3/32 in the restricted P5-1a set, just below the registered 0.10 threshold. The primary exact episode-level interval classifies 11/96 cells as interior and 2/32 in the restricted set. A Dirichlet–Jeffreys sensitivity classifies 19/96 and 5/32, respectively, which would fail the historical threshold. Thus the binary P5-1a verdict is method-sensitive. The continuous composition result is more stable: under all three interval approaches, most cells are non-interior, and the measurement-error-corrected variance decomposition assigns the large majority of observed variation to differences between prompt configurations.

### 4.2 What the marginal checks cannot identify

Let \(p_i(d)=E[Y\mid i,d]\), where \(i\) indexes the complete explicit persona prompt and \(d\) the experimental condition.

**Proposition A: broad bands only partially identify the aggregate contrast.** If a synthetic condition mean is accepted within tolerance \(\epsilon_d\) of a reference mean in each condition, then

\[
|\Delta^S-\Delta^H|\le \epsilon_0+\epsilon_1.
\]

Equivalently, accepted bands \([\ell_0,u_0]\) and \([\ell_1,u_1]\) imply only

\[
\Delta^S\in[\ell_1-u_0,u_1-\ell_0].
\]

Exact condition-specific mean matching would force the aggregate effect by the identity \(\Delta=\mu_1-\mu_0\); the empirical failure lives in the slack of coarse criteria.

**Proposition B: aggregate moments do not identify microstructure or response coupling.** Mean and total variance do not identify how variation is divided between prompt configurations and repeated draws, nor do they identify distributional shape or boundary concentration. Even exact condition-specific distributions do not identify the cross-condition coupling and therefore do not identify the distribution of prompt-indexed responses \(\Delta_i=p_i(1)-p_i(0)\). Reusing an explicit persona string supplies one prompt-indexed coupling, but interpreting it as a stable synthetic individual's potential-outcome contrast requires latent-person invariance, which this study does not test.

The study therefore identifies a composition pattern in one fixed prompt panel. It does not establish that humans have a different microstructure, that RLHF caused the pattern, that latent-user drift is absent, or that the same pattern occurs across persona generators.

### 4.3 Control-channel interactions

For the bare configuration, round-one cooperation was 0.000 at every registered continuation probability. A single continuation sentence, localized through a span ladder and confirmed on fresh seeds, moved held-out cooperation from 0/40 to 37/40. The same wording factor was null in one-shot play, showing that text effects depend on the context in which a phrase has a strategic referent.

In the label-swap conflict cell, the canonical payoffs were held fixed while the displayed words "Cooperate" and "Defect" were attached to the opposite strategic roles. The bare configuration selected the cooperation-worded option 0/40 times, choosing the strictly dominated role whenever it carried the word "Defect," while responding strongly to payoff changes when semantic labels did not oppose them. The supported statement is conditional: **semantic labels can override payoff dominance in direct conflict; payoff sensitivity is representation-dependent, not absent.**

Personas add separable presence and direction effects. Direction produces the 0.5–0.7 leaning gaps. Presence reverses the bare swap-cell choice: all sixteen personas overwhelmingly select the cooperation-worded/payoff-dominant option. The choice result is statistically strong but mechanism-confounded because word and payoff point to the same action. Under the episode-exact analysis, all 24 evaluable persona × temperature lanes retain a simultaneous familywise lower bound above the registered 0.20 threshold; the minimum is 0.462. This establishes the choice pattern, not whether it is driven by incentives or lexical attraction.

The pooled P5-2 task-consistent share is 0.128 with an exact episode-level 95% interval [0.092, 0.172], retaining the historical persona-dominant classification. But every repeated-game conflict subcell is mixed under the exact episode interval. Only the swap cell is individually persona-dominant, with a task-consistent share of 0 and interval [0, 0.027]. The pooled verdict is therefore carried entirely by the same word/payoff-confounded cell. We describe these findings as **control-channel interactions**, not a fixed hierarchy.

### 4.4 The favored persona-level result does not survive episode-level inference

Under the historical seat-level rule, persona p13 moved from 0.333 cooperation at δ=.10 to 0.750 at δ=.90 and passed a per-candidate lower-bound test. The rule searched multiple persona × wording candidates and fired on any pass without declared family-level error control. External review identified that defect.

A final 200,000-permutation audit reruns the complete gate-plus-maximum-selection procedure over all 32 evaluable clause-(a) candidates using the same raw-slope statistic in observed and permuted data. Under the historical seat-level gate, p13 remains the maximum at +0.4167, but the familywise permutation result is \(p=0.0592\), Monte Carlo 95% interval [0.0582, 0.0603]. Under the primary episode-exact gate, p13 is not interior: its low-δ lower bound falls below 0.05 and its high-δ upper bound exceeds 0.95. Only p04/s2p and p05/s2a pass both episode-level gates; the largest surviving positive slope is p05's +0.0833, with familywise \(p=0.7732\). The archived data therefore do not support an unconfounded persona-level incentive-response existence claim under episode-level inference.

The historical mechanical P5-3 verdict remains part of the sealed record because clause (b) fires strongly and p13 passed the rule as frozen. The scientific interpretation changes: p13 is a replication target, not a finding, and the capability-envelope interpretation selected by the precommitted branch is no longer supported by clause (a). This is the program's first post-adjudication inferential downgrade, categorically distinct from predictions refuted by new data.

### 4.5 Auditability

Twelve registered author predictions were refuted by data and published. Four underspecified analysis choices were resolved outcome-blind. A two-sided gate blocked a false ceiling conclusion. Sentinels detected a time-indexed behavioral discontinuity in an unversioned endpoint and exposed a monitoring gap that was repaired with an attestation gate. The public capsule replays all 4,576 Phase 4–5 runs exactly with zero live model calls. External review then found the family-error and dependence defects discussed above; the archived record made both diagnosable and correctable.

The claim is bounded: the machinery is procedurally exact and extensively auditable. Its strongest achievement is not self-validation but preservation of enough provenance for outsiders to identify where procedural correctness stopped short of statistical validity.

## 5. Discussion

### 5.1 Implications

For synthetic-participant practice, broad marginal resemblance is a weak validation target. Lightweight conditioning can generate plausible aggregate levels and substantial cross-prompt dispersion while leaving response to an economic lever small. Validation should therefore report the response surface over declared interventions and representation families, together with assay-sensitivity checks, dependence-aware uncertainty, model/provider provenance, and temporal monitoring. Statistical calibration [Hullman et al. 2026], causal-surrogacy assumptions [Persson et al. 2026], and latent-drift diagnostics [Lin et al. 2026] are complementary rather than competing safeguards.

The results also show why binary certification language should be used sparingly. The historical P5-1a predicate passes under its frozen seat-level rule and under the conservative episode-exact interval, but fails under a reasonable Dirichlet–Jeffreys sensitivity. The underlying continuous evidence is clearer than the binary gate: prompt identity explains most observed variation, many cells lie at or near behavioral boundaries, and the continuation-probability response remains small. A valid standard should privilege those quantities over one thresholded label.

For deployment, behavior that can be rewritten by a sentence, an action token, or an identity prefix is a safety-relevant property. But the present results do not imply that language always dominates incentives: in some cells numerical payoffs move behavior strongly, and precedence depends on the representation and conflict structure.

### 5.2 The precommitted discussion, and what changed after review

The Phase 5 discussion was sealed before its data existed. Excerpt (full text in supplement; sha `1f1d7de9…e356`):

> "The headline of Phase 5 is an existence result the program registered against itself: at least one persona in the sealed sixteen passed the two-sided assay gate and showed the registered signature of incentive sensitivity. The author's registered prediction — that none would — is refuted, and the refutation is the finding. … The capability was recoverable by content-side conditioning… The scope of the claim is deliberately narrow."

| Precommitted interpretation | Current status after external review and zero-call reanalysis |
|---|---|
| At least one persona establishes an unconfounded incentive-response existence result | **Not supported under episode-level inference.** Historical gate: familywise \(p=0.0592\). Exact episode gate excludes p13; largest surviving slope +0.0833, \(p=0.7732\). |
| "No game-relevant instruction — trait words only" | Restated precisely: no explicit game terminology, action recommendation, or payoff reference; traits are strategically relevant information, and name, age, and occupation are uncontrolled semantic treatments. |
| Persona framing "contested or beat" task switches | Pooled choice result survives exact episode inference, but every repeated conflict subcell is mixed; the pooled dominance classification is entirely carried by the word/payoff-confounded swap cell. |
| Bare corners characterize the configuration rather than the model's capability envelope | Retained only as a future hypothesis. The p13 evidence no longer supports it; clause (b) demonstrates a robust choice reversal but does not identify incentive sensitivity. |

The sealed text remains unchanged because its evidentiary value lies partly in making interpretive error visible. The correction is additive and explicit rather than silently rewritten.

## 6. Limitations

The primary evidence comes from one model deployment and sixteen complete persona prompts. Population-level generalization is weakly identified. The corner census depends on interval construction: the historical seat rule, exact episode projection, and Dirichlet–Jeffreys sensitivity produce different counts, although all locate most variation between prompts rather than within them. The exact episode interval is conservative, while the Bayesian sensitivity depends on its prior. The variance correction is a method-of-moments/hierarchical-bootstrap sensitivity for the fixed prompt panel, not a matched estimate of human latent heterogeneity.

Explicit persona strings are paired across conditions, but latent-person invariance is untested. Clause (b) remains word/payoff-confounded. Human references are published and protocol-nonmatched; the Dal Bó–Fréchette microdata analysis can contextualize first exposure, learning, and endpoint mass but cannot create a matched design or a human distribution of individual \(\Delta_i\). The temperature observation lacks an identified mechanism, the high-temperature δ interaction is not estimable under the registered design, and the Gemini tier is descriptive under documented endpoint non-stationarity.

The final family analysis was specified after reviewers found the original defect. It appropriately weakens the archived claim but cannot convert any favorable post hoc result into prospective confirmation. The natural next test is a newly registered replication with episode-level gates and family control fixed before data.

## 7. Reproducibility

The repository is public. The capsule replays 4,576/4,576 Phase 4–5 runs byte-exact with zero credentials and zero live model calls. Prompt registries, freeze packets, claim ledgers, adjudication records, external timestamp proofs, post-adjudication sensitivity scripts, and generated result tables are versioned in the repository. The submission analyses run in GitHub Actions directly against the archived databases and commit their outputs to the review branch; they make no provider calls and alter no sealed source artifact.

## 8. Attribution

The human author selected the research questions, approved the registered designs, evaluated reviewer recommendations, and accepts responsibility for all claims. The autonomous pipeline executed registration, dispatch, adjudication, and replay as apparatus. AI reviewers supplied adversarial analysis that materially changed the manuscript, including the family-error diagnosis, the condition-mean identity, the dependence-unit critique, and the latent-person-invariance correction. Drafting and verification assistance from Claude, Gemini, Grok, and ChatGPT is documented in the repository. Venue-specific disclosure language will be conformed at submission.

---

## Appendix A — Cutting room and correction ledger

### A.1 Findings retained outside the main arc

- **Entropy versus temperature:** choice entropy fell as decoding temperature rose, including on a matched-unit lattice. This is real in the recorded data but mechanism-free and remains supplementary.
- **RPS role-attached rock bias:** survived neutral symbols and randomized display order, with a cross-vendor sign reversal. Supplementary because it adds another game without strengthening the main causal claim.
- **Adversary-suite secondaries:** order-2 tracking exploited the primary configuration while a first-order tracker lost; the registered WSLS-targeter prediction failed. These support opponent contingency but require a separate technical appendix.
- **Drift case study:** retained as a full repository artifact and summarized only in §4.5.
- **Claude Haiku entry-gate failure:** preserved as evidence that eligibility to act as a behavioral subject is itself an empirical question.

### A.2 Framings set aside

- **"Level-Matching Is Cheap"** and **"Moment Matching Is Cheap"** were retired because exact condition-specific mean matching would recover the aggregate contrast by identity. The current title makes the load-bearing qualifier—coarse—explicit.
- Discovery-forward **"One Persona in Sixteen"** was rejected because p13 does not survive episode-level inference.
- Metascience-first, safety-first, prompt-stack, and temperature-anomaly papers remain possible spin-outs.

### A.3 Analyses not run

The balanced-payoff × persona cell remains the highest-value de-confounding experiment. Other follow-ups include a prospectively family-controlled p13 replication, broader persona sampling, cross-model persona transfer, richer interview-conditioned panels, a matched human arm, and additional wording interpolation. No new arm was added after the scope seal.

The Dal Bó–Fréchette microdata pipeline is written and fixture-tested, but the official package remains login-gated. Until the licensed data are supplied, only published table values are used and every comparison remains labeled nonmatched.

### A.4 Open questions for reviewers

1. Does the mechanism-forward framing sufficiently distinguish this paper from Li and Ji, the surrogacy framework, statistical-realism benchmarks, and persona-collapse/state-blindness work?
2. Is the exact-episode/Dirichlet method sensitivity the right reason to foreground continuous decomposition over the historical P5-1a verdict?
3. Should the full sealed discussion artifact remain supplementary, with only the excerpt and correction table in the main paper?
4. Should any quantitative Dal Bó–Fréchette comparator remain in the final manuscript without the microdata reanalysis?
5. Which supplementary result—RPS, adversaries, drift, or temperature—is most valuable to restore?
6. What credit convention should agentic research pipelines and adversarial AI reviewers receive?

### A.5 Correction ledger

| Change | Source | Category |
|---|---|---|
| p13 confirmatory → replication target | External review of family error | Inference |
| Final 200,000-permutation audit: historical gate \(p=0.0592\); exact episode gate excludes p13 and yields max \(p=0.7732\) | Zero-call submission analysis | Inference |
| Seat-level historical gate supplemented by exact episode-level CP projection | External dependence critique + zero-call analysis | Statistical unit |
| P5-1a historical 3/32; exact episode 2/32; Dirichlet sensitivity 5/32 | Zero-call submission analysis | Robustness |
| Percentile cluster bootstrap rejected as primary because it degenerates at exact corners | Internal review during integration | Statistical validity |
| Raw SDs corrected for finite episode counts; corrected SD 0.418–0.478 and between share 85%–96% | Zero-call hierarchical analysis | Variance interpretation |
| P5-2 pooled result survives, but exact episode analysis makes every repeated conflict subcell mixed; swap alone carries dominance | Zero-call submission analysis | Construct interpretation |
| Clause (b) survives simultaneous familywise exact episode bounds in all 24 lanes; minimum lower bound 0.462 | Zero-call submission analysis | Statistical robustness |
| "δ-matched" and N-fold human comparisons retired | Comparator audit | Comparator validity |
| Lin-style latent drift reframed as potentially coexisting, not excluded | Literature verification | Mechanism scope |
| Exact condition-level matching distinguished from broad-band checks | Identification audit | Theory |
| Full-store and ledger counts reconciled: 36,251 request events versus 30,530 Phase 4–5 ledger calls; 5,505 archived completed runs versus 4,576 replay-contract runs | Zero-call count analysis | Provenance |
| "Text-determined, not payoff-determined" replaced by conditional semantic dominance | Reviewer critique | Precision |
| Complete persona sentence treated as the unit; trait causality demoted | Construct audit | Scope |
| Sealed discussion preserved with correction table rather than silently edited | Transparency design | Research integrity |

*End of working draft v4.*
