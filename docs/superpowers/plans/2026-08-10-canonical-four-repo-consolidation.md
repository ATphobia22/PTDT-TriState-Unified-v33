# Canonical Four-Repository Consolidation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (inline execution is authorized for this session). Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Consolidate PTDT-v33, Tri-State-River-Valley-Engineering-System, and Tri-County-River-Valley-Digital-Twin into PTDT-TriState-Unified-v33 as one deduplicated, provenance-preserving engineering digital twin, with one Evidence Graph, one authority per scientific domain, connected Layer 19 buildings, regulatory evaluation, and verified CI/build wiring.

**Architecture:** PTDT-TriState-Unified-v33 remains the canonical repository. The authoritative Evidence Graph implementation from Tri-County-River-Valley-Digital-Twin becomes the canonical provenance layer; PTDT model contracts become the model-exchange boundary; HEC-RAS, MODFLOW6, EnKF, Bishop, and Archimedes retain explicit domain authority; MapLibre/WebGPU/HUD consume derived Evidence Graph records and cannot originate engineering or legal conclusions.

**Tech Stack:** Python model engines and tests; TypeScript/React; Vite; MapLibre GL; Three.js/WebGPU; existing PTDT contracts; Evidence Graph provenance records; GitHub Actions; npm/TypeScript build; pytest where present.

## Global Constraints

- Do not modify `main` until the complete consolidation branch passes repository-wide verification.
- Do not create a second Evidence Graph schema or duplicate provenance hashing logic.
- Derived evidence must preserve `parent_ids`, source record identity, timestamps, CRS/datum, units, status, and payload integrity.
- USGS observations remain authoritative observations; EnKF outputs are derived assimilation records and must never overwrite observations.
- Visualization is read-only with respect to engineering/regulatory authority.
- Building geometry/MapLibre state must never be used as the source of a regulatory conclusion.
- Regulatory rules must be versioned and scoped to their actual jurisdiction/provision; project-local constants cannot become universal legal rules.
- Every retained scientific implementation must have deterministic tests covering units, provenance, failure behavior, and numerical expectations.
- No duplicate authority implementation may remain active after consolidation.

---

### Task 1: Establish the consolidation inventory

**Files:**
- Create: `docs/architecture/CANONICAL_REPOSITORY_MANIFEST.md`
- Create: `docs/architecture/CANONICAL_AUTHORITY_MATRIX.md`
- Create: `docs/architecture/CANONICAL_DATA_FLOW.md`

**Inputs:**
- `ATphobia22/PTDT-TriState-Unified-v33` at canonical `main` commit `f9735d4824e3162efd25362b718bf179acd05b34`
- `ATphobia22/PTDT-v33`
- `ATphobia22/Tri-State-River-Valley-Engineering-System`
- `ATphobia22/Tri-County-River-Valley-Digital-Twin`

- [ ] Enumerate source modules for Evidence Graph, model contracts, EnKF, Bishop, Archimedes, HEC-RAS, MODFLOW6, buildings, GIS, HUD, regulatory rules, APIs, tests, and CI.
- [ ] Record each overlapping implementation as `KEEP`, `MERGE`, `ADAPT`, `DEPRECATE`, or `DELETE` with an authority-based reason.
- [ ] Record source commit SHA and destination path for every imported authoritative module.
- [ ] Verify that the inventory contains exactly one active authority for each domain.
- [ ] Commit the inventory to the consolidation branch.

### Task 2: Import the authoritative Evidence Graph

**Files:**
- Create/merge: `src/evidence/evidence_graph.py`
- Create/merge: `src/evidence/source_adapters.py`
- Create/merge: `src/evidence/usgs_semantics.py`
- Create/merge: `src/evidence/archimedes_authority.py`
- Create/merge: `src/evidence/__init__.py`
- Create/merge: `docs/architecture/AUTHORITATIVE_EVIDENCE_GRAPH.md`
- Test: `tests/test_evidence_graph.py`

**Interfaces:**
- Produces canonical provenance record creation, parent-link validation, hashing, and source/derived semantics for all later model adapters.

- [ ] Port the Tri-County Evidence Graph implementation without preserving a competing PTDT provenance implementation.
- [ ] Adapt imports to the canonical repository package layout.
- [ ] Preserve provenance IDs, source record IDs, role, authority, timestamps, spatial reference, datum, units, payload hash, and `parent_ids`.
- [ ] Preserve the read-only consumer boundary for visualization.
- [ ] Run the Evidence Graph tests before continuing.
- [ ] Commit the canonical Evidence Graph import.

### Task 3: Bind model contracts to the canonical Evidence Graph

**Files:**
- Modify: `engine/model_contracts.py`
- Modify: `engine/evidence_graph_binding.py`
- Modify: `engine/authority.py`
- Test: `tests/test_enkf_bishop_evidence_graph.py`
- Test: `tests/test_evidence_graph_model_contracts.py`

**Interfaces:**
- `ExchangePayload` remains the model-exchange envelope.
- Evidence Graph records become the authoritative lineage records behind derived payloads.

- [ ] Replace any duplicate provenance implementation with adapters to the canonical Evidence Graph.
- [ ] Require valid parent evidence for derived EnKF/Bishop results.
- [ ] Reject missing, stale, invalid, incompatible-datum, and incompatible-unit evidence before promotion.
- [ ] Ensure `ModelStatus` is preserved through Evidence Graph registration.
- [ ] Verify authority domains remain distinct.
- [ ] Run the model-contract tests.
- [ ] Commit the binding.

### Task 4: Consolidate scientific model authorities

**Files:**
- Modify/create: `engine/enkf_fusion.py`
- Modify/create: `engine/bishop_slope.py`
- Existing HEC-RAS/MODFLOW6 engine modules discovered in Task 1
- Existing Archimedes authority module discovered in Task 1
- Tests adjacent to each retained engine

- [ ] Keep one EnKF implementation and map its inputs to canonical Evidence Graph parent IDs.
- [ ] Keep one Bishop implementation using the verified Simplified Bishop formulation and convergence criteria.
- [ ] Keep HEC-RAS as hydraulic authority and MODFLOW6 as groundwater authority.
- [ ] Keep Archimedes as independent engineering-calculation authority where applicable.
- [ ] Remove or quarantine duplicate implementations after callers are rewired.
- [ ] Add cross-model provenance tests: HEC-RAS/MODFLOW6/USGS → EnKF → derived evidence and hydraulic/geotechnical evidence → Bishop → derived evidence.
- [ ] Run all scientific unit tests.
- [ ] Commit the scientific consolidation.

### Task 5: Consolidate Layer 19 Buildings / Structural Context

**Files:**
- Create: `src/services/buildingsService.ts`
- Modify: `src/services/gisService.ts`
- Modify: existing MapLibre map component discovered in the canonical repository
- Create: `src/services/buildingEvidenceService.ts`
- Create: `src/services/buildingRelationships.ts`
- Create: Layer 19 HUD/controller module in the canonical UI path
- Test: `tests/buildings*` and TypeScript tests available in the canonical project

**Interfaces:**
- `normalizeBuildingHeight(feature): number` returns canonical meters for rendering only.
- Building evidence records carry original value/unit, normalized value, normalization method, source identity, datum, and parent provenance.
- Terrain/BFE relationship functions consume Evidence Graph records, not rendered geometry.

- [ ] Import the authoritative building-footprint implementation from `src/services/buildingsService.ts` in the Engineering System repository.
- [ ] Preserve local forensic, Microsoft USBuildingFootprints, and Overture source priority only where source authority and provenance are explicit.
- [ ] Make height normalization deterministic and record the transformation method.
- [ ] Wire `fill-extrusion`, outline, opacity, height scale, and primary-building styling into Layer 19.
- [ ] Wire Layer 19 HUD controls to the actual map state rather than a disconnected demo state.
- [ ] Implement building-to-terrain and building-to-BFE calculations as derived evidence records with parent IDs and datum checks.
- [ ] Ensure MapLibre cannot be read by the compliance subsystem as an engineering data source.
- [ ] Add tests for height units, explicit 7.2 m structures, fallback behavior, datum mismatch, and provenance lineage.
- [ ] Commit Layer 19 integration.

### Task 6: Consolidate regulatory evidence and compliance evaluation

**Files:**
- Create/merge: `src/compliance/` canonical rule/evaluation modules
- Import/adapt: existing regulatory evidence manifests and rule sources from Engineering System
- Test: `tests/compliance/`
- Create: `docs/regulatory/verified-rule-sources.md`

- [ ] Represent Illinois, Indiana, and Kentucky rules as versioned, jurisdiction-scoped evidence records.
- [ ] Verify the actual current official text and applicability for each retained threshold before encoding it.
- [ ] Remove universal constants that incorrectly generalize floodway, no-rise, surcharge, freeboard, or permit-specific criteria.
- [ ] Make the compliance governor consume only validated Evidence Graph model results.
- [ ] Return `NOT_EVALUATED` when authoritative evidence or applicable rule scope is missing.
- [ ] Preserve model-run and rule provenance in every compliance result.
- [ ] Add tests proving that MapLibre geometry alone cannot generate a compliance result.
- [ ] Commit regulatory consolidation.

### Task 7: Consolidate application, GIS, HUD, and visualization wiring

**Files:**
- Modify: `src/services/gisService.ts`
- Modify: canonical map component
- Modify: canonical HUD/control components
- Modify: API/service adapters identified in the inventory
- Modify: `src/integration/RuntimeTwinContext.ts` where retained

- [ ] Rewire frontend consumers to request PTDT state and Evidence Graph projections rather than raw duplicated model outputs.
- [ ] Connect Layer 19 visibility, opacity, height scale, jurisdiction, and evidence indicators to live application state.
- [ ] Preserve MapLibre/Three.js/WebGPU visualization roles as consumers.
- [ ] Remove duplicate rendering pipelines that produce conflicting building or hydraulic state.
- [ ] Verify end-to-end evidence-to-HUD traceability.
- [ ] Commit application wiring.

### Task 8: Consolidate CI and release workflows

**Files:**
- Create/modify: `.github/workflows/ci.yml`
- Create/modify: `.github/workflows/evidence-graph.yml`
- Create/modify: `.github/workflows/integration.yml`
- Modify: `package.json`
- Modify: `package-lock.json` if dependency state requires it
- Create/modify: `pytest.ini` or `pyproject.toml` only if the canonical Python test layout requires it

- [ ] Create one canonical CI workflow covering Python tests, Evidence Graph integrity, TypeScript typecheck, and Vite build.
- [ ] Add cross-domain integration tests to the same CI gate.
- [ ] Fail CI on provenance gaps, duplicate authorities, stale evidence promotion, datum/unit mismatch, and frontend build failure.
- [ ] Use deterministic dependency installation and make lockfile state consistent with `package.json`.
- [ ] Ensure workflows run on pull requests and pushes to the consolidation branch/main.
- [ ] Commit CI consolidation.

### Task 9: Four-source forensic rescan after consolidation

**Files:**
- Modify: `docs/architecture/CANONICAL_REPOSITORY_MANIFEST.md`
- Create: `docs/verification/POST_CONSOLIDATION_FORENSIC_AUDIT.md`

- [ ] Search the consolidated tree for duplicate Evidence Graph/provenance classes.
- [ ] Search for duplicate EnKF, Bishop, HEC-RAS, MODFLOW6, Archimedes, building, and compliance implementations.
- [ ] Search for hard-coded regulatory thresholds and verify each retained occurrence is linked to a versioned rule source.
- [ ] Search for direct UI-to-regulatory or UI-to-authority access paths.
- [ ] Search for unit/datum conversion heuristics that are not recorded as transformations.
- [ ] Search for stale repository names/imports from the three source repositories.
- [ ] Search for dead branches of code and unreachable feature flags.
- [ ] Document every discrepancy found and its disposition.
- [ ] Commit the forensic audit.

### Task 10: Full verification and release gate

**Files:**
- No source changes unless a verification failure identifies a concrete defect.

- [ ] Run the complete Python test suite.
- [ ] Run Evidence Graph integrity tests.
- [ ] Run EnKF numerical verification.
- [ ] Run Bishop numerical/convergence verification.
- [ ] Run building/terrain/BFE lineage tests.
- [ ] Run regulatory evaluation tests.
- [ ] Run TypeScript `npm run typecheck`.
- [ ] Run `npm run build`.
- [ ] Run the complete GitHub Actions workflow and verify every required job is successful.
- [ ] Compare consolidation branch against canonical `main` and confirm only intended files changed.
- [ ] Confirm all four source repositories remain untouched by the consolidation process.
- [ ] Do not merge to `main` until all required checks are green.
- [ ] Create the final pull request with the authority matrix, manifest, forensic audit, and CI results attached.
