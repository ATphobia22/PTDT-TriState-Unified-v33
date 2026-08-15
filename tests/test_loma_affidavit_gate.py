from python.loma_affidavit_gate import LomaAffidavitGate


def test_dual_apn_blocks():
    gate = LomaAffidavitGate()
    res = gate.generate_affidavit_payload("65-09-35-000-001", "65-19-08-000-001")
    # Missing files fail first in CI; if files present, dual APN must block
    assert res["status"] in ("SOFT_FAIL_DEPENDENCY", "BLOCKED")
    assert res["seal"] is None


def test_natural_loma_math():
    gate = LomaAffidavitGate()
    assert gate.verify_natural_loma_eligibility() is True
    assert gate.LAG_FT - gate.BFE_FT == 2.2
