/**
 * WebGPU buffer / texture alignment helpers (spec minima).
 *
 * Key rules used by PTDT depth pipelines:
 * - writeTexture bytesPerRow: multiple of 256
 * - uniform buffer binding offset: multiple of 256
 * - uniform buffer size: multiple of 16 (struct packing)
 * - storage buffer binding offset: multiple of 256 (min dynamic offset)
 * - mapped buffer ranges: mapAsync size/offset constraints per usage
 */

export const TEXTURE_BYTES_PER_ROW_ALIGNMENT = 256;
export const UNIFORM_BUFFER_OFFSET_ALIGNMENT = 256;
export const UNIFORM_STRUCT_SIZE_ALIGNMENT = 16;
export const STORAGE_BUFFER_OFFSET_ALIGNMENT = 256;

/** Round up n to a multiple of align (align must be power of two). */
export function alignBytes(n: number, align: number): number {
  if (align <= 0 || (align & (align - 1)) !== 0) {
    throw new RangeError("align must be a positive power of two");
  }
  return (n + align - 1) & ~(align - 1);
}

/**
 * bytesPerRow for writeTexture / copyTextureToBuffer for tightly packed
 * 32-bit (4-byte) texels. Always a multiple of 256.
 */
export function textureBytesPerRow(width: number, bytesPerTexel = 4): number {
  if (!Number.isInteger(width) || width <= 0) {
    throw new RangeError("width must be a positive integer");
  }
  return alignBytes(width * bytesPerTexel, TEXTURE_BYTES_PER_ROW_ALIGNMENT);
}

/** Uniform buffer size rounded up to 16-byte struct alignment. */
export function uniformBufferSize(byteLength: number): number {
  return alignBytes(Math.max(byteLength, 16), UNIFORM_STRUCT_SIZE_ALIGNMENT);
}

/** Storage buffer size — at least 4 bytes, natural element alignment. */
export function storageBufferSize(byteLength: number, elementAlign = 4): number {
  return alignBytes(Math.max(byteLength, elementAlign), elementAlign);
}

/**
 * Pack tightly packed 4-byte texels into a 256-aligned staging buffer for writeTexture.
 */
export function packTextureRows(
  src: ArrayBufferView,
  width: number,
  height: number,
  bytesPerTexel = 4,
): { padded: Uint8Array; bytesPerRow: number } {
  if (src.byteLength < width * height * bytesPerTexel) {
    throw new RangeError(
      `source byteLength ${src.byteLength} < width*height*bpp (${width * height * bytesPerTexel})`,
    );
  }
  const bytesPerRow = textureBytesPerRow(width, bytesPerTexel);
  const rowBytes = width * bytesPerTexel;
  const padded = new Uint8Array(bytesPerRow * height);
  const srcBytes = new Uint8Array(src.buffer, src.byteOffset, src.byteLength);
  for (let y = 0; y < height; y++) {
    padded.set(srcBytes.subarray(y * rowBytes, (y + 1) * rowBytes), y * bytesPerRow);
  }
  return { padded, bytesPerRow };
}
