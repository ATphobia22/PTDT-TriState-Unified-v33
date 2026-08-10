"""Shared contracts for model status, provenance, and cross-model exchanges."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class ModelStatus(str, Enum):
    VALID = "VALID"
    STALE = "STALE"
    FAILED = "FAILED"
    INVALID = "INVALID"
    NOT_RUN = "NOT_RUN"


class FailureClass(str, Enum):
    EXECUTABLE_MISSING = "EXECUTABLE_MISSING"
    INPUT_INVALID = "INPUT_INVALID"
    PROCESS_ERROR = "PROCESS_ERROR"
    TIMEOUT = "TIMEOUT"
    CONVERGENCE_FAILURE = "CONVERGENCE_FAILURE"
    OUTPUT_MISSING = "OUTPUT_MISSING"
    OUTPUT_INVALID = "OUTPUT_INVALID"
    STALE_OUTPUT = "STALE_OUTPUT"


@dataclass(frozen=True)
class Provenance:
    source_model: str
    run_id: str
    scenario_id: str
    timestamp_utc: datetime
    datum: str
    units: str

    def __post_init__(self) -> None:
        for name in ("source_model", "run_id", "scenario_id", "datum", "units"):
            if not getattr(self, name).strip():
                raise ValueError(f"{name} must be non-empty")
        if self.timestamp_utc.tzinfo is None:
            raise ValueError("timestamp_utc must be timezone-aware")


@dataclass(frozen=True)
class ModelRunResult:
    status: ModelStatus
    failure_class: FailureClass | None
    exit_code: int | None
    stdout: str
    stderr: str
    started_at_utc: datetime
    finished_at_utc: datetime
    output_path: str | None
    provenance: Provenance
    diagnostics: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExchangePayload:
    values: dict[str, Any]
    provenance: Provenance
    status: ModelStatus

    def __post_init__(self) -> None:
        if self.status is ModelStatus.VALID and self.provenance.timestamp_utc > datetime.now(timezone.utc):
            raise ValueError("valid exchange timestamp cannot be in the future")
