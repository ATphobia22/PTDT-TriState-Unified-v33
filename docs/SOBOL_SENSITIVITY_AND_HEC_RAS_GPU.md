# Sobol Sensitivity Analysis & HEC-RAS GPU / WebGPU Acceleration

**Authority rule:** HEC-RAS Water Surface Elevation (WSE) remains absolute truth. WebGPU and Box3D are presentation / secondary derivation only. NAVD88 vertical, EPSG:2966 horizontal for engineering products.

---

## 1. Sobol Sensitivity Analysis (Variance-Based GSA)

Sobol’ indices decompose model output variance into fractions attributable to each input and to interactions.

### Indices

| Index | Meaning |
|-------|---------|
| **First-order \(S_i\)** | Fraction of output variance explained by input \(X_i\) alone |
| **Total-order \(S_{Ti}\)** | Fraction explained by \(X_i\) including all interactions involving \(X_i\) |
| **Second-order \(S_{ij}\)** | Interaction of \(X_i\) and \(X_j\) only |

\[
S_i = \frac{\mathrm{Var}_{X_i}(\mathbb{E}_{\sim i}[Y \mid X_i])}{\mathrm{Var}(Y)}, \quad
S_{Ti} = 1 - \frac{\mathrm{Var}_{\sim i}(\mathbb{E}_{X_i}[Y \mid X_{\sim i}])}{\mathrm{Var}(Y)}
\]

### Typical PTDT / HEC-RAS 2D Factors (from literature)

- DEM resolution  
- Mesh / cell size  
- Channel & floodplain Manning’s \(n\)  
- Upstream boundary hydrograph  
- Terrain hydro-conditioning choices  

Studies on HEC-RAS 2D and similar 2-D inundation models consistently rank **DEM resolution** and **mesh resolution** among the strongest first-order drivers of water-surface and inundation-extent variance; roughness remains important, especially for timing and peak attenuation.

### Operator Use in PTDT

1. Define continuous distributions on candidate parameters (uniform / triangular / normal / log-normal — same family as HEC-FIA Monte Carlo).  
2. Sample with a quasi-Monte-Carlo (Sobol’ sequence) or Monte-Carlo design.  
3. Run sealed HEC-RAS plans (or surrogate) for each sample.  
4. Compute \(S_i\) / \(S_{Ti}\) on outputs of interest: max WSE at Bonebank, inundation area, depth at LAG/FFE, peak arrival time.  
5. Record seed, sample size, and index table in the SovereignManifestEngine evidence package (state = MODELED).

**Relation to HEC-FIA Monte Carlo:** FIA already samples depth-damage, foundation height, etc., for consequence uncertainty. Sobol GSA is applied upstream on the **hydraulic** model so that the sealed WSE grids fed to FIA are themselves accompanied by a ranked sensitivity statement.

---

## 2. HEC-RAS GPU Acceleration (Official 2025 Path)

HEC-RAS **2025** ships a native **CUDA GPU solver** (NVIDIA, CUDA 12.4 target):

- Explicit Shallow Water Equations (SWE) with global time stepping.  
- CPU path retains both Diffusion Wave and SWE; GPU path is SWE-first (Diffusion Wave planned later).  
- Reported speed-ups typically **12–25×** vs multi-core CPU SWE on mid/high-end cards; larger meshes show higher speed-up.  
- Requires modern NVIDIA GPU + recent drivers.

This is the **authoritative hydraulic compute** path when licensed RAS 2025 + compatible GPU are available. Soft-fail if `rascmd` / GPU solver is absent; never fabricate HDF results.

---

## 3. HEC-RAS → WebGPU Acceleration Boundary (PTDT)

| Layer | Role | Technology |
|-------|------|------------|
| HEC-RAS 2D (CPU or CUDA) | Authoritative WSE / velocity | Native RAS solvers |
| HDF5 extract + seal | Forensic identity | Python `h5py` + SHA-256 |
| Cell-index map + depth bake | Derived presentation | **WebGPU compute** (`cell_index_compute.wgsl`, 16×16 workgroups) |
| MapLibre / TurboVec / Box3D | Visualization & VFX | WebGPU / Unity (secondary only) |

**WebGPU does not replace the RAS solver.** It accelerates:

- Unstructured cell → DEM-grid rasterization of sealed WSE (mm integers → r32float depth).  
- Coalesced texture loads, bounds checks, finite-value guards.  
- Optional async readback for HUD / affidavit plates.

Rules already enforced in `HecRasDepthPipeline.ts` and WGSL kernels:

- 256-byte `bytesPerRow` alignment on texture uploads.  
- `nodata` cell / WSE sentinels.  
- Depth = max(0, WSE − DEM) in NAVD88.  
- No mutation of authoritative hydraulic state.

---

## 4. Recommended Integration Sequence

1. Condition DEM (QGIS SAGA Fill Sinks / Burn Streams) → seal COG (EPSG:2966, NAVD88).  
2. Run HEC-RAS 2025 (GPU SWE if available) → plan HDF.  
3. Export Depth/WSE GeoTIFF via RAS Mapper **or** extract cell WSE → apply sealed `cell_index_map`.  
4. Optional Sobol GSA on key parameters; attach index table to evidence.  
5. Feed sealed depth grid to HEC-FIA (deterministic or Monte Carlo consequences).  
6. Upload sealed depth texture to WebGPU for MapLibre/TurboVec cinematic path.  
7. SovereignManifestEngine four-state seal (OBSERVED terrain, MODELED hydraulics, DERIVED consequences / viz).

---

## References (authoritative)

- HEC-FIA Technical Reference — Monte Carlo Application chapter  
- HEC-RAS 2025 GPU Solver documentation (CUDA explicit SWE)  
- Saltelli / Sobol variance-based global sensitivity literature  
- PTDT hard rules: no fabricated RAS results, no Archimedes overwrite of WSE, EPSG:2966 / NAVD88 only for regulatory Z
