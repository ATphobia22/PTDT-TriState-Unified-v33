# Analyze GIST Index Bloat

VACUUM does **not** fully compact indexes. After repeated DELETE/re-ingest of `twin_ras_cells`, GIST can bloat.

## Enable stats
```sql
CREATE EXTENSION IF NOT EXISTS pgstattuple;
```

## Size overview
```sql
SELECT
  c.relname AS index_name,
  pg_size_pretty(pg_relation_size(c.oid)) AS size,
  pg_relation_size(c.oid) AS bytes
FROM pg_class c
JOIN pg_index i ON c.oid = i.indexrelid
WHERE c.relname LIKE 'idx_twin%'
ORDER BY pg_relation_size(c.oid) DESC;
```

## Page-level (pgstattuple)
```sql
SELECT * FROM pgstattuple('idx_twin_ras_cells_point');
-- free_percent high + table rowcount stable ⇒ bloat candidate
```

Note: `pgstatindex()` targets **B-tree**. For GIST use `pgstattuple` + size growth vs live rows.

## Live rows vs index size trend
```sql
SELECT
  (SELECT reltuples::bigint FROM pg_class WHERE relname = 'twin_ras_cells') AS approx_rows,
  pg_size_pretty(pg_relation_size('idx_twin_ras_cells_point')) AS gist_size;
```

## Remediation
```sql
-- Online (PG 12+)
REINDEX INDEX CONCURRENTLY idx_twin_ras_cells_point;
REINDEX INDEX CONCURRENTLY idx_twin_static_parcels_geom;
ANALYZE twin_ras_cells;
ANALYZE twin_static_parcels;
```

Threshold: if index grows while row counts stay flat after plan REPLACE cycles, REINDEX.
