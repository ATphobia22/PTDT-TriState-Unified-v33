# Building footprints — Microsoft, Overture, operator path

## Priority (PTDT)

1. Local sealed survey / assessor footprints  
2. **Microsoft US Building Footprints — Indiana state GeoJSON**  
3. Overture Maps buildings (height enrichment)  
4. OSM only where others are empty  

Do not ship a placeholder FeatureCollection under `data/geo/bonebank_buildings.geojson`.

## Microsoft USBuildingFootprints (Indiana)

| Item | Value |
|------|--------|
| Upstream | https://github.com/microsoft/USBuildingFootprints |
| **Indiana zip** | https://minedbuildings.z5.web.core.windows.net/legacy/usbuildings-v2/Indiana.geojson.zip |
| Count | ~3,379,648 buildings |
| Size | ~920 MiB unzipped |
| CRS | **EPSG:4326** |
| License | ODbL |
| Heights | Not in legacy state pack (2D only) |

Global ML set (heights subset, CDLA Permissive 2.0):  
https://github.com/microsoft/GlobalMLBuildingFootprints  
Links CSV (2026 host): `https://bfppub.blob.core.windows.net/$web/2026-07-24/dataset-links.csv`  

**Note:** `ATphobia22/GlobalMLBuildingFootprints` is not a distinct published data source; use Microsoft upstream.

### Operator

```bash
bash scripts/fetch_bonebank_buildings.sh
# or manually:
curl -L -o /tmp/Indiana.geojson.zip \
  "https://minedbuildings.z5.web.core.windows.net/legacy/usbuildings-v2/Indiana.geojson.zip"
unzip -o /tmp/Indiana.geojson.zip -d /tmp
ogr2ogr -f GeoJSON -t_srs EPSG:2966 \
  -clipsrc -88.02 37.88 -87.98 37.93 \
  data/geo/bonebank_buildings.geojson /tmp/Indiana.geojson
sha256sum data/geo/bonebank_buildings.geojson > data/geo/bonebank_buildings.sha256
```

Tighten `-clipsrc` to the sealed site envelope after deed survey.

## Overture Maps buildings (GeoParquet → 2966)

- Cloud: `s3://overturemaps-us-west-2/release/<date>/theme=buildings/type=building/*`  
- CRS on wire: **EPSG:4326**  
- May include **height / num_floors**  

```bash
pip install overturemaps
overtruemaps download \
  --bbox=-88.02,37.88,-87.98,37.93 \
  -f geojson --type=building \
  -o data/geo/bonebank_overture_4326.geojson

ogr2ogr -f GeoJSON -t_srs EPSG:2966 \
  data/geo/bonebank_overture_2966.geojson \
  data/geo/bonebank_overture_4326.geojson
```

(`overturemaps` package; fix typo if shell alias interferes.)

## MapLibre / WebGPU

- Display may use 4326 sources.  
- **Sealed regulatory geometry** and cell-index alignment stay **EPSG:2966**.  
- Extrusion: prefer Overture/local height; else constant or LAG-relative only for viz (not LOMA).
