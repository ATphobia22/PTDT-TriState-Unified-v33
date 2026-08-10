# PTDT-TriState-Unified-v33

Production Windows 11 cinematic digital twin — Point Township / Tri-County River Valley.

## Locked constants
- BFE 375.0 ft NAVD88
- LAG 377.2 ft
- Berm crest 379.8 ft
- Compensatory storage 1.20×

## Model authority boundaries
- `engine/archimedes_engine.py` — deterministic regulatory BFE/storage checks only
- `engine/hec_ras_exchange.py` — validated HEC-RAS river-stage exchange boundary
- `engine/modflow6_runner.py` — fail-closed MODFLOW6 execution boundary
- `engine/modflow6_exchange.py` — controlled HEC-RAS → MODFLOW6 and groundwater promotion contract
- `engine/authority.py` — explicit authority matrix and promotion rules
- `engine/model_contracts.py` — status, failure, provenance, and exchange contracts
- `docs/architecture/model-authority.md` — operator/developer authority and failure semantics

Failed, missing, corrupt, stale, timed-out, or non-converged MODFLOW6 output is never promoted as current groundwater state. HEC-RAS publishes river hydraulics through an exchange contract; it does not mutate MODFLOW6 internals. Archimedes does not claim hydraulic or groundwater authority.

## Existing visual modules (Aug 2026)
- `src/cgi/TerrainDisplacement.ts` — Posey DEM heightmap displacement + fallback
- `src/cgi/PostProcessing.ts` — optimized bloom / vignette / grain
- `src/cgi/TriCountyCinematicScene.ts` — full cinematic scene controller
- `src/lib/elevationCheck.ts` — Archimedes BFE / storage checks (TS)
- `src/map/triCountyStyle.ts` — MapLibre Tri-County style
- `src/map/FloodCustomLayer.ts` — Three.js flood custom layer
- `src/map/VectorTileLayer.ts` — PMTiles / vector helpers

## Python engine tests
```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

## Build .EXE
```bash
npm i && npm run dist:win
```

## Inno Setup (optional)
Compile `installer/TriRiverTwin_Win11.iss` with Inno Setup.
