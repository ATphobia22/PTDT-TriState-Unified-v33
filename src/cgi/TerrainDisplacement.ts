import * as THREE from 'three';

export interface TerrainOptions {
  heightUrl?: string;
  width?: number;
  depth?: number;
  segments?: number;
  displacementScale?: number;
  color?: number;
  onError?: (err: Error) => void;
  onLoaded?: (mesh: THREE.Mesh) => void;
  fallbackColor?: number;
}

export function createDisplacedTerrain(options: TerrainOptions = {}): THREE.Mesh {
  const heightUrl: string = options.heightUrl ?? '/tiles/posey_height_preview.png';
  const width: number = options.width ?? 80;
  const depth: number = options.depth ?? 80;
  const segments: number = options.segments ?? 256;
  const displacementScale: number = options.displacementScale ?? 42;
  const color: number = options.color ?? 0x1a2f1a;
  const fallbackColor: number = options.fallbackColor ?? 0x2a3f2a;
  const onError = options.onError;
  const onLoaded = options.onLoaded;

  const geometry = new THREE.PlaneGeometry(width, depth, segments, segments);
  const material = new THREE.MeshStandardMaterial({
    color,
    roughness: 0.85,
    metalness: 0.05,
    displacementScale,
    flatShading: false,
  });

  const mesh = new THREE.Mesh(geometry, material);
  mesh.rotation.x = -Math.PI / 2;
  mesh.position.y = -1.2;
  mesh.name = 'posey-terrain';

  const applyFallback = (reason: string): void => {
    console.warn(`[PTDT Terrain] ${reason} — using flat fallback`);
    material.color.setHex(fallbackColor);
    material.displacementMap = null;
    material.displacementScale = 0;
    material.needsUpdate = true;

    const posAttr = geometry.getAttribute('position');
    if (posAttr instanceof THREE.BufferAttribute) {
      for (let i = 0; i < posAttr.count; i++) {
        const x = posAttr.getX(i);
        const y = posAttr.getY(i);
        const h =
          Math.sin(x * 0.08) * 1.8 +
          Math.cos(y * 0.07) * 1.4 -
          Math.exp(-((x * x + y * y) * 0.0015)) * 3.5;
        posAttr.setZ(i, h);
      }
      posAttr.needsUpdate = true;
    }
    geometry.computeVertexNormals();
    onError?.(new Error(reason));
  };

  if (!heightUrl) {
    applyFallback('No heightUrl provided');
    return mesh;
  }

  const loader = new THREE.TextureLoader();
  loader.load(
    heightUrl,
    (tex: THREE.Texture) => {
      if (!tex.image) {
        applyFallback('Heightmap texture empty');
        return;
      }
      tex.colorSpace = THREE.NoColorSpace;
      tex.wrapS = THREE.ClampToEdgeWrapping;
      tex.wrapT = THREE.ClampToEdgeWrapping;
      tex.minFilter = THREE.LinearFilter;
      tex.magFilter = THREE.LinearFilter;
      material.displacementMap = tex;
      material.needsUpdate = true;
      geometry.computeVertexNormals();
      onLoaded?.(mesh);
    },
    undefined,
    (err: unknown) => {
      const message = err instanceof Error ? err.message : String(err);
      applyFallback(`Heightmap load failed: ${message}`);
    }
  );

  return mesh;
}
