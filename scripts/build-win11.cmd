@echo off
setlocal
cd /d "%~dp0.."

echo === npm install ===
call npm install || exit /b 1

echo === vite + tsc build ===
call npm run build || exit /b 1

echo === electron-builder (NSIS + portable) ===
call npx electron-builder --win --x64 || exit /b 1

echo.
echo Output in release\
dir /b release\*.exe
endlocal
