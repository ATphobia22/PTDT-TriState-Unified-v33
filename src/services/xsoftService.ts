/**
 * Posey County XSoft Engage parcel detail client.
 *
 * Verified pattern (HTML detail page, not a public JSON API):
 *   https://engage.xsoftinc.com/posey/map/getparceldetail?parcelId=65-06-07-140-009.000-005
 *
 * Browser calls may fail on CORS. Prefer server-side proxy or operator paste.
 * Soft-fail: never invent assessment values.
 */

export interface XSoftParcelDetail {
  parcelId: string;
  sourceUrl: string;
  contentType: string;
  /** True when response body looks like Engage HTML detail page */
  htmlDocument: boolean;
  /** Raw text for operator/server parse — not regulatory authority */
  rawPreview: string;
  status: "OK" | "SOFT_FAIL";
  reason?: string;
}

const POSEY_DETAIL =
  "https://engage.xsoftinc.com/posey/map/getparceldetail";

export function buildPoseyParcelDetailUrl(parcelId: string): string {
  const id = parcelId.trim();
  return `${POSEY_DETAIL}?parcelId=${encodeURIComponent(id)}`;
}

/**
 * Attempt fetch. On CORS/network failure returns SOFT_FAIL with URL for manual open.
 * Does not claim structured JSON fields unless content-type is JSON.
 */
export async function fetchXSoftParcelData(
  parcelId: string,
  init?: RequestInit,
): Promise<XSoftParcelDetail> {
  const sanitizedId = parcelId.trim();
  const sourceUrl = buildPoseyParcelDetailUrl(sanitizedId);

  if (!sanitizedId) {
    return {
      parcelId: "",
      sourceUrl,
      contentType: "",
      htmlDocument: false,
      rawPreview: "",
      status: "SOFT_FAIL",
      reason: "empty parcelId",
    };
  }

  try {
    const response = await fetch(sourceUrl, {
      method: "GET",
      headers: {
        Accept: "text/html,application/json;q=0.9,*/*;q=0.8",
        ...(init?.headers ?? {}),
      },
      ...init,
    });

    if (!response.ok) {
      return {
        parcelId: sanitizedId,
        sourceUrl,
        contentType: response.headers.get("content-type") ?? "",
        htmlDocument: false,
        rawPreview: "",
        status: "SOFT_FAIL",
        reason: `HTTP ${response.status}`,
      };
    }

    const contentType = response.headers.get("content-type") ?? "";
    const text = await response.text();
    const htmlDocument = /text\/html/i.test(contentType) || /<html/i.test(text);

    return {
      parcelId: sanitizedId,
      sourceUrl,
      contentType,
      htmlDocument,
      rawPreview: text.slice(0, 2000),
      status: "OK",
    };
  } catch (error) {
    return {
      parcelId: sanitizedId,
      sourceUrl,
      contentType: "",
      htmlDocument: false,
      rawPreview: "",
      status: "SOFT_FAIL",
      reason: error instanceof Error ? error.message : "fetch failed (often CORS)",
    };
  }
}
