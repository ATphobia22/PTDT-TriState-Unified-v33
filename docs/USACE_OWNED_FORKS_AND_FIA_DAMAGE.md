# USACE-Adjacent Owned Repos + HEC-FIA Direct Damage

## Sobol GSA implementation (PTDT `python/sobol_sampler.py`)

1. **Unit samples** — `scipy.stats.qmc.Sobol` (scrambled, seedable) or pure fallback ≤20 dims.  
2. **Scale** — affine map from [0,1) to finite [lo, hi] per factor.  
3. **Saltelli matrix** — rows A, B, and A_B^(i) (optional B_A^(i) for second-order); size N·(D+2) or N·(2D+2).  
4. **Seal** — SHA-256 over rounded samples + metadata (evidence).  
5. **Orchestrator** — `python/usace_gsa_orchestrator.py` ties design → optional ras-commander → `HecRasPipeline.extract_wse_mm`.

Evaluate each matrix row with a sealed RAS plan (or surrogate); then compute Sobol’ S_i / S_Ti offline (e.g. SALib) on chosen outputs (max WSE at Bonebank, inundation area).

## HEC-FIA direct damage (official Technical Reference)

\[
D_i = d_i \times v_i
\]

- **Depth at structure** = max depth − foundation height (FH).  
- **d_i** = percent damage from occupancy-type depth–percent curves (structure, contents, vehicles; optional “other”); linear interpolation between ordinates.  
- **v_i** = monetary value from structure inventory.  
- Vehicle value may be reduced by evacuation (warning time / %clear / capacity).  
- If depth×velocity exceeds total-loss threshold → 100% loss on structure, contents, vehicles.

Hydraulic inputs to FIA must be **sealed HEC-RAS depth/WSE grids** (or cross-sections). FIA does not alter WSE.

## Owned ATphobia22 USACE-named repos (inventory)

| Repo | Status / notes |
|------|----------------|
| **USACE-WISP** | Present — static HTML/SCSS site (WISP UI assets), not hydraulic engine |
| **cwms-database** | Check fork of HEC CWMS DB schema (official upstream: HydrologicEngineeringCenter/cwms-database) |
| **Antecedent-Precipitation-Tool** | Likely fork/mirror of ERDC APT (wetland/regulatory climate normalcy) |
| **national-structure-inventory-examples** | NSI examples → FIA structure inventory feed |
| **usace-flood-geoprocessing** | Flood geoprocessing utilities if present |
| **groundwork / groundwork-water** | USACE Groundwork ecosystem forks if present |
| **RMC-BestFit, Numerics, rfaR** | Risk Management Center / frequency analysis tooling if present |
| **CE-QUAL-W2, pyBathy** | Water quality / bathymetry adjacent |
| **rts-utils, cwms-cli** | CWMS/RTS automation |
| **BIM-Revit-Templates, USACE, USACE_QCC_*, USACE_WaterManagementAccessibility** | BIM / portal / accessibility mirrors |

**Canonical hydraulic path for PTDT remains:** licensed HEC-RAS (6.x/7.x or 2025 GPU) + `hec_ras_bridge` / `hecras_pipeline` + sealed COGs — not these UI/schema forks alone.

Official APT upstream: `erdc/Antecedent-Precipitation-Tool` (v3.0).  
Official CWMS DB: `HydrologicEngineeringCenter/cwms-database`.  
CWMS data API: https://cwms-data.usace.army.mil/cwms-data/
