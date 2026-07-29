# Family E report (interim, per registered rider: final verdicts in step 8)

## Branch outcomes (registered vocabulary)

- **dselected|gpt-4.1** — corner-confounded: assay invalid for slope inference (registered branch i — explicitly NOT evidence of δ-insensitivity)
- **dselected|gemini-2.5-flash** — corner-confounded: assay invalid for slope inference (registered branch i; enters Holm as p=1 placeholder)
- **community|gpt-4.1** — corner-confounded: assay invalid for slope inference (registered branch i; enters Holm as p=1 placeholder)
- **community|gemini-2.5-flash** — corner-confounded: assay invalid for slope inference (registered branch i; enters Holm as p=1 placeholder)

### Gate anatomy (per cell — which bound denied the license)

Gate predicate (registered pre-dispatch): Clopper–Pearson 95% on the episode-majority binary M_ep = 1{Y_ep ≥ .5} wholly inside the OPEN interval (0.05, 0.95) in at least one δ cell. A violated bound is the entire content of a denial — no judgment enters.

| assay | δ cell | M_ep | CP95 | bound status |
|---|---|---|---|---|
| dselected|gpt-4.1 | d10 | 19/20 | [0.751, 0.999] | ceiling bound violated (hi ≥ 0.95) |
| dselected|gpt-4.1 | d90 | 20/20 | [0.832, 1.000] | ceiling bound violated (hi ≥ 0.95) |
| dselected|gemini-2.5-flash | d10 | 3/20 | [0.032, 0.379] | floor bound violated (lo ≤ 0.05) |
| dselected|gemini-2.5-flash | d90 | 17/20 | [0.621, 0.968] | ceiling bound violated (hi ≥ 0.95) |
| community|gpt-4.1 | d10 | 20/20 | [0.832, 1.000] | ceiling bound violated (hi ≥ 0.95) |
| community|gpt-4.1 | d90 | 20/20 | [0.832, 1.000] | ceiling bound violated (hi ≥ 0.95) |
| community|gemini-2.5-flash | d10 | 17/20 | [0.621, 0.968] | ceiling bound violated (hi ≥ 0.95) |
| community|gemini-2.5-flash | d90 | 18/20 | [0.683, 0.988] | ceiling bound violated (hi ≥ 0.95) |

### Methods note — the ceiling side of the gate

**Lesson.** The X1 endpoints taught this design that corner cells break interval inference: the sealed v1 endpoint sat constant at the floor (every episode Y = 0.00), which is why the registered machinery carries exact fallbacks for constant cells (predicates §X2). **Registration.** E's assay gate was registered pre-dispatch as a two-sided OPEN interval — floor and ceiling are symmetric refusals — and the INTERIOR selection rule was registered at the D1/D2 boundary expressly to maximize the chance of clearing it (the MAXCOOP alternative's rationale named the corner risk). **Error prevented here.** community|gpt-4.1 realized M_ep = 20/20 in both δ cells (means 1.000/1.000), so its slope descriptive is exactly Δ̂ = +0.000. Without a ceiling side, the gate would have passed at ceiling and that flat descriptive would have entered the record as branch (iii) "inconclusive" — inviting a δ-insensitivity reading the design cannot support. With it, the cell is corner-confounded (branch i) and the registered rule that flatness is never asserted holds mechanically.

Ordering per rider 5: the verdicts above are adjudicated on the sealed samples exactly as written; window composition is interpretation-layer disclosure, never a decision surface.

### Gemini cells — usable episodes by dispatch window (boundaries = sentinel check 7 store rows)

- `p4-e-community-d10-cvx` — W(6,7): 7, W(7,8): 13
- `p4-e-community-d90-cvx` — W(6,7): 8, W(7,8): 12
- `p4-e-dselected-d10-cvx` — W(6,7): 9, W(7,8): 11
- `p4-e-dselected-d90-cvx` — W(6,7): 9, W(7,8): 11

**Selection context.** "Most interior" was relative, not absolute: all 16 M=can candidate cells in D1 sat low (grand mean 0.2547), and the selected cell's D1 mean is 0.100 (distance 0.400 from 0.5). A gate failure at the D-selected cells — floor or ceiling — is therefore an informative, registered outcome, and the adjudication branches (supported / corner-confounded / inconclusive) exist for exactly that case.

D-selected presentation: `pd-rep-w2a-sem-cf-ad` (write-once resolution; selection derivation in e-selection-report.md).
160 usable episodes; 0 excluded (none).
Provider-failure attempts (non-observations, registered rule): 2 — [{"runId": "run_1784936973_0c12b60d", "armId": "p4-e-community-d90-cvx", "episodeIndex": 5, "seed": 2897}, {"runId": "run_1784939744_e18b90c8", "armId": "p4-e-community-d90-cvx", "episodeIndex": 5, "seed": 2897}].

## Descriptive numbers

| assay | gate | mean Y δ=.10 | mean Y δ=.90 | slope Δ̂ | LB95 | verdict |
|---|---|---|---|---|---|---|
| dselected|gpt-4.1 | INVALID | 0.750 | 1.000 | +nan | +nan | corner-confounded: assay invalid for slope inference (registered branch i — explicitly NOT evidence of δ-insensitivity) |
| dselected|gemini-2.5-flash | INVALID | 0.075 | 0.450 | +nan | +nan | corner-confounded: assay invalid for slope inference (registered branch i; enters Holm as p=1 placeholder) |
| community|gpt-4.1 | INVALID | 1.000 | 1.000 | +nan | +nan | corner-confounded: assay invalid for slope inference (registered branch i; enters Holm as p=1 placeholder) |
| community|gemini-2.5-flash | INVALID | 0.725 | 0.725 | +nan | +nan | corner-confounded: assay invalid for slope inference (registered branch i; enters Holm as p=1 placeholder) |
