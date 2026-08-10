from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .evidence_graph import ProvenanceRecord


@dataclass(frozen=True)
class USGSObservation:
    record: ProvenanceRecord
    provisional: bool


@dataclass(frozen=True)
class AssimilatedValue:
    observation_id: str
    model_input_id: str
    result: ProvenanceRecord


def observation_record(
    *,
    site_no: str,
    parameter_code: str,
    value: float,
    observed_at: str,
    provisional: bool = True,
    units: str | None = None,
) -> USGSObservation:
    payload: Mapping[str, Any] = {
        "site_no": site_no,
        "parameter_code": parameter_code,
        "value": value,
        "quality": "provisional" if provisional else "final",
    }
    record = ProvenanceRecord.create(
        source="USGS-NWIS",
        source_record_id=f"{site_no}:{parameter_code}:{observed_at}",
        role="usgs-observation",
        authority="USGS",
        payload=payload,
        observed_at=observed_at,
        units=units,
    )
    return USGSObservation(record=record, provisional=provisional)


def assimilated_record(
    *,
    observation: USGSObservation,
    model_input_id: str,
    assimilated_value: float,
    method: str,
    units: str | None = None,
) -> AssimilatedValue:
    payload = {
        "observation_id": observation.record.provenance_id,
        "model_input_id": model_input_id,
        "method": method,
        "assimilated_value": assimilated_value,
        "source_quality": "provisional" if observation.provisional else "final",
    }
    result = ProvenanceRecord.create(
        source="USGS-EnKF",
        source_record_id=f"assimilation:{observation.record.provenance_id}",
        role="derived-assimilation",
        authority="derived",
        payload=payload,
        observed_at=observation.record.observed_at,
        units=units,
        parent_ids=(observation.record.provenance_id,),
    )
    return AssimilatedValue(
        observation_id=observation.record.provenance_id,
        model_input_id=model_input_id,
        result=result,
    )
