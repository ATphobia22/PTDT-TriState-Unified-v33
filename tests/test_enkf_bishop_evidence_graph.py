from datetime import datetime, timezone

import pytest

from engine.authority import AuthorityDomain, assert_authorized, can_promote
from engine.bishop_slope import BishopSlice, bishop_to_exchange, simplified_bishop_factor_of_safety
from engine.enkf_fusion import assimilate_to_exchange, scalar_enkf_update
from engine.model_contracts import ModelStatus, Provenance


def test_enkf_scalar_update_matches_contract_equation():
    update = scalar_enkf_update(10.0, 14.0, 9.0, 3.0)
    assert update.kalman_gain == pytest.approx(0.75)
    assert update.analysis == pytest.approx(13.0)


def test_enkf_exchange_preserves_evidence_graph_provenance():
    provenance = Provenance("EnKF", "enkf-001", "base", datetime.now(timezone.utc), "NAVD88", "ft")
    payload = assimilate_to_exchange(
        forecast=10.0,
        observation=14.0,
        observation_error_variance=3.0,
        ensemble=[7.0, 9.0, 10.0, 12.0, 12.0],
        provenance=provenance,
        datum="NAVD88",
        units="ft",
    )
    assert payload.status is ModelStatus.VALID
    assert payload.provenance == provenance
    assert payload.values["kalman_gain"] == pytest.approx(4.5 / 7.5)


def test_enkf_rejects_non_authoritative_provenance():
    provenance = Provenance("PTDT", "run-001", "base", datetime.now(timezone.utc), "NAVD88", "ft")
    with pytest.raises(ValueError, match="source_model"):
        assimilate_to_exchange(
            forecast=1.0,
            observation=2.0,
            observation_error_variance=1.0,
            ensemble=[0.0, 1.0, 2.0],
            provenance=provenance,
            datum="NAVD88",
            units="ft",
        )


def test_bishop_iterates_to_convergence():
    slices = [
        BishopSlice(100.0, 5.0, 12.0, 8.0, 28.0, 2.0),
        BishopSlice(110.0, 5.0, 18.0, 8.0, 28.0, 2.0),
        BishopSlice(90.0, 5.0, 24.0, 8.0, 28.0, 2.0),
    ]
    result = simplified_bishop_factor_of_safety(slices)
    assert result.converged
    assert result.iterations < 100
    assert result.factor_of_safety > 0


def test_bishop_exchange_uses_slope_stability_authority():
    assert_authorized("Bishop", AuthorityDomain.SLOPE_STABILITY)
    provenance = Provenance("Bishop", "bishop-001", "base", datetime.now(timezone.utc), "NAVD88", "dimensionless")
    payload = bishop_to_exchange(
        slices=[BishopSlice(100.0, 5.0, 12.0, 8.0, 28.0, 2.0)],
        provenance=provenance,
        datum="NAVD88",
        units="dimensionless",
    )
    assert payload.status is ModelStatus.VALID
    assert payload.provenance.source_model == "Bishop"
    assert can_promote(payload.status, AuthorityDomain.SLOPE_STABILITY)


def test_bishop_rejects_ptdt_provenance():
    provenance = Provenance("PTDT", "run-001", "base", datetime.now(timezone.utc), "NAVD88", "dimensionless")
    with pytest.raises(ValueError, match="source_model"):
        bishop_to_exchange(
            slices=[BishopSlice(100.0, 5.0, 12.0, 8.0, 28.0)],
            provenance=provenance,
            datum="NAVD88",
            units="dimensionless",
        )
