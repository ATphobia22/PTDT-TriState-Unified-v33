# GIST Index Fillfactor Tuning

## Defaults
PostgreSQL GIST default fillfactor is **90**. Lower values leave free space for updates (write-heavy); higher packs denser (read-heavy).

## PTDT choice: 90 + buffering=on
Flood cell points and parcel polygons are **read-mostly** after HEC-RAS ingest. Dense leaves improve bbox hits.

```sql
CREATE INDEX idx_twin_ras_cells_point
  ON twin_ras_cells USING GIST (ST_SetSRID(ST_MakePoint(lon, lat), 4326))
  WITH (fillfactor = 90, buffering = on);
```

| fillfactor | When |
|-----------|------|
| 50–70 | Continuous inserts/updates on same index |
| **90** | Batch load then query (our case) |
| 100 | Static archive (no updates) |

`buffering=on` reduces page splits during concurrent inserts.

## After bulk load
```sql
REINDEX INDEX CONCURRENTLY idx_twin_ras_cells_point;
ANALYZE twin_ras_cells;
```
