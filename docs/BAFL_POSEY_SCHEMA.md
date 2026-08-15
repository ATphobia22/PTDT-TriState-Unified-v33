# Posey County BAFL extract — schema (from official metadata 2026-07-23)

## CRS

| Property | Value |
|---|---|
| Horizontal | **EPSG:26916** NAD83 UTM Zone 16N (meters) |
| Geographic | GCS_North_American_1983 |
| Vertical on elev pts | NAVD88 (per IDNR BAFL product docs; check `v_datum` on polygons) |
| Extract path (source machine) | `C:\arcgis\BAFLExtract\Posey\` |
| Tool chain | ArcGIS Pro Clip → CopyFeatures (county clip) |

**PTDT rule:** warp polygons/points to **EPSG:2966** only after explicit transform; never assume 26916 == 2966.

## FloodHazard_BestAvai_DNR_Water (polygon)

| Field | Type | Role |
|---|---|---|
| `fld_zone` | String | A, AE, X, AH, AO, … |
| `zone_subty` | String | FLOODWAY, APPROXIMATE FLOODWAY, DNR APPROVED STUDY, 0.2 PCT… |
| `source_dnr` | String | NFHL, IDNR, IDNR_MR, IDNR_ZONEA |
| `sfha_tf` | String(1) | SFHA flag |
| `static_bfe` | Double | Static BFE when present |
| `v_datum` | String | Vertical datum label |
| `depth` | Double | Depth (AO/AH style) |
| `dfirm_id` | String | DFIRM id |
| `version_id` | String | Version |
| `fld_ar_id` | String | Flood area id |
| `study_typ` | String | Study type |
| `source_cit` | String | Citation |
| `dual_zone` | String | Dual-zone flag |
| `shape_Leng` / `shape_Area` | Double | Geometry metrics |

### INFIP symbology keys (unique values on 3 fields)

Match MapLibre/deck categories to official table:

| FLD_ZONE | SOURCE_DNR | ZONE_SUBTY | Label |
|---|---|---|---|
| AE | NFHL | FLOODWAY | FEMA Zone AE Floodway |
| AE | NFHL | ADMINISTRATIVE FLOODWAY | FEMA Administrative Floodway |
| AE | IDNR_MR | DNR APPROVED FLOODWAY | DNR Detailed Floodway |
| A | IDNR_ZONEA | APPROXIMATE FLOODWAY | DNR Approximate Floodway |
| A | IDNR / NFHL | (blank) | FEMA Zone A |
| AE | IDNR / NFHL | (blank) | FEMA Zone AE |
| AE | IDNR_MR | DNR APPROVED STUDY | DNR Detailed Fringe |
| A | IDNR_ZONEA / IDNR_MR | (blank) | DNR Approximate Fringe |
| X | * | 0.2 PCT ANNUAL CHANCE… | 0.2% flood hazard |
| X | NFHL | AREA WITH REDUCED FLOOD RISK DUE TO LEVEE | Protected by levee |
| AH / AO | NFHL | (blank) | Ponding / sheet flow |

**Note:** `.lyr` symbology file is out-of-date for analysis — use field table only.

## Flood_Elevation_Pts_DNR_Water (point)

| Field | Type | Role |
|---|---|---|
| `streamname` | String | Reach name |
| `huc10` | String | HUC10 |
| `reachindex` | String | Reach index |
| `location` | String | Station / location text |
| `wsel10` | Double | 10% annual chance WSEL |
| `wsel4` | Double | 4% |
| `wsel2` | Double | 2% |
| `wsel1` | Double | **1% (100-yr) WSEL** — primary regulatory BFE candidate |
| `wsel02` | Double | 0.2% |
| `wsel1plus` | Double | 1% + freeboard style |
| `da` | Double | Drainage area |
| `bkwtr` / `bckwtr_src` | String | Backwater flags |
| `version` | String | Study version |

**Nearest-neighbor to Bonebank:** query elev pts in EPSG:26916, then convert WSEL to NAVD88 feet for comparison against Material Truth BFE **375.0 ft**. Do **not** average conflicting WSELs.

## Operator placement

```
data/bafl/posey/
  FloodHazard_BestAvai_DNR_Water.*
  Flood_Elevation_Pts_DNR_Water.*
  README (IDNR county zip)
```

Convert for web:

```bash
ogr2ogr -t_srs EPSG:4326 -f GeoJSON data/bafl/posey_flood_hazard_4326.geojson \
  data/bafl/posey/FloodHazard_BestAvai_DNR_Water.shp
ogr2ogr -t_srs EPSG:4326 -f GeoJSON data/bafl/posey_elev_pts_4326.geojson \
  data/bafl/posey/Flood_Elevation_Pts_DNR_Water.shp
```
