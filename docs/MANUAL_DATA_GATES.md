# Manual data gates (cannot be code-merged)

| Gate | Status | Action |
|---|---|---|
| **APN dual-ID** | OPEN | Reconcile deed + Posey XSoft Engage; do not file LOMA until single APN |
| **Sealed COG DEM** | OPEN | IGIO S3 LAS → PDAL ground → GDAL COG EPSG:2966 NAVD88 under `data/` |
| **bonebank_buildings.geojson** | OPEN | Replace placeholder; OSM/Overture/survey footprints |
| **Licensed RAS / rascmd** | OPEN | Install on PATH or soft-fail; no fabricated HDF |
| **BAFL .shp on disk** | OPEN | County zip → `data/bafl/posey/` → `scripts/bafl_ogr2ogr_posey.sh` |

Code already soft-fails when these are absent. CI must stay green without real shp/RAS binaries.

## PR #10 merge policy

Merge **only** when Actions `frontend` + `python` are green and `mergeable_state` is clean. Do not force-merge unstable heads.
