# PTDT Unified V33 — Setup Instructions

## Requirements

| Item | Version / notes |
|------|-----------------|
| OS | Windows 10/11 x64 |
| Node.js | 20 LTS or newer ([nodejs.org](https://nodejs.org)) |
| Git | Optional, for clone |
| RAM | 8 GB+ recommended |
| GPU | DirectX 12 capable (WebGL2) |

Optional:
- Inno Setup 6 — full installer from `installer/TriRiverTwin_Win11.iss`
- Python 3.10+ + `pip install ras-commander h5py` — HEC-RAS bridge
- Docker — PostGIS stack (`docker compose up`)

---

## 1. Clone

```powershell
git clone https://github.com/ATphobia22/PTDT-TriState-Unified-v33.git
cd PTDT-TriState-Unified-v33
```

Or download ZIP from GitHub → Extract.

---

## 2. Install dependencies

```powershell
npm install
```

If `electron` / `electron-builder` fail on first run, retry once (network).

---

## 3. Development (browser preview)

```powershell
npm run dev
```

Open the URL Vite prints (usually `http://localhost:5173`).

MapLibre needs network for the dark basemap. USGS HUD needs network for station 03378500.

---

## 4. Build Windows standalone .EXE

**Recommended (PowerShell):**

```powershell
.\scripts\build-win11.ps1
```

**Or CMD:**

```cmd
scripts\build-win11.cmd
```

**Manual:**

```powershell
npm install
npm run build
npx electron-builder --win --x64
```

### Output

| File | Purpose |
|------|--------|
| `release\PTDT-Unified-V33-Portable.exe` | No install — double-click |
| `release\PTDT-Unified-V33-*-x64.exe` | NSIS installer (shortcuts) |

Code signing is skipped unless `CSC_LINK` / `CSC_KEY_PASSWORD` are set.

---

## 5. Optional Inno Setup installer

1. Install [Inno Setup](https://jrsoftware.org/isinfo.php)
2. Build the portable EXE first (step 4)
3. Open `installer\TriRiverTwin_Win11.iss` → Compile
4. Result under `installer\installer_output\`

---

## 6. Optional PostGIS (Docker)

```powershell
docker compose up -d
```

- Postgres/PostGIS: `localhost:8087` (user/db `ptdt`)
- Init scripts: `volumes/postgresql_init.d/`

Middleware env:

```
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=8087
POSTGRES_DB=ptdt
POSTGRES_USER=ptdt
POSTGRES_PASSWORD=ptdt
```

---

## 7. Optional HEC-RAS Python bridge

```powershell
pip install ras-commander h5py
python python\hec_ras_bridge.py C:\path\to\ras\project 01
```

Requires HEC-RAS 6.x for `ras-commander` compute; HDF read works without the UI.

---

## 8. Offline / air-gapped use

- Use **Portable.exe** — no install registry required
- Basemap and USGS need network; without them the 3D twin + HUD still load (USGS shows zeros / last fail silent)
- Static GIS bootstrap: place GeoJSON at
  `%LOCALAPPDATA%\TriRiverTwin\static_gis\bonebank_parcels_fixed.json`

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `electron-builder` fails | Delete `node_modules`, `npm install`, rebuild |
| Blank map | Check network / firewall for Carto basemap |
| GPU black canvas | Update GPU drivers; ensure WebGL2 enabled |
| NSIS blocked | Run portable EXE instead; or allow installer in SmartScreen |
| `dist` missing | Run `npm run build` before electron-builder |

---

## Quick reference

```powershell
npm install
npm run dev          # develop
.\scripts\build-win11.ps1   # Windows .exe
```
