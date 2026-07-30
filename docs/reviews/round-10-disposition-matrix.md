# Round 10 disposition matrix — v11 review to preprint v12

> **STATUS:** generated work plan; validation results are committed beside the v12 manuscript. No new provider calls and no sealed source changes.

| ID | Disposition | v12 implementation |
|---|---|---|
| A1 | Adopt, improve beyond textual caveat | Add a zero-call verifier for all 320 Phase 3/X1 LLM runs and independently recompute the 20 deterministic P3-C3 baselines. Extend `capsule/verify.sh` so the public contract covers every confirmatory Phase 3–5 run. |
| A2 | Adopt | Define “switch-bearing” in the glossary as the span whose adjacent substitution produced the largest preregistered ladder gap and passed held-out confirmation. |
| A3 | Adopt after code/event audit | State that temperature and `max_tokens=16` were explicit; `top_p=1.0` was assembled but omitted from the wire at 1.0; presence/frequency penalties and logit bias were not supplied and inherited provider defaults. |
| B1 | Test independently | Reimplement the fixed-panel episode bootstrap without importing the original variance routine or human constants, run three high-replicate seeds, report full precision, and scan all bounds for reference-value collisions. |
| B2 | Adopt | Reframe the result as a displayed-label or label-linked learned-prior effect; name Prisoner’s Dilemma/game-theoretic memorization as a competing mechanism and note the missing non-PD control. |
| B3 | Adopt with full table | Publish all five non-swap cooperative- versus defect-leaning stratum means, eight prompts per group, and their differences. |
| B4 | Adopt | State where intervals first appear that width jointly reflects six independent episodes per cell and the conservative exact projection retaining uncertainty at empirical corners. |
| B5 | Adopt | Define P3-A3 and the frozen historical P5-1a “corner-mixture predicate” in the protocol glossary. |
| B6 | Adopt | State that Phase 6 will preregister candidate family, dependence unit, gate, maximum statistic, familywise rule, and sample size before data. |
| B7 | Adopt | Attribute binary-count divergence jointly to interval construction and low-resolution n=6 three-valued data. |
| B8 | Adopt | Lead the abstract and main interpretation with the fixed-panel latent-propensity posterior (63%–71% medians; 49%–81% intervals), then present 85%–96% as conditional plug-in estimates. |
| C1 | Test and define | Reproduce the historical pooled Shannon statistic, compute a composition-matched temperature lattice, and separately report pooled versus mean within-unit base-2 Shannon entropy. |

## Validation gate

- independent audits pass;
- all Phase 3–5 confirmatory runs verify with zero live model calls;
- manuscript and machine-readable summary regenerate;
- clean near-arXiv PDF builds and preflights;
- assertion, link, and sealed-boundary lint pass;
- exact v11→v12 changes and all outputs are committed before merge.
