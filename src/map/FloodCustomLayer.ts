import maplibregl from 'maplibre-gl';
import * as THREE from 'three';

export function createFloodCustomLayer(id = 'ptdt-flood-layer'): maplibregl.CustomLayerInterface {
  let renderer: THREE.WebGLRenderer;
  let scene: THREE.Scene;
  let camera: THREE.Camera;
  let water: THREE.Mesh;
  let mapRef: maplibregl.Map;

  return {
    id,
    type: 'custom',
    renderingMode: '3d',

    onAdd(map: maplibregl.Map, gl: WebGLRenderingContext) {
      mapRef = map;
      renderer = new THREE.WebGLRenderer({ canvas: map.getCanvas(), context: gl, antialias: true });
      renderer.autoClear = false;
      scene = new THREE.Scene();
      camera = new THREE.Camera();
      const geo = new THREE.PlaneGeometry(0.02, 0.02, 64, 64);
      const mat = new THREE.MeshPhysicalMaterial({ color: 0x0a6ea8, transparent: true, opacity: 0.55, roughness: 0.1, metalness: 0.2, transmission: 0.3 });
      water = new THREE.Mesh(geo, mat);
      water.rotateX(-Math.PI / 2);
      scene.add(water);
      scene.add(new THREE.AmbientLight(0xffffff, 0.8));
    },

    render(_gl: WebGLRenderingContext, matrix: any) {
      camera.projectionMatrix = new THREE.Matrix4().fromArray(matrix);
      const pos = (water.geometry as THREE.PlaneGeometry).attributes.position as THREE.BufferAttribute;
      const t = performance.now() * 0.001;
      for (let i = 0; i < pos.count; i++) {
        const x = pos.getX(i);
        const y = pos.getY(i);
        pos.setZ(i, Math.sin(x * 80 + t) * 0.00015 + Math.cos(y * 60 + t * 0.8) * 0.0001);
      }
      pos.needsUpdate = true;
      renderer.resetState();
      renderer.render(scene, camera);
      mapRef.triggerRepaint();
    },

    onRemove() {
      renderer?.dispose();
    },
  };
}
