#!/usr/bin/env bash
# Microsoft Indiana building footprints → sealed Bonebank clip in EPSG:2966.
# Optional: Overture bbox extract for height enrichment.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT_DIR="${ROOT}/data/geo"
WORKDIR="${TMPDIR:-/tmp}/ptdt_buildings_$$"
# WGS84 clip — tighten after deed survey of 13101 Bonebank Rd / Sec 35
CLIP_W="${CLIP_W:--88.02}"
CLIP_S="${CLIP_S:-37.88}"
CLIP_E="${CLIP_E:--87.98}"
CLIP_N="${CLIP_N:-37.93}"
MS_URL="https://minedbuildings.z5.web.core.windows.net/legacy/usbuildings-v2/Indiana.geojson.zip"
OUT_MS="${OUT_DIR}/bonebank_buildings.geojson"

mkdir -p "${OUT_DIR}" "${WORKDIR}"
cd "${WORKDIR}"

echo "=== Download Microsoft Indiana GeoJSON ==="
if command -v curl >/dev/null 2>&1; then
  curl -L --fail -o Indiana.geojson.zip "${MS_URL}"
elif command -v wget >/dev/null 2>&1; then
  wget -O Indiana.geojson.zip "${MS_URL}"
else
  echo "ERROR: need curl or wget"
  exit 1
fi

unzip -o Indiana.geojson.zip
if [[ ! -f Indiana.geojson ]]; then
  # some zips nest the file
  IN_JSON="$(find . -name 'Indiana.geojson' -type f | head -1)"
  if [[ -z "${IN_JSON}" ]]; then
    echo "ERROR: Indiana.geojson not found in zip"
    exit 1
  fi
else
  IN_JSON="Indiana.geojson"
fi

echo "=== Clip + reproject to EPSG:2966 ==="
ogr2ogr -f GeoJSON \
  -t_srs EPSG:2966 \
  -s_srs EPSG:4326 \
  -clipsrc "${CLIP_W}" "${CLIP_S}" "${CLIP_E}" "${CLIP_N}" \
  "${OUT_MS}" \
  "${IN_JSON}"

sha256sum "${OUT_MS}" | tee "${OUT_DIR}/bonebank_buildings.sha256"
echo "Wrote ${OUT_MS}"

if command -v overturemaps >/dev/null 2>&1; then
  echo "=== Optional Overture buildings (height) ==="
  overturemaps download \
    --bbox="${CLIP_W},${CLIP_S},${CLIP_E},${CLIP_N}" \
    -f geojson \
    --type=building \
    -o "${OUT_DIR}/bonebank_overture_4326.geojson" || true
  if [[ -f "${OUT_DIR}/bonebank_overture_4326.geojson" ]]; then
    ogr2ogr -f GeoJSON -t_srs EPSG:2966 \
      "${OUT_DIR}/bonebank_overture_2966.geojson" \
      "${OUT_DIR}/bonebank_overture_4326.geojson"
    sha256sum "${OUT_DIR}/bonebank_overture_2966.geojson" \
      | tee "${OUT_DIR}/bonebank_overture_2966.sha256"
  fi
else
  echo "SKIP Overture: pip install overturemaps to enable height enrichment"
fi

rm -rf "${WORKDIR}"
echo "Done."
