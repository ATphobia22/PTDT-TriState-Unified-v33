# HEC-RAS Integration

## Path A — ras-commander (recommended, HDF)

```powershell
pip install ras-commander h5py pandas
python python\hec_ras_bridge.py C:\Models\MyProject 01
```

- `init_ras_project` + `RasCmdr.compute_plan`
- `HdfResultsMesh.get_mesh_max_ws` for max WSE

## Path B — COM (legacy / rascontrol)

Requires HEC-RAS installed on Windows.

```python
# see python/hec_ras_bridge.py run_plan_com()
```

## Path C — push cells into PostGIS

1. Extract mesh cells (lon, lat, depth_m, wse_m) from plan `*.p##.hdf`
2. POST batch to `/api/engineering/ras-results`
3. MapLibre / twin reads from PostGIS or MVT

## Units

Router accepts `depth_m` / `wse_m` or converts `depth_ft` / `wse_ft` × 0.3048.
