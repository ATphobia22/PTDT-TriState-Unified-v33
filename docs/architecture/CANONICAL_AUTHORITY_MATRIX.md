# Canonical authority matrix

| Domain | Authority | Evidence input | Derived output | Consumer |
|---|---|---|---|---|
| Observations | USGS-NWIS / source dataset | source record | observation record | EnKF / HUD |
| Assimilation | EnKF | USGS/model evidence | derived-assimilation record | PTDT |
| Hydraulics | HEC-RAS | hydraulic model inputs | hydraulic result | Bishop / compliance |
| Groundwater | MODFLOW6 | groundwater inputs | groundwater result | PTDT / engineering |
| Slope stability | Bishop | hydraulic + geotechnical evidence | slope-stability record | compliance / HUD |
| Engineering calculation | Archimedes | provenance-bearing engineering inputs | engineering result | compliance / HUD |
| Buildings | Layer 19 | footprint/height/source evidence | structural-context relationships | MapLibre / scene state |
| Landscape / environmental context | PTDT-native derived analytics | land-cover, terrain, hydrography, floodplain evidence | landscape/riparian metrics | engineering state / scene state |
| Human / exposure context | PTDT-native derived analytics | population, roads, facilities, buildings, hydraulic evidence | exposure-context metrics | engineering state / reporting / scene state |
| Scene description | OpenUSD scene package | canonical Engineering State + Evidence Graph IDs | time-sampled scene artifact | Hydra / DCC / cinematic pipeline |
| Regulatory | versioned jurisdiction rule + authoritative model result | rule evidence + model evidence | PASS/FAIL/NOT_EVALUATED | HUD/reporting |
| Visualization | PTDT WebGPU/MapLibre/Three.js/Hydra projection | derived Evidence Graph + scene records | visual projection | operator / cinematic pipeline |

## External repository boundary

- `USEPA/ATtILA2` is a methodological/reference source for landscape, riparian, and human-environment metrics. It does not become the PTDT environmental authority.
- OpenStreetMap-derived data may be used only through an explicitly identified, versioned source artifact. `awesome-openstreetmap` is a catalog/reference repository, not data authority.
- OpenUSD is the scene-description/interchange authority only for cinematic scene artifacts. It does not define engineering truth.
- `openusd-mcp`, Hydra, OpenDCC, and related DCC tooling operate downstream of canonical scene state.
- WebGPU/WGSL is the primary interactive rendering path. `gpu.cpp` and Taichi are candidate compute backends and must pass numerical regression tests before promotion.
- GPUStack is infrastructure, not a scientific authority. Its credentials, cluster access, and model-serving endpoints must be isolated by least privilege.

## Promotion rules

1. A source observation is immutable from the perspective of derived-model promotion.
2. A derived result must contain parent evidence IDs.
3. A result with status other than `VALID` cannot be promoted to an authoritative derived state.
4. Vertical datum and units must be explicit when an elevation relationship is calculated.
5. Regulatory evaluation requires a scoped rule and authoritative model provenance.
6. Visualization cannot create engineering or regulatory evidence.
7. Scene artifacts must retain references to the engineering-state/evidence records from which they were generated.
8. GPU-accelerated implementations must reproduce reference numerical results within a documented tolerance before becoming production implementations.
9. External orchestration services cannot mutate authoritative evidence or engineering state directly.
