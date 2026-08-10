@echo off
setlocal EnableExtensions
cd /d "%~dp0.."

echo Root: %CD%
echo === 1/4 npm install ===
call npm install || exit /b 1

echo === 2/4 frontend build ===
call npm run build || exit /b 1
if not exist "dist\index.html" (
  echo dist\index.html missing
  exit /b 1
)

echo === 3/4 electron-builder ===
set CSC_IDENTITY_AUTO_DISCOVERY=false
call npx electron-builder --win --x64 || exit /b 1

echo === 4/4 artifacts ===
dir /b release\*.exe 2>nul
echo.
echo Portable + NSIS installer in release\
endlocal
