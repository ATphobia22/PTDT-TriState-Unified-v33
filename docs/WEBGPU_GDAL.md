# WebGPU Compute + GDAL

## Existing GPU code

| File | Role |
|------|------|
| `src/gpu/FloodDepthCompute.ts` | Flood depth WGSL |
| `src/gpu/HecRasDepthPipeline.ts` | DEM + cell index + WSE → r32float |
| `src/gpu/WseDepthCompute.ts` | Simple WSE−DEM compute pass |

## Pattern

1. GDAL/rasterio → Float32 DEM grid (EPSG:2966)
2. Data fabric / HEC-RAS → WSE grid (same shape)
3. `createWseDepthPipeline` + `runWseDepthPass` → depth map
4. Deck.gl / MapLibre texture or Three.js DataTexture

## Dependencies added

- `@deck.gl/core`, `@deck.gl/layers`, `@deck.gl/mapbox` — overlay layers
- `geotiff` — client GeoTIFF/COG decode
- Proxy stack already: `express`, `cors`, `http-proxy-middleware`
