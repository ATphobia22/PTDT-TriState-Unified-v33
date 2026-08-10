-- Helpers for index size / maintenance (run as needed; pgstattuple optional)
CREATE EXTENSION IF NOT EXISTS pgstattuple;

CREATE OR REPLACE VIEW twin_index_sizes AS
SELECT
  c.relname AS index_name,
  pg_size_pretty(pg_relation_size(c.oid)) AS size,
  pg_relation_size(c.oid) AS bytes
FROM pg_class c
JOIN pg_index i ON c.oid = i.indexrelid
WHERE c.relname LIKE 'idx_twin%'
   OR c.relname LIKE 'idx_flow%';
