from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from math import isfinite
from typing import Any, Mapping

import rfc8785


@dataclass(frozen=True, slots=True)
class ClearanceManifest:
    building_id: str
    structural_use: str
    lowest_adjacent_grade_ft: float
    first_floor_elevation_ft: float
    current_water_surface_ft: float
    lowest_floor_freeboard_ft: float
    lag_submersion_delta_ft: float
    hydrostatic_threat_status: str
    engineering_threshold_ft: float
    threshold_source: str
    statutory_compliance_pass: bool
    execution_timestamp_utc: str
    manifest_seal: str


class StructuralClearanceAnalyzer:
    """Calculates physical clearance metrics without making agency determinations."""

    def __init__(self, required_freeboard_ft: float = 2.2, threshold_source: str = "configured-engineering-policy") -> None:
        if not isfinite(required_freeboard_ft) or required_freeboard_ft < 0:
            raise ValueError("required freeboard must be a finite non-negative value")
        self.required_freeboard_ft = required_freeboard_ft
        self.threshold_source = threshold_source

    @staticmethod
    def _number(record: Mapping[str, Any], key: str) -> float:
        value = float(record[key])
        if not isfinite(value):
            raise ValueError(f"{key} must be finite")
        return value

    def evaluate_node_clearance(self, building_record: Mapping[str, Any], current_wse_navd88: float) -> ClearanceManifest:
        if not isfinite(current_wse_navd88):
            raise ValueError("current WSE must be finite")
        building_id = str(building_record.get("building_id", "UNKNOWN_NODE"))
        structural_use = str(building_record.get("structural_use", "unknown"))
        lag = self._number(building_record, "lowest_adjacent_grade_ft")
        ffe = self._number(building_record, "first_floor_elevation_ft")
        freeboard = ffe - current_wse_navd88
        lag_delta = current_wse_navd88 - lag

        if freeboard <= 0.0:
            status = "CRITICAL_FIRST_FLOOR_SUBMERSION"
            compliance = False
        elif lag_delta > 0.0:
            status = "HYDROSTATIC_FOUNDATION_STRESS"
            compliance = False
        elif freeboard < self.required_freeboard_ft:
            status = "SUB_STANDARD_FREEBOARD_MARGIN"
            compliance = False
        else:
            status = "SECURE_PASS_COMPLIANT"
            compliance = True

        unsigned = {
            "building_id": building_id,
            "structural_use": structural_use,
            "lowest_adjacent_grade_ft": round(lag, 4),
            "first_floor_elevation_ft": round(ffe, 4),
            "current_water_surface_ft": round(current_wse_navd88, 4),
            "lowest_floor_freeboard_ft": round(freeboard, 4),
            "lag_submersion_delta_ft": round(lag_delta, 4),
            "hydrostatic_threat_status": status,
            "engineering_threshold_ft": self.required_freeboard_ft,
            "threshold_source": self.threshold_source,
            "statutory_compliance_pass": compliance,
        }
        seal = hashlib.sha256(rfc8785.dumps(unsigned)).hexdigest()
        return ClearanceManifest(
            **unsigned,
            execution_timestamp_utc=datetime.now(timezone.utc).isoformat(),
            manifest_seal=seal,
        )

    def as_evidence_payload(self, manifest: ClearanceManifest) -> dict[str, Any]:
        payload = asdict(manifest)
        payload["calculation_type"] = "engineering-clearance-analysis"
        payload["regulatory_determination"] = "not-established-by-this-calculator"
        return payload
