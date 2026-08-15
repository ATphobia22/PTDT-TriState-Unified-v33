#!/usr/bin/env bash
# Posey / Bonebank bbox → GeoJSON (paginated FeatureServer) → tippecanoe → PMTiles
# Requires: curl, jq, tippecanoe (or tile-join), optional pmtiles CLI
set -euo pipefail

LAYER="${LAYER:-https://gisdata.in.gov/server/rest/services/Hosted/Parcel_Boundaries_of_Indiana_2025/FeatureServer/0}"
OUT_DIR="${OUT_DIR:-./runtime_assets/parcels}"
PAGE=2000
WEST="${WEST:--88.05}"
SOUTH="${SOUTH:-37.85}"
EAST="${EAST:--87.95}"
NORTH="${NORTH:-37.95}"

mkdir -p "${OUT_DIR}"
TMP="${OUT_DIR}/pages"
mkdir -p "${TMP}"
rm -f "${TMP}"/*.geojson "${OUT_DIR}/posey_parcels.geojson"

offset=0
page=0
while true; do
  geom=$(printf '{"xmin":%s,"ymin":%s,"xmax":%s,"ymax":%s,"spatialReference":{"wkid":4326}}' "$WEST" "$SOUTH" "$EAST" "$NORTH")
  url="${LAYER}/query?f=geojson&where=1%3D1&geometry=$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "$geom")&geometryType=esriGeometryEnvelope&inSR=4326&spatialRel=esriSpatialRelIntersects&outFields=*&returnGeometry=true&resultOffset=${offset}&resultRecordCount=${PAGE}"
  out="${TMP}/page_${page}.geojson"
  echo "Fetching offset=${offset} → ${out}"
  curl -fsSL "$url" -o "$out"
  count=$(jq '.features | length' "$out")
  echo "  features=${count}"
  if [[ "$count" -eq 0 ]]; then
    rm -f "$out"
    break
  fi
  offset=$((offset + count))
  page=$((page + 1))
  if [[ "$count" -lt "$PAGE" ]]; then
    break
  fi
  if [[ "$page" -ge 25 ]]; then
    echo "Hit page cap 25" >&2
    break
  fi
done

echo "Merging pages..."
jq -s '{type:"FeatureCollection", features: map(.features) | add}' "${TMP}"/*.geojson \
  > "${OUT_DIR}/posey_parcels.geojson"

if ! command -v tippecanoe >/dev/null 2>&1; then
  echo "tippecanoe not installed; GeoJSON written to ${OUT_DIR}/posey_parcels.geojson"
  exit 0
fi

tippecanoe \
  -o "${OUT_DIR}/posey_parcels.pmtiles" \
  -Z10 -z16 \
  -l parcels \
  --drop-densest-as-needed \
  --extend-zooms-if-still-dropping \
  -P \
  "${OUT_DIR}/posey_parcels.geojson"

echo "Wrote ${OUT_DIR}/posey_parcels.pmtiles"
