/**
 * PTDT sovereign constants — only government-verified or explicitly labeled.
 * APN candidate is NOT auto-verified; LOMA stays blocked until Engage+deed match.
 */

export const SOVEREIGN = {
  APP_ID: "point-township-dt-v33",
  CRS_HORIZ: "EPSG:2966",
  CRS_HORIZ_LABEL: "NAD83 / Indiana West (ftUS)",
  CRS_BAFL_NATIVE: "EPSG:26916",
  CRS_BAFL_LABEL: "NAD83 / UTM Zone 16N (m)",
  VERTICAL_DATUM: "NAVD88",
  /** Material Truth — not a substitute for licensed LOMA survey */
  BFE_FT: 375.0,
  LAG_FT: 377.2,
  FFE_FT: 382.5,
  CID_POSEY_UNINCORPORATED: "180209",
  CID_MOUNT_VERNON: "180389",
  /**
   * Candidate assessor-style ID only. Must match Engage Property ID + deed
   * before LomaAffidavitGate clears UNVERIFIED_DUAL.
   */
  APN_CANDIDATE: "65-19-08-100-008.001-010",
  ASSESSOR_OFFICE: "Posey County Assessor",
  ASSESSOR_PHONE: "(812) 838-1309",
  ASSESSOR_ADDRESS: "126 E Third Street, Mt. Vernon, IN 47620",
  ENGAGE_BASE: "https://engage.xsoftinc.com/posey",
  /** Confirmed detail page pattern (HTML). Prefer server proxy. */
  ENGAGE_PARCEL_DETAIL: "https://engage.xsoftinc.com/posey/map/getparceldetail",
  /**
   * getparcellist?search-envelop= returns Map shell, not public JSON.
   * Keep for research only; do not treat as API contract.
   */
  ENGAGE_PARCEL_LIST_EXPERIMENTAL:
    "https://engage.xsoftinc.com/posey/map/getparcellist",
  NWS_GAUGE_MT_VERNON: "https://water.noaa.gov/gauges/mtvi3",
  NWS_GAUGE_ID: "MTVI3",
} as const;

export function normalizeParcelId(id: string): string {
  return String(id || "").replace(/\D/g, "");
}

export function parcelIdsEquivalent(a: string, b: string): boolean {
  const na = normalizeParcelId(a);
  const nb = normalizeParcelId(b);
  return na.length > 0 && na === nb;
}

/** Natural grade above BFE → LOMA path, not LOMR-F. */
export function naturalLomaClearanceFt(): number {
  return SOVEREIGN.LAG_FT - SOVEREIGN.BFE_FT;
}
