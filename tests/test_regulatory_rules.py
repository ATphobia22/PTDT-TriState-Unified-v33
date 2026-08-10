from engine.regulatory_rules import EvaluationStatus, HydraulicEvidence, RULES, evaluate_hydraulic_result


def test_illinois_delineation_threshold_is_not_project_certification():
    evidence = HydraulicEvidence("prov-il", "HEC-RAS", "IL", 0.05, "VALID", "floodway")
    result = evaluate_hydraulic_result(RULES["IL-3700-FLOODWAY-DELINEATION"], evidence)
    assert result.status is EvaluationStatus.NOT_EVALUATED


def test_kentucky_no_impact_uses_authoritative_result():
    evidence = HydraulicEvidence("prov-ky", "HEC-RAS", "KY", 0.0, "VALID", "regulatory-floodway")
    result = evaluate_hydraulic_result(RULES["KY-401KAR-4-060-NO-IMPACT"], evidence)
    assert result.status is EvaluationStatus.PASS
    assert result.provenance_id == "prov-ky"


def test_indiana_state_and_fema_criteria_are_distinct():
    evidence = HydraulicEvidence("prov-in", "HEC-RAS", "IN", 0.10, "VALID", "fema-floodway")
    state_result = evaluate_hydraulic_result(RULES["IN-DNR-312IAC10-ADVERSE-EFFECT"], evidence)
    fema_result = evaluate_hydraulic_result(RULES["IN-FEMA-FLOODWAY-NO-RISE"], evidence)
    assert state_result.status is EvaluationStatus.PASS
    assert fema_result.status is EvaluationStatus.FAIL


def test_missing_authoritative_result_is_not_evaluated():
    result = evaluate_hydraulic_result(RULES["KY-401KAR-4-060-NO-IMPACT"], None)
    assert result.status is EvaluationStatus.NOT_EVALUATED
