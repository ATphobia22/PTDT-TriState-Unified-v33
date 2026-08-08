# PTDT-TriState-Unified-v33

Production Windows 11 cinematic digital twin — Point Township / Tri-County River Valley.

## Locked constants
- BFE 375.0 ft NAVD88
- LAG 377.2 ft
- Berm crest 379.8 ft
- Compensatory storage 1.20×

## New modules (Aug 2026)
- `src/cgi/TerrainDisplacement.ts` — Posey DEM heightmap displacement + fallback
- `src/cgi/PostProcessing.ts` — optimized bloom / vignette / grain
- `src/cgi/TriCountyCinematicScene.ts` — full cinematic scene controller
- `src/lib/elevationCheck.ts` — Archimedes BFE / storage checks (TS)
- `src/map/triCountyStyle.ts` — MapLibre Tri-County style
- `src/map/FloodCustomLayer.ts` — Three.js flood custom layer
- `src/map/VectorTileLayer.ts` — PMTiles / vector helpers
- `engine/archimedes_engine.py` — Python regulatory core

## Build .EXE
```bash
npm i && npm run dist:win
```

## Inno Setup (optional)
Compile `installer/TriRiverTwin_Win11.iss` with Inno Setup.
