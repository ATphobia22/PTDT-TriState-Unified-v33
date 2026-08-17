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

# Optional SciPy QMC (preferred when available)
try:
    from scipy.stats import qmc as _scipy_qmc

    _HAS_SCIPY_QMC = True
except ImportError:
    _HAS_SCIPY_QMC = False

SCHEMA_VERSION: Final[int] = 1


def _next_power_of_two(n: int) -> int:
    if n <= 1:
        return 1
    return 1 << (n - 1).bit_length()


def _direction_numbers(dim: int, bits: int = 32) -> list[list[int]]:
    """
    Minimal direction numbers for low dimension Sobol' (Joe-Kuo style subset).
    Sufficient for typical hydraulic GSA factor counts (≤ 20).
    For production high-D prefer scipy.stats.qmc.Sobol.
    """
    # Primitive polynomials and initial direction numbers (standard small set)
    # dim 0 is special-cased as van der Corput binary.
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
    # Dimension 0
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
    """Generate n×dim points in [0,1)^dim (unscrambled, deterministic)."""
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
    """
    Draw n samples of dimension dim in the unit hypercube [0, 1)^dim.

    Prefers scipy.stats.qmc.Sobol when available; otherwise uses a bounded
    pure-Python/NumPy fallback (dim ≤ 20).
    """
    if n < 1 or dim < 1:
        raise ValueError("n and dim must be ≥ 1")
    if _HAS_SCIPY_QMC:
        engine = _scipy_qmc.Sobol(d=dim, scramble=scramble, seed=seed)
        if skip > 0:
            engine.fast_forward(skip)
        # Prefer power-of-two draws for best balance; still return exactly n
        m = max(1, int(math.ceil(math.log2(max(n, 2)))))
        pts = engine.random_base2(m=m)
        return np.asarray(pts[:n], dtype=np.float64)
    if scramble and seed is not None:
        # Lightweight deterministic scramble of fallback points
        rng = np.random.default_rng(seed)
        shifts = rng.random(dim)
        base = _sobol_unit_fallback(n, dim, skip=skip)
        return (base + shifts) % 1.0
    return _sobol_unit_fallback(n, dim, skip=skip)


def scale_to_bounds(
    unit_samples: np.ndarray,
    bounds: Sequence[tuple[float, float]],
) -> np.ndarray:
    """Map unit-hypercube samples to [low, high] per dimension."""
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
    Build a Saltelli-style sample matrix for Sobol' index estimation.

    Rows = N*(D+2) if calc_second_order is False, else N*(2D+2).
    Columns = D (one per parameter).

    This matrix is intended for model evaluation Y = f(X); analysis of Y
    yields first/total (and optional second-order) Sobol' indices.
    """
    d = len(bounds)
    if d < 1:
        raise ValueError("at least one parameter bound required")
    # Saltelli needs 2D columns of unit Sobol, then A/B and cross matrices
    unit = sobol_unit_samples(
        n_base,
        2 * d,
        seed=seed,
        scramble=scramble,
        skip=1,  # skip origin for numerical stability with some transforms
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
    return scale_to_bounds(mat_unit, bounds)


def seal_sample_matrix(matrix: np.ndarray, meta: Mapping[str, Any] | None = None) -> str:
    """SHA-256 over canonical JSON of rounded samples + metadata (evidence)."""
    payload = {
        "schema_version": SCHEMA_VERSION,
        "shape": list(matrix.shape),
        "samples": np.round(matrix, decimals=12).tolist(),
        "meta": dict(meta or {}),
    }
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256(raw.encode("utf-8")).hexdigest()


def default_hydraulic_gsa_bounds() -> dict[str, tuple[float, float]]:
    """
    Example factor bounds for PTDT / HEC-RAS 2D GSA (illustrative only).
    Operator must replace with calibrated study ranges; values are not regulatory.
    """
    return {
        "manning_channel": (0.025, 0.045),
        "manning_floodplain": (0.04, 0.12),
        "mesh_cell_ft": (25.0, 200.0),
        "dem_cell_m": (1.0, 10.0),
        "upstream_peak_scale": (0.85, 1.15),
    }


def generate_gsa_design(
    n_base: int = 64,
    bounds: Mapping[str, tuple[float, float]] | None = None,
    *,
    seed: int = 42,
    calc_second_order: bool = False,
) -> dict[str, Any]:
    """
    Convenience: named parameters → sealed Saltelli design for RAS batch runs.
    """
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
    }


if __name__ == "__main__":
    design = generate_gsa_design(n_base=16, seed=7)
    print(f"status={design['status']} rows={design['n_rows']} seal={design['seal'][:16]}…")
    print("parameters:", design["parameter_names"])
