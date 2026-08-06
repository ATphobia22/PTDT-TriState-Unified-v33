import * as THREE from 'three';

export function createFloodWaterMaterial(timeUniform: { value: number }) {
  return new THREE.ShaderMaterial({
    transparent: true,
    side: THREE.DoubleSide,
    uniforms: {
      uTime: timeUniform,
      uDeepColor: { value: new THREE.Color(0x031428) },
      uShallowColor: { value: new THREE.Color(0x0ea5e9) },
      uFoamColor: { value: new THREE.Color(0xe0f2fe) },
      uCameraPos: { value: new THREE.Vector3() },
      uOpacity: { value: 0.65 },
    },
    vertexShader: /* glsl */ `
      uniform float uTime;
      varying vec2 vUv;
      varying vec3 vWorldPos;
      varying float vWave;
      void main() {
        vUv = uv;
        vec3 pos = position;
        float w1 = sin(pos.x * 0.35 + uTime * 1.4) * 0.22;
        float w2 = cos(pos.y * 0.28 + uTime * 1.1) * 0.16;
        float w3 = sin((pos.x + pos.y) * 0.2 + uTime * 1.9) * 0.09;
        vWave = w1 + w2 + w3;
        pos.z += vWave;
        vec4 world = modelMatrix * vec4(pos, 1.0);
        vWorldPos = world.xyz;
        gl_Position = projectionMatrix * viewMatrix * world;
      }
    `,
    fragmentShader: /* glsl */ `
      uniform float uTime;
      uniform vec3 uDeepColor;
      uniform vec3 uShallowColor;
      uniform vec3 uFoamColor;
      uniform vec3 uCameraPos;
      uniform float uOpacity;
      varying vec2 vUv;
      varying vec3 vWorldPos;
      varying float vWave;
      void main() {
        float depthFactor = smoothstep(-0.3, 0.4, vWave);
        vec3 col = mix(uDeepColor, uShallowColor, depthFactor);
        float foam = pow(1.0 - smoothstep(-0.15, 0.25, vWave), 2.5);
        col = mix(col, uFoamColor, foam * 0.7);
        float sparkle = sin(vUv.x * 50.0 + uTime * 3.0) * cos(vUv.y * 42.0 + uTime * 2.6) * 0.1;
        col += sparkle * (1.0 - foam);
        vec3 viewDir = normalize(uCameraPos - vWorldPos);
        float fresnel = pow(1.0 - max(dot(viewDir, vec3(0.0, 1.0, 0.0)), 0.0), 3.0);
        col = mix(col, vec3(0.75, 0.9, 1.0), fresnel * 0.3);
        gl_FragColor = vec4(col, mix(uOpacity * 0.7, uOpacity, depthFactor));
      }
    `,
  });
}
