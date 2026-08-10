-- Spatial index optimization for twin tables
CREATE INDEX IF NOT EXISTS idx_twin_ras_cells_plan_depth
  ON twin_ras_cells (plan_id, depth_m DESC);

CREATE INDEX IF NOT EXISTS idx_twin_ras_cells_point
  ON twin_ras_cells USING GIST (
    ST_SetSRID(ST_MakePoint(lon, lat), 4326)
  );

-- Optional geography for distance queries (meters)
-- CREATE INDEX IF NOT EXISTS idx_twin_ras_cells_geog
--   ON twin_ras_cells USING GIST (
--     geography(ST_SetSRID(ST_MakePoint(lon, lat), 4326))
--   );

ANALYZE twin_ras_cells;
ANALYZE twin_static_parcels;

-- Faster plan-scoped bbox filter helper
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
    AND c.lat BETWEEN miny AND maxy;
$$ LANGUAGE sql STABLE;
