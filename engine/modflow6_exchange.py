"""Controlled HEC-RAS -> MODFLOW6 exchange and groundwater promotion."""
from __future__ import annotations

from typing import Any

from .hec_ras_exchange import HecRasBoundary
from .model_contracts import ExchangePayload, ModelRunResult, ModelStatus, Provenance


def build_modflow_boundary(boundary: HecRasBoundary, target_cells: list[tuple[int, int]]) -> ExchangePayload:
    if not target_cells:
        raise ValueError("target_cells must not be empty")
    if boundary.datum != "NAVD88":
        raise ValueError("MODFLOW boundary requires NAVD88")
    provenance = Provenance("HEC-RAS", boundary.run_id, boundary.scenario_id, boundary.timestamp_utc, "NAVD88", "ft")
    return ExchangePayload(
        {"stage_ft": boundary.stage_ft, "target_cells": target_cells, "exchange_direction": "HEC-RAS_TO_MODFLOW6"},
        provenance, ModelStatus.VALID,
    )


def require_valid_result(result: ModelRunResult) -> None:
    if result.status is not ModelStatus.VALID:
        raise ValueError(f"MODFLOW6 result is not valid for promotion: {result.status.value}")
    if result.failure_class is not None:
        raise ValueError("MODFLOW6 valid result cannot contain a failure class")


def promote_groundwater_result(result: ModelRunResult, heads: dict[tuple[int, int], float]) -> ExchangePayload:
    require_valid_result(result)
    if not heads:
        raise ValueError("groundwater heads must not be empty")
    if any(not isinstance(value, (int, float)) for value in heads.values()):
        raise ValueError("groundwater heads must be numeric")
    provenance = Provenance("MODFLOW6", result.provenance.run_id, result.provenance.scenario_id, result.provenance.timestamp_utc, result.provenance.datum, "ft")
    return ExchangePayload({"heads_ft": {str(cell): float(value) for cell, value in heads.items()}, "exchange_direction": "MODFLOW6_TO_PTDT_GROUNDWATER"}, provenance, ModelStatus.VALID)
