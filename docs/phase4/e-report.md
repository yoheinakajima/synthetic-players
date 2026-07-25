# Family E report (interim, per registered rider: final verdicts in step 8)

## Branch outcomes (registered vocabulary)

- **dselected|gpt-4.1** — corner-confounded: assay invalid for slope inference (registered branch i — explicitly NOT evidence of δ-insensitivity)
- **dselected|gemini-2.5-flash** — corner-confounded: assay invalid for slope inference (registered branch i; enters Holm as p=1 placeholder)
- **community|gpt-4.1** — corner-confounded: assay invalid for slope inference (registered branch i; enters Holm as p=1 placeholder)
- **community|gemini-2.5-flash** — corner-confounded: assay invalid for slope inference (registered branch i; enters Holm as p=1 placeholder)

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
