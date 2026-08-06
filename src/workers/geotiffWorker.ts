/** Optimized GeoTIFF decode worker — block reads, stride downsample, batch POST */
self.onmessage = async (e: MessageEvent) => {
  const { tiffUrl, maxDim = 512, batchSize = 5000 } = e.data;
  try {
    // @ts-ignore
    const tiff = await (self as any).GeoTIFF.fromUrl(tiffUrl);
    const image = await tiff.getImage();
    const { width, height } = image;
    const raster = await image.readRasters({ interleave: true, pool: (self as any).navigator?.hardwareConcurrency || 4 });
    const strideX = Math.ceil(width / maxDim);
    const strideY = Math.ceil(height / maxDim);
    const cells: { lon: number; lat: number; depth_m: number }[] = [];
    for (let y = 0; y < height; y += strideY) {
      const rowOffset = y * width;
      for (let x = 0; x < width; x += strideX) {
        const i = rowOffset + x;
        const depth = raster[i];
        if (depth <= 0 || Number.isNaN(depth)) continue;
        cells.push({ lon: 0, lat: 0, depth_m: depth as number });
      }
    }
    for (let i = 0; i < cells.length; i += batchSize) {
      self.postMessage({ type: "batch", cells: cells.slice(i, i + batchSize) });
    }
    self.postMessage({ type: "done", total: cells.length });
  } catch (err) {
    self.postMessage({ type: "error", message: String(err) });
  }
};
export {};
