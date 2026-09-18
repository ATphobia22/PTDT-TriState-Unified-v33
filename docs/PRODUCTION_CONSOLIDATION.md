# PTDT-TriState-Unified-v33 — Production Consolidation

## Architecture

| Path | Role |
|------|------|
| `.github/workflows/` | CI (TSM Parse Gate, MapLibre visual, branch sync) |
| `backend/proxies/` | USGS/NOAA/USACE/INDNR token proxies |
| `data/` | GeoTIFF, station registries |
| `docs/` | LaTeX FEMA/LOMC evidence templates |
| `electron/` | Windows .exe shell |
| `engine/` | MapLibre shaders, WebGPU, PostGIS/HEC-RAS |

## Checklist

1. **Branches** — Unique feature work merged; duplicate hydraulic-authority-* SHAs closed as conflicted or already-in-main.
2. **Secrets / env** — Set `VITE_TSM_API_BASE_URL` to HTTPS proxy (`backend/proxies/`).
3. **Local gate**

```bash
npm ci
npm run ci:full
npm run electron:dist   # optional Windows package
```

## Notes

- Many `feature/hydraulic-groundwater-authority-v*` branches share one SHA; only latest unique tip needed.
- Conflicted merges require manual resolve (ours/theirs) on Windows/local git.
