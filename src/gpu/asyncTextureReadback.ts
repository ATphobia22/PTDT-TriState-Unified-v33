/// <reference types="@webgpu/types" />

import { textureBytesPerRow } from "./webgpuAlignment";

export interface DepthReadbackResult {
  width: number;
  height: number;
  /** Tightly packed row-major float32 depth (no 256 padding). */
  depth: Float32Array;
}

/**
 * Copy r32float texture → staging buffer → mapAsync → tight Float32Array.
 * Waits for GPU via mapAsync (implicit dependency on submitted copy).
 */
export async function readR32FloatTextureAsync(
  device: GPUDevice,
  texture: GPUTexture,
  width: number,
  height: number,
): Promise<DepthReadbackResult> {
  if (!Number.isInteger(width) || !Number.isInteger(height) || width <= 0 || height <= 0) {
    throw new RangeError("width and height must be positive integers");
  }

  const bytesPerRow = textureBytesPerRow(width, 4);
  const bufferSize = bytesPerRow * height;

  const staging = device.createBuffer({
    label: "PTDT_DepthReadbackStaging",
    size: bufferSize,
    usage: GPUBufferUsage.COPY_DST | GPUBufferUsage.MAP_READ,
  });

  try {
    const encoder = device.createCommandEncoder({ label: "PTDT_DepthReadbackEncoder" });
    encoder.copyTextureToBuffer(
      { texture },
      { buffer: staging, bytesPerRow, rowsPerImage: height },
      { width, height, depthOrArrayLayers: 1 },
    );
    device.queue.submit([encoder.finish()]);

    await staging.mapAsync(GPUMapMode.READ);

    const mapped = new Uint8Array(staging.getMappedRange());
    const tight = new Float32Array(width * height);
    const rowBytes = width * 4;

    for (let y = 0; y < height; y++) {
      const row = new Float32Array(
        mapped.buffer,
        mapped.byteOffset + y * bytesPerRow,
        width,
      );
      tight.set(row, y * width);
      void rowBytes; // documentation: source row is width*4 within padded stride
    }

    staging.unmap();
    return { width, height, depth: tight };
  } finally {
    staging.destroy();
  }
}
