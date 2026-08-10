import maplibregl from 'maplibre-gl';

type FillPaint = Extract<maplibregl.LayerSpecification, { type: 'fill' }>['paint'];
type LinePaint = Extract<maplibregl.LayerSpecification, { type: 'line' }>['paint'];

export const INDIANA_VECTOR_STYLE_BASE = {
  version: 8 as const,
  name: 'PTDT-Vector-Base',
  sources: {
    localVector: {
      type: 'vector' as const,
      url: 'pmtiles:///data/tri-county.pmtiles',
    },
  },
  layers: [] as maplibregl.LayerSpecification[],
};

export function addVectorFillLayer(map: maplibregl.Map, sourceId: string, sourceLayer: string, layerId: string, paint: FillPaint): void {
  if (map.getLayer(layerId)) return;
  map.addLayer({ id: layerId, type: 'fill', source: sourceId, 'source-layer': sourceLayer, paint });
}

export function addVectorLineLayer(map: maplibregl.Map, sourceId: string, sourceLayer: string, layerId: string, paint: LinePaint): void {
  if (map.getLayer(layerId)) return;
  map.addLayer({ id: layerId, type: 'line', source: sourceId, 'source-layer': sourceLayer, paint });
}

export function addPMTilesVectorSource(map: maplibregl.Map, sourceId: string, pmtilesUrl: string): void {
  if (map.getSource(sourceId)) return;
  map.addSource(sourceId, { type: 'vector', url: `pmtiles://${pmtilesUrl}` });
}

export function addFloodZoneVectorLayer(map: maplibregl.Map, sourceId = 'flood-zones'): void {
  addVectorFillLayer(map, sourceId, 'flood', 'flood-fill', {
    'fill-color': ['interpolate', ['linear'], ['get', 'depth_m'], 0, '#38bdf8', 1, '#0ea5e9', 2, '#1e40af', 3, '#0f172a'],
    'fill-opacity': 0.55,
  });
  addVectorLineLayer(map, sourceId, 'flood', 'flood-outline', {
    'line-color': '#7dd3fc',
    'line-width': 1.2,
    'line-opacity': 0.8,
  });
}
