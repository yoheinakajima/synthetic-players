# Propositions — what the study demonstrates, and what nothing here identifies

> **STATUS: DOCUMENTATION — R2 item 3, 2026-07-29. Conceptual layer;
> no new data, zero subject calls. Notation is defined here and used in
> `hierarchy.md` and the paper draft.**

Setup. Binary round-1 outcome Y ∈ {0,1}; condition d ∈ {0,1} (e.g.
δ=.10 vs δ=.90). Personas i = 1…16 with condition-specific means
p_i(d) = E[Y | persona i, d]. Decompose the population moments:

- pool mean **μ(d)** = (1/16) Σᵢ p_i(d)
- between-persona variance **B(d)** = Var_i(p_i(d))
- within-persona variance **W(d)** = (1/16) Σᵢ p_i(d)(1 − p_i(d))
- persona-level response **Δᵢ** = p_i(1) − p_i(0)

Total variance at condition d is B(d) + W(d); the pool response is
Δ̄ = μ(1) − μ(0) = (1/16) Σᵢ Δᵢ.

## Proposition A — coarse marginal validation does not identify aggregate treatment response

**Claim.** Validation criteria of the kind used in practice — broad
bands on μ(d), pooled or separate-condition tolerances on B(d) + W(d),
each condition checked in isolation — can all pass while Δ̄ takes any
value in a wide interval, including the wrong sign.

**Why.** The criteria constrain each marginal distribution of Y | d
only up to a band. Δ̄ = μ(1) − μ(0) is a *difference of the two
marginals' means*; if each mean is only pinned to a band of width w,
Δ̄ is only pinned to a band of width 2w around the human difference —
and corner-mixture populations (this study's pools: bimodal by
leaning, 9–10 of 16 personas pure-corner in every cell) can sit
anywhere in that band while matching level and variance bands exactly.
Empirically here: levels within ~0.15 of the published values, SDs
inside the published bands, and a pool δ-response of −0.08 against the
published human −0.42 (nonmatched comparator).

**The identity that makes "coarse" the operative word.** Since
Δ̄ = μ(1) − μ(0) exactly, *exact* condition-specific mean matching
would force the correct aggregate effect by identity. Coarse criteria
are therefore precisely the ones that are cheat-able: the failure mode
lives entirely in the slack of the bands, which is why our validation
criteria must be described as **coarse marginal checks** — the study's
demonstration is that populations passing them can carry essentially
no incentive economics.

## Proposition B — even exact aggregate moments do not identify the individual structure

**Claim.** Suppose μ(d), B(d), W(d) are matched *exactly* at every
condition — not bands, equalities. This still does not identify:

1. **the between/within allocation at the response level** — how Δ̄
   distributes across personas: sixteen personas each with Δᵢ = Δ̄, or
   one persona with Δᵢ = 16·Δ̄ and fifteen with Δᵢ = 0, generate
   identical per-condition moments whenever the p_i(d) multisets
   match;
2. **the corner concentration** — whether mass at p ≈ 0/1 is the same
   individuals at both conditions or different ones (the permutation
   of persona identities across conditions is invisible to every
   per-condition moment);
3. **the joint coupling of potential outcomes — the Δᵢ
   distribution.** Per-condition moments are functionals of the two
   marginal distributions of {p_i(0)} and {p_i(1)} separately. The Δᵢ
   distribution is a functional of the *joint* distribution
   (coupling), which is unconstrained by the marginals beyond
   Fréchet–Hoeffding bounds. Identifying it requires repeated
   measurements of the same unit under both conditions (a within-unit
   design — available for synthetic personas, structurally absent
   from between-session human data such as DF2011) or structural
   assumptions (e.g. rank invariance, a parametric random-effects
   model) that must then be declared and defended.

**Consequence for this study's comparisons.** Our within-persona Δᵢ is
measurable because the persona is re-runnable; the published human
comparator observes only μ(d) across different sessions. The two
estimands live on different sides of Proposition B — which is exactly
why every DF-derived pin in this project is labeled *published,
nonmatched comparator*, and why no analysis here claims a human Δᵢ
distribution to compare against.
