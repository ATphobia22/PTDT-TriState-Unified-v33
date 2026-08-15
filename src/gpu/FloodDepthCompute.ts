/**
 * WebGPU compute pass for deriving a binary flood mask from a canonical
 * hydraulic depth raster. The source depth remains authoritative upstream.
 *
 * Fail-closed for non-finite depth. WGSL has no isNan/isInf builtins
 * (removed from the language); use IEEE inequality + magnitude guard.
 */

/// <reference types="@webgpu/types" />

export const FLOOD_DEPTH_COMPUTE_WGSL = /* wgsl */ `
struct Params {
  width: u32,
  height: u32,
  thresholdM: f32,
  dilateCells: i32,
};

@group(0) @binding(0)
var srcDepth: texture_storage_2d<r32float, read>;

@group(0) @binding(1)
var dstMask: texture_storage_2d<r32float, write>;

@group(0) @binding(2)
var<uniform> params: Params;

// Portable finite check: NaN != NaN; reject extreme magnitudes
fn validDepth(value: f32) -> bool {
  return (value == value) && (abs(value) < 1e30);
}

@compute @workgroup_size(8, 8, 1)
fn main(@builtin(global_invocation_id) gid: vec3<u32>) {
  if (gid.x >= params.width || gid.y >= params.height) {
    return;
  }

  let x = i32(gid.x);
  let y = i32(gid.y);
  let radius = params.dilateCells;
  var maxDepth = textureLoad(srcDepth, vec2<i32>(x, y)).r;

  if (!validDepth(maxDepth)) {
    maxDepth = -1.0;
  }

  if (radius > 0) {
    for (var dy = -radius; dy <= radius; dy++) {
      for (var dx = -radius; dx <= radius; dx++) {
        let sx = x + dx;
        let sy = y + dy;
        if (sx >= 0 && sy >= 0 && sx < i32(params.width) && sy < i32(params.height)) {
          let sample = textureLoad(srcDepth, vec2<i32>(sx, sy)).r;
          if (validDepth(sample)) {
            maxDepth = max(maxDepth, sample);
          }
        }
      }
    }
  }

  let wet = validDepth(maxDepth) && maxDepth >= params.thresholdM;
  textureStore(
    dstMask,
    vec2<i32>(x, y),
    vec4<f32>(select(0.0, 1.0, wet), 0.0, 0.0, 1.0),
  );
}
`;

export interface FloodComputeHandles {
  readonly device: GPUDevice;
  readonly pipeline: GPUComputePipeline;
  readonly paramBuffer: GPUBuffer;
  readonly bindGroupLayout: GPUBindGroupLayout;
}

export async function createFloodDepthCompute(
  device: GPUDevice,
): Promise<FloodComputeHandles> {
  const module = device.createShaderModule({
    label: "PTDT_FloodDepthCompute",
    code: FLOOD_DEPTH_COMPUTE_WGSL,
  });

  const bindGroupLayout = device.createBindGroupLayout({
    entries: [
      {
        binding: 0,
        visibility: GPUShaderStage.COMPUTE,
        storageTexture: {
          access: "read-only",
          format: "r32float",
          viewDimension: "2d",
        },
      },
      {
        binding: 1,
        visibility: GPUShaderStage.COMPUTE,
        storageTexture: {
          access: "write-only",
          format: "r32float",
          viewDimension: "2d",
        },
      },
      {
        binding: 2,
        visibility: GPUShaderStage.COMPUTE,
        buffer: { type: "uniform" },
      },
    ],
  });

  const pipeline = device.createComputePipeline({
    label: "PTDT_FloodDepthPipeline",
    layout: device.createPipelineLayout({ bindGroupLayouts: [bindGroupLayout] }),
    compute: { module, entryPoint: "main" },
  });

  const paramBuffer = device.createBuffer({
    size: 16,
    usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST,
  });

  return { device, pipeline, paramBuffer, bindGroupLayout };
}

export function dispatchFloodDepthCompute(
  handles: FloodComputeHandles,
  src: GPUTexture,
  dst: GPUTexture,
  width: number,
  height: number,
  thresholdM: number,
  dilateCells = 0,
): void {
  if (!Number.isInteger(width) || !Number.isInteger(height) || width <= 0 || height <= 0) {
    throw new RangeError("width and height must be positive integers");
  }
  if (!Number.isFinite(thresholdM)) {
    throw new RangeError("thresholdM must be finite");
  }
  if (!Number.isInteger(dilateCells) || dilateCells < 0 || dilateCells > 2) {
    throw new RangeError("dilateCells must be an integer in the range 0..2");
  }
  if (src === dst) {
    throw new Error("src and dst textures must be distinct");
  }

  const params = new ArrayBuffer(16);
  const view = new DataView(params);
  view.setUint32(0, width, true);
  view.setUint32(4, height, true);
  view.setFloat32(8, thresholdM, true);
  view.setInt32(12, dilateCells, true);
  handles.device.queue.writeBuffer(handles.paramBuffer, 0, params);

  const bindGroup = handles.device.createBindGroup({
    layout: handles.bindGroupLayout,
    entries: [
      { binding: 0, resource: src.createView() },
      { binding: 1, resource: dst.createView() },
      { binding: 2, resource: { buffer: handles.paramBuffer } },
    ],
  });

  const encoder = handles.device.createCommandEncoder({
    label: "PTDT_FloodDepthCommandEncoder",
  });
  const pass = encoder.beginComputePass({ label: "PTDT_FloodDepthPass" });
  pass.setPipeline(handles.pipeline);
  pass.setBindGroup(0, bindGroup);
  pass.dispatchWorkgroups(Math.ceil(width / 8), Math.ceil(height / 8), 1);
  pass.end();
  handles.device.queue.submit([encoder.finish()]);
}
