import React, { useEffect, useRef } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import * as THREE from 'three';
import { depthColorExpression } from './map/maplibreCustomFilters';

export default function App() {
  const mapRef = useRef<HTMLDivElement>(null);
  const threeRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (!mapRef.current) return;
    const map = new maplibregl.Map({
      container: mapRef.current,
      style: 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
      center: [-88.0051, 37.8459],
      zoom: 13.8,
      pitch: 62,
      bearing: 45,
      antialias: true,
    });
    map.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), 'top-right');

    // Cinematic fog + atmosphere
    map.on('style.load', () => {
      map.setFog({
        color: 'rgb(10, 22, 40)',
        'high-color': 'rgb(20, 40, 70)',
        'horizon-blend': 0.15,
        'space-color': 'rgb(5, 10, 20)',
        'star-intensity': 0.4,
      });
    });

    // Three.js water surface overlay
    if (threeRef.current) {
      const renderer = new THREE.WebGLRenderer({ canvas: threeRef.current, alpha: true, antialias: true });
      renderer.setSize(window.innerWidth, window.innerHeight);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
      const scene = new THREE.Scene();
      const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
      camera.position.set(0, 8, 20);

      const geo = new THREE.PlaneGeometry(40, 40, 128, 128);
      const mat = new THREE.MeshStandardMaterial({
        color: 0x0ea5e9,
        transparent: true,
        opacity: 0.55,
        roughness: 0.15,
        metalness: 0.3,
      });
      const water = new THREE.Mesh(geo, mat);
      water.rotation.x = -Math.PI / 2;
      scene.add(water);

      const light = new THREE.DirectionalLight(0xffffff, 1.2);
      light.position.set(5, 20, 10);
      scene.add(light);
      scene.add(new THREE.AmbientLight(0x334455, 0.6));

      let t = 0;
      const animate = () => {
        t += 0.016;
        const pos = geo.attributes.position;
        for (let i = 0; i < pos.count; i++) {
          const x = pos.getX(i);
          const y = pos.getY(i);
          pos.setZ(i, Math.sin(x * 0.4 + t * 1.5) * 0.25 + Math.cos(y * 0.35 + t * 1.1) * 0.18);
        }
        pos.needsUpdate = true;
        geo.computeVertexNormals();
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
    }

    return () => map.remove();
  }, []);

  return (
    <div style={{ position: 'fixed', inset: 0, background: '#0a1628' }}>
      <div ref={mapRef} style={{ width: '100%', height: '100%' }} />
      <canvas
        ref={threeRef}
        style={{ position: 'absolute', inset: 0, pointerEvents: 'none', opacity: 0.7 }}
      />
      <div style={{
        position: 'absolute', top: 16, left: 16, right: 16,
        background: 'rgba(10,22,40,0.88)', color: '#e0f2fe',
        padding: '12px 18px', borderRadius: 12, fontSize: 15,
        backdropFilter: 'blur(12px)', border: '1px solid rgba(56,189,248,0.25)',
        fontFamily: 'system-ui, sans-serif',
      }}>
        PTDT Unified V33 — Cinematic Flood Twin · Point Township
      </div>
    </div>
  );
}
