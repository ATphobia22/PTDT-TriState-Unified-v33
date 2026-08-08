import maplibregl from 'maplibre-gl';

export const INDIANA_VECTOR_STYLE_BASE = {
  version: 8 as const,
  name: 'PTDT-Vector-Base',
  sources: {
    openmaptiles: {
      type: 'vector' as const,
      url: 'https://api.maptiler.com/tiles/v3/tiles.json?key=get_your_own_key',
    },
  },
  layers: [] as maplibregl.LayerSpecification[],
};

export function addVectorFillLayer(
  map: maplibregl.Map,
  sourceId: string,
  sourceLayer: string,
  layerId: string,
  paint: maplibregl.FillPaint
): void {
  if (map.getLayer(layerId)) return;
  map.addLayer({
    id: layerId,
    type: 'fill',
    source: sourceId,
    'source-layer': sourceLayer,
    paint,
  });
}

export function addVectorLineLayer(
  map: maplibregl.Map,
  sourceId: string,
  sourceLayer: string,
  layerId: string,
  paint: maplibregl.LinePaint
): void {
  if (map.getLayer(layerId)) return;
  map.addLayer({
    id: layerId,
    type: 'line',
    source: sourceId,
    'source-layer': sourceLayer,
    paint,
  });
}

export function addPMTilesVectorSource(
  map: maplibregl.Map,
  sourceId: string,
  pmtilesUrl: string
): void {
  if (map.getSource(sourceId)) return;
  map.addSource(sourceId, {
    type: 'vector',
    url: `pmtiles://${pmtilesUrl}`,
  });
}

export function addFloodZoneVectorLayer(map: maplibregl.Map, sourceId = 'flood-zones'): void {
  addVectorFillLayer(map, sourceId, 'flood', 'flood-fill', {
    'fill-color': [
      'interpolate',
      ['linear'],
      ['get', 'depth_m'],
      0, '#38bdf8',
      1, '#0ea5e9',
      2, '#1e40af',
      3, '#0f172a',
    ],
    'fill-opacity': 0.55,
  });
  addVectorLineLayer(map, sourceId, 'flood', 'flood-outline', {
    'line-color': '#7dd3fc',
    'line-width': 1.2,
    'line-opacity': 0.8,
  });
}
