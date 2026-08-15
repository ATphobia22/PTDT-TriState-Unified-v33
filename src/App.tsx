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
import { fetchBonebankBuildings } from './services/buildingsService';
import { addLayer19Buildings, type Layer19Controller } from './map/layer19Buildings';
import { simplifiedBishopFoS, FEDERAL_FOS_THRESHOLD } from './services/bishopFoS';
import { wireIndianaParcels } from './map/loadParcelsOnStyle';
import { ParcelPopup } from './components/ParcelPopup';
import {
  registerPmtilesProtocol,
  unregisterPmtilesProtocol,
  tryAddPoseyParcelsPmtiles,
  PMTILES_PARCEL_LAYER,
} from './map/pmtilesProtocol';

export default function App() {
  const mapRef = useRef<HTMLDivElement>(null);
  const threeRef = useRef<HTMLCanvasElement>(null);
  const mapInstanceRef = useRef<maplibregl.Map | null>(null);
  const layer19Ref = useRef<Layer19Controller | null>(null);
  const [layer19, setLayer19] = useState({ visible: true, opacity: 0.85, heightScale: 1 });
  const [selectedParcelId, setSelectedParcelId] = useState<string | null>(null);
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

    registerPmtilesProtocol();

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
    mapInstanceRef.current = map;
    map.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), 'top-right');

    map.on('style.load', async () => {
      (map as any).setFog?.({
        color: 'rgb(8, 18, 32)',
        'high-color': 'rgb(18, 36, 62)',
        'horizon-blend': 0.18,
        'space-color': 'rgb(3, 6, 14)',
        'star-intensity': 0.55,
      });

      // Offline PMTiles first; FeatureServer GeoJSON fallback
      const pmOk = tryAddPoseyParcelsPmtiles(map);
      if (!pmOk) {
        await wireIndianaParcels(map);
      } else {
        map.on('click', PMTILES_PARCEL_LAYER, (e) => {
          const f = e.features?.[0];
          const id =
            f?.properties?.parcel_id ??
            f?.properties?.PARCEL_ID ??
            f?.properties?.parcelid ??
            f?.properties?.PROP_ID;
          if (id != null) setSelectedParcelId(String(id));
        });
      }

      map.on('ptdt:parcelclick' as any, (e: any) => {
        if (e?.parcelId) setSelectedParcelId(String(e.parcelId));
      });

      try {
        const buildings = await fetchBonebankBuildings();
        const controller = addLayer19Buildings(map, buildings);
        controller.setVisible(layer19.visible);
        controller.setOpacity(layer19.opacity);
        controller.setHeightScale(layer19.heightScale);
        layer19Ref.current = controller;
        if (layer19.visible) map.easeTo({ pitch: 55, bearing: -20, duration: 900 });
      } catch {
        /* Layer 19 optional */
      }
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
    const camera = new THREE.PerspectiveCamera(
      42,
      window.innerWidth / window.innerHeight,
      0.1,
      2000,
    );
    camera.position.set(0, 12, 28);
    const camCtrl = new CinematicCameraController(camera);

    const terrainGeo = new THREE.PlaneGeometry(80, 80, 96, 96);
    const tPos = terrainGeo.attributes.position;
    for (let i = 0; i < tPos.count; i++) {
      const x = tPos.getX(i);
      const y = tPos.getY(i);
      tPos.setZ(
        i,
        Math.sin(x * 0.08) * 1.8 +
          Math.cos(y * 0.07) * 1.4 +
          Math.sin((x + y) * 0.05) * 0.9 -
          Math.exp(-(x * x + y * y) * 0.0015) * 3.5,
      );
    }
    terrainGeo.computeVertexNormals();
    const terrain = new THREE.Mesh(
      terrainGeo,
      new THREE.MeshStandardMaterial({ color: 0x1a2f1a, roughness: 0.85, metalness: 0.05 }),
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
    const pollUsgs = async () => {
      try {
        const r = await fetchWabashNewHarmony();
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
        renderer.toneMappingExposure = gradeFromFloodDepth(depthM).exposure;
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
      if (!(camCtrl as any).active && BONEBANK_TRACKS.length) {
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
      layer19Ref.current?.remove();
      layer19Ref.current = null;
      mapInstanceRef.current = null;
      map.remove();
      renderer.dispose();
      unregisterPmtilesProtocol();
    };
  }, []);

  const updateLayer19 = (next: Partial<typeof layer19>) => {
    const merged = { ...layer19, ...next };
    setLayer19(merged);
    if (next.visible !== undefined) {
      layer19Ref.current?.setVisible(next.visible);
      if (next.visible) mapInstanceRef.current?.easeTo({ pitch: 55, bearing: -20, duration: 900 });
    }
    if (next.opacity !== undefined) layer19Ref.current?.setOpacity(next.opacity);
    if (next.heightScale !== undefined) layer19Ref.current?.setHeightScale(next.heightScale);
  };

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
      <div
        style={{
          position: 'absolute',
          right: 14,
          top: 64,
          width: 250,
          background: 'rgba(8,16,28,0.92)',
          color: '#e0f2fe',
          padding: 14,
          borderRadius: 11,
          border: '1px solid rgba(56,189,248,0.22)',
          fontFamily: 'system-ui,Segoe UI,sans-serif',
          fontSize: 12,
        }}
      >
        <div style={{ fontWeight: 700, marginBottom: 8 }}>Layer 19 · Buildings / Structural Context</div>
        <label style={{ display: 'flex', gap: 8, alignItems: 'center', marginBottom: 8 }}>
          <input
            type="checkbox"
            checked={layer19.visible}
            onChange={(e) => updateLayer19({ visible: e.target.checked })}
          />
          3D building extrusion
        </label>
        <label style={{ display: 'block', marginBottom: 8 }}>
          Opacity {layer19.opacity.toFixed(2)}
          <input
            style={{ width: '100%' }}
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={layer19.opacity}
            onChange={(e) => updateLayer19({ opacity: Number(e.target.value) })}
          />
        </label>
        <label style={{ display: 'block' }}>
          Height scale {layer19.heightScale.toFixed(1)}×
          <input
            style={{ width: '100%' }}
            type="range"
            min="0.25"
            max="3"
            step="0.05"
            value={layer19.heightScale}
            onChange={(e) => updateLayer19({ heightScale: Number(e.target.value) })}
          />
        </label>
        <div style={{ marginTop: 10, opacity: 0.8 }}>
          Evidence Graph is the engineering source; rendered geometry is read-only.
        </div>
      </div>
      {selectedParcelId && (
        <div style={{ position: 'absolute', left: 14, bottom: 14, zIndex: 20 }}>
          <ParcelPopup
            parcelId={selectedParcelId}
            apiBase="http://127.0.0.1:8000"
            onClose={() => setSelectedParcelId(null)}
          />
        </div>
      )}
      <ForensicHUD {...hud} />
    </div>
  );
}
