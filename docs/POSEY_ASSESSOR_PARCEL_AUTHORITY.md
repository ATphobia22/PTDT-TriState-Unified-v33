# Posey County parcel / APN authority (verified government sources)

## Official offices and portals

| Role | Source |
|---|---|
| County Assessor (market-value-in-use) | [poseycountyin.gov Assessors Office](https://www.poseycountyin.gov/county-offices/assessors-office/) |
| Citizen property search / PRC | [Engage — engage.xsoftinc.com/posey](https://engage.xsoftinc.com/posey) |
| Engage map | [engage.xsoftinc.com/posey/Map/Index](https://engage.xsoftinc.com/posey/Map/Index) |
| Engage user guide | [Engage_UserGuide.pdf](https://engageblob.blob.core.windows.net/engage-assets/help/Engage_UserGuide.pdf) |
| County GIS (WTH) | [poseyin.wthgis.com](http://poseyin.wthgis.com/) |
| DLGF forms / appeals | [in.gov/dlgf](https://www.in.gov/dlgf/) |
| Sales disclosure (SDF) | [DLGF 8294](https://www.in.gov/dlgf/8294.htm) |
| Business personal property | [DLGF personal property](https://www.in.gov/dlgf/assessments/personal-property/) (due **May 15**) |
| Statewide parcels (geometry) | IndianaMap Parcel Boundaries of Indiana **2025** |

**Assessor contacts (county site / Engage Contact):**  
126 E Third St, Rooms 223/228, Mt Vernon, IN 47620 · (812) 838-1309 · M–F 8:00–4:00 **CT**  
Assessor: Nancy A. Hoehn · nancy.hoehn@poseycountyin.gov  
GIS / related deputies listed on county and Engage contact pages (titles may rotate).

**Disclaimer (Engage):** Assessment data provided **as is**; subject to IC 36-1-8.5 restrictions. Not a survey or LOMA authority.

## Indiana parcel number structure (50 IAC 26-8-1)

Canonical pattern:

```text
00-00-00-000-000.000-000
```

| Segment | Meaning |
|---|---|
| 1st `00` | County code (Posey = **65**) |
| 2nd `00` | Congressional township & range |
| 3rd `00` | PLSS **section** |
| 4th `000` | Urban block (often `000` rural) |
| 5th `000.000` | Permanent parcel number |
| Last `000` | State-assigned **taxing district** |

IGIO Data Harvest / IndianaMap: `STATE_PARCEL_ID` is digits-only; display form restores hyphens/dot as above. Join tax district using first 2 + last 3 digits when 18-character numeric ID is present.

**Rule 6 (PTDT):** Internal twin ID and assessor **Property ID** must **match character-for-character** after normalize (strip spaces). Mismatch → `UNVERIFIED_DUAL` → LOMA affidavit **BLOCKED**.  
Do not invent a preferred APN. Resolve via: **deed (Recorder)** + **Engage Property ID** + **IndianaMap/WTH parcel geometry**.

## Where citizens find the parcel number (Engage FAQ)

- Form 11 (Notice of Assessment)  
- Property record card  
- Tax bill  
- Engage search by address  

## Assessment calendar (county site)

| Date | Event |
|---|---|
| **January 1** | Real / personal / oil & gas assessment date |
| **April** | Notices of assessment mailed |
| **May 15** | Business personal property filing; exemptions; oil & gas forms |
| Ongoing | 25% of county reassessed each year (4-year cycle) |

Assessment ratio target: **100%** (AV / sale price). Approaches: cost, income, sales comparison. Annual adjustment + ratio study required by state.

## Appeals (Engage / IC 6-1.1-15-1.1)

- Form **130** (blank or parcel-prepopulated in Engage Forms tab)  
- If Form 11 mailed **before May 1** → appeal by **June 15** that year  
- If Form 11 mailed **after April 30** → appeal by **June 15** of the year tax statements are mailed  

## Regrid and commercial aggregators

[app.regrid.com/us/in/posey](https://app.regrid.com/us/in/posey) and similar sites are **secondary**. For PTDT regulatory gates use **Engage + IndianaMap + deed** only. Regrid may help exploration but must not override dual-APN lock.

## Integration hooks (existing code)

| Component | Use |
|---|---|
| `/api/proxy/xsoft/posey/parcel` | Server-side Engage HTML/JSON soft-fail |
| `queryIndianaParcelsGeoJson` | IndianaMap FeatureServer bbox (maxRecordCount ~2000) |
| `LomaAffidavitGate.verify_apn_dual_id` | Exact match gate |
| WTH GIS | Operator visual check: http://poseyin.wthgis.com/ |

## Operator checklist for Bonebank / 13101 Bonebank Rd

1. Search address on Engage → copy **Property ID** exactly.  
2. Open same parcel on IndianaMap 2025 / WTH GIS → confirm geometry.  
3. Match **deed** legal description / APN at Recorder.  
4. Set twin `county_assessor_apn` = Engage ID; clear dual-ID only when all three agree.  
5. Proceed to LOMA package only after step 4 (elevations still need licensed survey).
