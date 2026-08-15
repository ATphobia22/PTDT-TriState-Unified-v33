/**
 * Protomaps PMTiles ↔ MapLibre addProtocol (npm `pmtiles`).
 * Register once at app root; remove on teardown.
 * @see https://docs.protomaps.com/pmtiles/maplibre
 */
import maplibregl from "maplibre-gl";
import { Protocol } from "pmtiles";

let registered = false;
let protocol: Protocol | null = null;

export function registerPmtilesProtocol(): void {
  if (registered) return;
  protocol = new Protocol();
  maplibregl.addProtocol("pmtiles", protocol.tile);
  registered = true;
}

export function unregisterPmtilesProtocol(): void {
  if (!registered) return;
  try {
    maplibregl.removeProtocol("pmtiles");
  } catch {
    /* already removed */
  }
  protocol = null;
  registered = false;
}

/** Local offline pack from scripts/posey_parcels_to_pmtiles.sh */
export const LOCAL_POSEY_PARCELS_PMTILES =
  "pmtiles:///runtime_assets/parcels/posey_parcels.pmtiles";

export const PMTILES_PARCEL_SOURCE = "posey-parcels-pmtiles";
export const PMTILES_PARCEL_LAYER = "posey-parcels-pmtiles-fill";
export const PMTILES_SOURCE_LAYER = "parcels"; // tippecanoe -l parcels

/**
 * Prefer offline PMTiles when served; soft-fail if file missing.
 * source-layer must match tippecanoe `-l parcels`.
 */
export function tryAddPoseyParcelsPmtiles(
  map: maplibregl.Map,
  url: string = LOCAL_POSEY_PARCELS_PMTILES,
): boolean {
  try {
    if (map.getSource(PMTILES_PARCEL_SOURCE)) return true;
    map.addSource(PMTILES_PARCEL_SOURCE, {
      type: "vector",
      url,
      attribution: "IGIO Indiana Data Harvest parcels (offline PMTiles)",
    });
    if (!map.getLayer(PMTILES_PARCEL_LAYER)) {
      map.addLayer({
        id: PMTILES_PARCEL_LAYER,
        type: "fill",
        source: PMTILES_PARCEL_SOURCE,
        "source-layer": PMTILES_SOURCE_LAYER,
        paint: {
          "fill-color": "#38bdf8",
          "fill-opacity": 0.12,
        },
      });
      map.addLayer({
        id: `${PMTILES_PARCEL_LAYER}-line`,
        type: "line",
        source: PMTILES_PARCEL_SOURCE,
        "source-layer": PMTILES_SOURCE_LAYER,
        paint: {
          "line-color": "#38bdf8",
          "line-width": 1,
        },
      });
    }
    return true;
  } catch (err) {
    console.warn("[PTDT] PMTiles parcels soft-fail (use FeatureServer GeoJSON)", err);
    return false;
  }
}
