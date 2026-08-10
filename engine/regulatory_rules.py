"""Versioned, scoped regulatory criteria.

These records deliberately distinguish floodway delineation criteria from
project-specific no-rise/permit determinations. They are metadata and evaluation
inputs, not legal advice or certification.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class EvaluationStatus(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    NOT_EVALUATED = "NOT_EVALUATED"


@dataclass(frozen=True)
class RegulatoryRule:
    rule_id: str
    jurisdiction: str
    citation: str
    criterion_type: str
    threshold_ft: float | None
    operator: str | None
    scope: str
    source_url: str
    verified_on: str


RULES = {
    "IL-3700-FLOODWAY-DELINEATION": RegulatoryRule(
        rule_id="IL-3700-FLOODWAY-DELINEATION",
        jurisdiction="IL",
        citation="17 Ill. Adm. Code Part 3700, §3700.20",
        criterion_type="floodway_delineation_stage_increase",
        threshold_ft=0.10,
        operator="<=",
        scope="Illinois floodway definition/delineation; not a universal project no-rise certification threshold.",
        source_url="https://www.ilga.gov/agencies/JCAR/EntirePart?titlepart=01703700",
        verified_on="2026-08-10",
    ),
    "KY-401KAR-4-060-NO-IMPACT": RegulatoryRule(
        rule_id="KY-401KAR-4-060-NO-IMPACT",
        jurisdiction="KY",
        citation="401 KAR 4:060, §4(1)",
        criterion_type="regulatory_floodway_no_impact",
        threshold_ft=0.0,
        operator="<=",
        scope="Encroachments in the regulatory floodway require licensed-engineer certification with technical data demonstrating no impact/no increase during base flood discharge, subject to the regulation's exceptions.",
        source_url="https://apps.legislature.ky.gov/law/kar/titles/401/004/060/",
        verified_on="2026-08-10",
    ),
    "IN-DNR-312IAC10-ADVERSE-EFFECT": RegulatoryRule(
        rule_id="IN-DNR-312IAC10-ADVERSE-EFFECT",
        jurisdiction="IN",
        citation="312 IAC 10-2-3",
        criterion_type="state_adverse_effect_floodway_capacity",
        threshold_ft=0.15,
        operator="<",
        scope="Indiana definition of adversely affecting floodway efficiency/capacity; exceptions apply. This is distinct from FEMA mapped-floodway no-rise requirements.",
        source_url="https://www.in.gov/dnr/water/regulatory-permit-programs/exemptions/",
        verified_on="2026-08-10",
    ),
    "IN-FEMA-FLOODWAY-NO-RISE": RegulatoryRule(
        rule_id="IN-FEMA-FLOODWAY-NO-RISE",
        jurisdiction="IN",
        citation="44 CFR 60.3(d)(3), as implemented/explained by Indiana DNR",
        criterion_type="fema_floodway_no_rise",
        threshold_ft=0.0,
        operator="<=",
        scope="FEMA-mapped floodway projects in NFIP communities require no-rise certification or the applicable FEMA map-revision process; project applicability must be established from the site and community context.",
        source_url="https://www.in.gov/dnr/water/surface-water/indiana-floodplain-mapping/no-rise/",
        verified_on="2026-08-10",
    ),
}


@dataclass(frozen=True)
class HydraulicEvidence:
    provenance_id: str
    source: str
    jurisdiction: str
    rise_ft: float
    status: str
    scope_context: str


@dataclass(frozen=True)
class ComplianceResult:
    rule_id: str
    status: EvaluationStatus
    provenance_id: str | None
    reason: str


def evaluate_hydraulic_result(rule: RegulatoryRule, evidence: HydraulicEvidence | None) -> ComplianceResult:
    if evidence is None:
        return ComplianceResult(rule.rule_id, EvaluationStatus.NOT_EVALUATED, None, "authoritative hydraulic Evidence Graph result is required")
    if evidence.status != "VALID":
        return ComplianceResult(rule.rule_id, EvaluationStatus.NOT_EVALUATED, evidence.provenance_id, f"hydraulic result status is {evidence.status}")
    if evidence.jurisdiction != rule.jurisdiction:
        return ComplianceResult(rule.rule_id, EvaluationStatus.NOT_EVALUATED, evidence.provenance_id, "jurisdiction mismatch")
    if rule.threshold_ft is None:
        return ComplianceResult(rule.rule_id, EvaluationStatus.NOT_EVALUATED, evidence.provenance_id, "rule has no numeric criterion")
    if rule.criterion_type == "floodway_delineation_stage_increase":
        return ComplianceResult(rule.rule_id, EvaluationStatus.NOT_EVALUATED, evidence.provenance_id, "delineation criterion cannot certify a project permit/no-rise result")
    if rule.operator == "<=" and evidence.rise_ft <= rule.threshold_ft:
        return ComplianceResult(rule.rule_id, EvaluationStatus.PASS, evidence.provenance_id, "hydraulic rise satisfies scoped criterion")
    if rule.operator == "<" and evidence.rise_ft < rule.threshold_ft:
        return ComplianceResult(rule.rule_id, EvaluationStatus.PASS, evidence.provenance_id, "hydraulic rise satisfies scoped criterion")
    return ComplianceResult(rule.rule_id, EvaluationStatus.FAIL, evidence.provenance_id, "hydraulic rise exceeds scoped criterion")
