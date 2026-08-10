#==============================================================================
# load_raster.ps1 — Tile GeoTIFF into PostGIS twin_rasters (256x256 default)
# Requires: raster2pgsql (GDAL/OSGeo4W) on PATH; container ptdt_postgis up
#
# Example:
#   .\scripts\load_raster.ps1 .\volumes\gis_import\depth.tif -PlanId 01
#==============================================================================
param(
  [Parameter(Mandatory = $true)][string]$TifPath,
  [string]$PlanId = "baseline",
  [string]$Table = "twin_rasters",
  [string]$Srid = "4326",
  [string]$Tile = "256x256",
  [string]$Container = "ptdt_postgis",
  [string]$Db = "ptdt",
  [string]$User = "ptdt"
)

$ErrorActionPreference = "Stop"
if (-not (Test-Path $TifPath)) { throw "Missing $TifPath" }
if (-not (Get-Command raster2pgsql -ErrorAction SilentlyContinue)) {
  throw "raster2pgsql not found. Install GDAL/OSGeo4W."
}

# -I GIST  -C constraints  -M vacuum  -t tiles  -Y copy mode
$sql = & raster2pgsql -s $Srid -I -C -M -t $Tile -Y $TifPath "public.$Table"
$sql | docker exec -i $Container psql -U $User -d $Db
if ($LASTEXITCODE -ne 0) { throw "raster load failed" }

docker exec $Container psql -U $User -d $Db -c "UPDATE public.$Table SET plan_id = '$PlanId' WHERE plan_id IS NULL;"
Write-Host "Loaded $TifPath → $Table ($Tile), plan_id=$PlanId"
