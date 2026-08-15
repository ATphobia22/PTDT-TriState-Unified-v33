# External live endpoints (data gates)

## Posey assessor (XSoft Engage)

- Portal: https://engage.xsoftinc.com/posey
- Detail pattern (verified HTML):  
  `https://engage.xsoftinc.com/posey/map/getparceldetail?parcelId={APN}`
- Example: `65-06-07-140-009.000-005`
- **Not** a documented public JSON API. Browser fetch often **CORS-blocked**.
- Client: `src/services/xsoftService.ts` (soft-fail + open official URL)

## IGIO elevation / imagery (AWS Open Data)

- Elevation LAS: `aws s3 ls --no-sign-request s3://giselevationingov/`
- Docs: https://elevation.gio.in.gov/ | https://registry.opendata.aws/in-elevation
- Imagery COGs: `s3://gisimageryingov/` (CC0)
- Scripts: `scripts/pdal_extract_ground.json`, `scripts/cog_bare_earth_navd88.sh`
- Project horizontal default: **EPSG:2966**; vertical **NAVD88**

## FEMA NFHL

- MapServer: https://hazards.fema.gov/arcgis/rest/services/public/NFHL/MapServer
- Identify helper: `src/services/nfhlIdentify.ts`
- Insurance context only; LOMA needs sealed LAG/survey

## IDNR / INFIP

- Best Available floodplain + FARA: Indiana Floodplain Information Portal (DNR Division of Water)
- Manual download still required for sealed BAFL packages
