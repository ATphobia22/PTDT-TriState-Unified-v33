# PTDT Unified V33 — optimized Windows build + checksums
$ErrorActionPreference = "Stop"
$Root = if ($PSScriptRoot) { (Resolve-Path (Join-Path $PSScriptRoot "..")).Path } else { (Get-Location).Path }
Set-Location $Root

Write-Host "=== npm install ===" -ForegroundColor Cyan
npm install
if ($LASTEXITCODE -ne 0) { throw "npm install failed" }

Write-Host "=== vite build (minified, chunked) ===" -ForegroundColor Cyan
npm run build
if ($LASTEXITCODE -ne 0) { throw "vite build failed" }
if (-not (Test-Path ".\dist\index.html")) { throw "dist/index.html missing" }

Write-Host "=== electron-builder (max compression) ===" -ForegroundColor Cyan
if (-not $env:CSC_LINK) { $env:CSC_IDENTITY_AUTO_DISCOVERY = "false" }
npx electron-builder --win --x64
if ($LASTEXITCODE -ne 0) { throw "electron-builder failed" }

Write-Host "=== SHA256 checksums ===" -ForegroundColor Cyan
& "$Root\scripts\checksums.ps1"

Write-Host ""
Write-Host "Artifacts:" -ForegroundColor Green
Get-ChildItem .\release -Filter "*.exe" | ForEach-Object {
  Write-Host ("  {0:N1} MB  {1}" -f ($_.Length/1MB), $_.Name)
}
Write-Host "Verify later: .\scripts\checksums.ps1 -Verify"
