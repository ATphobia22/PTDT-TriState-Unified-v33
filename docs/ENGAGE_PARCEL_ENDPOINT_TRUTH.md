# XSoft Engage Posey — endpoint truth (verified 2026-08-15)

## What was tested

| URL | Result |
|---|---|
| `https://engage.xsoftinc.com/posey/map/getparcellist?search-envelop=65-19-08-100-008.001-010` | Returns **Map shell HTML** + disclaimer only. **No** parcel JSON body in the public response. |
| `https://engage.xsoftinc.com/posey/map/getparceldetail?parcelId={id}` | **Works** for parcel detail pages (HTML). Example path shape confirmed with other Posey IDs (e.g. `65-06-07-140-009.000-005`). |
| Engage search UI | Official path for citizens: search by address / parcel number on `/posey`. |

**Implication for PTDT:** Do **not** treat `getparcellist?search-envelop=` as a stable machine API. Prefer:

1. Server proxy that fetches **`/posey/map/getparceldetail?parcelId=`** and parses typed fields, or
2. Operator paste of Property ID from Engage UI / Form 11 / tax bill.

Disclaimer on all Engage pages: data **as is**, not for legal/real-estate reliance without assessor confirmation.

## Candidate vs verified APN

| ID | Status |
|---|---|
| `65-19-08-100-008.001-010` | **CANDIDATE only** — well-formed Posey (`65`) 50 IAC display string. **Not** web-proven as 13101 Bonebank Rd without Engage + deed match. |
| `65-09-35-...` (older twin internal) | **Rejected as sole truth** — dual-ID conflict until cleared. |

`LomaAffidavitGate` remains **BLOCKED** until digit-normalized Engage Property ID equals deed-recorded ID.

## LOMA vs LOMR-F (do not conflate)

| Process | When |
|---|---|
| **LOMA** (44 CFR Part 70) | Natural grade (LAG) above BFE **without** fill |
| **LOMR-F** | Structure/grade depends on **fill**; fee + more review |

UI that shows `LAG > BFE` as “LOMR-F Eligibility” is **wrong**. Label as **natural-ground LOMA path (survey still required)**.

## Gauge (Ohio River @ Mount Vernon)

- NWS/NOAA product page: [water.noaa.gov/gauges/mtvi3](https://water.noaa.gov/gauges/mtvi3)
- Impact note: **~45 ft** — large portions of **Point Township** flooded (moderate category context on gauge page).
- Stages are **live** — never hardcode stage/cfs as static sovereign constants.

## Correct CONFIG subset for code

```ts
CRS_HORIZ = EPSG:2966
CRS_BAFL_NATIVE = EPSG:26916
VERTICAL = NAVD88
CID_POSEY_UNINC = 180209
CID_MT_VERNON = 180389
ENGAGE_DETAIL = https://engage.xsoftinc.com/posey/map/getparceldetail?parcelId=
ENGAGE_LIST = experimental / not public JSON
APN_CANDIDATE = 65-19-08-100-008.001-010  // not auto-verified
BFE/LAG/FFE = Material Truth constants; LOMA needs licensed survey
```
