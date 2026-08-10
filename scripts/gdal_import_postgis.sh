#!/usr/bin/env bash
# GDAL/OGR → PostGIS import for PTDT
# Requires: ogr2ogr (GDAL), PostGIS on localhost:8087
set -euo pipefail

HOST="${POSTGRES_HOST:-127.0.0.1}"
PORT="${POSTGRES_PORT:-8087}"
DB="${POSTGRES_DB:-ptdt}"
USER="${POSTGRES_USER:-ptdt}"
PASS="${POSTGRES_PASSWORD:-ptdt}"
PG="PG:host=${HOST} port=${PORT} dbname=${DB} user=${USER} password=${PASS}"

SRC="${1:?Usage: $0 <shapefile|geojson|gpkg> [layer_name]}"
LAYER="${2:-}"

ARGS=(
  -f PostgreSQL
  "$PG"
  "$SRC"
  -nln twin_static_parcels_import
  -nlt PROMOTE_TO_MULTI
  -t_srs EPSG:4326
  -lco GEOMETRY_NAME=geom
  -lco FID=gid
  -lco PRECISION=NO
  --config PG_USE_COPY YES
  -overwrite
)

if [[ -n "$LAYER" ]]; then
  ARGS+=("$LAYER")
fi

echo "Importing $SRC → twin_static_parcels_import"
ogr2ogr "${ARGS[@]}"
echo "Done. Reindex/merge into twin_static_parcels as needed."
