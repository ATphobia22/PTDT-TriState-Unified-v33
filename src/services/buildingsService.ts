export interface GeoJSONFeature {
  type: "Feature";
  properties: Record<string, unknown> | null;
  geometry: { type: string; coordinates: unknown };
}

export interface GeoJSONFeatureCollection {
  type: "FeatureCollection";
  features: GeoJSONFeature[];
}

export type BBox = [number, number, number, number];

export const DEFAULT_BUILDING_HEIGHT_M = 6.5;
export const METERS_PER_FOOT = 0.3048;
export const METERS_PER_LEVEL = 3.2;

const EMPTY_FC: GeoJSONFeatureCollection = { type: "FeatureCollection", features: [] };
const BONEBANK_CENTER: [number, number] = [-88.02, 37.83];
const BONEBANK_BBOX: BBox = [-88.035, 37.82, -88.005, 37.84];

function isFinitePositive(value: unknown): value is number { return typeof value === "number" && Number.isFinite(value) && value > 0; }
function numericValue(value: unknown): number | undefined {
  if (isFinitePositive(value)) return value;
  if (typeof value === "string") { const n = Number.parseFloat(value.trim()); return Number.isFinite(n) && n > 0 ? n : undefined; }
  return undefined;
}

export function normalizeBuildingHeight(props: Record<string, unknown> | null): number {
  if (!props) return DEFAULT_BUILDING_HEIGHT_M;
  const explicit = [props.height, props.Height, props.building_height, props["building:height"], props.eaveheight, props.EaveHeight].map(numericValue).find((v): v is number => v !== undefined);
  if (explicit !== undefined) return explicit > 100 ? explicit * METERS_PER_FOOT : explicit;
  const levels = [props.levels, props["building:levels"], props.BuildingLevels, props.num_floors].map(numericValue).find((v): v is number => v !== undefined);
  return levels !== undefined ? levels * METERS_PER_LEVEL : DEFAULT_BUILDING_HEIGHT_M;
}

function featureIntersectsBBox(feature: GeoJSONFeature, bbox: BBox): boolean {
  const coordinates: number[][] = [];
  const walk = (value: unknown): void => {
    if (Array.isArray(value) && value.length >= 2 && typeof value[0] === "number" && typeof value[1] === "number") { coordinates.push(value as number[]); return; }
    if (Array.isArray(value)) value.forEach(walk);
  };
  walk(feature.geometry?.coordinates);
  if (!coordinates.length) return false;
  const xs = coordinates.map((c) => c[0]); const ys = coordinates.map((c) => c[1]);
  return !(Math.max(...xs) < bbox[0] || Math.min(...xs) > bbox[2] || Math.max(...ys) < bbox[1] || Math.min(...ys) > bbox[3]);
}

function enrich(features: GeoJSONFeature[]): GeoJSONFeatureCollection {
  return { type: "FeatureCollection", features: features.map((feature) => ({ ...feature, properties: { ...(feature.properties ?? {}), height_m: normalizeBuildingHeight(feature.properties) } })) };
}

export function getLocalBonebankBuildings(): GeoJSONFeatureCollection {
  const [lon, lat] = BONEBANK_CENTER; const d = 0.00035;
  return enrich([
    { type: "Feature", properties: { id: "bonebank-primary", name: "13101 Bonebank Rd Primary Structure", height_m: 7.2, levels: 1, source: "local-forensic" }, geometry: { type: "Polygon", coordinates: [[[lon - d * 1.2, lat - d * 0.8], [lon + d * 1.4, lat - d * 0.8], [lon + d * 1.4, lat + d * 0.9], [lon - d * 1.2, lat + d * 0.9], [lon - d * 1.2, lat - d * 0.8]]] } },
    { type: "Feature", properties: { id: "bonebank-outbuilding", name: "Accessory Structure", height_m: 4.5, levels: 1, source: "local-forensic" }, geometry: { type: "Polygon", coordinates: [[[lon + d * 1.8, lat - d * 0.4], [lon + d * 2.6, lat - d * 0.4], [lon + d * 2.6, lat + d * 0.3], [lon + d * 1.8, lat + d * 0.3], [lon + d * 1.8, lat - d * 0.4]]] } },
  ]);
}

async function fetchGeoJSON(url: string): Promise<GeoJSONFeatureCollection> {
  try { const response = await fetch(url); if (!response.ok) throw new Error(`HTTP ${response.status}`); const data = (await response.json()) as GeoJSONFeatureCollection; return data?.features ? data : EMPTY_FC; } catch { return EMPTY_FC; }
}

async function fetchMicrosoftClip(bbox: BBox): Promise<GeoJSONFeatureCollection> {
  const data = await fetchGeoJSON("/data/buildings/indiana_bonebank_clip.geojson");
  return enrich(data.features.filter((feature) => featureIntersectsBBox(feature, bbox)));
}

async function fetchOvertureBuildings(bbox: BBox): Promise<GeoJSONFeatureCollection> {
  const params = new URLSearchParams({ xmin: String(bbox[0]), ymin: String(bbox[1]), xmax: String(bbox[2]), ymax: String(bbox[3]) });
  const data = await fetchGeoJSON(`/api/gis/buildings/overture?${params}`);
  return enrich(data.features);
}

export async function fetchBuildings(bbox: BBox = BONEBANK_BBOX): Promise<GeoJSONFeatureCollection> {
  const local = getLocalBonebankBuildings();
  const localInBbox = local.features.filter((feature) => featureIntersectsBBox(feature, bbox));
  if (localInBbox.length) return enrich(localInBbox);
  const microsoft = await fetchMicrosoftClip(bbox);
  if (microsoft.features.length) return microsoft;
  const overture = await fetchOvertureBuildings(bbox);
  if (overture.features.length) return overture;
  return EMPTY_FC;
}

export function fetchBonebankBuildings(): Promise<GeoJSONFeatureCollection> { return fetchBuildings(BONEBANK_BBOX); }
