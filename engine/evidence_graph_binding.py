"""Adapter contract for publishing PTDT model exchanges to the authoritative Evidence Graph.

The authoritative graph implementation lives in Tri-County-River-Valley-Digital-Twin.
This module deliberately does not duplicate graph hashing or storage; it produces the
field contract consumed by that repository's PTDTExchangeAdapter.
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from .model_contracts import ExchangePayload


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
    """Translate a valid PTDT exchange into the authoritative graph adapter schema."""
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
    return to_evidence_input(
        exchange,
        source_record_id=source_record_id,
        parent_ids=parent_ids,
        role="derived-assimilation",
        authority="derived",
        **metadata,
    )


def bishop_evidence_input(exchange: ExchangePayload, *, source_record_id: str, parent_ids: Sequence[str] = (), **metadata: str | None) -> dict[str, Any]:
    return to_evidence_input(
        exchange,
        source_record_id=source_record_id,
        parent_ids=parent_ids,
        role="slope-stability",
        authority="slope-stability-model",
        **metadata,
    )
