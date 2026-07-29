> **Pool vs DF2011 human distributions: pins, SDs, bimodality, delta-drop [EXPLORATORY] (source: engine/gen_analysis_pack.py)**

# Distribution pack — persona pools vs DF2011 human panels

> **STATUS: WORKING DRAFT — PRE-PUBLICATION, NOT FOR CITATION.**
> EXPLORATORY (close-out §3). Human pins (sealed in the Phase 5 predicates):
> Dal Bó & Fréchette 2011, R=40 first-round cooperation 0.6110 (δ matched to
> .90) and 0.1872 (δ matched to .10); between-subject SDs 0.3116 / 0.4122.
> Sources: `../figure-sources/p5-persona-means.csv`, adjudication report P5-1b.

## Level and response

| quantity | human (DF2011) | persona pool (T=0.7) |
|---|---|---|
| first-round coop, δ=.90 | 0.611 | 0.432 (s2a) / 0.505 (s2p) |
| first-round coop, δ=.10 | 0.187 | 0.349 (s2a) / 0.427 (s2p) |
| δ-response (drop .90→.10) | **−0.424** | −0.083 (s2a) / −0.078 (s2p) |
| between-subject SD, δ=.90 | 0.3116 | 0.4454 / 0.4362 |
| between-subject SD, δ=.10 | 0.4122 | 0.4241 / 0.4800 |

The pool matches human *levels* within ~0.15 and human *spread* fully
(P5-1b consistent in all four cells) while showing **one fifth of the human
δ-response at pool level**. The S2 paraphrase, by contrast, moves the pool
+0.07–0.08 — in this population the wording lever and the δ lever have
comparable pool-level force, where in humans δ dominates.

## Shape

Human panels at these ns are broad unimodal-with-mass-at-corners; the
persona pool is starkly bimodal by leaning (coop-leaning 0.62–0.87,
defect-leaning 0.08–0.18 pool means; 9 of 16 personas are pure-corner in
every cell). The P5-1b SD match is therefore a shape artifact — variance
without interior mass, exactly the "shape-blind" caveat recorded in
outcome-blind completion D3. Per-persona histograms per cell are one line
of pandas away from `p5-persona-means.csv`.

## Reading

A mixture of leaning-corners can impersonate a human panel in mean and
variance while failing every response-level and shape diagnostic. Any
synthetic-panel validation protocol that checks only marginal moments would
have certified this pool; the δ-response column is the discriminator.
