#!/usr/bin/env bash
# Extract Posey County building footprints from IGIO FeatureServer → EPSG:2966 GeoJSON.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="${ROOT}/data/geo"
WORKDIR="${TMPDIR:-/tmp}/ptdt_igio_bldg_$$"
BASE="https://gisdata.in.gov/server/rest/services/Hosted/Building_Footprints/FeatureServer/0/query"
OUT_4326="${OUT_DIR}/posey_buildings_igio_4326.geojson"
OUT_2966="${OUT_DIR}/posey_buildings_igio_2966.geojson"
PAGE=2000
OFFSET=0

mkdir -p "${OUT_DIR}" "${WORKDIR}"
cd "${WORKDIR}"

echo "=== Paginated IGIO query (county=Posey) ==="
PARTS=()
i=0
while true; do
  PART="page_${i}.geojson"
  URL="${BASE}?where=county%3D%27Posey%27&outFields=objectid,lidaryear,county&returnGeometry=true&outSR=4326&f=geojson&resultRecordCount=${PAGE}&resultOffset=${OFFSET}"
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL -o "${PART}" "${URL}" || {
      echo "SOFT_FAIL: IGIO query failed at offset ${OFFSET}"
      exit 0
    }
  else
    echo "ERROR: curl required"
    exit 1
  fi
  # Count features roughly
  N=$(grep -o '"type"[[:space:]]*:[[:space:]]*"Feature"' "${PART}" | wc -l | tr -d ' ')
  echo "offset=${OFFSET} features≈${N}"
  PARTS+=("${PART}")
  if [[ "${N}" -lt "${PAGE}" ]]; then
    break
  fi
  OFFSET=$((OFFSET + PAGE))
  i=$((i + 1))
  if [[ "${i}" -gt 500 ]]; then
    echo "ERROR: pagination safety stop"
    exit 1
  fi
done

if command -v ogrmerge.py >/dev/null 2>&1; then
  ogrmerge.py -o merged.geojson -f GeoJSON "${PARTS[@]}" -single -nln buildings
elif command -v ogr2ogr >/dev/null 2>&1; then
  # Sequential append
  ogr2ogr -f GeoJSON merged.geojson "${PARTS[0]}"
  for ((j=1; j<${#PARTS[@]}; j++)); do
    ogr2ogr -f GeoJSON -append merged.geojson "${PARTS[$j]}" || true
  done
else
  echo "ERROR: need gdal/ogr2ogr"
  exit 1
fi

cp -f merged.geojson "${OUT_4326}"
ogr2ogr -f GeoJSON -t_srs EPSG:2966 -s_srs EPSG:4326 "${OUT_2966}" "${OUT_4326}"

if command -v sha256sum >/dev/null 2>&1; then
  sha256sum "${OUT_2966}" | tee "${OUT_DIR}/posey_buildings_igio_2966.sha256"
fi

echo "Wrote ${OUT_2966}"
echo "Optional Bonebank clip:"
echo "  ogr2ogr -f GeoJSON -clipsrc -88.02 37.88 -87.98 37.93 ${OUT_DIR}/bonebank_buildings.geojson ${OUT_2966}"

rm -rf "${WORKDIR}"
