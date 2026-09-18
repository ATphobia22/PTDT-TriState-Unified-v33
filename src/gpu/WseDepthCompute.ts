/// <reference types="@webgpu/types" />

/**
 * Minimal WebGPU compute path: per-cell depth = max(0, WSE - DEM).
 * Complements FloodDepthCompute / HecRasDepthPipeline.
 */

export const WSE_DEPTH_WGSL = /* wgsl */ `
struct Params {
  width: u32,
  height: u32,
  _pad0: u32,
  _pad1: u32,
}

@group(0) @binding(0) var<uniform> params: Params;
@group(0) @binding(1) var<storage, read> dem: array<f32>;
@group(0) @binding(2) var<storage, read> wse: array<f32>;
@group(0) @binding(3) var<storage, read_write> depth: array<f32>;

@compute @workgroup_size(16, 16)
fn main(@builtin(global_invocation_id) gid: vec3<u32>) {
  if (gid.x >= params.width || gid.y >= params.height) {
    return;
  }
  let i = gid.y * params.width + gid.x;
  let d = wse[i] - dem[i];
  depth[i] = select(0.0, d, d > 0.0);
}
`;

export async function createWseDepthPipeline(
  device: GPUDevice
): Promise<GPUComputePipeline> {
  const module = device.createShaderModule({ code: WSE_DEPTH_WGSL });
  return device.createComputePipeline({
    layout: 'auto',
    compute: { module, entryPoint: 'main' },
  });
}

export async function runWseDepthPass(
  device: GPUDevice,
  pipeline: GPUComputePipeline,
  width: number,
  height: number,
  dem: Float32Array,
  wse: Float32Array
): Promise<Float32Array> {
  const n = width * height;
  if (dem.length < n || wse.length < n) {
    throw new Error('DEM/WSE length must be >= width*height');
  }

  const paramsBuf = device.createBuffer({
    size: 16,
    usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST,
  });
  device.queue.writeBuffer(
    paramsBuf,
    0,
    new Uint32Array([width, height, 0, 0])
  );

  const demBuf = device.createBuffer({
    size: dem.byteLength,
    usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST,
  });
  device.queue.writeBuffer(demBuf, 0, dem);

  const wseBuf = device.createBuffer({
    size: wse.byteLength,
    usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST,
  });
  device.queue.writeBuffer(wseBuf, 0, wse);

  const depthBuf = device.createBuffer({
    size: n * 4,
    usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_SRC,
  });

  const bindGroup = device.createBindGroup({
    layout: pipeline.getBindGroupLayout(0),
    entries: [
      { binding: 0, resource: { buffer: paramsBuf } },
      { binding: 1, resource: { buffer: demBuf } },
      { binding: 2, resource: { buffer: wseBuf } },
      { binding: 3, resource: { buffer: depthBuf } },
    ],
  });

  const encoder = device.createCommandEncoder();
  const pass = encoder.beginComputePass();
  pass.setPipeline(pipeline);
  pass.setBindGroup(0, bindGroup);
  pass.dispatchWorkgroups(Math.ceil(width / 16), Math.ceil(height / 16));
  pass.end();

  const readBuf = device.createBuffer({
    size: n * 4,
    usage: GPUBufferUsage.COPY_DST | GPUBufferUsage.MAP_READ,
  });
  encoder.copyBufferToBuffer(depthBuf, 0, readBuf, 0, n * 4);
  device.queue.submit([encoder.finish()]);

  await readBuf.mapAsync(GPUMapMode.READ);
  const out = new Float32Array(readBuf.getMappedRange().slice(0));
  readBuf.unmap();
  return out;
}
