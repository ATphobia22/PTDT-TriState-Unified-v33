#==============================================================================
# backup_postgis.ps1 — PTDT PostGIS dumps into ./volumes/backups
# Requires: docker container ptdt_postgis running, backups volume mounted
#
# Examples:
#   .\scripts\backup_postgis.ps1 -Mode full
#   .\scripts\backup_postgis.ps1 -Mode data-only
#   .\scripts\backup_postgis.ps1 -Mode schema-only
#   .\scripts\backup_postgis.ps1 -Mode tables -Tables twin_ras_cells,twin_rasters
#==============================================================================
param(
  [ValidateSet("full", "data-only", "schema-only", "tables")]
  [string]$Mode = "full",
  [string]$OutDir = ".\volumes\backups",
  [string]$Container = "ptdt_postgis",
  [string]$Db = "ptdt",
  [string]$User = "ptdt",
  [string[]]$Tables = @("twin_ras_cells", "twin_static_parcels", "twin_rasters")
)

$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"

switch ($Mode) {
  "full" {
    $name = "ptdt_full_$stamp.dump"
    Write-Host "FULL custom dump → volumes/backups/$name"
    docker exec $Container pg_dump -U $User -d $Db -Fc -f "/backups/$name"
  }
  "data-only" {
    $name = "ptdt_data_$stamp.dump"
    Write-Host "DATA-ONLY → volumes/backups/$name"
    docker exec $Container pg_dump -U $User -d $Db -Fc --data-only -f "/backups/$name"
  }
  "schema-only" {
    $name = "ptdt_schema_$stamp.sql"
    Write-Host "SCHEMA-ONLY → volumes/backups/$name"
    docker exec $Container pg_dump -U $User -d $Db --schema-only --no-owner |
      Set-Content (Join-Path $OutDir $name) -Encoding utf8
  }
  "tables" {
    $name = "ptdt_tables_$stamp.dump"
    $targs = foreach ($t in $Tables) { @("-t", $t) }
    Write-Host "TABLES [$($Tables -join ', ')] → volumes/backups/$name"
    docker exec $Container pg_dump -U $User -d $Db -Fc @targs -f "/backups/$name"
  }
}

$sqlName = "ptdt_plain_$stamp.sql"
Write-Host "Plain SQL → volumes/backups/$sqlName"
docker exec $Container pg_dump -U $User -d $Db --no-owner --no-acl |
  Set-Content (Join-Path $OutDir $sqlName) -Encoding utf8

Get-ChildItem $OutDir -File -ErrorAction SilentlyContinue |
  Where-Object { $_.Name -like "ptdt_*" } |
  Sort-Object LastWriteTime -Descending |
  Select-Object -Skip 14 |
  Remove-Item -Force -ErrorAction SilentlyContinue

Write-Host "Done."
Get-ChildItem $OutDir -Filter "ptdt_*" | Sort-Object LastWriteTime -Descending |
  Select-Object -First 5 Name, Length, LastWriteTime
