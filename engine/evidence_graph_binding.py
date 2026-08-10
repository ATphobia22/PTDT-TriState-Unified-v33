"""Bridge PTDT model exchanges into the canonical Evidence Graph."""
from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from .model_contracts import ExchangePayload, ModelStatus
from src.evidence.evidence_graph import EvidenceGraph, ProvenanceRecord


def to_evidence_input(
    exchange: ExchangePayload,
    *,
    source_record_id: str,
    parent_ids: Sequence[str] = (),
    role: str,
    authority: str,
    observed_at: str | None = None,
    spatial_ref: str | None = None,
    vertical_datum: str | None = None,
) -> dict[str, Any]:
    if not source_record_id.strip():
        raise ValueError("source_record_id must be non-empty")
    if not role.strip() or not authority.strip():
        raise ValueError("role and authority must be non-empty")
    return {
        "source": exchange.provenance.source_model,
        "source_record_id": source_record_id,
        "role": role,
        "authority": authority,
        "payload": dict(exchange.values),
        "parent_ids": tuple(sorted(parent_ids)),
        "observed_at": observed_at,
        "spatial_ref": spatial_ref,
        "vertical_datum": vertical_datum or exchange.provenance.datum,
        "units": exchange.provenance.units,
        "status": exchange.status.value,
        "run_id": exchange.provenance.run_id,
        "scenario_id": exchange.provenance.scenario_id,
        "timestamp_utc": exchange.provenance.timestamp_utc.isoformat(),
    }


def enkf_evidence_input(exchange: ExchangePayload, *, source_record_id: str, parent_ids: Sequence[str] = (), **metadata: str | None) -> dict[str, Any]:
    return to_evidence_input(exchange, source_record_id=source_record_id, parent_ids=parent_ids, role="derived-assimilation", authority="derived", **metadata)


def bishop_evidence_input(exchange: ExchangePayload, *, source_record_id: str, parent_ids: Sequence[str] = (), **metadata: str | None) -> dict[str, Any]:
    return to_evidence_input(exchange, source_record_id=source_record_id, parent_ids=parent_ids, role="slope-stability", authority="slope-stability-model", **metadata)


def publish_exchange(
    exchange: ExchangePayload,
    graph: EvidenceGraph,
    *,
    source_record_id: str,
    parent_ids: Sequence[str] = (),
    role: str,
    authority: str,
    observed_at: str | None = None,
    spatial_ref: str | None = None,
    vertical_datum: str | None = None,
) -> ProvenanceRecord:
    """Register a valid model result in the canonical graph.

    Invalid/stale/failed model outputs cannot be promoted into the authoritative
    derived-result path. Parent IDs are checked by EvidenceGraph.add_record().
    """
    if exchange.status is not ModelStatus.VALID:
        raise ValueError(f"Only VALID model exchanges may be promoted: {exchange.status.value}")
    data = to_evidence_input(
        exchange,
        source_record_id=source_record_id,
        parent_ids=parent_ids,
        role=role,
        authority=authority,
        observed_at=observed_at,
        spatial_ref=spatial_ref,
        vertical_datum=vertical_datum,
    )
    record = ProvenanceRecord.create(
        source=data["source"],
        source_record_id=data["source_record_id"],
        role=data["role"],
        authority=data["authority"],
        payload={
            **data["payload"],
            "status": data["status"],
            "run_id": data["run_id"],
            "scenario_id": data["scenario_id"],
            "timestamp_utc": data["timestamp_utc"],
        },
        observed_at=data["observed_at"],
        spatial_ref=data["spatial_ref"],
        vertical_datum=data["vertical_datum"],
        units=data["units"],
        parent_ids=data["parent_ids"],
    )
    graph.add_record(record)
    return record
