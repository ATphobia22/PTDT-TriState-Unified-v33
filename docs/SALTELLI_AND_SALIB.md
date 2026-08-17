# Saltelli sample size + SALib usage

## Sample size formula

Let **N** = base sample size (`n_base`), **D** = number of parameters.

| Goal | Model runs |
|------|------------|
| First-order + total-order only | **N × (D + 2)** |
| Include second-order pairs | **N × (2D + 2)** |

Examples (D = 5 hydraulic factors):

- N = 64, first/total → **64 × 7 = 448** RAS (or surrogate) evaluations  
- N = 1024, first/total → **1024 × 7 = 7168**  
- N = 1024, second-order → **1024 × 12 = 12288**

Prefer **N as a power of 2** (64, 128, 256, 512, 1024) for Sobol sequence balance. Convergence of index confidence intervals usually needs N ≥ 512–1024 for noisy models; start smaller only for smoke tests.

PTDT helper:

```python
from sobol_sampler import saltelli_n_model_runs, generate_gsa_design

n_runs = saltelli_n_model_runs(1024, 5, calc_second_order=False)  # 7168
design = generate_gsa_design(n_base=64, seed=42)
assert design["n_rows"] == design["meta"]["n_model_runs"]
```

## Sobol sampler snippet

```python
from sobol_sampler import generate_gsa_design, saltelli_n_model_runs

bounds = {
    "manning_channel": (0.025, 0.045),
    "manning_floodplain": (0.04, 0.12),
    "mesh_cell_ft": (50.0, 150.0),
}
N, D = 128, len(bounds)
print("model runs:", saltelli_n_model_runs(N, D))  # 128 * 5 = 640

design = generate_gsa_design(n_base=N, bounds=bounds, seed=7)
X = design["matrix"]          # shape (640, 3)
problem = design["problem"]   # SALib problem dict
seal = design["seal"]         # evidence SHA-256

# Evaluate model once per row → Y shape (640,)
# Y[i] = f(X[i])  e.g. max WSE at Bonebank from sealed RAS plan i
```

## SALib analysis (optional dependency)

```bash
pip install SALib numpy scipy
```

```python
import numpy as np
from SALib.analyze import sobol
from sobol_sampler import generate_gsa_design

design = generate_gsa_design(n_base=256, seed=42, calc_second_order=False)
problem = design["problem"]
X = design["matrix"]

# Placeholder: replace with sealed RAS / surrogate outputs aligned to X rows
Y = np.random.default_rng(0).normal(size=X.shape[0])  # DEMO ONLY — not regulatory

Si = sobol.analyze(problem, Y, calc_second_order=False, print_to_console=True)
# Si["S1"], Si["ST"], Si["S1_conf"], Si["ST_conf"]
```

Modern SALib `ProblemSpec` API:

```python
from SALib import ProblemSpec
import numpy as np

sp = ProblemSpec({
    "names": design["parameter_names"],
    "bounds": design["problem"]["bounds"],
    "outputs": ["max_wse_ft"],
})
# Prefer feeding precomputed X/Y if using PTDT sealed matrix:
# sp.set_samples(X); sp.set_results(Y); sp.analyze_sobol()
```

**Invariant:** Y must come from real model runs on sealed designs — never random values for affidavits.
