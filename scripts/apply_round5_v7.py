#!/usr/bin/env python3
"""Integrate Explore Science Round 5 findings into the living v7 manuscript.

This script reads only post-adjudication audit outputs and edits only living
paper/review/navigation files. It does not modify sealed registrations,
adjudications, precommitted discussion text, raw event data, or historical
mechanical verdicts.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "docs" / "paper" / "paper-draft.md"
AUDIT_JSON = ROOT / "docs" / "analysis" / "submission" / "round5" / "round5-review-audit.json"


def replace(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise RuntimeError(f"missing expected text for {label}")
    return text.replace(old, new, 1)


def insert_before(text: str, marker: str, block: str, label: str) -> str:
    if block.strip() in text:
        return text
    if marker not in text:
        raise RuntimeError(f"missing marker for {label}: {marker[:80]}")
    return text.replace(marker, block.rstrip() + "\n\n" + marker, 1)


def fmt(x: float, digits: int = 6) -> str:
    return f"{x:.{digits}f}"


def update_paper(audit: dict) -> None:
    path = PAPER
    text = path.read_text(encoding="utf-8")
    dynamic = audit["dynamicGate"]
    n6 = audit["exactGateAttainability"]["n6"]
    tail = audit["exactGateAttainability"]["currentFamilyTailAtMaxAttainableSlope"]
    prov = audit["provenance"]
    p45_req = prov.get("requestedCoverage", {}).get("phase4-5", {})
    p45_resp = prov.get("respondedCoverage", {}).get("phase4-5", {})

    text = text.replace("WORKING DRAFT v6 — EXPLORE SCIENCE REVIEW DRAFT", "WORKING DRAFT v7 — ROUND 5 RESPONSE DRAFT")
    text = text.replace("*End of working draft v6.*", "*End of working draft v7.*")

    # Methods: architecture, glossary, bootstrap rationale.
    phase_table = """### 3.1 Sequential architecture and registration status

| Stage | Primary question and role | Unit used in the paper | Registration status |
|---|---|---|---|
| Phase 1 | Initial prototype and naive behavioral claims; establishes the historical baseline, not current confirmatory evidence | provider calls / recorded decisions | post hoc instrument development |
| Phase 2 | Mechanical re-adjudication and enforcement repair after the initial harness exposed analyst discretion | archived runs and claim predicates | corrective, not prospective confirmation |
| Phase 3 | Bare GPT-4.1 configuration in repeated PD, framing, and RPS | episode, with historical seat-level summaries disclosed | claims registered before Phase 3 data |
| Phase 4 | Representation robustness, X1/X2 wording extensions, counterfactual payoffs/labels, continuation-probability assays, adversaries, and sentinels | complete episode for current sensitivities | X1 was result-informed but registered before X1 data; the remaining blocks were registered before their own data |
| Phase 5 | Sixteen sealed persona-prefix configurations crossed with the Phase 4 instruments; descriptive Gemini tier | complete persona prompt for the fixed panel; episode beneath it | confirmatory predicates registered before Phase 5 data; post-adjudication sensitivities are explicitly unregistered |

The present paper’s main empirical decomposition is Phase 5, interpreted using representation results from Phases 3–4. Phases 1–2 document instrument evolution and are not counted as prospective confirmation."""
    text = insert_before(text, "The full event store contains", phase_table, "phase architecture")

    glossary = """**Protocol glossary.** `S2-absent` and `S2-present` are the two registered repeated-game wording families: the latter includes the switch-bearing continuation sentence localized in X2, while the former omits that sentence. `P5-1a` is the registered fraction of selected persona–condition cells classified interior, with support for the corner-mixture predicate when that fraction is below 0.10; `P5-1b` is the registered between-persona dispersion comparison. `P5-2` pools registered conflict cells and classifies whether choices follow task text or persona-conditioned direction. `P5-3(a)` asks whether any persona × wording pair has both continuation-probability cells interior and a positive slope lower bound; `P5-3(b)` asks whether each persona lane rejects the bare configuration’s dominated, semantically attracted swap-cell option at a registered minimum rate. Historical alphanumeric verdicts remain visible even where post-adjudication sensitivities change their scientific interpretation."""
    text = insert_before(text, "The machinery’s boundary is explicit:", glossary, "protocol glossary")

    text = replace(
        text,
        "A Dirichlet–Jeffreys interval is reported as a Bayesian sensitivity. The percentile cluster bootstrap is also retained in the audit trail but rejected as the primary interval because it becomes degenerate at exact corners.",
        "A Dirichlet–Jeffreys interval is reported as a Bayesian sensitivity. The percentile cluster bootstrap is also retained as a post-adjudication sensitivity. The exact Clopper–Pearson projection is the conservative reference because it provides finite-sample coverage for the discrete episode mean; at n=6 the percentile bootstrap has no comparable coverage guarantee and can understate uncertainty. Its degeneracy at exact corners is a symptom of that limitation, not by itself a false-positive mechanism for this strict interiority gate.",
        "bootstrap rationale",
    )

    # Results 4.1: heading, wording definitions, represented-treatment caveat, Gemini pointer.
    text = text.replace(
        "### 4.1 Coarse marginal checks pass while the observed incentive response is small",
        "### 4.1 Coarse marginal checks pass while represented-treatment estimates remain imprecise",
    )
    text = replace(
        text,
        "Across the continuation-probability manipulation, the observed fixed-panel point differences are +0.083 for S2-absent wording and +0.078 for S2-present wording.",
        "Across the represented continuation-probability treatment, the observed fixed-panel point differences are +0.083 for S2-absent wording (the registered family omitting the switch-bearing continuation sentence) and +0.078 for S2-present wording (the family including it).",
        "S2 first-use definition",
    )
    represented_caveat = """The treatment changes both the environment’s continuation process and the text used to communicate that process. Round-one choices therefore identify response to **continuation probability under a specified representation**, not a semantically neutral economic parameter: incentive and framing channels remain undecomposed."""
    text = insert_before(text, "Dal Bó and Fréchette [2011] remain useful", represented_caveat, "represented treatment caveat")

    gemini_sentence = """The registered Gemini tier was descriptive only and is excluded from these estimates because its endpoint showed documented non-stationarity. Across eight personas and three cells, recorded means ranged from 0 to 0.90 and 9/24 cells met the historical interiority rule; complete values are in `docs/analysis/figure-sources/p5-tierC-gemini.csv` and the stability record."""
    text = insert_before(text, "![Prompt-indexed continuation-probability responses]", gemini_sentence, "Gemini descriptive pointer")

    # Proposition grounding.
    text = replace(
        text,
        "**Proposition B: aggregate moments do not identify microstructure or response coupling.** Mean and total variance do not identify how variation is divided between prompt configurations and repeated draws, nor do they identify distributional shape or boundary concentration. Even exact condition-specific distributions do not identify the cross-condition coupling and therefore do not identify the distribution of prompt-indexed responses \(\Delta_i=p_i(1)-p_i(0)\).",
        "**Proposition B: aggregate moments do not identify microstructure or response coupling.** This is an application of the law of total variance and classical Fréchet–Hoeffding/Sklar coupling results [Hoeffding 1940; Sklar 1959] to synthetic-participant validation, not a new probability theorem. Mean and total variance do not identify how variation is divided between prompt configurations and repeated draws, nor do they identify distributional shape or boundary concentration. Even exact condition-specific distributions do not identify the cross-condition coupling and therefore do not identify the distribution of prompt-indexed responses \(\Delta_i=p_i(1)-p_i(0)\).",
        "probability grounding",
    )

    # Span ladder and prefix confound.
    text = replace(
        text,
        "For the bare configuration, round-one cooperation was 0.000 at every registered continuation probability. A single continuation sentence, localized through a span ladder and confirmed on fresh seeds, moved held-out cooperation from 0/40 to 37/40. The same wording factor was null in one-shot play, showing that text effects depend on the context in which a phrase has a strategic referent.",
        "For the bare configuration, round-one cooperation was 0.000 at every registered continuation probability. X2 mechanically decomposed the two registered prompt bundles into six rendered sentence/block spans, constructed forward and reverse ladders by replacing one complete span at a time, screened ten new rungs with ten episodes each, and selected the largest adjacent gap subject to a preregistered |Δ|≥0.50 rule and deterministic tie-break. The selected S2 minimal pair was then tested at temperature 0.7 on 20 fresh episodes per side (seeds 2953–2972, disjoint from screening), moving held-out cooperation from 0/40 to 37/40. S2 is therefore the switch-bearing span under this registered ladder; the design does not eliminate every possible positional interaction. The same wording factor was null in one-shot play, showing that text effects depend on the context in which a phrase has a strategic referent.",
        "span ladder definition",
    )
    text = replace(
        text,
        "Personas add separable presence and direction effects. Direction produces the 0.5–0.7 leaning gaps. Presence reverses the bare swap-cell choice: all sixteen personas overwhelmingly select the cooperation-worded/payoff-dominant option.",
        "Adding the registered persona-format prefix and varying among the complete persona prompts produce two observed contrasts, but they are not fully factorially separable. Differences among prompts produce the 0.5–0.7 leaning gaps. Adding any tested persona string reverses the bare swap-cell choice: all sixteen personas overwhelmingly select the cooperation-worded/payoff-dominant option. Because no length-, punctuation-, and position-matched non-semantic prefix was run, this prefix contrast cannot isolate semantic persona presence from generic sequence-length or displacement effects.",
        "persona prefix qualification",
    )

    # Section 4.4: dynamic filtering, power, bootstrap rationale, status.
    text = text.replace(
        "### 4.4 The favored persona-level result does not survive dependence-aware inference",
        "### 4.4 The favored persona-level result is not prospectively confirmed; the archived family is underpowered",
    )
    old_audit_paragraph = "Three 200,000-permutation gate constructions are now reported. Under the historical seat-level gate, p13 remains the maximum at +0.4167, with familywise \(p=0.059230\), Monte Carlo 95% interval [0.058194, 0.060268]. Under the retained percentile episode-cluster-bootstrap gate, p13 also remains the maximum and \(p=0.043455\), interval [0.042561, 0.044353]. That construction is the only variant below 0.05, but it is not primary because percentile intervals become degenerate at exact corners. Because the gate itself is an interval-interiority test, that degeneracy can misclassify precisely the boundary cells the assay exists to screen with non-zero policy uncertainty. Under the primary conservative exact-episode gate, p13 is not interior: its low-δ lower bound falls below 0.05 and its high-δ upper bound exceeds 0.95. Only p04/s2p and p05/s2a pass both gates; the largest surviving positive slope is +0.0833, with familywise \(p=0.773206\), interval [0.771363, 0.775039]."
    new_audit_paragraph = (
        "Three 200,000-permutation gate constructions are now reported. Under the historical seat-level gate, p13 remains the maximum at +0.4167, with familywise \\(p=0.059230\\), Monte Carlo 95% interval [0.058194, 0.060268]. Under the percentile episode-cluster-bootstrap sensitivity, p13 also remains the maximum and \\(p=0.043455\\), interval [0.042561, 0.044353]. The exact projection is the conservative reference because it has finite-sample coverage for the discrete episode mean; the percentile bootstrap is retained symmetrically but has no comparable small-sample coverage guarantee. Under the conservative exact-episode gate, p13 is ineligible: its low-δ lower bound falls below 0.05 and its high-δ upper bound exceeds 0.95. Only p04/s2p and p05/s2a pass both gates; the largest eligible slope belongs to p05/s2a (+0.0833), with familywise \\(p=0.773206\\), interval [0.771363, 0.775039]."
    )
    text = replace(text, old_audit_paragraph, new_audit_paragraph, "family audit paragraph")

    dynamic_paragraph = (
        f"The complete data-dependent gate is dynamically reapplied within every permutation, not frozen from the observed-data mask. The implementation precomputes {dynamic['precomputedIntervalGateEvaluations']:,} possible-composition gate values and performs {dynamic['dynamicGateLookupApplicationsAtB200000']:,} condition-gate lookup applications at B=200,000; lookup/direct parity and an intentionally static-mask regression are recorded in `docs/analysis/submission/round5/round5-review-audit.md`."
    )
    text = insert_before(text, "These variants were specified and executed together", dynamic_paragraph, "dynamic filtering statement")

    power_paragraph = (
        f"An exhaustive attainability audit shows that with six episodes per condition, the exact gate admits sample means only from {n6['minPassingMean']:.3f} to {n6['maxPassingMean']:.3f}, so two eligible cells can differ by at most {n6['maxAttainableSlope']:.3f}. Under the archived 32-candidate null structure, the estimated familywise tail probability at that maximum attainable slope is {tail['pAddOne']:.6f}; no exact-gate result in this archived family can reach 0.05. The exact analysis is therefore a valid dependence-aware sensitivity but not a powered disconfirmation of a p13-sized capability claim. The record neither prospectively confirms nor decisively disconfirms p13; it identifies a replication target whose next test must be sized prospectively (Appendix A.4)."
    )
    text = insert_before(text, "These variants were specified and executed together", power_paragraph, "gate power statement")

    text = replace(
        text,
        "Scientifically, p13 is a replication target, not a finding; the capability-envelope interpretation selected by the precommitted branch is no longer supported by clause (a).",
        "Scientifically, p13 is a replication target, not a finding. Clause (a) did not prospectively establish the capability claim because the frozen search lacked family control; the conservative post-adjudication procedure is too underpowered at n=6 to provide decisive evidence against it.",
        "p13 status",
    )
    text = replace(
        text,
        "*Figure 5. All three post-review familywise constructions. The percentile-bootstrap gate is the only numerical result below 0.05, but it is non-primary because its interval gate degenerates at exact corners. None of the constructions was registered at the original freeze; no bar creates prospective confirmation.*",
        "*Figure 5. All three post-review familywise constructions. The first two points are p13/s2a under the historical and percentile-bootstrap gates. Under the conservative exact-episode gate, p13 is ineligible; the third point is the familywise result for the largest eligible candidate, p05/s2a. The exact method is the conservative coverage reference, while the percentile bootstrap is retained as a small-sample sensitivity. None was registered at the original freeze; no point creates prospective confirmation.*",
        "Figure 5 caption",
    )

    # Discussion and correction table.
    text = text.replace("response to an economic lever", "response to a represented continuation-probability treatment")
    text = replace(
        text,
        "| At least one persona establishes an unconfounded incentive-response existence result | **Not supported.** Post-review variants: historical seat gate \(p=0.059230\); percentile cluster-bootstrap gate \(p=0.043455\) but non-primary because of corner degeneracy; primary exact-episode gate excludes p13 and gives maximum surviving slope +0.0833, \(p=0.773206\). None was registered at the original freeze, so none creates prospective confirmation. |",
        f"| At least one persona establishes an unconfounded incentive-response existence result | **Not prospectively established.** Post-review variants: historical seat gate \\(p=0.059230\\); percentile cluster-bootstrap sensitivity \\(p=0.043455\\); conservative exact-episode sensitivity excludes p13 and gives the largest eligible slope +0.0833 for p05/s2a, \\(p=0.773206\\). None was registered at the original freeze. The exact gate’s maximum attainable n=6 slope is {n6['maxAttainableSlope']:.3f}, with archived-family tail probability {tail['pAddOne']:.6f}; the current data are insufficient for decisive confirmation or disconfirmation. |",
        "sealed discussion correction row",
    )

    # Limitations and provenance.
    limitations_addition = """The bare-versus-prefixed swap-cell contrast is format/content-confounded: no non-semantic prefix matched on length, punctuation, and position was run, so it cannot isolate semantic persona presence. The continuation-probability contrast likewise combines the actual continuation process with the language used to represent it; it is not a pure numeric-incentive manipulation. The six-episode exact-gate family analysis is underpowered by construction, as quantified in §4.4, and should not be read as evidence that p13 has no response."""
    text = insert_before(text, "The post-adjudication family analyses were specified", limitations_addition, "Round 5 limitations")

    provenance_paragraph = (
        f"For Phase 4–5, the event record contains complete rendered prompts, bundle and request-body SHA-256 values, engine commit and provider route, raw completion text, and provider response IDs for {p45_resp.get('responseId', 0):,} of {p45_resp.get('events', 0):,} recorded response events. The live adapter asserted that its actual deterministic request-body hash matched the recorded mirror. Individual raw completion payloads were not separately hash-chained or provider-attested at receipt, and the full provider JSON object was not retained. Capsule checksum manifests and external timestamps make the later released database snapshot tamper-evident relative to that snapshot; replay does not prove that no alteration occurred between provider receipt and snapshot sealing."
    )
    text = insert_before(text, "The original `scope-seal.md`", provenance_paragraph, "provenance boundary")

    # Appendix power note.
    text = replace(
        text,
        "A Phase 6 replication should not inherit the full 32-candidate search by default. It should preselect the replication target or a small declared family, use complete episodes as the unit, declare family control before data, and size the design by simulation against the exact decision rule. The present six episodes per arm are sufficient to reveal boundary concentration but intrinsically produce wide response intervals. A practical replication will require substantially more episodes per arm; the precise number depends on the smallest scientifically relevant response, the allowed family size, and whether the design tests a single target or a broader persona population. The repository therefore treats sample-size selection as a preregistration input rather than inferring a definitive number from this post hoc record.",
        f"A Phase 6 replication should not inherit the full 32-candidate search by default. It should preselect the replication target or a small declared family, use complete episodes as the unit, declare family control before data, and size the design by simulation against the exact decision rule. At n=6, exhaustive enumeration limits exact-gate-eligible cell means to [{n6['minPassingMean']:.3f}, {n6['maxPassingMean']:.3f}] and the largest eligible slope to {n6['maxAttainableSlope']:.3f}; under the archived family, even that maximum has estimated null tail probability {tail['pAddOne']:.6f}. The present design is therefore incapable of conventional exact-family rejection, not merely imprecise. Prospective planning simulations in `docs/analysis/submission/round5/` show how power changes with episode count and family size, but the registered Phase 6 calculation must use its declared dependence model, effect margin, and exact decision rule.",
        "Appendix power note",
    )

    # Correction ledger and references.
    ledger_marker = "| Aggregate and per-prompt response estimates added to the machine-readable submission summary | Round 4 review | Reproducibility |"
    round5_rows = """| Dynamic gate reapplication documented and regression-tested; 25.6 million lookup applications at B=200,000 | Explore Science B1 + zero-call audit | Familywise inference |
| Exact-gate attainability and prospective-power audit added; p13 reframed as neither confirmed nor decisively disconfirmed | Explore Science B3 + zero-call audit | Power and interpretation |
| Percentile-bootstrap rationale corrected from corner misclassification to lack of small-sample coverage guarantee | Explore Science B5 | Statistical validity |
| Persona-prefix effect qualified as format/content-confounded; δ reframed as a represented treatment | Explore Science B2/B7 | Construct validity |
| Request/response provenance and archive tamper-evidence boundary audited and stated | Explore Science A2 | Provenance |
| Phase table, protocol glossary, span-ladder specification, Gemini pointer, and probability-theory grounding added | Explore Science A1/B4/B6/B8/B9 | Self-contained reporting |
| Figures 1 and 5 corrected for aggregate markers and candidate attribution | Explore Science C1/C2 | Figure integrity |"""
    if round5_rows.splitlines()[0] not in text:
        text = text.replace(ledger_marker, ledger_marker + "\n" + round5_rows)

    references = """
Clopper, C. J., and Pearson, E. S. (1934). The use of confidence or fiducial limits illustrated in the case of the binomial. *Biometrika, 26*(4), 404–413. https://doi.org/10.1093/biomet/26.4.404

Hoeffding, W. (1940). Maßstabinvariante Korrelationstheorie. *Schriften des Mathematischen Instituts und des Instituts für Angewandte Mathematik der Universität Berlin, 5*, 181–233.

Lehmann, E. L., and Romano, J. P. (2005). *Testing Statistical Hypotheses* (3rd ed.). Springer. https://doi.org/10.1007/0-387-27605-X

Sklar, A. (1959). Fonctions de répartition à n dimensions et leurs marges. *Publications de l’Institut de Statistique de l’Université de Paris, 8*, 229–231.

Westfall, P. H., and Young, S. S. (1993). *Resampling-Based Multiple Testing: Examples and Methods for p-Value Adjustment*. Wiley.
"""
    if "Sklar, A. (1959)" not in text:
        text = text.replace("## References\n", "## References\n\n" + references.strip() + "\n")

    path.write_text(text, encoding="utf-8")


def update_navigation() -> None:
    replacements = {
        ROOT / "README.md": [
            ("synthetic-players-review-draft-v6.pdf", "synthetic-players-review-draft-v7.pdf"),
            ("Current v6 Markdown manuscript", "Current v7 Markdown manuscript"),
        ],
        ROOT / "REVIEW.md": [
            ("synthetic-players-review-draft-v6.pdf", "synthetic-players-review-draft-v7.pdf"),
            ("Current Markdown manuscript", "Current v7 Markdown manuscript"),
        ],
        ROOT / "docs" / "analysis" / "INDEX.md": [
            ("synthetic-players-review-draft-v6.pdf", "synthetic-players-review-draft-v7.pdf"),
            ("Current v6 Markdown manuscript", "Current v7 Markdown manuscript"),
        ],
    }
    for path, reps in replacements.items():
        text = path.read_text(encoding="utf-8")
        for old, new in reps:
            text = text.replace(old, new)
        path.write_text(text, encoding="utf-8")

    review = ROOT / "REVIEW.md"
    text = review.read_text(encoding="utf-8")
    audit_line = "- **Round 5 audit:** [`docs/analysis/submission/round5/round5-review-audit.md`](docs/analysis/submission/round5/round5-review-audit.md) documents dynamic gate reapplication, exact-gate power, and the completion-provenance boundary.\n"
    anchor = "## Corrections reviewers should know before reading\n\n"
    if audit_line not in text:
        text = text.replace(anchor, anchor + audit_line)
    review.write_text(text, encoding="utf-8")


def main() -> int:
    if not AUDIT_JSON.exists():
        raise RuntimeError(f"missing Round 5 audit: {AUDIT_JSON}")
    audit = json.loads(AUDIT_JSON.read_text(encoding="utf-8"))
    update_paper(audit)
    update_navigation()
    print("apply_round5_v7: integrated Explore Science audit into living v7 documents")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
