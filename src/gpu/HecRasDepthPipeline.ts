/// <reference types="@webgpu/types" />

/**
 * WebGPU depth bake: DEM + cell_index_map + WSE_mm → r32float depth.
 * bytesPerRow padded to 256 for writeTexture.
 */
export class HecRasDepthPipeline {
  private device: GPUDevice;
  private pipeline: GPUComputePipeline;
  private bindGroupLayout: GPUBindGroupLayout;
  private demTexture: GPUTexture | null = null;
  private cellIndexTexture: GPUTexture | null = null;
  private wseBuffer: GPUBuffer | null = null;
  private paramsBuffer: GPUBuffer;
  public depthOutTexture: GPUTexture | null = null;
  private width = 0;
  private height = 0;

  constructor(device: GPUDevice, shaderCode: string) {
    this.device = device;
    this.paramsBuffer = this.device.createBuffer({
      size: 16,
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
    this.width = width;
    this.height = height;
    this.demTexture = this.device.createTexture({
      size: [width, height],
      format: "r32float",
      usage: GPUTextureUsage.TEXTURE_BINDING | GPUTextureUsage.COPY_DST,
    });
    const bytesPerRow = Math.ceil((width * 4) / 256) * 256;
    const padded = new Uint8Array(bytesPerRow * height);
    const src = new Uint8Array(demData.buffer, demData.byteOffset, demData.byteLength);
    for (let y = 0; y < height; y++) {
      padded.set(src.subarray(y * width * 4, (y + 1) * width * 4), y * bytesPerRow);
    }
    this.device.queue.writeTexture(
      { texture: this.demTexture },
      padded,
      { bytesPerRow, rowsPerImage: height },
      { width, height, depthOrArrayLayers: 1 },
    );
    this.initDepthOutTexture();
    this.updateParams();
  }

  public async uploadCellIndexMap(width: number, height: number, data: Uint32Array): Promise<void> {
    this.cellIndexTexture = this.device.createTexture({
      size: [width, height],
      format: "r32uint",
      usage: GPUTextureUsage.TEXTURE_BINDING | GPUTextureUsage.COPY_DST,
    });
    const bytesPerRow = Math.ceil((width * 4) / 256) * 256;
    const padded = new Uint8Array(bytesPerRow * height);
    const src = new Uint8Array(data.buffer, data.byteOffset, data.byteLength);
    for (let y = 0; y < height; y++) {
      padded.set(src.subarray(y * width * 4, (y + 1) * width * 4), y * bytesPerRow);
    }
    this.device.queue.writeTexture(
      { texture: this.cellIndexTexture },
      padded,
      { bytesPerRow, rowsPerImage: height },
      { width, height, depthOrArrayLayers: 1 },
    );
  }

  public uploadWseMm(wseMm: Int32Array): void {
    const copy = new Int32Array(wseMm);
    const byteLength = copy.byteLength;
    if (!this.wseBuffer || this.wseBuffer.size < byteLength) {
      this.wseBuffer?.destroy();
      this.wseBuffer = this.device.createBuffer({
        size: Math.max(byteLength, 4),
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
    const paramsArray = new ArrayBuffer(16);
    const dataView = new DataView(paramsArray);
    dataView.setUint32(0, this.width, true);
    dataView.setUint32(4, this.height, true);
    dataView.setUint32(8, 0xffffffff, true);
    dataView.setInt32(12, -9999, true);
    this.device.queue.writeBuffer(this.paramsBuffer, 0, paramsArray);
  }

  public dispatchDepthBake(): GPUTexture {
    if (!this.demTexture || !this.cellIndexTexture || !this.wseBuffer || !this.depthOutTexture) {
      throw new Error("Pipeline incomplete: Missing dependent textures/buffers");
    }
    const bindGroup = this.device.createBindGroup({
      layout: this.bindGroupLayout,
      entries: [
        { binding: 0, resource: this.demTexture.createView() },
        { binding: 1, resource: this.cellIndexTexture.createView() },
        { binding: 2, resource: { buffer: this.wseBuffer } },
        { binding: 3, resource: this.depthOutTexture.createView() },
        { binding: 4, resource: { buffer: this.paramsBuffer } },
      ],
    });
    const commandEncoder = this.device.createCommandEncoder();
    const passEncoder = commandEncoder.beginComputePass();
    passEncoder.setPipeline(this.pipeline);
    passEncoder.setBindGroup(0, bindGroup);
    passEncoder.dispatchWorkgroups(Math.ceil(this.width / 16), Math.ceil(this.height / 16), 1);
    passEncoder.end();
    this.device.queue.submit([commandEncoder.finish()]);
    return this.depthOutTexture;
  }
}
