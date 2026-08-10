# Canonical repository consolidation manifest

Base: `f9735d4824e3162efd25362b718bf179acd05b34`
Consolidation branch: `consolidation/ptdt-unified-canonical`

## Source decisions

| Source | Candidate | Canonical disposition | Reason |
|---|---|---|---|
| Tri-County Digital Twin | `src/evidence/evidence_graph.py` | KEEP/IMPORT as `src/evidence/evidence_graph.py` | Canonical provenance/hash/parent-lineage implementation |
| Tri-County Digital Twin | `src/evidence/source_adapters.py` | KEEP/IMPORT as `src/evidence/source_adapters.py` | Source semantics map directly to canonical Evidence Graph |
| Tri-County Digital Twin | `src/evidence/usgs_semantics.py` | KEEP/IMPORT as `src/evidence/usgs_semantics.py` | Explicit observed-vs-derived EnKF distinction |
| Tri-County Digital Twin | `src/evidence/archimedes_authority.py` | KEEP/IMPORT as `src/evidence/archimedes_authority.py` | Independent engineering calculation authority boundary |
| PTDT Unified | `engine/model_contracts.py` | KEEP | Existing cross-model exchange contract remains the model boundary |
| PTDT Unified | `engine/evidence_graph_binding.py` | MERGE/REWIRE | Directly publishes valid exchanges into canonical Evidence Graph |
| PTDT Unified | `engine/enkf_fusion.py` | KEEP | EnKF remains assimilation authority |
| PTDT Unified | `engine/bishop_slope.py` | KEEP | Bishop remains slope-stability authority |
| PTDT Unified | `engine/hec_ras_exchange.py` | KEEP | Explicit hydraulic exchange contract |
| PTDT Unified | `engine/modflow6_exchange.py` | KEEP | Explicit groundwater exchange contract |
| PTDT Unified | `engine/modflow6_runner.py` | FIX | Existing runner failed CI script-backed process tests; boundary hardened |
| Engineering System | `src/services/buildingsService.ts` | ADAPT/IMPORT as canonical Layer 19 service | Best existing deterministic building source/height implementation |
| Engineering System | `src/lib/siteConstants.ts` | ADAPT | Site values must be separated from legal/model authority and linked to evidence when promoted |
| Engineering System | `src/server-gis-routes.ts` | ADAPT if required by deployed API | Overture/Microsoft server proxy behavior; not imported as a second frontend authority |
| Engineering System | `docs/ptdt-v32/v32_Evidence_Manifest.schema.json` | DEPRECATE as v32 schema | Superseded by canonical Evidence Graph; retain only as historical documentation if needed |
| Engineering System | `docs/ptdt-v32/v32_DAG_*` | DOCUMENT_ONLY | Historical v32 architecture; not a runtime authority |
| PTDT-v33 | `backend/physics/hecras_coupler.py` | DO NOT IMPORT | It is a simplified Manning surrogate, not the authoritative HEC-RAS solver; importing it as HEC-RAS authority would be scientifically misleading |
| PTDT-v33 | `frontend/src/shaders/floodWater.wgsl` | DO NOT DUPLICATE | Canonical repository already contains WebGPU/WGSL terrain/flood visualization paths |
| PTDT-v33 | `frontend/src/maplibreCustomFilters.ts` | REVIEW/ADAPT only if canonical lacks equivalent | Avoid duplicate frontend map filter pipeline |
| PTDT-v33 | `frontend/package.json` | DO NOT IMPORT | Canonical root package owns the application dependency graph |

## Active authority matrix

- Evidence/provenance: canonical `src/evidence/evidence_graph.py`
- USGS observations: USGS source records
- Assimilation: `engine/enkf_fusion.py`
- River hydraulics: HEC-RAS exchange/runtime boundary
- Groundwater: MODFLOW6 exchange/runtime boundary
- Slope stability: `engine/bishop_slope.py`
- Independent engineering calculation: Archimedes boundary
- Regulatory evaluation: scoped `engine/regulatory_rules.py` + authoritative rule evidence
- Buildings/structural context: Layer 19 services and Evidence Graph records
- Visualization: MapLibre/Three.js/WebGPU; non-authoritative

## Deduplication invariant

The executable source tree must contain exactly one `ProvenanceRecord` class and exactly one `EvidenceGraph` class. Model contracts may contain `Provenance` for run metadata; that is intentionally a distinct type and is not a second Evidence Graph schema.
