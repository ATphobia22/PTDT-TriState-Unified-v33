# PostGIS Raster Performance Tips

1. **Tile at load** — `raster2pgsql -t 256x256` (128x128 for dense LiDAR).
2. **In-db tiles** for interactive twin; out-db only for cold archive.
3. **GIST on footprint** — `ST_ConvexHull(rast)` with fillfactor 90.
4. **Filter before clip** — always `ST_Intersects` / plan_id before `ST_Clip` / `ST_Value`.
5. **AddRasterConstraints** after first load for scale/SRID checks.
6. **Avoid** selecting whole rast without bbox; use helper functions below.

## Load
```powershell
.\scripts\load_raster.ps1 .\volumes\gis_import\depth.tif -PlanId 01 -Tile 256x256
```

## SQL examples (raster functions)

### Point sample
```sql
SELECT twin_raster_value('01', -87.9354, 38.1294, 1) AS depth_m;
```

### Clip to Bonebank area
```sql
SELECT ST_AsGDALRaster(
  twin_raster_clip_bbox('01', -87.95, 38.12, -87.92, 38.14),
  'GTiff'
) AS tif_bytes;
```

### Plan band summary
```sql
SELECT * FROM twin_raster_summary('01', 1);
-- min_val | max_val | mean_val
```

### Raw ST_Value with spatial filter
```sql
SELECT ST_Value(rast, 1, ST_SetSRID(ST_MakePoint(-87.9354, 38.1294), 4326))
FROM twin_rasters
WHERE plan_id = '01'
  AND ST_Intersects(rast, ST_SetSRID(ST_MakePoint(-87.9354, 38.1294), 4326))
LIMIT 1;
```

### Map algebra (depth > 1 m mask)
```sql
SELECT ST_MapAlgebra(rast, 1, '32BF',
  'CASE WHEN [rast] > 1.0 THEN [rast] ELSE 0 END')
FROM twin_rasters WHERE plan_id = '01' LIMIT 1;
```
