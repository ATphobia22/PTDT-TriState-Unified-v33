# OpenUSD / GPU / OpenStreetMap Federation Forensic Capability Map

**Status:** Federated research inventory; no external repository becomes a PTDT scientific authority by inclusion.

## Scope

This document maps the newly supplied repositories and references into the canonical PTDT architecture. The default disposition is **reference/federate first**, followed by benchmark or adapter work. Source code is not vendored merely because a repository is useful.

## Repository inventory

| Source | Domain | Disposition | PTDT role |
|---|---|---|---|
| `ATphobia22/awesome-openstreetmap` | OSM ecosystem reference | RETAIN/REFERENCE | Data-source and tooling discovery; no runtime authority |
| `ATphobia22/OpenUSD` | OpenUSD scene description | FEDERATE / ADAPT | Canonical interchange/archive representation for cinematic scene packages; not engineering-state authority |
| `ATphobia22/noodles` | Unspecified from supplied repository identity | AUDIT FIRST | Capability discovery only until repository contents are reviewed |
| `ATphobia22/glTF-MaterialX-Converterq` | glTF / MaterialX | AUDIT / CORRECT PATH | Candidate asset/material conversion adapter; supplied path currently returns GitHub 404 |
| `ATphobia22/UniversalSceneDescription` | USD ecosystem | FEDERATE / DEDUPLICATE | Compare against OpenUSD; do not maintain two USD authorities |
| `ATphobia22/openusd-mcp` | MCP / OpenUSD automation | WRAP | Optional agent/tooling adapter around USD operations; never scientific authority |
| `ATphobia22/awesome-openusd` | OpenUSD ecosystem reference | RETAIN/REFERENCE | Discovery, interoperability, examples |
| `ATphobia22/Aurora` | Rendering/graphics research candidate | AUDIT FIRST | Candidate cinematic/rendering subsystem; no authority until capability audit |
| `ATphobia22/hydra-viewport-toolbox` | USD Hydra viewport | WRAP / ADAPT | Offline/professional viewport/reference path; downstream of engineering state |
| `ATphobia22/OpenDCC` | DCC / asset pipeline | WRAP / ADAPT | DCC interchange and asset-processing path; not simulation authority |
| `ATphobia22/omniverse-dsx-blueprint-for-ai-factories` | GPU/AI factory architecture | REFERENCE | Infrastructure topology and GPU orchestration patterns; no direct PTDT runtime dependency by default |
| `ATphobia22/gpustack` | GPU orchestration | WRAP / INFRASTRUCTURE | Optional multi-GPU compute/inference orchestration; isolated from scientific authority |
| `ATphobia22/gpuweb` | WebGPU specification/reference implementation ecosystem | RETAIN/REFERENCE | WebGPU/WGSL compatibility and conformance reference |
| `webgpu.org` | WebGPU standards/docs | RETAIN/REFERENCE | API/specification authority for WebGPU implementation decisions |
| `AnswerDotAI/gpu.cpp` | GPU compute C++ abstraction | BENCHMARK / ADAPT | Native/offline compute benchmark candidate; do not replace WebGPU renderer |
| `ATphobia22/taichi` | GPU numerical programming | BENCHMARK / RESEARCH ADAPTER | Scientific/GPU kernel prototyping and benchmark path; production authority only after validation |
| `ATphobia22/gpu-perf-engineering-resources` | GPU performance knowledge base | RETAIN/REFERENCE | Optimization, profiling, kernel and GPU architecture reference |

## Canonical architecture mapping

### 1. OpenStreetMap

**Use:** authoritative-source discovery and open geospatial context where an actual OSM-derived dataset is explicitly selected and versioned.

**Do not use:** an `awesome-*` repository as data authority.

**Native PTDT path:** normalized OSM-derived artifacts -> provenance -> Evidence Graph -> MapLibre/engineering consumers.

### 2. OpenUSD

OpenUSD is an efficient, scalable system for authoring, reading, and streaming time-sampled scene description for graphics interchange. The supplied fork's README also documents Linux/macOS/Windows support and WebAssembly build capability. fileciteturn31file0L2-L2

**Disposition:** FEDERATE / ADAPT.

**Target role:** cinematic scene package/interchange layer:

`Engineering State -> Scene State -> USD stage -> Hydra/DCC/render/export`

**Boundary:** USD stores and transports scene representation. It does not define HEC-RAS, MODFLOW6, Bishop, EnKF, regulatory, or Evidence Graph authority.

### 3. UniversalSceneDescription

**Disposition:** DEDUPLICATE against `OpenUSD`.

The PTDT federation must select one OpenUSD source tree/version for build and compatibility testing. `UniversalSceneDescription` may remain a research/reference source, but two independently vendored USD implementations are prohibited.

### 4. OpenUSD MCP

**Disposition:** WRAP.

MCP tooling can expose controlled scene operations to agents. It must operate through validated project/workspace boundaries and must not permit an agent to mutate authoritative scientific state without an explicit engineering-state API.

### 5. Hydra viewport toolbox / OpenDCC

**Disposition:** WRAP / ADAPT.

These belong downstream of canonical scene generation. They can accelerate inspection, DCC interchange, and cinematic production, but cannot create authoritative hydraulic, groundwater, structural, or regulatory results.

### 6. GPUStack / Omniverse DSX blueprint

**Disposition:** INFRASTRUCTURE REFERENCE / OPTIONAL WRAPPER.

GPUStack is a GPU cluster manager for deploying inference engines and managing GPU resources; current upstream documentation describes multi-cluster management, pluggable inference engines, monitoring, authentication and access control. citeturn0search0

**Security requirement:** do not deploy PTDT workloads against an unpatched GPUStack release. Upstream release notes document security fixes for authorization and SAML authentication vulnerabilities in earlier 2.x versions. citeturn0search1

The DSX blueprint is architectural reference material, not a PTDT dependency.

### 7. WebGPU / gpuweb / gpu.cpp

**WebGPU:** standards/reference authority.

**gpuweb:** conformance/specification implementation reference.

**gpu.cpp:** native C++ compute benchmark/adapter candidate.

**Boundary:** PTDT's browser/Electron renderer remains WebGPU/WGSL. Native GPU compute can be benchmarked separately and selected only when it materially improves a validated workload.

### 8. Taichi

Taichi is a portable GPU/CPU numerical programming framework with JIT compilation and support for multiple GPU APIs. citeturn0search5

**Disposition:** RESEARCH / BENCHMARK ADAPTER.

Candidate workloads:

- flood-grid morphology
- terrain raster transforms
- particle/flow visualization experiments
- sediment/particle prototypes
- numerical kernels
- EnKF matrix/vector benchmarks
- Bishop parameter sweeps

A Taichi implementation must reproduce canonical PTDT results before it can be considered for production acceleration.

### 9. GPU performance resources

**Disposition:** RETAIN/REFERENCE.

Use for profiling methodology, memory-transfer analysis, occupancy/workgroup tuning, shader optimization, and regression benchmarks. It does not become executable runtime code merely by federation.

## Required PTDT scene pipeline

```text
Canonical Engineering State
        |
        +-- HEC-RAS / MODFLOW6 / Bishop / EnKF
        +-- Terrain / Buildings / Landscape / Exposure
        +-- Evidence Graph + provenance
        |
        v
Canonical Scene State
        |
        +--> WebGPU/WGSL real-time renderer
        +--> MapLibre geographic context
        +--> OpenUSD time-sampled scene package
        |       +--> Hydra viewport
        |       +--> OpenDCC/DCC adapters
        |       +--> cinematic export
        |
        v
Validated frame / scene artifact
```

## Deduplication rules

1. One canonical OpenUSD implementation/version per PTDT build environment.
2. One canonical WebGPU renderer; external GPU frameworks are benchmark/adapter candidates.
3. No OSM catalog repository becomes an authoritative geospatial dataset.
4. No DCC or USD layer can write directly into authoritative engineering state.
5. All derived scene artifacts retain parent engineering/evidence identifiers.
6. GPU acceleration must be numerically regression-tested against the CPU/reference implementation.
7. External infrastructure services must remain isolated from scientific state and must use authenticated, least-privilege access.

## Known source-resolution issue

`ATphobia22/glTF-MaterialX-Converterq` could not be resolved through the connected GitHub repository API at the supplied path. It remains in the inventory as **AUDIT / CORRECT PATH** rather than being silently replaced with another repository.

## Recommended implementation order

1. Freeze canonical OpenUSD version/source.
2. Define `EngineeringState -> SceneState` USD schema/prim conventions.
3. Add USD export/import contract tests.
4. Benchmark WebGPU vs native GPU candidates for identified kernels.
5. Add Hydra/OpenDCC inspection adapters.
6. Add controlled OpenUSD MCP operations.
7. Add GPUStack only when distributed GPU execution is required.
8. Promote no external implementation to scientific authority without validation and provenance tests.
