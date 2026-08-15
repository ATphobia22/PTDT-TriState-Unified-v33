/**
 * IndianaMap FeatureServer parcel queries with pagination.
 * maxRecordCount on Hosted services is typically 2000.
 */
import type { Map as MaplibreMap, GeoJSONSource } from "maplibre-gl";

export const INDIANA_PARCELS_2025 =
  "https://gisdata.in.gov/server/rest/services/Hosted/Parcel_Boundaries_of_Indiana_2025/FeatureServer/0";

export const INDIANA_PARCELS_CURRENT =
  "https://gisdata.in.gov/server/rest/services/Hosted/Parcel_Boundaries_of_Indiana_Current/FeatureServer/0";

export const FEATURESERVER_PAGE_SIZE = 2000;
export const FEATURESERVER_MAX_PAGES = 25;

export type Bbox4326 = {
  xmin: number;
  ymin: number;
  xmax: number;
  ymax: number;
};

export const BONEBANK_BBOX: Bbox4326 = {
  xmin: -88.02,
  ymin: 37.89,
  xmax: -87.98,
  ymax: 37.92,
};

export const PARCEL_SOURCE_ID = "indiana-parcels-geojson";
export const PARCEL_FILL_LAYER = "indiana-parcels-fill";
export const PARCEL_LINE_LAYER = "indiana-parcels-outline";

async function queryPage(
  layerUrl: string,
  bbox: Bbox4326,
  offset: number,
  pageSize: number,
  where: string,
): Promise<{ features: GeoJSON.Feature[]; exceeded: boolean }> {
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
    resultOffset: String(offset),
    resultRecordCount: String(pageSize),
    orderByFields: "OBJECTID ASC",
  });

  const url = `${layerUrl}/query?${params.toString()}`;
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`IndianaMap parcel query HTTP ${res.status} offset=${offset}`);
  }
  const body = (await res.json()) as {
    type?: string;
    features?: GeoJSON.Feature[];
    exceededTransferLimit?: boolean;
    error?: { message?: string };
  };
  if (body.error?.message) {
    throw new Error(`IndianaMap error: ${body.error.message}`);
  }
  const features = body.features ?? [];
  const exceeded =
    body.exceededTransferLimit === true || features.length >= pageSize;
  return { features, exceeded };
}

export async function queryIndianaParcelsGeoJson(
  bbox: Bbox4326 = BONEBANK_BBOX,
  layerUrl: string = INDIANA_PARCELS_2025,
  where = "1=1",
): Promise<GeoJSON.FeatureCollection> {
  const all: GeoJSON.Feature[] = [];
  let offset = 0;

  for (let page = 0; page < FEATURESERVER_MAX_PAGES; page++) {
    const { features, exceeded } = await queryPage(
      layerUrl,
      bbox,
      offset,
      FEATURESERVER_PAGE_SIZE,
      where,
    );
    all.push(...features);
    if (!exceeded || features.length === 0) break;
    offset += features.length;
  }

  return { type: "FeatureCollection", features: all };
}

/** Attach paginated IndianaMap parcels to a MapLibre map instance. */
export async function loadIndianaParcelsIntoMap(
  map: MaplibreMap,
  bbox: Bbox4326 = BONEBANK_BBOX,
): Promise<number> {
  const fc = await queryIndianaParcelsGeoJson(bbox);
  const existing = map.getSource(PARCEL_SOURCE_ID) as GeoJSONSource | undefined;
  if (existing && typeof existing.setData === "function") {
    existing.setData(fc);
  } else if (!map.getSource(PARCEL_SOURCE_ID)) {
    map.addSource(PARCEL_SOURCE_ID, { type: "geojson", data: fc });
  }
  if (!map.getLayer(PARCEL_FILL_LAYER)) {
    map.addLayer({
      id: PARCEL_FILL_LAYER,
      type: "fill",
      source: PARCEL_SOURCE_ID,
      paint: { "fill-color": "#00ff66", "fill-opacity": 0.08 },
    });
  }
  if (!map.getLayer(PARCEL_LINE_LAYER)) {
    map.addLayer({
      id: PARCEL_LINE_LAYER,
      type: "line",
      source: PARCEL_SOURCE_ID,
      paint: { "line-color": "#00ff66", "line-width": 1 },
    });
  }
  return fc.features.length;
}
