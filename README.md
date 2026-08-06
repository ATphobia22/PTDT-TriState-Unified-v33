# PTDT-TriState-Unified-v33

Virtual Tri-State River Valley — Cinematic CGI + Windows 11 standalone .exe

## Build Windows Standalone .EXE
```bash
npm install
npm run dist:win
```

Output in `release/`:
- `PTDT-Unified-V33-33.0.0-x64.exe` (NSIS installer)
- `PTDT-Unified-V33-Portable.exe` (no-install portable)

## Features
- GPU rasterization + zero-copy flags
- AppUserModelId for Windows taskbar
- Cinematic flood water ShaderMaterial
- MapLibre + Three.js river valley
- GeoTIFF worker, PostGIS, depth filters
