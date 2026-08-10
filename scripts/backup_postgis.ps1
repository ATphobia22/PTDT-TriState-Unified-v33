# PostGIS backup examples (PTDT)
# Prerequisites: docker compose up -d  (container ptdt_postgis, volume ./volumes/backups)

param(
  [ValidateSet("full", "data-only", "schema-only", "tables")]
  [string]$Mode = "full",
  [string]$OutDir = ".\volumes\backups",
  [string]$Container = "ptdt_postgis",
  [string]$Db = "ptdt",
  [string]$User = "ptdt",
  [string[]]$Tables = @("twin_ras_cells", "twin_static_parcels")
)

$ErrorActionPreference = "Stop"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$stamp = Get-Date -Format "yyyyMMdd_HHmmss"

switch ($Mode) {
  "full" {
    # Example 1 — full custom-format dump (best for pg_restore)
    $name = "ptdt_full_$stamp.dump"
    Write-Host "FULL custom dump → volumes/backups/$name"
    docker exec $Container pg_dump -U $User -d $Db -Fc -f "/backups/$name"
  }
  "data-only" {
    # Example 2 — data only (keep schema; faster refresh)
    $name = "ptdt_data_$stamp.dump"
    Write-Host "DATA-ONLY → volumes/backups/$name"
    docker exec $Container pg_dump -U $User -d $Db -Fc --data-only -f "/backups/$name"
  }
  "schema-only" {
    # Example 3 — schema only (DDL)
    $name = "ptdt_schema_$stamp.sql"
    Write-Host "SCHEMA-ONLY → volumes/backups/$name"
    docker exec $Container pg_dump -U $User -d $Db --schema-only --no-owner |
      Set-Content (Join-Path $OutDir $name) -Encoding utf8
  }
  "tables" {
    # Example 4 — selected tables
    $name = "ptdt_tables_$stamp.dump"
    $targs = ($Tables | ForEach-Object { "-t"; $_ })
    Write-Host "TABLES [$($Tables -join ', ')] → volumes/backups/$name"
    docker exec $Container pg_dump -U $User -d $Db -Fc @targs -f "/backups/$name"
  }
}

# Example 5 — plain SQL full (portable text)
$sqlName = "ptdt_plain_$stamp.sql"
Write-Host "Also writing plain SQL → volumes/backups/$sqlName"
docker exec $Container pg_dump -U $User -d $Db --no-owner --no-acl |
  Set-Content (Join-Path $OutDir $sqlName) -Encoding utf8

# Retention: keep 14 newest files
Get-ChildItem $OutDir -File -ErrorAction SilentlyContinue |
  Where-Object { $_.Name -like "ptdt_*" } |
  Sort-Object LastWriteTime -Descending |
  Select-Object -Skip 14 |
  Remove-Item -Force -ErrorAction SilentlyContinue

Write-Host "Done. List:"
Get-ChildItem $OutDir -Filter "ptdt_*" | Sort-Object LastWriteTime -Descending | Select-Object -First 5 Name, Length, LastWriteTime
