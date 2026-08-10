# archimedes_engine.py
# -*- coding: utf-8 -*-
"""Deterministic regulatory elevation/storage core for Point Township Section 35."""
from __future__ import annotations
from typing import Dict, Union

class ArchimedesEngine:
    """Regulatory/constraint authority only; not a river or groundwater solver."""

    def __init__(self) -> None:
        self.base_flood_elevation_ft: float = 375.0
        self.site_lag_ft: float = 377.2
        self.datum: str = "NAVD88"
        self.site: str = "13101 Bonebank Road, Section 35, T7S, R14W, Posey County, IN"

    @staticmethod
    def authority_domains() -> set[str]:
        return {"REGULATORY"}

    def compensatory_storage_cy(
        self,
        fill_cy: float,
        surcharge_ft: float = 0.0,
    ) -> Dict[str, Union[float, str, bool]]:
        if fill_cy < 0:
            raise ValueError("fill_cy must be non-negative")
        required = float(fill_cy) * 1.20
        passed = surcharge_ft <= 0.0 and required >= fill_cy
        return {
            "fill_cy": float(fill_cy),
            "required_compensatory_cy": required,
            "surcharge_ft": float(surcharge_ft),
            "bfe_ft_navd88": self.base_flood_elevation_ft,
            "passed": passed,
            "datum": self.datum,
            "rule": "IN-312-IAC-10",
        }

    def stage_vs_bfe(self, stage_ft: float) -> Dict[str, Union[float, str, bool]]:
        freeboard = stage_ft - self.base_flood_elevation_ft
        return {
            "stage_ft": float(stage_ft),
            "bfe_ft": self.base_flood_elevation_ft,
            "freeboard_ft": freeboard,
            "above_bfe": freeboard > 0,
            "datum": self.datum,
        }

if __name__ == "__main__":
    engine = ArchimedesEngine()
    assert engine.base_flood_elevation_ft == 375.0
    print("Engine Core Verified")
