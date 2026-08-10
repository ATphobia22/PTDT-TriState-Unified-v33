"""Controlled normalization boundary for HEC-RAS river-stage results."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from .model_contracts import ExchangePayload, ModelStatus, Provenance


@dataclass(frozen=True)
class HecRasBoundary:
    stage_ft: float
    timestamp_utc: datetime
    datum: str
    river_id: str
    run_id: str
    scenario_id: str


def normalize_hec_ras_boundary(payload: dict[str, Any]) -> HecRasBoundary:
    required = ("stage_ft", "timestamp_utc", "datum", "river_id", "run_id", "scenario_id")
    missing = [key for key in required if key not in payload]
    if missing:
        raise ValueError(f"missing HEC-RAS fields: {', '.join(missing)}")
    try:
        stage = float(payload["stage_ft"])
    except (TypeError, ValueError) as exc:
        raise ValueError("stage_ft must be numeric") from exc
    if payload["datum"] != "NAVD88":
        raise ValueError("HEC-RAS exchange requires explicit NAVD88 datum")
    timestamp = payload["timestamp_utc"]
    if isinstance(timestamp, str):
        timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    if timestamp.tzinfo is None:
        raise ValueError("timestamp_utc must be timezone-aware")
    for key in ("river_id", "run_id", "scenario_id"):
        if not str(payload[key]).strip():
            raise ValueError(f"{key} must be non-empty")
    return HecRasBoundary(stage, timestamp, "NAVD88", str(payload["river_id"]), str(payload["run_id"]), str(payload["scenario_id"]))


def to_exchange_payload(boundary: HecRasBoundary) -> ExchangePayload:
    provenance = Provenance("HEC-RAS", boundary.run_id, boundary.scenario_id, boundary.timestamp_utc, "NAVD88", "ft")
    return ExchangePayload({"stage_ft": boundary.stage_ft, "river_id": boundary.river_id, "exchange_direction": "HEC-RAS_TO_MODFLOW6"}, provenance, ModelStatus.VALID)
