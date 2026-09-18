import express from 'express';
import cors from 'cors';
import { createProxyMiddleware } from 'http-proxy-middleware';

const app = express();
const PORT = process.env.PORT || 8080;

app.use(
  cors({
    origin: '*',
    methods: ['GET', 'POST', 'OPTIONS'],
    allowedHeaders: ['Content-Type', 'Authorization'],
  })
);

app.use(
  '/api/usgs',
  createProxyMiddleware({
    target: 'https://waterservices.usgs.gov',
    changeOrigin: true,
    pathRewrite: { '^/api/usgs': '' },
    on: {
      error: (err, req, res) => {
        res.status(502).json({
          error: 'USGS Streamgage Upstream Proxy Error',
          details: err.message,
        });
      },
    },
  })
);

app.use(
  '/api/noaa',
  createProxyMiddleware({
    target: 'https://api.water.noaa.gov',
    changeOrigin: true,
    pathRewrite: { '^/api/noaa': '' },
    on: {
      error: (err, req, res) => {
        res.status(502).json({
          error: 'NOAA NWPS Upstream Proxy Error',
          details: err.message,
        });
      },
    },
  })
);

app.get('/health', (_req, res) => {
  res.json({ status: 'ok', service: 'ptdt-token-proxy' });
});

app.listen(PORT, () => {
  console.log(`[PTDT-Proxy] Data Fabric Proxy active on port ${PORT}`);
});
