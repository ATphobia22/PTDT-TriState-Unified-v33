#!/usr/bin/env bash
# Convert Posey BAFL shapefiles (EPSG:26916) → GeoJSON EPSG:4326 for MapLibre.
# Engineering ingest remains python/dnr_regulatory_bridge.py (EPSG:2966 + seal).
set -euo pipefail
ROOT="${1:-data/bafl/posey}"
OUT="${2:-data/bafl}"
mkdir -p "$OUT"

if [[ ! -f "$ROOT/FloodHazard_BestAvai_DNR_Water.shp" ]]; then
  echo "SOFT_FAIL: missing $ROOT/FloodHazard_BestAvai_DNR_Water.shp"
  exit 0
fi

ogr2ogr -t_srs EPSG:4326 -f GeoJSON \
  "$OUT/posey_flood_hazard_4326.geojson" \
  "$ROOT/FloodHazard_BestAvai_DNR_Water.shp"

if [[ -f "$ROOT/Flood_Elevation_Pts_DNR_Water.shp" ]]; then
  ogr2ogr -t_srs EPSG:4326 -f GeoJSON \
    "$OUT/posey_elev_pts_4326.geojson" \
    "$ROOT/Flood_Elevation_Pts_DNR_Water.shp"
  echo "Wrote $OUT/posey_elev_pts_4326.geojson"
else
  echo "SOFT_FAIL: missing elevation points shp"
fi

echo "Wrote $OUT/posey_flood_hazard_4326.geojson"
