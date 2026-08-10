# PostGIS Setup

## Start
```powershell
docker compose up -d
docker exec ptdt_postgis pg_isready -U ptdt -d ptdt
```
`postgresql://ptdt:ptdt@127.0.0.1:8087/ptdt`

## Indexes
- GIST on cell points
- `(plan_id, depth_m DESC)`
- Partial wet cells `WHERE depth_m > 0`
- Parcel GIST + `metadata->>'ASSET_ID'`

## Backup / restore
```powershell
.\scripts\backup_postgis.ps1
.\scripts\restore_postgis.ps1 .\volumes\backups\ptdt_YYYYMMDD_HHMMSS.dump
```
Retention: last 14 dumps under `volumes/backups`.

## GDAL import
```powershell
.\scripts\gdal_import_postgis.ps1 .\volumes\gis_import\parcels.geojson
```
