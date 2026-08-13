/**
 * PTDT WebGPU SceneState synchronization client.
 *
 * JSON is retained for the control-plane envelope. The client validates every
 * manifest before writing Float32Array data into a GPUBuffer. The transport is
 * deliberately described as low-copy rather than zero-copy because WebSocket
 * and GPU queue boundaries necessarily perform ownership transfers.
 */

const DEFAULT_MAX_RECONNECT_DELAY_MS = 30_000;
const DEFAULT_INITIAL_RECONNECT_DELAY_MS = 1_000;
const DEFAULT_HEARTBEAT_INTERVAL_MS = 15_000;
const MATRIX_FLOAT_STRIDE = 16;
const FLOAT32_BYTES = 4;
const MAX_DRAW_CALLS = 100_000;
const SHA256_HEX_PATTERN = /^[0-9a-f]{64}$/i;

export class WebGPUSyncClient {
  constructor(endpointUrl, device, options = {}) {
    if (!(device instanceof GPUDevice)) {
      throw new TypeError("A valid GPUDevice is required.");
    }

    this.url = String(endpointUrl);
    this.device = device;
    this.protocolToken = options.protocolToken ?? null;
    this.sceneId = options.sceneId ?? "ptdt";
    this.viewportId = options.viewportId ?? "default";
    this.maxFps = Math.max(1, Math.min(120, options.maxFps ?? 30));
    this.heartbeatIntervalMs = Math.max(
      5_000,
      options.heartbeatIntervalMs ?? DEFAULT_HEARTBEAT_INTERVAL_MS,
    );
    this.maxReconnectDelayMs = Math.max(
      DEFAULT_INITIAL_RECONNECT_DELAY_MS,
      options.maxReconnectDelayMs ?? DEFAULT_MAX_RECONNECT_DELAY_MS,
    );
    this.socket = null;
    this.reconnectTimer = null;
    this.heartbeatTimer = null;
    this.reconnectDelayMs = DEFAULT_INITIAL_RECONNECT_DELAY_MS;
    this.closedByUser = false;
    this.lastSequence = -1;
    this.lastSceneStateVersion = -1;
    this.lastSeal = null;
    this.manifestSchemaVersion = 1;
    this.bufferCapacityBytes = 0;
    this.gpuStorageBuffer = null;

    this.ensureBufferCapacity(MATRIX_FLOAT_STRIDE * FLOAT32_BYTES * 256);
  }

  ensureBufferCapacity(requiredBytes) {
    if (!Number.isSafeInteger(requiredBytes) || requiredBytes <= 0) {
      throw new RangeError("GPU buffer size must be a positive safe integer.");
    }

    if (requiredBytes <= this.bufferCapacityBytes && this.gpuStorageBuffer) {
      return;
    }

    const maxStorageBindingSize = this.device.limits.maxStorageBufferBindingSize;
    if (requiredBytes > maxStorageBindingSize) {
      throw new RangeError(
        `Required transform buffer (${requiredBytes} bytes) exceeds WebGPU storage limit (${maxStorageBindingSize} bytes).`,
      );
    }

    this.gpuStorageBuffer?.destroy();
    this.gpuStorageBuffer = this.device.createBuffer({
      size: requiredBytes,
      usage: GPUBufferUsage.STORAGE | GPUBufferUsage.COPY_DST,
      label: "ptdt_authoritative_transform_buffer",
    });
    this.bufferCapacityBytes = requiredBytes;
  }

  initializeStream() {
    this.closedByUser = false;
    this.openSocket();
  }

  openSocket() {
    if (this.closedByUser) {
      return;
    }

    const protocols = ["ptdt.v1"];
    if (this.protocolToken) {
      protocols.push(`ptdt.token.${this.protocolToken}`);
    }

    this.socket = new WebSocket(this.url, protocols);
    this.socket.binaryType = "arraybuffer";

    this.socket.onopen = () => {
      this.reconnectDelayMs = DEFAULT_INITIAL_RECONNECT_DELAY_MS;
      this.startHeartbeat();
      this.send({
        type: "SUBSCRIBE",
        scene_id: this.sceneId,
        viewport_id: this.viewportId,
        max_fps: this.maxFps,
      });
    };

    this.socket.onmessage = async (event) => {
      try {
        if (typeof event.data === "string") {
          const payload = JSON.parse(event.data);
          await this.applySceneStateEnvelope(payload);
          return;
        }

        if (event.data instanceof ArrayBuffer) {
          await this.applyBinaryTransformFrame(event.data);
        }
      } catch (error) {
        this.dispatchError(error);
      }
    };

    this.socket.onerror = () => {
      this.dispatchError(new Error("PTDT WebSocket transport error."));
    };

    this.socket.onclose = () => {
      this.stopHeartbeat();
      this.socket = null;
      this.scheduleReconnect();
    };
  }

  startHeartbeat() {
    this.stopHeartbeat();
    this.heartbeatTimer = setInterval(() => {
      this.send({
        type: "PING",
        sequence: this.lastSequence >= 0 ? this.lastSequence : undefined,
      });
    }, this.heartbeatIntervalMs);
  }

  stopHeartbeat() {
    if (this.heartbeatTimer !== null) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  send(message) {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      return false;
    }

    const encoded = JSON.stringify(message);
    if (new TextEncoder().encode(encoded).byteLength > 32 * 1024) {
      throw new RangeError("PTDT WebSocket control message exceeds 32 KiB.");
    }

    this.socket.send(encoded);
    return true;
  }

  async applySceneStateEnvelope(envelope) {
    this.validateEnvelope(envelope);

    if (envelope.sequence <= this.lastSequence) {
      return;
    }

    if (this.lastSequence >= 0 && envelope.sequence > this.lastSequence + 1) {
      this.send({
        type: "RESYNC",
        sequence: this.lastSequence,
        scene_id: this.sceneId,
        viewport_id: this.viewportId,
      });
      this.dispatchError(
        new Error(
          `SceneState sequence gap detected: expected ${this.lastSequence + 1}, received ${envelope.sequence}.`,
        ),
      );
    }

    if (envelope.scene_state_version < this.lastSceneStateVersion) {
      return;
    }

    const manifest = envelope.payload;
    this.validateManifest(manifest, envelope.state_cryptographic_seal);
    this.writeManifestToGpu(manifest);

    this.lastSequence = envelope.sequence;
    this.lastSceneStateVersion = envelope.scene_state_version;
    this.lastSeal = envelope.state_cryptographic_seal;

    this.send({
      type: "ACK",
      sequence: envelope.sequence,
    });

    window.dispatchEvent(
      new CustomEvent("ptdt:frame-updated", {
        detail: {
          version: envelope.scene_state_version,
          sequence: envelope.sequence,
          frameIndex: envelope.frame_index,
          nodeCount: manifest.draw_call_count,
          seal: envelope.state_cryptographic_seal,
        },
      }),
    );
  }

  validateEnvelope(envelope) {
    if (!envelope || typeof envelope !== "object") {
      throw new TypeError("SceneState envelope must be an object.");
    }
    if (envelope.type !== "SCENE_STATE") {
      throw new TypeError("Unsupported PTDT stream message type.");
    }
    if (!Number.isInteger(envelope.sequence) || envelope.sequence < 0) {
      throw new TypeError("Invalid SceneState sequence.");
    }
    if (!Number.isInteger(envelope.scene_state_version) || envelope.scene_state_version < 0) {
      throw new TypeError("Invalid SceneState version.");
    }
    if (!SHA256_HEX_PATTERN.test(envelope.state_cryptographic_seal ?? "")) {
      throw new TypeError("Invalid SceneState cryptographic seal.");
    }
  }

  validateManifest(manifest, expectedSeal) {
    if (!manifest || typeof manifest !== "object") {
      throw new TypeError("WebGPU manifest must be an object.");
    }
    if (manifest.schema_version !== this.manifestSchemaVersion) {
      throw new Error(`Unsupported WebGPU manifest schema: ${manifest.schema_version}`);
    }
    if (!Number.isInteger(manifest.draw_call_count) || manifest.draw_call_count < 0 || manifest.draw_call_count > MAX_DRAW_CALLS) {
      throw new RangeError("Invalid WebGPU draw_call_count.");
    }
    if (manifest.transform_stride_f32 !== MATRIX_FLOAT_STRIDE) {
      throw new Error("Unsupported transform stride.");
    }
    if (manifest.state_cryptographic_seal !== expectedSeal) {
      throw new Error("Manifest seal does not match SceneState envelope seal.");
    }

    const transforms = manifest.transform_buffer_flat;
    const visibility = manifest.visibility_bitmask;
    const lodIndices = manifest.lod_indices;

    if (!Array.isArray(transforms) || transforms.length !== manifest.draw_call_count * MATRIX_FLOAT_STRIDE) {
      throw new Error("Transform buffer length does not match draw_call_count.");
    }
    if (!Array.isArray(visibility) || visibility.length !== manifest.draw_call_count) {
      throw new Error("Visibility buffer length does not match draw_call_count.");
    }
    if (!Array.isArray(lodIndices) || lodIndices.length !== manifest.draw_call_count) {
      throw new Error("LoD buffer length does not match draw_call_count.");
    }

    for (const value of transforms) {
      if (!Number.isFinite(value)) {
        throw new Error("Transform buffer contains a non-finite value.");
      }
    }
    for (const value of visibility) {
      if (value !== 0 && value !== 1) {
        throw new Error("Visibility buffer contains an invalid value.");
      }
    }
    for (const value of lodIndices) {
      if (!Number.isInteger(value) || value < 0 || value > 3) {
        throw new Error("LoD buffer contains an invalid value.");
      }
    }
  }

  writeManifestToGpu(manifest) {
    const requiredBytes = manifest.transform_buffer_flat.length * FLOAT32_BYTES;
    this.ensureBufferCapacity(Math.max(requiredBytes, FLOAT32_BYTES));

    const transformData = Float32Array.from(manifest.transform_buffer_flat);
    this.device.queue.writeBuffer(
      this.gpuStorageBuffer,
      0,
      transformData.buffer,
      transformData.byteOffset,
      transformData.byteLength,
    );
  }

  async applyBinaryTransformFrame(arrayBuffer) {
    if (!(arrayBuffer instanceof ArrayBuffer) || arrayBuffer.byteLength < 16) {
      throw new Error("Invalid binary PTDT frame.");
    }

    const header = new DataView(arrayBuffer, 0, 16);
    const magic = header.getUint32(0, true);
    const version = header.getUint32(4, true);
    const drawCallCount = header.getUint32(8, true);
    const transformBytes = header.getUint32(12, true);

    if (magic !== 0x50445431) {
      throw new Error("Invalid PTDT binary frame magic.");
    }
    if (version !== 1) {
      throw new Error(`Unsupported PTDT binary frame version: ${version}`);
    }
    if (drawCallCount > MAX_DRAW_CALLS) {
      throw new Error("Binary frame draw count exceeds safety limit.");
    }
    if (transformBytes !== drawCallCount * MATRIX_FLOAT_STRIDE * FLOAT32_BYTES) {
      throw new Error("Binary transform byte count is inconsistent.");
    }
    if (16 + transformBytes > arrayBuffer.byteLength) {
      throw new Error("Binary transform payload is truncated.");
    }

    const transformView = new Float32Array(arrayBuffer, 16, transformBytes / FLOAT32_BYTES);
    for (const value of transformView) {
      if (!Number.isFinite(value)) {
        throw new Error("Binary transform payload contains a non-finite value.");
      }
    }

    this.ensureBufferCapacity(Math.max(transformView.byteLength, FLOAT32_BYTES));
    this.device.queue.writeBuffer(
      this.gpuStorageBuffer,
      0,
      transformView.buffer,
      transformView.byteOffset,
      transformView.byteLength,
    );
  }

  scheduleReconnect() {
    if (this.closedByUser || this.reconnectTimer !== null) {
      return;
    }

    const delay = this.reconnectDelayMs;
    this.reconnectDelayMs = Math.min(
      this.reconnectDelayMs * 2,
      this.maxReconnectDelayMs,
    );

    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      this.openSocket();
    }, delay);
  }

  close() {
    this.closedByUser = true;
    this.stopHeartbeat();
    if (this.reconnectTimer !== null) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
    this.socket?.close(1000, "Client shutdown");
    this.socket = null;
    this.gpuStorageBuffer?.destroy();
    this.gpuStorageBuffer = null;
    this.bufferCapacityBytes = 0;
  }

  dispatchError(error) {
    console.error("[PTDT WebGPU]", error);
    window.dispatchEvent(
      new CustomEvent("ptdt:stream-error", {
        detail: { error },
      }),
    );
  }
}
