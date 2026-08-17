#!/usr/bin/env bash
# Convert Posey BAFL shapefiles (native EPSG:26916) →
#   - GeoJSON EPSG:4326 for MapLibre display
#   - GeoJSON EPSG:2966 for engineering / seal alignment
# Engineering ingest may also use python/dnr_regulatory_bridge.py.
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

ogr2ogr -t_srs EPSG:2966 -f GeoJSON \
  "$OUT/posey_flood_hazard_2966.geojson" \
  "$ROOT/FloodHazard_BestAvai_DNR_Water.shp"

if [[ -f "$ROOT/Flood_Elevation_Pts_DNR_Water.shp" ]]; then
  ogr2ogr -t_srs EPSG:4326 -f GeoJSON \
    "$OUT/posey_elev_pts_4326.geojson" \
    "$ROOT/Flood_Elevation_Pts_DNR_Water.shp"
  ogr2ogr -t_srs EPSG:2966 -f GeoJSON \
    "$OUT/posey_elev_pts_2966.geojson" \
    "$ROOT/Flood_Elevation_Pts_DNR_Water.shp"
  echo "Wrote elev pts 4326 + 2966"
else
  echo "SOFT_FAIL: missing elevation points shp"
fi

if command -v sha256sum >/dev/null 2>&1; then
  sha256sum \
    "$ROOT/FloodHazard_BestAvai_DNR_Water.shp" \
    "$OUT/posey_flood_hazard_2966.geojson" \
    > "$OUT/BAFL_POSEY.sha256" || true
fi

echo "Wrote $OUT/posey_flood_hazard_4326.geojson and _2966.geojson"
