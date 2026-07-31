#!/usr/bin/env python3
"""Integrate bounded, zero-call v13 corrections after the v12 transform."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "docs/paper/paper-draft.md"
AUDIT = ROOT / "docs/analysis/submission/v13/p52-dependence-audit.json"


def main() -> int:
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    boot = audit["stratifiedPromptClusterBootstrap"]
    latent = audit["fixedPanelDirichletJeffreys"]
    boot_lo, boot_hi = boot["interval95"]
    latent_lo, latent_hi = latent["interval95"]
    latent_median = latent["posteriorMedian"]

    text = PAPER.read_text(encoding="utf-8")
    text = text.replace(
        "**Preprint v12 (July 2026).**",
        "**Preprint v13 (July 2026; Claude review candidate).**",
    )

    old = "constructs simultaneous Clopper–Pearson intervals for the two episode-level binary components, and projects them onto \\(E[Y]\\). This construction is conservative, does not assume seat independence, and does not collapse to zero uncertainty when all observed episodes agree."
    new = r"""constructs simultaneous Clopper–Pearson intervals for the two episode-level binary components, and projects them onto \(E[Y]\). For wording family \(w\), prompt \(i\), continuation condition \(d\), and six complete episodes \(e\), define \(A_{ide}=\mathbf 1(Y_{ide}\ge .5)\) and \(B_{ide}=\mathbf 1(Y_{ide}=1)\), so \(\hat p_i(d)=\{\bar A_i(d)+\bar B_i(d)\}/2\). For each aggregate contrast, the sixteen equally weighted prompt cells contribute 96 episodes per condition; pooled component counts therefore estimate \(\bar p(d)=16^{-1}\sum_i p_i(d)\). The four component-condition intervals split the total error rate by Bonferroni. If \([L_d,U_d]\) is the projected condition-mean interval, the contrast interval is

\[
[L_{.90}-U_{.10},\;U_{.90}-L_{.10}].
\]

Under the pooled independent-binomial component model this union-bound construction has at least 95% simultaneous coverage; its role is a conservative small-sample projection rather than a claim that the sixteen prompt propensities are homogeneous. It does not assume seat independence and does not collapse to zero uncertainty when all observed episodes agree."""
    if old not in text:
        raise RuntimeError("CP paragraph anchor missing")
    text = text.replace(old, new)

    text = text.replace(
        "The frozen ratio ρ=.75 gives thresholds 0.3092 and 0.2337.",
        "The frozen ratio ρ=.75 gives thresholds 0.3092 and 0.2337. The ratio was a preregistered heuristic tolerance—not a theoretically derived equivalence or psychometric margin—so P5-1b is interpreted as a permissive historical dispersion checkpoint rather than evidence of human-variance equivalence.",
    )
    text = text.replace(
        "For comparison, finite-opportunity plug-in shares are 85.5%, 96.1%, 88.8%, and 90.2%.",
        "For comparison, finite-opportunity plug-in shares are 85.5%, 96.1%, 88.8%, and 90.2%, with conditional episode-bootstrap 95% intervals [82.0%, 93.8%], [94.6%, 98.9%], [86.7%, 94.6%], and [87.9%, 95.5%], respectively.",
    )

    old_p52 = "The pooled P5-2 task-consistent share is 90/704 seat decisions across 352 episodes, equivalently 45/352=0.128 on episode means, with exact interval [0.092, 0.172]. Every repeated conflict subcell is mixed; only the swap cell is individually persona-dominant. The pooled verdict is therefore carried by the mechanism-confounded swap cell."
    new_p52 = (
        "The pooled P5-2 task-consistent share is 90/704 seat decisions across 352 episodes, "
        "equivalently 45/352=0.128 on episode means. The frozen historical adjudication used "
        "the seat-level rule. An episode-iid Clopper–Pearson projection gives [0.092, 0.172], "
        "but that interval does not propagate the prompt clustering visible elsewhere in the study. "
        "Two post-adjudication, zero-call sensitivities retain the historical point estimate while "
        "changing the uncertainty model: a stratified prompt-cluster bootstrap over the forty "
        f"registered persona × conflict-cell clusters gives 95% interval [{boot_lo:.3f}, {boot_hi:.3f}], "
        "and a fixed-panel Dirichlet–Jeffreys latent-propensity aggregation gives posterior median "
        f"{latent_median:.3f} with 95% interval [{latent_lo:.3f}, {latent_hi:.3f}]. Both remain below "
        "the registered 0.20 persona-dominant boundary, although the Bayesian result approaches it. "
        "Every repeated conflict subcell is mixed; only the swap cell is individually persona-dominant. "
        "The pooled classification is therefore mechanism-confounded and carried by the swap cell, "
        "not evidence of a general persona-dominance mechanism."
    )
    if old_p52 not in text:
        raise RuntimeError("P5-2 paragraph anchor missing")
    text = text.replace(old_p52, new_p52)

    text = text.replace(
        "The primary evidence comes from one deployment and sixteen complete prompt bundles.",
        "The confirmatory predicates were registered and adjudicated separately at nominal thresholds; no study-wide alpha allocation or familywise rule was registered across P5-1a, P5-1b, P5-2, P5-3(a), P5-3(b), and the sequential X1 extension. They address distinct estimands and are not interpreted here as one omnibus test, but study-level false-positive exposure is consequently greater than under a prospectively hierarchical or alpha-spending design. A Phase 6 replication should preregister the primary/secondary hierarchy, candidate families, dependence units, maximum statistics, and cross-predicate error allocation before data collection.\n\nThe primary evidence comes from one deployment and sixteen complete prompt bundles.",
    )
    text = text.replace(
        "Phase 4–5 contain 30,421 normal request events and 30,397 response events; the 24-event difference is the disclosed provider-failure partial set.",
        "Phase 4–5 contain 30,421 normal request events and 30,397 response events; the 24-event difference is the disclosed provider-failure partial set. Each partial belongs to a failed run, was excluded from completed-run analyses and the 4,916-run replay denominator, and was never decoded as an action. Request attempts remain represented in request and budget accounting rather than being silently discarded; only completed replacement runs, where present under the registered replacement procedure, enter analysis.",
    )
    text = text.replace(
        "Diamonds show fixed-panel aggregates.",
        "Blue and orange diamonds show the S2-absent and S2-present fixed-panel aggregates, respectively.",
    )
    text = text.replace("Preprint v12", "Preprint v13")
    PAPER.write_text(text, encoding="utf-8")

    reviews = ROOT / "docs/reviews"
    reviews.mkdir(parents=True, exist_ok=True)
    (reviews / "round-11-explore-science-v12-review.md").write_text(
        "# Round 11 — Explore Science review of preprint v12\n\n"
        "Source: Explore Science review report dated July 31, 2026 (96/100, Platinum; eight minor issues). "
        "The v13 response is additive and zero-call. Historical predicates and verdicts are unchanged.\n",
        encoding="utf-8",
    )
    (reviews / "round-11-disposition-matrix.md").write_text(
        """# Round 11 disposition matrix — v13

| Issue | Disposition | v13 action |
|---|---|---|
| A1 global multiplicity | Adopted | Explicit limitation and prospective hierarchy/error-allocation remedy. |
| A2 provider failures | Adopted | Failed/excluded/never action-coded; attempts retained in accounting. |
| B1 P5-2 dependence | Adopted | Prompt-cluster bootstrap plus fixed-panel Dirichlet–Jeffreys sensitivity. |
| B2 Figure 3 bounds | Adopted | Four share-level intervals added to text. |
| B3 rho=.75 | Adopted | Identified as preregistered heuristic. |
| B4 aggregate CP | Adopted with qualification | Formula, alpha allocation, projection and working-model scope added. |
| C1 Figure 1 dodge | Strengthened | Larger vertical separation. |
| C2 aggregate legend | Adopted | Separate colored aggregate entries. |
""",
        encoding="utf-8",
    )
    print("apply_preprint_v13: integrated bounded final-review corrections")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
