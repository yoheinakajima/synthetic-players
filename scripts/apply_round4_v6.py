#!/usr/bin/env python3
"""Apply the reviewer-approved Round 4/v6 living-document package.

This script changes only living paper/review/navigation files. It does not edit
sealed registrations, adjudications, event data, or historical verdicts. The
compressed transport payload is deleted after extraction.
"""
from __future__ import annotations

import base64
import io
import shutil
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAYLOAD_DIR = ROOT / "scripts/.round4_payload"


def extract_payload() -> None:
    parts = sorted(PAYLOAD_DIR.glob("part-*.b64"))
    if not parts:
        # Idempotent after the payload has already been applied and removed.
        if (ROOT / "docs/paper/paper-draft.md").exists():
            return
        raise RuntimeError("Round 4 payload parts are missing")
    encoded = "".join("".join(p.read_text(encoding="utf-8").split()) for p in parts)
    data = base64.b64decode(encoded, validate=True)
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tf:
        root = ROOT.resolve()
        for member in tf.getmembers():
            target = (ROOT / member.name).resolve()
            if root not in target.parents and target != root:
                raise RuntimeError(f"unsafe payload member: {member.name}")
        tf.extractall(ROOT)
    shutil.rmtree(PAYLOAD_DIR)


def replace(text: str, old: str, new: str, label: str) -> str:
    if new in text:
        return text
    if old not in text:
        raise RuntimeError(f"missing expected {label}")
    return text.replace(old, new, 1)


def update_readme() -> None:
    path = ROOT / "README.md"
    text = path.read_text(encoding="utf-8")
    text = replace(text,
        "> **Passing Coarse Marginal Checks Can Be Cheap: Persona Mixtures and Weak Observed Incentive Response in LLM Behavioral Simulation**",
        "> **Passing Coarse Marginal Checks Can Be Cheap: Persona Mixtures and Imprecise Incentive-Response Estimates in an LLM Persona Panel**",
        "README title")
    text = replace(text,
        "[`docs/paper/paper-draft.md`](docs/paper/paper-draft.md)\n\nThe sealed experimental program and the scientific review gate are complete. Exact v2 and v3 manuscript history is public. Remaining formal-submission work is editorial: final citation metadata and bibliography formatting, target-venue formatting, and human sign-off on the title and venue-specific AI-assistance statement.",
        "[`docs/paper/paper-draft.md`](docs/paper/paper-draft.md)\n\n**Formatted review copy:** [`docs/paper/synthetic-players-review-draft-v6.pdf`](docs/paper/synthetic-players-review-draft-v6.pdf) · [build notes](docs/paper/PDF-README.md)\n\nThe sealed experimental program and the scientific review gate are complete. Round 4 independently cloned the repository, passed lint, and replayed all 4,576 runs with zero credentials. Remaining formal-submission work is venue formatting and human sign-off on the final title and venue-specific AI-assistance statement.",
        "README review links")
    text = replace(text,
        "> A fixed panel of sixteen lightweight persona prompts passed preregistered **coarse marginal checks**. Corrected estimates assign approximately 85%–96% of episode-level variation to differences between prompt configurations. The observed aggregate continuation-probability contrasts are +0.083 and +0.078, with conservative exact intervals too wide to establish equivalence or a null response.",
        "> A fixed panel of sixteen lightweight persona prompts passed preregistered **coarse marginal checks**. Corrected estimates assign approximately 85%–96% of episode-level variation to differences between prompt configurations. The observed aggregate continuation-probability contrasts are +0.083 and +0.078, with conservative exact intervals of approximately [−0.171, +0.330] and [−0.181, +0.330]. These are small point estimates with substantial uncertainty—not evidence of equivalence, a null response, or a narrow upper bound.",
        "README bounded claim")
    text = text.replace("| [`docs/paper/paper-draft.md`](docs/paper/paper-draft.md) | Current v5 manuscript |", "| [`docs/paper/paper-draft.md`](docs/paper/paper-draft.md) | Current v6 Markdown manuscript |\n| [`docs/paper/synthetic-players-review-draft-v6.pdf`](docs/paper/synthetic-players-review-draft-v6.pdf) | Line-numbered Explore Science review PDF with five vector figures |")
    text = text.replace("| [`docs/reviews/`](docs/reviews/) | Methods review, reviewer-role disclosure, and independent verification |", "| [`docs/reviews/`](docs/reviews/) | Round 1–4 review archive, reviewer-role disclosure, and direct outside reproduction |")
    path.write_text(text, encoding="utf-8")


def update_review() -> None:
    path = ROOT / "REVIEW.md"
    text = path.read_text(encoding="utf-8")
    text = replace(text,
        "1. **Current manuscript:** [`docs/paper/paper-draft.md`](docs/paper/paper-draft.md)\n2. **Independent verification memo:** [`docs/reviews/round-3-independent-verification.md`](docs/reviews/round-3-independent-verification.md)",
        "1. **Formatted review PDF:** [`docs/paper/synthetic-players-review-draft-v6.pdf`](docs/paper/synthetic-players-review-draft-v6.pdf)\n2. **Current Markdown manuscript:** [`docs/paper/paper-draft.md`](docs/paper/paper-draft.md)\n3. **Round 4 direct reproduction and review:** [`docs/reviews/round-4-independent-review.md`](docs/reviews/round-4-independent-review.md)\n4. **Round 3 artifact verification:** [`docs/reviews/round-3-independent-verification.md`](docs/reviews/round-3-independent-verification.md)",
        "review start list")
    # Renumber the remaining original entries only for readability.
    for old,new in [("3. **Machine-readable", "5. **Machine-readable"), ("4. **Review/submission", "6. **Review/submission"), ("5. **Novelty", "7. **Novelty"), ("6. **Literature", "8. **Literature"), ("7. **Identification", "9. **Identification"), ("8. **Exact manuscript", "10. **Exact manuscript"), ("9. **Review and role", "11. **Review and role")]:
        text=text.replace(old,new)
    text = replace(text,
        "The two observed aggregate continuation-probability contrasts are +0.083 and +0.078, with conservative exact intervals wide enough that the paper does **not** claim equivalence, a null response, incentive insensitivity, or human substitutability.",
        "The two observed aggregate continuation-probability contrasts are +0.083 and +0.078, with conservative exact intervals of approximately [−0.171, +0.330] and [−0.181, +0.330]. The point estimates are small, but the intervals remain compatible with materially larger positive and negative effects; the paper does **not** claim equivalence, a null response, incentive insensitivity, or human substitutability.",
        "review uncertainty claim")
    text = text.replace("while the observed response to the experimental lever remains small and imprecisely estimated.", "while the observed response to the experimental lever has small point estimates and remains imprecisely estimated.")
    anchor = "- The broad realism-versus-effect divergence is occupied by prior work; novelty is positioned around the strategic-interaction decomposition, representation experiments, and audit architecture.\n"
    if "Ashokkumar" not in text:
        text=text.replace(anchor, anchor + "- Strong positive contrary evidence is addressed explicitly: Ashokkumar, Hewitt, Ghezae, and Willer (Nature 2026) predict study-level treatment effects well, a forecasting estimand distinct from subject-level response-surface simulation.\n")
    text = text.replace("Expected result: **4,576/4,576 Phase 4–5 runs replay byte-exact with zero credentials and zero live model calls.**", "Expected result: **4,576/4,576 Phase 4–5 runs replay byte-exact with zero credentials and zero live model calls.** Round 4 reproduced this end-to-end on an outside machine rather than relying only on Actions evidence.")
    text = text.replace("Does Figure 1 make clear that +0.083/+0.078 are small point estimates, not equivalence results or identified upper bounds?", "Does Figure 1 make clear that +0.083/+0.078 are small but imprecise point estimates, not equivalence results, null findings, or identified upper bounds?")
    path.write_text(text, encoding="utf-8")


def update_analysis_index() -> None:
    path = ROOT / "docs/analysis/INDEX.md"
    text = path.read_text(encoding="utf-8")
    text = text.replace("Current v5 manuscript", "Current v6 Markdown manuscript")
    if "synthetic-players-review-draft-v6.pdf" not in text:
        text=text.replace("| [`../paper/paper-draft.md`](../paper/paper-draft.md) | Current v6 Markdown manuscript |", "| [`../paper/paper-draft.md`](../paper/paper-draft.md) | Current v6 Markdown manuscript |\n| [`../paper/synthetic-players-review-draft-v6.pdf`](../paper/synthetic-players-review-draft-v6.pdf) | Line-numbered Explore Science review PDF with five figures |")
    text=text.replace("Round-2 methods review, role disclosure, and round-3 independent verification", "Round 1–4 review archive, role disclosure, and Round 4 direct outside reproduction")
    text=text.replace("Machine-readable summary of generated zero-call analyses", "Machine-readable summary, including aggregate and per-prompt continuation-probability contrasts")
    path.write_text(text, encoding="utf-8")


def update_literature_map() -> None:
    path = ROOT / "docs/analysis/literature-map.md"
    text = path.read_text(encoding="utf-8")
    text=text.replace("while showing weak response to a registered incentive manipulation.", "while producing small but imprecisely estimated point differences under a registered incentive manipulation.")
    old="- **Li & Ji (2026), arXiv:2604.02458.** Three LLM families, 11 interventions, 59,508 participants in 62 countries, plus two replication datasets. Descriptive/statistical realism is only weakly related to treatment-effect accuracy, and prompt refinements selected for realism can worsen effect estimates. **Implication:** do not claim the first levels-versus-response demonstration; differentiate on mechanism, strategic interaction, and prospective registration."
    new="- **Li & Ji (2026), arXiv:2604.02458.** Three LLM families, 11 interventions, 59,508 participants in 62 countries, plus two replication datasets. Descriptive/statistical realism is only weakly related to treatment-effect accuracy, prompt refinements selected for realism can worsen effect estimates, and the expanded analysis traces errors to intervention logic, outcome structure, and excessive attitude–behavior coupling. **Implication:** neither the divergence nor mechanism analysis in general is new; differentiate on the specific fixed-panel composition pattern, strategic minimal pairs, and public inferential correction."
    if old in text: text=text.replace(old,new)
    if "Ashokkumar" not in text:
        text=text.replace(new+"\n", new+"\n- **Ashokkumar, Hewitt, Ghezae & Willer (2026), Nature, DOI 10.1038/s41586-026-10742-x.** Study descriptions predict 469 effects from 70 preregistered survey experiments with strong correlations, though effect sizes are systematically overestimated and performance weakens in a megastudy archive. **Implication:** this is the strongest positive counterexample to blanket pessimism. It forecasts study-level effects rather than simulating subject-level response surfaces, so it is compatible with the present composition failure and sharpens the estimand distinction.\n")
    text=text.replace("a fixed panel of lightweight persona prompts passes preregistered coarse marginal checks while the continuation-probability response remains small.", "a fixed panel of lightweight persona prompts passes preregistered coarse marginal checks while the continuation-probability point estimates remain small and imprecise.")
    text=text.replace("## 8. Must-resolve before submission", "## 8. Reviewer-draft verification status")
    text=text.replace("1. Replace every citation placeholder with verified metadata and a formatted reference.\n2. Recheck all 2026 preprint versions and venue status.\n3. Attribute empirical distribution-collapse evidence to the primary empirical paper, not secondhand through a surrogacy paper.\n4. Keep Li–Ji, Persson, Lin, Xie et al., Harry et al., persona-collapse work, Pal et al., Georgousis et al., and Same Game/Different Story in the explicit collision section.\n5. Keep the human comparator labeled nonmatched even after microdata reanalysis.\n6. Ensure no related-work sentence implies that matched explicit prompts establish latent-person invariance.", "1. The v6 reviewer PDF includes a formatted bibliography and re-verifies the load-bearing current metadata, including Li–Ji, Ashokkumar–Hewitt et al., Harry et al., Xiao et al., Georgousis et al., and Same Game, Different Story.\n2. A final metadata and style pass remains necessary at the actual venue-submission date.\n3. Empirical distribution-collapse claims should continue to point to primary empirical sources.\n4. Keep the human comparator labeled protocol-nonmatched even after any future microdata reanalysis.\n5. No related-work sentence should imply that matched explicit prompts establish latent-person invariance.")
    path.write_text(text, encoding="utf-8")


def update_citation() -> None:
    path = ROOT / "CITATION.cff"
    text = path.read_text(encoding="utf-8")
    text=text.replace('version: "phase5-review-v5"', 'version: "phase5-review-v6"')
    text=text.replace("a fixed panel of lightweight persona prompts that passes coarse marginal\n  checks while producing small, imprecisely estimated continuation-probability\n  contrasts.", "a fixed panel of lightweight persona prompts that passes coarse marginal\n  checks while producing small continuation-probability point estimates with\n  wide dependence-aware intervals.")
    path.write_text(text, encoding="utf-8")


def main() -> int:
    extract_payload()
    update_readme()
    update_review()
    update_analysis_index()
    update_literature_map()
    update_citation()
    print("apply_round4_v6: living review package updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
