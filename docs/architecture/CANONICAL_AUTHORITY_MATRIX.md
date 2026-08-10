# Canonical authority matrix

| Domain | Authority | Evidence input | Derived output | Consumer |
|---|---|---|---|---|
| Observations | USGS-NWIS / source dataset | source record | observation record | EnKF / HUD |
| Assimilation | EnKF | USGS/model evidence | derived-assimilation record | PTDT |
| Hydraulics | HEC-RAS | hydraulic model inputs | hydraulic result | Bishop / compliance |
| Groundwater | MODFLOW6 | groundwater inputs | groundwater result | PTDT / engineering |
| Slope stability | Bishop | hydraulic + geotechnical evidence | slope-stability record | compliance / HUD |
| Engineering calculation | Archimedes | provenance-bearing engineering inputs | engineering result | compliance / HUD |
| Buildings | Layer 19 | footprint/height/source evidence | structural-context relationships | MapLibre |
| Regulatory | versioned jurisdiction rule + authoritative model result | rule evidence + model evidence | PASS/FAIL/NOT_EVALUATED | HUD/reporting |
| Visualization | PTDT | derived Evidence Graph records | visual projection | operator |

## Promotion rules

1. A source observation is immutable from the perspective of derived-model promotion.
2. A derived result must contain parent evidence IDs.
3. A result with status other than `VALID` cannot be promoted to an authoritative derived state.
4. Vertical datum and units must be explicit when an elevation relationship is calculated.
5. Regulatory evaluation requires a scoped rule and authoritative model provenance.
6. Visualization cannot create engineering or regulatory evidence.
