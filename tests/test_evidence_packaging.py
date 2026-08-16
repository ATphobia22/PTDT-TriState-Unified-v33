import tarfile

from services.fema_appeal_packager import FemaAppealPackager


def test_passing_manifest_is_not_packaged(tmp_path):
    manifest = {"compliance_metrics": {"statutory_compliance_pass": True}}
    assert FemaAppealPackager(str(tmp_path)).compile_fema_appeal_package(manifest) is None


def test_failed_manifest_creates_dossier(tmp_path):
    manifest = {
        "manifest_metadata": {"cryptographic_manifest_seal": "source-seal"},
        "compliance_metrics": {
            "building_id": "node-1",
            "structural_use": "municipal",
            "lowest_adjacent_grade_ft": 377.2,
            "first_floor_elevation_ft": 382.5,
            "current_water_surface_ft": 383.1,
            "lowest_floor_freeboard_ft": -0.6,
            "hydrostatic_threat_status": "CRITICAL_FIRST_FLOOR_SUBMERSION",
            "statutory_compliance_pass": False,
        },
    }
    archive = FemaAppealPackager(str(tmp_path)).compile_fema_appeal_package(manifest)
    assert archive is not None and archive.exists()
    with tarfile.open(archive, "r:gz") as tar:
        names = tar.getnames()
    assert "appeal_dossier/structural_clearance_manifest.json" in names
    assert "appeal_dossier/engineering_clearance_brief.pdf" in names
    assert "appeal_dossier/package_manifest.json" in names
