import fs from 'fs';
import path from 'path';
import { Pool } from 'pg';

const pgPool = new Pool({
  host: process.env.POSTGRES_HOST || '127.0.0.1',
  port: parseInt(process.env.POSTGRES_PORT || '8087', 10),
  database: process.env.POSTGRES_DB || 'ptdt',
  user: process.env.POSTGRES_USER || 'ptdt',
  password: process.env.POSTGRES_PASSWORD || 'ptdt',
});

export async function bootstrapLocalStaticAssets() {
  const localDataDir = path.join(
    process.env.LOCALAPPDATA || process.env.APPDATA || '.',
    'TriRiverTwin',
    'static_gis'
  );
  const targetFile = path.join(localDataDir, 'bonebank_parcels_fixed.json');

  if (!fs.existsSync(targetFile)) {
    console.warn(`[GIS] Static baseline missing at ${targetFile}. Awaiting upstream sync...`);
    return { status: 'missing', count: 0 };
  }

  try {
    const rawData = fs.readFileSync(targetFile, 'utf8');
    const geoJson = JSON.parse(rawData);
    let count = 0;

    for (const feature of geoJson.features || []) {
      const assetId = feature.properties?.ASSET_ID || feature.id || `auto_${count}`;
      const wktGeom = feature.properties?.wkt_geom || null;
      if (!wktGeom) continue;

      await pgPool.query(
        `INSERT INTO public.twin_static_parcels (id, geom, metadata)
         VALUES ($1, ST_GeomFromText($2, 4326), $3)
         ON CONFLICT (id) DO UPDATE SET metadata = EXCLUDED.metadata`,
        [assetId, wktGeom, JSON.stringify(feature.properties || {})]
      );
      count++;
    }

    console.log(`[GIS] Bootstrapped ${count} local properties.`);
    return { status: 'ok', count };
  } catch (error) {
    console.error('[GIS] Critical boot breakdown:', error);
    return { status: 'error', message: String(error) };
  }
}
