// PTDT Photoreal Terrain — full vertex + fragment (WebGPU / WGSL)
// Free OSS: Indiana GIO / AWS DEM heightmap + BFE-aware water/terrain

struct Uniforms {
  viewProj: mat4x4<f32>,
  invViewProj: mat4x4<f32>,
  cameraPos: vec3<f32>,
  time: f32,
  lightDir: vec3<f32>,
  bfeScaled: f32,
  resolution: vec2<f32>,
  _pad: vec2<f32>,
};

struct VertexOut {
  @builtin(position) position: vec4<f32>,
  @location(0) uv: vec2<f32>,
  @location(1) worldPos: vec3<f32>,
};

@group(0) @binding(0) var<uniform> u: Uniforms;
@group(0) @binding(1) var heightTex: texture_2d<f32>;
@group(0) @binding(2) var heightSamp: sampler;

const MAX_STEPS: i32 = 192;
const MAX_DIST: f32 = 800.0;
const SURF_DIST: f32 = 0.025;

@vertex
fn vs(@builtin(vertex_index) vid: u32) -> VertexOut {
  var out: VertexOut;
  let x = f32(i32(vid & 1u) * 4 - 1);
  let y = f32(i32(vid >> 1u) * 4 - 1);
  out.uv = vec2<f32>(x, y) * 0.5 + 0.5;
  out.position = vec4<f32>(x, y, 0.0, 1.0);
  out.worldPos = u.cameraPos;
  return out;
}

fn sampleHeight(xz: vec2<f32>) -> f32 {
  let uv = xz * 0.008 + 0.5;
  let h = textureSampleLevel(heightTex, heightSamp, clamp(uv, vec2<f32>(0.0), vec2<f32>(1.0)), 0.0).r;
  return h * 48.0 - 12.0;
}

fn terrainSDF(p: vec3<f32>) -> f32 {
  return p.y - sampleHeight(p.xz);
}

fn calcNormal(p: vec3<f32>) -> vec3<f32> {
  let e = vec2<f32>(0.12, 0.0);
  return normalize(vec3<f32>(
    terrainSDF(p + e.xyy) - terrainSDF(p - e.xyy),
    terrainSDF(p + e.yxy) - terrainSDF(p - e.yxy),
    terrainSDF(p + e.yyx) - terrainSDF(p - e.yyx)
  ));
}

fn rayMarch(ro: vec3<f32>, rd: vec3<f32>) -> f32 {
  var d = 0.0;
  for (var i = 0; i < MAX_STEPS; i++) {
    let p = ro + rd * d;
    let ds = terrainSDF(p);
    if (abs(ds) < SURF_DIST || d > MAX_DIST) { break; }
    d += max(ds * 0.8, 0.02);
  }
  return d;
}

fn skyColor(rd: vec3<f32>, sun: vec3<f32>) -> vec3<f32> {
  let t = max(rd.y, 0.0);
  let zenith = vec3<f32>(0.04, 0.10, 0.26);
  let horizon = vec3<f32>(0.42, 0.52, 0.72);
  var col = mix(horizon, zenith, pow(t, 0.65));
  let sunDot = max(dot(rd, sun), 0.0);
  col += vec3<f32>(1.0, 0.92, 0.75) * pow(sunDot, 256.0) * 2.8;
  col += vec3<f32>(1.0, 0.55, 0.28) * pow(sunDot, 6.0) * 0.4;
  return col;
}

fn waterColor(p: vec3<f32>, n: vec3<f32>, rd: vec3<f32>, sun: vec3<f32>) -> vec3<f32> {
  let fresnel = pow(1.0 - max(dot(-rd, n), 0.0), 4.0);
  let refl = skyColor(reflect(rd, n), sun);
  let base = vec3<f32>(0.035, 0.22, 0.40);
  let foam = smoothstep(0.35, 0.0, abs(p.y - sampleHeight(p.xz)));
  return mix(base, refl, fresnel * 0.75) + foam * vec3<f32>(0.3);
}

@fragment
fn fs(in: VertexOut) -> @location(0) vec4<f32> {
  let uvNdc = in.uv * 2.0 - 1.0;
  let ndc = vec4<f32>(uvNdc.x, -uvNdc.y, 1.0, 1.0);
  let world = u.invViewProj * ndc;
  let rd = normalize(world.xyz / world.w - u.cameraPos);
  let ro = u.cameraPos;
  let d = rayMarch(ro, rd);
  var col: vec3<f32>;
  let sun = normalize(u.lightDir);
  if (d < MAX_DIST) {
    let p = ro + rd * d;
    let n = calcNormal(p);
    let elev = sampleHeight(p.xz);
    if (elev < u.bfeScaled) {
      col = waterColor(p, n, rd, sun);
    } else {
      var albedo = vec3<f32>(0.11, 0.20, 0.09);
      albedo = mix(albedo, vec3<f32>(0.34, 0.30, 0.20), smoothstep(0.0, 22.0, elev));
      let diff = max(dot(n, sun), 0.0);
      col = albedo * (0.22 + diff * 0.88);
      let h = normalize(sun - rd);
      col += vec3<f32>(1.0) * pow(max(dot(n, h), 0.0), 64.0) * 0.12;
    }
    let fog = 1.0 - exp(-d * 0.0038);
    col = mix(col, skyColor(rd, sun) * 0.55, fog);
  } else {
    col = skyColor(rd, sun);
  }
  col = col * 1.08;
  col = col / (col + vec3<f32>(1.0));
  col = pow(col, vec3<f32>(1.0 / 2.2));
  return vec4<f32>(col, 1.0);
}
