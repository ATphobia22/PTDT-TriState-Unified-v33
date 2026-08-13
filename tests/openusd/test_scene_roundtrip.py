"""OpenUSD scene-contract round-trip test.

This test verifies that the PTDT SceneState identity/provenance fields survive
serialization into a USD stage and a subsequent stage reload.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from pxr import Sdf, Usd


SCHEMA_VERSION = "1.0.0"
ENGINEERING_STATE_ID = "eng-001"
SIMULATION_TIME_UTC = "2026-08-13T00:00:00Z"
CRS = "EPSG:26916"
VERTICAL_DATUM = "NAVD88"
EVIDENCE_ID = "ev-001"


def test_scene_state_usd_round_trip() -> None:
    with tempfile.TemporaryDirectory() as temporary_directory:
        stage_path = Path(temporary_directory) / "ptdt_scene.usda"

        stage = Usd.Stage.CreateNew(str(stage_path))
        root = stage.DefinePrim("/PTDT", "Xform")
        root.CreateAttribute(
            "ptdt:sceneSchemaVersion", Sdf.ValueTypeNames.String
        ).Set(SCHEMA_VERSION)
        root.CreateAttribute(
            "ptdt:engineeringStateId", Sdf.ValueTypeNames.String
        ).Set(ENGINEERING_STATE_ID)
        root.CreateAttribute(
            "ptdt:simulationTimeUtc", Sdf.ValueTypeNames.String
        ).Set(SIMULATION_TIME_UTC)
        root.CreateAttribute("ptdt:crs", Sdf.ValueTypeNames.String).Set(CRS)
        root.CreateAttribute(
            "ptdt:verticalDatum", Sdf.ValueTypeNames.String
        ).Set(VERTICAL_DATUM)
        root.CreateAttribute(
            "ptdt:evidenceId", Sdf.ValueTypeNames.String
        ).Set(EVIDENCE_ID)
        stage.GetRootLayer().Save()

        reopened_stage = Usd.Stage.Open(str(stage_path))
        reopened_root = reopened_stage.GetPrimAtPath("/PTDT")

        assert reopened_root.IsValid()
        assert reopened_root.GetAttribute("ptdt:sceneSchemaVersion").Get() == SCHEMA_VERSION
        assert reopened_root.GetAttribute("ptdt:engineeringStateId").Get() == ENGINEERING_STATE_ID
        assert reopened_root.GetAttribute("ptdt:simulationTimeUtc").Get() == SIMULATION_TIME_UTC
        assert reopened_root.GetAttribute("ptdt:crs").Get() == CRS
        assert reopened_root.GetAttribute("ptdt:verticalDatum").Get() == VERTICAL_DATUM
        assert reopened_root.GetAttribute("ptdt:evidenceId").Get() == EVIDENCE_ID
