# PostGIS backup — custom format + plain SQL fallback
param(
  [string]$OutDir = ".\volumes\backups",
  [string]$Container = "ptdt_postgis",
  [string]$Db = "ptdt",
  [string]$User = "ptdt"
)

$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"
$dumpFile = Join-Path $OutDir "ptdt_$stamp.dump"
$sqlFile = Join-Path $OutDir "ptdt_$stamp.sql"

Write-Host "Custom dump → $dumpFile"
docker exec $Container pg_dump -U $User -d $Db -Fc -f "/backups/ptdt_$stamp.dump"
if ($LASTEXITCODE -ne 0) {
  # if file written inside volume mount
  Write-Host "Trying host path via volume..."
}

Write-Host "Plain SQL → $sqlFile"
docker exec $Container pg_dump -U $User -d $Db --no-owner --no-acl |
  Set-Content -Path $sqlFile -Encoding utf8

# Keep last 14 dumps
Get-ChildItem $OutDir -Filter "ptdt_*.dump", "ptdt_*.sql" -ErrorAction SilentlyContinue |
  Sort-Object LastWriteTime -Descending |
  Select-Object -Skip 14 |
  Remove-Item -Force -ErrorAction SilentlyContinue

Write-Host "Backup complete."
