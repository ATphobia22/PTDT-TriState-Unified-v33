# PostGIS Vector Indexes

| Type | Best for | Tradeoff |
|------|----------|----------|
| **GIST** | Default spatial (&&, ST_Intersects, KNN) | Larger; best general read |
| **SP-GIST** | Low-overlap points, uniform partition | Build faster; can beat GIST if little overlap |
| **BRIN** | Huge append-only, spatially sorted | Tiny index; slow random bbox |
| **B-tree** | plan_id, depth_m scalars | Non-spatial filters |

## PTDT choice
- Cells/parcels: **GIST** fillfactor 90 (interactive flood queries).
- BRIN only if archiving multi-year cell history in physical lon/lat order.
- SP-GIST optional experiment on pure points with low overlap:

```sql
CREATE INDEX idx_twin_ras_cells_spgist
  ON twin_ras_cells USING SPGIST (ST_SetSRID(ST_MakePoint(lon, lat), 4326));
```

Keep GIST as primary; SP-GIST is additive A/B only.
