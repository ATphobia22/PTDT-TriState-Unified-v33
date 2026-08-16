/// <reference types="@webgpu/types" />

/** GPUIndirectDispatchArgs: three u32 workgroup counts (12 bytes). */
export const INDIRECT_DISPATCH_BYTES = 12;

export interface WorkgroupCounts {
  x: number;
  y: number;
  z: number;
}

export function workgroupsForGrid(
  width: number,
  height: number,
  workgroupSizeX: number,
  workgroupSizeY: number,
  workgroupSizeZ = 1,
): WorkgroupCounts {
  if (workgroupSizeX <= 0 || workgroupSizeY <= 0 || workgroupSizeZ <= 0) {
    throw new RangeError("workgroup sizes must be positive");
  }
  return {
    x: Math.ceil(width / workgroupSizeX),
    y: Math.ceil(height / workgroupSizeY),
    z: workgroupSizeZ > 1 ? Math.ceil(1 / workgroupSizeZ) || 1 : 1,
  };
}

/** Pack x/y/z into an ArrayBuffer for writeBuffer / INDIRECT. */
export function encodeIndirectDispatchArgs(counts: WorkgroupCounts): ArrayBuffer {
  for (const [name, v] of [
    ["x", counts.x],
    ["y", counts.y],
    ["z", counts.z],
  ] as const) {
    if (!Number.isInteger(v) || v < 0) {
      throw new RangeError(`workgroupCount${name.toUpperCase()} must be a non-negative integer`);
    }
  }
  const buf = new ArrayBuffer(INDIRECT_DISPATCH_BYTES);
  const view = new DataView(buf);
  view.setUint32(0, counts.x, true);
  view.setUint32(4, counts.y, true);
  view.setUint32(8, counts.z, true);
  return buf;
}

export function createIndirectDispatchBuffer(
  device: GPUDevice,
  counts: WorkgroupCounts,
  label = "PTDT_IndirectDispatch",
): GPUBuffer {
  const buffer = device.createBuffer({
    label,
    size: INDIRECT_DISPATCH_BYTES,
    usage: GPUBufferUsage.INDIRECT | GPUBufferUsage.COPY_DST,
  });
  device.queue.writeBuffer(buffer, 0, encodeIndirectDispatchArgs(counts));
  return buffer;
}

/**
 * Optional: clamp counts to device limits before encode.
 */
export function clampWorkgroupCounts(
  counts: WorkgroupCounts,
  limits: GPUSupportedLimits,
): WorkgroupCounts {
  const max = limits.maxComputeWorkgroupsPerDimension;
  return {
    x: Math.min(counts.x, max),
    y: Math.min(counts.y, max),
    z: Math.min(counts.z, max),
  };
}
