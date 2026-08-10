# PostGIS Setup

## Start
```powershell
docker compose up -d
docker exec ptdt_postgis pg_isready -U ptdt -d ptdt
```

Connection: `postgresql://ptdt:ptdt@127.0.0.1:8087/ptdt`

## Volumes
| Host path | Container |
|-----------|----------|
| `volumes/postgresql_data` | `/var/lib/postgresql/data` |
| `volumes/postgresql_init.d` | init scripts (ro) |
| `volumes/gis_import` | `/gis_import` (ro) — drop shapefiles/GeoJSON here |
| `volumes/backups` | `/backups` |
| `volumes/qgis_projects` | QGIS projects |

## Spatial indexes
Init applies GIST on points + `(plan_id, depth_m)` btree. Helper: `twin_ras_bbox(...)`.

## GDAL import
```powershell
# winget install OSGeo.GDAL
.\scripts\gdal_import_postgis.ps1 .\volumes\gis_import\parcels.geojson
```
or
```bash
./scripts/gdal_import_postgis.sh ./volumes/gis_import/parcels.shp
```
→ table `twin_static_parcels_import`
