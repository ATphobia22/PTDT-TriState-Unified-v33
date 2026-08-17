# IGIO Indiana Building Footprints (2016–2020)

Official state service (LiDAR-era polygons).

| Item | Value |
|------|--------|
| FeatureServer | https://gisdata.in.gov/server/rest/services/Hosted/Building_Footprints/FeatureServer/0 |
| Layer name | Indiana Building Footprints 2016-2020 |
| Native CRS | **EPSG:3857** (Web Mercator) |
| Fields | `objectid`, `lidaryear`, `county` |
| MaxRecordCount | 2000 (paginate with `resultOffset`) |
| Formats | JSON, GeoJSON, shapefile, filegdb |

## Operator

```bash
bash scripts/fetch_igio_posey_buildings.sh
# Optional: clip further to Bonebank bbox after download
```

## Priority vs other sources

1. Local sealed survey footprints  
2. **IGIO 2016–2020** (this service) — aligned with statewide LiDAR years  
3. Microsoft USBuildingFootprints Indiana zip (`scripts/fetch_bonebank_buildings.sh`)  
4. Overture (height enrichment)  
5. OSM fill gaps only  

Always reproject sealed engineering geometry to **EPSG:2966**. Display may use 4326.

## Related IGIO services

- Parcel boundaries (Current): `…/Hosted/Parcel_Boundaries_of_Indiana_Current/FeatureServer`  
- Address points / road centerlines (Current)  
- Orthoimagery tile footprints (COG download URLs)  
