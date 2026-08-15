/**
 * Indiana real parcel index (50 IAC 26-8-1).
 * Display form: 00-00-00-000-000.000-000
 * Posey county code = 65.
 */

const DISPLAY_RE =
  /^(\d{2})-(\d{2})-(\d{2})-(\d{3})-(\d{3})\.(\d{3})-(\d{3})$/;

/** Strip to 18 digits for comparison with STATE_PARCEL_ID-style keys. */
export function parcelIdToDigits(raw: string): string {
  return raw.replace(/\D/g, "");
}

/** True if both IDs refer to the same parcel under digit-only equality. */
export function parcelIdsEquivalent(a: string, b: string): boolean {
  const da = parcelIdToDigits(a);
  const db = parcelIdToDigits(b);
  if (!da || !db) return false;
  return da === db;
}

/** Posey county segment must be 65. */
export function isPoseyCountyParcelId(raw: string): boolean {
  const d = parcelIdToDigits(raw);
  return d.length >= 2 && d.startsWith("65");
}

/** Soft-validate display form; returns null if not 50 IAC shaped. */
export function parseIndianaParcelDisplay(raw: string): {
  county: string;
  townshipRange: string;
  section: string;
  block: string;
  permanent: string;
  taxDistrict: string;
} | null {
  const m = raw.trim().match(DISPLAY_RE);
  if (!m) return null;
  return {
    county: m[1],
    townshipRange: m[2],
    section: m[3],
    block: m[4],
    permanent: `${m[5]}.${m[6]}`,
    taxDistrict: m[7],
  };
}
