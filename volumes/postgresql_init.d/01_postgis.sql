CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_raster;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

CREATE TABLE IF NOT EXISTS twin_ras_cells (
  id          BIGSERIAL PRIMARY KEY,
  plan_id     TEXT NOT NULL,
  lon         DOUBLE PRECISION NOT NULL,
  lat         DOUBLE PRECISION NOT NULL,
  depth_m     DOUBLE PRECISION NOT NULL CHECK (depth_m >= 0),
  wse_m       DOUBLE PRECISION,
  velocity_ms DOUBLE PRECISION,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_twin_ras_cells_plan ON twin_ras_cells (plan_id);
CREATE INDEX IF NOT EXISTS idx_twin_ras_cells_depth ON twin_ras_cells (depth_m) WHERE depth_m > 0;
CREATE INDEX IF NOT EXISTS idx_twin_ras_cells_geom ON twin_ras_cells USING GIST (ST_SetSRID(ST_MakePoint(lon, lat), 4326));

CREATE OR REPLACE FUNCTION twin_ras_cells_mvt(z integer, x integer, y integer)
RETURNS bytea AS $$
  SELECT ST_AsMVT(tile, 'twin_ras_cells', 4096, 'geom')
  FROM (
    SELECT id, plan_id, depth_m, wse_m, velocity_ms,
      ST_AsMVTGeom(
        ST_Transform(ST_SetSRID(ST_MakePoint(lon, lat), 4326), 3857),
        ST_TileEnvelope(z, x, y),
        4096, 64, true
      ) AS geom
    FROM twin_ras_cells
    WHERE depth_m > 0.05
      AND ST_Intersects(
        ST_Transform(ST_SetSRID(ST_MakePoint(lon, lat), 4326), 3857),
        ST_TileEnvelope(z, x, y)
      )
  ) AS tile;
$$ LANGUAGE sql STABLE PARALLEL SAFE;
