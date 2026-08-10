# GDAL/OGR → PostGIS (Windows)
# Install GDAL: winget install OSGeo.GDAL   OR  conda install -c conda-forge gdal
param(
  [Parameter(Mandatory = $true)][string]$Source,
  [string]$Layer = ""
)

$HostName = if ($env:POSTGRES_HOST) { $env:POSTGRES_HOST } else { "127.0.0.1" }
$Port = if ($env:POSTGRES_PORT) { $env:POSTGRES_PORT } else { "8087" }
$Db = if ($env:POSTGRES_DB) { $env:POSTGRES_DB } else { "ptdt" }
$User = if ($env:POSTGRES_USER) { $env:POSTGRES_USER } else { "ptdt" }
$Pass = if ($env:POSTGRES_PASSWORD) { $env:POSTGRES_PASSWORD } else { "ptdt" }
$Pg = "PG:host=$HostName port=$Port dbname=$Db user=$User password=$Pass"

$argsList = @(
  "-f", "PostgreSQL", $Pg, $Source,
  "-nln", "twin_static_parcels_import",
  "-nlt", "PROMOTE_TO_MULTI",
  "-t_srs", "EPSG:4326",
  "-lco", "GEOMETRY_NAME=geom",
  "-lco", "FID=gid",
  "-lco", "PRECISION=NO",
  "--config", "PG_USE_COPY", "YES",
  "-overwrite"
)
if ($Layer) { $argsList += $Layer }

Write-Host "Importing $Source → PostGIS"
& ogr2ogr @argsList
if ($LASTEXITCODE -ne 0) { throw "ogr2ogr failed" }
Write-Host "Done."
