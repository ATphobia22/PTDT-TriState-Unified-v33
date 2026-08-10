# Detailed SQL Examples (PTDT)

## Vector cells
```sql
-- Wet cells in bbox for plan
SELECT * FROM twin_ras_bbox('01', -87.95, 38.12, -87.92, 38.14);

-- Deepest 20 cells
SELECT id, lon, lat, depth_m
FROM twin_ras_cells
WHERE plan_id = '01' AND depth_m > 0
ORDER BY depth_m DESC
LIMIT 20;

-- Spatial join parcels ∩ deep water
SELECT p.id, p.metadata->>'ASSET_ID', c.depth_m
FROM twin_static_parcels p
JOIN twin_ras_cells c
  ON ST_DWithin(
    p.geom::geography,
    ST_SetSRID(ST_MakePoint(c.lon, c.lat), 4326)::geography,
    50
  )
WHERE c.plan_id = '01' AND c.depth_m >= 1.0;
```

## Raster
```sql
SELECT twin_raster_value('01', -87.9354, 38.1294, 1);
SELECT * FROM twin_raster_summary('01', 1);
SELECT ST_AsGDALRaster(
  twin_raster_clip_bbox('01', -87.95, 38.12, -87.92, 38.14),
  'GTiff'
);
```

## Index health
```sql
CREATE EXTENSION IF NOT EXISTS pgstattuple;
SELECT * FROM pgstattuple('idx_twin_ras_cells_point');
REINDEX INDEX CONCURRENTLY idx_twin_ras_cells_point;
```

## MVT
```sql
SELECT twin_ras_mvt(14, 4200, 6200, '01');
```
