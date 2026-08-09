# Natron 4K Offline Master — Tri-County River Valley

## Open & auto-build in Natron

1. Launch **Natron** (https://natrongithub.github.io/)
2. **Script Editor** → Open → select `natron/build_tristate_cinematic.py`
3. Click **Run** (or Ctrl+Enter) → Full node graph is created automatically
4. Select node **Master_MP4_Export_4K**
5. **Render → Render** → Writes `out/TriCounty_Cinematic_DigitalTwin_Master_4K.mp4`

## Required assets (`data/`)

| File | Source |
|------|--------|
| `posey_lidar_dem_navd88.tif` | Indiana GIO / AWS COG DSM |
| `posey_naip_ortho_4k.png` | USDA NAIP |
| `archimedes_water_sim_pass.%04d.exr` | HEC-RAS / FLIP depth sequence |
| `building_extrusions_4k.png` | Overture / local footprints |

## Specs

- Resolution: **3840×2160** (4K UHD)
- Frame rate: **24 fps**
- Duration: **240 frames** (10 seconds)
- Codec: **H.264 @ 50 Mbps**
- HUD: BFE 375.0 / LAG 377.2 / USGS 03378500 / OpenMI stack
