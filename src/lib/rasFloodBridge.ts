export interface RasCell { lon: number; lat: number; depth_m: number; wse_m?: number; }
export function computeHints(cells: RasCell[]) {
  const maxD = Math.max(...cells.map(c => c.depth_m), 0);
  return { intensity: Math.min(1, maxD / 3), particleDensity: Math.min(1.5, maxD * 0.5), wetness: Math.min(1, maxD) };
}
export async function ingestCells(cells: RasCell[], endpoint = "/api/engineering/ras-results") {
  const batch = 5000;
  for (let i = 0; i < cells.length; i += batch) {
    await fetch(endpoint, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(cells.slice(i, i + batch)) });
  }
}
