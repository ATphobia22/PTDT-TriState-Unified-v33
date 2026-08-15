/**
 * Engage Posey parcel client.
 * Prefer /api/proxy/xsoft/posey/parcel (server HTML parse).
 * Direct getparcellist is NOT a public JSON API.
 */

import { SOVEREIGN, normalizeParcelId } from "../config/sovereignConstants";

export type EngageParcelSoftFail = {
  status: "OK" | "SOFT_FAIL";
  parcelId?: string;
  reason?: string;
  detailUrl?: string;
  rawSnippet?: string;
};

export function engageDetailUrl(parcelId: string): string {
  const id = encodeURIComponent(parcelId.trim());
  return `${SOVEREIGN.ENGAGE_PARCEL_DETAIL}?parcelId=${id}`;
}

/**
 * Browser-side: call same-origin proxy only (CORS + HTML parse on server).
 */
export async function fetchParcelViaProxy(
  parcelId: string,
  proxyBase = "/api/proxy/xsoft/posey/parcel",
): Promise<EngageParcelSoftFail> {
  const digits = normalizeParcelId(parcelId);
  if (digits.length < 10 || !digits.startsWith("65")) {
    return {
      status: "SOFT_FAIL",
      reason: "Parcel ID must be Posey (65) and 50 IAC-shaped",
    };
  }
  try {
    const url = `${proxyBase}?parcelId=${encodeURIComponent(parcelId.trim())}`;
    const res = await fetch(url, { credentials: "same-origin" });
    if (!res.ok) {
      return {
        status: "SOFT_FAIL",
        parcelId: parcelId.trim(),
        reason: `Proxy HTTP ${res.status}`,
        detailUrl: engageDetailUrl(parcelId),
      };
    }
    const data = (await res.json()) as EngageParcelSoftFail;
    return data;
  } catch (e) {
    return {
      status: "SOFT_FAIL",
      parcelId: parcelId.trim(),
      reason: e instanceof Error ? e.message : "proxy fetch failed",
      detailUrl: engageDetailUrl(parcelId),
    };
  }
}
