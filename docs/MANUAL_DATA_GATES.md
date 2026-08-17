# Manual data gates (cannot be code-merged)

| Gate | Status | Action |
|---|---|---|
| **APN dual-ID** | OPEN | Reconcile deed + Posey XSoft Engage + WTH GIS (`posey.in.wthgis.com`); single APN before LOMA |
| **Sealed COG DEM** | OPEN | Posey 2020 LiDAR/DEM → PDAL ground → `scripts/cog_bare_earth_navd88.sh` → `data/dem/` + SHA-256 (`docs/INDIANA_LIDAR_POSEY.md`) |
| **bonebank_buildings.geojson** | OPEN | Prefer `bash scripts/fetch_igio_posey_buildings.sh` then site clip; else `scripts/fetch_bonebank_buildings.sh` (Microsoft) |
| **Licensed RAS / rascmd** | OPEN | Install on PATH or soft-fail; **no fabricated HDF** |
| **BAFL .shp on disk** | OPEN | County zip → `data/bafl/posey/` → `scripts/bafl_ogr2ogr_posey.sh` |

Code soft-fails when these are absent. CI must stay green without real shp/RAS binaries.

## Operational flood HUD (implemented as data)

- Thresholds: `data/geo/property_impact_thresholds.json`  
- Docs: `docs/MYERS_GAUGE_AND_PROPERTY_IMPACT.md`  
- Gauge: USGS **03322420** / NWS **UNWK2** (navigation, not flood-control)  
- Does **not** replace NAVD88 BFE/LAG/FFE for LOMA  

## CRS quick lock

| Layer | CRS |
|-------|-----|
| Engineering / DEM / LOMA geometry | **EPSG:2966** + **NAVD88** |
| BAFL native archive | **EPSG:26916** |
| IGIO Building Footprints service | EPSG:3857 (query outSR=4326) |
| MapLibre display | EPSG:4326 / Web Mercator |
| MS / Overture download | EPSG:4326 until reprojected |

False easting/northing for 2966: **2952750 / 820208.333** US survey feet.

## County contacts

- Area Plan Commission: 126 E Third St Rm 132, Mt. Vernon; (812) 838-1323; areaplancommission@poseycountyin.gov  
- Assessor / Engage: https://engage.xsoftinc.com/posey  
- County GIS: http://posey.in.wthgis.com/  

## Merge policy

Merge to `main` only when required Actions are green and mergeable state is clean.
