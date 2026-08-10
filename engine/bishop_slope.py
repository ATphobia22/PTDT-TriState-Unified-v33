"""Evidence-Graph-bound simplified Bishop circular-slip stability solver."""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timezone

from .authority import AuthorityDomain, assert_authorized, can_promote
from .model_contracts import ExchangePayload, ModelStatus, Provenance


@dataclass(frozen=True)
class BishopSlice:
    weight_kn: float
    base_length_m: float
    alpha_deg: float
    cohesion_kpa: float
    friction_deg: float
    pore_pressure_kpa: float = 0.0


@dataclass(frozen=True)
class BishopResult:
    factor_of_safety: float
    iterations: int
    converged: bool


def simplified_bishop_factor_of_safety(
    slices: list[BishopSlice],
    *,
    initial_fs: float = 1.5,
    tolerance: float = 1e-6,
    max_iterations: int = 100,
) -> BishopResult:
    """Solve the Simplified Bishop equation iteratively for circular slip.

    The formulation follows the USACE simplified Bishop method: interslice
    forces are taken as horizontal, vertical force equilibrium and overall
    moment equilibrium are satisfied, and FS occurs on both sides of the
    equation, requiring iteration.
    """
    if not slices:
        raise ValueError("at least one slice is required")
    if initial_fs <= 0 or tolerance <= 0 or max_iterations < 1:
        raise ValueError("invalid Bishop iteration controls")

    fs = initial_fs
    for iteration in range(1, max_iterations + 1):
        numerator = 0.0
        denominator = 0.0
        for slc in slices:
            alpha = math.radians(slc.alpha_deg)
            phi = math.radians(slc.friction_deg)
            m_alpha = math.cos(alpha) + math.sin(alpha) * math.tan(phi) / fs
            if abs(m_alpha) < 1e-12:
                raise ValueError("Bishop m_alpha is singular")
            effective_normal_term = slc.weight_kn - slc.pore_pressure_kpa * slc.base_length_m
            numerator += (
                slc.cohesion_kpa * slc.base_length_m
                + effective_normal_term * math.tan(phi)
            ) / m_alpha
            denominator += slc.weight_kn * math.sin(alpha)
        if denominator <= 0:
            raise ValueError("Bishop driving force must be positive")
        next_fs = numerator / denominator
        if not math.isfinite(next_fs) or next_fs <= 0:
            raise ValueError("Bishop produced a non-positive or non-finite factor of safety")
        if abs(next_fs - fs) <= tolerance:
            return BishopResult(next_fs, iteration, True)
        fs = next_fs
    return BishopResult(fs, max_iterations, False)


def bishop_to_exchange(
    *,
    slices: list[BishopSlice],
    provenance: Provenance,
    datum: str,
    units: str,
) -> ExchangePayload:
    """Create an authoritative SLOPE_STABILITY exchange for downstream display."""
    assert_authorized("Bishop", AuthorityDomain.SLOPE_STABILITY)
    if provenance.source_model != "Bishop":
        raise ValueError("Bishop payload provenance must identify Bishop as source_model")
    if provenance.datum != datum or provenance.units != units:
        raise ValueError("payload datum/units must match provenance")
    result = simplified_bishop_factor_of_safety(slices)
    status = ModelStatus.VALID if result.converged else ModelStatus.INVALID
    if status is ModelStatus.VALID and not can_promote(status, AuthorityDomain.SLOPE_STABILITY):
        raise PermissionError("Bishop cannot promote into SLOPE_STABILITY")
    return ExchangePayload(
        values={
            "factor_of_safety": result.factor_of_safety,
            "iterations": result.iterations,
            "converged": result.converged,
        },
        provenance=provenance,
        status=status,
    )


def new_provenance(run_id: str, scenario_id: str, datum: str, units: str) -> Provenance:
    return Provenance("Bishop", run_id, scenario_id, datetime.now(timezone.utc), datum, units)
