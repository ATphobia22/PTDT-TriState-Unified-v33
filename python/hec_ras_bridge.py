\"\"\"
HEC-RAS Python API bridge for PTDT / TSDES
Primary: ras-commander (HDF-native, HEC-RAS 6.x+)
Fallback: COM HECRASController / rascontrol for older versions
\"\"\"
from __future__ import annotations

from pathlib import Path
from typing import Any

def run_plan_ras_commander(project_dir: str, plan: str = "01", ras_version: str = "6.5") -> bool:
    \"\"\"Execute plan via ras-commander (preferred).\"\"\"
    from ras_commander import init_ras_project, RasCmdr

    init_ras_project(project_dir, ras_version)
    return bool(RasCmdr.compute_plan(plan))


def extract_max_wse(project_dir: str, plan: str = "01", ras_version: str = "6.5") -> Any:
    \"\"\"Mesh max water-surface elevation from plan HDF.\"\"\"
    from ras_commander import init_ras_project, HdfResultsMesh

    init_ras_project(project_dir, ras_version)
    return HdfResultsMesh.get_mesh_max_ws(plan)


def cells_from_hdf(hdf_path: str) -> list[dict]:
    \"\"\"
    Lightweight direct HDF read (h5py) for depth/WSE cells
    when ras-commander is unavailable.
    Paths vary by HEC-RAS version — adjust group names as needed.
    \"\"\"
    import h5py
    import numpy as np

    cells: list[dict] = []
    with h5py.File(hdf_path, "r") as f:
        # Example unsteady 2D max depth path (version-dependent)
        # Explore with: f['Results'].visit(print)
        try:
            depth = f["Results/Unsteady/Output/Output Blocks/Base Output/Unsteady Time Series/2D Flow Areas"]
            # structure is model-specific; return empty if not found
        except KeyError:
            return cells
    return cells


def run_plan_com(project_path: str, plan_index: int = 1, version: str = "6.0") -> None:
    \"\"\"Legacy COM path (Windows + HEC-RAS installed).\"\"\"
    try:
        import rascontrol
        rc = rascontrol.RasController(version=version.replace(".", ""))
        rc.open_project(project_path)
        rc.run_current_plan()
    except ImportError:
        # win32com HECRASController alternative
        import win32com.client
        ras = win32com.client.Dispatch("RAS6x.HECRASController")
        ras.Project_Open(project_path)
        ras.Compute_CurrentPlan()


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python hec_ras_bridge.py <project_dir> [plan]")
        sys.exit(1)
    ok = run_plan_ras_commander(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "01")
    print("compute_plan:", ok)
