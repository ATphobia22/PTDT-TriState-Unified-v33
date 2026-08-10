# Hydraulic-Groundwater Authority Boundaries Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a production-safe MODFLOW6 execution boundary, controlled HEC-RAS-to-MODFLOW exchange, and explicit Archimedes regulatory authority boundaries without coupling numerical-model failures into PTDT state.

**Architecture:** Keep `engine/archimedes_engine.py` as the deterministic regulatory/constraint core. Add focused MODFLOW6 runner/exchange modules and a HEC-RAS exchange adapter under `engine/`; all model outputs carry provenance, units, datum, timestamp, scenario, and status. Failed numerical runs fail closed and retain the last valid state rather than fabricating or silently promoting data.

**Tech Stack:** Python 3, MODFLOW6 process execution, HEC-RAS exchange artifacts, dataclasses/typed dictionaries, pytest, existing TypeScript UI unchanged except for future integration hooks.

## Global Constraints

- Preserve locked project constants: BFE 375.0 ft NAVD88; LAG 377.2 ft; berm crest 379.8 ft; compensatory storage 1.20×.
- Archimedes is authoritative for deterministic regulatory elevation/storage checks only.
- HEC-RAS is authoritative for river hydraulics supplied to the exchange boundary.
- MODFLOW6 is authoritative for groundwater state only when a run completes and output validation succeeds.
- Failed, missing, corrupt, stale, or non-converged MODFLOW6 output must never be promoted as current groundwater state.
- Every cross-model value must retain units, datum, timestamp, scenario/run identifier, source model, status, and provenance.
- Do not add proprietary APIs or make the UI responsible for scientific-model authority decisions.
- Keep model coupling one-way per exchange artifact; no direct mutation of another model's internal state.
- Do not change the existing Archimedes formulas unless a test demonstrates a defect and the change is separately approved.

---

## File Map

### New files
- `engine/model_contracts.py` — shared typed contracts for status, provenance, model results, and exchange payloads.
- `engine/modflow6_runner.py` — subprocess execution, timeout, log capture, output validation, and failure classification.
- `engine/modflow6_exchange.py` — conversion of validated HEC-RAS boundary conditions into MODFLOW6 exchange inputs and validated MODFLOW results into PTDT groundwater observations.
- `engine/hec_ras_exchange.py` — HEC-RAS result normalization into the controlled exchange contract.
- `engine/authority.py` — explicit authority matrix and promotion rules for Archimedes, HEC-RAS, MODFLOW6, EnKF, and derived/display state.
- `tests/test_model_contracts.py` — contract serialization/status tests.
- `tests/test_modflow6_runner.py` — runner failure/success tests using a fake executable.
- `tests/test_modflow6_exchange.py` — exchange validation and promotion tests.
- `tests/test_hec_ras_exchange.py` — HEC-RAS normalization tests.
- `tests/test_authority.py` — authority-boundary tests.
- `docs/architecture/model-authority.md` — operator/developer documentation of authority boundaries and failure semantics.

### Existing files to modify
- `engine/archimedes_engine.py` — expose explicit regulatory authority metadata without moving hydraulic or groundwater responsibilities into Archimedes.
- `README.md` — document the new engine boundaries, failure behavior, and test commands.
- `requirements.txt` or project dependency manifest if present — add pytest only if the repository does not already provide a test dependency.

---

### Task 1: Establish shared model contracts

**Files:**
- Create: `engine/model_contracts.py`
- Test: `tests/test_model_contracts.py`

**Interfaces:**
- Produces `ModelStatus` with values `VALID`, `STALE`, `FAILED`, `INVALID`, `NOT_RUN`.
- Produces `FailureClass` with values `EXECUTABLE_MISSING`, `INPUT_INVALID`, `PROCESS_ERROR`, `TIMEOUT`, `CONVERGENCE_FAILURE`, `OUTPUT_MISSING`, `OUTPUT_INVALID`, `STALE_OUTPUT`.
- Produces `Provenance(source_model, run_id, scenario_id, timestamp_utc, datum, units)`.
- Produces `ModelRunResult(status, failure_class, exit_code, stdout, stderr, started_at_utc, finished_at_utc, output_path, provenance, diagnostics)`.
- Produces `ExchangePayload(values, provenance, status)`.

- [ ] **Step 1: Write failing contract tests**

```python
from datetime import datetime, timezone
from engine.model_contracts import ModelStatus, FailureClass, Provenance


def test_valid_provenance_is_serializable():
    p = Provenance(
        source_model="HEC-RAS",
        run_id="ras-001",
        scenario_id="base",
        timestamp_utc=datetime(2026, 8, 10, tzinfo=timezone.utc),
        datum="NAVD88",
        units="ft",
    )
    assert p.source_model == "HEC-RAS"
    assert p.datum == "NAVD88"
    assert p.units == "ft"


def test_failure_classes_are_distinct():
    assert FailureClass.TIMEOUT.value != FailureClass.CONVERGENCE_FAILURE.value
    assert ModelStatus.FAILED.value == "FAILED"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_model_contracts.py -v`
Expected: FAIL because `engine.model_contracts` does not yet exist.

- [ ] **Step 3: Implement the minimal typed contracts**

Use `dataclasses.dataclass` and `enum.Enum`; validate that `source_model`, `run_id`, `scenario_id`, `datum`, and `units` are non-empty and that timestamps are timezone-aware.

- [ ] **Step 4: Run the focused tests**

Run: `python -m pytest tests/test_model_contracts.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add engine/model_contracts.py tests/test_model_contracts.py
git commit -m "feat: add model provenance and status contracts"
```

---

### Task 2: Build the MODFLOW6 execution boundary

**Files:**
- Create: `engine/modflow6_runner.py`
- Test: `tests/test_modflow6_runner.py`

**Interfaces:**
- `Modflow6Runner(executable: str, timeout_seconds: float = 900.0)`
- `run(workdir: Path, namefile: Path, provenance: Provenance) -> ModelRunResult`
- `validate_outputs(workdir: Path, started_at_utc: datetime) -> tuple[bool, FailureClass | None, dict[str, object]]`

- [ ] **Step 1: Write failing tests for every required failure mode**

```python
from pathlib import Path
from engine.modflow6_runner import Modflow6Runner
from engine.model_contracts import FailureClass, ModelStatus, Provenance


def test_missing_executable_fails_closed(tmp_path):
    result = Modflow6Runner("definitely-missing-mf6").run(
        tmp_path, Path("model.nam"), _provenance()
    )
    assert result.status is ModelStatus.FAILED
    assert result.failure_class is FailureClass.EXECUTABLE_MISSING


def test_nonzero_exit_is_process_error(tmp_path):
    exe = tmp_path / "fake-mf6"
    exe.write_text("#!/bin/sh\necho boom >&2\nexit 7\n")
    exe.chmod(0o755)
    result = Modflow6Runner(str(exe)).run(tmp_path, Path("model.nam"), _provenance())
    assert result.status is ModelStatus.FAILED
    assert result.failure_class is FailureClass.PROCESS_ERROR
    assert result.exit_code == 7


def _provenance():
    from datetime import datetime, timezone
    return Provenance("MODFLOW6", "mf-001", "base", datetime.now(timezone.utc), "NAVD88", "ft")
```

- [ ] **Step 2: Add tests for timeout, missing output, stale output, and valid output**

The fake executable must sleep past the configured timeout for the timeout test. The valid-output test must create the expected output artifact after process completion; the stale-output test must pre-create an older artifact and verify it is rejected.

- [ ] **Step 3: Run tests and verify they fail**

Run: `python -m pytest tests/test_modflow6_runner.py -v`
Expected: FAIL because the runner does not exist.

- [ ] **Step 4: Implement subprocess isolation**

Use `subprocess.run` with an argument list rather than a shell string, capture stdout/stderr, apply the configured timeout, and classify `FileNotFoundError`, `TimeoutExpired`, nonzero exit, and output validation failures separately. Never treat an old output file as current.

- [ ] **Step 5: Implement convergence detection**

Parse the MODFLOW6 log for explicit convergence/error indicators. A process that exits successfully but reports solver non-convergence must return `ModelStatus.FAILED` with `FailureClass.CONVERGENCE_FAILURE`.

- [ ] **Step 6: Implement output freshness checks**

Require expected output files to exist and have modification times at or after the current run start. Missing files map to `OUTPUT_MISSING`; unreadable/malformed files map to `OUTPUT_INVALID`; pre-existing files not refreshed by the run map to `STALE_OUTPUT`.

- [ ] **Step 7: Run focused tests**

Run: `python -m pytest tests/test_modflow6_runner.py -v`
Expected: PASS for all execution/failure cases.

- [ ] **Step 8: Commit**

```bash
git add engine/modflow6_runner.py tests/test_modflow6_runner.py
git commit -m "feat: add fail-closed MODFLOW6 runner"
```

---

### Task 3: Normalize HEC-RAS boundary conditions

**Files:**
- Create: `engine/hec_ras_exchange.py`
- Test: `tests/test_hec_ras_exchange.py`

**Interfaces:**
- `HecRasBoundary(stage_ft: float, timestamp_utc: datetime, datum: str, river_id: str, run_id: str, scenario_id: str)`
- `normalize_hec_ras_boundary(payload: dict) -> HecRasBoundary`
- `to_exchange_payload(boundary: HecRasBoundary) -> ExchangePayload`

- [ ] **Step 1: Write failing tests**

```python
from datetime import datetime, timezone
from engine.hec_ras_exchange import normalize_hec_ras_boundary


def test_hec_ras_stage_requires_navd88():
    boundary = normalize_hec_ras_boundary({
        "stage_ft": 376.5,
        "timestamp_utc": "2026-08-10T00:00:00+00:00",
        "datum": "NAVD88",
        "river_id": "tri-county-mainstem",
        "run_id": "ras-001",
        "scenario_id": "base",
    })
    assert boundary.stage_ft == 376.5
    assert boundary.datum == "NAVD88"
```

- [ ] **Step 2: Add rejection tests for missing datum, units, timestamp, river ID, and non-numeric stage**

Each malformed payload must raise a deterministic `ValueError`; no implicit datum conversion is permitted in this adapter.

- [ ] **Step 3: Run tests to verify failure**

Run: `python -m pytest tests/test_hec_ras_exchange.py -v`
Expected: FAIL because the adapter does not exist.

- [ ] **Step 4: Implement normalization**

Normalize only already-declared HEC-RAS results. Preserve the source run/scenario and timestamp. Do not convert HEC-RAS hydraulics into groundwater values here.

- [ ] **Step 5: Run focused tests**

Run: `python -m pytest tests/test_hec_ras_exchange.py -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add engine/hec_ras_exchange.py tests/test_hec_ras_exchange.py
 git commit -m "feat: add HEC-RAS exchange boundary"
```

---

### Task 4: Implement HEC-RAS → MODFLOW6 exchange

**Files:**
- Create: `engine/modflow6_exchange.py`
- Test: `tests/test_modflow6_exchange.py`

**Interfaces:**
- `build_modflow_boundary(boundary: HecRasBoundary, target_cells: list[tuple[int, int]]) -> ExchangePayload`
- `promote_groundwater_result(result: ModelRunResult, heads: dict[tuple[int, int], float]) -> ExchangePayload`
- `require_valid_result(result: ModelRunResult) -> None`

- [ ] **Step 1: Write failing tests for successful boundary construction**

```python
def test_build_boundary_preserves_hec_ras_provenance():
    payload = build_modflow_boundary(_boundary(), [(1, 1), (1, 2)])
    assert payload.values["stage_ft"] == 376.5
    assert payload.values["target_cells"] == [(1, 1), (1, 2)]
    assert payload.provenance.source_model == "HEC-RAS"
```

- [ ] **Step 2: Write failing tests proving failed MODFLOW results cannot be promoted**

```python
def test_failed_modflow_result_cannot_be_promoted():
    result = ModelRunResult(..., status=ModelStatus.FAILED, ...)
    with pytest.raises(ValueError, match="not valid"):
        require_valid_result(result)
```

- [ ] **Step 3: Add datum/unit mismatch tests**

Reject HEC-RAS boundaries that are not explicitly in NAVD88/feet for this initial exchange contract; do not silently convert them.

- [ ] **Step 4: Implement controlled conversion**

Generate an exchange payload containing stage, target-cell mapping, source provenance, and an explicit exchange direction `HEC-RAS_TO_MODFLOW6`. The adapter must not mutate a MODFLOW package directly unless a later integration layer explicitly consumes this payload.

- [ ] **Step 5: Implement result promotion**

Only `ModelStatus.VALID` results can produce a current groundwater payload. `FAILED`, `INVALID`, `STALE`, and `NOT_RUN` results raise a deterministic promotion error.

- [ ] **Step 6: Run focused tests**

Run: `python -m pytest tests/test_modflow6_exchange.py -v`
Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add engine/modflow6_exchange.py tests/test_modflow6_exchange.py
git commit -m "feat: add controlled HEC-RAS to MODFLOW6 exchange"
```

---

### Task 5: Formalize authority boundaries

**Files:**
- Create: `engine/authority.py`
- Test: `tests/test_authority.py`
- Modify: `engine/archimedes_engine.py`

**Interfaces:**
- `AuthorityDomain` enum: `REGULATORY`, `RIVER_HYDRAULICS`, `GROUNDWATER`, `ASSIMILATION`, `DERIVED_DISPLAY`.
- `AUTHORITY_MATRIX` mapping source model to its allowed domain.
- `assert_authorized(source_model: str, domain: AuthorityDomain) -> None`
- `can_promote(status: ModelStatus, domain: AuthorityDomain) -> bool`

- [ ] **Step 1: Write failing authority tests**

```python
def test_archimedes_owns_regulatory_domain():
    assert_authorized("Archimedes", AuthorityDomain.REGULATORY)


def test_archimedes_cannot_claim_groundwater_authority():
    with pytest.raises(PermissionError):
        assert_authorized("Archimedes", AuthorityDomain.GROUNDWATER)


def test_failed_modflow_cannot_promote_groundwater():
    assert not can_promote(ModelStatus.FAILED, AuthorityDomain.GROUNDWATER)
```

- [ ] **Step 2: Run tests to verify failure**

Run: `python -m pytest tests/test_authority.py -v`
Expected: FAIL because the authority module does not exist.

- [ ] **Step 3: Implement the authority matrix**

Define exactly:

```python
AUTHORITY_MATRIX = {
    "Archimedes": {AuthorityDomain.REGULATORY},
    "HEC-RAS": {AuthorityDomain.RIVER_HYDRAULICS},
    "MODFLOW6": {AuthorityDomain.GROUNDWATER},
    "EnKF": {AuthorityDomain.ASSIMILATION},
    "PTDT": {AuthorityDomain.DERIVED_DISPLAY},
}
```

A model may publish observations into another subsystem through an exchange contract, but publication does not transfer authority.

- [ ] **Step 4: Add explicit Archimedes metadata**

Extend `ArchimedesEngine` with a read-only authority descriptor such as `authority_domains()` returning `{"REGULATORY"}`. Keep the existing BFE and storage calculations unchanged.

- [ ] **Step 5: Run focused tests**

Run: `python -m pytest tests/test_authority.py -v && python -m pytest -q`
Expected: PASS; existing Archimedes behavior remains unchanged.

- [ ] **Step 6: Commit**

```bash
git add engine/authority.py engine/archimedes_engine.py tests/test_authority.py
git commit -m "feat: formalize PTDT model authority boundaries"
```

---

### Task 6: Document the operational contract

**Files:**
- Create: `docs/architecture/model-authority.md`
- Modify: `README.md`

- [ ] **Step 1: Document the authority matrix**

Include the exact domains and prohibited authority transfers:

```text
Archimedes -> regulatory checks only
HEC-RAS    -> river hydraulics
MODFLOW6   -> groundwater
EnKF       -> assimilation
PTDT       -> orchestration/derived display
```

- [ ] **Step 2: Document failure semantics**

State that MODFLOW6 failure produces a failed run result, retains the last valid groundwater state, marks it stale, and prevents current-state promotion. Explicitly list executable, timeout, process, convergence, missing-output, invalid-output, and stale-output failures.

- [ ] **Step 3: Document exchange semantics**

Describe the HEC-RAS → MODFLOW6 direction, required datum/units, provenance fields, and the rule that adapters exchange immutable payloads rather than mutating another model's internal state.

- [ ] **Step 4: Update README**

Add the new modules and a test command:

```bash
python -m pytest -q
```

- [ ] **Step 5: Commit**

```bash
git add docs/architecture/model-authority.md README.md
git commit -m "docs: define model authority and failure semantics"
```

---

### Task 7: Full verification and integration gate

**Files:**
- Modify only if a failing integration test identifies a concrete defect.

- [ ] **Step 1: Run the complete Python test suite**

Run: `python -m pytest -q`
Expected: all tests pass.

- [ ] **Step 2: Run the Archimedes deterministic smoke test**

Run: `python engine/archimedes_engine.py`
Expected: `Engine Core Verified`.

- [ ] **Step 3: Verify fail-closed behavior manually with the fake MODFLOW executable**

Run the runner tests with the executable missing, a nonzero exit, a timeout, a convergence-failure log, a stale output, and a valid output. Confirm each status/failure class exactly matches the contract.

- [ ] **Step 4: Verify authority isolation**

Run: `python -m pytest tests/test_authority.py -v`
Expected: Archimedes cannot claim groundwater authority; HEC-RAS cannot claim groundwater authority; failed MODFLOW cannot promote current groundwater; only the designated domains pass authorization.

- [ ] **Step 5: Verify repository state**

Run:

```bash
git status --short
git log --oneline -10
```

Expected: only intentional implementation commits are present and no generated MODFLOW output, cache, or runtime artifact is tracked.

- [ ] **Step 6: Review against the original requirements**

Confirm all three approved requirements are covered: MODFLOW6 execution-failure handling, HEC-RAS → MODFLOW exchange, and explicit Archimedes authority boundaries.

- [ ] **Step 7: Commit any verified integration correction**

```bash
git add <only-corrected-files>
git commit -m "test: verify hydraulic-groundwater authority integration"
```

---

## Acceptance Criteria

1. A missing or failed MODFLOW6 executable cannot produce a `VALID` groundwater state.
2. A successful process with missing, malformed, stale, or non-converged output cannot produce a `VALID` groundwater state.
3. A prior valid groundwater result may remain available only as explicitly marked `STALE` after a subsequent failed run.
4. HEC-RAS stage data enters MODFLOW6 through a typed exchange payload carrying provenance, datum, units, timestamp, run ID, and scenario ID.
5. MODFLOW6 results can be promoted to current groundwater state only after successful execution and output validation.
6. Archimedes remains the authority for BFE/compensatory-storage regulatory checks and is explicitly prohibited from acting as the groundwater or river-hydraulic authority.
7. HEC-RAS remains authoritative for the river-hydraulic exchange input; MODFLOW6 remains authoritative for groundwater output.
8. Existing Archimedes deterministic behavior remains unchanged.
9. The full Python test suite passes.
10. No proprietary service is required for the new model-boundary layer.

## Self-Review

**Spec coverage:** MODFLOW6 failure handling is covered by Tasks 1–2 and 7; HEC-RAS → MODFLOW6 exchange is covered by Tasks 3–4 and 7; Archimedes authority boundaries are covered by Task 5 and documented in Task 6.

**Placeholder scan:** No `TBD`, `TODO`, or unspecified implementation step is required by this plan. Each task names concrete files, interfaces, tests, commands, and expected outcomes.

**Type consistency:** `ModelStatus`, `FailureClass`, `Provenance`, `ModelRunResult`, and `ExchangePayload` originate in Task 1 and are consumed by Tasks 2, 4, and 5. `HecRasBoundary` originates in Task 3 and is consumed by Task 4. Authority enums and promotion functions originate in Task 5 and are tested independently.
