"""Evidence-Graph-bound scalar Ensemble Kalman assimilation primitives."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from statistics import fmean
from typing import Sequence

from .authority import AuthorityDomain, assert_authorized, can_promote
from .model_contracts import ExchangePayload, ModelStatus, Provenance


@dataclass(frozen=True)
class EnKFUpdate:
    forecast: float
    observation: float
    observation_error_variance: float
    ensemble_variance: float
    kalman_gain: float
    analysis: float


def scalar_enkf_update(
    forecast: float,
    observation: float,
    ensemble_variance: float,
    observation_error_variance: float,
) -> EnKFUpdate:
    """Apply the scalar EnKF/Kalman analysis equation.

    K = P/(P+R), x_a = x_f + K(y-x_f).
    """
    if ensemble_variance < 0:
        raise ValueError("ensemble_variance must be non-negative")
    if observation_error_variance <= 0:
        raise ValueError("observation_error_variance must be positive")
    denominator = ensemble_variance + observation_error_variance
    gain = ensemble_variance / denominator
    analysis = forecast + gain * (observation - forecast)
    return EnKFUpdate(
        forecast=forecast,
        observation=observation,
        observation_error_variance=observation_error_variance,
        ensemble_variance=ensemble_variance,
        kalman_gain=gain,
        analysis=analysis,
    )


def ensemble_variance(ensemble: Sequence[float]) -> float:
    """Return the unbiased sample variance used for scalar ensemble spread."""
    if len(ensemble) < 2:
        raise ValueError("ensemble must contain at least two members")
    mean = fmean(ensemble)
    return sum((value - mean) ** 2 for value in ensemble) / (len(ensemble) - 1)


def assimilate_to_exchange(
    *,
    forecast: float,
    observation: float,
    observation_error_variance: float,
    ensemble: Sequence[float],
    provenance: Provenance,
    datum: str,
    units: str,
) -> ExchangePayload:
    """Create an authoritative ASSIMILATION exchange payload from an EnKF update."""
    assert_authorized("EnKF", AuthorityDomain.ASSIMILATION)
    if provenance.source_model != "EnKF":
        raise ValueError("EnKF payload provenance must identify EnKF as source_model")
    if provenance.datum != datum or provenance.units != units:
        raise ValueError("payload datum/units must match provenance")
    update = scalar_enkf_update(
        forecast,
        observation,
        ensemble_variance(ensemble),
        observation_error_variance,
    )
    if not can_promote(ModelStatus.VALID, AuthorityDomain.ASSIMILATION):
        raise PermissionError("EnKF cannot promote into ASSIMILATION")
    return ExchangePayload(
        values={
            "forecast": update.forecast,
            "observation": update.observation,
            "ensemble_variance": update.ensemble_variance,
            "observation_error_variance": update.observation_error_variance,
            "kalman_gain": update.kalman_gain,
            "analysis": update.analysis,
        },
        provenance=provenance,
        status=ModelStatus.VALID,
    )


def new_provenance(run_id: str, scenario_id: str, datum: str, units: str) -> Provenance:
    """Convenience constructor for UTC Evidence Graph provenance."""
    return Provenance("EnKF", run_id, scenario_id, datetime.now(timezone.utc), datum, units)
