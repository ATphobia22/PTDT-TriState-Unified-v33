# ArcGIS FeatureServer limits + PMTiles

## Limits (Esri / IndianaMap Hosted)

| Property | Typical value |
|---|---|
| `maxRecordCount` | **2000** (Indiana parcels Hosted) |
| Pagination | `resultOffset` + `resultRecordCount` |
| More data signal | `exceededTransferLimit: true` or full page length |
| Hard client cap | 25 pages (~50k) in `indianaMapParcels.ts` |

Do not request `resultRecordCount` above service max; server clamps.

## Runtime

```bash
pip install -r requirements.txt
python -m uvicorn python.main:app --host 0.0.0.0 --port 8000
# Vite app → http://localhost:8000/api/proxy/xsoft/posey/parcel?parcel_id=...
```

## Offline PMTiles

```bash
bash scripts/posey_parcels_to_pmtiles.sh
# requires tippecanoe for .pmtiles; always writes GeoJSON
```

MapLibre: `pmtiles://` protocol or static host of `runtime_assets/parcels/posey_parcels.pmtiles`.
