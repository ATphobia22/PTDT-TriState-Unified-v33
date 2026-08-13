struct TransformBuffer {
  transforms: array<mat4x4<f32>>,
};

struct UintBuffer {
  values: array<u32>,
};

@group(0) @binding(0)
var<storage, read> transformBuffer: TransformBuffer;

@group(0) @binding(1)
var<storage, read> visibilityBuffer: UintBuffer;

@group(0) @binding(2)
var<storage, read> lodBuffer: UintBuffer;

struct SceneManifestMetadata {
  sceneStateVersion: u32,
  drawCallCount: u32,
  transformStrideF32: u32,
  schemaVersion: u32,
};

@group(0) @binding(3)
var<uniform> metadata: SceneManifestMetadata;

@vertex
fn main_vertex(@builtin(vertex_index) vertexIndex: u32) -> @builtin(position) vec4<f32> {
  let assetIndex = vertexIndex;
  if (assetIndex >= metadata.drawCallCount) {
    return vec4<f32>(0.0, 0.0, 0.0, 1.0);
  }

  let transform = transformBuffer.transforms[assetIndex];
  let visible = visibilityBuffer.values[assetIndex] == 1u;
  if (!visible) {
    return vec4<f32>(0.0, 0.0, 0.0, 0.0);
  }

  let lod = lodBuffer.values[assetIndex];
  let scale = max(1.0, f32(lod));
  return transform * vec4<f32>(0.0, 0.0, -scale, 1.0);
}
