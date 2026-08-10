import React, { useEffect, useRef, useState } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import * as THREE from 'three';
import { gradeFromFloodDepth } from './cgi/CinematicGrade';
import { ForensicHUD } from './cgi/ForensicHUD';
import { CinematicCameraController, BONEBANK_TRACKS } from './cgi/CinematicCamera';
import { resolveWeather } from './cgi/WeatherStateMachine';
import { createFloodWaterMaterial } from './cgi/FloodWaterMaterial';
import { fetchWabashNewHarmony } from './services/usgsTelemetry';
import { simplifiedBishopFoS, FEDERAL_FOS_THRESHOLD } from './services/bishopFoS';

export default function App() {
  const mapRef = useRef<HTMLDivElement>(null);
  const threeRef = useRef<HTMLCanvasElement>(null);
  const [hud, setHud] = useState({
    stageFt: 0,
    depthM: 0,
    dischargeCfs: 0,
    fos: 2.1,
    station: '03378500',
    timestamp: new Date().toISOString(),
    alert: false,
  });

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
    renderer.toneMappingExposure = 1.1;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(42, window.innerWidth / window.innerHeight, 0.1, 2000);
    camera.position.set(0, 12, 28);
    const camCtrl = new CinematicCameraController(camera);

    // terrain
    const terrainGeo = new THREE.PlaneGeometry(80, 80, 96, 96);
    const tPos = terrainGeo.attributes.position;
    for (let i = 0; i < tPos.count; i++) {
      const x = tPos.getX(i);
      const y = tPos.getY(i);
      const h =
        Math.sin(x * 0.08) * 1.8 +
        Math.cos(y * 0.07) * 1.4 +
        Math.sin((x + y) * 0.05) * 0.9 -
        Math.exp(-((x * x + y * y) * 0.0015)) * 3.5;
      tPos.setZ(i, h);
    }
    terrainGeo.computeVertexNormals();
    const terrain = new THREE.Mesh(
      terrainGeo,
      new THREE.MeshStandardMaterial({ color: 0x1a2f1a, roughness: 0.85, metalness: 0.05 })
    );
    terrain.rotation.x = -Math.PI / 2;
    terrain.position.y = -1.2;
    scene.add(terrain);

    const timeU = { value: 0 };
    const waterMat = createFloodWaterMaterial(timeU);
    const water = new THREE.Mesh(new THREE.PlaneGeometry(70, 70, 128, 128), waterMat);
    water.rotation.x = -Math.PI / 2;
    water.position.y = 0.15;
    scene.add(water);

    scene.add(new THREE.DirectionalLight(0xfff4e0, 1.5).translateX(18).translateY(32).translateZ(12));
    scene.add(new THREE.AmbientLight(0x2a3f55, 0.5));
    scene.add(new THREE.HemisphereLight(0x87b5e0, 0x1a2a1a, 0.35));

    let depthM = 0.5;
    let trackIdx = 0;
    camCtrl.play(BONEBANK_TRACKS[0]);

    // USGS poll
    const pollUsgs = async () => {
      try {
        const r = await fetchWabashNewHarmony();
        // rough stage→depth proxy for local scene (NAV D88 relative)
        depthM = Math.max(0, (r.stageFt - 15) * 0.15);
        const fos = simplifiedBishopFoS({
          cohesionKpa: 12,
          frictionDeg: 28,
          unitWeightKnM3: 18,
          slopeHeightM: 4.5,
          slopeAngleDeg: 32,
          waterHeightM: depthM,
        });
        setHud({
          stageFt: r.stageFt,
          depthM,
          dischargeCfs: r.dischargeCfs,
          fos,
          station: r.site,
          timestamp: r.timestamp,
          alert: fos < FEDERAL_FOS_THRESHOLD || depthM > 3,
        });
        const w = resolveWeather(depthM);
        scene.fog = new THREE.FogExp2(0x0a1628, w.fogDensity);
        waterMat.uniforms.uOpacity.value = w.waterOpacity;
        const g = gradeFromFloodDepth(depthM);
        renderer.toneMappingExposure = g.exposure;
      } catch {
        /* offline ok */
      }
    };
    pollUsgs();
    const usgsTimer = setInterval(pollUsgs, 15 * 60 * 1000);

    let last = performance.now();
    const animate = (now: number) => {
      const dt = Math.min(0.05, (now - last) / 1000);
      last = now;
      timeU.value += dt;
      camCtrl.update(dt);
      if (!camCtrl['active'] && BONEBANK_TRACKS.length) {
        trackIdx = (trackIdx + 1) % BONEBANK_TRACKS.length;
        camCtrl.play(BONEBANK_TRACKS[trackIdx]);
      }
      waterMat.uniforms.uCameraPos.value.copy(camera.position);
      renderer.render(scene, camera);
      requestAnimationFrame(animate);
    };
    requestAnimationFrame(animate);

    const onResize = () => {
      renderer.setSize(window.innerWidth, window.innerHeight);
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
    };
    window.addEventListener('resize', onResize);

    return () => {
      clearInterval(usgsTimer);
      window.removeEventListener('resize', onResize);
      map.remove();
      renderer.dispose();
    };
  }, []);

  return (
    <div style={{ position: 'fixed', inset: 0, background: '#0a1628' }}>
      <div ref={mapRef} style={{ width: '100%', height: '100%' }} />
      <canvas
        ref={threeRef}
        style={{
          position: 'absolute',
          inset: 0,
          pointerEvents: 'none',
          mixBlendMode: 'screen',
          opacity: 0.85,
        }}
      />
      <div
        style={{
          position: 'absolute',
          top: 14,
          left: 14,
          right: 14,
          background: 'rgba(8,16,28,0.9)',
          color: '#e0f2fe',
          padding: '11px 16px',
          borderRadius: 11,
          fontSize: 14,
          backdropFilter: 'blur(14px)',
          border: '1px solid rgba(56,189,248,0.22)',
          fontFamily: 'system-ui,Segoe UI,sans-serif',
        }}
      >
        PTDT Unified V33 — Virtual Tri-State River Valley · Cinematic CGI
      </div>
      <ForensicHUD {...hud} />
    </div>
  );
}
