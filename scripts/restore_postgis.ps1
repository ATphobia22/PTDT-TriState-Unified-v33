param(
  [Parameter(Mandatory = $true)][string]$DumpPath,
  [string]$Container = "ptdt_postgis",
  [string]$Db = "ptdt",
  [string]$User = "ptdt"
)
$ErrorActionPreference = "Stop"
if (-not (Test-Path $DumpPath)) { throw "File not found: $DumpPath" }

$name = Split-Path $DumpPath -Leaf
# Assume dump is under volumes/backups mounted at /backups
docker exec -i $Container pg_restore -U $User -d $Db --clean --if-exists "/backups/$name"
if ($LASTEXITCODE -ne 0) {
  Write-Host "pg_restore failed; trying plain SQL..."
  Get-Content $DumpPath -Raw | docker exec -i $Container psql -U $User -d $Db
}
Write-Host "Restore finished."
