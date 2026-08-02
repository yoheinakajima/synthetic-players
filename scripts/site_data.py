"""Content graph for the Synthetic Players project site.

Single source of truth consumed by scripts/build_site.py. Every entry in
ITEMS becomes one page; `rel` lists forward relations (backlinks are computed).
Bodies are HTML fragments. Numbers are taken verbatim from the canonical
manuscript (docs/paper/paper.md), the machine-readable submission summary
(docs/analysis/submission/submission-analysis-summary.json), and the archived
analysis documents; nothing here is a new scientific claim.
"""
from __future__ import annotations

GH = "https://github.com/yoheinakajima/synthetic-players"
GHB = GH + "/blob/main"
GHT = GH + "/tree/main"

STATUS_LABEL = {
    "registered-pass": "Registered · verdict pass",
    "registered-fail": "Registered · not supported",
    "registered-mixed": "Registered · mixed record",
    "method-sensitive": "Method-sensitive",
    "prior-sensitive": "Prior-sensitive",
    "replication-target": "Replication target",
    "withdrawn": "Interpretation withdrawn",
    "descriptive": "Descriptive",
    "post-adjudication": "Post-adjudication",
    "procedural": "Procedural record",
    "prospective": "Prospective",
    "sealed": "Sealed record",
    "superseded": "Superseded",
    "final": "Final",
    "imprecise": "Imprecisely estimated",
}


def tbl(headers, rows, numeric=()):
    """Small helper: HTML table with horizontal scroll wrapper."""
    th = "".join(
        f'<th{" class=" + chr(34) + "num" + chr(34) if i in numeric else ""}>{h}</th>'
        for i, h in enumerate(headers)
    )
    trs = []
    for row in rows:
        tds = "".join(
            f'<td{" class=" + chr(34) + "num" + chr(34) if i in numeric else ""}>{c}</td>'
            for i, c in enumerate(row)
        )
        trs.append(f"<tr>{tds}</tr>")
    return (
        '<div class="tbl-scroll"><table><thead><tr>' + th +
        "</tr></thead><tbody>" + "".join(trs) + "</tbody></table></div>"
    )


ITEMS: list[dict] = []


def add(**kw):
    kw.setdefault("rel", [])
    kw.setdefault("links", [])
    ITEMS.append(kw)
    return kw["id"]


# ---------------------------------------------------------------------------
# References. `diff` = how this project differs / relates, shown on the page.
# Sources: docs/paper/paper.md §References, docs/analysis/literature-map.md,
# docs/analysis/novelty-relationships.md.
# ---------------------------------------------------------------------------

REFS = [
    dict(
        id="ref-li-ji-2026", key="Li & Ji 2026",
        title="When simulations look right but causal effects go wrong: LLMs as behavioral simulators",
        cite="Li, Y., and Ji, X. (2026). arXiv:2604.02458.",
        href="https://doi.org/10.48550/arXiv.2604.02458",
        role="Closest occupied territory",
        diff="Establishes at survey scale (3 model families, 11 interventions, 59,508 participants, 62 countries) that descriptive realism and treatment-effect accuracy are only weakly related, and that prompt refinements selected for realism can worsen effect estimates. This paper therefore does not claim the broad divergence as new; it contributes one concrete strategic-interaction mechanism — a fixed persona panel passing coarse marginal checks largely through between-prompt composition of corner-concentrated policies — under prospective registration.",
    ),
    dict(
        id="ref-ashokkumar-2026", key="Ashokkumar et al. 2026",
        title="Large language models can predict the results of social science experiments",
        cite="Ashokkumar, A., Hewitt, L., Ghezae, I., and Willer, R. (2026). Nature.",
        href="https://doi.org/10.1038/s41586-026-10742-x",
        role="Strong positive counterexample",
        diff="Forecasts 469 effects from 70 preregistered survey experiments with strong correlations (alongside systematic effect-size overestimation and weaker megastudy performance). It is the strongest evidence against blanket pessimism — but it is a forecasting task over studies, not subject-level simulation of a response surface. Strong effect forecasting is compatible with the fixed-panel composition failure studied here; the two sharpen the estimand distinction.",
    ),
    dict(
        id="ref-persson-2026", key="Persson et al. 2026",
        title="Statistical foundations of LLM-based A/B testing: a surrogacy framework",
        cite="Persson, E., Schultzberg, M., and Ankargren, S. (2026). arXiv:2606.17165.",
        href="https://doi.org/10.48550/arXiv.2606.17165",
        role="Formal causal frame",
        diff="Formalizes the assumptions and calibration under which effects on LLM outcomes identify effects on human outcomes; prior validation does not verify validity for a new intervention. This project supplies a design-side registered example: coarse marginal validation left the incentive-response estimand weakly constrained and the microstructure unidentified.",
    ),
    dict(
        id="ref-lin-2026", key="Lin et al. 2026",
        title="The illusion of intervention: your LLM-simulated experiment is an observational study",
        cite="Lin, V., Yun, T., Matarić, M. J., Canny, J., Gretton, A., and D'Amour, A. (2026). arXiv:2605.20767.",
        href="https://doi.org/10.48550/arXiv.2605.20767",
        role="Latent-user drift mechanism",
        diff="Shows an intervention prompt can shift the implied latent user even when the explicit persona is fixed. Sealed templates and paired explicit prompts in this project control assignment and execution — they do not establish latent-person invariance. The corner-mixture pattern observed here and Lin-style drift can coexist; the paper says so explicitly.",
    ),
    dict(
        id="ref-xie-2026", key="Xie et al. 2026",
        title="Evaluating the statistical realism of LLM-generated social science data (SSDataBench)",
        cite="Xie, Y., et al. (2026). PNAS 123(19):e2538145123.",
        href="https://doi.org/10.1073/pnas.2538145123",
        role="Statistical-realism foil",
        diff="Benchmarks 15 LLMs and finds sparse conditioning compresses heterogeneity into typological structures and exaggerates associations. This project connects an analogous concentration pattern (empirical corner concentration in a persona panel) to weak comparative-static response in a preregistered strategic game.",
    ),
    dict(
        id="ref-harry-2026", key="Harry et al. 2026",
        title="Beyond fixed psychological personas: state beats trait, but language models are state-blind",
        cite="Harry, T., Ngong, I. C., Nweke, C., Feng, Y., and Near, J. (2026). Findings of ACL 2026.",
        href="https://doi.org/10.18653/v1/2026.findings-acl.1316",
        role="Between/within adjacency",
        diff="Shows most psychological variation is within-person/state while LLMs respond weakly to state. Direct adjacency for this paper's between/within decomposition — but it does not study game-theoretic incentive response. Here, a trait-persona panel places most observed variation between prompt configurations while remaining weakly responsive to an economic lever.",
    ),
    dict(
        id="ref-xiao-2026", key="Xiao et al. 2026",
        title="The chameleon's limit: persona collapse and homogenization in LLMs",
        cite="Xiao, Y., Zhang, V. J., Yang, C., Ma, N., Xuan, W., and Huang, J.-t. (2026). arXiv:2604.24698.",
        href="https://doi.org/10.48550/arXiv.2604.24698",
        role="Persona-collapse territory",
        diff="Occupies the broad claim that persona diversity can be structurally hollow. The distinct combination here is strategic interaction, a manipulated incentive, quantitative between/within decomposition, prospective registration, and mechanical adjudication linking a concentration pattern to a failed incentive-response validation.",
    ),
    dict(
        id="ref-batzner-2025", key="Batzner et al. 2025",
        title="Whose personae? Synthetic persona experiments and pathways to transparency",
        cite="Batzner, J., et al. (2025). AAAI/ACM AIES 8(1), 343–354.",
        href="https://doi.org/10.1609/aies.v8i1.36553",
        role="Transparency standard",
        diff="Reviews 63 persona studies and calls for complete persona disclosure. This project publishes the full sixteen-sentence persona table, the seeded construction rule (mulberry32, seed 20260728), and exact prompt provenance for every request.",
    ),
    dict(
        id="ref-akata-2025", key="Akata et al. 2025",
        title="Playing repeated games with large language models",
        cite="Akata, E., Schulz, L., Coda-Forno, J., Oh, S. J., Bethge, M., and Schulz, E. (2025). Nature Human Behaviour 9, 1380–1390.",
        href="https://doi.org/10.1038/s41562-025-02172-y",
        role="Repeated-game collision",
        diff="Establishes repeated-game LLM play modulated by prompts and opponents. This paper is not first to put LLMs in repeated games; it adds the fixed persona panel, the response-versus-marginal decomposition, exact provenance, prospective registration, and mechanical adjudication.",
    ),
    dict(
        id="ref-pal-2026", key="Pal et al. 2026",
        title="Strategies of cooperation and defection in five large language models",
        cite="Pal, S., et al. (2026). arXiv:2601.09849.",
        href="https://arxiv.org/abs/2601.09849",
        role="Nearest manipulation set",
        diff="Varies continuation probability, payoffs, horizon knowledge, and framing across five LLMs — a near-direct collision on the manipulation set. The differentiation is the corner-mixture mechanism in a persona panel plus the audit architecture, not the games themselves.",
    ),
    dict(
        id="ref-georgousis-2026", key="Georgousis et al. 2026",
        title="Evaluating counterfactual strategic reasoning in large language models",
        cite="Georgousis, D., Lymperaiou, M., Dimitriou, A., Filandrianos, G., and Stamou, G. (2026). arXiv:2603.19167.",
        href="https://doi.org/10.48550/arXiv.2603.19167",
        role="Label/payoff counterfactuals",
        diff="Alters action labels and payoff structures in PD and RPS. This project's D2/D3 label-swap and counterfactual-payoff cells are a preregistered extension and decomposition, not the invention of counterfactual label testing.",
    ),
    dict(
        id="ref-mousavi-2026", key="Mousavi Davoudi et al. 2026",
        title="Same game, different story: a strategic-robustness benchmark",
        cite="Mousavi Davoudi, S. P., et al. (2026). arXiv:2607.19670.",
        href="https://doi.org/10.48550/arXiv.2607.19670",
        role="Representation-robustness term",
        diff="Defines strategic robustness as invariance under payoff-preserving framing, from secondary published aggregates. This project supplies primary registered observations, exact prompt hashes, minimal-pair localization (the S2 switch), and the persona-pool mechanism.",
    ),
    dict(
        id="ref-sclar-2024", key="Sclar et al. 2024",
        title="Quantifying language models' sensitivity to spurious features in prompt design",
        cite="Sclar, M., Choi, Y., Tsvetkov, Y., and Suhr, A. (2024). ICLR.",
        href="https://arxiv.org/abs/2310.11324",
        role="Prompt sensitivity",
        diff="Establishes that prompt formatting matters broadly. X1/X2 here differ by prospective registration, a formally game-equivalent strategic task, and a held-out minimal-span confirmation of one atomic wording-and-position operation.",
    ),
    dict(
        id="ref-shanahan-2023", key="Shanahan et al. 2023",
        title="Role play with large language models",
        cite="Shanahan, M., McDonell, K., and Reynolds, L. (2023). Nature 623, 493–498.",
        href="https://doi.org/10.1038/s41586-023-06647-8",
        role="Simulacra framing",
        diff="Supports treating the experimental object as a model–prompt–deployment configuration inducing a policy, rather than a stable synthetic person — exactly how this paper defines its units.",
    ),
    dict(
        id="ref-bisbee-2024", key="Bisbee et al. 2024",
        title="Synthetic replacements for human survey data? The perils of large language models",
        cite="Bisbee, J., Clinton, J. D., Dorff, C., Kenkel, B., and Larson, J. M. (2024). Political Analysis 32(4), 401–416.",
        href="https://doi.org/10.1017/pan.2024.5",
        role="Close empirical ally",
        diff="Plausible survey averages with compressed variance, distorted coefficients, and temporal drift. This project extends the concern to incentive-bearing strategic interaction and prompt-indexed response surfaces.",
    ),
    dict(
        id="ref-boelaert-2025", key="Boelaert et al. 2025",
        title="Machine bias: how do generative language models answer opinion polls?",
        cite="Boelaert, J., Coavoux, S., Ollion, É., Petev, I., and Präg, P. (2025). Sociological Methods & Research 54(3), 1156–1196.",
        href="https://doi.org/10.1177/00491241251330582",
        role="Excess homogeneity",
        diff="Documents excess homogeneity in LLM poll answers — an adjacent distributional-collapse observation to the corner concentration measured here at the level of strategic choices.",
    ),
    dict(
        id="ref-anthis-2025", key="Anthis et al. 2025",
        title="Position: LLM social simulations are a promising research method",
        cite="Anthis, J. R., et al. (2025). ICML, PMLR 267, 81005–81034.",
        href="https://proceedings.mlr.press/v267/anthis25a.html",
        role="Field survey",
        diff="Catalogs diversity and generalization challenges for LLM social simulation. This project operationalizes several of its recommendations — registration, provenance, replication targets — in a single auditable pipeline.",
    ),
    dict(
        id="ref-hullman-2026", key="Hullman et al. 2026",
        title="This human study did not involve human subjects: validating LLM simulations",
        cite="Hullman, J., Broska, D., Sun, H., and Shaw, A. (2026). arXiv:2602.15785.",
        href="https://doi.org/10.48550/arXiv.2602.15785",
        role="Statistical calibration",
        diff="Distinguishes heuristic interchangeability from statistically calibrated use of synthetic responses. Complementary: calibration presupposes knowing which response surface must be validated — the object this paper measures directly.",
    ),
    dict(
        id="ref-park-2024", key="Park et al. 2024",
        title="LLM agents grounded in self-reports enable general-purpose simulation of individuals",
        cite="Park, J. S., et al. (2024, rev. 2026). arXiv:2411.10109v3.",
        href="https://doi.org/10.48550/arXiv.2411.10109",
        role="Rich-conditioning contrast",
        diff="Shows rich interview conditioning can substantially outperform lightweight persona descriptions. This paper studies the lightweight end deliberately: the cheap construction that practitioners actually deploy at scale.",
    ),
    dict(
        id="ref-argyle-2023", key="Argyle et al. 2023",
        title="Out of one, many: using language models to simulate human samples",
        cite="Argyle, L. P., et al. (2023). Political Analysis 31(3), 337–351.",
        href="https://doi.org/10.1017/pan.2023.2",
        role="Algorithmic fidelity",
        diff="Coined 'algorithmic fidelity' for marginal resemblance. The present result is a worked example of why fidelity checks on marginals do not validate the treatment-response object.",
    ),
    dict(
        id="ref-horton-2023", key="Horton 2023",
        title="Large language models as simulated economic agents (Homo Silicus)",
        cite="Horton, J. J. (2023). NBER Working Paper 31122.",
        href="https://doi.org/10.3386/w31122",
        role="Homo silicus",
        diff="Early articulation of LLMs as simulated economic agents. This project tests the validation practice that grew from it: whether passing aggregate checks licenses treatment inference (it did not, here).",
    ),
    dict(
        id="ref-mei-2024", key="Mei et al. 2024",
        title="A Turing test of whether AI chatbots are behaviorally similar to humans",
        cite="Mei, Q., Xie, Y., Yuan, W., and Jackson, M. O. (2024). PNAS 121(9), e2313925121.",
        href="https://doi.org/10.1073/pnas.2313925121",
        role="Aggregate resemblance",
        diff="Reports behavior 'statistically indistinguishable from a random human' in economic games. Cited as the strongest form of the marginal-resemblance evidence whose inferential limits this paper quantifies.",
    ),
    dict(
        id="ref-dalbo-2011", key="Dal Bó & Fréchette 2011",
        title="The evolution of cooperation in infinitely repeated games",
        cite="Dal Bó, P., and Fréchette, G. R. (2011). American Economic Review 101(1), 411–429.",
        href="https://doi.org/10.1257/aer.101.1.411",
        role="Human comparator (protocol-nonmatched)",
        diff="Canonical human continuation-probability evidence. Used here only as a broad-reference band source and SD reference — explicitly protocol-nonmatched (different δ, payoffs, incentives, assignment, experience). No matched human effect or substitutability claim is made.",
    ),
    dict(
        id="ref-lucas-1976", key="Lucas 1976",
        title="Econometric policy evaluation: a critique",
        cite="Lucas, R. E., Jr. (1976). Carnegie-Rochester Conference Series 1, 19–46.",
        href="https://doi.org/10.1016/S0167-2231(76)80003-6",
        role="Organizing analogy",
        diff="The reduced-form/structural distinction: fitting aggregate resemblance need not identify behavior under a changed regime. Used as an analogy for synthetic subjects, not literal econometrics.",
    ),
    dict(
        id="ref-cronbach-1955", key="Cronbach & Meehl 1955",
        title="Construct validity in psychological tests",
        cite="Cronbach, L. J., and Meehl, P. E. (1955). Psychological Bulletin 52(4), 281–302.",
        href="https://doi.org/10.1037/h0040957",
        role="Construct validity",
        diff="Construct validity rests on a nomological network, not one matching statistic — the methodological home for distinguishing marginal resemblance from response validity.",
    ),
    dict(
        id="ref-ich-e10", key="ICH E10 / Temple & Ellenberg 2000",
        title="Assay sensitivity in controlled trials",
        cite="ICH (2000) E10 guideline; Temple, R., and Ellenberg, S. S. (2000). Annals of Internal Medicine 133(6), 455–463.",
        href="https://doi.org/10.7326/0003-4819-133-6-200009190-00014",
        role="Assay sensitivity",
        diff="A design pinned at floor or ceiling cannot support equivalence or no-effect conclusions. Basis for the project's two-sided interiority gates and the refusal to interpret ceiling cells as slope evidence.",
    ),
    dict(
        id="ref-windrum-2007", key="Windrum et al. 2007 / Grimm et al. 2005",
        title="Agent-based model validation and equifinality",
        cite="Windrum, P., Fagiolo, G., and Moneta, A. (2007). JASSS 10(2):8; Grimm, V., et al. (2005). Science 310, 987–991.",
        href="https://www.jasss.org/10/2/8.html",
        role="Equifinality analogy",
        diff="Matching one aggregate pattern does not establish the generative mechanism; multiple patterns constrain equifinal models. One concise analogy for why marginal checks under-identify the panel's microstructure.",
    ),
    dict(
        id="ref-stats-methods", key="Statistical methods",
        title="Statistical foundations used by the analyses",
        cite="Clopper & Pearson (1934); Hoeffding (1940); Sklar (1959); Efron & Tibshirani (1993); Westfall & Young (1993); Lehmann & Romano (2005); Berger, Bernardo & Sun (2009); Holtzman et al. (2020).",
        href="https://doi.org/10.1093/biomet/26.4.404",
        role="Methods lineage",
        diff="Exact binomial intervals, Fréchet–Hoeffding/Sklar coupling bounds (Proposition B is an application, not a new theorem), bootstrap methodology, resampling-based multiple testing, reference priors, and decoding-degeneration context for temperature secondaries.",
    ),
]

for r in REFS:
    add(
        id=r["id"], type="reference", title=r["key"],
        short=r["title"],
        meta=r["cite"],
        status=None,
        links=[{"label": "Source ↗", "href": r["href"]}],
        body=(
            f"<p><b>{r['title']}.</b> {r['cite']}</p>"
            f"<h2>Relationship to this project — {r['role']}</h2>"
            f"<p>{r['diff']}</p>"
        ),
        rel=[],
    )

# ---------------------------------------------------------------------------
# Figures. PNG derivatives live in site/assets/ (same renders as the paper).
# ---------------------------------------------------------------------------

add(
    id="fig-between-prompt-share", type="figure",
    title="Figure 1 — Between-prompt share of episode-level variation",
    short="Two uncertainty views of the same fixed panel: Jeffreys posteriors vs plug-in estimates.",
    meta="Sources: <code>docs/paper/figures/between-prompt-share.*</code> · pinned vector source in the arXiv package",
    links=[{"label": "SVG", "href": GHB + "/docs/paper/figures/between-prompt-share.svg"},
           {"label": "PDF", "href": GHB + "/docs/paper/figures/between-prompt-share.pdf"}],
    body=(
        '<p><img src="assets/between-prompt-share.png" alt="Between-prompt share of episode-level variation under two uncertainty views"></p>'
        "<p>The Jeffreys fixed-panel posterior propagates uncertainty in six-episode prompt cells "
        "(medians 63.1%–70.5%); plug-in/conditional-bootstrap estimates describe the archived "
        "concentration more literally (85.5%–96.1%). A symmetric-prior sweep shows the stronger "
        "“share above one-half” reading is prior-dependent: α=0.25 medians 74.8%–82.5%, α=1 medians 47.1%–53.5%.</p>"
    ),
    rel=["claim-composition", "an-variance", "an-p52-prior", "phase-5"],
)
add(
    id="fig-prompt-indexed-delta", type="figure",
    title="Figure 2 — Prompt-indexed continuation-probability response",
    short="Δ per persona prompt with conservative exact simultaneous intervals; corners keep non-zero uncertainty.",
    meta="Sources: <code>docs/paper/figures/prompt-indexed-delta.*</code> (+ CSV)",
    links=[{"label": "CSV", "href": GHB + "/docs/paper/figures/prompt-indexed-delta.csv"},
           {"label": "SVG", "href": GHB + "/docs/paper/figures/prompt-indexed-delta.svg"}],
    body=(
        '<p><img src="assets/prompt-indexed-delta.png" alt="Prompt-indexed differences in round-one cooperation with simultaneous intervals"></p>'
        "<p>Δ<sub>i</sub> = p̂<sub>i</sub>(δ=.90) − p̂<sub>i</sub>(δ=.10) for both wording families, "
        "with complete episodes as the unit. The p05 row is the largest candidate eligible under the "
        "conservative exact family gate; p13 is the historical candidate selected by the original rule.</p>"
    ),
    rel=["claim-response", "claim-p13", "phase-5"],
)
add(
    id="fig-condition-means", type="figure",
    title="Figure 3 — Fixed-panel cooperation across the represented treatment",
    short="Condition means with conservative exact intervals across the four repeated-game cells.",
    meta="Sources: <code>docs/paper/figures/condition-means.*</code>",
    links=[{"label": "SVG", "href": GHB + "/docs/paper/figures/condition-means.svg"}],
    body=(
        '<p><img src="assets/condition-means.png" alt="Fixed-panel cooperation by represented continuation-probability condition"></p>'
        "<p>Pool means 0.349, 0.427, 0.432, 0.505 against the preregistered broad-reference band "
        "[0.36, 0.63]; only the S2-absent δ=.10 cell misses, by 0.011. Error bars are conservative "
        "exact condition intervals; lines connect conditions for orientation only.</p>"
    ),
    rel=["claim-p3-a3", "claim-response", "concept-conditions", "phase-5"],
)
add(
    id="fig-representation-effects", type="figure",
    title="Figure 4 — Representation-channel corner shifts",
    short="The S2 wording operation (0/40 → 37/40) and the label-conflict selection shares.",
    meta="Sources: <code>docs/paper/figures/representation-effects.*</code>",
    links=[{"label": "SVG", "href": GHB + "/docs/paper/figures/representation-effects.svg"}],
    body=(
        '<p><img src="assets/representation-effects.png" alt="Two representation interventions in the bare configuration"></p>'
        "<p>Two bare-configuration interventions: the S2 wording-and-position operation moved "
        "cooperation from 0/40 to 37/40, and in the one-shot label conflict the payoff-dominant "
        "action was never chosen when the dominated role carried “Defect.” These are selection "
        "shares, not a uniquely identified causal mechanism.</p>"
    ),
    rel=["claim-s2-switch", "claim-label-swap", "phase-4"],
)
add(
    id="fig-p13-audit", type="figure",
    title="Figure 5 — Post-adjudication familywise constructions for p13",
    short="Three 200,000-permutation gate constructions and the p=0.075 attainability floor.",
    meta="Sources: <code>docs/paper/figures/p13-audit.*</code>",
    links=[{"label": "SVG", "href": GHB + "/docs/paper/figures/p13-audit.svg"}],
    body=(
        '<p><img src="assets/p13-audit.png" alt="Post-adjudication familywise constructions"></p>'
        "<p>p13/s2a under the historical gate (p=0.059230) and the percentile-bootstrap gate "
        "(p=0.043455); under the conservative exact-episode gate p13 is ineligible and the largest "
        "eligible candidate is p05/s2a (p=0.773206). The dotted line marks p=0.075040 — the minimum "
        "attainable familywise p for the archived n=6, 32-candidate exact-gate design. None of these "
        "procedures was registered at the original freeze.</p>"
    ),
    rel=["claim-p13", "an-p13-family", "an-round5-audit", "rev-round-5"],
)

# ---------------------------------------------------------------------------
# Claims ledger. Verbatim numbers from docs/paper/paper.md.
# ---------------------------------------------------------------------------

add(
    id="claim-p3-a3", type="claim", status="registered-pass",
    title="P3-A3 / broad marginal checks — 3 of 4 cells in band",
    short="Registered broad-reference cooperation band [0.36, 0.63]; sole miss 0.011 below the lower bound.",
    meta="Registered before Phase 3 data · band inherited by the Phase 5 panel cells · Paper §4.1",
    body=(
        "<p>The preregistered broad-reference cooperation band was <b>[0.36, 0.63]</b>. Phase 5 "
        "repeated-game pool means were <b>0.349, 0.427, 0.432, 0.505</b>; only the S2-absent δ=.10 "
        "cell fell outside — by <b>0.011</b> below the lower boundary. The panel therefore “passed "
        "coarse marginal checks” in three of four repeated-game cells.</p>"
        "<h2>Why passing is cheap</h2>"
        "<p>Proposition A (paper §4.3): accepting condition means within tolerances ε₀, ε₁ only "
        "bounds the aggregate contrast by ε₀+ε₁. The band’s slack is exactly where the imprecisely "
        "estimated treatment response lives — the checks could be passed without precisely "
        "estimating the response object they might be taken to validate.</p>"
    ),
    rel=["phase-3", "phase-5", "fig-condition-means", "claim-response", "concept-estimands"],
)
add(
    id="claim-composition", type="claim", status="prior-sensitive",
    title="Between-prompt composition — substantial, dominance prior-dependent",
    short="Median between-prompt share 63–71% (Jeffreys α=.5), 47–53% (α=1); plug-in 85–96%.",
    meta="Fixed-panel decomposition · Paper §4.1 · P5-1b context",
    body=(
        "<p>Variation in the panel is strongly prompt-indexed, but its <i>share</i> depends on the "
        "uncertainty model:</p>"
        + tbl(
            ["Uncertainty view", "Between-prompt share (4 repeated-game cells)", "Reading"],
            [
                ["Plug-in / conditional bootstrap", "85.5%, 96.1%, 88.8%, 90.2%",
                 "conditions on recorded boundary concentration; tends upward"],
                ["Fixed-panel Dirichlet, Jeffreys α=0.5", "medians 63.1%, 70.5%, 66.1%, 66.6%",
                 "shrinks six-episode corner cells toward the interior"],
                ["Symmetric α=0.25", "medians 74.8%–82.5%", "P(share&gt;½)&gt;0.999 in every cell"],
                ["Symmetric α=1", "medians 47.1%–53.5%", "P(share&gt;½) only 0.325–0.700"],
            ],
        )
        + "<p>The data support <b>substantial</b> prompt-indexed composition across the sweep, while "
        "the stronger “dominant between-prompt share” reading is <b>prior-dependent</b>. The views "
        "bracket the claim under opposite conditioning choices; they are not interchangeable "
        "estimators.</p>"
    ),
    rel=["claim-p5-1a", "claim-p5-1b", "fig-between-prompt-share", "an-variance",
         "an-p52-prior", "phase-5", "rev-round-9"],
)
add(
    id="claim-response", type="claim", status="imprecise",
    title="Treatment response — small points, wide intervals",
    short="Contrasts +0.083 / +0.078 with conservative simultaneous 95% intervals [−0.171,+0.330] / [−0.181,+0.330].",
    meta="Represented continuation-probability treatment (δ=.10 → δ=.90) · Paper §4.1",
    body=(
        "<p>Across the represented continuation-probability treatment, fixed-panel point "
        "differences are <b>+0.083</b> (S2-absent) and <b>+0.078</b> (S2-present). Conservative "
        "exact simultaneous 95% intervals are <b>[−0.171, +0.330]</b> and <b>[−0.181, +0.330]</b>.</p>"
        "<p>The treatment changed both the continuation process and the text communicating it — "
        "round-one actions identify response under a specified <i>representation</i>, not a "
        "semantically neutral economic parameter. The data establish neither equivalence nor a "
        "null nor a narrow bound. A design-effect heuristic (six episodes per prompt, between-share "
        "0.855–0.961) gives roughly 16.5–18.2 episode-equivalents per condition: prompt-family size, "
        "not raw episode count, is the operative precision constraint.</p>"
    ),
    rel=["claim-p3-a3", "fig-prompt-indexed-delta", "fig-condition-means",
         "concept-conditions", "phase-5", "concept-estimands"],
)
add(
    id="claim-p5-1a", type="claim", status="method-sensitive",
    title="P5-1a — corner-mixture predicate",
    short="Registered support condition passes under 2 of 3 census methods: 3/32, 2/32, 5/32 interior.",
    meta="Registered before Phase 5 data · frozen seat-level rule · threshold: interior fraction < 0.10",
    body=(
        "<p>P5-1a fires when the interior fraction in the exact-bare-twin restricted set "
        "(<code>rep-d90-s2a</code> and <code>os-swap</code>; 32 persona-condition units) is below "
        "0.10 under the frozen seat-level rule. The census is method-sensitive:</p>"
        + tbl(
            ["Census method", "Restricted (of 32)", "Unrestricted (of 96)", "Predicate would support"],
            [
                ["Historical seat-level rule", "3 interior", "14 interior", "yes"],
                ["Conservative exact episode projection", "2 interior", "11 interior", "yes"],
                ["Dirichlet–Jeffreys sensitivity", "5 interior", "19 interior", "no"],
            ],
        )
        + "<p>At n=6 with a three-valued outcome, modest interval-width differences move cells across "
        "the threshold. The continuous composition estimates are primary; the binary census is a "
        "worked example of why certification language should be used sparingly (paper §5.1).</p>"
    ),
    rel=["claim-composition", "an-episode-cluster", "phase-5", "concept-conditions"],
)
add(
    id="claim-p5-1b", type="claim", status="registered-pass",
    title="P5-1b — between-persona dispersion checkpoint",
    short="Corrected between-prompt SDs 0.418–0.478 cleared frozen thresholds 0.309/0.234; retained as permissive.",
    meta="Registered heuristic tolerance from protocol-nonmatched human SD references (ρ=.75)",
    body=(
        "<p>P5-1b compared panel dispersion against thresholds mechanically implied from Dal Bó "
        "&amp; Fréchette’s R=40 strategy-frequency SDs (0.4122 for δ=.50, 0.3116 for δ=.75; frozen "
        "ρ=.75 gave thresholds <b>0.3092</b> and <b>0.2337</b>). Finite-opportunity-corrected "
        "plug-in SDs were <b>0.4182, 0.4784, 0.4408, 0.4323</b> — all clear.</p>"
        "<p>Caveats made explicit after review: unanimous cells are point masses in the conditional "
        "bootstrap; a two-stage prompt+episode bootstrap (a persona-generator estimand) widens the "
        "intervals to 0.27–0.51; and the displayed equality of one lower bound with the human 0.4122 "
        "reference is a rounding coincidence, verified by independent recomputation. P5-1b is a "
        "<b>permissive historical checkpoint, not evidence of human-variance equivalence</b>.</p>"
    ),
    rel=["ref-dalbo-2011", "an-variance", "an-v12-audits", "claim-composition", "phase-5"],
)
add(
    id="claim-p5-2", type="claim", status="registered-mixed",
    title="P5-2 — persona-direction vs task-text classification",
    short="Pooled 45/352 = 0.128 task-consistent; historical verdict preserved; Bayesian proximity to 0.20 is prior-dependent.",
    meta="Registered conflict-cell pooling · frozen boundary 0.20 · Paper §4.2, §5.1",
    body=(
        "<p>P5-2 pools registered conflict cells and classifies whether choices follow task text or "
        "persona-conditioned direction. The pooled task-consistent share is <b>90/704 seat decisions "
        "across 352 episodes</b> — 45/352 = <b>0.128</b> on episode means. The prompt-cluster "
        "bootstrap (principal dependence-aware sensitivity) gives <b>[0.071, 0.189]</b>.</p>"
        "<h2>Prior sensitivity of the Bayesian aggregation</h2>"
        + tbl(
            ["symmetric α", "posterior median", "95% interval", "P(θ ≤ .20)"],
            [
                ["0.10", "0.138", "[0.124, 0.153]", "1.000"],
                ["0.25", "0.152", "[0.135, 0.171]", "&gt;0.999"],
                ["0.50", "0.172", "[0.152, 0.195]", "0.991"],
                ["1.00", "0.205", "[0.182, 0.231]", "0.329"],
            ],
            numeric=(0, 1, 2, 3),
        )
        + "<p>The α=1 posterior crosses the registered 0.20 boundary, so proximity to the boundary "
        "is prior-dependent rather than an independent signal. Every repeated conflict subcell is "
        "mixed; only the swap cell is individually persona-dominant — the pooled classification is "
        "<b>mechanism-confounded and carried by the word/payoff-confounded swap cell</b>.</p>"
    ),
    rel=["an-p52-prior", "an-v13-dependence", "claim-label-swap", "phase-5", "rev-round-14"],
)
add(
    id="claim-p13", type="claim", status="replication-target",
    title="P5-3(a) / p13 — the demoted headline",
    short="0.333→0.750 under the frozen rule, but no family control; exact-gate family is underpowered. Replication target.",
    meta="Historical verdict visible · post-adjudication audits unregistered · Phase 6 target · Paper §4.4",
    body=(
        "<p>Under the historical seat-level rule, persona p13 moved from 0.333 cooperation at δ=.10 "
        "to 0.750 at δ=.90 and passed a per-candidate lower-bound test. The rule searched multiple "
        "candidates and fired on any pass <b>without declared family-level error control</b> — the "
        "defect external review exposed.</p>"
        "<h2>Three 200,000-permutation constructions</h2>"
        + tbl(
            ["Gate construction", "Eligible max", "Familywise p (add-one)", "Monte Carlo 95%"],
            [
                ["Historical seat-level gate", "p13/s2a (+0.4167)", "0.059230", "[0.058194, 0.060268]"],
                ["Percentile episode-cluster bootstrap", "p13/s2a (+0.4167)", "0.043455", "[0.042561, 0.044353]"],
                ["Conservative exact-episode gate", "p05/s2a (+0.0833; p13 ineligible)", "0.773206", "[0.771363, 0.775039]"],
            ],
        )
        + "<p>The exact family cannot reach 0.05 at all: with six episodes per condition, the minimum "
        "attainable familywise p is <b>0.075040</b>. So the archived record neither prospectively "
        "confirms nor decisively disconfirms p13 — it is a <b>replication target</b> whose next test "
        "(Phase 6) must preregister the candidate family, gate, statistic, decision rule, and sample "
        "size before any data are collected. The favorable 0.043 variant cannot create prospective "
        "confirmation; the sealed Branch-2 discussion that celebrated p13 is preserved with its "
        "correction table.</p>"
    ),
    rel=["an-p13-family", "an-round5-audit", "fig-p13-audit", "fig-prompt-indexed-delta",
         "phase-5", "phase-6", "rev-round-1", "rev-round-3", "concept-discussion"],
)
add(
    id="claim-p5-3b", type="claim", status="registered-pass",
    title="P5-3(b) — dominated-option rejection",
    short="All 24 evaluable lanes rejected the bare configuration's dominated swap choice; minimum lower bound 0.462.",
    meta="Registered minimum rate 0.20 · 16 personas at T=0.7 + p02/p06/p11/p15 at T=1.0 and 1.3",
    body=(
        "<p>Clause (b) asked whether each persona lane rejects the bare configuration’s dominated "
        "swap-cell option at a registered minimum rate. Every one of the 24 evaluable lanes retains "
        "a simultaneous episode-exact lower bound above the frozen 0.20 threshold; the minimum is "
        "<b>0.462</b>.</p>"
        "<p>Interpretive limit: clause (b) demonstrates a robust choice reversal under persona "
        "conditioning, but does not identify incentive sensitivity — in the swap cell, label and "
        "payoff point to the same option for persona-conditioned configurations, leaving the "
        "reversal mechanism ambiguous (no format-matched neutral prefix control was run).</p>"
    ),
    rel=["claim-label-swap", "claim-p13", "phase-5", "concept-personas"],
)
add(
    id="claim-s2-switch", type="claim", status="registered-pass",
    title="X2 / S2 switch — one sentence operation, 0/40 → 37/40",
    short="A single wording-and-position operation on the continuation sentence moved bare cooperation across the range.",
    meta="Ladder screening 10 episodes/rung · held-out confirmation 20 fresh episodes/side, seeds 2953–2972, T=0.7",
    body=(
        "<p>The bare configuration cooperated 0.000 at every registered continuation probability. "
        "X2 decomposed the prompt into six spans and ran forward/reverse replacement ladders. The "
        "selected operation replaced and repositioned <i>“After every round there is a {deltaPct}% "
        "chance the session continues with another round”</i> with <i>“At the end of each round "
        "there is a {deltaPct}% chance that the session goes on for one more round.”</i> Held-out "
        "confirmation moved cooperation from <b>0/40 to 37/40</b>.</p>"
        "<p>Wording and position were one atomic operation, so the design does not separate them. "
        "The effect is specific to representing repeated interaction — the registered one-shot D1 "
        "wording main effect was a null (+0.0063, Holm-adjusted p=1.00).</p>"
    ),
    rel=["claim-d1-wording", "fig-representation-effects", "phase-4", "ref-sclar-2024",
         "ref-mousavi-2026"],
)
add(
    id="claim-d1-wording", type="claim", status="registered-fail",
    title="D1 — ordinary one-shot wording main effect (null)",
    short="+0.0063 (SE 0.0210; Holm-adjusted p=1.00) across the 640-episode one-shot battery.",
    meta="Registered wording main effect and interactions · GPT-4.1 · Paper §4.2",
    body=(
        "<p>In the 640-episode one-shot D1 battery, GPT-4.1’s registered wording main effect was "
        "<b>+0.0063</b> (SE 0.0210; Holm-adjusted p=1.00); none of the registered wording "
        "interactions was supported. Ordinary wording variation did essentially nothing.</p>"
        "<p>The contrast that matters: the same presentation whose one-shot mean was 0.100 rose to "
        "0.750 (δ=.10) and 1.000 (δ=.90) when embedded in the repeated-game protocol — announcing "
        "and implementing repeated interaction is a much larger treatment than one-shot wording. "
        "Those ceiling cells were correctly classified ceiling-confounded and do not identify a "
        "continuation-probability slope. This null is what makes the S2 switch result specific "
        "rather than a generic “wording matters” observation.</p>"
    ),
    rel=["claim-s2-switch", "phase-4", "rev-round-14"],
)
add(
    id="claim-label-swap", type="claim", status="registered-pass",
    title="Label-swap conflict — semantic label overrides payoff dominance",
    short="Bare GPT-4.1 chose the cooperation-worded option 0/40, taking the payoff-dominated role when it carried “Defect.”",
    meta="One-shot canonical-payoff label swap (os-swap) · registered cell · Paper §4.2",
    body=(
        "<p>With canonical payoffs fixed and “Cooperate”/“Defect” attached to opposite strategic "
        "roles, the bare configuration chose the cooperation-worded option <b>0/40</b> times — it "
        "took the payoff-dominated role whenever that role carried the word “Defect.”</p>"
        "<p>What this shows: a displayed label or a label-linked learned prior can override payoff "
        "dominance in this registered cell. What it does not show: intrinsic lexical valence. A "
        "learned association (“Defect = the dominant action in PD”) is equally plausible, and no "
        "structurally equivalent non-PD control retained the same labels. Cross-vendor: Gemini "
        "mostly followed payoff dominance instead (0.213 cooperation role, 0.788 the word "
        "COOPERATE) — see the cross-vendor dissociation record.</p>"
    ),
    rel=["claim-crossvendor-label", "claim-p5-2", "fig-representation-effects", "phase-4",
         "ref-georgousis-2026"],
)
add(
    id="claim-leaning", type="claim", status="descriptive",
    title="Leaning-stratum gaps — 0.51 to 0.72",
    short="Preregistered trait-rule strata differ by 0.510–0.719 across conditions; bundle contrasts, not trait causality.",
    meta="Leaning label assigned from generated traits before any behavior existed · 8 vs 8 prompts",
    body=(
        "<p>The preregistered leaning rule (cooperative-leaning iff at least two of agreeable, "
        "patient, risk-averse) divides the panel 8/8 by construction. Descriptive gaps:</p>"
        + tbl(
            ["condition", "cooperative-leaning", "defect-leaning", "difference"],
            [
                ["rep-d10-s2a", "0.615", "0.083", "+0.531"],
                ["rep-d10-s2p", "0.760", "0.094", "+0.667"],
                ["rep-d90-s2a", "0.688", "0.177", "+0.510"],
                ["rep-d90-s2p", "0.865", "0.146", "+0.719"],
                ["os-community", "0.688", "0.019", "+0.669"],
            ],
            numeric=(1, 2, 3),
        )
        + "<p>These are fixed-panel prompt-bundle contrasts. The confirmatory unit is the complete "
        "persona sentence; names, ages, and occupations are uncontrolled semantic components, so no "
        "causal trait effect is claimed.</p>"
    ),
    rel=["concept-personas", "claim-composition", "phase-5", "an-v12-audits"],
)
add(
    id="claim-adversary", type="claim", status="registered-mixed",
    title="RPS adversary suite — exploitability is opponent-contingent",
    short="n-gram2 earned +0.215/round vs GPT-4.1 (Holm-surviving); the WSLS-targeter designed from its signature earned +0.008.",
    meta="50-round RPS suite · registered GPT-4.1 opponent tests, Holm-controlled secondary arms · Appendix A.2",
    body=(
        "<p>A second-order n-gram opponent earned <b>+0.215</b> payoff units per round against "
        "GPT-4.1 and survived Holm correction. A first-order tracker earned <b>−0.118</b> (the "
        "subject beat it). The WSLS-targeter, designed around the earlier near-deterministic "
        "lose-shift signature, earned only <b>+0.008</b> with a lower confidence bound below zero. "
        "The shuffled-history control was not worse than the ordered tracker.</p>"
        "<p>Reading: a behavioral signature measured against one opponent did not transport as a "
        "profitable rule against another — exploitable structure was opponent-contingent rather "
        "than a single global label. Cross-opponent transport interpretation is descriptive.</p>"
    ),
    rel=["phase-4", "claim-rps-role"],
)
add(
    id="claim-rps-role", type="claim", status="registered-fail",
    title="RPS role-attached asymmetry — registered direction reversed",
    short="First-minus-rock contrast −0.181 (prediction was positive); Gemini mirror +0.243. Vendor-specific asymmetry.",
    meta="Neutral symbols, counterbalanced display · registered GPT-4.1 contrast; Gemini mirror descriptive · Appendix A.2",
    body=(
        "<p>After RPS moves were renamed with neutral symbols and display order exactly "
        "counterbalanced, the registered GPT-4.1 first-minus-rock contrast was <b>−0.181</b>: the "
        "preregistered positive-direction hypothesis was not supported and the observed direction "
        "reversed. A support-only Dirichlet analysis assigned probability <b>0.0001</b> to "
        "first-only selection exceeding rock-only selection. The cross-vendor mirror had the "
        "opposite sign, <b>+0.243</b> (one-sided lower bound +0.139).</p>"
        "<p>Descriptive evidence of vendor-specific, role-attached asymmetry in a formally "
        "symmetric game — not a universal “rock bias.” The wrong-sided interval originally attached "
        "to this result was removed in the Round 14 precision pass.</p>"
    ),
    rel=["phase-4", "claim-adversary", "rev-round-14"],
)
add(
    id="claim-crossvendor-label", type="claim", status="descriptive",
    title="Cross-vendor label–payoff dissociation",
    short="GPT-4.1 followed the token DEFECT even when payoff-dominated; Gemini mostly followed payoff dominance.",
    meta="GPT-4.1 cells registered; Gemini figures descriptive under endpoint nonstationarity · Appendix A.2",
    body=(
        "<p>In the canonical label-swap cell, GPT-4.1 chose the cooperation <i>role</i> 1.000 of "
        "the time while choosing the displayed word COOPERATE 0.000 — following the token DEFECT "
        "even when it named the payoff-dominated role. Gemini chose the cooperation role 0.213 and "
        "the word COOPERATE 0.788. When counterfactual payoffs made the cooperation role strictly "
        "dominant and displayed it as DEFECT, cooperation-role shares were 1.000 (GPT-4.1) and "
        "0.975 (Gemini).</p>"
        "<p>For GPT-4.1 word and payoff dominance were congruent in that cell, so it does not "
        "separate the channels (a Round 14 precision correction); for Gemini the cell is "
        "informative because it moved to the payoff-dominant role despite the DEFECT label. The "
        "vendors differ in when a familiar action word overrides supplied payoffs; no universal "
        "lexical mechanism is identified.</p>"
    ),
    rel=["claim-label-swap", "phase-4", "phase-5", "rev-round-14"],
)
add(
    id="claim-entropy", type="claim", status="descriptive",
    title="Temperature secondary — matched-lattice entropy decline",
    short="Pooled entropy 0.831 → 0.782 → 0.770 bits at T=0.7/1.0/1.3 on the identical 13-unit lattice.",
    meta="Registered secondary, composition-confounded as pooled; survives matched sweep · Appendix A.1",
    body=(
        "<p>Base-2 Shannon entropy over round-one choices, restricted to persona-cell lanes "
        "observed at all three temperatures:</p>"
        + tbl(
            ["temperature", "matched units", "seats", "pooled entropy (bits)", "mean within-unit (bits)"],
            [
                ["0.7", "13", "544", "0.8310", "0.4484"],
                ["1.0", "13", "284", "0.7822", "0.2566"],
                ["1.3", "13", "284", "0.7698", "0.2877"],
            ],
            numeric=(0, 1, 2, 3, 4),
        )
        + "<p>The registered pooled decline is partly composition-confounded but survives on the "
        "identical lattice. Neither statistic identifies a temperature mechanism; the "
        "high-temperature continuation interaction was not registered.</p>"
    ),
    rel=["phase-5", "an-v12-audits"],
)
add(
    id="claim-drift", type="claim", status="procedural",
    title="Endpoint drift and subject eligibility",
    short="Gemini sentinel fell from 10/10 to 6/10–7/10 on an unversioned endpoint; Claude Haiku failed the entry gate.",
    meta="Procedural monitoring record, not a behavioral-effect estimate · Appendix A.2",
    body=(
        "<p>The Gemini sentinel fingerprint changed from 10/10 baseline matches to an oscillating "
        "sequence — 10 → 9 → 9 → 8 → 8 → 7* → [re-baseline 10] → 6* → 7* → 6* → 7* — on the "
        "unversioned endpoint, triggering block-boundary freezes, disclosure memos, re-baselining, "
        "and a later attestation gate; the Phase 4 F cross-vendor tier was demoted to "
        "descriptive-only rather than re-evaluating the rule on the data it fired on. GPT-4.1’s "
        "sentinel cells remained 10/10 throughout, and every deviant episode was a clean, valid "
        "single-token choice — a distributional change, not an infrastructure fault.</p>"
        "<p>Separately, the original Claude Haiku candidate failed the registered Gate-0 "
        "behavioral entry gate (it could not complete a turn at max_tokens=16) and was replaced "
        "under a sealed amendment. Model identity and endpoint availability do not by themselves "
        "establish a stable, usable behavioral subject; deployed-model change over time is why "
        "behavioral sentinels exist in the architecture. Contaminated confirmatory spend: zero.</p>"
    ),
    rel=["phase-4", "phase-5", "concept-architecture"],
)

# ---------------------------------------------------------------------------
# Phases.
# ---------------------------------------------------------------------------

add(
    id="phase-1-2", type="phase", status="superseded",
    title="Phases 1–2 — prototype and instrument repair",
    short="The historical v1 prototype and the mechanical re-adjudication layer built after it exposed analyst discretion.",
    meta="Not prospective confirmation · v1 frozen July 2026 · postmortem published",
    links=[{"label": "Postmortem", "href": GHB + "/docs/POSTMORTEM.md"},
           {"label": "v1 paper (frozen)", "href": GHB + "/docs/v1/paper-v1.md"},
           {"label": "Metrics spec", "href": GHB + "/docs/METRICS.md"}],
    body=(
        "<p><b>Phase 1</b> was the algorithmic-strategy prototype: 7 classic games, 8 strategies, "
        "40 experiments, and a 2,149-word v1 paper whose 11 claims were all called “supported.” "
        "Mechanical re-adjudication in Phase 2 revised that record to <b>6 supported, 1 refuted, "
        "4 inconclusive</b> — the refuted claim (TFT &gt;50% cooperation vs Always Defect; observed "
        "0.02) became dead prediction #1. Four process errors were documented: a literature "
        "transplant, payoff totals presented as per-round, metrics applied to undefined game "
        "classes, and single unseeded runs treated as facts.</p>"
        "<p><b>Phase 2</b> rebuilt the instrument: seeded mulberry32 randomness, 20-seed replicate "
        "batches, a versioned per-class metric suite, predicate-based mechanical adjudication "
        "(verdicts never hand-set; predicates immutable after first adjudication), and a 396-run "
        "backfill with zero drift. Neither phase carries confirmatory weight; they exist in the "
        "record because the correction is part of the result.</p>"
    ),
    rel=["phase-3", "concept-architecture"],
)
add(
    id="phase-3", type="phase", status="sealed",
    title="Phase 3 — can an LLM serve as a behavioral subject?",
    short="Bare GPT-4.1 in repeated PD, framing, and RPS: 3 supported, 6 refuted, 1 inconclusive; X1 flips the corner.",
    meta="Complete 2026-07-24 · registry phase3-v1/v2 · 320 LLM runs + 20 baselines · claims registered before data",
    links=[{"label": "Phase 3 report", "href": GHB + "/docs/phase3-report.md"},
           {"label": "Preregistration", "href": GHB + "/docs/phase3-preregistration.md"},
           {"label": "Layer-2 statistics", "href": GHB + "/docs/phase3-layer2.md"}],
    body=(
        "<p>Bare GPT-4.1 (temperature 0.7, max_tokens 16, no persona) across three families: "
        "<b>A</b> — random-termination repeated PD at δ ∈ {.10, .50, .75, .90} with a payoff "
        "isomorph; <b>B</b> — one-shot framing (Community / Wall Street / neutral); <b>C</b> — "
        "50-round RPS versus a pattern tracker, Nash mixing, and self-play. 320 LLM runs, 5,820 "
        "calls, plus 20 deterministic baselines.</p>"
        "<h2>Registered verdicts</h2>"
        + tbl(
            ["Predicate", "Verdict", "Key number"],
            [
                ["P3-A1 shadow of the future", "refuted", "0.000 cooperation at both δ"],
                ["P3-A2 risk-dominance separation", "refuted", "0.000 vs 0.000"],
                ["P3-A3 human band [0.36, 0.63]", "refuted", "0.000"],
                ["P3-A4 isomorph invariance", "refuted", "fails the separation limb"],
                ["P3-B1 framing direction", "supported", "0.175 vs 0.000, CI [0.061, 0.290]"],
                ["P3-B2 framing magnitude", "inconclusive", "edge rule at Wall Street = 0"],
                ["P3-B3 neutral interior", "supported", "0.000 ≤ 0.000 ≤ 0.175"],
                ["P3-C1 RPS rock band", "refuted", "rock 0.80 ∉ [0.33, 0.40]"],
                ["P3-C2 win-stay / lose-shift", "supported", "P(shift|lose) 0.974"],
                ["P3-C3 tracker exploits LLM", "refuted, sign reversed", "−0.103; subject beat the tracker"],
                ["P3-X1 paraphrase robustness", "refuted", "0.000 → 1.000 under two rewordings, same seeds"],
            ],
        )
        + "<p>The approved headline: <i>prompt wording dominated the tested incentive manipulation "
        "and rendered single-wording behavioral inference non-identifiable.</i> X1’s total corner "
        "flip is what motivated Phase 4’s representation program. All 320 runs replay bit-exact "
        "with zero live calls; the disclosed Phase 3 gap (no provider response IDs) is stated in "
        "the paper.</p>"
    ),
    rel=["phase-4", "claim-p3-a3", "concept-architecture", "concept-conditions"],
)
add(
    id="phase-4", type="phase", status="sealed",
    title="Phase 4 — representation, counterfactuals, adversaries, drift",
    short="Registry v3, 250 sealed arms, 2,864 runs: the S2 switch, label-swap conflict, corner-confounded δ-assays, adversary suite, and the sentinel that caught endpoint drift.",
    meta="Approved 2026-07-24 · sealed tag phase4-v3-seal · closed phase4-final 2026-07-28 · 20,102 calls",
    links=[{"label": "Final report", "href": GHB + "/docs/phase4/final-report.md"},
           {"label": "Predicates", "href": GHB + "/docs/phase4/predicates.md"},
           {"label": "Seal record", "href": GHB + "/docs/phase4/seal-record.md"},
           {"label": "Replay audit", "href": GHB + "/docs/phase4/step8-replay-audit.md"}],
    body=(
        "<p>Phase 4 asked how much of Phase 3’s corner behavior was representation. Registry v3 "
        "sealed 44 new templates and 250 arms before data; GPT-4.1 primary with a Gemini 2.5 Flash "
        "cross-vendor mirror (the original Claude Haiku candidate failed Gate-0 and was replaced "
        "under an archived amendment).</p>"
        "<h2>Blocks</h2>"
        "<ul>"
        "<li><b>X2 span ladder</b> — decomposed the prompt into six spans, walked forward/reverse "
        "ladders, localized the S2 continuation sentence, and confirmed it held-out: 0/40 → 37/40 "
        "(est +0.925, LB95 +0.708). Registered confirmatory.</li>"
        "<li><b>D1 factorial</b> — 640 episodes over presentation factors: every registered GPT-4.1 "
        "main effect null (grand mean 0.2547); the Gemini mirror was presentation-sensitive where "
        "the primary was not.</li>"
        "<li><b>D2 label/payoff decoupling</b> — role channel strong on both vendors (+0.725 / "
        "+0.638); word channel null on GPT-4.1 but +0.763 on Gemini; conflict cell: payoff-dominant "
        "branch, word-following share 0.0, CP [0, 0.088].</li>"
        "<li><b>D3 positional bias</b> — registered direction reversed on GPT-4.1 (−0.181; "
        "P(first-only&gt;rock-only)=0.0001) and supported on Gemini (+0.243): vendors disagree in "
        "sign.</li>"
        "<li><b>E δ-assays</b> — all four corner-confounded under the registered two-sided gate "
        "(ceiling cells everywhere); explicitly <i>not</i> evidence of δ-insensitivity.</li>"
        "<li><b>F adversary suite</b> — n-gram2 exploits GPT-4.1 (+0.215, Holm-surviving); the "
        "signature-designed WSLS-targeter earns +0.008; the tracker loses (−0.118). Exploitability "
        "is opponent-contingent.</li>"
        "<li><b>Sentinels</b> — behavioral fingerprinting caught a time-indexed Gemini "
        "discontinuity that version pinning was structurally blind to; the affected tier was "
        "demoted, never rescued.</li>"
        "</ul>"
        "<p>2,864/2,864 completed observations replay byte-exact; 24 provider-failure partials are "
        "individually disclosed non-observations. Registry seal is externally anchored "
        "(OpenTimestamps; tags <code>phase4-v3-seal</code>, <code>phase4-final</code>).</p>"
    ),
    rel=["phase-3", "phase-5", "claim-s2-switch", "claim-d1-wording", "claim-label-swap",
         "claim-adversary", "claim-rps-role", "claim-drift", "concept-architecture"],
)
add(
    id="phase-5", type="phase", status="sealed",
    title="Phase 5 — the sixteen-persona panel",
    short="16 sealed persona sentences × 6 conditions × 3 temperatures; 1,712 runs; both author predictions with teeth failed.",
    meta="Sealed 2026-07-28 (registry v4, tag phase5-v4-seal) · closed phase5-final · 10,428 calls, 93.2% of amended cap",
    links=[{"label": "Final report", "href": GHB + "/docs/phase5/final-report.md"},
           {"label": "Adjudication report", "href": GHB + "/docs/phase5-close/adjudication-report.md"},
           {"label": "Seal record", "href": GHB + "/docs/phase5/seal-record.md"},
           {"label": "Branch selection", "href": GHB + "/docs/phase5-close/branch-selection.md"}],
    body=(
        "<p>The final experiment: sixteen sealed persona sentences (generated by seeded PRNG "
        "before any data; full 2×2×2×2 trait cross) prepended to byte-identical Phase 3/4 task "
        "text, across six conditions and a registered temperature sweep. The discussion was "
        "written and sealed before dispatch; the stopping rule forbade new arms.</p>"
        "<h2>Registered verdicts (adjudicated by sealed code)</h2>"
        + tbl(
            ["Predicate", "Verdict", "Key number"],
            [
                ["P5-1a corner mixture", "SUPPORTED", "3/32 = 0.094 &lt; 0.10 — by a single unit"],
                ["P5-1b dispersion vs human SD", "corner-mixture-consistent", "SDs 0.42–0.48 vs thresholds 0.23/0.31"],
                ["P5-2 surface-cue dominance", "persona-dominant — prediction failed", "0.128, CP [0.104, 0.155]; predicted task-dominant"],
                ["P5-3 interior-persona existence", "16/16 pass — prediction failed", "predicted zero; p13 alone fires the slope clause"],
                ["P5-4 temperature refutation", "not refuted", "Newcombe LB −0.095; entropy falls with T"],
            ],
        )
        + "<p>Both author predictions with teeth failed — those failures are dead predictions #11 "
        "and #12 and selected precommitted <b>Branch 2</b> (“an interior persona exists”) with the "
        "not-task-dominant P5-2 variant. Post-adjudication review then demoted the p13 reading "
        "(no family control) — the correction that reshaped the paper. 1,712/1,712 runs replay "
        "byte-exact; zero invalid trials at any temperature; sentinels green at all 10 checks; "
        "budget projections matched actuals to the call.</p>"
    ),
    rel=["phase-4", "phase-6", "concept-personas", "concept-conditions", "concept-discussion",
         "claim-p5-1a", "claim-p5-1b", "claim-p5-2", "claim-p13", "claim-p5-3b",
         "claim-composition", "claim-response", "claim-entropy"],
)
add(
    id="phase-6", type="phase", status="prospective",
    title="Phase 6 — the preregistered replication (not yet run)",
    short="Forbidden before publication by the scope seal; its design requirements are already written.",
    meta="Scope seal rule 2: “No Phase 6 before publication” · design requirements in paper §A.3",
    links=[{"label": "Scope seal", "href": GHB + "/docs/paper/scope-seal.md"},
           {"label": "Prospective power table", "href": GHB + "/docs/analysis/submission/round5/round5-review-audit.md"}],
    body=(
        "<p>Phase 6 does not exist yet — deliberately. The sealed stopping rule forbids any new "
        "arm before publication, so everything Phase 5 surfaced routes here. The paper commits the "
        "replication to preregister, before any data: the candidate family, the episode-level "
        "dependence unit, the interiority gate, the maximum statistic, the familywise decision "
        "rule, and the sample size.</p>"
        "<p>The archived design’s power problem is quantified: at 6 episodes/arm the exact gate "
        "cannot reject at all (minimum attainable familywise p = 0.075); illustrative planning "
        "shows ~20 episodes/arm reaches ≈78% family rejection for a p13-sized effect and 30 "
        "reaches ≈96%. The design should also add a format-matched neutral prefix, a continuation "
        "× wording factorial, and a non-PD label-conflict control — the three confounds the "
        "current record cannot separate.</p>"
    ),
    rel=["claim-p13", "phase-5", "an-round5-audit"],
)

# ---------------------------------------------------------------------------
# Protocol / concept pages.
# ---------------------------------------------------------------------------

add(
    id="concept-personas", type="concept", status="sealed",
    title="The sixteen persona prompts",
    short="One sealed sentence each, generated by seeded PRNG before any data; the complete sentence is the experimental unit.",
    meta="mulberry32 seed 20260728 · full trait cross · SHA-256 per persona · sealed in registry v4",
    links=[{"label": "Persona table", "href": GHB + "/docs/analysis/persona-table.md"},
           {"label": "Sealed personas JSON", "href": GHB + "/docs/phase5/personas-v4.json"}],
    body=(
        "<p>Template: <i>“You are {Name}, a {age}-year-old {occupation}. People who know you "
        "describe you as {d1}, {d2}, and {d3}.”</i> The sixteen sentences are the full cross of "
        "two age bands × agreeable/competitive × patient/impulsive × risk-averse/risk-seeking. "
        "The leaning label (cooperative iff ≥2 of agreeable, patient, risk-averse) was fixed at "
        "generation — never from behavior. A sealed banned-content guard excluded game vocabulary "
        "(“cooperat”, “defect”, “payoff”, “strateg”, …). Names, ages, and occupations are "
        "uncontrolled semantic treatments; trait-level attribution is exploratory.</p>"
        + tbl(
            ["id", "name", "age", "occupation", "traits", "leaning", "interior cells"],
            [
                ["p01", "Arden", "31", "bus driver", "agreeable · patient · risk-averse", "coop", "0"],
                ["p02", "Sasha", "35", "nurse", "agreeable · patient · risk-seeking", "coop", "0"],
                ["p03", "Quinn", "31", "electrician", "agreeable · impulsive · risk-averse", "coop", "0"],
                ["p04", "Marlow", "31", "physiotherapist", "agreeable · impulsive · risk-seeking", "defect", "2"],
                ["p05", "Riley", "35", "optician", "competitive · patient · risk-averse", "coop", "3"],
                ["p06", "Tatum", "33", "pharmacist", "competitive · patient · risk-seeking", "defect", "0"],
                ["p07", "Devon", "34", "dental hygienist", "competitive · impulsive · risk-averse", "defect", "1"],
                ["p08", "Avery", "32", "librarian", "competitive · impulsive · risk-seeking", "defect", "0"],
                ["p09", "Rowan", "64", "archivist", "agreeable · patient · risk-averse", "coop", "0"],
                ["p10", "Morgan", "63", "surveyor", "agreeable · patient · risk-seeking", "coop", "0"],
                ["p11", "Jordan", "61", "accountant", "agreeable · impulsive · risk-averse", "coop", "0"],
                ["p12", "Casey", "65", "veterinary technician", "agreeable · impulsive · risk-seeking", "defect", "1"],
                ["<b>p13</b>", "<b>Harper</b>", "61", "landscape gardener", "competitive · patient · risk-averse", "coop", "<b>4</b>"],
                ["p14", "Ellis", "65", "bookkeeper", "competitive · patient · risk-seeking", "defect", "0"],
                ["p15", "Reese", "63", "school teacher", "competitive · impulsive · risk-averse", "defect", "3"],
                ["p16", "Emerson", "62", "carpenter", "competitive · impulsive · risk-seeking", "defect", "0"],
            ],
        )
        + "<p>Ten personas are pure-corner in every cell; the 14 interior units concentrate in six "
        "personas (p13: 4, p05 and p15: 3 each). p13 — Harper, the competitive-patient-risk-averse "
        "landscape gardener — is the persona whose slope reading became the program’s central "
        "correction story.</p>"
    ),
    rel=["phase-5", "claim-leaning", "claim-p13", "ref-batzner-2025"],
)
add(
    id="concept-conditions", type="concept", status="sealed",
    title="The six Phase 5 conditions",
    short="Four repeated-PD cells (δ × S2 wording) plus two one-shot conflict/framing cells, all byte-identical to sealed templates.",
    meta="96 Tier-A persona–condition units = 16 prompts × 6 conditions",
    body=(
        tbl(
            ["Code", "Condition", "Role in the paper"],
            [
                ["<code>rep-d10-s2a</code>", "repeated PD, δ=.10, S2 absent", "level, variance, response"],
                ["<code>rep-d10-s2p</code>", "repeated PD, δ=.10, S2 present", "level, variance, response"],
                ["<code>rep-d90-s2a</code>", "repeated PD, δ=.90, S2 absent", "level, variance, response"],
                ["<code>rep-d90-s2p</code>", "repeated PD, δ=.90, S2 present", "level, variance, response"],
                ["<code>os-swap</code>", "one-shot canonical-payoff label swap", "semantic-label / payoff conflict"],
                ["<code>os-community</code>", "one-shot Community framing", "near-interior framing anchor"],
            ],
        )
        + "<p>S2-absent/S2-present are the registered wording families around the switch-bearing "
        "continuation sentence found by the X2 ladder. The registered P5-1a denominator was "
        "restricted to cells whose exact recorded bare twin failed the same interiority gate — an "
        "outcome-blind completion fixed that set as <code>rep-d90-s2a</code> and "
        "<code>os-swap</code> (32 units); the Community twin passed the bare gate (7/42 interior — "
        "the program’s only bare interior point), and three repeated cells lacked exact bare "
        "twins.</p>"
    ),
    rel=["phase-5", "claim-s2-switch", "claim-p5-1a", "concept-estimands"],
)
add(
    id="concept-architecture", type="concept", status="final",
    title="Audit architecture — register, execute, adjudicate, correct, replay, preserve",
    short="The pipeline is procedurally exact and publicly replayable; the record includes where that stopped short of statistical validity.",
    meta="Event-sourced engine · sealed registries · mechanical predicates · OpenTimestamps anchors · zero-call capsule",
    links=[{"label": "Capsule", "href": GHT + "/capsule"},
           {"label": "Instance ledger (22 process failures)", "href": GHB + "/docs/instance-ledger.md"},
           {"label": "Close-out verification", "href": GHB + "/docs/close-out-verification.md"}],
    body=(
        "<p><b>Register.</b> Claims carry structured predicates sealed before their adjudicating "
        "data; predicates are immutable after first adjudication (an HTTP 409 HARKing guard). "
        "Registries seal append-only with SHA-256 manifests, annotated tags, GitHub releases, and "
        "OpenTimestamps Bitcoin anchors (blocks 959483–960086).</p>"
        "<p><b>Execute.</b> An event-sourced engine archives every rendered prompt, completion, "
        "decoding configuration, action, payoff, seed, and provenance field — 5,505 completed "
        "runs, 54,276 rounds, 108,552 seat decisions, 36,251 provider-request events. Sealed "
        "execution schedules, transactional budget caps, and fail-closed freezes govern dispatch.</p>"
        "<p><b>Adjudicate.</b> Verdicts come from sealed adjudicator code that never reads claim "
        "prose, with selftest fixtures; the author adjudicated nothing. Twelve registered author "
        "predictions were refuted and published.</p>"
        "<p><b>Correct.</b> External review exposed family-error, dependence, construct, and "
        "boundary-uncertainty defects. Corrections are additive: sealed records are never edited; "
        "current interpretations travel beside them. A 22-instance process-failure ledger is "
        "public; every resolution that touched confirmatory standing went the conservative "
        "direction.</p>"
        "<p><b>Replay.</b> The public capsule verifies <b>4,919 archived Phase 3–5 runs (4,916 "
        "confirmatory + 3 legacy diagnostics)</b> with zero credentials and zero live model calls: "
        "4,896 LLM runs byte-exact plus 20 deterministic baselines independently recomputed.</p>"
        "<p><b>Preserve.</b> Sealed discussion branches, the v10 text freeze, manuscript history, "
        "and the dead-predictions ledger keep the interpretive record inspectable. The boundary is "
        "stated in the paper: <i>the pipeline can enforce a registered predicate exactly; it "
        "cannot guarantee that the predicate represents a valid estimand, test family, or "
        "construct.</i></p>"
    ),
    rel=["concept-discussion", "claim-drift", "an-counts", "art-capsule", "phase-3", "phase-4",
         "phase-5"],
)
add(
    id="concept-estimands", type="concept", status="final",
    title="Units, estimands, and what marginal checks cannot identify",
    short="Deployment → persona prompt → condition → episode → seat → round → request; four estimand families kept distinct.",
    meta="Sources: hierarchy.md, propositions.md · Paper §3, §4.3",
    links=[{"label": "Unit hierarchy", "href": GHB + "/docs/analysis/hierarchy.md"},
           {"label": "Identification propositions", "href": GHB + "/docs/analysis/propositions.md"}],
    body=(
        "<p>The unit chain is deployment → explicit persona prompt (16 + bare control) → condition "
        "(6 cells, 160 arms) → episode (1,712 in Phase 5) → seat (2/episode) → round (54,276) → "
        "provider request (36,251). These nouns are not interchangeable; calls are operational "
        "scale, not subjects.</p>"
        "<h2>Four estimand families</h2>"
        + tbl(
            ["Family", "Definition", "Status in this program"],
            [
                ["Fixed-panel", "properties of these sixteen sealed prompts", "all registered Phase 5 predicates attach here"],
                ["Persona-generator", "a wider persona population", "exploratory at n=16; two-stage bootstrap targets it"],
                ["Prompt-indexed", "Δ<sub>i</sub> for the same explicit string across conditions", "identified; a latent person’s effect is not (invariance untested)"],
                ["Human-substitution", "human–LLM equivalence", "not claimed; references protocol-nonmatched"],
            ],
        )
        + "<h2>Identification propositions</h2>"
        "<p><b>Proposition A</b> — accepted bands [ℓ₀,u₀], [ℓ₁,u₁] identify only "
        "Δ ∈ [ℓ₁−u₀, u₁−ℓ₀]: the interval can contain zero, an attenuated effect, or the wrong "
        "sign. Exact mean matching would force the aggregate effect by identity — the failure "
        "lives in the slack of <i>coarse</i> criteria. <b>Proposition B</b> — mean and variance "
        "identify neither the between/within split, the shape, boundary mass, nor the "
        "cross-condition coupling that defines prompt-indexed response (a Fréchet–Hoeffding/Sklar "
        "application, not a new theorem).</p>"
    ),
    rel=["claim-p3-a3", "claim-composition", "claim-response", "ref-stats-methods",
         "ref-persson-2026"],
)
add(
    id="concept-discussion", type="concept", status="sealed",
    title="The precommitted discussion — written before the data, corrected after",
    short="Four full discussion branches sealed pre-dispatch; verdicts selected Branch 2; review then invalidated its headline.",
    meta="Sealed with registry v4 (sha 1f1d7de9…e356) · selection rule mechanical · correction table in paper §5.2",
    links=[{"label": "Discussion branches (sealed)", "href": GHB + "/docs/paper/discussion-branches.md"},
           {"label": "Branch selection record", "href": GHB + "/docs/phase5-close/branch-selection.md"},
           {"label": "Scope-seal status", "href": GHB + "/docs/paper/scope-seal-status.md"}],
    body=(
        "<p>Before Phase 5 dispatched, four complete discussion texts were written and sealed — "
        "one for each combination of the registered verdict axes (corner mixture / interior "
        "persona / temperature grading), with both P5-2 variant paragraphs embedded. <i>“The "
        "author does not get a vote after data exists.”</i> The registered selection rule fired on "
        "axis B (at-least-one interior persona) and spliced <b>Branch 2</b> verbatim.</p>"
        "<p>External review then showed Branch 2’s headline — an unconfounded incentive-response "
        "existence result — was not prospectively established (no family control; the exact "
        "post-adjudication family is underpowered). The sealed text remains byte-identical in the "
        "record, quoted in §5.2 beside a four-row correction table, because its evidentiary value "
        "lies partly in making interpretive error visible.</p>"
        "<p>The companion scope seal froze the experimental boundary: no new arms, no Phase 6 "
        "before publication, exit by registered adjudication + replay + anchored release. Its "
        "header still reads “PROPOSED — UNSEALED” because the file sealed <i>byte-exact</i> before "
        "dispatch — editing it now would destroy the chronology it proves; a living addendum "
        "explains the apparent mismatch instead.</p>"
    ),
    rel=["phase-5", "claim-p13", "concept-architecture"],
)

# ---------------------------------------------------------------------------
# Post-adjudication analyses (all zero-call, over archived databases).
# ---------------------------------------------------------------------------

add(
    id="an-p52-prior", type="analysis", status="post-adjudication",
    title="P5-2 prior-sensitivity sweep",
    short="Posterior median rises 0.138 → 0.205 across symmetric α; the α=1 interval crosses the registered 0.20 boundary.",
    meta="500,000 draws per α · seeds 2026080100–03 · 40 clusters over 352 episodes",
    links=[{"label": "Record", "href": GHB + "/docs/analysis/submission/p52-prior-sensitivity.md"},
           {"label": "JSON", "href": GHB + "/docs/analysis/submission/p52-prior-sensitivity.json"}],
    body=(
        "<p>Each of 40 sparse persona × conflict-cell clusters receives an independent symmetric "
        "Dirichlet prior; at α=0.5 the total prior concentration (≈60 category-count units) is "
        "non-negligible against 352 observed episodes and pulls the aggregate toward 0.5. The "
        "sweep shows the Jeffreys posterior’s proximity to the registered 0.20 boundary is a "
        "prior artifact, not a data signal — the empirical anchor stays 45/352 = 0.128 and the "
        "prompt-cluster bootstrap [0.071, 0.189] remains the principal dependence-aware "
        "sensitivity. This correction (Round 14) demoted “independent Bayesian corroboration” "
        "from the P5-2 story.</p>"
    ),
    rel=["claim-p5-2", "rev-round-14", "phase-5"],
)
add(
    id="an-p13-family", type="analysis", status="post-adjudication",
    title="p13 familywise audit (final)",
    short="Three 200,000-permutation constructions: p 0.0592 / 0.0435 / 0.7732; exact gate excludes p13 entirely.",
    meta="Seed 20260783 · dynamic gate reapplied inside every permutation · add-one convention",
    links=[{"label": "Final audit", "href": GHB + "/docs/analysis/submission/p13-family-audit-final.md"},
           {"label": "Superseded R2 audit", "href": GHB + "/docs/analysis/r2/p13-family-audit.md"}],
    body=(
        "<p>Episode outcomes are permuted between δ conditions within each candidate, the complete "
        "data-dependent gate re-applied inside every permutation, and the familywise maximum "
        "tested. The first pass (R2, B=2,000) gave p = 0.0525 ± 0.0050 and downgraded p13 to "
        "“suggestive”; the final B=200,000 audit sharpened this to 0.059230 (historical gate), "
        "0.043455 (percentile bootstrap — reported symmetrically, cannot create prospective "
        "confirmation), and 0.773206 (conservative exact gate, under which p13 is ineligible and "
        "p05/s2a leads at +0.0833). The registered procedure’s empirical familywise false-fire "
        "rate under the null was 12.9%.</p>"
    ),
    rel=["claim-p13", "an-round5-audit", "fig-p13-audit", "rev-round-3"],
)
add(
    id="an-round5-audit", type="analysis", status="post-adjudication",
    title="Round-5 review audit — dynamic gate, attainability, provenance",
    short="Gate parity 56/56; dynamic vs frozen mask differs in 14.4% of null draws; exact-gate floor p=0.075 at n=6.",
    meta="Answers Explore Science issues B1, B3, A2 · seed 20260792",
    links=[{"label": "Audit", "href": GHB + "/docs/analysis/submission/round5/round5-review-audit.md"}],
    body=(
        "<p>Three verifications requested by external review: <b>(B1)</b> the interiority gate is "
        "genuinely re-applied inside permutations — 56 precomputed gate values, 25.6M lookup "
        "applications, 0 parity failures, and a regression showing a frozen-mask shortcut would "
        "change the maximum in 718/5,000 null draws; <b>(B3)</b> with six episodes per condition "
        "only 12 of 28 outcome compositions pass the exact gate, two passing cells can differ by "
        "at most ⅓, and the archived family’s minimum attainable familywise p is 0.075040 — the "
        "power boundary that caps what the archived record can decide about p13; <b>(A2)</b> the "
        "provenance boundary: request-side hashes cover 30,421/30,421 Phase 4–5 events, but replay "
        "proves reproducibility from the released archive, not provider attestation.</p>"
    ),
    rel=["an-p13-family", "claim-p13", "phase-6", "rev-round-5"],
)
add(
    id="an-variance", type="analysis", status="post-adjudication",
    title="Finite-opportunity variance correction",
    short="Corrected between-prompt SDs 0.418–0.478; plug-in between-shares 85.5–96.1% with bootstrap intervals.",
    meta="50,000 bootstrap replicates · 16 personas × 6 episodes per cell",
    links=[{"label": "Record", "href": GHB + "/docs/analysis/submission/variance-correction.md"},
           {"label": "v11 latent-propensity view", "href": GHB + "/docs/analysis/submission/variance-uncertainty-v11.md"}],
    body=(
        "<p>Separates real between-prompt variation from finite-opportunity measurement noise "
        "(six episodes per cell): corrected SDs 0.4182 / 0.4784 / 0.4408 / 0.4323, between-shares "
        "0.855 / 0.961 / 0.888 / 0.902. The v11 companion adds the fixed-panel Dirichlet–Jeffreys "
        "latent-propensity view (share medians 0.631–0.705), created after Round 9 identified that "
        "resampling unanimous six-episode cells as point masses is a conditional statement, not a "
        "complete uncertainty statement. Together they are the two bracketing views quoted "
        "throughout the paper.</p>"
    ),
    rel=["claim-composition", "claim-p5-1b", "fig-between-prompt-share", "rev-round-9"],
)
add(
    id="an-episode-cluster", type="analysis", status="post-adjudication",
    title="Episode-cluster sensitivity census",
    short="Interiority reclassified under episode units: 3/32 → 2/32 → 5/32 across methods; disagreement = method sensitivity.",
    meta="Exact conservative projection primary; percentile bootstrap retained as audit trail",
    links=[{"label": "Record", "href": GHB + "/docs/analysis/submission/episode-cluster-sensitivity.md"}],
    body=(
        "<p>Because two seats share an episode, seat-level intervals are anti-conservative under "
        "positive dependence — the Round 2 dependence critique. This census reruns the P5-1a, "
        "P5-2, and clause-(b) classifications with complete episodes as the unit. The frozen rule "
        "is treated as historical; the interpretation rule is explicit: <i>any disagreement among "
        "defensible interval constructions is treated as method sensitivity, not resolved by "
        "choosing the favorable method.</i> Clause (b) survives everywhere (minimum familywise "
        "lower bound 0.462); P5-1a flips under the Jeffreys construction only.</p>"
    ),
    rel=["claim-p5-1a", "claim-p5-3b", "rev-round-2", "concept-estimands"],
)
add(
    id="an-counts", type="analysis", status="post-adjudication",
    title="Count reconciliation",
    short="Every count noun defined and reconciled: 5,505 runs ≠ 4,916 replay contract ≠ 36,251 requests ≠ 30,530 ledger calls.",
    meta="Machine-readable definitions committed with the numbers",
    links=[{"label": "Record", "href": GHB + "/docs/analysis/submission/count-reconciliation.md"}],
    body=(
        tbl(
            ["Quantity", "Count", "Definition"],
            [
                ["Distinct run IDs", "5,540", "any event in the store"],
                ["Archived completed runs", "5,505", "runs with run.completed, all phases"],
                ["Confirmatory replay contract", "4,916", "320 P3/X1 + 20 baselines + 2,864 P4 + 1,712 P5"],
                ["Capsule total", "4,919", "4,916 confirmatory + 3 legacy diagnostics"],
                ["Round events", "54,276", "simultaneous move pairs"],
                ["Seat-round decisions", "108,552", "two per round event"],
                ["Provider-request events", "36,251", "all llm.requested, full store"],
                ["Phase 4–5 ledger calls", "30,530", "transactional budget ledger (13.1M in / 45.2k out tokens)"],
            ],
            numeric=(1,),
        )
        + "<p>The ~1.5 output-token average per call is expected: valid actions were ordinarily "
        "one-token completions even though max_tokens=16. The reconciliation exists because an "
        "early draft conflated two of these scopes — a Round 2 queue item.</p>"
    ),
    rel=["concept-architecture", "concept-estimands", "rev-round-2"],
)
add(
    id="an-v12-audits", type="analysis", status="post-adjudication",
    title="v12 independent audits — coincidence, strata, entropy, decoding",
    short="The 0.4122 bootstrap/human-reference match is a rounding coincidence; leaning gaps and the entropy decline verified.",
    meta="Independent recomputation, 3 seeds × 250,000 reps · exact event-store recomputation",
    links=[{"label": "Record", "href": GHB + "/docs/analysis/submission/v12/v12-audits.md"},
           {"label": "Phase 3 replay audit", "href": GHB + "/docs/analysis/submission/v12/phase3-replay-audit.md"}],
    body=(
        "<p>Four audits triggered by Round 10: the suspicious equality of a bootstrap lower bound "
        "with the human SD reference is independently reproduced as a rounding coincidence "
        "(stored 0.412198 vs published 0.4122, zero seed-to-seed range); the leaning-stratum "
        "table is recomputed exactly; the temperature-entropy decline survives on the identical "
        "13-unit lattice; and all 36,251 archived request payloads are inspected for decoding "
        "parameters (temperature and max_tokens explicit on every request; penalties inherited "
        "provider defaults). The companion Phase 3 replay audit extended the capsule to all 320 "
        "registered Phase 3/X1 runs plus 20 deterministic baselines — PASS, CLEAN.</p>"
    ),
    rel=["claim-p5-1b", "claim-leaning", "claim-entropy", "rev-round-10", "art-capsule"],
)
add(
    id="an-dead-predictions", type="analysis", status="final",
    title="Dead-predictions ledger — 12 refuted author predictions",
    short="The program's scoreboard against its own author, adjudicated entirely by sealed code.",
    meta="Ten refutations through Phase 4, two in Phase 5; non-detections listed separately",
    links=[{"label": "Final ledger", "href": GHB + "/docs/analysis/dead-predictions-final.md"}],
    body=(
        "<p>Twelve affirmative refutations, from the v1 TFT prediction (predicted &gt;50% "
        "cooperation; observed 0.02) through the Phase 3 shadow-of-the-future and RPS bands, the "
        "paraphrase-robustness flip (0.000 → 1.000), two sign reversals in Phase 4, and the two "
        "consequential Phase 5 failures: <b>P5-2</b> (predicted task-dominant; verdict "
        "persona-dominant) and <b>P5-3</b> (predicted zero of sixteen personas pass; 16/16 "
        "passed). Those two selected the sealed Branch 2 discussion and inverted the reading of "
        "Phases 3–4: corner behavior characterizes the bare configuration, not the model’s "
        "capability envelope. The post-adjudication p13 downgrade is an inferential correction "
        "and deliberately not counted here.</p>"
    ),
    rel=["phase-5", "claim-p13", "concept-discussion", "concept-architecture"],
)

# ---------------------------------------------------------------------------
# Artifacts.
# ---------------------------------------------------------------------------

add(
    id="art-paper", type="artifact", status="final",
    title="Canonical paper PDF + arXiv package",
    short="19 pages, 5 figures; SHA-256-pinned; independently recompiled and byte-compared page-by-page in CI.",
    meta="PDF sha256 c5f15319…c98f8 · source zip 0b75e835…df0b1 · markdown b6c8a95d…0dc4",
    links=[{"label": "Paper PDF", "href": "paper.pdf"},
           {"label": "arXiv source zip", "href": "arxiv-source.zip"},
           {"label": "Manuscript (Markdown)", "href": GHB + "/docs/paper/paper.md"},
           {"label": "Submission metadata", "href": GHB + "/docs/paper/arxiv-metadata.txt"}],
    body=(
        "<p>The release workflow verifies all three pinned hashes, recompiles the arXiv source in "
        "a clean directory with PDFLaTeX, byte-compares all 19 rendered pages and extracted text "
        "against the canonical PDF, lints references and the sealed boundary, replays the capsule, "
        "and stamps the checksum with OpenTimestamps. The upload package contains exactly "
        "<code>main.tex</code> and five vector figures. Submission fields (title, abstract, "
        "cs.CL primary with cs.CY cross-list) are frozen in <code>arxiv-metadata.txt</code>.</p>"
    ),
    rel=["ver-final", "concept-architecture"],
)
add(
    id="art-capsule", type="artifact", status="final",
    title="Zero-call replay capsule",
    short="One command verifies 4,919 archived runs with no credentials and no live model calls.",
    meta="bash capsule/verify.sh · transactional (checkout restored) · zero-credential guard",
    links=[{"label": "Capsule", "href": GHT + "/capsule"},
           {"label": "Capsule README", "href": GHB + "/capsule-README.md"}],
    body=(
        "<p>The capsule stages the archived engine and budget databases, unsets every provider "
        "credential, replays Phase 3 prompts/actions (5,830/5,830 calls byte-verified), replays "
        "Phases 4–5 byte-exact against a local engine (2,864 + 1,712 runs; 10,428 Phase 5 calls "
        "verified), and independently recomputes the 20 deterministic baselines. Expected "
        "output:</p>"
        '<div class="terminal"><pre>CAPSULE VERIFICATION PASS — 4,919 archived Phase 3-5 runs verified\n'
        "(4,916 confirmatory + 3 legacy diagnostics)</pre></div>"
        "<p>The disclosed boundary: byte-exact replay proves reproducibility from the released, "
        "checksummed, externally timestamped archive — it is not provider attestation of what the "
        "API returned before sealing.</p>"
    ),
    rel=["concept-architecture", "an-counts"],
)
add(
    id="art-provenance", type="artifact", status="final",
    title="Checksums, timestamps, and seals",
    short="SHA-256 manifests, OpenTimestamps Bitcoin anchors (blocks 959483–960086), annotated tags and releases.",
    meta="11 OTS proofs across phase seals, close-outs, and the paper checksum",
    links=[{"label": "Phase 5 seal record", "href": GHB + "/docs/phase5/seal-record.md"},
           {"label": "Phase 4 seal record", "href": GHB + "/docs/phase4/seal-record.md"},
           {"label": "Releases", "href": GH + "/releases"}],
    body=(
        "<p>Every registry seal and close-out is hash-manifested and externally anchored: tags "
        "<code>phase4-v3-seal</code>, <code>phase4-final</code>, <code>phase5-v4-seal</code>, "
        "<code>phase5-final</code>, and <code>paper-text-freeze-v10</code>, each with a GitHub "
        "release timestamp and OpenTimestamps proofs upgraded to complete Bitcoin attestations. "
        "The registered language is deliberate: records are <i>externally anchored</i>, not "
        "“cryptographically immutable,” and no GPG signature exists (a disclosed plan deviation). "
        "Repository made public 2026-07-29T14:03Z with all hashes byte-identical across the "
        "flip.</p>"
    ),
    rel=["concept-architecture", "ver-v10", "phase-4", "phase-5"],
)

# ---------------------------------------------------------------------------
# Review rounds. (There is no round 13; the numbering in the archive jumps.)
# ---------------------------------------------------------------------------

REVIEWS = [
    ("rev-round-1", "Round 1 — multi-review synthesis",
     "Multiple AI reviewers (ChatGPT, Gemini, Grok R1)", "v1 → v2", "docs/reviews/round-1-review-summary.md",
     "Five majors: the P5-3 existence claim fired on any of 16 personas with no familywise "
     "control; the human comparator was not protocol-matched (“δ-matched” and N-fold language "
     "retired); human microstructure was unproven; the broad realism-vs-effect thesis was already "
     "occupied by concurrent work; and the draft was three papers in one. Disposition: the "
     "contribution narrowed to a fixed-panel strategic-interaction example with auditability as a "
     "credibility layer, not the sole novelty.",
     ["claim-p13", "ver-v2", "ref-li-ji-2026", "ref-dalbo-2011"]),
    ("rev-round-2", "Round 2 — adversarial methods and framing review",
     "Adversarial methods reviewer + two editorial reviews · 2026-07-29", "v2 → v3", "docs/reviews/round-2-methods-review.md",
     "Seven numbered defects, including seat-level intervals nested within episodes "
     "(anti-conservative under positive dependence), the Δ = μ₁ − μ₀ identity correction, and "
     "estimation noise inside the raw between-persona variance. Specified the five-item zero-call "
     "analysis queue (episode-level sensitivity, high-precision family audit, variance "
     "correction, count reconciliation; DF microdata deferred) that became the submission "
     "analyses. The enduring lesson entered the paper as its boundary quote. This reviewer's "
     "role later expanded to specifying analyses — disclosed in the attribution section.",
     ["an-episode-cluster", "an-variance", "an-counts", "an-p13-family", "ver-v3"]),
    ("rev-round-3", "Round 3 — independent anonymous-clone verification",
     "Independent reviewer, blobless anonymous clone · 2026-07-29", "v4 → v5", "docs/reviews/round-3-independent-verification.md",
     "Re-verified every headline number from the archived JSONs, then found what mattered most: "
     "an omitted computed variant (the percentile-bootstrap familywise p = 0.043455 — the only "
     "construction below 0.05 — absent from the prose) and the absence of any seal-before-compute "
     "record for the post-adjudication sensitivities. Disposition: all three constructions "
     "reported symmetrically, exact-episode designated primary, p13 capped at replication-target, "
     "reviewer-role expansion disclosed, v2/v3 drafts committed to history.",
     ["an-p13-family", "claim-p13", "ver-v5"]),
    ("rev-round-4", "Round 4 — independent reproduction and final editorial review",
     "Independent reviewer, ran the capsule end-to-end · 2026-07-29", "v5 → v6", "docs/reviews/round-4-independent-review.md",
     "Reproduced the full replay on an outside machine with zero credentials (4,576/4,576 "
     "byte-exact at that date) and cross-checked the aggregate contrasts. Eight editorial "
     "requests, including replacing “weak observed response” with “small, imprecisely estimated "
     "point differences” (the intervals reach ≈+0.33) and restoring Ashokkumar et al. as strong "
     "contrary evidence. Verdict: ready for full scientific review.",
     ["art-capsule", "ref-ashokkumar-2026", "ver-v6", "claim-response"]),
    ("rev-round-5", "Round 5 — Explore Science review of v6",
     "Explore Science (external) · 2026-07-29 · 92/100, Platinum", "v6 → v7", "docs/reviews/round-5-explore-science-review.md",
     "Zero major, thirteen minor issues, 42 merits. The consequential ones: the dynamic "
     "interiority filtering inside permutations was ambiguous (B1 — verified, plus a reporting "
     "omission corrected); no format-matched dummy control exists for the persona-prefix contrast "
     "(B2 — construct confound conceded); and the exact episode-level family gate is severely "
     "underpowered at six episodes per arm (B3 — adopted, tested, and turned into the p=0.075 "
     "attainability result). Figure 5's misattribution (C1) was corrected. The full disposition "
     "matrix and validation record are archived beside it.",
     ["an-round5-audit", "fig-p13-audit", "ver-v7", "claim-p13"]),
    ("rev-round-6", "Round 6 — Claude repository review of v7",
     "Claude (repository review)", "v7 → v8", "docs/reviews/round-6-claude-v7-review.md",
     "Independently re-derived the attainability numbers, contributed eleven adopted "
     "recommendations — including retitling “incentive-response” to “treatment-response” — and "
     "produced the archive's most instructive reviewer error: initially concluding two Explore "
     "Science figure issues were fabricated because the wrong branch was inspected. The "
     "retraction created a permanent process rule: every review request pins repository, commit, "
     "PDF SHA-256, page count, and build run.",
     ["ver-v8", "claim-response"]),
    ("rev-round-7", "Round 7 — Claude review of v8",
     "Claude (independent, commit-pinned)", "v8 → v9", "docs/reviews/round-7-claude-v8-review.md",
     "Six adopted requests: separate the archived finite panel from latent-propensity inference; "
     "define “cheap” (evidentiary economy); clarify that exact-gate eligibility depends on the "
     "full episode-value composition, not the sample mean; attach Monte Carlo intervals and the "
     "add-one convention; reconcile the Phase 4–5 request/response/partial/ledger counts; use "
     "“five-phase” consistently.",
     ["ver-v9", "an-counts"]),
    ("rev-round-8", "Round 8 — Claude freeze review of v9",
     "Claude (mechanical freeze-integrity review) · 2026-07-30", "v9 → v10 freeze", "docs/reviews/round-8-claude-v9-freeze-review.md",
     "Word-diffed v8 against v9 and confirmed the delta matched the declared change set exactly — "
     "“no silent scientific drift.” Closed two citations, adopted three micro-fixes, and "
     "recommended freezing the scientific text at v10 with an externally timestamped tag. Also "
     "mechanically caught that the review artifact had been mislabeled v8.",
     ["ver-v10"]),
    ("rev-round-9", "Round 9 — Explore Science review of v10",
     "Explore Science (external) · 2026-07-30 · 97/100, Platinum", "v10 → v11 addendum", "docs/reviews/round-9-explore-science-v10-review.md",
     "Zero major, twenty minor. The scientifically load-bearing theme: boundary-policy "
     "uncertainty — the fixed-panel episode bootstrap resamples empirically unanimous cells as "
     "point masses, a conditional statement rather than a complete uncertainty statement. The "
     "response created the Dirichlet–Jeffreys latent-propensity sensitivity (85–96% plug-in vs "
     "63–71% posterior medians) as the first post-freeze addendum, and made every numerical "
     "anchor self-contained.",
     ["an-variance", "claim-composition", "ver-v11"]),
    ("rev-round-10", "Round 10 — Explore Science review of v11",
     "Explore Science (external) · 2026-07-30 · 96/100, Platinum", "v11 → v12", "docs/reviews/round-10-explore-science-v11-review.md",
     "Twelve minors. Top three: the bootstrap/human-reference coincidence (audited: rounding "
     "coincidence), the label-conflict mechanism (learned game-theoretic prior named as a "
     "competing explanation), and the leaning-strata support. v12 extended the capsule to all of "
     "Phase 3 (320 runs + 20 baselines), audited archived decoding parameters, and reordered the "
     "abstract to lead with the latent-propensity posterior. Response rule: every numerical "
     "concern is tested independently before prose changes.",
     ["an-v12-audits", "claim-label-swap", "ver-v12"]),
    ("rev-round-11", "Round 11 — Explore Science review of v12",
     "Explore Science (external) · 2026-07-31 · 96/100, Platinum", "v12 → v13", "docs/reviews/round-11-disposition-matrix.md",
     "Eight minors, all adopted or strengthened for v13: a global-multiplicity limitation "
     "(no study-wide alpha allocation across the registered predicates), provider-failure "
     "accounting in the main text, the P5-2 prompt-cluster bootstrap and Dirichlet–Jeffreys "
     "dependence sensitivities, interval-bearing Figure 3, and ρ=.75 identified explicitly as a "
     "preregistered heuristic.",
     ["an-v13-dependence", "claim-p5-2", "ver-v13"]),
    ("rev-round-12", "Round 12 — Claude deep review of v13",
     "Claude (deep review, commit-pinned)", "v13 → v14", "docs/reviews/round-12-claude-v13-review.md",
     "Three release blockers, all fixed for v14: a bibliography regression, capsule-manifest "
     "ordering, and a duplicated sentence in the PDF. (There is no Round 13 in the archive — the "
     "numbering jumps to 14.)",
     ["ver-v14"]),
    ("rev-round-14", "Round 14 — middle-path findings restoration and final precision pass",
     "Final Claude review · accepted into the final candidate", "v14 → final", "docs/reviews/round-14-middle-path-finalization.md",
     "Kept the paper narrow while restoring three findings with full caveats: the registered "
     "one-shot wording null (+0.0063, Holm p=1.00) beside the repeated-game wrapper shift; the "
     "P5-2 Bayesian aggregation demoted from “independent corroboration” via the prior sweep "
     "(0.138 → 0.205, α=1 crossing 0.20); and four citable Appendix A.2 secondary findings. Five "
     "precision corrections, including dropping a wrong-sided RPS interval and the D2 congruence "
     "clause (GPT-4.1's swap cell cannot separate word from payoff channels). Deliberately "
     "excluded: the post-hoc p13 trait-tension theory.",
     ["claim-d1-wording", "an-p52-prior", "claim-rps-role", "claim-crossvendor-label",
      "ver-final"]),
]

for rid, title, meta, arc, path, summary, rel in REVIEWS:
    add(
        id=rid, type="review", title=title,
        short=f"{arc} · {meta.split('·')[-1].strip() if '·' in meta else 'external adversarial review'}",
        meta=f"{meta} · manuscript arc: {arc}",
        links=[{"label": "Archived record", "href": f"{GHB}/{path}"}],
        body=f"<p>{summary}</p>",
        rel=rel,
    )

# ---------------------------------------------------------------------------
# Manuscript versions.
# ---------------------------------------------------------------------------

VERSIONS = [
    ("ver-v1", "v1 — the refuted prototype paper", "superseded",
     "“Empirical Deviations from Nash Equilibrium in Classic Game Theory Games” — 40 experiments, "
     "11 claims, all initially called supported. Mechanical re-adjudication revised the record to "
     "6 supported / 1 refuted / 4 inconclusive, and the postmortem documents four process errors. "
     "Frozen as the program's origin artifact.",
     "docs/v1/paper-v1.md", None, ["phase-1-2"]),
    ("ver-v2", "v2 — first corrected draft", "superseded",
     "“Passing Marginal Checks Can Be Cheap: Persona Mixtures and Weak Incentive Response…” — "
     "p13 demoted from confirmatory to suggestive (family p = 0.0525 ± 0.0050), δ-matched and "
     "fivefold comparator language retired, and a 17-row v1→v2 correction ledger appended. "
     "Produced by Round 1.",
     "docs/paper/history/draft-v2-passing-marginal-checks.md", None, ["rev-round-1"]),
    ("ver-v3", "v3 — the registered reanalysis queue", "superseded",
     "Adds “Coarse” to the title, retires the “Level-Matching Is Cheap” hook, and registers the "
     "A.7 queue of five zero-call reanalyses with precommitted reporting rules — the blueprint "
     "for the submission analyses. Carries both correction ledgers (v1→v2, v2→v3).",
     "docs/paper/history/draft-v3.md", None, ["rev-round-2"]),
    ("ver-v5", "v4–v5 — verification and readiness", "superseded",
     "v4 was verified by the Round 3 anonymous clone; v5 adopted its corrections (all three "
     "family constructions reported, registration language scoped to confirmatory claims, "
     "reviewer-role disclosure, drafts committed to history, five contributions cut to three) and "
     "was declared “ready for full scientific review” by Round 4.",
     "docs/paper/history/README.md", None, ["rev-round-3", "rev-round-4"]),
    ("ver-v6", "v6 — first Explore Science PDF", "superseded",
     "The first formatted review PDF (14 pages), scored 92/100 Platinum with 13 minor issues.",
     "docs/paper/synthetic-players-review-draft-v6.pdf", None, ["rev-round-5"]),
    ("ver-v7", "v7 — the Round 5 integration", "superseded",
     "Integrates all thirteen Explore Science issues: the five-stage architecture table, protocol "
     "glossary, X2 operational definition, corrected Figures 1 and 5, represented-treatment "
     "language, and the corrected p13 power statement. 19 pages, line-numbered.",
     "docs/paper/synthetic-players-review-draft-v7.pdf", None, ["rev-round-5", "rev-round-6"]),
    ("ver-v8", "v8 — treatment-response retitle", "superseded",
     "Eleven Round 6 recommendations, including the title change from “incentive-response” to "
     "“treatment-response” and the p≈0.075 attainability boundary added to Figure 5. First "
     "version with in-tree checksum and artifact manifest.",
     "docs/paper/synthetic-players-review-draft-v8.pdf", None, ["rev-round-6", "rev-round-7"]),
    ("ver-v9", "v9 — freeze candidate", "superseded",
     "The text-freeze candidate: archived-panel vs latent-propensity separation, “cheap” defined "
     "as evidentiary economy, count reconciliation integrated. Word-diffed against v8 in Round 8 "
     "with no silent drift; the PDF survives only as its recorded hash.",
     "docs/reviews/round-8-claude-v9-freeze-review.md", None, ["rev-round-7", "rev-round-8"]),
    ("ver-v10", "v10 — the scientific text freeze", "sealed",
     "The frozen scientific text (21 pages, tag paper-text-freeze-v10, OpenTimestamps-anchored). "
     "Venue-driven changes remain permitted; any scientific change requires a new version and "
     "explicit addendum — the rule v11 then exercised. Scored 97/100 in Round 9.",
     "docs/paper/synthetic-players-review-v10.pdf", None, ["rev-round-8", "rev-round-9", "art-provenance"]),
    ("ver-v11", "v11 — the post-freeze addendum", "superseded",
     "Adds the fixed-panel Dirichlet–Jeffreys latent-propensity sensitivity — the uncertainty "
     "view that turned “85–96% dominant” into “63–71% medians, prior-dependent dominance” — as an "
     "explicit, declared addendum to the frozen v10 (22 pages; margin line numbers removed).",
     "docs/paper/synthetic-players-review-v11.pdf", None, ["rev-round-9", "rev-round-10", "an-variance"]),
    ("ver-v12", "v12 — near-arXiv preprint", "superseded",
     "Extends the replay perimeter to all of Phase 3 (320 runs + 20 baselines), adds the "
     "independent bootstrap-coincidence audit, full leaning-strata table, matched-lattice entropy "
     "reanalysis, and decoding audit; the abstract leads with the latent-propensity posterior. "
     "18 pages.",
     "docs/paper/synthetic-players-preprint-v12.pdf", None, ["rev-round-10", "rev-round-11", "an-v12-audits"]),
    ("ver-v13", "v13 — dependence-aware candidate", "superseded",
     "Adds the global-multiplicity limitation, provider-failure accounting, P5-2 prompt-cluster "
     "bootstrap and Dirichlet–Jeffreys sensitivities, and interval-bearing Figure 3. 19 pages.",
     "docs/paper/synthetic-players-preprint-v13.pdf", None, ["rev-round-11", "rev-round-12", "an-v13-dependence"]),
    ("ver-v14", "v14 — arXiv candidate", "superseded",
     "Fixes the three Round 12 release blockers and incorporates the Round 14 middle-path "
     "restorations and precision corrections. 19 pages, clean preprint surface, five vector "
     "figures.",
     "docs/paper/synthetic-players-preprint-v14.pdf", None, ["rev-round-12", "rev-round-14"]),
    ("ver-final", "Final — canonical release", "final",
     "The canonical 19-page, five-figure release: PDF, byte-identical Markdown, and minimal "
     "PDFLaTeX arXiv package, all SHA-256-pinned, independently recompiled and page-image-"
     "compared in CI, OpenTimestamps-anchored, and published with the project site on "
     "2026-08-01 (PR #13).",
     "docs/paper/synthetic-players.pdf", None, ["rev-round-14", "art-paper", "art-provenance"]),
]

for vid, title, status, summary, path, _unused, rel in VERSIONS:
    add(
        id=vid, type="version", title=title, status=status,
        short=summary.split(". ")[0] + ".",
        meta=f"Record: <code>{path}</code>",
        links=[{"label": "Archived file", "href": f"{GHB}/{path}"}],
        body=f"<p>{summary}</p>",
        rel=rel,
    )

add(
    id="an-v13-dependence", type="analysis", status="post-adjudication",
    title="P5-2 dependence audit (v13)",
    short="Prompt-cluster bootstrap [0.071, 0.189] and fixed-panel Dirichlet–Jeffreys [0.152, 0.195] around the 0.128 point.",
    meta="B = 200,000 · 40 clusters, 5 strata · seeds 20260731–32",
    links=[{"label": "Record", "href": GHB + "/docs/analysis/submission/v13/p52-dependence-audit.md"}],
    body=(
        "<p>The dependence-aware companion to the P5-2 story: a stratified bootstrap over the "
        "forty persona × conflict-cell clusters preserves the empirical point (0.128) with "
        "interval [0.071, 0.189], while the fixed-panel Jeffreys aggregation gives median 0.172, "
        "[0.152, 0.195]. Both sit below the frozen 0.20 boundary — but the subsequent prior sweep "
        "showed that Bayesian proximity to the boundary moves with α, which is why the bootstrap "
        "is the principal sensitivity.</p>"
    ),
    rel=["claim-p5-2", "an-p52-prior", "rev-round-11"],
)

# ===========================================================================
# Hub pages.
# ===========================================================================

def _claim_rows(idx, h, ids):
    rows = []
    for cid in ids:
        it = idx[cid]
        rows.append([
            f'<a href="{h["page_href"](cid)}">{h["esc"](it["title"])}</a>',
            h["status_chip"](it.get("status")),
            h["esc"](it.get("short", "")),
        ])
    return rows


CLAIM_ORDER = [
    "claim-p3-a3", "claim-composition", "claim-response", "claim-p5-1a", "claim-p5-1b",
    "claim-p5-2", "claim-p13", "claim-p5-3b", "claim-s2-switch", "claim-d1-wording",
    "claim-label-swap", "claim-leaning", "claim-adversary", "claim-rps-role",
    "claim-crossvendor-label", "claim-entropy", "claim-drift",
]


def build_index(idx, back, h):
    figs = "".join(
        f'<figure><a href="{h["page_href"](fid)}"><img src="assets/{fid[4:]}.png" '
        f'alt="{h["esc"](idx[fid]["title"])}" loading="lazy"></a>'
        f'<figcaption><a href="{h["page_href"](fid)}">{h["esc"](idx[fid]["title"])}</a></figcaption></figure>'
        for fid in ["fig-between-prompt-share", "fig-prompt-indexed-delta",
                    "fig-condition-means", "fig-representation-effects", "fig-p13-audit"]
    )
    claims_tbl = tbl(["Claim", "Status", "One-line result"],
                     _claim_rows(idx, h, CLAIM_ORDER))
    return f"""
<section class="lede">
<p class="kicker">Open computational behavioral science · final release · August 2026</p>
<h1>Passing Coarse Marginal Checks Can Be Cheap</h1>
<p class="authors">Persona mixtures and imprecise treatment-response estimates in an LLM persona panel · <b>Yohei Nakajima</b>, Untapped Capital · <a href="paper.pdf">PDF</a> · <a href="arxiv-source.zip">arXiv source</a> · <a href="https://github.com/yoheinakajima/synthetic-players">repository</a> · <a href="reviews.html">review record</a></p>
<div class="mode-toggle" role="group" aria-label="Reading mode">
<button id="mode-tech" type="button" class="on" aria-pressed="true">Technical</button>
<button id="mode-plain" type="button" aria-pressed="false">Plain English</button>
</div>
<p class="mode-note">Prefer a walkthrough? <a href="qa.html">Read the whole study as a Q&amp;A</a> — including the findings that didn't make the paper.</p>
<div class="lang-tech">
<p class="abstract">LLMs are increasingly used as synthetic research participants and validated by whether their marginal responses resemble human data. A fixed panel of sixteen lightweight persona-conditioned GPT-4.1 configurations met preregistered broad-reference condition-mean criteria in three of four repeated-game cells — while the treatment-response object those checks might be taken to validate stayed loosely bounded, and much of the apparent behavioral diversity was between-prompt composition of empirically corner-concentrated policies. The registered marginal criteria could be passed without precisely estimating the treatment response. One fixed model-prompt panel; no human-substitutability claim.</p>
<div class="statrow">
<div class="stat"><b>3 / 4</b><span>repeated-game cells inside the preregistered band; sole miss 0.011 below</span></div>
<div class="stat"><b>47–71%</b><span>prior-sensitive median between-prompt share (α=1 → Jeffreys); plug-in 85–96%</span></div>
<div class="stat"><b>+0.083 / +0.078</b><span>treatment contrasts, 95% intervals ≈ [−0.18, +0.33]</span></div>
<div class="stat"><b>0/40 → 37/40</b><span>cooperation after one wording-and-position operation</span></div>
<div class="stat"><b>4,919</b><span>archived runs replayed by the public capsule — 4,916 confirmatory + 3 diagnostics</span></div>
</div>
</div>
<div class="lang-plain">
<p class="abstract">Researchers have started using AI models as stand-ins for human study participants — it's fast and nearly free. The usual quality check asks: does the AI's behavior <i>look</i> statistically human? This project built sixteen simple AI “personas” (one sentence each — “You are Harper, a 61-year-old landscape gardener… competitive, patient, and risk-averse”), had them play cooperation games thousands of times, and found something uncomfortable: <b>the panel passed the standard looks-human checks while the thing experiments actually exist to measure — how behavior shifts when you change the incentives — stayed basically unmeasured.</b> Looking human is cheap. Reacting like humans is a different, harder property, and the popular checks don't test it.</p>
<div class="statrow">
<div class="stat"><b>3 / 4</b><span>of the game setups passed the “looks human” test — by the usual standard, the panel worked</span></div>
<div class="stat"><b>≈ 0</b><span>clear reaction when the incentive to cooperate got 9× stronger — the change was tiny and uncertain</span></div>
<div class="stat"><b>1 sentence</b><span>rewording one line flipped the base model from 0% to 92% cooperation</span></div>
<div class="stat"><b>1 word</b><span>a label reading “Defect” beat the actual money on the table</span></div>
<div class="stat"><b>4,919</b><span>archived game runs anyone can re-verify on a laptop — no AI account needed</span></div>
</div>
</div>
</section>

<section class="sec">
<div class="lang-tech">
<h2>The result in four sentences</h2>
<p>Coarse marginal checks were <a href="claim-p3-a3.html">passed</a> while the <a href="claim-response.html">registered treatment response</a> remained imprecisely estimated — the slack in the checks is exactly where the response lives (<a href="concept-estimands.html">Proposition A</a>). The panel's apparent diversity is largely <a href="claim-composition.html">between-prompt composition</a> of corner-concentrated policies, and whether that share is “dominant” is prior-dependent. Representation, not incentives, controlled the corners: <a href="claim-s2-switch.html">one sentence operation</a> moved bare cooperation from 0/40 to 37/40 while ordinary wording changes did <a href="claim-d1-wording.html">nothing</a>, and a displayed label <a href="claim-label-swap.html">overrode payoff dominance</a>. The favored persona-level result, p13, was <a href="claim-p13.html">demoted to a replication target</a> after external review exposed the missing family control — and the P5-2 posterior's proximity to its 0.205 boundary reading is likewise prior-dependent.</p>
</div>
<div class="lang-plain">
<h2>Why this is interesting</h2>
<p><b>Cheap AI “participants” are already informing real decisions</b> — pretesting surveys, products, and policy messages. This project shows the standard quality bar can be cleared by accident: a panel can look statistically human while nobody has actually checked whether it <i>reacts</i> to changed conditions the way the test seems to promise. It's like hiring an actor who nails the accent but ignores the script — convincing at a glance, wrong for the job.</p>
<p><b>The “diversity” was a trick of mixing.</b> Almost every persona was locked into a habit — always cooperate or always defect. Stir eight of one and eight of the other together and the <i>averages</i> come out human-shaped, even though no individual is weighing the decision. That's the “cheap pass” in the title: variety that comes from the recipe, not from anyone's judgment (<a href="claim-composition.html">the decomposition</a>).</p>
<p><b>Words beat money.</b> Rewriting one sentence about the game continuing took the base model from never cooperating to almost always (<a href="claim-s2-switch.html">0/40 → 37/40</a>), while a battery of ordinary wording tweaks did nothing at all. And when a label said “Defect” on the objectively better-paying choice, the model followed <a href="claim-label-swap.html">the word, not the money</a>. Behavior a sentence can rewrite isn't a stable synthetic person — which matters for safety, not just science.</p>
<p><b>The team caught its own best result being too good.</b> One persona — Harper, the 61-year-old landscape gardener — seemed to genuinely respond to incentives. Outside reviewers showed the test behind that headline had a statistical hole, so <a href="claim-p13.html">the paper demotes its own favorite finding</a> to “needs a proper replication.” The mistakes, the refuted predictions (twelve of them), and every correction are part of the published record — you can watch the science self-correct in the open.</p>
</div>
</section>

<section class="sec">
<div class="lang-tech">
<h2>Claims ledger</h2>
<p class="sec-note">Every registered predicate and citable secondary, with its current evidentiary status. Each row is a page; each page links its evidence, analyses, figures, and review history. Full tier definitions on the <a href="claims.html">claims page</a>.</p>
{claims_tbl}
</div>
<div class="lang-plain">
<h2>The findings, in plain terms</h2>
<ul>
<li><b>Passed the resemblance test:</b> in 3 of 4 game setups, group averages landed inside the pre-registered “human range” — <a href="claim-p3-a3.html">the checks the field actually uses</a>.</li>
<li><b>Barely reacted to incentives:</b> making future rounds 9× more likely moved cooperation by about 8 points out of 100, with uncertainty so wide the true effect could plausibly be negative — <a href="claim-response.html">the imprecise response</a>.</li>
<li><b>Habits, not decisions:</b> ten of sixteen personas never varied their choice in any setup; the human-looking spread came from mixing stubborn habits — <a href="claim-composition.html">the mixture result</a>.</li>
<li><b>Wording is the control knob:</b> one rewritten sentence flipped behavior end to end; a one-word label outweighed the payoffs — <a href="claim-s2-switch.html">the switch</a> and <a href="claim-label-swap.html">the label conflict</a>.</li>
<li><b>The star witness got demoted:</b> the single persona that seemed incentive-sensitive rests on a test with no multiple-comparisons control; it's now officially a “<a href="claim-p13.html">replication target</a>,” not a finding.</li>
</ul>
<p class="sec-note">Want the full ledger with statistical detail? Flip to Technical, or open the <a href="claims.html">claims page</a>.</p>
</div>
</section>

<section class="sec">
<h2>Figures</h2>
<p class="sec-note lang-tech">The paper's five figures, each with sources and provenance.</p>
<p class="sec-note lang-plain">The paper's five figures — click any of them for a guided explanation of what you're seeing.</p>
<div class="figrow">{figs}</div>
</section>

<section class="sec">
<div class="lang-tech">
<h2>The program</h2>
<p class="sec-note">Five phases, sealed registries, mechanical adjudication, 12 refuted author predictions, 14 review rounds, 15 manuscript versions. Full <a href="timeline.html">timeline</a> · <a href="phases.html">phases</a> · <a href="reviews.html">reviews</a> · <a href="versions.html">versions</a>.</p>
{tbl(["Phase", "What it established", "Scale"], [
    [f'<a href="phase-1-2.html">Phases 1–2</a>', "prototype → mechanical re-adjudication after it exposed analyst discretion", "40 + 400 experiments"],
    [f'<a href="phase-3.html">Phase 3</a>', "bare GPT-4.1 sits at corners; one paraphrase flips 0.000 → 1.000", "320 runs, 5,820 calls"],
    [f'<a href="phase-4.html">Phase 4</a>', "the S2 switch, label/payoff conflict, corner-confounded δ-assays, sentinel catches endpoint drift", "2,864 runs, 20,102 calls"],
    [f'<a href="phase-5.html">Phase 5</a>', "the sixteen-persona panel; both author predictions with teeth failed", "1,712 runs, 10,428 calls"],
    [f'<a href="phase-6.html">Phase 6</a>', "preregistered replication — power-planned, not yet run", "prospective"],
])}
</div>
<div class="lang-plain">
<h2>How the study was run</h2>
<p class="sec-note">Five stages over five weeks, with predictions locked in — publicly and tamper-evidently — <i>before</i> the data existed, and a computer (not the author) deciding pass or fail.</p>
{tbl(["Stage", "Plain-language version"], [
    [f'<a href="phase-1-2.html">Phases 1–2</a>', "built the lab — and learned that human judgment sneaks into scoring, so scoring was handed to sealed, automatic rules"],
    [f'<a href="phase-3.html">Phase 3</a>', "the plain AI (no persona) turned out to be an extreme case: it essentially never cooperates — until a rewording flips it completely"],
    [f'<a href="phase-4.html">Phase 4</a>', "hunted down which words matter: found the one controlling sentence, showed labels can beat money, and a tripwire caught the AI vendor's model changing mid-study"],
    [f'<a href="phase-5.html">Phase 5</a>', "gave the AI sixteen one-sentence personalities and ran the full experiment — the author's two boldest predictions both failed, and that failure is the finding"],
    [f'<a href="phase-6.html">Phase 6</a>', "the honest follow-up: a bigger, properly powered redo, designed before any new data is collected"],
])}
</div>
</section>

<section class="sec">
<div class="lang-tech">
<h2>How this differs from prior work</h2>
<p class="sec-note">The broad “realism ≠ effect accuracy” thesis is occupied; the contribution here is narrower and mechanism-level. Full map with per-paper differentiation on the <a href="related-work.html">related-work page</a>.</p>
<p>Li &amp; Ji establish the realism/effect divergence at survey scale; this project identifies one concrete strategic-interaction pattern behind cheap passes — <a href="ref-li-ji-2026.html">how we differ</a>. Persson et al. formalize LLM causal surrogacy; this is a registered design-side example of what coarse checks leave unidentified — <a href="ref-persson-2026.html">details</a>. Lin et al.'s latent-user drift can coexist with the composition pattern measured here — <a href="ref-lin-2026.html">details</a>. Pal et al. run nearly the same manipulations without the persona panel or audit architecture — <a href="ref-pal-2026.html">details</a>. Ashokkumar et al. is the strong positive counterexample, on a different estimand — <a href="ref-ashokkumar-2026.html">details</a>.</p>
</div>
<div class="lang-plain">
<h2>Hasn't someone shown this already?</h2>
<p>Partly — and the paper says so. Large studies have shown AI simulations can look right while getting cause-and-effect wrong, and one impressive study shows AI can <i>forecast</i> experiment outcomes surprisingly well. What's new here is the mechanism, caught in the act: a specific, common recipe (one-sentence personas) that passes the checks by mixing stuck habits — plus receipts. Predictions were locked before data, every AI call was archived, and the whole record replays on your machine. The <a href="related-work.html">related-work page</a> compares this paper to each neighboring study in a sentence or two.</p>
</div>
</section>

<section class="sec">
<h2 class="lang-tech">Reproduce the confirmatory record</h2>
<h2 class="lang-plain">Don't take our word for it</h2>
<div class="two-col">
<div>
<div class="lang-tech"><p>One command replays every confirmatory run — <b>4,916 confirmatory</b> plus three legacy diagnostics — byte-exact from the archived, checksummed, externally timestamped databases. No credentials, no live model calls. The <a href="art-capsule.html">capsule page</a> documents what replay does and does not prove.</p>
<p class="smallprint">Expected: CAPSULE VERIFICATION PASS — 4,919 archived Phase 3-5 runs verified.</p></div>
<div class="lang-plain"><p>Every archived game — all 4,919 — re-checks byte-for-byte from the published record with the three lines on the right. No AI accounts or API keys, because nothing is re-generated: your machine verifies the archive against itself, including every prompt, every response, and every scored outcome. <a href="art-capsule.html">What that does and doesn't prove</a>.</p></div>
</div>
<div class="terminal"><button id="copy-command" type="button">Copy</button><pre><code id="verify-command">git clone https://github.com/yoheinakajima/synthetic-players
cd synthetic-players/capsule
bash verify.sh</code></pre></div>
</div>
</section>

<section class="sec">
<h2>Materials</h2>
{tbl(["Artifact", "What it is"], [
    ['<a href="art-paper.html">Paper PDF + arXiv package</a>', "canonical 19-page PDF, byte-identical Markdown, minimal PDFLaTeX zip — all hash-pinned"],
    ['<a href="art-capsule.html">Replay capsule</a>', "one-command zero-credential verification of 4,919 archived runs"],
    ['<a href="art-provenance.html">Checksums, timestamps, seals</a>', "SHA-256 manifests, OpenTimestamps Bitcoin anchors, sealed tags and releases"],
    ['<a href="concept-personas.html">Persona table</a>', "all sixteen sealed sentences with construction rule and hashes"],
    ['<a href="an-dead-predictions.html">Dead-predictions ledger</a>', "12 refuted author predictions, adjudicated by sealed code"],
    ['<a href="https://github.com/yoheinakajima/synthetic-players/tree/main/docs/reviews">Review archive</a>', "every external critique, disposition matrix, and role disclosure"],
])}
</section>
"""


def build_claims(idx, back, h):
    tiers = tbl(["Tier", "Meaning"], [
        ["Registered · verdict pass/fail", "frozen mechanical verdicts, adjudicated by sealed code before interpretation; historical labels never rewritten"],
        ["Method-/prior-sensitive", "classification changes across defensible interval constructions or symmetric priors; continuous estimates primary"],
        ["Replication target", "neither prospectively confirmed nor decisively disconfirmed; next test must be prospectively powered"],
        ["Descriptive", "reported without inferential weight (cross-vendor tier, non-registered comparisons)"],
        ["Post-adjudication", "computed after the seal in response to review; cannot create prospective confirmation"],
        ["Procedural", "monitoring and process records, not behavioral findings"],
    ])
    return f"""
<article class="item">
<p class="kicker">Ledger</p>
<h1>Claims and their evidentiary tiers</h1>
<p class="dek">Every registered predicate, its frozen verdict, and its current scientific status — kept deliberately distinct.</p>
<div class="body">
<p>The program's rule: historical mechanical verdicts stay visible verbatim; later analyses are additive and explicitly labeled. Twelve registered author predictions were refuted and published (<a href="an-dead-predictions.html">the dead-predictions ledger</a>); the p13 demotion is an inferential correction, not a refutation, and is deliberately not counted among them.</p>
<h2>Tier vocabulary</h2>
{tiers}
<h2>All claims</h2>
{tbl(["Claim", "Status", "One-line result"], _claim_rows(idx, h, CLAIM_ORDER))}
<h2>Dependency spine</h2>
<p>The paper's argument rests on four load-bearing links: the <a href="claim-p3-a3.html">marginal checks</a> license nothing about <a href="claim-response.html">response</a> beyond band arithmetic (Proposition A); the <a href="claim-composition.html">composition claim</a> depends on which uncertainty view conditions on boundary concentration; the <a href="claim-p13.html">p13 story</a> rests on the family audits and the attainability floor; and the <a href="claim-p5-2.html">P5-2 classification</a> is carried by the word/payoff-confounded swap cell. The archived <a href="https://github.com/yoheinakajima/synthetic-players/blob/main/docs/analysis/claim-dependencies.md">claim-dependency audit</a> maps every quotation of these results to its correction rule.</p>
</div>
</article>
"""


def build_phases(idx, back, h):
    rows = []
    for pid in ["phase-1-2", "phase-3", "phase-4", "phase-5", "phase-6"]:
        it = idx[pid]
        rows.append([
            f'<a href="{h["page_href"](pid)}">{h["esc"](it["title"])}</a>',
            h["status_chip"](it.get("status")),
            h["esc"](it.get("short", "")),
        ])
    return f"""
<article class="item">
<p class="kicker">Program</p>
<h1>The five-phase experimental program</h1>
<p class="dek">Sequential, sealed, and mechanically adjudicated — with each phase's question set by the previous phase's failure.</p>
<div class="body">
{tbl(["Phase", "Status", "Question and answer"], rows)}
<h2>The through-line</h2>
<p>Phase 1's prototype exposed analyst discretion → Phase 2 mechanized adjudication. Phase 3 found the bare subject at corners everywhere, with a paraphrase flip (X1) showing wording dominated the incentive manipulation → Phase 4 mapped representation: localized the flip to one sentence (X2/S2), decoupled labels from payoffs (D2), found δ-assays corner-confounded (E), and caught live endpoint drift with behavioral sentinels. Phase 5 asked whether cheap persona conditioning produces an interior, incentive-sensitive population — and answered with the composition result the paper reports. Phase 6 is the preregistered replication the scope seal deferred until after publication.</p>
<h2>Scale and integrity</h2>
{tbl(["Quantity", "Value"], [
    ["Archived completed runs (all phases)", "5,505"],
    ["Confirmatory replay contract", "4,916 runs (+3 legacy diagnostics = 4,919)"],
    ["Round events / seat decisions", "54,276 / 108,552"],
    ["Phase 4–5 ledger", "30,530 calls · 13,141,675 input tokens · 45,247 output tokens"],
    ["Invalid trials in Phases 4–5", "0 (24 provider-failure partials disclosed individually)"],
    ["Registered author predictions refuted", "12"],
    ["Process-failure instances publicly ledgered", "22"],
])}
</div>
</article>
"""


TIMELINE = [
    ("Jul 2026", "Phases 1–2", "v1 prototype (40 experiments, 11 claims) → mechanical re-adjudication revises the record; postmortem published", "phase-1-2"),
    ("Jul 24", "Phase 3 complete", "320 bare-GPT-4.1 runs: corners everywhere; X1 paraphrase flips the corner same-day", "phase-3"),
    ("Jul 24", "Phase 4 sealed + dispatched", "registry v3 (250 arms) sealed 18:58 UTC, tag phase4-v3-seal anchored 19:04", "phase-4"),
    ("Jul 25–27", "Phase 4 executes", "sentinel alert 5 catches Gemini endpoint drift at a block boundary; freezes + memos; zero contaminated confirmatory spend", "claim-drift"),
    ("Jul 28", "Phase 4 closes; Phase 5 sealed + run + closed", "phase4-final · registry v4 + personas + discussion branches sealed pre-dispatch · 1,712 runs · Branch 2 selected · phase5-final", "phase-5"),
    ("Jul 29", "Repository public + Round 1–5 reviews", "public at 14:03 UTC, hashes byte-identical; first external reviews land; zero-call reanalysis queue specified and executed", "rev-round-1"),
    ("Jul 29", "p13 demoted", "R2 family audit: registered rule had a 12.9% familywise false-fire rate; slope downgraded to suggestive", "an-p13-family"),
    ("Jul 30", "v10 text freeze", "scientific text frozen, tagged, OpenTimestamps-anchored (Round 8); Explore Science scores it 97/100 (Round 9)", "ver-v10"),
    ("Jul 30", "v11 addendum", "Dirichlet–Jeffreys latent-propensity sensitivity: composition dominance becomes prior-dependent", "ver-v11"),
    ("Jul 30–31", "v12–v14 candidates", "capsule extended to Phase 3 (4,919 total); dependence audits; three release blockers fixed", "ver-v12"),
    ("Jul 31", "Round 14 final pass", "middle-path restorations: wording null, P5-2 prior sweep, Appendix A.2 findings; precision corrections", "rev-round-14"),
    ("Aug 1", "Final release", "PR #13 merges: canonical PDF + arXiv package, hash-pinned, independently recompiled, capsule green; project site published", "ver-final"),
]


def build_timeline(idx, back, h):
    lis = "".join(
        f'<li><span class="tdate">{h["esc"](d)}</span><span><b><a href="{h["page_href"](link)}">{h["esc"](t)}</a></b><br>'
        f'<span class="tnote">{h["esc"](note)}</span></span></li>'
        for d, t, note, link in TIMELINE
    )
    return f"""
<article class="item">
<p class="kicker">Chronology</p>
<h1>Program timeline</h1>
<p class="dek">From prototype to sealed release in five weeks — every step externally anchored.</p>
<div class="body">
<ul class="timeline">{lis}</ul>
<p class="smallprint">Chronology anchors: GitHub release timestamps, annotated tags, and OpenTimestamps proofs upgraded to Bitcoin attestations (blocks 959483, 959985, 960020, 960086). Dates are 2026, UTC.</p>
</div>
</article>
"""


def build_reviews(idx, back, h):
    rows = []
    for rid, title, meta, arc, path, _s, _r in REVIEWS:
        it = idx[rid]
        rows.append([
            f'<a href="{h["page_href"](rid)}">{h["esc"](title.split("—")[0].strip())}</a>',
            h["esc"](meta),
            h["esc"](arc),
        ])
    return f"""
<article class="item">
<p class="kicker">Adversarial record</p>
<h1>Fourteen review rounds</h1>
<p class="dek">External critique changed this paper's central claim — and the full trail is preserved: reviews, disposition matrices, reviewer errors, and role disclosures.</p>
<div class="body">
<p>The correction record is part of the result. Reviews diagnosed the missing family control that demoted p13, the seat-vs-episode dependence defect, the boundary-uncertainty gap that produced the latent-propensity view, and the prior sensitivity that demoted P5-2's Bayesian corroboration. Reviewer roles are disclosed — including one reviewer's expansion from critique to analysis specification, and one reviewer's retracted fabrication accusation that became a permanent artifact-identity rule. Preservation rule: sealed research files are never edited in response to review; corrections are additive.</p>
{tbl(["Round", "Reviewer · date · score", "Manuscript arc"], rows)}
<p class="smallprint">There is no Round 13 in the archive — the numbering jumps from 12 to 14. Author-side response plans are archived separately from external review text.</p>
</div>
</article>
"""


def build_related(idx, back, h):
    def refrow(ids):
        rows = []
        for rid in ids:
            it = idx[rid]
            link = it["links"][0]["href"] if it.get("links") else "#"
            rows.append([
                f'<a href="{h["page_href"](rid)}">{h["esc"](it["title"])}</a>',
                h["esc"](it.get("short", "")),
                f'<a href="{h["esc"](link)}">source ↗</a>',
            ])
        return rows
    return f"""
<article class="item">
<p class="kicker">Positioning</p>
<h1>Related work — occupied territory and precise differentiation</h1>
<p class="dek">What is already established, what collides, and the narrow triangle this paper defends.</p>
<div class="body">
<h2>The defensible novelty triangle</h2>
<p><b>1.</b> A registered strategic-interaction example where a fixed persona panel passes coarse marginal checks while continuation-probability estimates stay small and imprecise. <b>2.</b> The mechanism-level pattern: dispersion carried largely by between-prompt composition of empirically corner-concentrated policies. <b>3.</b> The credibility layer: registration, provenance, replay, mechanical adjudication, and public post-adjudication correction. Explicitly <i>not</i> claimed: first demonstration of realism/effect divergence, drift-free panels, human interiority, trait causality, or a p13 capability finding.</p>
<h2>Closest occupied territory</h2>
{tbl(["Work", "What it establishes", ""], refrow(["ref-li-ji-2026", "ref-ashokkumar-2026", "ref-persson-2026", "ref-lin-2026", "ref-xie-2026", "ref-harry-2026", "ref-xiao-2026"]))}
<h2>Direct strategic-behavior collisions</h2>
{tbl(["Work", "Collision", ""], refrow(["ref-akata-2025", "ref-pal-2026", "ref-georgousis-2026", "ref-mousavi-2026", "ref-mei-2024"]))}
<h2>Synthetic participants and personas</h2>
{tbl(["Work", "Relation", ""], refrow(["ref-bisbee-2024", "ref-boelaert-2025", "ref-anthis-2025", "ref-hullman-2026", "ref-park-2024", "ref-argyle-2023", "ref-horton-2023", "ref-batzner-2025", "ref-sclar-2024", "ref-shanahan-2023"]))}
<h2>Comparators and classical lineages</h2>
{tbl(["Work", "Use here", ""], refrow(["ref-dalbo-2011", "ref-lucas-1976", "ref-cronbach-1955", "ref-ich-e10", "ref-windrum-2007", "ref-stats-methods"]))}
<p class="smallprint">Sources: the paper's §2 and References, plus the archived <a href="https://github.com/yoheinakajima/synthetic-players/blob/main/docs/analysis/literature-map.md">literature map</a> and <a href="https://github.com/yoheinakajima/synthetic-players/blob/main/docs/analysis/novelty-relationships.md">novelty-relationships</a> documents (working research maps, not verdict-bearing).</p>
</div>
</article>
"""


def build_versions(idx, back, h):
    rows = []
    for vid, title, status, _s, path, _u, _r in VERSIONS:
        it = idx[vid]
        rows.append([
            f'<a href="{h["page_href"](vid)}">{h["esc"](title)}</a>',
            h["status_chip"](status),
            h["esc"](it.get("short", "")),
        ])
    return f"""
<article class="item">
<p class="kicker">Provenance</p>
<h1>Manuscript genealogy — v1 to the canonical release</h1>
<p class="dek">Fifteen versions, each prompted by a named review round; earlier drafts preserved byte-exact, never rewritten.</p>
<div class="body">
<p>The title itself records the corrections: <i>“Empirical Deviations from Nash Equilibrium…”</i> (v1) → <i>“Passing Marginal Checks Can Be Cheap… Weak Incentive Response”</i> (v2) → adding <i>“Coarse”</i> (v3) → <i>“Persona Mixtures and Imprecise Incentive-Response Estimates”</i> (v5–v7) → <i>“Treatment-Response”</i> (v8, final). The v10 scientific text freeze is externally timestamped; v11 is its first declared addendum.</p>
{tbl(["Version", "Status", "What changed"], rows)}
<p class="smallprint">Historical PDFs and hash manifests live in <a href="https://github.com/yoheinakajima/synthetic-players/tree/main/docs/paper">docs/paper/</a>; exact v2/v3 sources in <a href="https://github.com/yoheinakajima/synthetic-players/tree/main/docs/paper/history">docs/paper/history/</a>. v4/v5 exist as verified states of the working draft rather than separate files; the v9 PDF survives as its recorded hash in the Round 8 review.</p>
</div>
</article>
"""


def build_qa(idx, back, h):
    return """
<article class="item qa">
<p class="kicker">Conversational walkthrough</p>
<h1>The whole study, in plain Q&amp;A</h1>
<p class="dek">The questions people actually ask, in order — including what moved the AI, what didn't, the result that got demoted, and the findings that didn't make the paper.</p>
<div class="body">
<p class="checknote">Every number below is fact-checked against the archived record, and every answer links to the page that holds its evidence. Where popular retellings drift from the record (it happens fast), the linked pages are authoritative.</p>

<p class="part">Part 1 · The study</p>

<h2>What was the basic idea?</h2>
<p>Instead of recruiting people for a behavioral experiment, use an AI (GPT-4.1) as the participants. The project created <a href="concept-personas.html">sixteen fake people</a>, each defined by a single sentence — a name, age, job, and three personality traits (agreeable vs. competitive, patient vs. impulsive, risk-averse vs. risk-seeking), across two age bands. Same AI every time; the only thing that changed was which intro sentence it got (plus a no-sentence control). The question: does this cheap, common trick give you human-like study participants?</p>

<h2>What game did they play?</h2>
<p>Mainly the Prisoner's Dilemma. Two players each secretly pick “Cooperate” or “Defect.” Both cooperate: both do well. One defects on a cooperator: the defector does great, the cooperator gets burned. Both defect: both do poorly. (Earlier phases also used Rock-Paper-Scissors and framing games — see Part 2.)</p>

<h2>How were the versions different?</h2>
<p>The key manipulation was whether the game would keep going. In one version, players were told there's a <b>10% chance of another round</b> after each round — the game is basically ending, so betrayal is tempting. In the other, a <b>90% chance</b> — you'll probably face this player again, so cooperating pays. In classic human experiments, people cooperate far more when the game is likely to continue (in the reference data, first-round cooperation roughly tripled between comparable conditions — though that <a href="ref-dalbo-2011.html">human study ran under different rules</a>, so it's context, not a matched benchmark). That continuation incentive is what the AI panel was tested on, in <a href="concept-conditions.html">four repeated-game setups</a> (two continuation odds × two wordings), plus two one-shot cells: a “Community Game” framing, and a trick cell where the words “Cooperate” and “Defect” were pasted onto the opposite choices.</p>

<h2>Did the AI look human?</h2>
<p>At a glance, yes. Average cooperation rates landed inside a preregistered “consistent with human data” band in <a href="claim-p3-a3.html">three of four repeated-game setups</a>, and the miss was by a hair — 0.011. If you only checked the averages, which is how a lot of this research gets validated, you'd say it passed.</p>

<h2>But where did the variety actually come from?</h2>
<p>Mostly not from anyone “deciding” anything. <a href="concept-personas.html">Ten of the sixteen characters</a> were locked dials — 0% or 100% cooperation in every setup, every time. The panel's spread came largely from <i>which sentence you fed it</i> rather than from characters weighing choices: less “sixteen people,” more “sixteen wind-up toys, each doing its one thing.” (How dominant that mixing is depends on statistical assumptions — the honest range runs from “about half” to “nearly all” of the variation; <a href="claim-composition.html">the decomposition page</a> shows all the views.)</p>

<h2>Did they respond to the incentive that mattered?</h2>
<p>Not detectably. Going from “game's ending” to “game continues” moved average cooperation up by only about <a href="claim-response.html">8 points out of 100</a> — and with six games per character per setup, the uncertainty is wide enough that the true effect could plausibly be zero or even negative. The correct claim is “no meaningful response could be pinned down,” not “there was none.” The plain no-character model was starker: <a href="phase-3.html">0% cooperation at every continuation probability</a>.</p>

<h2>What DID move the AI?</h2>
<p>Words. Rewriting one sentence — re-phrasing and re-positioning how the continue-chance was described, changing nothing about the actual odds — flipped the plain model from <a href="claim-s2-switch.html">0/40 cooperation to 37/40</a>. And in the label-swap game, it picked the option carrying the word “Defect” <a href="claim-label-swap.html">all 40 times, even though that option paid worse</a>. It followed the vocabulary, not the money.</p>

<h2>What about the one character that seemed genuinely responsive?</h2>
<p>One character — p13, “Harper, a 61-year-old landscape gardener” — went from 33% cooperation to 75% when the game was likely to continue. Exactly what you'd hope for. But the way it was found wasn't a fair test: <a href="claim-p13.html">32 candidate combinations were checked and any hit would have counted</a> — like buying 32 lottery tickets and being amazed one won. External reviewers caught it, and the paper demotes its own best result from “finding” to “worth retesting properly” — with the added twist that the archived data is <i>too small to settle it either way</i>: the conservative re-test literally cannot reach significance at six games per cell.</p>

<h2>So what's the headline?</h2>
<p>“The averages look human” is a test an AI can pass without behaving like a human where it counts. These synthetic participants matched human-looking numbers while no meaningful reaction to the game's central incentive could be established — and their behavior could be flipped by a reworded sentence or a swapped label. If you use AI as synthetic study participants, validate the specific reaction your study is about, not just the totals. Side story: the whole thing ran with receipts — <a href="an-dead-predictions.html">predictions written down in advance</a> (twelve were refuted), <a href="reviews.html">mistakes found by reviewers</a>, and corrections published instead of quietly edited.</p>

<p class="part">Part 2 · The details people ask next</p>

<h2>How many game variations, exactly?</h2>
<p>Each of the sixteen characters played six setups — <a href="concept-conditions.html">96 character-setup combinations</a>. The four repeated-game setups ran 6 games per character; the two one-shot setups ran 20 per character. Phase 5 totaled <a href="phase-5.html">1,712 completed runs</a>, on top of ~3,200 from earlier phases.</p>

<h2>Any other games?</h2>
<p>Yes, mainly with the plain no-character model in <a href="phase-3.html">Phase 3</a> and <a href="phase-4.html">Phase 4</a>: one-shot framing games (“Community Game” vs. “Wall Street Game” — framing worked, 17.5% vs 0%), and Rock-Paper-Scissors — including matches against scripted opponents, where the model's exploitability turned out to depend on who it was playing (Part 3 below), and a strange <a href="claim-rps-role.html">seat-attached bias</a> that survived renaming the moves to neutral symbols.</p>

<h2>Any other models?</h2>
<p>Two stories. <b>Claude Haiku</b> was the registered second model but failed the <a href="claim-drift.html">basic entry gate</a> — it couldn't reliably produce a one-token move under the protocol — and was replaced, under a sealed amendment, by <b>Gemini 2.5 Flash</b>. Gemini got a smaller, explicitly descriptive side tier (24 persona-cells in Phase 5, mirrors in Phase 4) and behaved noticeably differently: more mixed, non-extreme behavior (9 of 24 cells “interior” versus 14 of 96 for GPT-4.1), and several wording effects <a href="claim-crossvendor-label.html">flipped direction</a>. So “locked dials” is a fact about this GPT-4.1 setup, not a law of LLMs.</p>

<h2>Wasn't it just the temperature setting?</h2>
<p>No — and this was tested. Main runs used temperature 0.7; a registered sweep re-ran four characters at 1.0 and 1.3. Turning up the randomness did not unlock human-like variety: <a href="claim-entropy.html">measured choice variety actually drifted slightly down</a> (0.83 → 0.78 → 0.77 bits on the matched comparison). The extremeness isn't a randomness dial; it's the model.</p>

<h2>How big was this, really?</h2>
<p>About <a href="an-counts.html">5,505 completed runs, 54,276 rounds, and 36,251 archived AI requests</a> (13.1 million input tokens; the answers were usually one token). And the record self-verifies: anyone can <a href="art-capsule.html">replay all 4,919 archived runs byte-for-byte</a> on a laptop without making a single new AI call. The one-sentence discovery came from a systematic <a href="claim-s2-switch.html">ladder</a> — swapping one span of the prompt at a time until the single controlling edit emerged. And a monitoring tripwire <a href="claim-drift.html">caught the API provider's model changing behavior mid-project</a>, forcing a freeze and a permanent monitoring fix.</p>

<p class="part">Part 3 · Findings that didn't make the paper's main arc</p>

<p>The paper deliberately narrowed to one causal chain — marginal checks pass → variety is composition → words control the corners → the star result demoted. Phases 3–4 produced more than that. These live in <a href="https://github.com/yoheinakajima/synthetic-players/blob/main/docs/paper/paper.md">Appendix A</a>, the <a href="https://github.com/yoheinakajima/synthetic-players/blob/main/docs/analysis/cut-map.md">cut map</a>, and the archived phase reports — none of it was discarded, but most of it is one paragraph where it could be a paper.</p>

<h2>The exploitability suite: the obvious exploit fails, the dumb one works</h2>
<p>The model had a near-perfect tell — after losing a round of RPS it switched moves ~97% of the time. An opponent <i>built specifically to punish that tell</i> made essentially nothing (+0.008/round, statistically zero). Meanwhile a simple pattern-matcher tracking the last two moves <a href="claim-adversary.html">profitably exploited it</a> (+0.215/round), and a frequency-tracker actually <i>lost</i> to the model (−0.118) — the opposite of the preregistered prediction. Behavioral signatures measured in one matchup didn't transport to another: exploitability is opponent-contingent. This could be its own short paper.</p>

<h2>The rock thing is weirder than it sounds</h2>
<p>The plain model played rock 80% of the time — far outside the human band. The strange part came later: with moves renamed to neutral symbols and display order fully counterbalanced, a pull toward the <i>rock-mapped role</i> persisted — attached to the game role, not the word “rock” or its screen position — and the registered position-bias prediction <a href="claim-rps-role.html">reversed sign</a>. Gemini showed the opposite-signed bias on the same contrast. A seat-attached asymmetry in a perfectly symmetric game, different per vendor, is genuinely odd — and it's a few sentences in Appendix A.2.</p>

<h2>GPT follows words absolutely; Gemini follows them only when it's cheap</h2>
<p>In the label-swap cell, GPT-4.1 followed the word “Defect” 40/40 even at a payoff cost. Gemini's choices mostly landed on the better-paying option instead (word-following ~79% — but in that cell the word and the money pointed the same way for Gemini, so it's confounded). The separator was the <a href="claim-crossvendor-label.html">counterfactual-payoff cell</a>, where the payoffs were flipped so the “Defect”-labeled option became the better one: Gemini followed the money (word-following fell to 1 of 40), while for GPT-4.1 word and payoff agreed, so its cell can't separate the two. One caveat the record is strict about: the fully <i>balanced</i>-payoff probe that would nail this down was never run — it fell outside the sealed experiment boundary. Still, this is the sharpest model-vs-model difference in the program, and it's compressed to one appendix paragraph.</p>

<h2>Wording power is context-dependent — that's the point</h2>
<p>The sentence rewording that flips repeated-game cooperation from 0/40 to 37/40 does <i>nothing</i> in one-shot games: a full 640-episode sweep of ordinary wording variations was a <a href="claim-d1-wording.html">clean null</a> (+0.6 points, p=1.00). The model isn't “sensitive to phrasing” in general — it's sensitive to phrasing <i>about the future of the game</i>. That null was restored to the paper in the final review pass, but it reads as a footnote to the switch rather than the finding it is.</p>

<h2>Merely mentioning “more rounds” is itself a giant treatment</h2>
<p>A setup where the model cooperated 10% of the time as a one-shot jumped to 75–100% the moment it was wrapped in repeated-game language — before the continuation odds even mattered. The wrapper saturated behavior so hard that an entire planned family of continuation-sensitivity comparisons became <a href="phase-4.html">uninterpretable (“corner-confounded”) by the registered rules</a>.</p>

<h2>The provider changed the model mid-study — and the tripwire caught it</h2>
<p>Behavioral fingerprinting caught Gemini's unversioned endpoint drifting over several days — 10/10 baseline matches decaying to 6–7 and oscillating — while version strings and API health looked normal. The study <a href="claim-drift.html">auto-froze at a block boundary, re-baselined, disclosed, and gained an attestation gate</a>; the affected tier was demoted rather than rescued. Zero contaminated confirmatory spend. As an operational case study — “the API you're studying is a moving target; here's how to detect it behaviorally” — it's methods-paper material.</p>

<h2>Two smaller loose ends</h2>
<p>The <a href="claim-entropy.html">temperature-entropy inversion</a> (more randomness, slightly <i>less</i> measured choice variety — exploratory, mechanism unknown). And the p13-vs-p05 puzzle: <a href="concept-personas.html">p05 “Riley, 35”</a> has the <i>same three traits</i> as p13 “Harper, 61” — competitive, patient, risk-averse — yet only the 61-year-old showed the big apparent slope (p05's was +0.08). The post-hoc “trait tension” theory about why was deliberately excluded from the paper along with the p13 demotion; it's a <a href="phase-6.html">Phase 6 question</a> now.</p>

<h2>If there's a follow-up paper in here, where is it?</h2>
<p>Two candidates stand out, both with complete, replayable data already in the archive: the opponent-contingent exploitability suite, and the cross-vendor word-versus-payoff dissociation (with the balanced-payoff cell as the missing experiment a follow-up would add). The <a href="phase-6.html">registered Phase 6 replication</a> — the properly powered re-test of incentive response — remains the committed next step.</p>
</div>
</article>
"""


def build_artifacts(idx, back, h):
    return f"""
<article class="item">
<p class="kicker">Materials</p>
<h1>Artifacts and verification surfaces</h1>
<p class="dek">Everything needed to read, check, or attack the result — and what each surface can and cannot prove.</p>
<div class="body">
{tbl(["Artifact", "Contents", "Verification"], [
    ['<a href="art-paper.html">Canonical paper</a>', "19-page PDF · byte-identical Markdown · minimal arXiv PDFLaTeX zip", "SHA-256 pins; CI recompiles and byte-compares all 19 rendered pages"],
    ['<a href="art-capsule.html">Replay capsule</a>', "archived databases + verifier", "4,919 runs replayed with zero credentials and zero live calls"],
    ['<a href="art-provenance.html">Seals and timestamps</a>', "hash manifests, tags, releases, OTS proofs", "external chronology anchors on Bitcoin blocks 959483–960086"],
    ['<a href="concept-personas.html">Persona registry</a>', "16 sealed sentences, construction rule, per-persona SHA-256", "sealed pre-data in registry v4"],
    ['<a href="concept-discussion.html">Precommitted discussion</a>', "four full branches written before Phase 5 data", "byte-identical to sealed hash; correction table beside the quoted excerpt"],
    ['<a href="an-dead-predictions.html">Dead predictions</a>', "12 refuted author predictions", "adjudicated by sealed code; published regardless of direction"],
    ['<a href="https://github.com/yoheinakajima/synthetic-players/blob/main/docs/instance-ledger.md">Instance ledger</a>', "22 process failures with causes and durable rules", "every confirmatory-touching resolution went the conservative direction"],
    ['<a href="https://github.com/yoheinakajima/synthetic-players/tree/main/docs/analysis">Analysis pack</a>', "claims ledger, dependency audit, corner map, stability compendium, submission analyses", "zero-call scripts over archived databases, committed with seeds"],
])}
<h2>Reproduce</h2>
<div class="terminal"><button id="copy-command" type="button">Copy</button><pre><code id="verify-command">git clone https://github.com/yoheinakajima/synthetic-players
cd synthetic-players/capsule
bash verify.sh</code></pre></div>
<p class="smallprint">Expected: CAPSULE VERIFICATION PASS — 4,919 archived Phase 3-5 runs verified (4,916 confirmatory + 3 legacy diagnostics). The capsule is transactional: the checkout is restored on success or failure.</p>
</div>
</article>
"""


SPECIAL_PAGES = [
    ("index.html", "Synthetic Players — Passing Coarse Marginal Checks Can Be Cheap",
     "A fixed panel of sixteen persona-conditioned GPT-4.1 configurations passed preregistered marginal checks while its treatment response stayed imprecisely estimated. Full auditable research record.",
     "index.html", build_index),
    ("qa.html", "Q&A — the whole study, plainly — Synthetic Players",
     "A conversational walkthrough of the study: what was tested, what moved the AI, the demoted result, and the findings that didn't make the paper.",
     "qa.html", build_qa),
    ("claims.html", "Claims ledger — Synthetic Players",
     "Every registered predicate and citable secondary with its evidentiary tier.",
     "claims.html", build_claims),
    ("phases.html", "Phases — Synthetic Players",
     "The five-phase sealed experimental program.",
     "phases.html", build_phases),
    ("timeline.html", "Timeline — Synthetic Players",
     "Chronology of the program with external anchors.",
     "timeline.html", build_timeline),
    ("reviews.html", "Review record — Synthetic Players",
     "Fourteen adversarial review rounds and their dispositions.",
     "reviews.html", build_reviews),
    ("related-work.html", "Related work — Synthetic Players",
     "Occupied territory, collisions, and precise differentiation.",
     "related-work.html", build_related),
    ("versions.html", "Manuscript versions — Synthetic Players",
     "The manuscript genealogy from v1 to the canonical release.",
     "versions.html", build_versions),
    ("artifacts.html", "Artifacts — Synthetic Players",
     "Verification surfaces: paper, capsule, seals, registries, ledgers.",
     "artifacts.html", build_artifacts),
]
