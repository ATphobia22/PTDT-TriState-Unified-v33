/** Stub GIS service — prevents import errors from MapComponent */
export async function fetchFloodDepth(_bbox?: number[]) {
  return { features: [] };
}
export async function getParcelEnvelope() {
  return { xmin: -88.02, ymin: 37.83, xmax: -87.99, ymax: 37.86 };
}
export default { fetchFloodDepth, getParcelEnvelope };
