"""Explicit model-authority and promotion boundaries."""
from __future__ import annotations

from enum import Enum

from .model_contracts import ModelStatus


class AuthorityDomain(str, Enum):
    REGULATORY = "REGULATORY"
    RIVER_HYDRAULICS = "RIVER_HYDRAULICS"
    GROUNDWATER = "GROUNDWATER"
    ASSIMILATION = "ASSIMILATION"
    SLOPE_STABILITY = "SLOPE_STABILITY"
    DERIVED_DISPLAY = "DERIVED_DISPLAY"


AUTHORITY_MATRIX = {
    "Archimedes": {AuthorityDomain.REGULATORY},
    "HEC-RAS": {AuthorityDomain.RIVER_HYDRAULICS},
    "MODFLOW6": {AuthorityDomain.GROUNDWATER},
    "EnKF": {AuthorityDomain.ASSIMILATION},
    "Bishop": {AuthorityDomain.SLOPE_STABILITY},
    "PTDT": {AuthorityDomain.DERIVED_DISPLAY},
}


def assert_authorized(source_model: str, domain: AuthorityDomain) -> None:
    if domain not in AUTHORITY_MATRIX.get(source_model, set()):
        raise PermissionError(f"{source_model} is not authoritative for {domain.value}")


def can_promote(status: ModelStatus, domain: AuthorityDomain) -> bool:
    if status is not ModelStatus.VALID:
        return False
    return domain in {
        AuthorityDomain.REGULATORY,
        AuthorityDomain.RIVER_HYDRAULICS,
        AuthorityDomain.GROUNDWATER,
        AuthorityDomain.ASSIMILATION,
        AuthorityDomain.SLOPE_STABILITY,
    }
