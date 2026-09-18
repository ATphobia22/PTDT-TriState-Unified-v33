# Build & Repair Runbook — PTDT-TriState-Unified-v33

```bash
rm -rf node_modules package-lock.json
npm install

# Optional live proxy (USGS/NOAA)
npm run proxy &

npm run build
npm run electron:build   # or: npm run dist:win
```

Requires: Node 20+, Python 3.11 (CI), GDAL/PROJ on Linux CI runners.

Env for static hosts: `VITE_TSM_API_BASE_URL=https://<your-proxy>/api`
