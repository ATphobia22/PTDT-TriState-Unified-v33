#==============================================================================
# PTDT Unified V33 — Windows 11 production build
# Prerequisites: Node.js 20+ LTS, Windows 10/11 x64
# Optional: code-signing cert (CSC_LINK / CSC_KEY_PASSWORD)
#==============================================================================
$ErrorActionPreference = "Stop"
$Root = if ($PSScriptRoot) {
  (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
} else { (Get-Location).Path }
Set-Location $Root

function Step($n, $title) {
  Write-Host ""
  Write-Host "=== $n $title ===" -ForegroundColor Cyan
}

Step "1/5" "Environment"
Write-Host "Root: $Root"
node -v
npm -v

Step "2/5" "npm install"
npm install
if ($LASTEXITCODE -ne 0) { throw "npm install failed" }

Step "3/5" "Frontend (tsc + vite)"
npm run build
if ($LASTEXITCODE -ne 0) { throw "Frontend build failed" }
if (-not (Test-Path ".\dist\index.html")) {
  throw "Missing dist\index.html"
}

Step "4/5" "electron-builder (NSIS + portable x64)"
# Skip auto code-sign when no cert present
if (-not $env:CSC_LINK) { $env:CSC_IDENTITY_AUTO_DISCOVERY = "false" }
npx electron-builder --win --x64
if ($LASTEXITCODE -ne 0) { throw "electron-builder failed" }

Step "5/5" "Artifacts"
$rel = Join-Path $Root "release"
if (Test-Path $rel) {
  Get-ChildItem $rel -File | Where-Object { $_.Extension -match '\.(exe|yml|yaml)$' } |
    ForEach-Object {
      Write-Host ("  {0,8:N1} MB  {1}" -f ($_.Length / 1MB), $_.Name)
    }
} else {
  Write-Host "release/ not found" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Portable:  release\PTDT-Unified-V33-Portable.exe" -ForegroundColor Green
Write-Host "Installer: release\PTDT-Unified-V33-*-x64.exe" -ForegroundColor Green
Write-Host "Inno opt:  installer\TriRiverTwin_Win11.iss" -ForegroundColor DarkGray
