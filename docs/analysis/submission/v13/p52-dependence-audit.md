# P5-2 dependence-aware sensitivity

> Post-adjudication, zero subject calls. Historical adjudication unchanged.

- Historical episode mean: 45/352 = 0.127841; episode-iid projection [0.091753, 0.172069].
- Stratified prompt-cluster bootstrap (40 persona x conflict-cell clusters, five strata, B=200,000, seed 20260731): [0.071023, 0.188920].
- Fixed-panel Dirichlet-Jeffreys aggregation (40 prompt-condition propensities, 200,000 draws, seed 20260732): median 0.172390, 95% interval [0.152215, 0.194907], Pr(theta <= .20)=0.9911.

Both sensitivities remain below the frozen 0.20 persona-dominant boundary. The classification remains mechanism-confounded and is driven by the swap cell.
