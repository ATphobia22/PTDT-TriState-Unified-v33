/// <reference lib="webworker" />

interface WorkerIn {
  tiffUrl: string;
  maxDim?: number;
  batchSize?: number;
  geoTransform?: number[];
}

interface Cell {
  lon: number;
  lat: number;
  depth_m: number;
}

self.onmessage = async (e: MessageEvent<WorkerIn>) => {
  const {
    tiffUrl,
    maxDim = 512,
    batchSize = 5000,
    geoTransform = [-88.02, 0.0001, 0, 37.86, 0, -0.0001],
  } = e.data;

  try {
    const GeoTIFF = (self as any).GeoTIFF;
    if (!GeoTIFF) throw new Error("GeoTIFF library not loaded in worker");

    const tiff = await GeoTIFF.fromUrl(tiffUrl);
    const image = await tiff.getImage();
    const width = image.getWidth();
    const height = image.getHeight();

    const rasters = await image.readRasters({
      interleave: true,
      pool: (self as any).navigator?.hardwareConcurrency ?? 4,
    });

    const data = rasters as Float32Array | Uint16Array | Float64Array;
    const [ox, pw, , oy, , ph] = geoTransform;

    const strideX = Math.max(1, Math.ceil(width / maxDim));
    const strideY = Math.max(1, Math.ceil(height / maxDim));

    const cells: Cell[] = [];

    for (let y = 0; y < height; y += strideY) {
      const rowOffset = y * width;
      for (let x = 0; x < width; x += strideX) {
        const i = rowOffset + x;
        const depth = Number(data[i]);
        if (depth <= 0 || Number.isNaN(depth)) continue;
        const lon = ox + x * pw;
        const lat = oy + y * ph;
        cells.push({ lon, lat, depth_m: depth });
      }
    }

    for (let i = 0; i < cells.length; i += batchSize) {
      self.postMessage({ type: "batch", cells: cells.slice(i, i + batchSize), index: i });
    }
    self.postMessage({ type: "done", total: cells.length });
  } catch (err) {
    self.postMessage({
      type: "error",
      message: err instanceof Error ? err.message : String(err),
    });
  }
};

export {};
