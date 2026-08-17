# HEC-RAS 2D Computational Mesh Generation

Official workflow summary (HEC-RAS 2D User’s Manual / RAS Mapper).  
**Authority:** Mesh geometry supports hydraulics; WSE from the solver remains absolute truth. NAVD88 / EPSG:2966 for PTDT engineering products.

---

## 1. Mesh Structure

Finite-volume mesh (structured or unstructured):

| Element | Role |
|---------|------|
| **Cell center** | One WSE computed per cell per time step |
| **Cell faces** | Control flux between cells (may be multi-point on perimeter) |
| **Face points** | Endpoints of faces; used for 1D/BC connections |

- Cells may have **3–8 sides** (max 8).  
- Built via **Delaunay triangulation** of computation points → **Voronoi** cells (faces orthogonal to point connections).  
- **Subgrid bathymetry:** elevation–volume curves and face hydraulic tables are derived from the detailed terrain under each cell/face (Casulli-style high-resolution subgrid). Large cells still “feel” fine terrain.

---

## 2. Generation Steps (RAS Mapper)

1. **Perimeter polygon**  
   - Draw 2D Flow Area boundary on terrain (within terrain extent).  
   - Prefer high ground separating 1D channel from floodplain when coupling.

2. **Base computation points**  
   - Edit 2D Area Properties → Points Spacing **DX / DY** (e.g. 50–200 ft study-dependent).  
   - **Generate Computation Points** (with or without breaklines).  
   - Warning: regenerating replaces existing points (hand edits lost unless regenerated from features).

3. **Breaklines** (enforce faces along barriers)  
   - Place on levees, roads, berms, channel banks/centerlines — anything that controls flow direction.  
   - Properties: Near Spacing, Near Repeats, Far Spacing, optional 1-cell protection radius.  
   - Process: buffer remove points → insert aligned points → snap/enforce faces.

4. **Refinement regions**  
   - Polygon with interior cell spacing + perimeter treated like a breakline.  
   - Use for channels, structures, steep WSE gradients.

5. **Manual edits** (last resort)  
   - Move / add / delete computation points.  
   - Prefer breaklines + refinement + **Regenerate Computation Points** for reproducibility.

6. **Property tables**  
   - Pre-processor builds elev–volume and face tables (filter tolerances, min area fraction, conveyance tol, laminar depth, min face length ratio).  
   - Default Manning’s n + optional land-use n polygons.

**Recommended reproducible workflow:** start coarse → add refinements incrementally → always **Regenerate Computation Points** (ordered enforcement) rather than one-off hand edits for sensitivity batches.

---

## 3. Quality Guidance

- Align faces with high ground so water does not “leak” through barriers.  
- Smaller cells where WSE slope changes rapidly; coarser where flat.  
- Avoid concave perimeter artifacts; smooth boundary or refine locally.  
- One face between cells; one BC per face.  
- Mesh cell size is a primary Sobol GSA factor (see `python/sobol_sampler.py`).

---

## 4. PTDT Coupling

```
Terrain (sealed COG, NAVD88)
    → 2D perimeter + DX/DY + breaklines/refinement
    → Generate / regenerate mesh
    → Compute property tables
    → Unsteady plan (CPU or RAS 2025 GPU SWE)
    → HDF WSE / RAS Mapper Depth GeoTIFF
    → SHA-256 seal → cell_index_map / WebGPU depth bake / FIA grids
```

Soft-fail if licensed RAS / plan HDF absent. Never invent mesh or WSE.

---

## References

- HEC-RAS: Development of the 2D Computational Mesh  
- RAS Mapper: 2D Flow Areas, Breaklines, Refinement Regions  
- HEC-RAS 2D modeling advantages (subgrid property tables)
