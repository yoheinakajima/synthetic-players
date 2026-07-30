#!/usr/bin/env python3
"""Apply Explore Science v10 review dispositions as an explicit v11 addendum.

Edits living manuscript/support files only. The v10 freeze artifacts and tag remain
untouched; v11 is a new post-freeze review version.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "docs/paper/paper-draft.md"
README = ROOT / "README.md"
REVIEW = ROOT / "REVIEW.md"
INDEX = ROOT / "docs/analysis/INDEX.md"
STATUS = ROOT / "docs/analysis/submission-blockers.md"
PDFREADME = ROOT / "docs/paper/PDF-README.md"
CITATION = ROOT / "CITATION.cff"
REVIEWS = ROOT / "docs/reviews/README.md"

ABSTRACT = """## Abstract

Large language models are increasingly used as synthetic research participants, but they are often validated by whether their marginal responses resemble published human data. We report a five-phase research program. Confirmatory claims from Phases 3–5 were registered before the data that adjudicated them and were mechanically evaluated from an event-sourced record; Phases 1–2 document post hoc instrument development and corrective re-adjudication rather than prospective confirmation. A fixed panel of sixteen lightweight persona-conditioned GPT-4.1 configurations passed preregistered broad-reference checks for condition-level cooperation in three of four repeated-game cells. Finite-opportunity-corrected point estimates place between-prompt standard deviations at 0.418–0.478 and 85%–96% of observed episode-level variation between prompt configurations. A fixed-panel Dirichlet–Jeffreys latent-propensity sensitivity, which propagates uncertainty from six-episode boundary cells, yields posterior median between shares of 63%–71% with 95% intervals spanning 49%–81%. The observed aggregate continuation-probability contrasts are +0.083 and +0.078 across two wording families; conservative exact simultaneous 95% intervals are [−0.171, +0.330] and [−0.181, +0.330] (rounded to three decimals). The treatment jointly changed the continuation process and the language communicating it, so incentive and framing channels remain undecomposed. Cell-level boundary classification is also method-sensitive: the historical seat-level rule classified 14/96 cells interior, a conservative exact episode-level interval classified 11/96, and a Dirichlet–Jeffreys sensitivity classified 19/96. Separate representation experiments showed that, in the bare non-persona-conditioned configuration, replacing and repositioning one continuation sentence shifted cooperation from 0/40 to 37/40 on held-out decisions, and that semantic action labels made the bare configuration choose an action dominated by the payoffs in a registered conflict condition. Together, the findings identify a concrete validation failure mode: broad-reference marginal criteria can be satisfied through composition across concentrated prompt-conditioned policies without requiring the treatment-response object to be estimated. External review later exposed family-error, dependence, and boundary-uncertainty defects; post-adjudication sensitivities changed the scientific interpretation without rewriting the historical record. Human references are published and protocol-nonmatched, the results concern one fixed model–persona panel, and we do not claim human substitutability.
"""

CONDITION_BLOCK = """**Phase 5 condition matrix.** The 96 Tier-A persona–condition units are the full cross of sixteen prompts with six conditions:

| Code | Condition | Role in the paper |
|---|---|---|
| `rep-d10-s2a` | repeated PD, δ=.10, S2 absent | repeated-game level, variance, and response |
| `rep-d10-s2p` | repeated PD, δ=.10, S2 present | repeated-game level, variance, and response |
| `rep-d90-s2a` | repeated PD, δ=.90, S2 absent | repeated-game level, variance, and response |
| `rep-d90-s2p` | repeated PD, δ=.90, S2 present | repeated-game level, variance, and response |
| `os-swap` | one-shot canonical-payoff label swap | semantic-label/payoff conflict |
| `os-community` | one-shot Community framing | near-interior framing anchor |

The registered P5-1a concept restricted its primary denominator to persona cells whose **exact recorded bare twin** failed the same interiority gate. An outcome-blind exact-twin completion fixed that set as `rep-d90-s2a` and `os-swap`: sixteen personas in each condition, hence 32 units. The exact Community twin passed the bare gate; the other three repeated-game cells lacked exact bare twins and entered only the unrestricted 96-cell secondary.
"""

SECTION41 = r"""### 4.1 Coarse marginal checks pass while represented-treatment estimates remain imprecise

The preregistered leaning rule—at least two of agreeable, patient, and risk-averse—separates round-one cooperation by 0.5–0.7 in every non-swap cell. Because names, ages, occupations, and all trait descriptors vary in the complete sentence, this is a property of the registered prompts rather than a causal trait estimate. The preregistered P3-A3 broad-reference cooperation band is [0.36, 0.63]. The four repeated-game pool means are 0.349 (`rep-d10-s2a`), 0.427 (`rep-d10-s2p`), 0.432 (`rep-d90-s2a`), and 0.505 (`rep-d90-s2p`); only the S2-absent δ=.10 cell falls outside the band, by 0.011 below its lower boundary.

Raw cross-persona standard deviations range from 0.4241 to 0.4800. Correcting the plug-in estimates for finite episode counts leaves between-prompt SD point estimates of 0.4182, 0.4784, 0.4408, and 0.4323 in the cell order above. P5-1b used protocol-nonmatched human references mechanically implied from Dal Bó and Fréchette’s [2011] R=40 Table 7 strategy-frequency estimates: SD=0.4122 for their δ=.50 panel and SD=0.3116 for their δ=.75 panel. The frozen ratio ρ=.75 therefore gives thresholds 0.3092 for this study’s δ=.10 cells and 0.2337 for its δ=.90 cells. All four plug-in estimates exceed those historical thresholds.

Three post-adjudication uncertainty views answer different questions. First, a **conditional fixed-panel episode bootstrap** retains the sixteen prompts and resamples their empirical episode distributions; its corrected-SD 95% intervals are [0.4122, 0.4391], [0.4696, 0.4916], [0.4279, 0.4654], and [0.4269, 0.4496]. Because an empirically unanimous six-episode cell resamples as a point mass, these intervals condition on the recorded boundary concentration and do not propagate uncertainty about latent prompt policies. Second, a **fixed-panel latent-propensity sensitivity** assigns each prompt/cell outcome distribution on {0, .5, 1} an independent Dirichlet(0.5, 0.5, 0.5) posterior. Its SD medians (95% intervals) are 0.3543 [0.3090, 0.3886], 0.3959 [0.3521, 0.4308], 0.3698 [0.3253, 0.4060], and 0.3620 [0.3179, 0.3970]; three of four lower bounds exceed the historical threshold, with `rep-d10-s2a` essentially on it (0.3090 versus 0.3092). Third, the **two-stage prompt+episode bootstrap**, which changes the estimand toward a hypothetical persona generator, yields corrected-SD intervals `rep-d10-s2a` [0.2724, 0.4879], `rep-d10-s2p` [0.3696, 0.5123], `rep-d90-s2a` [0.3457, 0.4890], and `rep-d90-s2p` [0.3345, 0.4847]. None of these post hoc sensitivities changes the frozen mechanical P5-1b verdict.

The corresponding plug-in between-prompt shares are 85.5%, 96.1%, 88.8%, and 90.2%. Conditional episode-bootstrap intervals are [82.0%, 93.8%], [94.6%, 98.9%], [86.7%, 94.6%], and [87.9%, 95.5%]. The latent-propensity posterior is materially wider and lower: medians 63.1%, 70.5%, 66.1%, and 66.5%, with 95% intervals [49.4%, 74.5%], [57.3%, 81.3%], [52.8%, 77.0%], and [52.8%, 77.7%]. Thus the robust statement is that between-prompt composition is substantial and likely dominant in this fixed panel; 85%–96% are plug-in point estimates, not fully uncertainty-adjusted population facts.

Across the represented continuation-probability treatment, the observed fixed-panel point differences are +0.083 for S2-absent wording and +0.078 for S2-present wording. Conservative exact simultaneous 95% intervals are [−0.171, +0.330] and [−0.181, +0.330] (rounded to three decimals). The point estimates are small on the unit scale, but the intervals permit effects as large as +0.33 and moderately negative effects; the experiment does not establish equivalence, a zero response, or a narrow upper bound. The treatment changes both the environment’s continuation process and the text used to communicate that process. Round-one choices therefore identify response to **continuation probability under a specified representation**, not a semantically neutral economic parameter: incentive and framing channels remain undecomposed.

These numbers have two distinct readings. For the finite archived panel, the contrasts +0.083 and +0.078 are exact descriptive arithmetic and require no sampling interval. For inference about the latent cooperation propensities of these sixteen configurations under repeated sampling, the conservative exact intervals remain wide. A plug-in or asymptotic clustered interval that treats zero observed within-cell variation as zero latent variance can be much narrower by construction; six agreeing episodes do not establish a deterministic boundary policy. A design-effect heuristic using six episodes per prompt and the plug-in between-share range 0.855–0.961 yields effective sample sizes of roughly 16.5–18.2 episode equivalents per condition, close to the sixteen prompt units. This is a planning heuristic, not the degrees of freedom of the exact procedure, but it identifies prompt count as the operative precision constraint.

Dal Bó and Fréchette [2011] remain useful only as protocol-nonmatched context: their treatments use different continuation probabilities and payoffs, monetary incentives, between-session assignment, and repeated supergames through which behavior changes with experience. Their pooled experienced contrast is substantially larger, while first-supergame ordering reverses. We make no matched magnitude or human-equivalence claim.

The registered Gemini tier was descriptive only and is excluded from these estimates because its endpoint showed documented non-stationarity. Across eight personas and three cells, recorded means ranged from 0 to 0.90 and 9/24 cells (37.5%) met the historical interiority rule, compared with 14/96 (14.6%) in the primary GPT-4.1 panel; several representation-channel effects also reversed direction across vendors. Because the endpoint was non-stationary and the evaluated panels differed, this is not a formal replication comparison. It is contrary descriptive evidence that the composition pattern is deployment-specific rather than universal. Complete values are in `docs/analysis/figure-sources/p5-tierC-gemini.csv` and the stability record.

![Prompt-indexed continuation-probability responses](figures/prompt-indexed-delta.svg)

*Figure 1. Prompt-indexed differences in round-one cooperation, \(\Delta_i=\hat p_i(\delta=.90)-\hat p_i(\delta=.10)\), for both registered wording families. The series are vertically dodged so coincident values and intervals remain separately visible. Bars are conservative exact simultaneous 95% intervals with complete episodes as the unit; observed corners retain non-zero uncertainty. Diamonds on the **Fixed-panel aggregate** row show the two wording-family estimates in their corresponding colors. Rows at \(\Delta_i=0\) can reflect boundary concentration in both recorded cells; they are not precise evidence of homogeneous response or no effect.*

![Condition-level cooperation means](figures/condition-means.svg)

*Figure 2. Fixed-panel round-one cooperation by represented continuation-probability condition and wording family. Series are horizontally dodged; point labels and the y-axis are percentages. Error bars are conservative exact condition intervals. Lines connect conditions for orientation only and do not imply a precise, semantically isolated incentive effect.*

![Between-prompt variance share](figures/between-prompt-share.svg)

*Figure 3. Between-prompt share of episode-level variation in each repeated-game cell. Circles and thin intervals show the finite-opportunity-corrected plug-in estimates with conditional episode-bootstrap intervals. Offset squares and thicker intervals show the fixed-panel Dirichlet–Jeffreys latent-propensity posterior medians and 95% intervals, which propagate uncertainty from empirically unanimous cells. The wider two-stage prompt+episode bootstrap changes the estimand toward a persona generator and is reported in text.*

Across all six Phase 5 conditions, the historical seat-level rule classifies 14/96 persona–condition cells interior, the conservative exact episode-level interval 11/96, and the Dirichlet–Jeffreys sensitivity 19/96. In the registered 32-unit restricted set (`rep-d90-s2a` plus `os-swap`), the corresponding counts are 3/32, 2/32, and 5/32. The historical 3/32 fraction falls just below the frozen 0.10 threshold; the Bayesian sensitivity would not. Thus the binary verdict is not invariant to interval construction. The continuous uncertainty analyses above provide the less brittle description.
"""

SECTION43 = r"""### 4.3 Control-channel interactions

For the bare configuration, round-one cooperation was 0.000 at every registered continuation probability. X2 mechanically decomposed the v1 and v2a prompt bundles into six rendered sentence/block spans and constructed forward and reverse ladders by replacing one complete span at a time. The selected S2 operation replaced and repositioned the v1 sentence “After every round there is a {deltaPct}% chance the session continues with another round” with the v2a first-line sentence “At the end of each round there is a {deltaPct}% chance that the session goes on for one more round.” Here **switch-bearing** means the span whose adjacent substitution produced the largest preregistered ladder gap and then passed held-out confirmation; it is not a strategy-switch instruction. Screening used ten episodes per rung. The exact S2 minimal pair was then tested at temperature 0.7 on 20 fresh episodes per side (seeds 2953–2972, disjoint from screening), moving held-out cooperation from 0/40 to 37/40. Because S2 combined wording and position as one atomic operation, the design does not separate those components or eliminate every positional interaction. The same wording factor was null in one-shot play, showing that text effects depend on strategic context.

In the label-swap conflict cell, canonical payoffs were held fixed while the displayed words “Cooperate” and “Defect” were attached to opposite strategic roles. The bare configuration selected the cooperation-worded option 0/40 times, choosing the strictly dominated role whenever it carried the word “Defect,” while responding strongly to payoff changes when semantic labels did not oppose them. The precise conclusion is conditional: semantic labels can override payoff dominance in a registered conflict cell; payoff sensitivity is representation-dependent, not absent.

Persona conditioning produces two observed contrasts, but they are not fully factorially separable. Differences among complete persona prompts produce the 0.5–0.7 leaning gaps. Adding any tested persona string reverses the bare swap-cell choice: all sixteen personas overwhelmingly select the cooperation-worded/payoff-dominant option. Because no non-semantic prefix matched for length, punctuation, and position was run, this prefix contrast cannot isolate semantic persona content from generic sequence-length or displacement effects. The choice result is also mechanism-confounded because word and payoff point to the same action.

P5-3(b)’s 24 evaluable persona × temperature lanes comprise all sixteen personas at T=0.7 plus the registered sweep subset p02, p06, p11, and p15 at each of T=1.0 and T=1.3 (16+4+4=24). Under simultaneous episode-exact familywise bounds, every lane retains a lower bound above the frozen 0.20 threshold; the minimum is 0.462. This establishes the choice pattern, not whether incentives or lexical attraction caused it.

The pooled P5-2 task-consistent share is 90 of 704 seat decisions across 352 independent episodes. Equivalently, the pooled episode-mean total is 45/352=0.128, with conservative exact episode-level 95% interval [0.092, 0.172], retaining the historical persona-dominant classification. Every repeated-game conflict subcell is mixed under the exact episode interval. Only the swap cell is individually persona-dominant, with task-consistent share 0 and interval [0, 0.027]. The pooled verdict is therefore carried entirely by the word/payoff-confounded cell. We describe these findings as **control-channel interactions**, not a fixed hierarchy.

![Representation-channel corner shifts](figures/representation-effects.svg)

*Figure 4. Two distinct representation interventions in the bare configuration. In repeated play, the registered S2 wording-and-position operation moved observed cooperation from 0/40 to 37/40. In the one-shot label conflict, the payoff-dominant action was never chosen when the dominated action carried the displayed word “Defect.” The bars report selection shares, not a common causal estimand.*
"""


def replace_section(text: str, start: str, end: str, new: str) -> str:
    pattern = re.escape(start) + r".*?(?=" + re.escape(end) + r")"
    output, count = re.subn(
        pattern,
        lambda _match: new + "\n\n",
        text,
        count=1,
        flags=re.S,
    )
    if count != 1:
        raise RuntimeError(f"section replace failed: {start}")
    return output


def update_navigation() -> None:
    for path in (README, REVIEW, INDEX, STATUS, PDFREADME, CITATION):
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        text = text.replace(
            "synthetic-players-review-v10.pdf",
            "synthetic-players-review-v11.pdf",
        )
        text = text.replace(
            "Current v10 frozen Markdown manuscript",
            "Current v11 review-revision Markdown manuscript",
        )
        text = text.replace(
            "v10 frozen Markdown manuscript",
            "v11 review-revision Markdown manuscript",
        )
        text = text.replace("phase5-review-v10", "phase5-review-v11")
        path.write_text(text, encoding="utf-8")

    if REVIEW.exists():
        text = REVIEW.read_text(encoding="utf-8")
        row = "- **Explore Science review of v10:** [`docs/reviews/round-9-explore-science-v10-review.md`](docs/reviews/round-9-explore-science-v10-review.md) identifies reporting-completeness and boundary-uncertainty issues addressed in v11; the scientific change is declared in [`docs/paper/v11-addendum.md`](docs/paper/v11-addendum.md).\n"
        anchor = "## Corrections reviewers should know before reading\n\n"
        if row not in text and anchor in text:
            text = text.replace(anchor, anchor + row, 1)
        REVIEW.write_text(text, encoding="utf-8")

    if REVIEWS.exists():
        text = REVIEWS.read_text(encoding="utf-8")
        row = "| [`round-9-explore-science-v10-review.md`](round-9-explore-science-v10-review.md) / [`round-9-disposition-matrix.md`](round-9-disposition-matrix.md) | Explore Science review of frozen v10 and v11 response | 97/100, 0 major and 20 minor issues; numerical anchors, latent-policy uncertainty, figures, and construct qualifiers addressed in v11. |"
        marker = "## Role disclosure"
        if row not in text and marker in text:
            text = text.replace(marker, row + "\n\n" + marker, 1)
        REVIEWS.write_text(text, encoding="utf-8")


def main() -> None:
    text = PAPER.read_text(encoding="utf-8")
    text = text.replace(
        "TEXT FREEZE v10 — EXPLORE SCIENCE REVIEW COPY, NOT FOR CITATION.",
        "REVIEW REVISION v11 — POST-v10 ADDENDUM, NOT FOR CITATION.",
    )
    text = text.replace(
        "This revision incorporates the completed zero-call submission analyses, direct outside reproduction of the 4,576-run capsule, the Explore Science Round 5 corrections, and an independent repository review of v7.",
        "The v10 scientific text freeze remains archived and unchanged. This v11 addendum incorporates the subsequent Explore Science reporting-completeness review and one new zero-call fixed-panel latent-propensity sensitivity; all sealed experimental artifacts and historical mechanical verdicts remain unchanged.",
    )
    text = replace_section(text, "## Abstract", "## 1. Introduction", ABSTRACT)
    text = text.replace(
        "Second, we identify and formalize the associated composition problem: corrected variance estimates place 85%–96% of episode-level variation between prompt configurations, the binary boundary census is interval-method-sensitive, and aggregate moments do not identify microstructure or cross-condition response coupling; representation experiments further show how wording and semantic labels govern the induced policies (§4.1–4.3).",
        "Second, we identify and formalize the associated composition problem: finite-opportunity plug-in point estimates place 85%–96% of observed variation between prompts, while a latent-propensity sensitivity yields posterior median shares of 63%–71%; the binary boundary census is interval-method-sensitive, aggregate moments do not identify microstructure, and representation experiments show how wording and semantic labels govern the induced policies (§4.1–4.3).",
    )
    text = text.replace(
        "A Dirichlet–Jeffreys interval is reported as a Bayesian sensitivity.",
        r"A Dirichlet–Jeffreys sensitivity uses the symmetric Dirichlet(0.5, 0.5, 0.5) prior on the probabilities of episode outcomes {0, 0.5, 1}; posterior draws project \(E[Y]=0.5q_{0.5}+q_1\).",
    )
    glossary_anchor = "Historical alphanumeric verdicts remain visible even where post-adjudication sensitivities change their scientific interpretation."
    if CONDITION_BLOCK not in text:
        text = text.replace(
            glossary_anchor,
            glossary_anchor + "\n\n" + CONDITION_BLOCK,
            1,
        )
    text = replace_section(
        text,
        "### 4.1 Coarse marginal checks pass while represented-treatment estimates remain imprecise",
        "### 4.2 What the marginal checks cannot identify",
        SECTION41,
    )
    text = replace_section(
        text,
        "### 4.3 Control-channel interactions",
        "### 4.4 The favored persona-level result is not prospectively confirmed; the archived family is underpowered",
        SECTION43,
    )
    text = text.replace(
        "The underlying continuous evidence is clearer than the thresholded label: prompt identity accounts for most estimated variation, many cells lie near behavioral boundaries, and the continuation-probability point differences are small but uncertain.",
        "The underlying continuous evidence is clearer than the thresholded label: plug-in estimates assign most observed variation between prompts, and the fixed-panel latent-propensity sensitivity still places posterior medians above one-half while substantially widening and lowering the intervals.",
    )
    temperature_old = "The temperature observation lacks an identified mechanism, the high-temperature δ interaction is not estimable under the registered design, and the Gemini tier is descriptive under documented endpoint non-stationarity."
    temperature_new = "The temperature observation lacks an identified mechanism, the high-temperature δ interaction is not estimable under the registered design, and the Gemini tier is descriptive under documented endpoint non-stationarity. Because choice entropy fell rather than rose over the registered temperature sweep, boundary concentration at T=0.7 cannot be attributed to persona conditioning in isolation; a prospectively crossed temperature × persona-prefix design is needed to partition those contributions."
    text = text.replace(temperature_old, temperature_new)

    anchor = "| Figures 1 and 5 corrected for aggregate markers and candidate attribution | Explore Science C1/C2 | Figure integrity |"
    rows = """| Human SD references, thresholds, broad-reference band, failing cell, condition matrix, restricted denominator, P5-2 counts, and 24-lane construction reported in text | Explore Science v10 C1/C2/C4–C7 | Reporting completeness |
| Fixed-panel Dirichlet–Jeffreys latent-propensity sensitivity added to propagate boundary-cell uncertainty without changing the prompt panel | Explore Science v10 C3 | Uncertainty interpretation |
| Figures 1, 2, 3, and 5 redrawn for dodging, unit consistency, dual uncertainty views, and reference-line labels | Explore Science v10 D1–D4 | Figure integrity |
| Bare-configuration and represented-treatment qualifiers added to abstract; S2 sentence quoted and defined | Explore Science v10 A2/A3/C10 | Construct precision |"""
    if rows.splitlines()[0] not in text and anchor in text:
        text = text.replace(anchor, anchor + "\n" + rows, 1)

    for reference in (
        "Berger, J. O., Bernardo, J. M., and Sun, D. (2009). The formal definition of reference priors. *Annals of Statistics, 37*(2), 905–938. https://doi.org/10.1214/07-AOS587",
        "Efron, B., and Tibshirani, R. J. (1993). *An Introduction to the Bootstrap*. Chapman & Hall/CRC. https://doi.org/10.1007/978-1-4899-4541-9",
        "Holtzman, A., Buys, J., Du, L., Forbes, M., and Choi, Y. (2020). The curious case of neural text degeneration. In *International Conference on Learning Representations*.",
    ):
        if reference not in text:
            text = text.replace(
                "Clopper, C. J., and Pearson",
                reference + "\n\nClopper, C. J., and Pearson",
                1,
            )
    text = text.replace(
        "*End of text-freeze review copy v10.*",
        "*End of post-freeze review revision v11.*",
    )
    PAPER.write_text(text, encoding="utf-8")
    update_navigation()
    print("apply_explore_v11: manuscript and review navigation revised")


if __name__ == "__main__":
    main()
