CREATE TABLE IF NOT EXISTS twin_static_parcels (
  id TEXT PRIMARY KEY,
  geom GEOMETRY(Geometry, 4326),
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_twin_static_parcels_geom
  ON twin_static_parcels USING GIST (geom);
