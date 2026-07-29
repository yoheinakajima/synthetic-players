# Passing Coarse Marginal Checks Can Be Cheap: Persona Mixtures and Weak Observed Incentive Response in LLM Behavioral Simulation

**STATUS: WORKING DRAFT v5 — READY FOR FULL SCIENTIFIC REVIEW, NOT FOR CITATION.** This revision incorporates the completed zero-call submission analyses and the independent verification pass at PR head `5858543`, while leaving every sealed registration, adjudication, report, and precommitted discussion artifact unchanged. §5.2 quotes an exact excerpt of a discussion text sealed and externally timestamped before the final experiment's data existed (sha `1f1d7de9…e356`); the full sealed text remains in the supplement and is not edited. Draft history, review records, and the correction ledger are public in the repository.

**Author:** Yohei Nakajima (Untapped Capital). Experiments executed by an autonomous pipeline (Replit Agent + ActiveGraph event-sourced engine). Attribution and reviewer-role disclosure: §8.

**Artifacts (public):** github.com/yoheinakajima/synthetic-players — anonymous clone + one-command zero-credential verifier; 4,576/4,576 Phase 4–5 runs replay byte-exact; registries hashed and externally anchored (GitHub timestamps + OpenTimestamps/Bitcoin).

---

## Abstract

Large language models are increasingly used as synthetic research participants, but they are often validated by whether their marginal responses resemble published human data. We report a five-phase study in which confirmatory claims were registered before their adjudicating data and mechanically evaluated from an event-sourced record. A fixed panel of sixteen lightweight persona-conditioned GPT-4.1 configurations passed preregistered broad-reference checks for condition-level cooperation in three of four repeated-game cells. Correcting raw cross-persona dispersion for finite episode counts leaves estimated between-prompt standard deviations of 0.418–0.478 and attributes approximately 85%–96% of episode-level variation to differences between prompt configurations. Yet the observed aggregate continuation-probability contrasts are only +0.083 and +0.078 across two wording families; conservative exact simultaneous intervals are wide and do not establish equivalence or a null effect. Cell-level boundary classification is also method-sensitive: the historical seat-level rule classified 14/96 cells interior, a conservative exact episode-level interval classified 11/96, and a Dirichlet–Jeffreys sensitivity classified 19/96. Separate representation experiments showed that one continuation sentence shifted cooperation from 0/40 to 37/40 on held-out decisions and that semantic action labels could override payoff dominance in a registered conflict condition. Together, the findings identify a concrete failure mode: coarse marginal checks can be satisfied largely through composition across prompt-conditioned policies that are highly concentrated within recorded cells, while the observed response to the experimental lever remains small. External review later exposed family-error and dependence defects; post-adjudication sensitivities changed the scientific interpretation without rewriting the historical record. Human references are published and protocol-nonmatched, the results concern one fixed model–persona panel, and we do not claim human substitutability.

## 1. Introduction

Human behavioral experiments are slow and expensive; LLM calls are fast and nearly free. A growing literature reports that suitably conditioned LLMs produce data resembling human data—“algorithmic fidelity” [Argyle et al. 2023], “homo silicus” [Horton 2023], behavior “statistically indistinguishable from a random human” [Mei et al. 2024]—and a formal framework for evaluating *statistical realism* now exists [Xie et al. 2026]. Much of this evidence validates marginals: means, distributions, and aggregate replication.

Recent work shows that descriptive realism and causal fidelity can diverge at scale [Li & Ji 2026], that treating LLM outcomes as surrogates for human outcomes requires assumptions that marginal equivalence does not supply [Persson et al. 2026], and that intervention prompts can shift a model’s implied latent user even when explicit persona text is fixed [Lin et al. 2026]. Our contribution is narrower than the broad realism–effect divergence. In incentive-bearing strategic interaction, we decompose a fixed explicit persona panel into between-prompt dispersion, within-prompt variation, and prompt-indexed incentive response. The panel passes coarse marginal checks while its observed continuation-probability response remains small, and most recorded variation lies between prompt configurations rather than within them. Sealed templates and matched procedures control explicit assignment, environment randomization, and execution. They do not establish latent-person invariance; Lin-style user drift and the observed composition pattern can coexist.

**Contributions.** First, we provide a registered strategic-interaction example in which a fixed persona panel passes coarse condition-level and variance checks while producing observed aggregate continuation-probability differences of only +0.083 and +0.078; exact dependence-aware intervals show these are estimates, not equivalence claims (§4.1). Second, we identify and formalize the associated composition problem: corrected variance estimates place 85%–96% of episode-level variation between prompt configurations, the binary boundary census is interval-method-sensitive, and aggregate moments do not identify microstructure or cross-condition response coupling; representation experiments further show how wording and semantic labels govern the induced policies (§4.1–4.3). Third, we demonstrate an auditable reliability protocol—and its limit—through prospectively registered confirmatory claims, external chronology, exact replay, mechanical adjudication, and a public post-adjudication correction in which outside review overturns the favored persona-level interpretation without altering the frozen record (§4.4–4.5).

## 2. Related work

**Occupied territory, and where we sit.** Li and Ji [2026] establish across three model families, eleven interventions, and 59,508 participants that descriptive fit and intervention-effect accuracy can diverge, and that prompt refinements improving realism do not reliably improve effect accuracy. Persson, Schultzberg, and Ankargren [2026] formalize when LLM outcomes can serve as causal surrogates and why novel interventions still require human evidence. Lin et al. [2026] show that interventions can change the implicit simulated population even when explicit personas are fixed. Statistical-realism, persona-collapse, and state-versus-trait work further show that persona-conditioned populations can compress or misallocate heterogeneity [Xie et al. 2026; Harry et al. 2026; Xiao et al. 2026]. Our differentiation is a registered mechanism-level decomposition in strategic interaction: a fixed explicit prompt panel is evaluated simultaneously for marginal fit, between/within composition, representation sensitivity, and response to an economic lever. The observed composition pattern is complementary to, not exclusive of, latent-user drift.

**LLM strategic behavior.** Akata et al. [2025] characterize repeated-game play modulated by prompts; Pal et al. [2026] elicit strategies from five models while varying continuation probability, payoffs, horizon knowledge, and framing; counterfactual-reasoning evaluations alter labels and payoff structures [Georgousis et al. 2026]; and “strategic robustness” has been defined as payoff-preserving invariance across narratives [Mousavi Davoudi et al. 2026]. These works establish that neither repeated games nor prompt/payoff perturbations are new. Our distinct combination is the fixed persona panel, the explicit between/within/response decomposition, exact prompt provenance, prospective registration of confirmatory claims, and mechanical adjudication followed by public inferential correction.

**Synthetic participants and personas.** Bisbee et al. [2024] find plausible survey averages alongside compressed variance, distorted coefficients, and temporal drift; Boelaert et al. [2025] report excess homogeneity; Anthis et al. [2025] catalog diversity and generalization challenges; Hullman et al. [2026] propose statistical calibration for confirmatory use; and Park et al. [2024] show that rich interview conditioning can substantially outperform lightweight demographic/persona descriptions. Format sensitivity [Sclar et al. 2024], role-play framing [Shanahan et al. 2023], persona collapse [Xiao et al. 2026], state blindness [Harry et al. 2026], and reviews of persona-experiment transparency [Batzner et al. 2025] all caution against treating a persona string as a stable human analogue. RLHF-related diversity reduction is a possible mechanism for concentrated policies, not a mechanism identified by this design. Full map: `docs/analysis/literature-map.md`; differentiation table: `docs/analysis/novelty-relationships.md`.

## 3. Instrument and inferential units

The primary deployment is gpt-4.1 at temperature 0.7 with 16-token outputs and a fixed minimal behavioral-subject prompt containing no game-theory vocabulary or reasoning scaffold. Phase 5 prepends one sealed persona sentence to byte-identical task text, giving every persona cell an exact bare twin. The cross-vendor Gemini tier is descriptive; the original Claude Haiku candidate failed a registered entry gate and was replaced under an archived amendment. Environment randomness is seeded; provider-side generation is not claimed to be seeded. Every request, rendered prompt, completion, decoding configuration, round, and provenance record is archived.

The full event store contains 5,505 completed runs, 54,276 round events, 108,552 seat-round decisions, and 36,251 archived provider-request events. The public Phase 4–5 replay contract covers 4,576 completed runs. A separate transactional ledger records 30,530 Phase 4–5 calls, 13,141,675 input tokens, and 45,247 output tokens; it excludes earlier phases and therefore must not be conflated with the full event-store request count. Counts and definitions are reconciled in `docs/analysis/submission/count-reconciliation.md`.

Confirmatory claims were registered before the data that adjudicated them and were mechanically evaluated in a fixed vocabulary. The historical two-sided interiority rule used Clopper–Pearson bounds on seat-level round-one trials. Because two seats share an episode, the submission analysis additionally treats the complete episode as the independence unit. For an episode outcome \(Y\in\{0,0.5,1\}\), the primary exact sensitivity writes

\[
Y=\tfrac12\{\mathbf 1(Y\ge0.5)+\mathbf 1(Y=1)\},
\]

constructs simultaneous Clopper–Pearson intervals for the two episode-level binary components, and projects them onto \(E[Y]\). This construction is conservative, does not assume seat independence, and does not collapse to zero uncertainty when all observed episodes agree. A Dirichlet–Jeffreys interval is reported as a Bayesian sensitivity. The percentile cluster bootstrap is also retained in the audit trail but rejected as the primary interval because it becomes degenerate at exact corners.

The hierarchy is deployment → explicit persona prompt → condition → episode → seat → round → provider request. Phase 5’s confirmatory unit is the complete persona sentence; name, age, occupation, and traits are bundled semantic treatments. Registered claims attach to the conditional finite-panel estimand for these sixteen prompts. Claims about a wider persona generator are exploratory at \(n=16\). Pairing the same explicit prompt across conditions identifies a prompt-indexed contrast, not necessarily a stable latent person’s treatment effect.

The machinery’s boundary is explicit:

> **The pipeline can enforce a registered predicate exactly; it cannot guarantee that the predicate represents a valid estimand, test family, or construct.**

## 4. Results

### 4.1 Coarse marginal checks pass while the observed incentive response is small

The preregistered leaning rule—at least two of agreeable, patient, and risk-averse—separates round-one cooperation by 0.5–0.7 in every non-swap cell. Because names, ages, occupations, and all trait descriptors vary in the complete sentence, this is a property of the registered prompts rather than a causal trait estimate. Pool means of 0.349–0.505 enter the published cooperation band in three of four repeated-game cells.

Raw cross-persona standard deviations range from 0.4241 to 0.4800. Correcting for finite episode counts leaves fixed-panel between-prompt SD estimates of 0.4182, 0.4784, 0.4408, 0.4323 across the four repeated cells. The primary bootstrap retains all sixteen registered prompts and resamples episodes within prompt; its 95% intervals are [0.4122, 0.4391], [0.4696, 0.4916], [0.4279, 0.4654], [0.4269, 0.4496]. The corrected between-prompt component accounts for 85.5%, 96.1%, 88.8%, 90.2% of total episode-level variation, with fixed-panel 95% intervals [82.0%, 93.8%], [94.6%, 98.9%], [86.7%, 94.6%], [87.9%, 95.5%]. All four fixed-panel lower bounds exceed the historical registered threshold of 0.75 times the published human SD. An exploratory two-stage bootstrap that additionally resamples prompts produces wider corrected-SD intervals of [0.2724, 0.4879], [0.3696, 0.5123], [0.3457, 0.4890], [0.3345, 0.4847]; 3/4 lower bounds exceed the historical threshold. These are fixed-panel prompt-heterogeneity estimates and exploratory persona-generator sensitivities, not matched human latent variances.

Across the continuation-probability manipulation, the observed fixed-panel point differences are +0.083 for S2-absent wording and +0.078 for S2-present wording. Conservative exact simultaneous 95% intervals are approximately [−0.171, +0.330] and [−0.181, +0.330]. The estimates are therefore small, but the experiment does not establish equivalence, a zero response, or a narrow upper bound. Dal Bó and Fréchette [2011] remain useful only as protocol-nonmatched context: their treatments use different continuation probabilities and payoffs, monetary incentives, between-session assignment, and repeated supergames through which behavior changes with experience. Their pooled experienced contrast is substantially larger, while first-supergame ordering reverses. We make no matched magnitude or human-equivalence claim.

![Prompt-indexed continuation-probability responses](figures/prompt-indexed-delta.svg)

*Figure 1. Prompt-indexed differences in round-one cooperation, \(\Delta_i=\hat p_i(\delta=.90)-\hat p_i(\delta=.10)\), for both registered wording families. Bars are conservative exact simultaneous 95% intervals with complete episodes as the unit; observed corners retain non-zero uncertainty. Aggregate diamonds show the fixed-panel point differences and intervals. Pairing the same explicit prompt supplies a prompt-indexed coupling, not a person-level treatment effect without latent-person invariance.*

The historical seat-level interiority rule classified 14/96 persona–condition cells as interior and 3/32 in the restricted P5-1a set, just below the registered 0.10 threshold. The primary exact episode-level interval classifies 11/96 and 2/32. A Dirichlet–Jeffreys sensitivity classifies 19/96 and 5/32, which would fail the historical threshold. Thus the binary verdict is not invariant to interval construction. The more stable result is continuous: the corrected decomposition assigns a large majority of observed episode-level variation to differences between prompt configurations, while the observed aggregate continuation-probability point differences remain small and imprecisely estimated.

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

**Proposition B: aggregate moments do not identify microstructure or response coupling.** Mean and total variance do not identify how variation is divided between prompt configurations and repeated draws, nor do they identify distributional shape or boundary concentration. Even exact condition-specific distributions do not identify the cross-condition coupling and therefore do not identify the distribution of prompt-indexed responses \(\Delta_i=p_i(1)-p_i(0)\). Reusing an explicit persona string supplies one prompt-indexed coupling, but interpreting it as a stable synthetic individual’s potential-outcome contrast requires latent-person invariance, which this study does not test.

The study therefore identifies a composition pattern in one fixed prompt panel. It does not establish that humans have a different microstructure, that RLHF caused the pattern, that latent-user drift is absent, or that the same pattern occurs across persona generators.

### 4.3 Control-channel interactions

For the bare configuration, round-one cooperation was 0.000 at every registered continuation probability. A single continuation sentence, localized through a span ladder and confirmed on fresh seeds, moved held-out cooperation from 0/40 to 37/40. The same wording factor was null in one-shot play, showing that text effects depend on the context in which a phrase has a strategic referent.

In the label-swap conflict cell, canonical payoffs were held fixed while the displayed words “Cooperate” and “Defect” were attached to opposite strategic roles. The bare configuration selected the cooperation-worded option 0/40 times, choosing the strictly dominated role whenever it carried the word “Defect,” while responding strongly to payoff changes when semantic labels did not oppose them. The supported statement is conditional: **semantic labels can override payoff dominance in direct conflict; payoff sensitivity is representation-dependent, not absent.**

Personas add separable presence and direction effects. Direction produces the 0.5–0.7 leaning gaps. Presence reverses the bare swap-cell choice: all sixteen personas overwhelmingly select the cooperation-worded/payoff-dominant option. The choice result is statistically strong but mechanism-confounded because word and payoff point to the same action. Under episode-exact analysis, all 24 evaluable persona × temperature lanes retain a simultaneous familywise lower bound above the registered 0.20 threshold; the minimum is 0.462. This establishes the choice pattern, not whether incentives or lexical attraction caused it.

The pooled P5-2 task-consistent share is 0.128 with an exact episode-level 95% interval [0.092, 0.172], retaining the historical persona-dominant classification. Every repeated-game conflict subcell is mixed under the exact episode interval. Only the swap cell is individually persona-dominant, with a task-consistent share of 0 and interval [0, 0.027]. The pooled verdict is therefore carried entirely by the word/payoff-confounded cell. We describe these findings as **control-channel interactions**, not a fixed hierarchy.

### 4.4 The favored persona-level result does not survive dependence-aware inference

Under the historical seat-level rule, persona p13 moved from 0.333 cooperation at δ=.10 to 0.750 at δ=.90 and passed a per-candidate lower-bound test. The rule searched multiple persona × wording candidates and fired on any pass without declared family-level error control. External review identified that defect.

Three 200,000-permutation gate constructions are now reported. Under the historical seat-level gate, p13 remains the maximum at +0.4167, with familywise \(p=0.059230\), Monte Carlo 95% interval [0.058194, 0.060268]. Under the retained percentile episode-cluster-bootstrap gate, p13 also remains the maximum and \(p=0.043455\), interval [0.042561, 0.044353]. That construction is the only variant below 0.05, but it is not primary because percentile intervals become degenerate at exact corners—the very locations the assay must classify with non-zero policy uncertainty. Under the primary conservative exact-episode gate, p13 is not interior: its low-δ lower bound falls below 0.05 and its high-δ upper bound exceeds 0.95. Only p04/s2p and p05/s2a pass both gates; the largest surviving positive slope is +0.0833, with familywise \(p=0.773206\), interval [0.771363, 0.775039].

These variants were specified and executed together only after external review exposed the original defects. No familywise gate was registered at the original freeze, and the repository contains no seal-before-compute record for these sensitivities. The analyses ran in GitHub Actions against archived databases with fixed seeds, and their outputs were committed regardless of direction. Accordingly, the favorable \(p=0.043455\) variant cannot create prospective confirmation, just as the other variants cannot retroactively strengthen the frozen claim. The historical mechanical P5-3 verdict remains visible because clause (b) fired strongly and p13 passed the rule as frozen. Scientifically, p13 is a replication target, not a finding; the capability-envelope interpretation selected by the precommitted branch is no longer supported by clause (a).

### 4.5 Auditability

Twelve registered author predictions were refuted by data and published. Four underspecified analysis choices were resolved outcome-blind. A two-sided gate blocked a false ceiling conclusion. Sentinels detected a time-indexed behavioral discontinuity in an unversioned endpoint and exposed a monitoring gap that was repaired with an attestation gate. The public capsule replays all 4,576 Phase 4–5 runs exactly with zero live model calls. External review then found the family-error and dependence defects discussed above; the archived record made both diagnosable and correctable.

The claim is bounded: the machinery is procedurally exact and extensively auditable. Its strongest achievement is not self-validation but preservation of enough provenance for outsiders to identify where procedural correctness stopped short of statistical validity.

## 5. Discussion

### 5.1 Implications

For synthetic-participant practice, broad marginal resemblance is a weak validation target. Lightweight conditioning can generate plausible aggregate levels and substantial cross-prompt dispersion while leaving the observed response to an economic lever small. Validation should therefore report response surfaces over declared interventions and representation families, together with assay-sensitivity checks, dependence-aware uncertainty, model/provider provenance, and temporal monitoring. Statistical calibration [Hullman et al. 2026], causal-surrogacy assumptions [Persson et al. 2026], and latent-drift diagnostics [Lin et al. 2026] are complementary rather than competing safeguards.

The result can be read as a synthetic-subject analogue of the reduced-form/structural distinction associated with the Lucas critique [Lucas 1976]: fitting or selecting for aggregate resemblance need not identify behavior under a moved policy lever. In psychometric terms, it is a construct-validity and assay-sensitivity problem [Cronbach & Meehl 1955; ICH E10; Temple & Ellenberg 2000]. Agent-based modeling’s equifinality and pattern-oriented validation provide a related analogy [Windrum et al. 2007; Grimm et al. 2005]. These are organizing analogies, not claims that the study literally estimates a structural economic model or validates a human measurement model.

The results also show why binary certification language should be used sparingly. The historical P5-1a predicate passes under its frozen seat-level rule and under the conservative episode-exact interval, but fails under a reasonable Dirichlet–Jeffreys sensitivity. The underlying continuous evidence is clearer than the thresholded label: prompt identity accounts for most estimated variation, many cells lie near behavioral boundaries, and the continuation-probability point differences are small but uncertain.

For deployment, behavior that can be rewritten by a sentence, an action token, or an identity prefix is safety-relevant. The results do not imply that language always dominates incentives: in some cells numerical payoffs move behavior strongly, and precedence depends on representation and conflict structure.

### 5.2 The precommitted discussion, and what changed after review

The Phase 5 discussion was sealed before its data existed. Excerpt (full text in supplement; sha `1f1d7de9…e356`):

> “The headline of Phase 5 is an existence result the program registered against itself: at least one persona in the sealed sixteen passed the two-sided assay gate and showed the registered signature of incentive sensitivity. The author’s registered prediction—that none would—is refuted, and the refutation is the finding. … The capability was recoverable by content-side conditioning… The scope of the claim is deliberately narrow.”

| Precommitted interpretation | Current status after external review and zero-call reanalysis |
|---|---|
| At least one persona establishes an unconfounded incentive-response existence result | **Not supported.** Post-review variants: historical seat gate \(p=0.059230\); percentile cluster-bootstrap gate \(p=0.043455\) but non-primary because of corner degeneracy; primary exact-episode gate excludes p13 and gives maximum surviving slope +0.0833, \(p=0.773206\). None was registered at the original freeze, so none creates prospective confirmation. |
| “No game-relevant instruction—trait words only” | Restated precisely: no explicit game terminology, action recommendation, or payoff reference; traits are strategically relevant information, and name, age, and occupation are uncontrolled semantic treatments. |
| Persona framing “contested or beat” task switches | Pooled choice result survives exact episode inference, but every repeated conflict subcell is mixed; the pooled dominance classification is entirely carried by the word/payoff-confounded swap cell. |
| Bare corners characterize the configuration rather than the model’s capability envelope | Retained only as a future hypothesis. The p13 evidence no longer supports it; clause (b) demonstrates a robust choice reversal but does not identify incentive sensitivity. |

The sealed text remains unchanged because its evidentiary value lies partly in making interpretive error visible. The correction is additive and explicit rather than silently rewritten.

## 6. Limitations

The primary evidence comes from one model deployment and sixteen complete persona prompts. Population-level generalization is weakly identified. The boundary census depends on interval construction: the historical seat rule, exact episode projection, and Dirichlet–Jeffreys sensitivity produce different counts, although the corrected variance analysis consistently locates most estimated variation between prompts rather than within them. The exact episode interval is conservative, while the Bayesian sensitivity depends on its prior. The variance correction is a fixed-panel method-of-moments/bootstrap sensitivity, not a matched estimate of human latent heterogeneity.

The two aggregate continuation-probability point estimates are small, but their conservative intervals are wide; the data do not establish equivalence, incentive insensitivity, or a narrow maximum effect. Explicit persona strings are paired across conditions, but latent-person invariance is untested. Clause (b) remains word/payoff-confounded. Human references are published and protocol-nonmatched. The Dal Bó–Fréchette microdata pipeline is fixture-tested but the licensed package remains login-gated; Q5 is therefore deferred and nonblocking under the current internal claim. The temperature observation lacks an identified mechanism, the high-temperature δ interaction is not estimable under the registered design, and the Gemini tier is descriptive under documented endpoint non-stationarity.

The post-adjudication family analyses were specified after reviewers found the original defects and were not sealed before computation. Fixed seeds, Actions execution, complete output retention, and public review constrain discretion but do not convert the analyses into preregistered confirmation. The natural next test is a newly registered replication with episode-level gates and family control fixed before data.

## 7. Reproducibility

The repository is public. The capsule replays 4,576/4,576 Phase 4–5 runs byte-exact with zero credentials and zero live model calls. Prompt registries, freeze packets, claim ledgers, adjudication records, external timestamp proofs, post-adjudication sensitivity scripts, generated result tables, draft history, and reviewer records are versioned in the repository. The submission analyses run in GitHub Actions directly against archived databases and commit their outputs to the review branch; they make no provider calls and alter no sealed source artifact.

The original `scope-seal.md` was sealed byte-for-byte with a header that still reads “PROPOSED—UNSEALED.” It is not edited because its hash is part of the Phase 5 seal. A living status addendum points to the sealing event, manifest hash, and stopping-rule evidence.

## 8. Attribution

The human author selected the research questions, approved the registered designs, adjudicated which reviewer recommendations to adopt, and accepts responsibility for every claim. The autonomous pipeline executed registration, dispatch, adjudication, and replay as apparatus. AI reviewers supplied adversarial analysis that materially changed the manuscript, including the family-error diagnosis, the condition-mean identity, the dependence-unit critique, and the latent-person-invariance correction.

The role of one round-2 reviewer subsequently expanded from critique to specification of the post-adjudication analyses and management of their integration. Those analyses were executed by GitHub Actions against the archived databases; resulting commits were authored by Yohei Nakajima or the Actions bot. A later reviewer independently checked the branch through an anonymous blobless clone against the generated JSON and commit history. Review prompts, role changes, adopted recommendations, and the independent verification memo are archived under `docs/reviews/`. Venue-specific AI-assistance language will be conformed at submission.

---

## Appendix A — Cutting room and correction ledger

### A.1 Findings retained outside the main arc

- **Entropy versus temperature:** choice entropy fell as decoding temperature rose, including on a matched-unit lattice. This is real in the recorded data but mechanism-free and remains supplementary.
- **RPS role-attached rock bias:** survived neutral symbols and randomized display order, with a cross-vendor sign reversal. Supplementary because it adds another game without strengthening the main claim.
- **Adversary-suite secondaries:** order-2 tracking exploited the primary configuration while a first-order tracker lost; the registered WSLS-targeter prediction failed. These support opponent contingency but require a separate technical appendix.
- **Drift case study:** retained as a full repository artifact and summarized only in §4.5.
- **Claude Haiku entry-gate failure:** preserved as evidence that eligibility to act as a behavioral subject is itself an empirical question.

### A.2 Framings set aside

- “Level-Matching Is Cheap” and “Moment Matching Is Cheap” were retired because exact condition-specific mean matching would recover the aggregate contrast by identity.
- “Corner Mixtures” was removed from the title because the binary corner census is interval-method-sensitive. The less brittle load-bearing construct is the persona-mixture composition and corrected between-prompt share.
- Discovery-forward “One Persona in Sixteen” was rejected because p13 does not survive primary episode-level inference.
- Metascience-first, safety-first, prompt-stack, and temperature-anomaly papers remain possible spin-outs.

### A.3 Analyses not run

The balanced-payoff × persona cell remains the highest-value de-confounding experiment. Other follow-ups include a prospectively family-controlled p13 replication, broader persona sampling, cross-model persona transfer, richer interview-conditioned panels, a matched human arm, and additional wording interpolation. No new arm was added after the scope seal.

The Dal Bó–Fréchette microdata pipeline is written and fixture-tested, but the official package remains login-gated. The statistical submission gate is complete with this Q5 contextualization deferred. Until licensed data are supplied, only published table values are used and every comparison remains labeled nonmatched.

### A.4 Open questions for reviewers

1. Does the mechanism-forward framing sufficiently distinguish this paper from Li and Ji, the surrogacy framework, statistical-realism benchmarks, and persona-collapse/state-blindness work?
2. Does the figure make the central distinction clear: small observed fixed-panel point differences, but no equivalence conclusion?
3. Is the exact-episode/Dirichlet method sensitivity the right reason to foreground the continuous decomposition over the historical P5-1a verdict?
4. Should the full sealed discussion artifact remain supplementary, with only the excerpt and correction table in the main paper?
5. Should any quantitative Dal Bó–Fréchette comparator remain in the final submitted manuscript without the microdata reanalysis?
6. What credit convention should agentic research pipelines and adversarial AI reviewers receive?

### A.5 Correction ledger

| Change | Source | Category |
|---|---|---|
| p13 confirmatory → replication target | External review of family error | Inference |
| All three 200,000-permutation variants reported: historical seat gate \(p=0.059230\); retained percentile cluster-bootstrap gate \(p=0.043455\); primary exact-episode gate excludes p13 and yields max \(p=0.773206\) | Independent verification + zero-call submission analyses | Inference transparency |
| Post-adjudication variants explicitly labeled unregistered at the original freeze; fixed-seed Actions execution and complete output retention documented | Independent verification | Chronology and discretion |
| Seat-level historical gate supplemented by exact episode-level CP projection | External dependence critique + zero-call analysis | Statistical unit |
| P5-1a historical 3/32; exact episode 2/32; Dirichlet sensitivity 5/32 | Zero-call submission analysis | Robustness |
| Percentile cluster bootstrap retained but rejected as primary because it degenerates at exact corners | Statistical audit | Statistical validity |
| Raw SDs corrected for finite episode counts; corrected SD 0.418–0.478 and between share 85%–96% | Zero-call variance analysis | Variance interpretation |
| Prompt-indexed \(\Delta_i\) figure added with exact non-degenerate intervals, aggregate intervals, and latent-coupling caveat | Independent review recommendation | Interpretability |
| P5-2 pooled result survives, but exact episode analysis makes every repeated conflict subcell mixed; swap alone carries dominance | Zero-call submission analysis | Construct interpretation |
| Clause (b) survives simultaneous familywise exact episode bounds in all 24 lanes; minimum lower bound 0.462 | Zero-call submission analysis | Statistical robustness |
| “δ-matched” and N-fold human comparisons retired | Comparator audit | Comparator validity |
| Lin-style latent drift reframed as potentially coexisting, not excluded | Literature verification | Mechanism scope |
| Exact condition-level matching distinguished from broad-band checks | Identification audit | Theory |
| Full-store and ledger counts reconciled: 36,251 request events versus 30,530 Phase 4–5 ledger calls; 5,505 archived completed runs versus 4,576 replay-contract runs | Zero-call count analysis | Provenance |
| “Text-determined, not payoff-determined” replaced by conditional semantic dominance | Reviewer critique | Precision |
| Complete persona sentence treated as the unit; trait causality demoted | Construct audit | Scope |
| Sealed discussion preserved with correction table rather than silently edited | Transparency design | Research integrity |
| Confirmatory registration language narrowed to claims registered before their adjudicating data | Independent verification | Registration accuracy |

*End of working draft v5.*
