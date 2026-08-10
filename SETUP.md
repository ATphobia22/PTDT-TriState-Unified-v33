# PTDT Unified V33 — Setup Instructions

## Requirements

| Item | Version / notes |
|------|-----------------|
| OS | Windows 10/11 x64 |
| Node.js | 20 LTS+ |
| Docker Desktop | For PostGIS (optional) |
| Python 3.10+ | For HEC-RAS bridge (optional) |

---

## 1. Clone & install

```powershell
git clone https://github.com/ATphobia22/PTDT-TriState-Unified-v33.git
cd PTDT-TriState-Unified-v33
npm install
```

## 2. Dev

```powershell
npm run dev
```

## 3. Windows .EXE

```powershell
.\scripts\build-win11.ps1
```

→ `release\PTDT-Unified-V33-Portable.exe`

## 4. PostGIS steps

```powershell
docker compose up -d
docker exec ptdt_postgis pg_isready -U ptdt -d ptdt
```

Connect: `postgresql://ptdt:ptdt@127.0.0.1:8087/ptdt`

Details: [docs/PostGIS_Setup.md](./docs/PostGIS_Setup.md)

## 5. HEC-RAS

```powershell
pip install ras-commander h5py
python python\hec_ras_bridge.py C:\path\to\project 01
```

Details: [docs/HEC_RAS_Integration.md](./docs/HEC_RAS_Integration.md)

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Port 8087 in use | Change ports in docker-compose.yml |
| electron-builder fail | `Remove-Item -Recurse node_modules; npm i` |
| Blank map | Network for Carto basemap |
