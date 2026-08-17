# HEC-FIA Monte Carlo & PTDT Integration

## Monte Carlo (HEC-FIA Technical Reference)

- Continuous distributions: uniform, triangular, normal, log-normal.  
- Controls: Initial Seed (repeatable), Convergence Tolerance, sample-size guidance.  
- Sampling techniques: single-parameter, two-parameter, tabular relationship (depth-damage), std-dev as % of mean.  
- Policy driver: ER 1105-2-101 risk-based analysis for BCR inputs.

## Integration Steps (fail-closed)

1. Sealed HEC-RAS Depth/WSE GeoTIFF (or 1-D mm array + cell_index_map).  
2. Import as **Grids** hydraulic event in HEC-FIA 3.4.2+.  
3. Structure inventory (NSI or sealed local GeoJSON).  
4. Optional Monte Carlo on damage curves / foundation heights.  
5. Export consequence reports → SovereignManifestEngine.  

**Invariant:** FIA never alters HEC-RAS WSE. WebGPU depth bake shares the same sealed source file as FIA grids when possible.
