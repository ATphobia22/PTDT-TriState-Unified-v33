/**
 * Indiana DNR Best Available Flood Hazard Layer (BAFL) query helper.
 * Verified MapServer:
 *   https://gisdata.in.gov/server/rest/services/Best_Available_Flood_Hazard_Layer/MapServer
 * Soft-fail; does not replace sealed FARA / HEC-RAS / survey for LOMA.
 */

export const BAFL_MAPSERVER =
  "https://gisdata.in.gov/server/rest/services/Best_Available_Flood_Hazard_Layer/MapServer";

/** Layer ids vary; discover via .../MapServer?f=pjson. Common: FloodHazard_BestAvai_DNR_Water */
export async function queryBaflAtPoint(
  lon: number,
  lat: number,
  layerIds = "all",
): Promise<{ status: "OK" | "SOFT_FAIL"; reason?: string; results: unknown[]; url: string }> {
  const pad = 0.005;
  const extent = [lon - pad, lat - pad, lon + pad, lat + pad].join(",");
  const params = new URLSearchParams({
    f: "json",
    geometry: JSON.stringify({ x: lon, y: lat, spatialReference: { wkid: 4326 } }),
    geometryType: "esriGeometryPoint",
    sr: "4326",
    layers: layerIds,
    tolerance: "5",
    mapExtent: extent,
    imageDisplay: "800,600,96",
    returnGeometry: "false",
  });
  const url = `${BAFL_MAPSERVER}/identify?${params.toString()}`;
  try {
    const res = await fetch(url);
    if (!res.ok) {
      return { status: "SOFT_FAIL", reason: `HTTP ${res.status}`, results: [], url };
    }
    const body = (await res.json()) as { results?: unknown[] };
    return { status: "OK", results: body.results ?? [], url };
  } catch (e) {
    return {
      status: "SOFT_FAIL",
      reason: e instanceof Error ? e.message : "BAFL identify failed",
      results: [],
      url,
    };
  }
}
