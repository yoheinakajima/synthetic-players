> **STATUS: PROPOSED — UNREGISTERED, UNSEALED, NOT RUN.** This is the
> operator's Phase 5 design sketch, committed verbatim per its own §0
> entry criteria. Nothing here is sealed; nothing dispatches before the
> freeze packet is approved by the operator's one-line sign-off.

Phase 5 prompt for Replit agent — final experiment, registration packet

Phase 5 is the last experiment for paper one. That's sealed as a stopping rule, not a preference: whatever Phase 5 surfaces beyond its registered predicates goes to future work — no new arms, no Phase 6 before publication. The question it answers: can any conditioning of the subject — content-side (personas) or decoding-side (temperature) — produce a human-like interior behavioral population, or do both just relocate and decorate the corners? Everything below is a proposal for the freeze packet; nothing runs before sign-off. Prepare the packet, bring me predicates, thresholds, persona registry contents, cell counts, fraction/aliasing, call table, and shedding order for approval. Predicates freeze first, registry v4 seals (append-only, per-arm shas, external anchor at seal like phase4-v3), then runs.

0. Entry criteria — verified before the packet is even drafted

The five rules from the instance ledger are now floor, not aspiration. Entry-verify and record: (1) freeze-time completeness linter live, acceptance test = reproduce prior instances as seal failures; (2) evaluator-attestation dispatch gating live (no attestation = no dispatch, fail-closed); (3) three-layer rule checked by the linter — every sealed rule exists in dispatch, enforcement, and replay; (4) watchdog auto-resume active for the registered restart/transport signatures; (5) budgeting from ledger prices, never design-unit counts. Also commit the Phase 5 design sketch (this document's content) under docs/phase5/ — it was never committed — banner-marked PROPOSED until seal.

1. Persona registry (registry v4)
16 personas, generated pre-data by a seeded procedure from crossed trait factors: age band × occupation × disposition (e.g., agreeable/competitive, patient/impulsive, risk-averse/risk-seeking). No hand-picking, no piloting, no game-relevant content — dispositions are trait words only, never instructions about games, cooperation, or strategy.
Each persona is a sealed system-prompt template with its own sha. The subject-frame task prompts stay byte-identical to the sealed Phase 3/4 templates — personas change only the system prompt layer, so every Phase 5 cell has an exact bare-subject twin in the prior record.
Cooperative-leaning vs defect-leaning classification for the hierarchy cells is assigned by a registered rule from the disposition factors (e.g., agreeable+patient = cooperative-leaning), fixed at seal — never from observed behavior.
Participant definition: one persona × one seed lane; self-play pairs use the same persona in both seats (continuity with the X1/E lineage); seat pooling disclosed as before.
2. Temperature factor
T ∈ {0.7, 1.0, 1.3}. 0.7 is the program constant; 1.3 is the proposed high point — verify the proxy passes temperature through and assert the echoed value in provenance per call (extend the Phase 3 packet assertion per-T). If 1.3 degrades parse rates, that is data: invalid-trial rate per T is a registered secondary outcome, not a nuisance — the registered exclusion rule stands unchanged.
Prediction to register (mine, on the record): raising T adds symmetric flip-noise around the corners and raises invalid rates, without increasing the interior fraction — variance manufactured, behavior unchanged. Refutation (interior fraction rising with T, or payoff-graded response appearing) would be QRE-like structure and a headline.
3. Task cells

Lean scope — six task cells, all reusing sealed templates:

Repeated PD, δ ∈ {0.10, 0.90} × S2 ∈ {present, absent} (4 cells) — the program's main instrument.
One-shot label-swap, canonical payoffs (1 cell) — the D2 token-vs-dominance probe.
One-shot Community framing (1 cell) — the only known near-interior operating point for the bare subject (0.175); the variance anchor.
4. Claim families (draft predicates; freeze at sign-off with exact thresholds)
P5-1 corner mixture. Persona pools are mixtures of corners, not interior distributions. Predicates: fraction of persona-cells whose episode-level CP interval sits wholly inside (0.05, 0.95) — the Phase 4 two-sided gate, reused verbatim — below a registered threshold; and distribution-level, between-persona variance ratio vs published human within-condition panels (source the human numbers at freeze, cite them in the predicate as always).
P5-2 surface-cue dominance hierarchy. Personas in conflict with the two known switches: cooperative-leaning × S2-absent, defect-leaning × S2-present, and each leaning × label-swap. Registered directional prediction: task-text switches dominate system-prompt personas (local semantic content beats global framing — the Phase 4 thesis extended one layer up). Estimand: within-conflict-cell choice share attributable to the task switch vs the persona lean.
P5-3 within-persona incentive sensitivity. Existence claim: at least one persona passes the two-sided assay gate AND shows a δ slope with LB > 0, or refuses the dominated mislabeled option in the swap cell above a registered rate. My registered prediction: none does. One persona passing relocates human-likeness into the conditioning; zero passing across 16 personas × 3 temperatures completes the paper's strongest claim.
P5-4 temperature. Interior fraction does not increase with T (confirmatory); choice-entropy and invalid-rate curves by T (registered secondaries); behavioral change decomposed from parse degradation.
5. Subjects, sentinels, budget
Primary: gpt-4.1, same pinned revision — verify the revision is unchanged at entry; any provider-side change is a disclosed event, not a silent substitution.
Secondary: gemini at reduced tier only — T=0.7, core cells, replication framing — given the documented plateau instability; sentinel battery from day one includes at least one persona-conditioned fingerprint cell per model, per-window indexing armed from the start. Cost this tier separately in the packet so I can drop it cleanly if the table argues for it.
Full cross (16 × 3 × 6 × episodes) explodes; propose the fraction: full persona set at T=0.7, temperature sweep on a registered 4-persona × 3-cell subset (δ=0.90 pair + swap). Bring the aliasing consequences like D1. Target ≤ 15k subject calls global cap, shedding order registered in the packet from the start, waste headroom priced from ledger actuals.
6. Paper integration — the unusual part, treat it as sealed material
docs/paper/discussion-branches.md: the paper's discussion/conclusion section pre-committed verbatim per P5 outcome branch (corners-everywhere; any-interior-persona; temperature-graded; mixed), written and sealed BEFORE any Phase 5 dispatch, hash-anchored with the registry. The published paper's discussion must be byte-diffable against the branch that the verdicts select. This is the "author doesn't get a vote" thesis executed to the last paragraph — the linter should treat a missing branch for any registered verdict combination as a seal failure.
docs/paper/scope-seal.md: one page stating Phase 5 is the final experiment for paper one, with the no-new-arms rule and the future-work routing. Sealed with the registry.
7. Sign-off gate

Bring back: the full predicate list with human-anchored thresholds and sources, the sealed persona registry (all 16, verbatim), cell counts and fraction with aliasing, per-block call table both subjects, shedding order, the discussion-branches file, and the entry-criteria verification record. Nothing dispatches before my one-line approval of that packet. Same discipline as Phase 4, plus everything the instance ledger taught us.