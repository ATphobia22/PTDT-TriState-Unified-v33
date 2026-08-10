-- Optimized spatial + attribute indexes for twin workload

-- Point geometry (lon/lat) — primary spatial access path
CREATE INDEX IF NOT EXISTS idx_twin_ras_cells_point
  ON twin_ras_cells USING GIST (
    ST_SetSRID(ST_MakePoint(lon, lat), 4326)
  );

-- Plan + depth for flood-stage filters and ranking
CREATE INDEX IF NOT EXISTS idx_twin_ras_cells_plan_depth
  ON twin_ras_cells (plan_id, depth_m DESC NULLS LAST);

-- Partial index: only wet cells (skips dry noise in queries)
CREATE INDEX IF NOT EXISTS idx_twin_ras_cells_wet
  ON twin_ras_cells (plan_id, depth_m)
  WHERE depth_m > 0;

-- Parcels GIST (already created in 02; ensure present)
CREATE INDEX IF NOT EXISTS idx_twin_static_parcels_geom
  ON twin_static_parcels USING GIST (geom);

-- Expression index for metadata asset lookups
CREATE INDEX IF NOT EXISTS idx_twin_static_parcels_asset
  ON twin_static_parcels ((metadata->>'ASSET_ID'));

ANALYZE twin_ras_cells;
ANALYZE twin_static_parcels;

CREATE OR REPLACE FUNCTION twin_ras_bbox(
  p_plan text,
  minx double precision,
  miny double precision,
  maxx double precision,
  maxy double precision
)
RETURNS SETOF twin_ras_cells AS $$
  SELECT c.*
  FROM twin_ras_cells c
  WHERE c.plan_id = p_plan
    AND c.lon BETWEEN minx AND maxx
    AND c.lat BETWEEN miny AND maxy
    AND c.depth_m > 0;
$$ LANGUAGE sql STABLE;
