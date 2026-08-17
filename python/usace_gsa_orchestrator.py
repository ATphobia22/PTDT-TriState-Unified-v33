"""
PTDT USACE GSA orchestrator
Sobol/Saltelli design → (optional) HEC-RAS plan → sealed WSE extract.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping
import json
import sys

# Package-safe imports: allow `python python/usace_gsa_orchestrator.py` and package use
_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from sobol_sampler import generate_gsa_design, default_hydraulic_gsa_bounds  # noqa: E402
from hecras_pipeline import HecRasPipeline  # noqa: E402


def _canonical_seal(payload: Mapping[str, Any]) -> str:
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256(raw.encode("utf-8")).hexdigest()


def run_gsa_design_only(
    n_base: int = 32,
    seed: int = 42,
    bounds: Mapping[str, tuple[float, float]] | None = None,
) -> dict[str, Any]:
    design = generate_gsa_design(
        n_base=n_base,
        bounds=bounds or default_hydraulic_gsa_bounds(),
        seed=seed,
        calc_second_order=False,
    )
    return {
        "status": design["status"],
        "phase": "DESIGN_ONLY",
        "parameter_names": design["parameter_names"],
        "n_rows": design["n_rows"],
        "n_cols": design["n_cols"],
        "design_seal": design["seal"],
        "meta": design["meta"],
        "problem": design.get("problem"),
        "matrix": design["matrix"],
    }


def try_compute_plan(
    project_dir: str | Path,
    plan: str = "01",
    ras_version: str = "6.5",
) -> dict[str, Any]:
    project_dir = str(project_dir)
    try:
        from hec_ras_bridge import run_plan_ras_commander

        ok = run_plan_ras_commander(project_dir, plan=plan, ras_version=ras_version)
        return {
            "status": "OK" if ok else "SOFT_FAIL_COMPUTE",
            "project_dir": project_dir,
            "plan": plan,
            "ras_version": ras_version,
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "SOFT_FAIL_NO_RAS_COMMANDER",
            "reason": str(exc),
            "project_dir": project_dir,
            "plan": plan,
        }


def extract_sealed_wse(
    plan_hdf: str | Path,
    flow_area: str = "Wabash_Confluence",
    timestep_index: int = 0,
) -> dict[str, Any]:
    pipe = HecRasPipeline(str(plan_hdf))
    return pipe.extract_wse_mm(flow_area=flow_area, timestep_index=timestep_index)


def orchestrate(
    *,
    n_base: int = 32,
    seed: int = 42,
    plan_hdf: str | Path | None = None,
    project_dir: str | Path | None = None,
    plan: str = "01",
    flow_area: str = "Wabash_Confluence",
    timestep_index: int = 0,
    run_compute: bool = False,
) -> dict[str, Any]:
    design = run_gsa_design_only(n_base=n_base, seed=seed)
    compute_result: dict[str, Any] | None = None
    if run_compute and project_dir is not None:
        compute_result = try_compute_plan(project_dir, plan=plan)

    wse_result: dict[str, Any] | None = None
    if plan_hdf is not None:
        wse_result = extract_sealed_wse(
            plan_hdf, flow_area=flow_area, timestep_index=timestep_index
        )

    envelope = {
        "schema_version": 1,
        "phase": "USACE_GSA_ORCHESTRATOR",
        "design_seal": design["design_seal"],
        "design_n_rows": design["n_rows"],
        "parameter_names": design["parameter_names"],
        "n_model_runs": (design.get("meta") or {}).get("n_model_runs"),
        "compute_status": (compute_result or {}).get("status", "SKIPPED"),
        "wse_status": (wse_result or {}).get("status", "SKIPPED"),
        "wse_seal": (wse_result or {}).get("seal"),
        "crs": (wse_result or {}).get("crs"),
        "vertical_datum": (wse_result or {}).get("vertical_datum"),
    }
    envelope["master_seal"] = _canonical_seal(envelope)

    return {
        "status": "OK",
        "design": {k: v for k, v in design.items() if k != "matrix"},
        "compute": compute_result,
        "wse": (
            {k: v for k, v in wse_result.items() if k != "data"} if wse_result else None
        ),
        "envelope": envelope,
        "matrix": design.get("matrix"),
    }


if __name__ == "__main__":
    import argparse

    p = argparse.ArgumentParser(description="PTDT USACE GSA orchestrator")
    p.add_argument("--n-base", type=int, default=16)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--plan-hdf", type=str, default=None)
    p.add_argument("--project-dir", type=str, default=None)
    p.add_argument("--run-compute", action="store_true")
    p.add_argument("--flow-area", type=str, default="Wabash_Confluence")
    args = p.parse_args()

    result = orchestrate(
        n_base=args.n_base,
        seed=args.seed,
        plan_hdf=args.plan_hdf,
        project_dir=args.project_dir,
        run_compute=args.run_compute,
        flow_area=args.flow_area,
    )
    print(json.dumps({k: v for k, v in result.items() if k != "matrix"}, indent=2))
