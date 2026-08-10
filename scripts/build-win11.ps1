# PTDT Unified V33 — Windows 11 standalone build
# Requires: Node 20+, Windows 10/11 x64

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

Write-Host "=== npm install ===" -ForegroundColor Cyan
npm install

Write-Host "=== vite + tsc build ===" -ForegroundColor Cyan
npm run build
if ($LASTEXITCODE -ne 0) { throw "Frontend build failed" }

Write-Host "=== electron-builder (NSIS + portable) ===" -ForegroundColor Cyan
npx electron-builder --win --x64
if ($LASTEXITCODE -ne 0) { throw "electron-builder failed" }

Write-Host ""
Write-Host "Output:" -ForegroundColor Green
Get-ChildItem -Path .\release -Filter "*.exe" | ForEach-Object { Write-Host "  $($_.FullName)" }
Write-Host ""
Write-Host "Portable: PTDT-Unified-V33-Portable.exe" -ForegroundColor Green
Write-Host "Installer: PTDT-Unified-V33-*-x64.exe" -ForegroundColor Green
