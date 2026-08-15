"""LOMA / LOMR-F affidavit gate — fail-closed dependency + APN dual-ID (Rule 6)."""
from __future__ import annotations

import hashlib
import json
import os
from typing import Any


class LomaAffidavitGate:
    """Final regulatory checks before affidavit packaging.

    Natural-grade clearance (LAG >= BFE, no fill) is **LOMA** path.
    **LOMR-F** is only appropriate when fill raised the grade.
    """

    def __init__(self) -> None:
        self.BFE_FT = 375.0
        self.LAG_FT = 377.2
        self.FFE_FT = 382.5
        self.dem_cog_path = "data/cog/bonebank_dem_navd88.tif"
        self.bafm_shp_path = "data/bafl/posey/FloodHazard_BestAvai_DNR_Water.shp"
        self.ras_hdf_path = "data/ras/PointTownship.p01.hdf"

    def verify_apn_dual_id(self, internal_apn: str, county_assessor_apn: str) -> str:
        """Rule 6: UNVERIFIED_DUAL until internal matches Posey assessor APN."""
        if internal_apn != county_assessor_apn:
            return "UNVERIFIED_DUAL"
        if not county_assessor_apn.startswith("65-"):
            return "UNVERIFIED_DUAL"
        return "VERIFIED"

    def verify_natural_loma_eligibility(self) -> bool:
        """FEMA LOMA (natural grade): LAG >= BFE."""
        return self.LAG_FT >= self.BFE_FT

    def verify_dependencies_on_disk(self) -> list[str]:
        missing: list[str] = []
        if not os.path.exists(self.dem_cog_path):
            missing.append("SEALED_COG_MISSING")
        if not os.path.exists(self.bafm_shp_path):
            missing.append("BAFL_SHP_MISSING")
        if not os.path.exists(self.ras_hdf_path):
            missing.append("LICENSED_RAS_HDF_MISSING")
        return missing

    def generate_affidavit_payload(
        self,
        internal_apn: str,
        county_assessor_apn: str,
        *,
        fill_present: bool = False,
    ) -> dict[str, Any]:
        missing_deps = self.verify_dependencies_on_disk()
        if missing_deps:
            return {
                "status": "SOFT_FAIL_DEPENDENCY",
                "reason": f"Missing regulatory files: {', '.join(missing_deps)}",
                "seal": None,
            }

        apn_status = self.verify_apn_dual_id(internal_apn, county_assessor_apn)
        if apn_status == "UNVERIFIED_DUAL":
            return {
                "status": "BLOCKED",
                "reason": "APN UNVERIFIED_DUAL: Assessor record does not match internal record.",
                "seal": None,
            }

        if not self.verify_natural_loma_eligibility():
            return {
                "status": "BLOCKED",
                "reason": f"Elevation gate denied: LAG ({self.LAG_FT}) < BFE ({self.BFE_FT}).",
                "seal": None,
            }

        product = "LOMR-F" if fill_present else "LOMA"
        payload = {
            "apn_verified": county_assessor_apn,
            "bfe_navd88_ft": self.BFE_FT,
            "lag_navd88_ft": self.LAG_FT,
            "ffe_navd88_ft": self.FFE_FT,
            "crs": "EPSG:2966",
            "vertical_datum": "NAVD88",
            "eligibility": f"{product} elevation-eligible (survey still required)",
            "fill_present": fill_present,
            "easement_note": "IC 36-9-27-33 75ft regulated-drain ROW must be cleared separately",
        }
        seal = hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        return {"status": "APPROVED", "payload": payload, "seal": seal}


if __name__ == "__main__":
    gate = LomaAffidavitGate()
    print("Test dual APN:", gate.generate_affidavit_payload("65-09-35-000-001", "65-19-08-000-001"))
    print("Test match (expect soft-fail without files):", gate.generate_affidavit_payload("65-19-08-000-001", "65-19-08-000-001"))
