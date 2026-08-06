# PTDT-TriState-Unified-v33

Production Windows 11 cinematic digital twin

## Build .EXE
```bash
npm i && npm run dist:win
```

## Inno Setup (optional full installer)
Compile `installer/TriRiverTwin_Win11.iss` with Inno Setup.

## Data Sync
- `middleware/sync-engine.js` — local static GIS bootstrap
- `middleware/ras-sync-router.js` — HEC-RAS results ingest
- PostGIS tables: twin_ras_cells + twin_static_parcels
