# XSoft HTML proxy + IndianaMap vectors

## Fixed XSoft URL

| Wrong | Correct |
|---|---|
| `https://xsoftinc.com?parcelId=` | **`https://engage.xsoftinc.com/posey/map/getparceldetail?parcelId=`** |

Client: `src/services/xsoftService.ts`  
Server proxy: `backend/proxies/xsoft_engage_proxy.py`  
Route: `GET /api/proxy/xsoft/posey/parcel?parcel_id=`

Mount: `mount_xsoft_proxy(app)` in FastAPI factory.

Parsed fields (best-effort): address, owner, legal, class, township, acreage, latest land/improvement/total value, sales list. **SOFT_FAIL** on network/parse errors.

Engage disclaims legal/financial reliance; PTDT uses this for **APN reconcile UI only**.

## IndianaMap “vector tiles”

Public IndianaMap parcel products are primarily **ArcGIS FeatureServer** (Query + GeoJSON/JSON), not a documented statewide free MVT VectorTileServer for parcels.

| Layer | URL |
|---|---|
| Parcels 2025 | `.../Hosted/Parcel_Boundaries_of_Indiana_2025/FeatureServer/0` |
| Parcels Current | `.../Hosted/Parcel_Boundaries_of_Indiana_Current/FeatureServer/0` |

Helper: `src/services/indianaMapParcels.ts` — bbox query → GeoJSON for MapLibre.

For true MVT/PMTiles offline: download FGDB/GeoJSON from IndianaMap API Explorer → tippecanoe → PMTiles.

## IGIO S3 elevation clip

`scripts/igio_s3_elevation_clip.sh` — list `s3://giselevationingov/`, download site tiles only, then PDAL + COG scripts.
