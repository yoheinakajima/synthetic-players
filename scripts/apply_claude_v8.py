#!/usr/bin/env python3
"""Integrate the independent Claude review into the living v8 review package.

This script runs after the completed Round 5 analysis and v7 integration. It
edits only living manuscript, navigation, citation, and review-index files. It
does not modify sealed registrations, historical adjudications, raw event data,
or precommitted discussion artifacts.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "docs" / "paper" / "paper-draft.md"
README = ROOT / "README.md"
REVIEW = ROOT / "REVIEW.md"
INDEX = ROOT / "docs" / "analysis" / "INDEX.md"
STATUS = ROOT / "docs" / "analysis" / "submission-blockers.md"
PDF_README = ROOT / "docs" / "paper" / "PDF-README.md"
REVIEWS = ROOT / "docs" / "reviews" / "README.md"
CITATION = ROOT / "CITATION.cff"

OLD_TITLE = (
    "Passing Coarse Marginal Checks Can Be Cheap: Persona Mixtures and "
    "Imprecise Incentive-Response Estimates in an LLM Persona Panel"
)
NEW_TITLE = (
    "Passing Coarse Marginal Checks Can Be Cheap: Persona Mixtures and "
    "Imprecise Treatment-Response Estimates in an LLM Persona Panel"
)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise RuntimeError(f"missing expected text for {label}")
    return text.replace(old, new, 1)


def insert_before(text: str, marker: str, block: str, label: str) -> str:
    if block.strip() in text:
        return text
    if marker not in text:
        raise RuntimeError(f"missing marker for {label}: {marker[:100]}")
    return text.replace(marker, block.rstrip() + "\n\n" + marker, 1)


def update_paper() -> None:
    text = PAPER.read_text(encoding="utf-8")
    text = replace_once(text, f"# {OLD_TITLE}", f"# {NEW_TITLE}", "title")
    text = text.replace(
        "WORKING DRAFT v7 — ROUND 5 RESPONSE DRAFT",
        "WORKING DRAFT v8 — INDEPENDENT REPOSITORY REVIEW DRAFT",
    )
    text = text.replace("*End of working draft v7.*", "*End of working draft v8.*")

    text = replace_once(
        text,
        "We report a five-phase study in which confirmatory claims were registered before their adjudicating data and mechanically evaluated from an event-sourced record.",
        "We report a five-stage research program. Confirmatory claims from Phases 3–5 were registered before the data that adjudicated them and were mechanically evaluated from an event-sourced record; Phases 1–2 document post hoc instrument development and corrective re-adjudication rather than prospective confirmation.",
        "abstract registration scope",
    )
    text = text.replace("prompt-indexed incentive response", "prompt-indexed treatment response")

    text = replace_once(
        text,
        "| Phase 4 | Representation robustness, X1/X2 wording extensions, counterfactual payoffs/labels, continuation-probability assays, adversaries, and sentinels | complete episode for current sensitivities | X1 was result-informed but registered before X1 data; the remaining blocks were registered before their own data |",
        "| Phase 4 | Representation robustness, X1/X2 wording extensions, counterfactual payoffs/labels, continuation-probability assays, adversaries, and sentinels | complete episode for current sensitivities | X1 was a sequentially registered, result-informed extension: Phase 3 motivated the test, while its prompts, sample size, and predicate were sealed before any X1 data; the remaining blocks were registered before their own data |",
        "X1 sequential registration",
    )
    text = replace_once(
        text,
        "`P5-3(a)` asks whether any persona × wording pair has both continuation-probability cells interior and a positive slope lower bound; `P5-3(b)` asks whether each persona lane rejects the bare configuration’s dominated, semantically attracted swap-cell option at a registered minimum rate.",
        "`P5-3(a)`—called clause (a) below—asks whether any persona × wording pair has both continuation-probability cells interior and a positive slope lower bound; `P5-3(b)`—clause (b)—asks whether each persona lane rejects the bare configuration’s dominated, semantically attracted swap-cell option at a registered minimum rate.",
        "clause glossary mapping",
    )

    text = replace_once(
        text,
        "The registered Gemini tier was descriptive only and is excluded from these estimates because its endpoint showed documented non-stationarity. Across eight personas and three cells, recorded means ranged from 0 to 0.90 and 9/24 cells met the historical interiority rule; complete values are in `docs/analysis/figure-sources/p5-tierC-gemini.csv` and the stability record.",
        "The registered Gemini tier was descriptive only and is excluded from these estimates because its endpoint showed documented non-stationarity. Across eight personas and three cells, recorded means ranged from 0 to 0.90 and 9/24 cells (37.5%) met the historical interiority rule, compared with 14/96 (14.6%) in the primary GPT-4.1 panel; several representation-channel effects also reversed direction across vendors. Because the endpoint was non-stationary and the evaluated panels differed, this is not a formal replication comparison. It is contrary descriptive evidence that the composition pattern is deployment-specific rather than universal. Complete values are in `docs/analysis/figure-sources/p5-tierC-gemini.csv` and the stability record.",
        "Gemini contrary evidence",
    )

    text = replace_once(
        text,
        "*Figure 1. Prompt-indexed differences in round-one cooperation, \\(\\Delta_i=\\hat p_i(\\delta=.90)-\\hat p_i(\\delta=.10)\\), for both registered wording families. Bars are conservative exact simultaneous 95% intervals with complete episodes as the unit; observed corners retain non-zero uncertainty. Aggregate diamonds show the fixed-panel point differences and intervals. Many rows at \\(\\Delta_i=0\\) arise because both recorded cells were fully concentrated at the same boundary; they visualize the composition pattern, not precise evidence of homogeneous response or no effect. Pairing the same explicit prompt supplies a prompt-indexed coupling, not a person-level treatment effect without latent-person invariance.*",
        "*Figure 1. Prompt-indexed differences in round-one cooperation, \\(\\Delta_i=\\hat p_i(\\delta=.90)-\\hat p_i(\\delta=.10)\\), for both registered wording families. Bars are conservative exact simultaneous 95% intervals with complete episodes as the unit; observed corners retain non-zero uncertainty. Diamonds on the **Fixed-panel aggregate** row show the two wording-family estimates in their corresponding series colors. Many rows at \\(\\Delta_i=0\\) arise because both recorded cells were fully concentrated at the same boundary; they visualize the composition pattern, not precise evidence of homogeneous response or no effect. Pairing the same explicit prompt supplies a prompt-indexed coupling, not a person-level treatment effect without latent-person invariance.*",
        "Figure 1 caption",
    )
    text = replace_once(
        text,
        "*Figure 2. Fixed-panel round-one cooperation means by continuation probability and wording family. The lines show the observed +0.083 (S2 absent) and +0.078 (S2 present) point differences; they do not encode equivalence or a precise upper bound.*",
        "*Figure 2. Fixed-panel round-one cooperation by represented continuation-probability condition and wording family. Points are observed means; error bars are the conservative exact condition intervals used in the within-wording contrast construction. Lines connect conditions for orientation only and do not imply a precise, semantically isolated incentive effect.*",
        "Figure 2 caption",
    )

    text = replace_once(
        text,
        "The complete data-dependent gate is dynamically reapplied within every permutation, not frozen from the observed-data mask. The implementation precomputes 56 possible-composition gate values and performs 25,600,000 condition-gate lookup applications at B=200,000; lookup/direct parity and an intentionally static-mask regression are recorded in `docs/analysis/submission/round5/round5-review-audit.md`.",
        "The complete data-dependent gate is dynamically reapplied within every permutation, not frozen from the observed-data mask. The implementation precomputes 56 possible-composition gate values and performs 25,600,000 condition-gate lookup applications at B=200,000. In a deliberately incorrect comparison that froze the observed-data mask, the maximum statistic differed from the dynamic procedure in 718 of 5,000 null draws (14.4%), showing that reapplication materially changes the reference distribution. Lookup/direct parity and the regression are recorded in `docs/analysis/submission/round5/round5-review-audit.md`.",
        "dynamic mask materiality",
    )

    interval_block = """For p13/s2a, the percentile bootstrap admitted both conditions as interior—δ=.10: [0.083, 0.667]; δ=.90: [0.583, 0.917]—whereas the conservative exact projection rejected both—[0.047, 0.800] and [0.287, 0.954], respectively. Neither recorded cell was at an exact corner. The eligibility difference therefore arises from small-sample interval width and coverage behavior, not from a corner interval falsely passing the gate."""
    text = insert_before(
        text,
        "The complete data-dependent gate is dynamically reapplied within every permutation",
        interval_block,
        "p13 interval comparison",
    )

    text = replace_once(
        text,
        "*Figure 5. All three post-review familywise constructions. The first two points are p13/s2a under the historical and percentile-bootstrap gates. Under the conservative exact-episode gate, p13 is ineligible; the third point is the familywise result for the largest eligible candidate, p05/s2a. The exact method is the conservative coverage reference, while the percentile bootstrap is retained as a small-sample sensitivity. None was registered at the original freeze; no point creates prospective confirmation.*",
        "*Figure 5. Post-adjudication familywise constructions. The first two points are p13/s2a under the historical and percentile-bootstrap gates. Under the conservative exact-episode gate, p13 is ineligible; the third point is the familywise result for the largest eligible candidate, p05/s2a. The dotted line at \\(p=0.075040\\) marks the estimated minimum attainable familywise p-value for the archived \\(n=6\\), 32-candidate exact-gate design and applies only to that construction. None of the procedures was registered at the original freeze; no point creates prospective confirmation.*",
        "Figure 5 caption and attainability boundary",
    )

    text = text.replace("small observed lever-response point estimates", "small observed treatment-response point estimates")
    text = text.replace("behavior under a moved policy lever", "behavior under a changed treatment")

    text = replace_once(
        text,
        "| At least one persona establishes an unconfounded incentive-response existence result | **Not prospectively established.** Post-review variants: historical seat gate \\(p=0.059230\\); percentile cluster-bootstrap sensitivity \\(p=0.043455\\); conservative exact-episode sensitivity excludes p13 and gives the largest eligible slope +0.0833 for p05/s2a, \\(p=0.773206\\). None was registered at the original freeze. The exact gate’s maximum attainable n=6 slope is 0.333, with archived-family tail probability 0.075040; the current data are insufficient for decisive confirmation or disconfirmation. |",
        "| At least one persona establishes an unconfounded incentive-response existence result | **Not prospectively established.** The frozen search lacked family control, and the post-adjudication procedures were method-dependent and unregistered. The conservative exact procedure cannot reach conventional familywise rejection in the archived n=6 design. See §4.4; p13 remains a replication target. |",
        "deduplicate correction-table p-values",
    )

    text = replace_once(
        text,
        "The bare-versus-prefixed swap-cell contrast is format/content-confounded: no non-semantic prefix matched on length, punctuation, and position was run, so it cannot isolate semantic persona presence. The continuation-probability contrast likewise combines the actual continuation process with the language used to represent it; it is not a pure numeric-incentive manipulation. The six-episode exact-gate family analysis is underpowered by construction, as quantified in §4.4, and should not be read as evidence that p13 has no response.",
        "The prefix and continuation-treatment construct limits are described in §4.1 and §4.3: no format-matched neutral prefix was run, and the continuation process was manipulated together with its textual representation. The six-episode exact-gate family analysis is underpowered by construction, as quantified in §4.4, and should not be read as evidence that p13 has no response.",
        "deduplicate limitations",
    )

    old_appendix = """### A.4 Prospective replication and questions for Explore Science

A Phase 6 replication should not inherit the full 32-candidate search by default. It should preselect the replication target or a small declared family, use complete episodes as the unit, declare family control before data, and size the design by simulation against the exact decision rule. At n=6, exhaustive enumeration limits exact-gate-eligible cell means to [0.333, 0.667] and the largest eligible slope to 0.333; under the archived family, even that maximum has estimated null tail probability 0.075040. The present design is therefore incapable of conventional exact-family rejection, not merely imprecise. Prospective planning simulations in `docs/analysis/submission/round5/` show how power changes with episode count and family size, but the registered Phase 6 calculation must use its declared dependence model, effect margin, and exact decision rule.

1. Is the paper’s specific novelty boundary—fixed-panel composition in strategic interaction plus minimal representation interventions and public correction—now sharp enough given Li and Ji’s expanded mechanism analysis?
2. Does Figure 1 prevent both mistakes: reading the small point estimates as equivalence and reading repeated zero rows as precise evidence of no variation?
3. Should the protocol-nonmatched Dal Bó–Fréchette context remain in the main text, move to a footnote, or become citation-only?
4. Which target venue best matches the combined behavioral-science and metascience contribution?
5. What additional prospective power or sensitivity analysis should be required before a Phase 6 replication is registered?"""
    new_appendix = """### A.4 Prospective replication and open design choices

A Phase 6 replication should not inherit the full 32-candidate search by default. It should preselect the replication target or a small declared family, use complete episodes as the unit, declare family control before data, and size the design by simulation against the exact decision rule. At n=6, exhaustive enumeration limits exact-gate-eligible cell means to [0.333, 0.667] and the largest eligible slope to 0.333; under the archived family, even that maximum has estimated null tail probability 0.075040. The present design is therefore incapable of conventional exact-family rejection, not merely imprecise. Prospective planning simulations in `docs/analysis/submission/round5/` show how power changes with episode count and family size, but the registered Phase 6 calculation must use its declared dependence model, effect margin, and exact decision rule.

The principal open design choices are the smallest scientifically relevant response, candidate-family size, format-matched prefix controls, a continuation-probability × wording factorial, and whether the next study targets one registered configuration or a broader persona generator."""
    text = replace_once(text, old_appendix, new_appendix, "venue-neutral appendix")

    ledger_anchor = "| Figures 1 and 5 corrected for aggregate markers and candidate attribution | Explore Science C1/C2 | Figure integrity |"
    claude_rows = """| Abstract registration scope restricted to confirmatory Phases 3–5; X1 labeled a sequentially registered result-informed extension | Claude repository review | Registration clarity |
| Dynamic-versus-static gate divergence (718/5,000; 14.4%) and concrete p13 interval disagreement reported | Claude repository review | Inferential transparency |
| Title changed from incentive-response to treatment-response; Gemini framed as deployment-specific contrary evidence | Claude repository review | Construct and scope discipline |
| Figure 1 aggregate row/legend, Figure 2 condition intervals, and Figure 5 archived-design attainability boundary added | Claude repository review | Figure integrity |
| Review artifact identity metadata and venue-neutral appendix added | Claude repository review | Review provenance |"""
    if claude_rows.splitlines()[0] not in text:
        if ledger_anchor not in text:
            raise RuntimeError("missing correction-ledger anchor")
        text = text.replace(ledger_anchor, ledger_anchor + "\n" + claude_rows, 1)

    PAPER.write_text(text, encoding="utf-8")


def update_navigation() -> None:
    paths = [README, REVIEW, INDEX, STATUS, PDF_README, CITATION]
    for path in paths:
        text = path.read_text(encoding="utf-8")
        text = text.replace(OLD_TITLE, NEW_TITLE)
        text = text.replace("synthetic-players-review-draft-v7.pdf", "synthetic-players-review-draft-v8.pdf")
        text = text.replace("phase5-review-v7", "phase5-review-v8")
        text = text.replace("Current v7 Markdown manuscript", "Current v8 Markdown manuscript")
        text = text.replace("v7 Markdown manuscript", "v8 Markdown manuscript")
        text = text.replace("v7 reviewer PDF", "v8 reviewer PDF")
        text = text.replace("v7 review PDF", "v8 review PDF")
        text = text.replace("v7 review package", "v8 review package")
        text = text.replace("v7 paper", "v8 paper")
        path.write_text(text, encoding="utf-8")

    review_text = REVIEW.read_text(encoding="utf-8")
    row = "- **Claude v7 repository review:** [`docs/reviews/round-6-claude-v7-review.md`](docs/reviews/round-6-claude-v7-review.md) verifies the Round 5 audit and motivates the final v8 registration, power, construct, and figure polish.\n"
    anchor = "## Corrections reviewers should know before reading\n\n"
    if row not in review_text:
        if anchor not in review_text:
            raise RuntimeError("missing REVIEW correction anchor")
        review_text = review_text.replace(anchor, anchor + row, 1)
    REVIEW.write_text(review_text, encoding="utf-8")

    reviews_text = REVIEWS.read_text(encoding="utf-8")
    review_row = "| [`round-6-claude-v7-review.md`](round-6-claude-v7-review.md) | Independent repository review of v7 | Verified the Round 5 audit, corrected artifact-selection provenance, and requested final abstract, interval, power-boundary, cross-vendor, and figure polish integrated into v8. |"
    if review_row not in reviews_text:
        marker = "| [`round-5-explore-science-review.md`](round-5-explore-science-review.md) / [`round-5-disposition-matrix.md`](round-5-disposition-matrix.md) | Explore Science review and response | Thirteen minor issues; dynamic-gate, power, provenance, construct, reporting, and figure corrections integrated into v7. |"
        if marker not in reviews_text:
            raise RuntimeError("missing review-index Round 5 row")
        reviews_text = reviews_text.replace(marker, marker + "\n" + review_row, 1)
    REVIEWS.write_text(reviews_text, encoding="utf-8")


def main() -> int:
    update_paper()
    update_navigation()
    print("apply_claude_v8: integrated independent repository review into living v8 package")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
