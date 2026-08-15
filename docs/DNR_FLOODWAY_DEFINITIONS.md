# DNR floodway definitions (verified)

## Statute / rule

**312 IAC 1-1-16 — Floodway** means:
1. the channel of a river or stream; **and**
2. the parts of the flood plain adjoining the channel that are reasonably required to efficiently carry and discharge the flood water or flood flow of a river or stream.

**312 IAC 10-2-3 — Adversely affect / unduly restrict floodway capacity:**
an increase in the elevation of the regulatory flood of **at least 0.15 ft** (project vs base condition), with listed exceptions (dams, authorized flood control, recorded flood easements).

**312 IAC 10-3-1:** local ordinances must cover floodway + fringe, or the undivided flood plain. DNR may delineate boundaries.

## BAFL `SOURCE_DNR` / `ZONE_SUBTY` meaning (product, not statute text)

| SOURCE_DNR | Typical ZONE_SUBTY | Meaning |
|---|---|---|
| **NFHL** | FLOODWAY / ADMINISTRATIVE FLOODWAY | FEMA effective / admin floodway |
| **IDNR_MR** | DNR APPROVED FLOODWAY | Detailed DNR model-reviewed floodway |
| **IDNR_MR** | DNR APPROVED STUDY | Detailed fringe (non-floodway) |
| **IDNR_ZONEA** | APPROXIMATE FLOODWAY | Zone-A quality approximate floodway |
| **IDNR / NFHL** | blank | Zone A/AE fringe or undetailed |

**Permit gate (simplified):** new residences in **floodway** generally prohibited; other floodway work needs **DNR permit** (IC 14-28-1). Fringe often local-only with elevation rules. Always confirm with DoWORC/INFIP FARA for the site.

**Insurance vs permitting:** mandatory flood insurance uses **FEMA NFHL/FIRM**; local/state construction permitting may use **BAFL** as best available under model ordinance.

## IndianaMap parcels 2025

```
https://gisdata.in.gov/server/rest/services/Hosted/Parcel_Boundaries_of_Indiana_2025/FeatureServer/0
```

- maxRecordCount **2000** — use `resultOffset` pagination
- Spatial ref **4326** on service
- Key fields: `state_parcel_id`, `parcel_id`, `county_fips` (Posey = **18129**)
- Not a survey product; accuracy varies by county

## Operator BAFL path

```bash
mkdir -p data/bafl/posey
# copy FloodHazard_BestAvai_DNR_Water.* + Flood_Elevation_Pts_DNR_Water.*
pip install geopandas pyproj
python python/dnr_regulatory_bridge.py
# optional web-only:
ogr2ogr -t_srs EPSG:4326 -f GeoJSON data/bafl/posey_flood_hazard_4326.geojson \
  data/bafl/posey/FloodHazard_BestAvai_DNR_Water.shp
```
