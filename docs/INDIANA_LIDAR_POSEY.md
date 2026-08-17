# Indiana LiDAR / elevation — Posey County

## Collections

| Program | Years | Quality | Posey |
|---------|-------|---------|--------|
| Statewide | 2011–2013 | ~QL3 | Western counties incl. Posey |
| **3DEP / NRCS statewide** | **2016–2020** | **QL2** (~2 pts/m²) | **Posey delivered 2020** |
| Next cycle | 2025–2028 | QL1 planned | Future |

## Access (CC0 / public)

| Source | Path |
|--------|------|
| IGIO Elevation Program | https://elevation.gio.in.gov/ |
| AWS Open Data | `s3://giselevationingov/` (us-east-2, **no-sign-request**) |
| Purdue Digital Forestry | https://lidar.digitalforestry.org/ — Posey 2020 LAZ/DEM/DSM/NDHM tiles |
| ISDP (IU) | 2016–2020 county DEM mosaics + LAS |
| OpenTopography | 2011–2013 Indiana custom AOI / CRS |
| USGS 3DEP EPT | `s3://usgs-lidar-public/` |

```bash
aws s3 ls --no-sign-request s3://giselevationingov/
```

## PTDT DEM sealing

1. Acquire Posey **2020** ground product (LAZ Class 2 or hydro-flattened DEM).  
2. Horizontal warp to **EPSG:2966**.  
3. Vertical **NAVD88** (confirm product metadata / geoid).  
4. COG: `scripts/cog_bare_earth_navd88.sh`  
5. SHA-256 under `data/dem/`  

**LOMA vertical authority** remains Indiana-licensed survey / elevation certificate, not unsealed LiDAR alone.

PDAL ground extract template: `scripts/pdal_extract_ground.json`  
IGIO clip helper: `scripts/igio_s3_elevation_clip.sh`
