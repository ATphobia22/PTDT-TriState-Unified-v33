import express from 'express';
import { Pool } from 'pg';

const router = express.Router();
const pool = new Pool({
  host: process.env.POSTGRES_HOST || '127.0.0.1',
  port: parseInt(process.env.POSTGRES_PORT || '8087', 10),
  database: process.env.POSTGRES_DB || 'ptdt',
  user: process.env.POSTGRES_USER || 'ptdt',
  password: process.env.POSTGRES_PASSWORD || 'ptdt',
});

router.post('/api/engineering/ras-results', async (req, res) => {
  const { plan_id, cells } = req.body;

  if (!plan_id || !Array.isArray(cells)) {
    return res.status(400).json({ error: 'Malformed multi-physics payload structure' });
  }

  const client = await pool.connect();
  try {
    await client.query('BEGIN');
    await client.query('DELETE FROM twin_ras_cells WHERE plan_id = $1', [plan_id]);

    const insertQuery = `
      INSERT INTO twin_ras_cells (plan_id, lon, lat, depth_m, wse_m)
      VALUES ($1, $2, $3, $4, $5)
    `;

    for (const cell of cells) {
      await client.query(insertQuery, [
        plan_id,
        parseFloat(cell.lon),
        parseFloat(cell.lat),
        parseFloat(cell.depth_m ?? cell.depth_ft * 0.3048 ?? 0),
        cell.wse_m != null ? parseFloat(cell.wse_m) : (cell.wse_ft != null ? parseFloat(cell.wse_ft) * 0.3048 : null),
      ]);
    }

    await client.query('COMMIT');
    res.status(200).json({ status: 'Synchronized', updated_cells: cells.length });
  } catch (error) {
    await client.query('ROLLBACK');
    console.error('[SYNC] Failed to commit mesh matrices:', error);
    res.status(500).json({ error: 'Database synchronization failure' });
  } finally {
    client.release();
  }
});

export default router;
