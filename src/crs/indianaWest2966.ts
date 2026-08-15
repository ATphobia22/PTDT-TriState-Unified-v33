/**
 * Official EPSG:2966 — NAD83 / Indiana West (ftUS)
 * Parameters from EPSG registry / NGS State Plane (US survey feet).
 * Posey County is in the Indiana West zone area of use.
 */
export const EPSG_2966_PROJ4 =
  "+proj=tmerc +lat_0=37.5 +lon_0=-87.08333333333333 +k=0.999966667 " +
  "+x_0=900000 +y_0=250000 +ellps=GRS80 +datum=NAD83 +units=us-ft +no_defs";

/** Native BAFL / many IDNR downloads: NAD83 UTM 16N metres */
export const EPSG_26916 = "EPSG:26916";

/** Engineering horizontal CRS for PTDT sealed products */
export const ENGINEERING_CRS = "EPSG:2966";

/** MapLibre GeoJSON presentation CRS */
export const MAPLIBRE_GEOJSON_CRS = "EPSG:4326";

/** FEMA CID — Posey County unincorporated (Community Status Book) */
export const FEMA_CID_POSEY_UNINCORPORATED = "180209";

/** FEMA CID — City of Mount Vernon */
export const FEMA_CID_MOUNT_VERNON = "180389";
