# J.T. Myers gauge + Bonebank property impact ladder

## Gauge authority (NWS / USGS)

| Item | Value |
|------|--------|
| Name | Ohio River at J.T. Myers Lock and Dam |
| NWS ID | **UNWK2** |
| USGS site | **03322420** |
| County | Posey, IN |
| Role | **Navigation** lock & dam — **not** flood-control storage |
| NWS page | https://water.noaa.gov/gauges/unwk2 |

**Vertical (NWS published table, approximate):**

| Level | NAVD88 (ft) |
|-------|-------------|
| Gauge zero | ~311.31 |
| Action | ~344.31 |
| Minor flood | ~348.31 |
| Moderate | ~360.31 |
| Major | ~371.31 |

Historic crests (NWS): 1937 **64.40** stage-ft; 2011 **56.92**; 2025-04-14 **54.09**.

Cross-check stations used in family records: Shawneetown IL (Ohio), New Harmony IN (Wabash), Mt. Vernon IN, Evansville IN.

## Operational property thresholds (family ground truth)

Stages below are **J.T. Myers stage feet** mapped to 13101 Bonebank Road impacts.  
They are **early-warning / operational** only.

**Not** a substitute for sealed **NAVD88** BFE 375.0 / LAG 377.2 / FFE 382.5 used for LOMA and Material Truth.

| Myers stage (ft) | Code | Impact |
|------------------|------|--------|
| 54.93 | ALERT | Dock bank full |
| 55.55 | WARNING | Bridge top begins flowing (Ohio side) |
| 55.85–56.25 | WARNING | Water at / over bridge top |
| 56.75 | DANGER | Road floods past bridge |
| 57.25 | DANGER | Near Bobby's house; pole barn ~3 ft less |
| 57.85 | DANGER | Barn; ~5 ft from house |
| 58.15 | CRITICAL | Property center |
| 58.45–58.75 | CRITICAL | House floor level |

Machine-readable: `data/geo/property_impact_thresholds.json`

## Regulatory twin (unchanged)

| Constant | Value | Datum |
|----------|-------|--------|
| BFE | 375.0 ft | NAVD88 |
| LAG | 377.2 ft | NAVD88 |
| FFE | 382.5 ft | NAVD88 |

LOMA / IDNR FARA / survey remain authoritative for elevations.
