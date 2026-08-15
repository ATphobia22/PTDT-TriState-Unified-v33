/**
 * FEMA NFHL MapServer identify (presentation + insurance context).
 * Source: https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer
 * Regulatory LOMA still requires sealed survey + FARA path — not this overlay alone.
 */

export interface NfhlIdentifyResult {
  status: "OK" | "SOFT_FAIL";
  reason?: string;
  results: unknown[];
  requestUrl: string;
}

const NFHL =
  "https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer/identify";

/** lon/lat WGS84; mapExtent is minx,miny,maxx,maxy around the pin */
export async function identifyNfhlAtPoint(
  lon: number,
  lat: number,
  mapExtent?: [number, number, number, number],
): Promise<NfhlIdentifyResult> {
  const pad = 0.01;
  const extent =
    mapExtent ??
    ([lon - pad, lat - pad, lon + pad, lat + pad] as [
      number,
      number,
      number,
      number,
    ]);

  const params = new URLSearchParams({
    f: "json",
    geometry: JSON.stringify({ x: lon, y: lat, spatialReference: { wkid: 4326 } }),
    geometryType: "esriGeometryPoint",
    sr: "4326",
    layers: "all",
    tolerance: "3",
    mapExtent: extent.join(","),
    imageDisplay: "800,600,96",
    returnGeometry: "false",
  });

  const requestUrl = `${NFHL}?${params.toString()}`;

  try {
    const res = await fetch(requestUrl);
    if (!res.ok) {
      return {
        status: "SOFT_FAIL",
        reason: `HTTP ${res.status}`,
        results: [],
        requestUrl,
      };
    }
    const body = (await res.json()) as { results?: unknown[] };
    return {
      status: "OK",
      results: body.results ?? [],
      requestUrl,
    };
  } catch (e) {
    return {
      status: "SOFT_FAIL",
      reason: e instanceof Error ? e.message : "identify failed",
      results: [],
      requestUrl,
    };
  }
}
