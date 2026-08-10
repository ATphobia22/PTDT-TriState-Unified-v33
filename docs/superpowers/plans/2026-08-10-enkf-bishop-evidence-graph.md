# EnKF + Bishop Evidence Graph Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrate EnKF assimilation and Simplified Bishop slope stability as contract-bound model engines without bypassing existing authority/provenance semantics.

**Architecture:** Reuse `engine/model_contracts.py` for all provenance and exchange payloads. Register EnKF under `ASSIMILATION` and Bishop under `SLOPE_STABILITY`; keep PTDT under `DERIVED_DISPLAY`. Numerical engines fail closed and only valid results can be promoted.

**Tech Stack:** Python 3, dataclasses, existing model contracts, pytest; repository TypeScript/Vite build remains a required verification gate.

## Global Constraints

- Do not modify `main` during implementation.
- Preserve source model, run ID, scenario ID, UTC timestamp, datum, and units in every accepted exchange.
- Do not create a second provenance/evidence schema.
- Simplified Bishop is limited to circular slip surfaces and requires iterative solution.

---

### Task 1: EnKF engine

**Files:**
- Create: `engine/enkf_fusion.py`
- Test: `tests/test_enkf_bishop_evidence_graph.py`

- [x] Implement scalar `K=P/(P+R)` and analysis update.
- [x] Compute unbiased ensemble variance.
- [x] Emit `ExchangePayload` with `EnKF` provenance and `VALID` status.
- [x] Reject source-model provenance mismatches.

### Task 2: Bishop engine and authority boundary

**Files:**
- Create: `engine/bishop_slope.py`
- Modify: `engine/authority.py`
- Test: `tests/test_enkf_bishop_evidence_graph.py`

- [x] Implement iterative Simplified Bishop factor-of-safety calculation.
- [x] Add explicit pore-pressure input per slice.
- [x] Add `SLOPE_STABILITY` authority domain and register `Bishop`.
- [x] Emit contract-bound Bishop exchanges and reject PTDT provenance.

### Task 3: Verification

**Files:**
- Existing test suite and `package.json` scripts.

- [ ] Run the full Python test suite in an environment with repository dependencies.
- [ ] Run `npm run typecheck`.
- [ ] Run `npm run build`.
- [ ] Inspect branch diff against `main`.
- [ ] Check CI status for the resulting branch commit.
- [ ] Do not merge/push to `main` unless all required checks pass.
