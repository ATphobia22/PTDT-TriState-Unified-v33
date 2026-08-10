from src.evidence import EvidenceGraph, ProvenanceRecord
from src.evidence.usgs_semantics import assimilated_record, observation_record


def test_parent_ids_are_required_and_hashes_verify():
    source = ProvenanceRecord.create(
        source="USGS-NWIS",
        source_record_id="site:0001:00060:2026-08-10T00:00:00Z",
        role="usgs-observation",
        authority="USGS",
        payload={"value": 10.0},
        observed_at="2026-08-10T00:00:00Z",
        vertical_datum="NAVD88",
        units="ft",
    )
    graph = EvidenceGraph()
    graph.add_record(source)
    derived = ProvenanceRecord.create(
        source="USGS-EnKF",
        source_record_id="enkf:1",
        role="derived-assimilation",
        authority="derived",
        payload={"value": 11.0},
        observed_at=source.observed_at,
        vertical_datum="NAVD88",
        units="ft",
        parent_ids=(source.provenance_id,),
    )
    graph.add_record(derived)
    assert derived.verify()
    assert derived.parent_ids == (source.provenance_id,)


def test_usgs_observation_is_not_replaced_by_assimilation():
    observation = observation_record(
        site_no="0001",
        parameter_code="00060",
        value=10.0,
        observed_at="2026-08-10T00:00:00Z",
        units="ft",
    )
    assimilation = assimilated_record(
        observation=observation,
        model_input_id="run-1",
        assimilated_value=10.5,
        method="EnKF",
        units="ft",
    )
    assert observation.record.source == "USGS-NWIS"
    assert observation.record.role == "usgs-observation"
    assert assimilation.result.source == "USGS-EnKF"
    assert assimilation.result.parent_ids == (observation.record.provenance_id,)
