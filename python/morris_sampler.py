"""
Method of Morris (elementary effects) — screening design.

Cost: r * (D + 1) model runs for r trajectories and D parameters.
Outputs per factor: mu, mu_star (mean |EE|), sigma (std of EE).

Use for cheap ranking before expensive Saltelli/Sobol on HEC-RAS.
"""
from __future__ import annotations

from hashlib import sha256
from typing import Any, Mapping, Sequence

import json
import math

try:
    import numpy as np
except ImportError as exc:  # pragma: no cover
    raise ImportError("numpy required for morris_sampler") from exc


def morris_n_model_runs(n_trajectories: int, n_params: int) -> int:
    if n_trajectories < 1 or n_params < 1:
        raise ValueError("n_trajectories and n_params must be ≥ 1")
    return int(n_trajectories * (n_params + 1))


def _grid_levels(num_levels: int) -> np.ndarray:
    if num_levels < 2 or num_levels % 2 != 0:
        raise ValueError("num_levels must be even and ≥ 2")
    return np.linspace(0.0, 1.0, num_levels)


def sample_morris_trajectories(
    n_trajectories: int,
    bounds: Sequence[tuple[float, float]],
    *,
    num_levels: int = 4,
    seed: int | None = 0,
) -> dict[str, Any]:
    """
    Vanilla Morris trajectories on a p-level grid.

    Returns matrix shape (r*(D+1), D) in physical units, plus delta and order map.
    """
    d = len(bounds)
    if d < 1:
        raise ValueError("at least one bound required")
    levels = _grid_levels(num_levels)
    # Step size Δ = p / (2*(p-1)) in unit space (classic even-p Morris)
    delta = num_levels / (2.0 * (num_levels - 1))
    rng = np.random.default_rng(seed)

    rows: list[np.ndarray] = []
    traj_meta: list[dict[str, Any]] = []

    for t in range(n_trajectories):
        # Start at random grid point with room to step ±Δ on each dim eventually
        x = np.array([float(rng.choice(levels)) for _ in range(d)], dtype=np.float64)
        # Clamp so x_i + Δ or x_i - Δ stays in [0,1] when possible
        order = rng.permutation(d)
        points = [x.copy()]
        for k, j in enumerate(order):
            xj = points[-1].copy()
            # Prefer +Δ if feasible else -Δ
            if xj[j] + delta <= 1.0 + 1e-12:
                xj[j] = min(1.0, xj[j] + delta)
                step_sign = 1.0
            else:
                xj[j] = max(0.0, xj[j] - delta)
                step_sign = -1.0
            points.append(xj)
            traj_meta.append(
                {"trajectory": t, "step": k, "param_index": int(j), "sign": step_sign}
            )
        for p in points:
            rows.append(p)

    unit = np.vstack(rows)
    physical = np.empty_like(unit)
    for j, (lo, hi) in enumerate(bounds):
        if not (math.isfinite(lo) and math.isfinite(hi)) or hi < lo:
            raise ValueError(f"invalid bounds at {j}")
        physical[:, j] = lo + unit[:, j] * (hi - lo)

    payload = {
        "schema_version": 1,
        "n_trajectories": n_trajectories,
        "n_params": d,
        "num_levels": num_levels,
        "delta_unit": delta,
        "shape": list(physical.shape),
        "samples": np.round(physical, 12).tolist(),
    }
    seal = sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    return {
        "status": "OK",
        "matrix": physical,
        "unit_matrix": unit,
        "n_rows": int(physical.shape[0]),
        "delta_unit": delta,
        "num_levels": num_levels,
        "step_meta": traj_meta,
        "n_model_runs": morris_n_model_runs(n_trajectories, d),
        "seal": seal,
    }


def elementary_effects(
    Y: np.ndarray,
    n_trajectories: int,
    n_params: int,
    *,
    delta_unit: float,
    step_meta: Sequence[Mapping[str, Any]],
) -> dict[str, np.ndarray]:
    """
    Compute EE per step; aggregate mu, mu_star, sigma per parameter.

    Y length must be r*(D+1). Within trajectory t, points are sequential;
    step_meta lists which param changed between consecutive points.
    """
    Y = np.asarray(Y, dtype=np.float64).ravel()
    expected = morris_n_model_runs(n_trajectories, n_params)
    if Y.size != expected:
        raise ValueError(f"Y length {Y.size} != expected {expected}")
    if len(step_meta) != n_trajectories * n_params:
        raise ValueError("step_meta length must be r*D")

    ees: list[list[float]] = [[] for _ in range(n_params)]
    for t in range(n_trajectories):
        base = t * (n_params + 1)
        for s in range(n_params):
            meta = step_meta[t * n_params + s]
            j = int(meta["param_index"])
            sign = float(meta["sign"])
            y0 = Y[base + s]
            y1 = Y[base + s + 1]
            # EE = (f(x+Δe) - f(x)) / Δ  with sign absorbed in Δ direction
            ee = (y1 - y0) / (sign * delta_unit)
            ees[j].append(float(ee))

    mu = np.array([float(np.mean(v)) if v else 0.0 for v in ees])
    mu_star = np.array([float(np.mean(np.abs(v))) if v else 0.0 for v in ees])
    sigma = np.array([float(np.std(v, ddof=1)) if len(v) > 1 else 0.0 for v in ees])
    return {"mu": mu, "mu_star": mu_star, "sigma": sigma}


def analyze_morris(
    bounds: Mapping[str, tuple[float, float]],
    Y: np.ndarray,
    design: Mapping[str, Any],
) -> dict[str, Any]:
    names = list(bounds.keys())
    d = len(names)
    stats = elementary_effects(
        Y,
        int(design["n_model_runs"] // (d + 1)),
        d,
        delta_unit=float(design["delta_unit"]),
        step_meta=design["step_meta"],
    )
    return {
        "names": names,
        "mu": stats["mu"],
        "mu_star": stats["mu_star"],
        "sigma": stats["sigma"],
        "interpretation": {
            "high_mu_star_low_sigma": "influential, approximately linear/additive",
            "high_mu_star_high_sigma": "influential with nonlinearity or interactions",
            "low_mu_star": "non-influential candidate for fixing",
        },
    }


if __name__ == "__main__":
    bounds = {"a": (0.0, 1.0), "b": (0.0, 1.0), "c": (0.0, 1.0)}
    des = sample_morris_trajectories(20, list(bounds.values()), num_levels=4, seed=3)
    X = des["matrix"]
    # Linear-ish smoke model
    Y = X[:, 0] + 0.1 * X[:, 1] ** 2
    r = des["n_model_runs"] // (len(bounds) + 1)
    stats = elementary_effects(
        Y, r, len(bounds), delta_unit=des["delta_unit"], step_meta=des["step_meta"]
    )
    print("mu_star", np.round(stats["mu_star"], 4))
    print("sigma", np.round(stats["sigma"], 4))
    print("runs", des["n_model_runs"], "seal", des["seal"][:16])
