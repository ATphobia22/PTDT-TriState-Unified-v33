# PTDT Unified V33.1 — Windows portable + NSIS
$ErrorActionPreference = "Stop"
$Root = if ($PSScriptRoot) { (Resolve-Path (Join-Path $PSScriptRoot "..")).Path } else { (Get-Location).Path }
Set-Location $Root

Write-Host "=== npm install ===" -ForegroundColor Cyan
npm install
if ($LASTEXITCODE -ne 0) { throw "npm install failed" }

Write-Host "=== vite build ===" -ForegroundColor Cyan
npm run build
if ($LASTEXITCODE -ne 0) { throw "vite build failed" }
if (-not (Test-Path ".\dist\index.html")) { throw "dist/index.html missing" }

Write-Host "=== electron-builder ===" -ForegroundColor Cyan
if (-not $env:CSC_LINK) { $env:CSC_IDENTITY_AUTO_DISCOVERY = "false" }
npx electron-builder --win --x64
if ($LASTEXITCODE -ne 0) { throw "electron-builder failed" }

Write-Host ""
Write-Host "Downloadable artifacts:" -ForegroundColor Green
Get-ChildItem .\release -Filter "*.exe" | ForEach-Object {
  Write-Host ("  {0:N1} MB  {1}" -f ($_.Length/1MB), $_.FullName)
}
