/// <reference types="@webgpu/types" />

/**
 * WebGPU depth bake: DEM + cell_index_map + WSE_mm → r32float depth.
 * - writeTexture bytesPerRow padded to 256
 * - uniform Params 16-byte aligned
 * - storage WSE size element-aligned
 * - async CPU readback via mapAsync (typed errors)
 * - optional indirect dispatch
 */

import { packTextureRows, storageBufferSize, uniformBufferSize } from "./webgpuAlignment";
import {
  readR32FloatTextureAsync,
  DepthReadbackError,
  type DepthReadbackResult,
} from "./asyncTextureReadback";
import {
  clampWorkgroupCounts,
  createIndirectDispatchBuffer,
  workgroupsForGrid,
} from "./indirectDispatch";

export class HecRasDepthPipeline {
  private device: GPUDevice;
  private pipeline: GPUComputePipeline;
  private bindGroupLayout: GPUBindGroupLayout;
  private demTexture: GPUTexture | null = null;
  private cellIndexTexture: GPUTexture | null = null;
  private wseBuffer: GPUBuffer | null = null;
  private indirectBuffer: GPUBuffer | null = null;
  private wseCount = 0;
  private paramsBuffer: GPUBuffer;
  public depthOutTexture: GPUTexture | null = null;
  private width = 0;
  private height = 0;

  constructor(device: GPUDevice, shaderCode: string) {
    this.device = device;
    this.paramsBuffer = this.device.createBuffer({
      size: uniformBufferSize(16),
      usage: GPUBufferUsage.UNIFORM | GPUBufferUsage.COPY_DST,
    });

    this.bindGroupLayout = this.device.createBindGroupLayout({
      entries: [
        { binding: 0, visibility: GPUShaderStage.COMPUTE, texture: { sampleType: "unfilterable-float" } },
        { binding: 1, visibility: GPUShaderStage.COMPUTE, texture: { sampleType: "uint" } },
        { binding: 2, visibility: GPUShaderStage.COMPUTE, buffer: { type: "read-only-storage" } },
        {
          binding: 3,
          visibility: GPUShaderStage.COMPUTE,
          storageTexture: { format: "r32float", access: "write-only" },
        },
        { binding: 4, visibility: GPUShaderStage.COMPUTE, buffer: { type: "uniform" } },
      ],
    });

    const pipelineLayout = this.device.createPipelineLayout({
      bindGroupLayouts: [this.bindGroupLayout],
    });
    const shaderModule = this.device.createShaderModule({ code: shaderCode });
    this.pipeline = this.device.createComputePipeline({
      layout: pipelineLayout,
      compute: { module: shaderModule, entryPoint: "main" },
    });
  }

  public async uploadDem(width: number, height: number, demData: Float32Array): Promise<void> {
    if (demData.length < width * height) {
      throw new RangeError(`DEM length ${demData.length} < width*height (${width * height})`);
    }
    this.width = width;
    this.height = height;
    this.demTexture?.destroy();
    this.demTexture = this.device.createTexture({
      size: [width, height],
      format: "r32float",
      usage: GPUTextureUsage.TEXTURE_BINDING | GPUTextureUsage.COPY_DST,
    });
    const { padded, bytesPerRow } = packTextureRows(demData, width, height, 4);
    this.device.queue.writeTexture(
      { texture: this.demTexture },
      padded,
      { bytesPerRow, rowsPerImage: height },
      { width, height, depthOrArrayLayers: 1 },
    );
    this.initDepthOutTexture();
    this.updateParams();
    this.rebuildIndirectBuffer();
  }

  public async uploadCellIndexMap(width: number, height: number, data: Uint32Array): Promise<void> {
    if (data.length < width * height) {
      throw new RangeError(`cell index length ${data.length} < width*height (${width * height})`);
    }
    if (width !== this.width || height !== this.height) {
      throw new RangeError("cell index map dimensions must match DEM");
    }
    this.cellIndexTexture?.destroy();
    this.cellIndexTexture = this.device.createTexture({
      size: [width, height],
      format: "r32uint",
      usage: GPUTextureUsage.TEXTURE_BINDING | GPUTextureUsage.COPY_DST,
    });
    const { padded, bytesPerRow } = packTextureRows(data, width, height, 4);
    this.device.queue.writeTexture(
      { texture: this.cellIndexTexture },
      padded,
      { bytesPerRow, rowsPerImage: height },
      { width, height, depthOrArrayLayers: 1 },
    );
  }

  public uploadWseMm(wseMm: Int32Array): void {
    const copy = new Int32Array(wseMm);
    const byteLength = storageBufferSize(copy.byteLength, 4);
    this.wseCount = copy.length;
    if (!this.wseBuffer || this.wseBuffer.size < byteLength) {
      this.wseBuffer?.destroy();
      this.wseBuffer = this.device.createBuffer({
        size: byteLength,
        usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST,
      });
    }
    this.device.queue.writeBuffer(this.wseBuffer, 0, copy.buffer, copy.byteOffset, copy.byteLength);
  }

  private initDepthOutTexture(): void {
    this.depthOutTexture?.destroy();
    this.depthOutTexture = this.device.createTexture({
      size: [this.width, this.height],
      format: "r32float",
      usage:
        GPUTextureUsage.STORAGE_BINDING |
        GPUTextureUsage.TEXTURE_BINDING |
        GPUTextureUsage.COPY_SRC,
    });
  }

  private updateParams(): void {
    const paramsArray = new ArrayBuffer(uniformBufferSize(16));
    const dataView = new DataView(paramsArray);
    dataView.setUint32(0, this.width, true);
    dataView.setUint32(4, this.height, true);
    dataView.setUint32(8, 0xffffffff, true);
    dataView.setInt32(12, -9999, true);
    this.device.queue.writeBuffer(this.paramsBuffer, 0, paramsArray);
  }

  private rebuildIndirectBuffer(): void {
    this.indirectBuffer?.destroy();
    let counts = workgroupsForGrid(this.width, this.height, 16, 16, 1);
    counts = clampWorkgroupCounts(counts, this.device.limits);
    this.indirectBuffer = createIndirectDispatchBuffer(
      this.device,
      counts,
      "PTDT_DepthBakeIndirect",
    );
  }

  private assertReady(): void {
    if (!this.demTexture || !this.cellIndexTexture || !this.wseBuffer || !this.depthOutTexture) {
      throw new Error("Pipeline incomplete: Missing dependent textures/buffers");
    }
    if (this.wseCount <= 0) {
      throw new Error("Pipeline incomplete: WSE array is empty");
    }
  }

  private beginBakePass(): { encoder: GPUCommandEncoder; pass: GPUComputePassEncoder; bindGroup: GPUBindGroup } {
    this.assertReady();
    const bindGroup = this.device.createBindGroup({
      layout: this.bindGroupLayout,
      entries: [
        { binding: 0, resource: this.demTexture!.createView() },
        { binding: 1, resource: this.cellIndexTexture!.createView() },
        { binding: 2, resource: { buffer: this.wseBuffer! } },
        { binding: 3, resource: this.depthOutTexture!.createView() },
        { binding: 4, resource: { buffer: this.paramsBuffer } },
      ],
    });
    const encoder = this.device.createCommandEncoder();
    const pass = encoder.beginComputePass();
    pass.setPipeline(this.pipeline);
    pass.setBindGroup(0, bindGroup);
    return { encoder, pass, bindGroup };
  }

  /** Direct dispatch (default, deterministic). */
  public dispatchDepthBake(): GPUTexture {
    const { encoder, pass } = this.beginBakePass();
    pass.dispatchWorkgroups(Math.ceil(this.width / 16), Math.ceil(this.height / 16), 1);
    pass.end();
    this.device.queue.submit([encoder.finish()]);
    return this.depthOutTexture!;
  }

  /**
   * Indirect dispatch using precomputed workgroup counts (16x16).
   * Prefer direct unless GPU-driven counts are required.
   */
  public dispatchDepthBakeIndirect(): GPUTexture {
    if (!this.indirectBuffer) {
      this.rebuildIndirectBuffer();
    }
    const { encoder, pass } = this.beginBakePass();
    pass.dispatchWorkgroupsIndirect(this.indirectBuffer!, 0);
    pass.end();
    this.device.queue.submit([encoder.finish()]);
    return this.depthOutTexture!;
  }

  /**
   * GPU → CPU depth readback after bake.
   * Throws DepthReadbackError with code for soft-fail UI paths.
   */
  public async readDepthAsync(): Promise<DepthReadbackResult> {
    if (!this.depthOutTexture || this.width <= 0 || this.height <= 0) {
      throw new DepthReadbackError(
        "INVALID_DIMENSIONS",
        "No depth texture to read back; call uploadDem + dispatchDepthBake first",
      );
    }
    return readR32FloatTextureAsync(this.device, this.depthOutTexture, this.width, this.height);
  }

  public destroy(): void {
    this.demTexture?.destroy();
    this.cellIndexTexture?.destroy();
    this.depthOutTexture?.destroy();
    this.wseBuffer?.destroy();
    this.indirectBuffer?.destroy();
    this.paramsBuffer.destroy();
    this.demTexture = null;
    this.cellIndexTexture = null;
    this.depthOutTexture = null;
    this.wseBuffer = null;
    this.indirectBuffer = null;
  }
}
