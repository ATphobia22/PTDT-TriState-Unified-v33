# Release — Standalone Windows .EXE

This environment cannot upload a pre-built binary. Build on a Windows 11 machine:

```powershell
git clone https://github.com/ATphobia22/PTDT-TriState-Unified-v33.git
cd PTDT-TriState-Unified-v33
.\scripts\build-win11.ps1
```

## Outputs (downloadable locally)

| File | Use |
|------|-----|
| `release\PTDT-Unified-V33-Portable.exe` | Double-click, no install |
| `release\PTDT-Unified-V33-33.1.0-x64.exe` | NSIS installer |

Publish: upload those files to a GitHub Release on this repo.

```powershell
gh release create v33.1.0 .\release\*.exe --title "PTDT Unified V33.1" --notes "Cinematic twin standalone"
```
