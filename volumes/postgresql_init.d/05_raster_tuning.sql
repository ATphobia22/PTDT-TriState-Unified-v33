-- PostGIS raster + complete helper functions for PTDT

CREATE EXTENSION IF NOT EXISTS postgis_raster;

CREATE TABLE IF NOT EXISTS twin_rasters (
  rid SERIAL PRIMARY KEY,
  plan_id TEXT,
  name TEXT,
  rast RASTER,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

DROP INDEX IF EXISTS idx_twin_rasters_rast_gist;
CREATE INDEX idx_twin_rasters_rast_gist
  ON twin_rasters USING GIST (ST_ConvexHull(rast))
  WITH (fillfactor = 90, buffering = on);

CREATE INDEX IF NOT EXISTS idx_twin_rasters_plan ON twin_rasters (plan_id);

CREATE OR REPLACE FUNCTION twin_raster_value(
  p_plan text,
  p_lon double precision,
  p_lat double precision,
  p_band int DEFAULT 1
)
RETURNS double precision AS $$
  SELECT ST_Value(r.rast, p_band, ST_SetSRID(ST_MakePoint(p_lon, p_lat), 4326))
  FROM twin_rasters r
  WHERE r.plan_id = p_plan
    AND ST_Intersects(r.rast, ST_SetSRID(ST_MakePoint(p_lon, p_lat), 4326))
  LIMIT 1;
$$ LANGUAGE sql STABLE PARALLEL SAFE;

CREATE OR REPLACE FUNCTION twin_raster_clip_bbox(
  p_plan text,
  minx double precision,
  miny double precision,
  maxx double precision,
  maxy double precision
)
RETURNS raster AS $$
  SELECT ST_Clip(
    r.rast,
    ST_MakeEnvelope(minx, miny, maxx, maxy, 4326),
    true
  )
  FROM twin_rasters r
  WHERE r.plan_id = p_plan
    AND ST_Intersects(r.rast, ST_MakeEnvelope(minx, miny, maxx, maxy, 4326))
  LIMIT 1;
$$ LANGUAGE sql STABLE PARALLEL SAFE;

CREATE OR REPLACE FUNCTION twin_raster_summary(
  p_plan text,
  p_band int DEFAULT 1
)
RETURNS TABLE(
  min_val double precision,
  max_val double precision,
  mean_val double precision,
  count_val bigint
) AS $$
  SELECT
    (stats).min,
    (stats).max,
    (stats).mean,
    (stats).count
  FROM (
    SELECT ST_SummaryStatsAgg(r.rast, p_band, true) AS stats
    FROM twin_rasters r
    WHERE r.plan_id = p_plan
  ) s;
$$ LANGUAGE sql STABLE PARALLEL SAFE;

ANALYZE twin_rasters;
