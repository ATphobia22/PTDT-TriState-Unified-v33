from engine.clearance_analyzer import StructuralClearanceAnalyzer


RECORD = {
    "building_id": "test-building",
    "structural_use": "municipal",
    "lowest_adjacent_grade_ft": 377.20,
    "first_floor_elevation_ft": 382.50,
}


def test_secure_clearance():
    manifest = StructuralClearanceAnalyzer().evaluate_node_clearance(RECORD, 376.40)
    assert manifest.lowest_floor_freeboard_ft == 6.10
    assert manifest.statutory_compliance_pass is True


def test_submersion_is_failure():
    manifest = StructuralClearanceAnalyzer().evaluate_node_clearance(RECORD, 383.10)
    assert manifest.lowest_floor_freeboard_ft == -0.60
    assert manifest.hydrostatic_threat_status == "CRITICAL_FIRST_FLOOR_SUBMERSION"
    assert manifest.statutory_compliance_pass is False
