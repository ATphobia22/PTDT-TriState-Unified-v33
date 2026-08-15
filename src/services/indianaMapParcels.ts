/**
 * IndianaMap / IGIO parcel FeatureServer helpers (not native MVT).
 *
 * Verified endpoints:
 * - 2025: https://gisdata.in.gov/server/rest/services/Hosted/Parcel_Boundaries_of_Indiana_2025/FeatureServer/0
 * - Current: https://gisdata.in.gov/server/rest/services/Hosted/Parcel_Boundaries_of_Indiana_Current/FeatureServer/0
 *
 * IndianaMap primarily exposes ArcGIS FeatureServer/MapServer + API Explorer filters.
 * For MapLibre MVT at runtime: query GeoJSON bbox → local tippecanoe/PMTiles, or proxy.
 * Do not treat cadastre as survey-grade for LOMA.
 */

export const INDIANA_PARCELS_2025 =
  "https://gisdata.in.gov/server/rest/services/Hosted/Parcel_Boundaries_of_Indiana_2025/FeatureServer/0";

export const INDIANA_PARCELS_CURRENT =
  "https://gisdata.in.gov/server/rest/services/Hosted/Parcel_Boundaries_of_Indiana_Current/FeatureServer/0";

export type Bbox4326 = {
  xmin: number;
  ymin: number;
  xmax: number;
  ymax: number;
};

/** Bonebank / Point Township approximate pin envelope */
export const BONEBANK_BBOX: Bbox4326 = {
  xmin: -88.02,
  ymin: 37.89,
  xmax: -87.98,
  ymax: 37.92,
};

export async function queryIndianaParcelsGeoJson(
  bbox: Bbox4326 = BONEBANK_BBOX,
  layerUrl: string = INDIANA_PARCELS_2025,
  where = "1=1",
): Promise<GeoJSON.FeatureCollection> {
  const geometry = {
    xmin: bbox.xmin,
    ymin: bbox.ymin,
    xmax: bbox.xmax,
    ymax: bbox.ymax,
    spatialReference: { wkid: 4326 },
  };

  const params = new URLSearchParams({
    f: "geojson",
    where,
    geometry: JSON.stringify(geometry),
    geometryType: "esriGeometryEnvelope",
    inSR: "4326",
    spatialRel: "esriSpatialRelIntersects",
    outFields: "*",
    returnGeometry: "true",
    resultRecordCount: "2000",
  });

  const url = `${layerUrl}/query?${params.toString()}`;
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`IndianaMap parcel query HTTP ${res.status}`);
  }
  return (await res.json()) as GeoJSON.FeatureCollection;
}

/** MapLibre source/layer id constants for GeoJSON fallback */
export const PARCEL_SOURCE_ID = "indiana-parcels-geojson";
export const PARCEL_FILL_LAYER = "indiana-parcels-fill";
export const PARCEL_LINE_LAYER = "indiana-parcels-outline";

export function parcelLayerStyle() {
  return {
    fill: {
      id: PARCEL_FILL_LAYER,
      type: "fill" as const,
      source: PARCEL_SOURCE_ID,
      paint: {
        "fill-color": "#00ff66",
        "fill-opacity": 0.08,
      },
    },
    line: {
      id: PARCEL_LINE_LAYER,
      type: "line" as const,
      source: PARCEL_SOURCE_ID,
      paint: {
        "line-color": "#00ff66",
        "line-width": 1,
      },
    },
  };
}
