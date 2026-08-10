from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Mapping

from .evidence_graph import ProvenanceRecord, sha256_json


@dataclass(frozen=True)
class ArchimedesCalculation:
    calculation_id: str
    engine: str
    engine_version: str
    inputs: ProvenanceRecord
    outputs: ProvenanceRecord
    input_sha256: str
    output_sha256: str


class ArchimedesAuthority:
    ENGINE = "archimedes"
    ENGINE_VERSION = "external-authoritative-core"

    def __init__(self, engine: Any) -> None:
        self.engine = engine

    def calculate(self, *, input_record: ProvenanceRecord, operation: str, **kwargs: Any) -> ArchimedesCalculation:
        if input_record.role not in {"terrain", "hydraulics", "ras", "usgs-observation", "postgis", "engineering-input"}:
            raise ValueError(f"Unsupported Archimedes input role: {input_record.role}")
        input_payload = {"operation": operation, "record": input_record.payload, "kwargs": kwargs}
        input_hash = sha256_json(input_payload)
        operation_fn = getattr(self.engine, operation, None)
        if operation_fn is None or not callable(operation_fn):
            raise AttributeError(f"Archimedes operation is not exposed: {operation}")
        output = operation_fn(**kwargs)
        if not isinstance(output, Mapping):
            output = {"value": output}
        output_payload: Dict[str, Any] = {"operation": operation, "result": dict(output), "input_sha256": input_hash}
        output_record = ProvenanceRecord.create(
            source="archimedes",
            source_record_id=operation,
            role="archimedes-output",
            authority="archimedes",
            payload=output_payload,
            spatial_ref=input_record.spatial_ref,
            vertical_datum=input_record.vertical_datum,
            units=input_record.units,
            parent_ids=(input_record.provenance_id,),
        )
        calculation_id = "calc-" + sha256_json({
            "engine": self.ENGINE,
            "version": self.ENGINE_VERSION,
            "input": input_record.provenance_id,
            "output": output_record.provenance_id,
        })
        return ArchimedesCalculation(
            calculation_id=calculation_id,
            engine=self.ENGINE,
            engine_version=self.ENGINE_VERSION,
            inputs=input_record,
            outputs=output_record,
            input_sha256=input_hash,
            output_sha256=output_record.payload_sha256,
        )

    @staticmethod
    def serialize(calculation: ArchimedesCalculation) -> Dict[str, Any]:
        return asdict(calculation)
