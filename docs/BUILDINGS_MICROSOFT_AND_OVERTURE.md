# Building footprints — IGIO, Microsoft, Overture

## Priority (PTDT)

1. Local sealed survey / assessor footprints  
2. **IGIO Indiana Building Footprints 2016–2020** (`docs/IGIO_BUILDING_FOOTPRINTS.md`, `scripts/fetch_igio_posey_buildings.sh`)  
3. **Microsoft US Building Footprints — Indiana** state GeoJSON  
4. Overture Maps buildings (height enrichment)  
5. OSM only where others are empty  

Do not ship a placeholder FeatureCollection under `data/geo/bonebank_buildings.geojson`.

## IGIO (preferred state LiDAR-era)

```bash
bash scripts/fetch_igio_posey_buildings.sh
# Then clip to site if needed → data/geo/bonebank_buildings.geojson + SHA-256
```

Service: https://gisdata.in.gov/server/rest/services/Hosted/Building_Footprints/FeatureServer/0  
Native CRS: EPSG:3857 → outSR=4326 on query → seal in **EPSG:2966**.

## Microsoft USBuildingFootprints (Indiana)

| Item | Value |
|------|--------|
| Upstream | https://github.com/microsoft/USBuildingFootprints |
| **Indiana zip** | https://minedbuildings.z5.web.core.windows.net/legacy/usbuildings-v2/Indiana.geojson.zip |
| Count | ~3,379,648 buildings |
| CRS | **EPSG:4326** |
| License | ODbL |

```bash
bash scripts/fetch_bonebank_buildings.sh
```

Global ML set: https://github.com/microsoft/GlobalMLBuildingFootprints  
(`ATphobia22/GlobalMLBuildingFootprints` is not a distinct published data host.)

## Overture Maps (height)

```bash
pip install overturemaps
overtruemaps download --bbox=-88.02,37.88,-87.98,37.93 \
  -f geojson --type=building -o data/geo/bonebank_overture_4326.geojson
ogr2ogr -f GeoJSON -t_srs EPSG:2966 \
  data/geo/bonebank_overture_2966.geojson data/geo/bonebank_overture_4326.geojson
```

## MapLibre / WebGPU

- Display may use 4326 sources.  
- **Sealed regulatory geometry** stays **EPSG:2966**.  
- Extrusion: prefer Overture/local height; else viz-only constants (not LOMA).
