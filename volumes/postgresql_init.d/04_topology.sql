-- PostGIS Topology for network / catchment edges (optional layer)
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Dedicated topology schema for Tri-State valley networks
SELECT topology.CreateTopology('twin_topo', 4326, 0.00001)
WHERE NOT EXISTS (
  SELECT 1 FROM topology.topology WHERE name = 'twin_topo'
);

-- Layer for engineered flow paths / berms (lines)
-- Usage after load:
--   SELECT topology.AddTopoGeometryColumn('twin_topo','public','flow_edges','topo','LINESTRING');

CREATE TABLE IF NOT EXISTS flow_edges (
  id SERIAL PRIMARY KEY,
  name TEXT,
  geom GEOMETRY(LineString, 4326),
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_flow_edges_geom
  ON flow_edges USING GIST (geom)
  WITH (fillfactor = 90, buffering = on);
