import React, { useEffect, useRef } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { depthColorExpression } from './map/maplibreCustomFilters';

export default function App() {
  const mapRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!mapRef.current) return;
    const map = new maplibregl.Map({
      container: mapRef.current,
      style: 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
      center: [-88.0051, 37.8459],
      zoom: 13.5,
      pitch: 55,
      bearing: 30
    });
    map.addControl(new maplibregl.NavigationControl(), 'top-right');
    return () => map.remove();
  }, []);

  return (
    <div style={{ position: 'fixed', inset: 0 }}>
      <div ref={mapRef} style={{ width: '100%', height: '100%' }} />
      <div style={{
        position: 'absolute', top: 12, left: 12, right: 12,
        background: 'rgba(10,22,40,0.85)', color: '#e0f2fe',
        padding: '10px 14px', borderRadius: 10, fontSize: 14,
        backdropFilter: 'blur(8px)'
      }}>
        PTDT Unified V33 — Point Township Flood Twin
      </div>
    </div>
  );
}
