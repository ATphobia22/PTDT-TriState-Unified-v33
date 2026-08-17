# Manual data gates (cannot be code-merged)

| Gate | Status | Action |
|---|---|---|
| **APN dual-ID** | OPEN | Reconcile deed + Posey XSoft Engage (`65-19-08-100-008.001-010` candidate); single APN before LOMA |
| **Sealed COG DEM** | OPEN | Posey 2020 LiDAR/DEM → PDAL ground → `scripts/cog_bare_earth_navd88.sh` → `data/dem/` + SHA-256 (see `docs/INDIANA_LIDAR_POSEY.md`) |
| **bonebank_buildings.geojson** | OPEN | `bash scripts/fetch_bonebank_buildings.sh` (Microsoft Indiana zip) or survey; optional Overture heights (`docs/BUILDINGS_MICROSOFT_AND_OVERTURE.md`) |
| **Licensed RAS / rascmd** | OPEN | Install on PATH or soft-fail; **no fabricated HDF** |
| **BAFL .shp on disk** | OPEN | County zip → `data/bafl/posey/` → `scripts/bafl_ogr2ogr_posey.sh` |

Code soft-fails when these are absent. CI must stay green without real shp/RAS binaries.

## CRS quick lock

| Layer | CRS |
|-------|-----|
| Engineering / DEM / LOMA geometry | **EPSG:2966** + **NAVD88** |
| BAFL native archive | **EPSG:26916** |
| MapLibre display | EPSG:4326 / Web Mercator |
| MS / Overture download | EPSG:4326 until reprojected |

False easting/northing for 2966: **2952750 / 820208.333** US survey feet (not 900000/250000).

## Merge policy

Merge to `main` only when required Actions are green and mergeable state is clean. Do not force-merge unstable heads.
