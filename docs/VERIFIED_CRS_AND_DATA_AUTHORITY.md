# Verified CRS, BAFL, and HEC-RAS HDF authority (government / USACE)

Sources: EPSG registry, IDNR Division of Water, IGIO, FEMA CIS/FIS, HEC-RAS 2D User Manual (HDF output).

## 1. Indiana NAD83 State Plane zones

| EPSG | Name | Units | Posey County? |
|---|---|---|---|
| **2966** | NAD83 / Indiana **West** (ftUS) | **US survey foot** | **Yes** (listed in EPSG area of use) |
| **26974** | NAD83 / Indiana West | **metre** | Same zone, metric federal definition |
| **2965** | NAD83 / Indiana **East** (ftUS) | US survey foot | No — eastern counties |
| **26973** | NAD83 / Indiana East | metre | No |

**EPSG:2966 parameters (NGS / EPSG):** Transverse Mercator  
- latitude_of_origin = **37.5**  
- central_meridian = **-87.0833333333333** (−87°05')  
- scale_factor = **0.999966667**  
- false_easting = **900000** US ft  
- false_northing = **250000** US ft  
- ellipsoid GRS80 / NAD83  

State law uses **US survey feet** → prefer **2966** for local engineering coordinates.  
Metric twin: **26974**.

**Do not** use EPSG:26916 (UTM) as the PTDT engineering horizontal CRS. UTM is the **native BAFL delivery CRS only**.

## 2. BAFL shapefile coordinate system (IDNR)

Official IDNR text (Best Available Floodplain Mapping page):

> Each zip file contains ESRI shapefiles, referenced to **Universal Transverse Mercator (UTM) horizontal datum (Zone 16, meters, NAD 1983)**.

| Item | Verified value |
|---|---|
| Native horizontal CRS | **EPSG:26916** (NAD83 / UTM zone 16N, metres) |
| MapServer SR | **26916** (gisdata.in.gov Best_Available_Flood_Hazard_Layer) |
| Layer name | `FloodHazard_BestAvai_DNR_Water` |
| Elev points | `Flood_Elevation_Pts_DNR_Water` — BFE **NAVD88** |
| Insurance use | **Not** for mandatory insurance (use effective FIRM/NFHL) |
| Regulatory use | Planning / construction / Flood Control Act; local ordinance may adopt BAFL |

**Pipeline:**  
`BAFL (26916 m)` → `to_crs(EPSG:2966)` for engineering seal → `to_crs(EPSG:4326)` for MapLibre only.

## 3. HEC-RAS HDF5 extraction (USACE)

Plan results file: **`ProjectName.p##.hdf`**.

Authoritative unsteady 2D time series path (HEC-RAS 2D User Manual):

```text
/Results/Unsteady/Output/Output Blocks/Base Output/Unsteady Time Series/2D Flow Areas/{MeshName}/Water Surface
```

Also documented:
- **Face Velocity** under the same 2D Flow Areas folder  
- Summary maxima under Summary Output  
- Geometry: `/Geometry/2D Flow Areas/{area}/Cells Center Coordinate`

WSE units: **project units** (ft or m) as stored in the plan — typically **feet NAVD88** for US river models. PTDT converts to **mm integer** only for WebGPU transport; regulatory elevations remain feet NAVD88.

**Authority:** Only real plan HDF from a local HEC-RAS run. Soft-fail if file missing. HEC-RAS software is free from HEC; support is not provided by USACE to non-Corps users.

## 4. FEMA community IDs (CIS / FIS)

| Community | CID |
|---|---|
| **Posey County (unincorporated)** | **180209** |
| Mount Vernon city | 180389 |
| New Harmony town | 180210 |

Effective FIRM family referenced in local ordinance materials: **November 5, 2014** (Posey County and Incorporated Areas). FIS elevations converted to **NAVD88** (VERTCON note in FIS materials).

**Do not use CID 180194** for Posey unincorporated.

## 5. Sovereign elevation constants (Material Truth — survey still required for LOMA)

| Quantity | Value | Datum |
|---|---|---|
| BFE | 375.0 ft | NAVD88 |
| LAG | 377.2 ft | NAVD88 |
| FFE | 382.5 ft | NAVD88 |
| Natural clearance | +2.2 ft (LAG−BFE) | — |

These are **internal sealed constants** for digital twin gating. Filing a LOMA still requires Indiana-licensed survey elevations + MT-EZ/MT-1 package.

## 6. Pipeline authority order (unchanged)

```text
HEC-RAS .p##.hdf WSE  → ValidatedHydraulicState (EPSG:2966 horiz, NAVD88 vert, SHA-256)
        → presentation only (WebGPU depth, MapLibre 4326)
BAFL 26916  → reproject 2966 for regulatory GIS  → 4326 for map
NFHL / FIRM  → insurance / SFHA mapping
Assessor APN  → single deed-reconciled ID before LOMA
```
