import React, { useEffect, useRef } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import * as THREE from 'three';
import { createDisplacedTerrain } from './cgi/TerrainDisplacement';
import { stageVsBfe, compensatoryStorage, SITE } from './lib/elevationCheck';

export default function App() {
  const mapRef = useRef<HTMLDivElement>(null);
  const threeRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!mapRef.current || !threeRef.current) return;

    const map = new maplibregl.Map({
      container: mapRef.current,
      style: 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
      center: [-88.0051, 37.8459],
      zoom: 13.6,
      pitch: 68,
      bearing: 38,
      antialias: true,
      maxPitch: 85,
    });
    map.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), 'top-right');

    map.on('style.load', () => {
      map.setFog({
        color: 'rgb(8, 18, 32)',
        'high-color': 'rgb(18, 36, 62)',
        'horizon-blend': 0.18,
        'space-color': 'rgb(3, 6, 14)',
        'star-intensity': 0.55,
      });
    });

    const canvas = threeRef.current;
    const renderer = new THREE.WebGLRenderer({
      canvas,
      alpha: true,
      antialias: true,
      powerPreference: 'high-performance',
    });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.15;

    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x0a1628, 0.012);

    const camera = new THREE.PerspectiveCamera(42, window.innerWidth / window.innerHeight, 0.1, 2000);
    camera.position.set(0, 12, 28);
    camera.lookAt(0, 0, 0);

    const terrain = createDisplacedTerrain({
      heightUrl: '/tiles/posey_height_preview.png',
      width: 80,
      depth: 80,
      segments: 256,
      displacementScale: 42,
      color: 0x1a2f1a,
    });
    scene.add(terrain);

    const waterGeo = new THREE.PlaneGeometry(70, 70, 160, 160);
    const waterMat = new THREE.MeshPhysicalMaterial({
      color: 0x0a6ea8,
      transparent: true,
      opacity: 0.62,
      roughness: 0.08,
      metalness: 0.25,
      transmission: 0.35,
      thickness: 1.2,
      envMapIntensity: 1.4,
    });
    const water = new THREE.Mesh(waterGeo, waterMat);
    water.rotation.x = -Math.PI / 2;
    water.position.y = 0.15;
    scene.add(water);

    const sun = new THREE.DirectionalLight(0xfff4e0, 1.6);
    sun.position.set(18, 32, 12);
    scene.add(sun);
    scene.add(new THREE.AmbientLight(0x2a3f55, 0.55));
    scene.add(new THREE.HemisphereLight(0x87b5e0, 0x1a2a1a, 0.4));

    const sprayCount = 400;
    const sprayGeo = new THREE.BufferGeometry();
    const sprayPos = new Float32Array(sprayCount * 3);
    for (let i = 0; i < sprayCount; i++) {
      sprayPos[i * 3] = (Math.random() - 0.5) * 50;
      sprayPos[i * 3 + 1] = Math.random() * 2.5;
      sprayPos[i * 3 + 2] = (Math.random() - 0.5) * 50;
    }
    sprayGeo.setAttribute('position', new THREE.BufferAttribute(sprayPos, 3));
    const spray = new THREE.Points(
      sprayGeo,
      new THREE.PointsMaterial({ color: 0xb0e0ff, size: 0.08, transparent: true, opacity: 0.45 })
    );
    scene.add(spray);

    console.log('[PTDT] LAG check', stageVsBfe(SITE.lag_ft));
    console.log('[PTDT] Berm check', stageVsBfe(SITE.berm_crest_ft));
    console.log('[PTDT] Storage', compensatoryStorage(1000));

    let t = 0;
    const animate = () => {
      t += 0.014;
      const pos = waterGeo.attributes.position as THREE.BufferAttribute;
      for (let i = 0; i < pos.count; i++) {
        const x = pos.getX(i);
        const y = pos.getY(i);
        pos.setZ(i, Math.sin(x * 0.35 + t * 1.4) * 0.22 + Math.cos(y * 0.28 + t * 1.1) * 0.16 + Math.sin((x + y) * 0.2 + t * 1.9) * 0.09);
      }
      pos.needsUpdate = true;
      waterGeo.computeVertexNormals();

      const sp = sprayGeo.attributes.position as THREE.BufferAttribute;
      for (let i = 0; i < sprayCount; i++) {
        let py = sp.getY(i) + 0.008;
        if (py > 2.8) py = 0.05;
        sp.setY(i, py);
      }
      sp.needsUpdate = true;

      renderer.render(scene, camera);
      requestAnimationFrame(animate);
    };
    animate();

    const onResize = () => {
      renderer.setSize(window.innerWidth, window.innerHeight);
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
    };
    window.addEventListener('resize', onResize);

    return () => {
      window.removeEventListener('resize', onResize);
      map.remove();
      renderer.dispose();
    };
  }, []);

  return (
    <div style={{ position: 'fixed', inset: 0, background: '#0a1628' }}>
      <div ref={mapRef} style={{ width: '100%', height: '100%' }} />
      <canvas ref={threeRef} style={{ position: 'absolute', inset: 0, pointerEvents: 'none', mixBlendMode: 'screen', opacity: 0.85 }} />
      <div style={{ position: 'absolute', top: 14, left: 14, right: 14, background: 'rgba(8,16,28,0.9)', color: '#e0f2fe', padding: '11px 16px', borderRadius: 11, fontSize: 14, backdropFilter: 'blur(14px)', border: '1px solid rgba(56,189,248,0.22)', fontFamily: 'system-ui,Segoe UI,sans-serif' }}>
        PTDT Unified V33 — Virtual Tri-State River Valley · Posey DEM + Archimedes BFE 375.0 ft NAVD88
      </div>
    </div>
  );
}
