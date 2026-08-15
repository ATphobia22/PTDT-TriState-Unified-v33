"""HEC-RAS HDF WSE extract + cell-index rasterize — soft-fail without licensed plan."""
from __future__ import annotations

import hashlib
import os
from typing import Any

import numpy as np


class HecRasPipeline:
    def __init__(self, plan_hdf_path: str) -> None:
        self.plan_hdf_path = plan_hdf_path

    def extract_wse_mm(self, flow_area: str, timestep_index: int) -> dict[str, Any]:
        if not os.path.exists(self.plan_hdf_path):
            return self._soft_fail(f"HDF missing: {self.plan_hdf_path}")
        hdf_path = (
            "/Results/Unsteady/Output/Output Blocks/Base Output/Unsteady Time Series/"
            f"2D Flow Areas/{flow_area}/Water Surface"
        )
        try:
            import h5py

            with h5py.File(self.plan_hdf_path, "r") as hdf:
                if hdf_path not in hdf:
                    return self._soft_fail(f"HDF path {hdf_path} missing")
                wse_dataset = hdf[hdf_path]
                if timestep_index >= wse_dataset.shape[0]:
                    return self._soft_fail("Timestep index out of bounds")
                wse_raw = wse_dataset[timestep_index, :]
                wse_mm = np.where(np.isnan(wse_raw), -9999, wse_raw * 1000).astype(np.int32)
                seal = hashlib.sha256(wse_mm.tobytes()).hexdigest()
                return {
                    "status": "OK",
                    "crs": "EPSG:2966",
                    "vertical_datum": "NAVD88",
                    "timestep": timestep_index,
                    "seal": seal,
                    "data": wse_mm,
                }
        except Exception as exc:  # noqa: BLE001
            return self._soft_fail(f"HDF read error: {exc}")

    def _soft_fail(self, reason: str) -> dict[str, Any]:
        return {
            "status": "SOFT_FAIL_NO_HDF",
            "reason": reason,
            "data": np.array([], dtype=np.int32),
            "seal": None,
        }

    def generate_cell_index_map(
        self,
        cells_geojson_path: str,
        dem_cog_path: str,
        out_tif_path: str,
    ) -> dict[str, Any]:
        if not os.path.exists(dem_cog_path):
            return self._soft_fail(f"DEM COG missing: {dem_cog_path}")
        if not os.path.exists(cells_geojson_path):
            return self._soft_fail(f"Cells GeoJSON missing: {cells_geojson_path}")
        try:
            import geopandas as gpd
            import rasterio
            from rasterio.features import rasterize

            with rasterio.open(dem_cog_path) as src:
                dem_meta = src.meta.copy()
                dem_transform = src.transform
                dem_width, dem_height = src.width, src.height

            cells_gdf = gpd.read_file(cells_geojson_path)
            if cells_gdf.crs and str(cells_gdf.crs) != "EPSG:2966":
                cells_gdf = cells_gdf.to_crs("EPSG:2966")
            if "Cell_Index" not in cells_gdf.columns:
                return self._soft_fail("Cell_Index attribute required")

            shapes = ((geom, int(val)) for geom, val in zip(cells_gdf.geometry, cells_gdf["Cell_Index"]))
            nodata_val = 4294967295
            cell_index_array = rasterize(
                shapes=shapes,
                out_shape=(dem_height, dem_width),
                transform=dem_transform,
                fill=nodata_val,
                dtype=rasterio.uint32,
                all_touched=False,
            )
            dem_meta.update(dtype=rasterio.uint32, count=1, nodata=nodata_val, compress="deflate")
            with rasterio.open(out_tif_path, "w", **dem_meta) as dst:
                dst.write(cell_index_array, 1)
            return {"status": "OK", "path": out_tif_path, "crs": "EPSG:2966"}
        except Exception as exc:  # noqa: BLE001
            return self._soft_fail(f"cell_index_map error: {exc}")


if __name__ == "__main__":
    pipeline = HecRasPipeline("data/ras/PointTownship.p01.hdf")
    state = pipeline.extract_wse_mm(flow_area="Wabash_Confluence", timestep_index=0)
    print(f"Hydraulic State Status: {state['status']} | Seal: {state.get('seal', 'N/A')}")
