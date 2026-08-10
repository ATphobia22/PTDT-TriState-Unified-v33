# PTDT-TriState-Unified-v33

Cinematic digital twin + Windows 11 standalone

## Windows build
```powershell
.\scripts\build-win11.ps1
```
or
```cmd
scripts\build-win11.cmd
```
→ `release/PTDT-Unified-V33-Portable.exe` + NSIS installer

## HEC-RAS
```bash
pip install ras-commander h5py
python python/hec_ras_bridge.py /path/to/ras/project 01
```

## OpenColorIO / Natron ACES
See `docs/OpenColorIO_Natron_ACES.md`
