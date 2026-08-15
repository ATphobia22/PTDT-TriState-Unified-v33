/**
 * MapLibre BAFL fill layer — paint by fld_zone × source_dnr × zone_subty
 * Matches IDNR INFIP symbology categories (presentation only).
 * Engineering authority: sealed GeoJSON from DnrRegulatoryBridge (EPSG:2966 → 4326).
 */
import type { Map as MapLibreMap, ExpressionSpecification } from "maplibre-gl";

export const BAFL_SOURCE = "ptdt-bafl";
export const BAFL_FILL_LAYER = "ptdt-bafl-fill";
export const BAFL_LINE_LAYER = "ptdt-bafl-line";

/** Unique-values style approximating INFIP table (colors illustrative). */
export const BAFL_FILL_COLOR: ExpressionSpecification = [
  "case",
  [
    "all",
    ["==", ["get", "fld_zone"], "AE"],
    ["==", ["get", "source_dnr"], "NFHL"],
    ["==", ["get", "zone_subty"], "FLOODWAY"],
  ],
  "#c026d3",
  [
    "all",
    ["==", ["get", "fld_zone"], "AE"],
    ["==", ["get", "source_dnr"], "IDNR_MR"],
    ["==", ["get", "zone_subty"], "DNR APPROVED FLOODWAY"],
  ],
  "#7e22ce",
  [
    "all",
    ["==", ["get", "fld_zone"], "A"],
    ["==", ["get", "source_dnr"], "IDNR_ZONEA"],
    ["==", ["get", "zone_subty"], "APPROXIMATE FLOODWAY"],
  ],
  "#a855f7",
  [
    "all",
    ["==", ["get", "fld_zone"], "AE"],
    ["==", ["get", "source_dnr"], "IDNR_MR"],
    ["==", ["get", "zone_subty"], "DNR APPROVED STUDY"],
  ],
  "#facc15",
  ["==", ["get", "fld_zone"], "AE"],
  "#38bdf8",
  ["==", ["get", "fld_zone"], "A"],
  "#67e8f9",
  [
    "all",
    ["==", ["get", "fld_zone"], "X"],
    ["in", ["get", "zone_subty"], ["literal", [
      "0.2 PCT ANNUAL CHANCE FLOOD HAZARD",
      "0.2 PCT ANNUAL CHANCE FLOOD HAZARD CONTAINED IN CHANNEL",
    ]]],
  ],
  "#fda4af",
  "#94a3b8",
];

export function addBaflGeoJson(
  map: MapLibreMap,
  geojson: GeoJSON.FeatureCollection,
): void {
  if (map.getSource(BAFL_SOURCE)) {
    (map.getSource(BAFL_SOURCE) as maplibregl.GeoJSONSource).setData(geojson);
    return;
  }
  map.addSource(BAFL_SOURCE, { type: "geojson", data: geojson });
  map.addLayer({
    id: BAFL_FILL_LAYER,
    type: "fill",
    source: BAFL_SOURCE,
    paint: {
      "fill-color": BAFL_FILL_COLOR,
      "fill-opacity": 0.35,
    },
  });
  map.addLayer({
    id: BAFL_LINE_LAYER,
    type: "line",
    source: BAFL_SOURCE,
    paint: {
      "line-color": "#e0e7ff",
      "line-width": 0.8,
      "line-opacity": 0.6,
    },
  });
}

// maplibregl type for setData
import type maplibregl from "maplibre-gl";
