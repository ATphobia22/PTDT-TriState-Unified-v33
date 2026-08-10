from datetime import datetime, timezone

from engine.evidence_graph_binding import bishop_evidence_input, enkf_evidence_input
from engine.model_contracts import ExchangePayload, ModelStatus, Provenance


def test_enkf_binding_matches_authoritative_graph_semantics() -> None:
    exchange = ExchangePayload(
        values={"analysis": 13.0, "kalman_gain": 0.75},
        provenance=Provenance("EnKF", "run-1", "scenario-1", datetime(2026, 8, 10, tzinfo=timezone.utc), "NAVD88", "ft"),
        status=ModelStatus.VALID,
    )
    bound = enkf_evidence_input(exchange, source_record_id="run-1:scenario-1", parent_ids=("prov-usgs",))
    assert bound["source"] == "EnKF"
    assert bound["role"] == "derived-assimilation"
    assert bound["authority"] == "derived"
    assert bound["parent_ids"] == ("prov-usgs",)
    assert bound["units"] == "ft"
    assert bound["status"] == "VALID"


def test_bishop_binding_preserves_parent_lineage() -> None:
    exchange = ExchangePayload(
        values={"factor_of_safety": 1.42, "converged": True},
        provenance=Provenance("Bishop", "run-2", "scenario-1", datetime(2026, 8, 10, tzinfo=timezone.utc), "NAVD88", "dimensionless"),
        status=ModelStatus.VALID,
    )
    bound = bishop_evidence_input(exchange, source_record_id="bishop:run-2", parent_ids=("prov-ras", "prov-geotech"))
    assert bound["source"] == "Bishop"
    assert bound["role"] == "slope-stability"
    assert bound["authority"] == "slope-stability-model"
    assert bound["parent_ids"] == ("prov-geotech", "prov-ras")
