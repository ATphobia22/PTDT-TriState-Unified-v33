# IDNR special streams, SHAARD, IGIO, DoWORC

## Special / Outstanding Rivers (Posey identifiers)

From IDNR Appendix E.4 / Outstanding Rivers roster (not 312 IAC Natural Scenic system — those are only Blue River, Cedar Creek, Wildcat):

| Stream | County | Segment identifier |
|---|---|---|
| **Black River** | Posey | Higginbotham Ditch confluence → Wabash confluence |
| **Cypress Slough** | Posey | Castlebury Creek confluence → Southwind Maritime Center |
| **Wabash River** | multi incl. Posey | IN–OH line → Ohio River confluence |

NRC navigable roster (Posey) still applies for public waters: Big Creek, Harris Ditch, Little Fork Big Creek, McFadden Creek, Ohio, Wabash.

**No official machine-readable stream ID API** was found for Special Streams; treat names + extent text as the identifier. Overlay as awareness layer only.

## Division of Water Online Research Center (DoWORC)

- Portal: https://www.in.gov/dnr/water/online-research-center/
- Records: permits, FARA, early coordination, dams, violations (UTM points)
- Companion DB note: https://dowunity.dnr.in.gov (per DNR help PDF)

Use for **site-specific permit history** near Bonebank; not a substitute for INFIP FARA generation.

## SHAARD (historic / archaeological)

| Resource | URL |
|---|---|
| Landing | https://www.in.gov/dnr/historic-preservation/county-survey-program/shaard-database/ |
| SHAARD app | https://shaard.dnr.in.gov/ |
| IHBBC Map | https://gisdata.in.gov/portal/apps/experiencebuilder/experience/?id=93749795652e4fa197fae122d2ba0a9c |

Includes IHSSI county surveys, cemeteries, historic bridges, NR listings. **Archaeology locations restricted.** Checking SHAARD does not waive Section 106 / state review duties. Relevant for cultural resources near confluence / Caborn-Welborn context — secondary to hydro authority.

## IGIO (Indiana Geographic Information Office)

| Product | Access |
|---|---|
| 2025 Parcels | IndianaMap FeatureServer / Data Harvest |
| Elevation / LiDAR | AWS Open Data `in-elevation` — https://registry.opendata.aws/in-elevation |
| Docs | https://elevation.gio.in.gov/ |
| Imagery + DEM REST | IGIO GeoInsights imagery hub |

S3 LAS remains the sealed-DEM path for WebGPU depth bake.
