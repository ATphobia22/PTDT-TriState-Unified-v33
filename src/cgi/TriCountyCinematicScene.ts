import * as THREE from 'three';
import { createDisplacedTerrain } from './TerrainDisplacement';
import { CinematicPostProcessing } from './PostProcessing';
import { stageVsBfe, SITE } from '../lib/elevationCheck';

export interface CinematicOptions {
  heightUrl?: string;
  enablePost?: boolean;
  dayNightCycle?: boolean;
}

export class TriCountyCinematicScene {
  scene: THREE.Scene;
  camera: THREE.PerspectiveCamera;
  renderer: THREE.WebGLRenderer;
  post: CinematicPostProcessing | null = null;
  private water: THREE.Mesh;
  private spray: THREE.Points;
  private sun: THREE.DirectionalLight;
  private hemi: THREE.HemisphereLight;
  private clock = new THREE.Clock();
  private time = 0;
  private opts: CinematicOptions;

  constructor(canvas: HTMLCanvasElement, opts: CinematicOptions = {}) {
    this.opts = opts;
    this.renderer = new THREE.WebGLRenderer({
      canvas,
      alpha: true,
      antialias: true,
      powerPreference: 'high-performance',
    });
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.15;

    this.scene = new THREE.Scene();
    this.scene.fog = new THREE.FogExp2(0x0a1628, 0.012);

    this.camera = new THREE.PerspectiveCamera(42, window.innerWidth / window.innerHeight, 0.1, 4000);
    this.camera.position.set(0, 18, 42);
    this.camera.lookAt(0, 0, 0);

    const terrain = createDisplacedTerrain({
      heightUrl: opts.heightUrl ?? '/tiles/posey_height_preview.png',
      width: 120,
      depth: 120,
      segments: 320,
      displacementScale: 48,
      onError: (e) => console.warn('[Cinematic]', e.message),
    });
    this.scene.add(terrain);

    const waterGeo = new THREE.PlaneGeometry(110, 110, 192, 192);
    const waterMat = new THREE.MeshPhysicalMaterial({
      color: 0x0a6ea8,
      transparent: true,
      opacity: 0.62,
      roughness: 0.08,
      metalness: 0.25,
      transmission: 0.35,
      thickness: 1.4,
      ior: 1.33,
      envMapIntensity: 1.5,
    });
    this.water = new THREE.Mesh(waterGeo, waterMat);
    this.water.rotation.x = -Math.PI / 2;
    this.water.position.y = 0.12;
    this.scene.add(this.water);

    this.sun = new THREE.DirectionalLight(0xfff4e0, 1.7);
    this.sun.position.set(22, 38, 14);
    this.scene.add(this.sun);
    this.scene.add(new THREE.AmbientLight(0x2a3f55, 0.5));
    this.hemi = new THREE.HemisphereLight(0x87b5e0, 0x1a2a1a, 0.45);
    this.scene.add(this.hemi);

    const count = 600;
    const geo = new THREE.BufferGeometry();
    const pos = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      pos[i * 3] = (Math.random() - 0.5) * 90;
      pos[i * 3 + 1] = Math.random() * 4;
      pos[i * 3 + 2] = (Math.random() - 0.5) * 90;
    }
    geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    this.spray = new THREE.Points(
      geo,
      new THREE.PointsMaterial({ color: 0xb0e0ff, size: 0.09, transparent: true, opacity: 0.4 })
    );
    this.scene.add(this.spray);

    if (opts.enablePost !== false) {
      this.post = new CinematicPostProcessing(this.renderer, window.innerWidth, window.innerHeight);
    }

    console.log('[PTDT Cinematic] LAG', stageVsBfe(SITE.lag_ft));
    window.addEventListener('resize', this.onResize);
  }

  private onResize = (): void => {
    const w = window.innerWidth;
    const h = window.innerHeight;
    this.renderer.setSize(w, h);
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
    this.post?.setSize(w, h);
  };

  setOrbit(radius = 42, height = 18, speed = 0.08): void {
    const t = this.time * speed;
    this.camera.position.x = Math.cos(t) * radius;
    this.camera.position.z = Math.sin(t) * radius;
    this.camera.position.y = height + Math.sin(t * 0.5) * 3;
    this.camera.lookAt(0, 0, 0);
  }

  render(): void {
    const dt = this.clock.getDelta();
    this.time += dt;

    const pos = this.water.geometry.attributes.position as THREE.BufferAttribute;
    for (let i = 0; i < pos.count; i++) {
      const x = pos.getX(i);
      const y = pos.getY(i);
      pos.setZ(
        i,
        Math.sin(x * 0.32 + this.time * 1.3) * 0.2 +
          Math.cos(y * 0.26 + this.time * 1.0) * 0.14 +
          Math.sin((x + y) * 0.18 + this.time * 1.7) * 0.08
      );
    }
    pos.needsUpdate = true;
    this.water.geometry.computeVertexNormals();

    const sp = this.spray.geometry.attributes.position as THREE.BufferAttribute;
    for (let i = 0; i < sp.count; i++) {
      let py = sp.getY(i) + 0.01;
      if (py > 4.2) py = 0.05;
      sp.setY(i, py);
    }
    sp.needsUpdate = true;

    if (this.opts.dayNightCycle) {
      const sunT = (Math.sin(this.time * 0.02) + 1) * 0.5;
      this.sun.intensity = 0.4 + sunT * 1.4;
      this.hemi.intensity = 0.2 + sunT * 0.35;
      this.renderer.toneMappingExposure = 0.85 + sunT * 0.4;
    }

    if (this.post) {
      this.post.render(this.scene, this.camera, this.time);
    } else {
      this.renderer.render(this.scene, this.camera);
    }
  }

  dispose(): void {
    window.removeEventListener('resize', this.onResize);
    this.post?.dispose();
    this.renderer.dispose();
  }
}
