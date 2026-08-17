"""
Sobol' index estimators + bootstrap confidence intervals (Saltelli layout).

Expects Y aligned to saltelli_sample_matrix rows:
  [A (N), B (N), A_B^(0..D-1) (N each)]  → length N*(D+2)
optional second-order block not required for S1/ST.

CI convention (SALib-compatible): report half-width
  conf ≈ z * std(bootstrap estimates)
so approximate 95% interval is index ± conf at conf_level=0.95.
"""
from __future__ import annotations

from typing import Any

import math

try:
    import numpy as np
except ImportError as exc:  # pragma: no cover
    raise ImportError("numpy required for sobol_indices") from exc


def _z_from_conf_level(conf_level: float) -> float:
    # Normal quantile for two-sided interval half-width multiplier
    # 0.95 → ~1.96; avoid scipy dependency via erfinv approximation if needed
    if not (0.5 < conf_level < 1.0):
        raise ValueError("conf_level must be in (0.5, 1)")
    try:
        from scipy.stats import norm

        return float(norm.ppf(0.5 + conf_level / 2.0))
    except ImportError:
        # Rational approximation for common levels
        table = {0.90: 1.64485362695, 0.95: 1.95996398454, 0.99: 2.57582930355}
        if conf_level in table:
            return table[conf_level]
        # Fallback: approximate via inverse erf for Φ^{-1}(p)
        p = 0.5 + conf_level / 2.0
        # Beasley-Springer-Moro style rough approx for demo; prefer scipy in CI
        t = math.sqrt(-2.0 * math.log(min(p, 1 - p)))
        z = t - (2.515517 + 0.802853 * t + 0.010328 * t * t) / (
            1 + 1.432788 * t + 0.189269 * t * t + 0.001308 * t * t * t
        )
        return z if p >= 0.5 else -z


def _split_saltelli_y(Y: np.ndarray, n_base: int, n_params: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    Y = np.asarray(Y, dtype=np.float64).ravel()
    expected = n_base * (n_params + 2)
    if Y.size < expected:
        raise ValueError(f"Y length {Y.size} < expected N*(D+2)={expected}")
    ya = Y[0:n_base]
    yb = Y[n_base : 2 * n_base]
    yab = Y[2 * n_base : 2 * n_base + n_base * n_params].reshape(n_params, n_base)
    return ya, yb, yab


def estimate_s1_st(
    Y: np.ndarray,
    n_base: int,
    n_params: int,
) -> dict[str, np.ndarray]:
    """
    Saltelli estimators (Jansen / Saltelli common form):

    ST_i ≈ 0.5 * mean( (Y_A - Y_ABi)^2 ) / Var(Y)
    S1_i ≈ mean( Y_B * (Y_ABi - Y_A) ) / Var(Y)   (Saltelli 2002-style)

    Variance denominator uses concatenated A|B for stability.
    """
    ya, yb, yab = _split_saltelli_y(Y, n_base, n_params)
    y_ref = np.concatenate([ya, yb])
    var_y = float(np.var(y_ref, ddof=1))
    if var_y <= 0.0 or not math.isfinite(var_y):
        raise ValueError("output variance is zero or non-finite; cannot form Sobol indices")

    s1 = np.empty(n_params, dtype=np.float64)
    st = np.empty(n_params, dtype=np.float64)
    for i in range(n_params):
        y_abi = yab[i]
        st[i] = 0.5 * float(np.mean((ya - y_abi) ** 2)) / var_y
        s1[i] = float(np.mean(yb * (y_abi - ya))) / var_y
    return {"S1": s1, "ST": st, "var_y": np.array([var_y])}


def bootstrap_sobol_ci(
    Y: np.ndarray,
    n_base: int,
    n_params: int,
    *,
    num_resamples: int = 100,
    conf_level: float = 0.95,
    seed: int | None = 0,
) -> dict[str, Any]:
    """
    Point estimates + bootstrap confidence half-widths for S1 and ST.

    Bootstrap: resample the N-row blocks with replacement (paired across A, B, ABi).
    Returns SALib-like keys: S1, ST, S1_conf, ST_conf.
    """
    if num_resamples < 10:
        raise ValueError("num_resamples should be ≥ 10")
    ya, yb, yab = _split_saltelli_y(Y, n_base, n_params)
    point = estimate_s1_st(Y, n_base, n_params)
    rng = np.random.default_rng(seed)
    s1_boot = np.empty((num_resamples, n_params), dtype=np.float64)
    st_boot = np.empty((num_resamples, n_params), dtype=np.float64)

    for b in range(num_resamples):
        idx = rng.integers(0, n_base, size=n_base)
        y_boot = np.concatenate(
            [
                ya[idx],
                yb[idx],
                yab[:, idx].reshape(-1),
            ]
        )
        est = estimate_s1_st(y_boot, n_base, n_params)
        s1_boot[b] = est["S1"]
        st_boot[b] = est["ST"]

    z = _z_from_conf_level(conf_level)
    s1_conf = z * s1_boot.std(axis=0, ddof=1)
    st_conf = z * st_boot.std(axis=0, ddof=1)

    return {
        "S1": point["S1"],
        "ST": point["ST"],
        "S1_conf": s1_conf,
        "ST_conf": st_conf,
        "conf_level": conf_level,
        "num_resamples": num_resamples,
        "var_y": float(point["var_y"][0]),
        "interval_note": "approx index ± conf (normal half-width from bootstrap std)",
    }


def analyze_with_salib_or_builtin(
    problem: dict[str, Any],
    Y: np.ndarray,
    *,
    n_base: int | None = None,
    calc_second_order: bool = False,
    conf_level: float = 0.95,
    num_resamples: int = 100,
    seed: int | None = 0,
) -> dict[str, Any]:
    """Prefer SALib when installed; else builtin S1/ST + bootstrap CI."""
    Y = np.asarray(Y, dtype=np.float64).ravel()
    try:
        from SALib.analyze import sobol as salib_sobol

        return dict(
            salib_sobol.analyze(
                problem,
                Y,
                calc_second_order=calc_second_order,
                conf_level=conf_level,
                num_resamples=num_resamples,
                print_to_console=False,
                seed=seed,
            )
        )
    except ImportError:
        d = int(problem["num_vars"])
        if n_base is None:
            # Infer N from Y and D for first-order design
            if Y.size % (d + 2) != 0:
                raise ValueError("Cannot infer n_base; pass n_base= explicitly")
            n_base = Y.size // (d + 2)
        return bootstrap_sobol_ci(
            Y,
            n_base,
            d,
            num_resamples=num_resamples,
            conf_level=conf_level,
            seed=seed,
        )


if __name__ == "__main__":
    # Deterministic smoke: linear model f = x0 + 2*x1 (S1 ≈ shares of var)
    from sobol_sampler import saltelli_sample_matrix

    bounds = [(0.0, 1.0), (0.0, 1.0)]
    n = 256
    X = saltelli_sample_matrix(n, bounds, seed=1, calc_second_order=False)
    Y = X[:, 0] + 2.0 * X[:, 1]
    res = bootstrap_sobol_ci(Y, n, 2, num_resamples=50, seed=1)
    print("S1", np.round(res["S1"], 4), "±", np.round(res["S1_conf"], 4))
    print("ST", np.round(res["ST"], 4), "±", np.round(res["ST_conf"], 4))
