import type { StyleSpecification } from 'maplibre-gl';
import type maplibregl from 'maplibre-gl';

export const triCountyStyle: StyleSpecification = {
  version: 8,
  name: 'PTDT Tri-County Photoreal Base',
  metadata: { 'ptdt:bfe_ft': 375.0, 'ptdt:datum': 'NAVD88', 'ptdt:site': '13101 Bonebank Road, Point Township, IN', 'ptdt:layer19': 'buildings-structural-context' },
  center: [-88.0051, 37.8459], zoom: 11.5, pitch: 62, bearing: 28,
  sources: {
    carto: { type: 'raster', tiles: ['https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}@2x.png', 'https://b.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}@2x.png', 'https://c.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}@2x.png'], tileSize: 256, attribution: '© CARTO © OpenStreetMap' },
    'terrain-dem': { type: 'raster-dem', tiles: ['https://elevation.gio.in.gov/tiles/{z}/{x}/{y}.png'], tileSize: 256, maxzoom: 15, encoding: 'mapbox' },
    'local-vector': { type: 'vector', url: 'pmtiles:///data/tri-county.pmtiles' },
  },
  layers: [
    { id: 'background', type: 'background', paint: { 'background-color': '#0a1628' } },
    { id: 'carto-base', type: 'raster', source: 'carto', paint: { 'raster-opacity': 0.92, 'raster-brightness-min': 0.05, 'raster-saturation': -0.15 } },
    { id: 'hillshade', type: 'hillshade', source: 'terrain-dem', paint: { 'hillshade-exaggeration': 0.55, 'hillshade-shadow-color': '#020617', 'hillshade-highlight-color': '#e0f2fe', 'hillshade-accent-color': '#0ea5e9' } },
    { id: 'flood-depth-fill', type: 'fill', source: 'local-vector', 'source-layer': 'flood', paint: { 'fill-color': ['interpolate', ['linear'], ['coalesce', ['get', 'depth_m'], 0], 0, 'rgba(56,189,248,0.15)', 0.5, 'rgba(14,165,233,0.35)', 1.5, 'rgba(30,64,175,0.55)', 3.0, 'rgba(15,23,42,0.75)'], 'fill-opacity': 0.7 } },
    { id: 'flood-depth-outline', type: 'line', source: 'local-vector', 'source-layer': 'flood', paint: { 'line-color': '#7dd3fc', 'line-width': 1.0, 'line-opacity': 0.65 } },
    { id: 'hydro-line', type: 'line', source: 'local-vector', 'source-layer': 'waterway', paint: { 'line-color': '#38bdf8', 'line-width': ['interpolate', ['linear'], ['zoom'], 10, 0.8, 14, 2.4], 'line-opacity': 0.85 } },
    { id: 'parcels-fill', type: 'fill', source: 'local-vector', 'source-layer': 'parcels', paint: { 'fill-color': 'rgba(148,163,184,0.08)', 'fill-outline-color': 'rgba(148,163,184,0.35)' } },
    { id: 'bafm-outline', type: 'line', source: 'local-vector', 'source-layer': 'bafm', paint: { 'line-color': '#f59e0b', 'line-width': 1.5, 'line-dasharray': [2, 1], 'line-opacity': 0.8 } },
  ],
};

export function applyTriCountyStyle(map: maplibregl.Map): void {
  map.setStyle(triCountyStyle as maplibregl.StyleSpecification);
  (map as any).setFog?.({ color: 'rgb(8, 18, 32)', 'high-color': 'rgb(18, 36, 62)', 'horizon-blend': 0.16, 'space-color': 'rgb(3, 6, 14)', 'star-intensity': 0.5 });
}
