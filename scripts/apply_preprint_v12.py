#!/usr/bin/env python3
"""Integrate the verified v12 audits into a clean near-arXiv manuscript.

This edits living paper/repository surfaces only. Sealed registrations, historical
adjudications, raw events, and the v10/v11 review artifacts remain unchanged.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "docs" / "paper" / "paper-draft.md"
README = ROOT / "README.md"
REVIEW = ROOT / "REVIEW.md"
CITATION = ROOT / "CITATION.cff"
STATUS = ROOT / "docs" / "analysis" / "submission-blockers.md"
AUDIT = ROOT / "docs" / "analysis" / "submission" / "v12" / "v12-audits.json"
P3 = ROOT / "docs" / "analysis" / "submission" / "v12" / "phase3-replay-audit.json"


def replace_section(text: str, start: str, end: str, replacement: str) -> str:
    pattern = re.escape(start) + r".*?(?=" + re.escape(end) + r")"
    new, count = re.subn(pattern, lambda _m: replacement.rstrip() + "\n\n", text, count=1, flags=re.DOTALL)
    if count != 1:
        raise RuntimeError(f"expected one section {start!r} -> {end!r}, replaced {count}")
    return new


def replace_paragraph(text: str, starts: str, replacement: str) -> str:
    pattern = re.escape(starts) + r".*?(?=\n\n)"
    new, count = re.subn(pattern, lambda _m: replacement.rstrip(), text, count=1, flags=re.DOTALL)
    if count != 1:
        raise RuntimeError(f"expected paragraph starting {starts!r}, replaced {count}")
    return new


def pct(x: float, digits: int = 1) -> str:
    return f"{100*x:.{digits}f}%"


def f(x: float, digits: int = 3) -> str:
    return f"{x:.{digits}f}"


def format_leaning_table(rows: list[dict]) -> str:
    lines = [
        "| condition | cooperative-leaning mean | defect-leaning mean | difference | prompts per stratum |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['cell']}` | {row['cooperativeLeaningMean']:.3f} | "
            f"{row['defectLeaningMean']:.3f} | {row['difference']:+.3f} | "
            f"{row['cooperativeLeaningPrompts']} |"
        )
    return "\n".join(lines)


def entropy_records(audit: dict, scope: str) -> list[dict]:
    return [r for r in audit["entropy"]["records"] if r["scope"] == scope]


def entropy_table(audit: dict) -> str:
    rows = entropy_records(audit, "matched-sweep-units")
    lines = [
        "| temperature | matched units | seats | pooled Shannon entropy (bits) | mean within-unit entropy (bits) |",
        "|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['temperature']:.1f} | {row['units']} | {row['seats']} | "
            f"{row['pooledShannonBits']:.4f} | {row['meanUnitShannonBits']:.4f} |"
        )
    return "\n".join(lines)


def main() -> int:
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    p3 = json.loads(P3.read_text(encoding="utf-8"))
    if audit.get("status") != "complete":
        raise RuntimeError("v12 audits are not complete")
    if p3.get("verdict") != "PASS — CLEAN":
        raise RuntimeError(f"Phase 3 replay is not clean: {p3.get('verdict')}")

    bootstrap = audit["bootstrapCoincidence"]
    leaning = audit["leaningStrata"]
    entropy = audit["entropy"]
    decoding = audit["decoding"]
    lo_values = [r["lo025"] for r in bootstrap["independentRuns"]]
    lo_min, lo_max = min(lo_values), max(lo_values)
    p3_totals = p3["totals"]
    registered_phase3_llm = sum(p3["expectedPromptCounts"].values())
    total_confirmatory = registered_phase3_llm + p3_totals["baselineRuns"] + 2864 + 1712
    total_llm_replayed = registered_phase3_llm + 2864 + 1712

    manuscript = PAPER.read_text(encoding="utf-8")
    title_line, rest = manuscript.split("\n", 1)
    rest = re.sub(
        r"^\s*\*\*STATUS:.*?\n\n",
        "**Preprint v12 (July 2026).** Historical registrations and mechanical verdicts are preserved verbatim; all post-adjudication analyses are labeled as such. The public repository contains the complete research record, version history, and zero-call replay capsule.\n\n",
        rest,
        count=1,
        flags=re.DOTALL,
    )
    manuscript = title_line + "\n" + rest
    manuscript = re.sub(
        r"\*\*Artifacts \(public\):\*\*.*?\n",
        f"**Artifacts (public):** github.com/yoheinakajima/synthetic-players — anonymous clone and one-command zero-credential verifier; {total_confirmatory:,} Phase 3–5 runs verified ({total_llm_replayed:,} LLM runs replayed byte-exact plus {p3_totals['baselineRuns']} deterministic baselines independently recomputed); prompt registries and freeze records are externally anchored.\n",
        manuscript,
        count=1,
    )

    abstract = f"""## Abstract

Large language models are increasingly used as synthetic research participants, but they are often validated by whether their marginal responses resemble published human data. We report a five-phase research program whose confirmatory claims from Phases 3–5 were registered before their adjudicating data and mechanically evaluated from an event-sourced record. A fixed panel of sixteen lightweight persona-conditioned GPT-4.1 configurations passed preregistered broad-reference checks for condition-level cooperation in three of four repeated-game cells. A fixed-panel Dirichlet–Jeffreys latent-propensity sensitivity yields posterior median between-prompt shares of 63%–71%, with 95% intervals spanning 49%–81%; finite-opportunity plug-in estimates that condition more strongly on the observed boundary concentration are 85%–96%. The observed aggregate continuation-probability contrasts are +0.083 and +0.078 across two wording families, with conservative exact simultaneous 95% intervals [−0.171, +0.330] and [−0.181, +0.330] (rounded to three decimals). Their width jointly reflects six independent episodes per prompt-cell and an exact construction that retains uncertainty at empirical corners. The treatment changed both the continuation process and the language communicating it, leaving incentive and framing channels undecomposed. Separate representation experiments showed that, in the bare configuration, replacing and repositioning one continuation sentence shifted cooperation from 0/40 to 37/40 on held-out decisions, and that a displayed action label or label-linked learned prior could override payoff dominance in one registered conflict cell. External review exposed family-error, dependence, and boundary-uncertainty defects; zero-call reanalysis changed the scientific interpretation without rewriting the historical record. The public capsule now verifies all {total_confirmatory:,} Phase 3–5 runs with no live model calls. Human references are protocol-nonmatched, the results concern one fixed model–persona panel, and we do not claim human substitutability.
"""
    manuscript = replace_section(manuscript, "## Abstract", "## 1. Introduction", abstract)

    contributions = """**Contributions.** First, we provide a registered strategic-interaction example in which a fixed persona panel passes coarse condition-level and dispersion checks while aggregate continuation-probability point differences remain imprecisely estimated; the design does not establish equivalence or a narrow response bound (§4.1). Second, we quantify the associated composition problem with three explicitly different uncertainty views: a fixed-panel latent-propensity posterior, finite-opportunity plug-in estimates, and an exploratory persona-generator bootstrap; the first places median between-prompt shares at 63%–71%, while representation experiments show how wording and displayed labels or learned game priors govern the induced policies (§4.1–4.3). Third, we demonstrate an auditable reliability protocol—and its limits—through prospective registration, external chronology, mechanical adjudication, complete zero-call replay of the confirmatory record, and public correction of family-error and construct-validity defects (§4.4–4.5)."""
    manuscript = replace_paragraph(manuscript, "**Contributions.**", contributions)

    methods_intro = """The primary deployment is gpt-4.1 with 16-token outputs and a fixed minimal behavioral-subject prompt containing no game-theory vocabulary or reasoning scaffold. Temperature was 0.7 except in the registered Phase 5 sweep at 1.0 and 1.3. On the primary OpenAI-compatible path, `temperature` and `max_tokens=16` were explicitly supplied; the assembled prompt set `top_p=1.0`, which the adapter intentionally omitted from the wire at 1.0, while `presence_penalty`, `frequency_penalty`, and `logit_bias` were not supplied and therefore inherited provider defaults. No tools or native structured output were used. Phase 5 prepends one sealed persona sentence to byte-identical task text. The cross-vendor Gemini tier is descriptive; the original Claude Haiku candidate failed a registered entry gate and was replaced under an archived amendment. Environment randomness is seeded; provider-side generation is not claimed to be seeded. Every request, rendered prompt, completion, decoding configuration, round, and provenance record is archived."""
    manuscript = replace_paragraph(manuscript, "The primary deployment is gpt-4.1", methods_intro)

    manuscript = manuscript.replace(
        "The full event store contains 5,505 completed runs, 54,276 round events, 108,552 seat-round decisions, and 36,251 archived provider-request events. The public Phase 4–5 replay contract covers 4,576 completed runs.",
        f"The full event store contains 5,505 completed runs, 54,276 round events, 108,552 seat-round decisions, and 36,251 archived provider-request events. The public confirmatory replay contract now verifies {total_confirmatory:,} Phase 3–5 runs: {registered_phase3_llm} registered Phase 3/X1 LLM runs, {p3_totals['baselineRuns']} deterministic Phase 3 baselines, 2,864 Phase 4 runs, and 1,712 Phase 5 runs; three additional completed legacy entry/diagnostic runs are also replayed but are not counted as confirmatory.",
    )

    glossary = """**Protocol glossary.** `S2-absent` and `S2-present` are the registered repeated-game wording families. **switch-bearing** means the span whose adjacent substitution produced the largest preregistered ladder gap and subsequently passed held-out confirmation; S2-present contains that replacement-and-reposition operation, while S2-absent contains the original sentence. `P3-A3` is the Phase 3 registered broad-reference cooperation claim, with band [0.36, 0.63]. `P5-1a`, historically called the **corner-mixture predicate**, is the registered support condition that fires when the interior fraction in the exact-bare-twin restricted set is below 0.10 under the frozen seat-level rule; it is not a general theorem about mixture structure. `P5-1b` is the registered between-persona dispersion comparison. `P5-2` pools registered conflict cells and classifies whether choices follow task text or persona-conditioned direction. `P5-3(a)`—clause (a)—asks whether any persona × wording pair has both continuation-probability cells interior and a positive slope lower bound; `P5-3(b)`—clause (b)—asks whether each persona lane rejects the bare configuration’s dominated swap-cell option at a registered minimum rate. Historical verdict labels remain visible even where post-adjudication analyses change their scientific interpretation."""
    manuscript = re.sub(
        r"\*\*Protocol glossary\.\*\*.*?(?=\n\n\*\*Phase 5 condition matrix)",
        glossary,
        manuscript,
        count=1,
        flags=re.DOTALL,
    )

    leaning_table = format_leaning_table(leaning)
    gap_min = min(r["difference"] for r in leaning)
    gap_max = max(r["difference"] for r in leaning)
    stored_lower = bootstrap["storedLowerBound"]
    latent = {
        "rep-d10-s2a": (0.631, 0.494, 0.745),
        "rep-d10-s2p": (0.705, 0.573, 0.813),
        "rep-d90-s2a": (0.661, 0.528, 0.770),
        "rep-d90-s2p": (0.665, 0.528, 0.777),
    }
    section41 = f"""### 4.1 Coarse marginal checks pass while represented-treatment estimates remain imprecise

The preregistered leaning rule—at least two of agreeable, patient, and risk-averse—divides the fixed panel into eight cooperative-leaning and eight defect-leaning complete prompts. The descriptive gaps range from {gap_min:.3f} to {gap_max:.3f} across every non-swap condition:

{leaning_table}

These are fixed-panel prompt-bundle contrasts, not causal estimates for any trait. The P3-A3 broad-reference cooperation band is [0.36, 0.63]. The four repeated-game pool means are 0.349 (`rep-d10-s2a`), 0.427 (`rep-d10-s2p`), 0.432 (`rep-d90-s2a`), and 0.505 (`rep-d90-s2p`); only the S2-absent δ=.10 cell falls outside the band, by 0.011 below its lower boundary.

P5-1b used protocol-nonmatched human SD references mechanically implied from Dal Bó and Fréchette’s [2011] R=40 strategy-frequency estimates: 0.4122 for their δ=.50 panel and 0.3116 for δ=.75. The frozen ratio ρ=.75 gives thresholds 0.3092 and 0.2337. Finite-opportunity-corrected plug-in SDs are 0.4182, 0.4784, 0.4408, and 0.4323, and all exceed the historical thresholds.

The uncertainty-propagating fixed-panel view is more conservative. Independent Dirichlet(0.5,0.5,0.5) posteriors for each prompt/cell outcome distribution yield between-prompt-share medians of 63.1%, 70.5%, 66.1%, and 66.5%, with 95% intervals [49.4%, 74.5%], [57.3%, 81.3%], [52.8%, 77.0%], and [52.8%, 77.7%]. The corresponding latent-SD medians are 0.3543, 0.3959, 0.3698, and 0.3620. Three of four lower bounds exceed the historical SD threshold; `rep-d10-s2a` is effectively on it (0.3090 versus 0.3092).

For comparison, finite-opportunity plug-in shares are 85.5%, 96.1%, 88.8%, and 90.2%. A conditional episode bootstrap that resamples the empirical distribution of each fixed prompt produces corrected-SD intervals [0.4122, 0.4391], [0.4696, 0.4916], [0.4279, 0.4654], and [0.4269, 0.4496], but empirically unanimous cells remain point masses in that bootstrap. The visually suspicious first lower bound is genuine: the stored full-precision value is {stored_lower:.6f}; an independent implementation that imports neither the original variance routine nor human constants produced 2.5th-percentile bounds from {lo_min:.6f} to {lo_max:.6f} across three {bootstrap['independentRuns'][0]['reps']:,}-replicate seeds. Its equality to the displayed human reference at four decimals is a rounding coincidence, not a computational link. A two-stage prompt+episode bootstrap changes the estimand toward a hypothetical persona generator and yields still wider SD intervals: [0.2724, 0.4879], [0.3696, 0.5123], [0.3457, 0.4890], and [0.3345, 0.4847]. Thus the robust statement is that between-prompt composition is substantial and likely dominant in this fixed panel; 85%–96% are conditional plug-in point estimates, not fully uncertainty-adjusted population facts.

Across the represented continuation-probability treatment, the observed fixed-panel point differences are +0.083 for S2-absent wording and +0.078 for S2-present wording. Conservative exact simultaneous 95% intervals are [−0.171, +0.330] and [−0.181, +0.330] (rounded to three decimals). Their breadth jointly reflects the registered six-episode-per-cell design and an exact projection that retains non-zero uncertainty at empirical corners. The treatment changes both the continuation process and the text used to communicate it; round-one actions identify response under a specified representation, not a semantically neutral economic parameter. The point estimates are small on the unit scale, but the data do not establish equivalence, a zero response, or a narrow upper bound.

For the finite archived panel, +0.083 and +0.078 are exact descriptive arithmetic. The intervals instead address repeated-sampling uncertainty about latent propensities. A design-effect heuristic using six episodes per prompt and the plug-in between-share range 0.855–0.961 gives roughly 16.5–18.2 episode equivalents per condition, close to the sixteen prompt units. This is not the degrees of freedom of the exact procedure, but it identifies prompt count as the operative precision constraint.

Dal Bó and Fréchette [2011] remain protocol-nonmatched context: their continuation probabilities, payoffs, monetary incentives, between-session assignment, and repeated-supergame experience differ from this study. We make no matched magnitude or human-equivalence claim.

The registered Gemini tier was descriptive and endpoint-nonstationary. Nine of 24 Gemini cells met the historical interiority rule, versus 14/96 in the primary panel, and several representation effects reversed direction. This is contrary descriptive evidence that the composition pattern is deployment-specific, not a formal replication comparison.

![Prompt-indexed continuation-probability responses](figures/prompt-indexed-delta.svg)

*Figure 1. Prompt-indexed differences in round-one cooperation, \(\Delta_i=\hat p_i(\delta=.90)-\hat p_i(\delta=.10)\), for both wording families. Bars are conservative exact simultaneous 95% intervals with complete episodes as the unit; observed corners retain non-zero uncertainty. Diamonds show fixed-panel aggregates. Rows at \(\Delta_i=0\) can reflect boundary concentration in both recorded cells and are not precise evidence of no response.*

![Condition-level cooperation means](figures/condition-means.svg)

*Figure 2. Fixed-panel cooperation by represented continuation-probability condition. Error bars are conservative exact condition intervals; lines connect conditions for orientation only.*

![Between-prompt variance share](figures/between-prompt-share.svg)

*Figure 3. Between-prompt share of episode-level variation. The uncertainty-propagating Dirichlet–Jeffreys fixed-panel posterior is the primary interpretive sensitivity; plug-in/conditional-bootstrap estimates are shown as a complementary description of the archived concentration. The two-stage prompt bootstrap changes the estimand and is reported in text.*

Across all six Phase 5 conditions, the historical seat-level rule classifies 14/96 persona–condition cells interior, the exact episode projection 11/96, and the Dirichlet–Jeffreys sensitivity 19/96. In the registered 32-unit set, the counts are 3/32, 2/32, and 5/32. At n=6 with a three-valued discrete outcome, modest differences in interval width deterministically move cells across the threshold; the divergence reflects both interval construction and low discrete-sample resolution. The continuous posterior and variance components are therefore more informative than the binary census.
"""
    manuscript = replace_section(manuscript, "### 4.1", "### 4.2", section41)

    section43 = """### 4.3 Control-channel interactions

For the bare configuration, round-one cooperation was 0.000 at every registered continuation probability. X2 decomposed the v1 and v2a prompt bundles into six sentence/block spans and constructed forward and reverse ladders by replacing one complete span at a time. The selected S2 operation replaced and repositioned “After every round there is a {deltaPct}% chance the session continues with another round” with “At the end of each round there is a {deltaPct}% chance that the session goes on for one more round.” Screening used ten episodes per rung; the selected minimal pair was confirmed at temperature 0.7 on 20 fresh episodes per side (seeds 2953–2972), moving cooperation from 0/40 to 37/40. Because wording and position were one atomic operation, the design does not separate them.

In the label-swap cell, canonical payoffs were held fixed while “Cooperate” and “Defect” were attached to opposite strategic roles. The bare configuration chose the cooperation-worded option 0/40 times and instead took the payoff-dominated role whenever it carried the word “Defect.” This shows that the displayed label or a label-linked learned prior can override payoff dominance in this registered cell. It does not identify intrinsic lexical valence: a learned game-theoretic association such as “Defect = equilibrium/dominant action in Prisoner’s Dilemma” is an equally plausible mechanism. A structurally equivalent non-PD control retaining the same labels was not run.

Persona conditioning produces two observed contrasts, but they are not factorially separable. Differences among complete persona prompts generate the leaning gaps reported in §4.1. Adding any tested persona string reverses the bare swap-cell choice, yet no non-semantic prefix matched for length, punctuation, and position was run; semantic persona content cannot be isolated from generic sequence-format disruption. In the swap cell, label and payoff also point to the same option for persona-conditioned configurations, leaving the reversal mechanism ambiguous.

P5-3(b)’s 24 evaluable lanes comprise sixteen personas at T=0.7 plus p02, p06, p11, and p15 at each of T=1.0 and T=1.3. Every lane retains a simultaneous episode-exact lower bound above the frozen 0.20 threshold; the minimum is 0.462. The pooled P5-2 task-consistent share is 90/704 seat decisions across 352 episodes, equivalently 45/352=0.128 on episode means, with exact interval [0.092, 0.172]. Every repeated conflict subcell is mixed; only the swap cell is individually persona-dominant. The pooled verdict is therefore carried by the mechanism-confounded swap cell.

![Representation-channel corner shifts](figures/representation-effects.svg)

*Figure 4. Two representation interventions in the bare configuration. The S2 wording-and-position operation moved cooperation from 0/40 to 37/40. In the one-shot label conflict, the payoff-dominant action was never chosen when the dominated role carried “Defect.” These bars report selection shares, not a common or uniquely identified causal mechanism.*
"""
    manuscript = replace_section(manuscript, "### 4.3", "### 4.4", section43)

    marker = "The record neither prospectively confirms nor decisively disconfirms p13; it identifies a replication target whose next test must be sized prospectively (Appendix A.4)."
    replacement = marker + " A Phase 6 test will preregister the candidate family, episode-level dependence unit, interiority gate, maximum statistic, familywise decision rule, and sample size before any data are collected."
    if marker not in manuscript:
        raise RuntimeError("missing Phase 6 insertion marker")
    manuscript = manuscript.replace(marker, replacement, 1)

    manuscript = manuscript.replace(
        "The public capsule replays all 4,576 Phase 4–5 runs exactly with zero live model calls.",
        f"The public capsule now verifies all {total_confirmatory:,} confirmatory Phase 3–5 runs with zero live model calls: {total_llm_replayed:,} LLM runs replay byte-exact and {p3_totals['baselineRuns']} deterministic baselines are independently recomputed.",
    )
    manuscript = manuscript.replace(
        "For deployment, behavior that can be rewritten by a sentence, an action token, or an identity prefix is safety-relevant. The results do not imply that language always dominates incentives: in some cells numerical payoffs move behavior strongly, and precedence depends on representation and conflict structure.",
        "For deployment, behavior that can be rewritten by a sentence, an action token, or an identity prefix is safety-relevant. The label-conflict result does not show that lexical valence always dominates incentives: numerical payoffs move behavior in other cells, and the observed choice may reflect semantic framing, learned game-theoretic priors, or their interaction.",
    )

    matched = entropy_records(audit, "matched-sweep-units")
    pooled_values = ", ".join(f"{r['pooledShannonBits']:.4f}" for r in matched)
    unit_values = ", ".join(f"{r['meanUnitShannonBits']:.4f}" for r in matched)
    limitations = f"""## 6. Limitations

The primary evidence comes from one deployment and sixteen complete prompt bundles. Generalization to a persona generator, other models, or human participants is not identified. The uncertainty views answer different questions: the latent-propensity posterior is prior-dependent, the plug-in/conditional bootstrap conditions on recorded boundary concentration, and the two-stage bootstrap changes the estimand by resampling prompts.

The treatment-response intervals are wide because each prompt-cell has six independent episodes and the exact projection retains uncertainty at empirical corners. The binary interior census is correspondingly sensitive to small-n discrete interval width. Explicit persona strings are paired across conditions, but latent-person invariance is untested. The continuation process was manipulated together with its textual representation. The persona-prefix contrast lacks a format-matched neutral control. The label-swap result cannot distinguish semantic valence from memorized game-theoretic associations because no non-PD control retained the same labels.

The registered choice-entropy secondary was base-2 Shannon entropy of pooled round-one payoff-role choices. Historical pooled temperature groups had different unit composition; on the identical matched sweep lattice, pooled entropy at T=0.7, 1.0, and 1.3 was {pooled_values} bits, while mean within-unit empirical entropy was {unit_values} bits. The registered pooled decline is partly composition-confounded but survives on the identical sweep lattice. Pooled and mean within-unit entropy capture different objects, and neither identifies a mechanism. The high-temperature continuation interaction was not registered, and the Gemini tier is descriptive under endpoint non-stationarity.

Human references are published and protocol-nonmatched. The original familywise analyses were specified after review and cannot create retrospective confirmation. The exact n=6 family is underpowered by construction; p13 remains a replication target, not evidence for or against a general capability envelope.
"""
    manuscript = replace_section(manuscript, "## 6. Limitations", "## 7. Reproducibility", limitations)

    reproducibility = f"""## 7. Reproducibility and data availability

The public repository contains the event stores, prompt registries, sealed registrations, adjudication records, timestamp proofs, post-adjudication analyses, figures, manuscript history, and review record. The one-command capsule verifies all {total_confirmatory:,} confirmatory Phase 3–5 runs with zero credentials and zero live model calls. The audit covers {registered_phase3_llm} registered Phase 3/X1 LLM runs, {p3_totals['baselineRuns']} deterministic Phase 3 baselines, 2,864 Phase 4 runs, and 1,712 Phase 5 runs; three additional completed legacy entry/diagnostic runs are also replayed but are not counted as confirmatory. Phase 3 replay re-renders every prompt, requires recorded-cache hash hits, reparses raw completions, recomputes actions, payoffs, and RNG draw counts, and checks recorded call parity. The deterministic P3-C3 baseline is independently recomputed from archived seeds and game objects.

Phase 3 used a legacy provider path without Phase 4–5 response IDs or deterministic request-body SHA capture. Phase 4–5 contain 30,421 normal request events and 30,397 response events; the 24-event difference is the disclosed provider-failure partial set. Those response records contain rendered prompts, bundle and request-body hashes, engine commit and provider route, raw text, and provider response IDs. Individual completion payloads were not provider-attested or separately hash-chained at receipt. Capsule checksum manifests and external timestamps make the released database snapshot tamper-evident relative to publication; replay cannot prove that no alteration occurred before snapshot sealing.

Reproduce the confirmatory record with:

```bash
git clone https://github.com/yoheinakajima/synthetic-players
cd synthetic-players/capsule
bash verify.sh
```

All post-adjudication analyses are zero-call scripts over the archived databases and are labeled separately from prospectively registered results.
"""
    manuscript = replace_section(manuscript, "## 7. Reproducibility", "## 8. Attribution", reproducibility)

    appendix = f"""## Appendix A — Supplementary scope and prospective design

### A.1 Temperature secondary

Choice entropy is defined as base-2 Shannon entropy, \(H=-\sum_a p(a)\log_2p(a)\), over round-one payoff-role choices. The historical registered secondary pooled all valid choices at each temperature, but the T=0.7 and higher-temperature samples had different composition. The matched-sweep reanalysis uses only persona-cell lanes observed at all three temperatures:

{entropy_table(audit)}

The registered pooled decline is partly composition-confounded but survives on the identical sweep lattice. Mean within-unit entropy is reported separately because pooled entropy can remain high when different prompt-cell units occupy opposite boundaries. Neither statistic identifies a temperature mechanism.

### A.2 Other supplementary findings

RPS retained a role-attached rock bias after neutral symbols and randomized order, with a cross-vendor sign reversal. The adversary suite showed opponent-contingent sequential structure. A sentinel case study documents endpoint drift and the resulting monitoring repair. These results and the Claude Haiku entry-gate failure remain in the public supplementary record but are outside the main causal arc.

### A.3 Prospective replication

A Phase 6 replication will preselect one target or a small candidate family and preregister the complete familywise procedure: candidate set, episode-level unit, interiority gate, maximum statistic, decision threshold, and sample size. It should also include a format-matched neutral prefix, a continuation-probability × wording factorial, and a structurally equivalent non-PD label-conflict control. The registered power calculation must simulate the exact decision rule under its declared dependence model rather than reuse the archived 32-candidate search.

### A.4 Research record

The complete correction ledger, sealed discussion text, dead-predictions ledger, reviewer-role disclosures, and mechanical v11→v12 disposition matrix are maintained in `docs/reviews/` and `docs/analysis/submission/`. Historical artifacts are never silently rewritten; current interpretations are linked to the versions they amend.
"""
    manuscript = replace_section(manuscript, "## Appendix A", "## References", appendix)

    manuscript = re.sub(
        r"\n\*End of post-freeze review revision v11\.\*\s*$",
        "\n",
        manuscript,
    )
    manuscript = manuscript.replace("*End of post-freeze review revision v11.*", "")
    manuscript = re.sub(r"(?i)review revision v11", "post-adjudication revision", manuscript)
    manuscript = re.sub(r"(?i)not for citation", "", manuscript)
    PAPER.write_text(manuscript, encoding="utf-8")

    readme = README.read_text(encoding="utf-8")
    readme = re.sub(r"> \*\*STATUS:.*?\*\*", "> **STATUS: PREPRINT v12 — NEAR-ARXIV MANUSCRIPT AND COMPLETE PUBLIC RECORD.**", readme, count=1)
    readme = readme.replace("synthetic-players-review-v11.pdf", "synthetic-players-preprint-v12.pdf")
    readme = readme.replace("Current v11 review-revision Markdown manuscript", "Current v12 preprint Markdown manuscript")
    readme = re.sub(
        r"> A fixed panel of sixteen lightweight persona prompts passed preregistered \*\*coarse marginal checks\*\*\..*?\n\n",
        "> A fixed panel of sixteen lightweight persona prompts passed preregistered **coarse marginal checks**. A fixed-panel latent-propensity sensitivity yields median between-prompt shares of 63%–71% (95% intervals 49%–81%); conditional plug-in estimates are 85%–96%. Aggregate continuation-probability contrasts are +0.083 and +0.078 with wide exact intervals, so the study does not establish equivalence or a narrow response bound.\n\n",
        readme,
        count=1,
        flags=re.DOTALL,
    )
    readme = readme.replace("4,576/4,576 completed Phase 4–5 runs replay byte-exact.", f"{total_confirmatory:,}/{total_confirmatory:,} confirmatory Phase 3–5 runs verified with zero live model calls.")
    README.write_text(readme, encoding="utf-8")

    review = REVIEW.read_text(encoding="utf-8")
    review = review.replace("synthetic-players-review-v11.pdf", "synthetic-players-preprint-v12.pdf")
    review = review.replace("Current v11 review-revision Markdown manuscript", "Current v12 preprint Markdown manuscript")
    review = re.sub(
        r"> \*\*CURRENT REVIEW SURFACE:.*?\n",
        "> **CURRENT PREPRINT SURFACE:** begin with this file, the v12 PDF, and `docs/paper/paper-draft.md`.\n",
        review,
        count=1,
    )
    review = review.replace("4,576/4,576 Phase 4–5 runs", f"{total_confirmatory:,}/{total_confirmatory:,} Phase 3–5 runs")
    REVIEW.write_text(review, encoding="utf-8")

    cff = CITATION.read_text(encoding="utf-8")
    cff = re.sub(r'message: ".*?"', 'message: "Please cite the preprint and software record below."', cff, count=1)
    cff = re.sub(r'version: ".*?"', 'version: "preprint-v12"', cff, count=1)
    if "preferred-citation:" not in cff:
        cff += """
preferred-citation:
  type: article
  title: "Passing Coarse Marginal Checks Can Be Cheap: Persona Mixtures and Imprecise Treatment-Response Estimates in an LLM Persona Panel"
  authors:
    - family-names: Nakajima
      given-names: Yohei
  year: 2026
  url: "https://github.com/yoheinakajima/synthetic-players"
"""
    CITATION.write_text(cff, encoding="utf-8")

    if STATUS.exists():
        status = STATUS.read_text(encoding="utf-8")
        status = re.sub(
            r"^# .*",
            "# Preprint v12 status — scientific revision complete",
            status,
            count=1,
        )
        status = re.sub(
            r"> \*\*STATUS:.*?\n",
            "> **STATUS: COMPLETE FOR NEAR-ARXIV REVIEW.** All v11 issues are dispositioned; remaining changes are venue metadata and formatting only.\n",
            status,
            count=1,
        )
        STATUS.write_text(status, encoding="utf-8")

    print(
        json.dumps(
            {
                "paper": str(PAPER),
                "confirmatoryRunsVerified": total_confirmatory,
                "llmRunsReplayed": total_llm_replayed,
                "bootstrapLowerRange": [lo_min, lo_max],
                "leaningGaps": [gap_min, gap_max],
                "decoding": decoding["primaryOpenAIPath"],
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
