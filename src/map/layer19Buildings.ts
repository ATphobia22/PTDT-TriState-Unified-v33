import type maplibregl from "maplibre-gl";
import type { GeoJSONFeatureCollection } from "../services/buildingsService";

export const LAYER19_SOURCE = "layer19-buildings";
export const LAYER19_EXTRUSION = "layer19-buildings-extrusion";
export const LAYER19_OUTLINE = "layer19-buildings-outline";

export interface Layer19Controller {
  setVisible(visible: boolean): void;
  setOpacity(opacity: number): void;
  setHeightScale(scale: number): void;
  remove(): void;
}

function visibility(visible: boolean): "visible" | "none" {
  return visible ? "visible" : "none";
}

export function addLayer19Buildings(map: maplibregl.Map, buildings: GeoJSONFeatureCollection): Layer19Controller {
  if (map.getLayer(LAYER19_EXTRUSION)) map.removeLayer(LAYER19_EXTRUSION);
  if (map.getLayer(LAYER19_OUTLINE)) map.removeLayer(LAYER19_OUTLINE);
  if (map.getSource(LAYER19_SOURCE)) map.removeSource(LAYER19_SOURCE);

  map.addSource(LAYER19_SOURCE, { type: "geojson", data: buildings as any });
  map.addLayer({
    id: LAYER19_EXTRUSION,
    type: "fill-extrusion",
    source: LAYER19_SOURCE,
    minzoom: 13,
    paint: {
      "fill-extrusion-color": ["case", ["==", ["get", "id"], "bonebank-primary"], "#2563eb", "#94a3b8"],
      "fill-extrusion-height": ["*", ["coalesce", ["get", "height_m"], 6.5], 1],
      "fill-extrusion-base": 0,
      "fill-extrusion-opacity": 0.85,
    },
  });
  map.addLayer({ id: LAYER19_OUTLINE, type: "line", source: LAYER19_SOURCE, minzoom: 13, paint: { "line-color": "#cbd5e1", "line-width": 1.2, "line-opacity": 0.9 } });

  return {
    setVisible(visible) {
      map.setLayoutProperty(LAYER19_EXTRUSION, "visibility", visibility(visible));
      map.setLayoutProperty(LAYER19_OUTLINE, "visibility", visibility(visible));
    },
    setOpacity(opacity) {
      map.setPaintProperty(LAYER19_EXTRUSION, "fill-extrusion-opacity", Math.min(1, Math.max(0, opacity)));
    },
    setHeightScale(scale) {
      map.setPaintProperty(LAYER19_EXTRUSION, "fill-extrusion-height", ["*", ["coalesce", ["get", "height_m"], 6.5], Math.max(0, scale)]);
    },
    remove() {
      if (map.getLayer(LAYER19_OUTLINE)) map.removeLayer(LAYER19_OUTLINE);
      if (map.getLayer(LAYER19_EXTRUSION)) map.removeLayer(LAYER19_EXTRUSION);
      if (map.getSource(LAYER19_SOURCE)) map.removeSource(LAYER19_SOURCE);
    },
  };
}
