# PostGIS Setup

## Start
```powershell
docker compose up -d
docker exec ptdt_postgis pg_isready -U ptdt -d ptdt
```

## GIST fillfactor
Point/parcel GIST indexes use `fillfactor=90, buffering=on` (read-heavy, denser pages).

## Topology
Extension `postgis_topology` + topology `twin_topo` (SRID 4326). Table `flow_edges` for line networks.

## Backup examples
```powershell
# Full custom dump
.\scripts\backup_postgis.ps1 -Mode full

# Data only
.\scripts\backup_postgis.ps1 -Mode data-only

# Schema only
.\scripts\backup_postgis.ps1 -Mode schema-only

# Specific tables
.\scripts\backup_postgis.ps1 -Mode tables -Tables twin_ras_cells,twin_static_parcels

# Restore
.\scripts\restore_postgis.ps1 .\volumes\backups\ptdt_full_YYYYMMDD_HHMMSS.dump
```
