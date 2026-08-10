# PostGIS Setup (PTDT)

## Start

```powershell
docker compose up -d
```

Wait until healthy:

```powershell
docker compose ps
# or
docker exec ptdt_postgis pg_isready -U ptdt -d ptdt
```

## Connection

| Key | Value |
|-----|--------|
| Host | 127.0.0.1 |
| Port | 8087 |
| Database | ptdt |
| User | ptdt |
| Password | ptdt |

```
postgresql://ptdt:ptdt@127.0.0.1:8087/ptdt
```

## Tables

- `twin_ras_cells` — HEC-RAS depth/WSE points (plan_id, lon, lat, depth_m, wse_m)
- `twin_static_parcels` — local parcel geometries + metadata JSONB
- MVT helper: `twin_ras_mvt(z, x, y, plan_id)`

## Ingest HEC-RAS cells

`POST http://127.0.0.1:<api>/api/engineering/ras-results`

```json
{
  "plan_id": "01",
  "cells": [
    { "lon": -87.93, "lat": 38.13, "depth_m": 1.2, "wse_m": 112.4 }
  ]
}
```

Uses `middleware/ras-sync-router.js`.

## Stop / reset

```powershell
docker compose down
# wipe data:
docker compose down -v
Remove-Item -Recurse -Force .\volumes\postgresql_data -ErrorAction SilentlyContinue
```
