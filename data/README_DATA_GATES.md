# Data gates (operator actions)

| Gate | Path / action |
|------|----------------|
| APN dual-ID | Edit `data/site/bonebank_site_record.json` after Posey XSoft Engage + deed match; set `apn_status` to `VERIFIED` and single `apn` |
| Sealed COGs | Place NAVD88 DEM/ortho under `data/cogs/`; run GDAL `gdal_translate -of COG` |
| Buildings | Replace `data/buildings/bonebank_buildings.geojson` empty features with real footprints |
| HEC-RAS | Install licensed RAS; put plan HDF under `data/ras/`; soft-fail if missing |

Code never fabricates hydraulic results or parcel IDs.
