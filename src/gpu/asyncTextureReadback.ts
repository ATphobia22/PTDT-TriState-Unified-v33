/// <reference types="@webgpu/types" />

import { textureBytesPerRow } from "./webgpuAlignment";

export interface DepthReadbackResult {
  width: number;
  height: number;
  /** Tightly packed row-major float32 depth (no 256 padding). */
  depth: Float32Array;
}

export type ReadbackErrorCode =
  | "INVALID_DIMENSIONS"
  | "TEXTURE_SIZE_MISMATCH"
  | "MAP_ASYNC_FAILED"
  | "DEVICE_LOST"
  | "COPY_FAILED"
  | "UNKNOWN";

export class DepthReadbackError extends Error {
  readonly code: ReadbackErrorCode;
  readonly cause?: unknown;

  constructor(code: ReadbackErrorCode, message: string, cause?: unknown) {
    super(message);
    this.name = "DepthReadbackError";
    this.code = code;
    this.cause = cause;
  }
}

function isDeviceLostError(err: unknown): boolean {
  if (!err || typeof err !== "object") return false;
  const e = err as { name?: string; message?: string };
  return (
    e.name === "OperationError" ||
    e.name === "GPUDeviceLostInfo" ||
    /device lost|destroyed/i.test(String(e.message ?? ""))
  );
}

/**
 * Copy r32float texture → staging buffer → mapAsync → tight Float32Array.
 * Fail-closed typed errors; always destroys staging; unmaps only if mapped.
 */
export async function readR32FloatTextureAsync(
  device: GPUDevice,
  texture: GPUTexture,
  width: number,
  height: number,
): Promise<DepthReadbackResult> {
  if (!Number.isInteger(width) || !Number.isInteger(height) || width <= 0 || height <= 0) {
    throw new DepthReadbackError(
      "INVALID_DIMENSIONS",
      `width/height must be positive integers (got ${width}x${height})`,
    );
  }

  if (texture.width < width || texture.height < height) {
    throw new DepthReadbackError(
      "TEXTURE_SIZE_MISMATCH",
      `texture ${texture.width}x${texture.height} smaller than requested ${width}x${height}`,
    );
  }

  let bytesPerRow: number;
  try {
    bytesPerRow = textureBytesPerRow(width, 4);
  } catch (err) {
    throw new DepthReadbackError("INVALID_DIMENSIONS", String(err), err);
  }

  const bufferSize = bytesPerRow * height;
  let staging: GPUBuffer | null = null;
  let mapped = false;

  try {
    staging = device.createBuffer({
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
    } catch (err) {
      throw new DepthReadbackError(
        isDeviceLostError(err) ? "DEVICE_LOST" : "COPY_FAILED",
        `copyTextureToBuffer/submit failed: ${String(err)}`,
        err,
      );
    }

    try {
      await staging.mapAsync(GPUMapMode.READ);
      mapped = true;
    } catch (err) {
      throw new DepthReadbackError(
        isDeviceLostError(err) ? "DEVICE_LOST" : "MAP_ASYNC_FAILED",
        `mapAsync(READ) failed: ${String(err)}`,
        err,
      );
    }

    const mappedBytes = new Uint8Array(staging.getMappedRange());
    const tight = new Float32Array(width * height);

    for (let y = 0; y < height; y++) {
      const byteOffset = mappedBytes.byteOffset + y * bytesPerRow;
      if (byteOffset + width * 4 > mappedBytes.byteOffset + mappedBytes.byteLength) {
        throw new DepthReadbackError(
          "MAP_ASYNC_FAILED",
          `mapped range underrun at row ${y}`,
        );
      }
      const row = new Float32Array(mappedBytes.buffer, byteOffset, width);
      tight.set(row, y * width);
    }

    return { width, height, depth: tight };
  } catch (err) {
    if (err instanceof DepthReadbackError) throw err;
    throw new DepthReadbackError(
      isDeviceLostError(err) ? "DEVICE_LOST" : "UNKNOWN",
      `readback failed: ${String(err)}`,
      err,
    );
  } finally {
    if (staging) {
      try {
        if (mapped) staging.unmap();
      } catch {
        // ignore unmap after failed map / device loss
      }
      try {
        staging.destroy();
      } catch {
        // ignore double-destroy
      }
    }
  }
}
