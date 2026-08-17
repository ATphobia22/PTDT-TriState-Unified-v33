# Sobol confidence intervals + Morris elementary effects

## Sobol index confidence intervals

SALib / PTDT report **`S1_conf` / `ST_conf` as half-widths**:

\[
\widehat{S} \pm z_{1-\alpha/2}\,\mathrm{sd}(\widehat{S}^{(\mathrm{boot})})
\]

- Bootstrap resamples the **N-row blocks** of the Saltelli design (A, B, AB_i) together.
- Default **conf_level=0.95** → z ≈ 1.96.
- Wide CI ⇒ increase **N** (base sample size), not only bootstrap count.
- Indices can be slightly outside [0,1] due to sampling error; treat CI overlap with zero as “not significant.”

```python
from sobol_sampler import generate_gsa_design
from sobol_indices import bootstrap_sobol_ci, analyze_with_salib_or_builtin

design = generate_gsa_design(n_base=256, seed=42)
X = design["matrix"]
# Y = sealed model outputs, length N*(D+2)
res = bootstrap_sobol_ci(Y, n_base=256, n_params=X.shape[1], num_resamples=100, seed=0)
# res["S1"], res["S1_conf"], res["ST"], res["ST_conf"]
```

Prefer `analyze_with_salib_or_builtin(problem, Y)` when SALib is installed.

## Morris method (elementary effects)

- **Cost:** `r × (D + 1)` runs (e.g. r=20, D=5 → 120) vs Saltelli hundreds–thousands.
- **Trajectory:** start on a p-level grid; one-factor-at-a-time steps of size Δ.
- **EE:** \((f(x+\Delta e_i)-f(x))/\Delta\).
- **μ\*** = mean |EE| (importance); **σ** = std of EE (nonlinearity / interactions); **μ** = signed mean (can cancel).

| Pattern | Meaning |
|---------|---------|
| High μ*, low σ | Influential, roughly linear |
| High μ*, high σ | Influential + nonlinear/interactions |
| Low μ* | Candidate to fix / drop before Sobol |

```python
from morris_sampler import sample_morris_trajectories, elementary_effects

bounds = [(0.025, 0.045), (0.04, 0.12)]
des = sample_morris_trajectories(30, bounds, num_levels=4, seed=1)
# run model on des["matrix"] → Y
stats = elementary_effects(
    Y, n_trajectories=30, n_params=2,
    delta_unit=des["delta_unit"], step_meta=des["step_meta"],
)
```

**Workflow:** Morris screen → fix non-influential factors → Saltelli/Sobol on remaining → report S1/ST ± CI on sealed RAS outputs only.
