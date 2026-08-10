CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_raster;

CREATE TABLE IF NOT EXISTS twin_ras_cells (
  id SERIAL PRIMARY KEY,
  plan_id TEXT NOT NULL,
  lon DOUBLE PRECISION,
  lat DOUBLE PRECISION,
  depth_m DOUBLE PRECISION,
  wse_m DOUBLE PRECISION,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_twin_ras_cells_plan ON twin_ras_cells (plan_id);
CREATE INDEX IF NOT EXISTS idx_twin_ras_cells_geom ON twin_ras_cells
  USING GIST (ST_SetSRID(ST_MakePoint(lon, lat), 4326));

CREATE OR REPLACE FUNCTION twin_ras_mvt(z integer, x integer, y integer, p_plan text)
RETURNS bytea AS $$
  WITH bounds AS (
    SELECT ST_TileEnvelope(z, x, y) AS geom
  ),
  mvtgeom AS (
    SELECT
      id, plan_id, depth_m, wse_m,
      ST_AsMVTGeom(
        ST_Transform(ST_SetSRID(ST_MakePoint(lon, lat), 4326), 3857),
        bounds.geom,
        4096, 64, true
      ) AS geom
    FROM twin_ras_cells, bounds
    WHERE plan_id = p_plan
      AND ST_Intersects(
        ST_Transform(ST_SetSRID(ST_MakePoint(lon, lat), 4326), 3857),
        bounds.geom
      )
  )
  SELECT ST_AsMVT(mvtgeom, 'twin_ras', 4096, 'geom') FROM mvtgeom;
$$ LANGUAGE sql STABLE;
