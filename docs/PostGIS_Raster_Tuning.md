# PostGIS Raster Performance

## Principles
1. **Tile** at load: `-t 256x256` (or 128x128 for dense DEM)
2. **In-db** rasters for twin latency; out-db only for huge archives
3. **GIST** on `ST_ConvexHull(rast)` + `plan_id` btree
4. **Constraints** via `AddRasterConstraints` after first load
5. **Avoid** full-table `ST_Clip` without bbox filter first

## Load
```powershell
.\scripts\load_raster.ps1 .\volumes\gis_import\depth.tif -PlanId 01 -Tile 256x256
```

## Query pattern
```sql
SELECT ST_Value(rast, ST_SetSRID(ST_MakePoint(lon,lat),4326))
FROM twin_rasters
WHERE plan_id = '01'
  AND ST_Intersects(rast, ST_SetSRID(ST_MakePoint(lon,lat),4326));
```

## Fillfactor
Raster footprint GIST: `fillfactor=90, buffering=on` (same as vector points).
