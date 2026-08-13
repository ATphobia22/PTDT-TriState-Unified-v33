from datetime import datetime, timezone
from pathlib import Path

import pytest

from engine.archimedes_engine import ArchimedesEngine
from engine.authority import AuthorityDomain, assert_authorized, can_promote
from engine.hec_ras_exchange import normalize_hec_ras_boundary, to_exchange_payload
from engine.model_contracts import FailureClass, ModelRunResult, ModelStatus, Provenance
from engine.modflow6_exchange import build_modflow_boundary, promote_groundwater_result
from engine.modflow6_runner import Modflow6Runner


def provenance(model="MODFLOW6"):
    return Provenance(model, "run-001", "base", datetime.now(timezone.utc), "NAVD88", "ft")


def test_contracts_and_authority():
    assert FailureClass.TIMEOUT is not FailureClass.CONVERGENCE_FAILURE
    assert_authorized("Archimedes", AuthorityDomain.REGULATORY)
    with pytest.raises(PermissionError):
        assert_authorized("Archimedes", AuthorityDomain.GROUNDWATER)
    assert not can_promote(ModelStatus.FAILED, AuthorityDomain.GROUNDWATER)
    assert ArchimedesEngine.authority_domains() == {"REGULATORY"}


def test_hec_ras_normalization_and_exchange():
    boundary = normalize_hec_ras_boundary({
        "stage_ft": 376.5,
        "timestamp_utc": "2026-08-10T00:00:00+00:00",
        "datum": "NAVD88",
        "river_id": "tri-county-mainstem",
        "run_id": "ras-001",
        "scenario_id": "base",
    })
    payload = to_exchange_payload(boundary)
    assert payload.values["stage_ft"] == 376.5
    assert payload.provenance.source_model == "HEC-RAS"
    assert build_modflow_boundary(boundary, [(1, 1)]).values["exchange_direction"] == "HEC-RAS_TO_MODFLOW6"


def test_hec_ras_rejects_wrong_datum():
    with pytest.raises(ValueError, match="NAVD88"):
        normalize_hec_ras_boundary({
            "stage_ft": 376.5, "timestamp_utc": "2026-08-10T00:00:00+00:00",
            "datum": "NGVD29", "river_id": "r", "run_id": "x", "scenario_id": "base",
        })


def test_missing_modflow_executable_fails_closed(tmp_path: Path):
    nam = tmp_path / "model.nam"
    nam.write_text("namefile")
    result = Modflow6Runner("missing-modflow6").run(tmp_path, nam, provenance())
    assert result.status is ModelStatus.FAILED
    assert result.failure_class is FailureClass.EXECUTABLE_MISSING


def test_modflow_process_failure(tmp_path: Path):
    exe = tmp_path / "fake-mf6"
    exe.write_text("#!/bin/sh\nexit 7\n")
    exe.chmod(0o755)
    nam = tmp_path / "model.nam"
    nam.write_text("BEGIN OPTIONS\nEND OPTIONS\n")
    result = Modflow6Runner(str(exe)).run(tmp_path, nam, provenance())
    assert result.status is ModelStatus.FAILED
    assert result.failure_class is FailureClass.PROCESS_ERROR
    assert result.exit_code == 7


def test_modflow_valid_output_promotes(tmp_path: Path):
    exe = tmp_path / "fake-mf6"
    exe.write_text("#!/bin/sh\nsleep 0.02\nprintf 'heads' > model.hds\nexit 0\n")
    exe.chmod(0o755)
    nam = tmp_path / "model.nam"
    nam.write_text("namefile")
    result = Modflow6Runner(str(exe)).run(tmp_path, nam, provenance())
    assert result.status is ModelStatus.VALID
    payload = promote_groundwater_result(result, {(1, 1): 375.2})
    assert payload.status is ModelStatus.VALID


def test_failed_modflow_cannot_promote():
    now = datetime.now(timezone.utc)
    result = ModelRunResult(ModelStatus.FAILED, FailureClass.PROCESS_ERROR, 1, "", "error", now, now, None, provenance())
    with pytest.raises(ValueError, match="not valid"):
        promote_groundwater_result(result, {(1, 1): 375.2})
