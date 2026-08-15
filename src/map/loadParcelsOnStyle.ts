import type { Map as MaplibreMap } from "maplibre-gl";
import {
  BONEBANK_BBOX,
  loadIndianaParcelsIntoMap,
  PARCEL_FILL_LAYER,
} from "../services/indianaMapParcels";

/**
 * Call from map.on('style.load') / after style is ready.
 * Soft-fails without taking down the twin.
 */
export async function wireIndianaParcels(map: MaplibreMap): Promise<void> {
  try {
    const n = await loadIndianaParcelsIntoMap(map, BONEBANK_BBOX);
    console.info(`[PTDT] IndianaMap parcels loaded: ${n}`);
    map.on("click", PARCEL_FILL_LAYER, (e) => {
      const f = e.features?.[0];
      const id =
        f?.properties?.parcel_id ??
        f?.properties?.PARCEL_ID ??
        f?.properties?.parcelid ??
        f?.properties?.PROP_ID;
      if (id != null) {
        map.fire("ptdt:parcelclick", { parcelId: String(id) } as never);
      }
    });
  } catch (err) {
    console.warn("[PTDT] IndianaMap parcels soft-fail", err);
  }
}
