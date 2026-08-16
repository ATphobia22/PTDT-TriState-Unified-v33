# WGSL workgroup memory & WebGPU indirect compute dispatch

## Workgroup memory (`var<workgroup>`)

| Topic | Spec / practice |
|---|---|
| Address space | `var<workgroup> name: T;` — shared by invocations in one workgroup |
| Lifetime | From workgroup start until workgroup end; not preserved across dispatches |
| Sync | `workgroupBarrier()` before/after shared R/W; `storageBarrier()` for storage buffers |
| Typical use | Tile caches, partial reductions, shared histogram bins |
| PTDT depth bake | **No workgroup memory today** — pure `textureLoad` / storage array (independent per-pixel). Shared memory would only help if a future kernel reused DEM tiles or did neighborhood reductions inside the group. |

### Limits (query at runtime)

```ts
const limits = device.limits;
// maxComputeWorkgroupStorageSize  — bytes of var<workgroup> per workgroup
// maxComputeInvocationsPerWorkgroup
// maxComputeWorkgroupSizeX/Y/Z
// maxComputeWorkgroupsPerDimension
```

**16×16×1** (256 invocations) fits common defaults (`maxComputeInvocationsPerWorkgroup` ≥ 256).  
Shared arrays must fit in `maxComputeWorkgroupStorageSize` (often 16 KiB–32 KiB).

### Divergence note

Branches on `gid` bounds are fine; avoid divergent `workgroupBarrier()` (all invocations in the group must reach the same barriers).

## Indirect compute dispatch

```ts
pass.dispatchWorkgroupsIndirect(indirectBuffer, indirectOffset);
```

Buffer layout (**12 bytes**, three little-endian `u32`):

| Offset | Field |
|---|---|
| 0 | `workgroupCountX` |
| 4 | `workgroupCountY` |
| 8 | `workgroupCountZ` |

**Usage flags:** `GPUBufferUsage.INDIRECT | COPY_DST` (and optionally `STORAGE` if a prior compute pass writes counts).

**When useful for PTDT:** GPU culls empty DEM tiles / zoom-dependent workgroup counts without CPU round-trip. Depth bake currently uses **direct** `dispatchWorkgroups(ceil(w/16), ceil(h/16), 1)` — deterministic and simpler. Indirect is available for multi-resolution or GPU-driven culling.

**Validation:** counts must be ≤ `maxComputeWorkgroupsPerDimension`; offset multiple of **4**.
