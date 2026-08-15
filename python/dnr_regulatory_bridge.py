"""
PTDT: IDNR BAFL + elevation points bridge.
Hard rules: soft-fail missing shp; EPSG:2966 horizontal; SHA-256 seal on attributes;
no fabricated geometry; do not average conflicting WSELs.
Expected native shp CRS: EPSG:26916 (Posey county extract metadata).
"""
from __future__ import annotations

import hashlib
import json
import os
from typing import Any

import geopandas as gpd
import pandas as pd

TARGET_CRS = "EPSG:2966"  # NAD83 / Indiana West (US ft) — PTDT Rule 14


class DnrRegulatoryBridge:
    def __init__(self, data_dir: str = "data/bafl/posey") -> None:
        self.data_dir = data_dir
        self.target_crs = TARGET_CRS
        self.bafm_shp_path = os.path.join(data_dir, "FloodHazard_BestAvai_DNR_Water.shp")
        self.pts_shp_path = os.path.join(data_dir, "Flood_Elevation_Pts_DNR_Water.shp")

    def ingest_bafm_polygons(self) -> dict[str, Any]:
        if not os.path.exists(self.bafm_shp_path):
            return self._soft_fail(f"Missing BAFM shapefile at {self.bafm_shp_path}")
        try:
            gdf = gpd.read_file(self.bafm_shp_path)
            if gdf.crs is None:
                return self._soft_fail("BAFM shapefile has no CRS; refuse implicit assumption")
            src = gdf.crs.to_string()
            if src != self.target_crs:
                gdf = gdf.to_crs(self.target_crs)

            # Normalize field names (shapefile often lower/upper mixed)
            gdf.columns = [c.lower() for c in gdf.columns]

            attrs = pd.DataFrame(gdf.drop(columns="geometry", errors="ignore"))
            payload = attrs.to_json(orient="records", date_format="iso")
            seal = hashlib.sha256(payload.encode("utf-8")).hexdigest()

            # Presentation GeoJSON in 4326 for MapLibre (engineering stays 2966)
            gdf_4326 = gdf.to_crs("EPSG:4326")
            return {
                "status": "OK",
                "crs_engineering": self.target_crs,
                "crs_presentation": "EPSG:4326",
                "source_crs": src,
                "layer": "Best_Available_Flood_Hazard",
                "feature_count": int(len(gdf)),
                "seal": seal,
                "geojson": json.loads(gdf_4326.to_json()),
            }
        except Exception as e:  # noqa: BLE001 — soft-fail boundary
            return self._soft_fail(f"BAFM Polygon Ingestion Error: {e}")

    def ingest_elevation_points(self) -> dict[str, Any]:
        if not os.path.exists(self.pts_shp_path):
            return self._soft_fail(f"Missing Elevation Points at {self.pts_shp_path}")
        try:
            gdf = gpd.read_file(self.pts_shp_path)
            if gdf.crs is None:
                return self._soft_fail("Elevation points have no CRS")
            src = gdf.crs.to_string()
            if src != self.target_crs:
                gdf = gdf.to_crs(self.target_crs)
            gdf.columns = [c.lower() for c in gdf.columns]

            if "wsel1" not in gdf.columns:
                return self._soft_fail("wsel1 field missing from elevation points DBF")

            valid = gdf[gdf["wsel1"].notna() & (gdf["wsel1"] > 0)].copy()
            inventory: list[dict[str, Any]] = []
            for _, row in valid.iterrows():
                inventory.append(
                    {
                        "stream_name": str(row.get("streamname", "UNKNOWN_STREAM")),
                        "reach_index": str(row.get("reachindex", "UNKNOWN_REACH")),
                        "wsel_10_yr": float(row.get("wsel10") or 0.0),
                        "wsel_100_yr_bfe": float(row["wsel1"]),
                        "wsel_500_yr": float(row.get("wsel02") or 0.0),
                        "x_2966": float(row.geometry.x),
                        "y_2966": float(row.geometry.y),
                    }
                )

            seal = hashlib.sha256(
                json.dumps(inventory, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest()

            return {
                "status": "OK",
                "crs": self.target_crs,
                "vertical_datum": "NAVD88",
                "layer": "Flood_Elevation_Points",
                "seal": seal,
                "bfe_inventory": inventory,
                "feature_count": len(inventory),
            }
        except Exception as e:  # noqa: BLE001
            return self._soft_fail(f"Elevation Points Ingestion Error: {e}")

    @staticmethod
    def _soft_fail(reason: str) -> dict[str, Any]:
        return {
            "status": "SOFT_FAIL_DNR_DATA_MISSING",
            "reason": reason,
            "seal": None,
        }


if __name__ == "__main__":
    bridge = DnrRegulatoryBridge()
    bafm = bridge.ingest_bafm_polygons()
    print("BAFM:", bafm["status"], bafm.get("seal") or bafm.get("reason"))
    pts = bridge.ingest_elevation_points()
    print("PTS:", pts["status"], pts.get("seal") or pts.get("reason"))
    if pts.get("bfe_inventory"):
        s = pts["bfe_inventory"][0]
        print(
            f"Sample: {s['stream_name']} 100yr={s['wsel_100_yr_bfe']} "
            f"@ ({s['x_2966']:.1f}, {s['y_2966']:.1f})"
        )
