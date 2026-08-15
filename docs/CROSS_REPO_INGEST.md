# Cross-repo assets needed in PTDT-TriState-Unified-v33

| Source repo | Bring into this tree |
|---|---|
| **PTDT-v33** | `backend/services` patterns, sovereign constants, Archimedes no-rise |
| **Point-Township-Digital-Twin** | hydrology orchestration ideas (not PINN weights unless licensed) |
| **Tri-State-River-Valley-Engineering-System** | `docs/ptdt-v32` OpenMI ICD, evidence manifest schema |
| **Tri-County-River-Valley-Digital-Twin** | site-specific GIS exports if any |

## Already merged (PR #10 squash)
Cinematic runtime, parcels/PMTiles, BAFL docs, MapLibre wiring, CI green.

## Operator still required
- Sealed DEM COG under `data/cog/`
- BAFL `.shp` under `data/bafl/posey/`
- Licensed RAS plan HDF under `data/ras/`
- Deed-reconciled single APN for LOMA filing

## MapLibre note
`bonebank_buildings.geojson` is **EPSG:2966**. MapLibre `geojson` sources expect **EPSG:4326** unless you reproject client-side or serve via PostGIS/tippecanoe.
