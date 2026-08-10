# Auto-update (electron-updater)

- Provider: GitHub Releases (`ATphobia22/PTDT-TriState-Unified-v33`)
- Packaged app checks on launch; downloads in background; installs on quit
- Publish:

```powershell
.\scripts\build-win11.ps1
gh release create v33.1.0 .\release\*.exe .\release\SHA256SUMS.txt --generate-notes
```

or `npx electron-builder --win --publish always` with `GH_TOKEN` set.

Portable builds do not auto-update the same way as NSIS; prefer NSIS for updater.
