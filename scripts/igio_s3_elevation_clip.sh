#!/usr/bin/env bash
# Site-bbox clip workflow for IGIO elevation open data.
# Bucket: s3://giselevationingov/ (us-east-2, no-sign-request)
# Docs: https://elevation.gio.in.gov/ | https://registry.opendata.aws/in-elevation
#
# LAS tiles use lower-left coordinate naming; list then download only tiles
# intersecting your site envelope. Default bbox ≈ Bonebank / Point Township.
set -euo pipefail

BUCKET="s3://giselevationingov"
OUT_DIR="${OUT_DIR:-./input_pointclouds}"
# WGS84 envelope for 13101 Bonebank vicinity
WEST="${WEST:--88.02}"
SOUTH="${SOUTH:-37.89}"
EAST="${EAST:--87.98}"
NORTH="${NORTH:-37.92}"

mkdir -p "${OUT_DIR}"

echo "=== Listing elevation bucket prefixes (no AWS account) ==="
aws s3 ls --no-sign-request "${BUCKET}/" | head -n 40

echo ""
echo "Manual step: identify Posey / Tier path from listing + IGIO tile index,"
echo "then download only intersecting LAS. Example:"
echo "  aws s3 cp --no-sign-request ${BUCKET}/<tier>/<tile>.las ${OUT_DIR}/"
echo ""
echo "Site bbox (WGS84): ${WEST},${SOUTH} → ${EAST},${NORTH}"
echo "After LAS in ${OUT_DIR}:"
echo "  pdal pipeline scripts/pdal_extract_ground.json"
echo "  bash scripts/cog_bare_earth_navd88.sh ./raw_dem ./runtime_assets/posey_bare_earth_navd88.tif"
echo ""
echo "Imagery COGs (optional): aws s3 ls --no-sign-request s3://gisimageryingov/"
