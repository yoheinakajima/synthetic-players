# Round 14 — middle-path findings restoration and final precision pass

**Status:** accepted and incorporated into the final manuscript candidate.  
**Scope:** no new model calls; no change to historical registrations or mechanical verdicts.

## Framing decision

The paper remains a narrow empirical and methodological result about coarse marginal validation, prompt composition, representation control, treatment-response uncertainty, and auditable correction. It is not reframed as a broad catalog of every obstacle to using LLMs as replacement participants. The broader five-failure-mode taxonomy belongs in the announcement, talk, or project page.

## Findings restored without weakening the causal arc

1. Section 4.2 now reports the registered one-shot D1 wording null (+0.0063; Holm-adjusted p=1.00) and the much larger repeated-game wrapper shift (0.100 one-shot to 0.750/1.000 when repeated). The ceiling cells are explicitly non-identifying for the continuation-probability slope.
2. The P5-2 fixed-panel Bayesian aggregation is no longer described as independent corroboration. The symmetric-prior sweep shows a posterior median from 0.138 at alpha=0.10 to 0.205 at alpha=1.00; the alpha=1 posterior crosses the registered 0.20 boundary. The prompt-cluster bootstrap remains the principal dependence-aware sensitivity.
3. Appendix A.2 now preserves four concise, citable findings: opponent-contingent adversarial play; role-attached RPS asymmetry; cross-vendor label-payoff dissociation; and endpoint drift / behavioral-subject eligibility.

## Precision corrections from the final Claude review

- **RPS interval direction:** accepted. The archived D3 analysis computed the registered one-sided lower bound for the predicted positive first-minus-rock contrast. It did not compute an opposite-direction upper bound. The final text therefore drops the wrong-sided GPT interval, reports the sign reversal descriptively, and cites the archived support-only Dirichlet probability P(first-only > rock-only)=0.0001. The Gemini +0.243 lower bound remains descriptive cross-vendor evidence.
- **D2 congruence:** accepted. In the strict-dominance cell, GPT-4.1's word and payoff channels point to the same displayed option, so its 1.000 share does not separate them. The cell is informative for Gemini's payoff-conditional word attachment.
- **Registration status:** accepted. Each Appendix A.2 paragraph now distinguishes registered GPT tests, Holm-controlled secondary arms, descriptive Gemini comparisons, and procedural monitoring records.
- **Cross-references:** accepted. Section 6 points to the prior sweeps in §§4.1 and 4.2. Section 5.1 adds P5-2 as a second example of prior-sensitive binary certification.
- **Typesetting:** accepted. Figure references use nonbreaking TeX spaces and the Figures 2–3 callout no longer breaks across the page turn.

## Deliberately excluded

The post hoc p13 age/trait-tension theory remains excluded. The paper does not infer a persona mechanism from a favored candidate that was later demoted. Detailed adversary mechanics and the full sentinel chronology remain in the repository record rather than the main causal narrative.
