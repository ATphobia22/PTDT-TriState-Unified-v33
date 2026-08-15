#!/usr/bin/env bash
# IGIO elevation (S3 LAS/DEM products) → runtime COG for presentation / GPU depth bake.
# Regulatory LOMA Z still requires sealed survey / elevation certificate.
# Horizontal: prefer project EPSG:2966 (IN State Plane West) when warping site clips.
# AWS open data: aws s3 ls --no-sign-request s3://giselevationingov/
set -euo pipefail

RAW_DIR="${1:-./raw_dem}"
OUT="${2:-./runtime_assets/posey_bare_earth_navd88.tif}"
TARGET_SRS="${TARGET_SRS:-EPSG:2966}"

mkdir -p "$(dirname "$OUT")" "${RAW_DIR}"

echo "=== VRT mosaic ==="
gdalbuildvrt "${RAW_DIR}/input_mosaic.vrt" "${RAW_DIR}"/*.tif

echo "=== Warp to ${TARGET_SRS} ==="
# Source SRS must match input tiles (do not assume 4326 for all IGIO products).
gdalwarp \
  -t_srs "${TARGET_SRS}" \
  -r bilinear \
  -of VRT \
  "${RAW_DIR}/input_mosaic.vrt" \
  "${RAW_DIR}/projected_target.vrt"

echo "=== COG ==="
gdal_translate \
  "${RAW_DIR}/projected_target.vrt" \
  "${OUT}" \
  -of COG \
  -co COMPRESS=DEFLATE \
  -co PREDICTOR=3 \
  -co NUM_THREADS=ALL_CPUS \
  -co BIGTIFF=YES

gdalinfo "${OUT}" -stats
echo "Wrote ${OUT}"
