"""
PTDT Sobol sequence sampling for global sensitivity analysis (GSA).

Produces low-discrepancy quasi-Monte-Carlo samples suitable for Sobol'
first/total-order index estimation (Saltelli design when n_params known).

Hard rules:
- Deterministic given seed
- Explicit finite bounds only
- No fabricated hydraulic results — samples parameter space only
- SHA-256 seal over canonical sample matrix for evidence packages
"""
from __future__ import annotations

from hashlib import sha256
from typing import Any, Final, Mapping, Sequence

import json
import math

try:
    import numpy as np
except ImportError as exc:  # pragma: no cover
    raise ImportError("numpy is required for sobol_sampler") from exc

try:
    from scipy.stats import qmc as _scipy_qmc

    _HAS_SCIPY_QMC = True
except ImportError:
    _HAS_SCIPY_QMC = False

SCHEMA_VERSION: Final[int] = 1


def saltelli_n_model_runs(n_base: int, n_params: int, *, calc_second_order: bool = False) -> int:
    """
    Total model evaluations required by a Saltelli design.

    First + total order only:  N * (D + 2)
    With second-order pairs:   N * (2*D + 2)

    N = n_base (base Sobol sample size; prefer power of 2 for balance).
    D = n_params.
    """
    if n_base < 1 or n_params < 1:
        raise ValueError("n_base and n_params must be ≥ 1")
    if calc_second_order:
        return int(n_base * (2 * n_params + 2))
    return int(n_base * (n_params + 2))


def _direction_numbers(dim: int, bits: int = 32) -> list[list[int]]:
    """Minimal direction numbers for low-dimension Sobol' fallback (≤20 dims)."""
    poly = [1, 3, 7, 11, 13, 19, 25, 37, 59, 47, 61, 55, 41, 67, 97, 91, 109, 103, 115, 131]
    m_init: list[list[int]] = [
        [1],
        [1, 3],
        [1, 3, 1],
        [1, 1, 1],
        [1, 1, 3, 3],
        [1, 3, 5, 13],
        [1, 1, 5, 5, 17],
        [1, 1, 5, 5, 5],
        [1, 1, 7, 11, 19],
        [1, 1, 5, 1, 1],
        [1, 1, 1, 3, 11],
        [1, 3, 5, 5, 31],
        [1, 3, 3, 9, 7],
        [1, 5, 1, 15, 7, 11],
        [1, 1, 3, 13],
        [1, 1, 7, 13, 3],
        [1, 1, 7, 1, 9],
        [1, 1, 11, 1, 5],
        [1, 1, 1, 3, 13],
    ]
    if dim > len(m_init) + 1:
        raise ValueError(
            f"Fallback Sobol supports dim ≤ {len(m_init) + 1}; install scipy for higher D"
        )
    directions: list[list[int]] = []
    d0 = [1 << (bits - 1 - k) for k in range(bits)]
    directions.append(d0)
    for j in range(1, dim):
        m = list(m_init[j - 1])
        degree = int(math.floor(math.log2(poly[j]))) if poly[j] > 1 else 1
        while len(m) < bits:
            i = len(m)
            term = m[i - degree] ^ (m[i - degree] >> degree)
            for k in range(1, degree):
                if (poly[j] >> (degree - k)) & 1:
                    term ^= m[i - k]
            m.append(term)
        directions.append([m[k] << (bits - 1 - k) for k in range(bits)])
    return directions


def _sobol_unit_fallback(n: int, dim: int, skip: int = 0) -> np.ndarray:
    bits = 32
    directions = _direction_numbers(dim, bits)
    out = np.zeros((n, dim), dtype=np.float64)
    for i in range(skip, skip + n):
        x = np.zeros(dim, dtype=np.float64)
        for d in range(dim):
            val = 0
            for b in range(bits):
                if (i >> b) & 1:
                    val ^= directions[d][b]
            x[d] = val / (1 << bits)
        out[i - skip] = x
    return out


def sobol_unit_samples(
    n: int,
    dim: int,
    *,
    seed: int | None = 0,
    scramble: bool = True,
    skip: int = 0,
) -> np.ndarray:
    """Draw n samples of dimension dim in [0, 1)^dim."""
    if n < 1 or dim < 1:
        raise ValueError("n and dim must be ≥ 1")
    if _HAS_SCIPY_QMC:
        engine = _scipy_qmc.Sobol(d=dim, scramble=scramble, seed=seed)
        if skip > 0:
            engine.fast_forward(skip)
        m = max(1, int(math.ceil(math.log2(max(n, 2)))))
        pts = engine.random_base2(m=m)
        return np.asarray(pts[:n], dtype=np.float64)
    if scramble and seed is not None:
        rng = np.random.default_rng(seed)
        shifts = rng.random(dim)
        base = _sobol_unit_fallback(n, dim, skip=skip)
        return (base + shifts) % 1.0
    return _sobol_unit_fallback(n, dim, skip=skip)


def scale_to_bounds(
    unit_samples: np.ndarray,
    bounds: Sequence[tuple[float, float]],
) -> np.ndarray:
    unit = np.asarray(unit_samples, dtype=np.float64)
    if unit.ndim != 2:
        raise ValueError("unit_samples must be 2-D (n, dim)")
    if len(bounds) != unit.shape[1]:
        raise ValueError("bounds length must equal sample dimension")
    out = np.empty_like(unit)
    for j, (lo, hi) in enumerate(bounds):
        if not (math.isfinite(lo) and math.isfinite(hi)) or hi < lo:
            raise ValueError(f"invalid bounds at dim {j}: {(lo, hi)}")
        out[:, j] = lo + unit[:, j] * (hi - lo)
    return out


def saltelli_sample_matrix(
    n_base: int,
    bounds: Sequence[tuple[float, float]],
    *,
    seed: int | None = 0,
    calc_second_order: bool = False,
    scramble: bool = True,
) -> np.ndarray:
    """
    Saltelli-style sample matrix.

    Rows = saltelli_n_model_runs(n_base, D, calc_second_order=...)
    Columns = D.
    """
    d = len(bounds)
    if d < 1:
        raise ValueError("at least one parameter bound required")
    unit = sobol_unit_samples(
        n_base,
        2 * d,
        seed=seed,
        scramble=scramble,
        skip=1,
    )
    a = unit[:, :d]
    b = unit[:, d:]
    rows: list[np.ndarray] = [a, b]
    for i in range(d):
        ab_i = a.copy()
        ab_i[:, i] = b[:, i]
        rows.append(ab_i)
    if calc_second_order:
        for i in range(d):
            ba_i = b.copy()
            ba_i[:, i] = a[:, i]
            rows.append(ba_i)
    mat_unit = np.vstack(rows)
    expected = saltelli_n_model_runs(n_base, d, calc_second_order=calc_second_order)
    if mat_unit.shape[0] != expected:
        raise RuntimeError(f"row count {mat_unit.shape[0]} != expected {expected}")
    return scale_to_bounds(mat_unit, bounds)


def seal_sample_matrix(matrix: np.ndarray, meta: Mapping[str, Any] | None = None) -> str:
    payload = {
        "schema_version": SCHEMA_VERSION,
        "shape": list(matrix.shape),
        "samples": np.round(matrix, decimals=12).tolist(),
        "meta": dict(meta or {}),
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256(raw.encode("utf-8")).hexdigest()


def default_hydraulic_gsa_bounds() -> dict[str, tuple[float, float]]:
    """Illustrative only — replace with calibrated study ranges."""
    return {
        "manning_channel": (0.025, 0.045),
        "manning_floodplain": (0.04, 0.12),
        "mesh_cell_ft": (25.0, 200.0),
        "dem_cell_m": (1.0, 10.0),
        "upstream_peak_scale": (0.85, 1.15),
    }


def problem_dict_from_bounds(bounds: Mapping[str, tuple[float, float]]) -> dict[str, Any]:
    """SALib-compatible problem definition."""
    names = list(bounds.keys())
    return {
        "num_vars": len(names),
        "names": names,
        "bounds": [list(bounds[n]) for n in names],
    }


def generate_gsa_design(
    n_base: int = 64,
    bounds: Mapping[str, tuple[float, float]] | None = None,
    *,
    seed: int = 42,
    calc_second_order: bool = False,
) -> dict[str, Any]:
    bmap = dict(bounds or default_hydraulic_gsa_bounds())
    names = list(bmap.keys())
    bound_list = [bmap[k] for k in names]
    matrix = saltelli_sample_matrix(
        n_base,
        bound_list,
        seed=seed,
        calc_second_order=calc_second_order,
    )
    meta = {
        "parameter_names": names,
        "n_base": n_base,
        "seed": seed,
        "calc_second_order": calc_second_order,
        "n_model_runs": saltelli_n_model_runs(
            n_base, len(names), calc_second_order=calc_second_order
        ),
        "scipy_qmc": _HAS_SCIPY_QMC,
    }
    digest = seal_sample_matrix(matrix, meta)
    return {
        "status": "OK",
        "parameter_names": names,
        "matrix": matrix,
        "n_rows": int(matrix.shape[0]),
        "n_cols": int(matrix.shape[1]),
        "seal": digest,
        "meta": meta,
        "problem": problem_dict_from_bounds(bmap),
    }


if __name__ == "__main__":
    design = generate_gsa_design(n_base=16, seed=7)
    print(
        f"status={design['status']} rows={design['n_rows']} "
        f"n_model_runs={design['meta']['n_model_runs']} seal={design['seal'][:16]}…"
    )
    print("parameters:", design["parameter_names"])
