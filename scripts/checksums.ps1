# SHA256 checksums for release artifacts
# Usage: .\scripts\checksums.ps1
#        .\scripts\checksums.ps1 -Verify

param(
  [string]$ReleaseDir = ".\release",
  [switch]$Verify
)

$ErrorActionPreference = "Stop"
if (-not (Test-Path $ReleaseDir)) { throw "Missing $ReleaseDir — run dist:win first" }

$files = Get-ChildItem $ReleaseDir -File | Where-Object {
  $_.Extension -match '\.(exe|yml|blockmap)$' -or $_.Name -like '*.exe'
}

if ($Verify) {
  $sumFile = Join-Path $ReleaseDir "SHA256SUMS.txt"
  if (-not (Test-Path $sumFile)) { throw "SHA256SUMS.txt not found" }
  Write-Host "Verifying against SHA256SUMS.txt" -ForegroundColor Cyan
  Get-Content $sumFile | ForEach-Object {
    if ($_ -match '^([A-Fa-f0-9]{64})\s+(.+)$') {
      $expected = $Matches[1].ToUpperInvariant()
      $name = $Matches[2].Trim()
      $path = Join-Path $ReleaseDir $name
      if (-not (Test-Path $path)) {
        Write-Host "MISSING  $name" -ForegroundColor Red
        return
      }
      $actual = (Get-FileHash -Algorithm SHA256 -Path $path).Hash
      if ($actual -eq $expected) {
        Write-Host "OK       $name" -ForegroundColor Green
      } else {
        Write-Host "FAIL     $name" -ForegroundColor Red
        Write-Host "  expected $expected"
        Write-Host "  actual   $actual"
      }
    }
  }
  return
}

$lines = @()
foreach ($f in $files) {
  $hash = (Get-FileHash -Algorithm SHA256 -Path $f.FullName).Hash
  $lines += "$hash  $($f.Name)"
  Write-Host "$hash  $($f.Name)"
}

$out = Join-Path $ReleaseDir "SHA256SUMS.txt"
$lines | Set-Content -Path $out -Encoding ascii
Write-Host ""
Write-Host "Wrote $out" -ForegroundColor Green
