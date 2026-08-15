"""IDNR BAFL / elevation points ingest — EPSG:2966 + soft-fail + SHA-256 seal."""
from __future__ import annotations

import hashlib
import json
import os
from typing import Any


class DnrRegulatoryBridge:
    def __init__(self, data_dir: str = "data/bafl/posey") -> None:
        self.data_dir = data_dir
        self.target_crs = "EPSG:2966"
        self.bafm_shp_path = os.path.join(data_dir, "FloodHazard_BestAvai_DNR_Water.shp")
        self.pts_shp_path = os.path.join(data_dir, "Flood_Elevation_Pts_DNR_Water.shp")

    def ingest_bafm_polygons(self) -> dict[str, Any]:
        if not os.path.exists(self.bafm_shp_path):
            return self._soft_fail(f"Missing BAFM shapefile at {self.bafm_shp_path}")
        try:
            import geopandas as gpd
            import pandas as pd

            gdf = gpd.read_file(self.bafm_shp_path)
            if gdf.crs and str(gdf.crs) != self.target_crs:
                gdf = gdf.to_crs(self.target_crs)
            df_attributes = pd.DataFrame(gdf.drop(columns="geometry"))
            seal = hashlib.sha256(df_attributes.to_json(orient="records").encode("utf-8")).hexdigest()
            return {
                "status": "OK",
                "crs": self.target_crs,
                "layer": "Best_Available_Flood_Hazard",
                "feature_count": len(gdf),
                "seal": seal,
                "geojson": json.loads(gdf.to_json()),
            }
        except Exception as exc:  # noqa: BLE001
            return self._soft_fail(f"BAFM Polygon Ingestion Error: {exc}")

    def ingest_elevation_points(self) -> dict[str, Any]:
        if not os.path.exists(self.pts_shp_path):
            return self._soft_fail(f"Missing Elevation Points at {self.pts_shp_path}")
        try:
            import geopandas as gpd

            gdf = gpd.read_file(self.pts_shp_path)
            if gdf.crs and str(gdf.crs) != self.target_crs:
                gdf = gdf.to_crs(self.target_crs)
            valid = gdf[gdf["wsel1"] > 0].copy() if "wsel1" in gdf.columns else gdf
            inventory = []
            for _, row in valid.iterrows():
                inventory.append(
                    {
                        "stream_name": row.get("streamname", "UNKNOWN_STREAM"),
                        "reach_index": row.get("reachindex", "UNKNOWN_REACH"),
                        "wsel_10_yr": float(row.get("wsel10", 0.0) or 0.0),
                        "wsel_100_yr_bfe": float(row.get("wsel1", 0.0) or 0.0),
                        "wsel_500_yr": float(row.get("wsel02", 0.0) or 0.0),
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
            }
        except Exception as exc:  # noqa: BLE001
            return self._soft_fail(f"Elevation Points Ingestion Error: {exc}")

    def _soft_fail(self, reason: str) -> dict[str, Any]:
        return {"status": "SOFT_FAIL_DNR_DATA_MISSING", "reason": reason, "seal": None}


if __name__ == "__main__":
    bridge = DnrRegulatoryBridge()
    print("BAFM:", bridge.ingest_bafm_polygons()["status"])
    print("PTS:", bridge.ingest_elevation_points()["status"])
