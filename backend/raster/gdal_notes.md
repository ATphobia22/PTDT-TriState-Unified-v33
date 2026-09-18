# GDAL Raster Processing (server / offline)

Node cannot run native GDAL without bindings. Prefer **Python + GDAL/rasterio** for DEM/GeoTIFF work, then feed Float32 grids into WebGPU.

## Typical pipeline

```bash
# Reproject Indiana East (EPSG:2966) DEM to Web Mercator or keep native
gdalwarp -t_srs EPSG:2966 -r bilinear input.tif dem_2966.tif

# Clip to Point Township bbox
gdal_translate -projwin <ulx> <uly> <lrx> <lry> dem_2966.tif dem_clip.tif

# Export raw float32 for GPU upload
gdal_translate -of ENVI dem_clip.tif dem_clip.bil
```

## Python (rasterio)

```python
import rasterio
import numpy as np

with rasterio.open("dem_clip.tif") as src:
    dem = src.read(1).astype(np.float32)
    transform = src.transform
    crs = src.crs
# dem.ravel() → upload to WebGPU storage buffer
```

## Browser-side GeoTIFF

Use `geotiff` npm package to decode COG/GeoTIFF in the client, then pass arrays to `runWseDepthPass`.

CI already installs `libgdal-dev` / `gdal-bin` in `tsm-parse-gate.yml`.
