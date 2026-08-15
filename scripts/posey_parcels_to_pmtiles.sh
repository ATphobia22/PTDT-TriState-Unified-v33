#!/usr/bin/env bash
# Posey bbox → paginated FeatureServer GeoJSON → tippecanoe → PMTiles
# Tippecanoe optimize (felt/mapbox tippecanoe):
#   -zg auto max zoom | --drop-densest-as-needed | --extend-zooms-if-still-dropping
#   -l parcels | --detect-shared-borders for polygons | -y keep only needed attrs
# Viewer: https://pmtiles.io  |  MapLibre: npm pmtiles Protocol + pmtiles:// URL
set -euo pipefail

LAYER="${LAYER:-https://gisdata.in.gov/server/rest/services/Hosted/Parcel_Boundaries_of_Indiana_2025/FeatureServer/0}"
OUT_DIR="${OUT_DIR:-./runtime_assets/parcels}"
PAGE=2000
WEST="${WEST:--88.05}"
SOUTH="${SOUTH:-37.85}"
EAST="${EAST:--87.95}"
NORTH="${NORTH:-37.95}"

mkdir -p "${OUT_DIR}/pages"
rm -f "${OUT_DIR}/pages"/*.geojson "${OUT_DIR}/posey_parcels.geojson" || true

offset=0
page=0
while true; do
  geom=$(printf '{"xmin":%s,"ymin":%s,"xmax":%s,"ymax":%s,"spatialReference":{"wkid":4326}}' "$WEST" "$SOUTH" "$EAST" "$NORTH")
  enc=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$geom")
  url="${LAYER}/query?f=geojson&where=1%3D1&geometry=${enc}&geometryType=esriGeometryEnvelope&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=*&returnGeometry=true&resultOffset=${offset}&resultRecordCount=${PAGE}"
  out="${OUT_DIR}/pages/page_${page}.geojson"
  echo "Fetching offset=${offset}"
  curl -fsSL "$url" -o "$out"
  count=$(jq '.features | length' "$out")
  echo "  features=${count}"
  [[ "$count" -eq 0 ]] && { rm -f "$out"; break; }
  offset=$((offset + count))
  page=$((page + 1))
  [[ "$count" -lt "$PAGE" || "$page" -ge 25 ]] && break
done

jq -s '{type:"FeatureCollection", features: map(.features) | add}' "${OUT_DIR}/pages"/*.geojson \
  > "${OUT_DIR}/posey_parcels.geojson"

if ! command -v tippecanoe >/dev/null 2>&1; then
  echo "Install tippecanoe (felt/tippecanoe). GeoJSON at ${OUT_DIR}/posey_parcels.geojson"
  exit 0
fi

# Recommended optimize set for cadastre polygons
tippecanoe \
  -o "${OUT_DIR}/posey_parcels.pmtiles" \
  -zg \
  -Z10 \
  -l parcels \
  --drop-densest-as-needed \
  --extend-zooms-if-still-dropping \
  --detect-shared-borders \
  --coalesce-densest-as-needed \
  -P \
  "${OUT_DIR}/posey_parcels.geojson"

echo "Wrote ${OUT_DIR}/posey_parcels.pmtiles — inspect at https://pmtiles.io"
