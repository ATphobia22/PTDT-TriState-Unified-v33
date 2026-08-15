# Posey / Point Township — verified data sources (web + PDF audit)

**FIPS:** 18129 (Posey County, IN)  
**Civil township tool:** https://www.randymajors.org/civil-townships-on-google-maps?fips=18129&labels=show  
**Point Township** is the MCD containing the Bonebank anchor (Census geoId for Point Township listed under Posey).

## Site constants (Material Truth — operator must still seal with survey)

From PTDT executive docs (internal Material Truth; LOMA requires sealed elev cert):

| Field | Value |
|---|---|
| Address | 13101 Bonebank Road, Mount Vernon, IN 47620 |
| BFE (NAVD88) | **375.0 ft** |
| LAG (NAVD88) | **377.2 ft** |
| Clearance | **+2.2 ft** |
| Compensatory storage factor | **1.20×** (IN floodway / 312 IAC context) |
| USGS gauge | **03378500** Wabash at New Harmony |

**Coordinate conflict in source PDFs:** some list `37.9035, -88.0007`; MapLibre App center uses `-88.0051, 37.8459`. Treat as **UNVERIFIED_DUAL** until survey control / deed pin.

**APN conflict:** internal docs cite `65-09-35-200-001.000-009`; public listings often differ (e.g. 65-19-08 pattern). **Engage + deed required** before LOMA path.

## IDNR Best Available Floodplain (BAFL)

| Resource | URL |
|---|---|
| Policy page | https://www.in.gov/dnr/water/surface-water/indiana-floodplain-mapping/the-indiana-best-available-floodplain-mapping/ |
| INFIP portal | https://www.in.gov/dnr/water/surface-water/indiana-floodplain-mapping/indiana-floodplain-information-portal/ |
| REST MapServer | https://gisdata.in.gov/server/rest/services/Best_Available_Flood_Hazard_Layer/MapServer |
| County downloads | FloodHazard_BestAvai_DNR_Water + Flood_Elevation_Pts (UTM 16N NAD83, NAVD88 elev pts) |

**Regulatory note:** BAFL is DNR-approved for planning/permitting under Indiana model ordinance when FIRM lacks detail; **insurance** still uses FEMA NFHL/FIRM. FARA via INFIP for LOMA support in A zones.

NFHL identify (insurance context):  
`https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer`

## Posey parcels

| Source | Notes |
|---|---|
| XSoft Engage | `https://engage.xsoftinc.com/posey/map/getparceldetail?parcelId=` — HTML; use server proxy |
| WTH ThinkGIS UI | https://poseyin.wthgis.com |
| IndianaMap 2025 parcels | FeatureServer (paginated maxRecordCount 2000) |

PDF "Real API calls" cited incomplete `https://in.gov` and `wthgis.com` layer paths — **do not hardcode untested full URLs**. Prefer verified IndianaMap + Engage proxy.

## IDNR Special Streams / navigable waters (Posey-relevant)

From Appendix E.4 / NRC roster (not a complete special-streams table):

**Special / listed reaches touching Posey (Appendix E.4 excerpts):**
- **Black River** (Posey): Higginbotham Ditch confluence → Wabash confluence
- **Cypress Slough** (Posey): Castlebury Creek confluence → Southwind Maritime Center
- **Wabash River**: statewide including **Posey** to Ohio confluence

**NRC navigable roster — Posey County:**
1. Big Creek — navigable from Wabash junction 25.4 mi
2. Harris Ditch — 0.9 mi from Ohio
3. Little Fork of Big Creek — 5.1 mi
4. McFadden Creek — 2.3 mi from Ohio
5. Ohio River — throughout county
6. Wabash River — throughout county

Use for regulatory awareness overlays; not a substitute for Flood Control Act permit determination.

## LiDAR / DEM (GGHHA Ch.4 + IGIO)

- Statewide LiDAR program: document horizontal/vertical datum **before** modeling
- AWS open data: `s3://giselevationingov/` (no-sign-request)
- Scripts: `scripts/igio_s3_elevation_clip.sh`, PDAL ground extract, COG warp to **EPSG:2966** + NAVD88 semantics

## Overture buildings snapshot (local JSON)

File `PTDT_Overture_PMT_Data_Snapshot_*.json` reported **renderedOvertureBuildingsCount: 0** — confirms empty footprint gate; need real GeoJSON / Overture clip.

## Geocaching Form 54539

IDNR State Form 54539 is **geocaching placement permit** — not floodplain engineering. Do not wire into hydro pipeline.

## Earthcache / ArcGIS Experience links

- earthcache.org — educational geoscience caches; not regulatory flood data
- ArcGIS Experience apps — validate layer by layer; prefer documented MapServer URLs above
