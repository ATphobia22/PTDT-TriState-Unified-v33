import * as THREE from 'three';

export class CinematicPostProcessing {
  private scene: THREE.Scene;
  private camera: THREE.OrthographicCamera;
  private material: THREE.ShaderMaterial;
  private quad: THREE.Mesh;
  private sceneTarget: THREE.WebGLRenderTarget;
  private bloomTarget: THREE.WebGLRenderTarget;
  private enabled = true;
  private bloomScale: number;

  constructor(
    private renderer: THREE.WebGLRenderer,
    width: number,
    height: number,
    bloomScale = 0.5
  ) {
    this.bloomScale = bloomScale;
    const opts: THREE.RenderTargetOptions = {
      minFilter: THREE.LinearFilter,
      magFilter: THREE.LinearFilter,
      format: THREE.RGBAFormat,
      type: THREE.UnsignedByteType,
      depthBuffer: false,
      stencilBuffer: false,
    };
    this.sceneTarget = new THREE.WebGLRenderTarget(width, height, { ...opts, depthBuffer: true });
    this.bloomTarget = new THREE.WebGLRenderTarget(
      Math.max(1, Math.floor(width * bloomScale)),
      Math.max(1, Math.floor(height * bloomScale)),
      opts
    );
    this.camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
    this.scene = new THREE.Scene();
    this.material = new THREE.ShaderMaterial({
      uniforms: {
        tDiffuse: { value: null },
        tBloom: { value: null },
        resolution: { value: new THREE.Vector2(width, height) },
        time: { value: 0 },
        bloomStrength: { value: 0.4 },
        vignette: { value: 0.5 },
        grain: { value: 0.03 },
        enabled: { value: 1 },
      },
      vertexShader: `varying vec2 vUv; void main() { vUv = uv; gl_Position = vec4(position, 1.0); }`,
      fragmentShader: `
        uniform sampler2D tDiffuse; uniform sampler2D tBloom; uniform vec2 resolution;
        uniform float time; uniform float bloomStrength; uniform float vignette;
        uniform float grain; uniform float enabled; varying vec2 vUv;
        float rand(vec2 co) { return fract(sin(dot(co.xy, vec2(12.9898, 78.233))) * 43758.5453 + time); }
        void main() {
          vec4 color = texture2D(tDiffuse, vUv);
          if (enabled < 0.5) { gl_FragColor = color; return; }
          vec3 bloom = texture2D(tBloom, vUv).rgb;
          color.rgb += bloom * bloomStrength;
          vec2 uv = vUv - 0.5;
          float vig = clamp(1.0 - dot(uv, uv) * vignette * 2.0, 0.0, 1.0);
          color.rgb *= vig;
          float g = (rand(gl_FragCoord.xy * 0.5) - 0.5) * grain;
          color.rgb += g;
          color.r *= 1.03; color.b *= 1.05;
          gl_FragColor = color;
        }`,
      depthTest: false,
      depthWrite: false,
    });
    this.quad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), this.material);
    this.scene.add(this.quad);
  }

  setEnabled(v: boolean): void {
    this.enabled = v;
    this.material.uniforms.enabled.value = v ? 1 : 0;
  }

  setSize(width: number, height: number): void {
    this.sceneTarget.setSize(width, height);
    this.bloomTarget.setSize(
      Math.max(1, Math.floor(width * this.bloomScale)),
      Math.max(1, Math.floor(height * this.bloomScale))
    );
    this.material.uniforms.resolution.value.set(width, height);
  }

  render(scene: THREE.Scene, camera: THREE.Camera, time: number): void {
    if (!this.enabled) {
      this.renderer.setRenderTarget(null);
      this.renderer.render(scene, camera);
      return;
    }
    this.renderer.setRenderTarget(this.sceneTarget);
    this.renderer.clear();
    this.renderer.render(scene, camera);
    this.renderer.setRenderTarget(this.bloomTarget);
    this.renderer.clear();
    this.material.uniforms.tDiffuse.value = this.sceneTarget.texture;
    this.material.uniforms.tBloom.value = null;
    this.renderer.render(this.scene, this.camera);
    this.renderer.setRenderTarget(null);
    this.material.uniforms.tDiffuse.value = this.sceneTarget.texture;
    this.material.uniforms.tBloom.value = this.bloomTarget.texture;
    this.material.uniforms.time.value = time;
    this.renderer.render(this.scene, this.camera);
  }

  dispose(): void {
    this.sceneTarget.dispose();
    this.bloomTarget.dispose();
    this.material.dispose();
    this.quad.geometry.dispose();
  }
}
