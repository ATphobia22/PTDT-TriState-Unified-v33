# PTDT Unified V33 — full Windows 11 standalone build
# Node 20+, Windows 10/11 x64, admin optional for NSIS shortcuts

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
if (-not $Root) { $Root = (Get-Location).Path }
Set-Location $Root

Write-Host "Root: $Root" -ForegroundColor DarkGray
Write-Host "=== 1/4 npm install ===" -ForegroundColor Cyan
npm install
if ($LASTEXITCODE -ne 0) { throw "npm install failed" }

Write-Host "=== 2/4 frontend build (tsc + vite) ===" -ForegroundColor Cyan
npm run build
if ($LASTEXITCODE -ne 0) { throw "vite/tsc build failed" }

if (-not (Test-Path ".\dist\index.html")) {
  throw "dist/index.html missing — frontend build incomplete"
}

Write-Host "=== 3/4 electron-builder NSIS + portable ===" -ForegroundColor Cyan
$env:CSC_IDENTITY_AUTO_DISCOVERY = "false"  # skip code-sign if no cert
npx electron-builder --win --x64 --config.win.target=nsis,portable
if ($LASTEXITCODE -ne 0) { throw "electron-builder failed" }

Write-Host "=== 4/4 artifacts ===" -ForegroundColor Green
$release = Join-Path $Root "release"
if (Test-Path $release) {
  Get-ChildItem $release -Filter "*.exe" | ForEach-Object {
    Write-Host ("  {0:N1} MB  {1}" -f ($_.Length/1MB), $_.Name)
  }
} else {
  Write-Host "No release/ folder" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Portable:  PTDT-Unified-V33-Portable.exe" -ForegroundColor Green
Write-Host "Installer: PTDT-Unified-V33-*-x64.exe" -ForegroundColor Green
Write-Host "Optional: compile installer\TriRiverTwin_Win11.iss with Inno Setup" -ForegroundColor DarkGray
