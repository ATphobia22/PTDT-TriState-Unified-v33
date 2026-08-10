-- PostGIS Raster performance tuning (PTDT flood / DEM tiles)

CREATE EXTENSION IF NOT EXISTS postgis_raster;

-- Raster catalog for USGS/HEC-RAS depth grids
CREATE TABLE IF NOT EXISTS twin_rasters (
  rid SERIAL PRIMARY KEY,
  plan_id TEXT,
  name TEXT,
  rast RASTER,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Constraint enforce: scale, SRID, block size (optional after load)
-- SELECT AddRasterConstraints('twin_rasters','rast',TRUE,TRUE,TRUE,TRUE,TRUE,TRUE,FALSE,TRUE,TRUE,TRUE,TRUE,TRUE);

-- Spatial index on raster footprint
CREATE INDEX IF NOT EXISTS idx_twin_rasters_rast_gist
  ON twin_rasters USING GIST (ST_ConvexHull(rast))
  WITH (fillfactor = 90, buffering = on);

CREATE INDEX IF NOT EXISTS idx_twin_rasters_plan
  ON twin_rasters (plan_id);

-- Prefer in-db tiled rasters: 128x128 or 256x256 blocks at load time
-- Example load (run manually):
-- raster2pgsql -s 4326 -I -C -M -t 256x256 dem.tif public.twin_rasters | psql ...

-- Session-level hints for raster ops (apply in app connection or here as defaults via ALTER DATABASE if desired)
-- SET postgis.gdal_enabled_drivers = 'ENABLE_ALL';
-- SET postgis.enable_outdb_rasters = true;  -- only if using out-of-db GDAL files

ANALYZE twin_rasters;
