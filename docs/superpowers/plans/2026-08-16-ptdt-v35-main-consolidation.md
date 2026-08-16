# PTDT v35 Main Consolidation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Consolidate the validated PTDT hydraulic, groundwater, EnKF/Bishop, evidence, cinematic/WebGPU, regulatory, spatial-streaming, clearance, security, and reporting capabilities into one production-oriented `main` branch without overwriting newer authoritative work already present on `main`.

**Architecture:** Treat `main` as the authoritative integration line. Existing branch work is imported selectively by file/commit lineage rather than blindly merging stale branch tips. The PTDT runtime is organized around canonical SceneState, provenance/evidence, hydraulic/groundwater analysis, geospatial transforms, WebGPU/MapLibre presentation, secure gRPC streaming, structural clearance analysis, and controlled evidence packaging.

**Tech Stack:** Python 3.12+, FastAPI, gRPC/Protobuf, Pydantic, NumPy, pyproj, Redis, HDF5/HEC-RAS adapters, TypeScript/React, MapLibre GL, WebGPU/WGSL, Three.js, OpenUSD test tooling, pytest/Vitest, GitHub Actions, cryptographic hashing/TLS, ReportLab, optional boto3/watchdog integration.

## Global Constraints

- `main` remains the authoritative branch and must retain its newer parcel/LOMA/LOMR-F/data-gate corrections.
- Do not silently fabricate missing authoritative telemetry, elevation, HEC-RAS, parcel, or neural data.
- EPSG:2966 engineering coordinates, NAVD88 elevations, WGS84 geographic coordinates, and EPSG:4978 ECEF must remain explicitly typed and datum-aware.
- RFC 8785 claims require an actual compliant canonicalization implementation, not merely `json.dumps(sort_keys=True)`.
- Synthetic/test data must be isolated behind explicit test fixtures and never presented as live evidence.
- Security credentials and private keys must never be committed to Git.
- Regulatory outputs must distinguish calculated engineering metrics from agency determinations.
- Performance claims must be benchmarked; no hard latency claim is accepted without measurements.
- Every new subsystem requires automated tests and CI integration before promotion to `main`.

---

### Task 1: Establish integration baseline and branch inventory

**Files:**
- Create: `docs/superpowers/plans/2026-08-16-ptdt-v35-main-consolidation.md`
- Inspect: `.github/workflows/*`, `engine/*`, `src/*`, `tests/*`, `docs/*`

**Interfaces:**
- Consumes: current `main` at `ab717d7c6cac1e9c6e20ae9825f36f4a98ce2104`.
- Produces: an integration branch anchored to current `main`, with a documented source-of-truth matrix.

- [ ] **Step 1: Record the current main SHA and branch heads.**

```text
main = ab717d7c6cac1e9c6e20ae9825f36f4a98ce2104
integration = integration/ptdt-v35-main-consolidation
```

- [ ] **Step 2: Compare candidate branches to `main`.**

Use GitHub commit comparison and retain only unique changes that are not already represented by `main`.

- [ ] **Step 3: Classify branch state.**

Classify each candidate as `already-integrated`, `superseded`, `selective-import`, or `requires-conflict-resolution`.

- [ ] **Step 4: Commit the baseline documentation.**

```bash
git add docs/superpowers/plans/2026-08-16-ptdt-v35-main-consolidation.md
git commit -m "docs: establish PTDT v35 consolidation plan"
```

---

### Task 2: Consolidate canonical evidence and authority graph

**Files:**
- Modify: `engine/evidence_graph_binding.py`
- Create/retain: `src/evidence/*`
- Modify: `engine/authority.py`
- Test: `tests/test_canonical_evidence_graph.py`
- Test: `tests/test_evidence_graph_binding.py`

**Interfaces:**
- Consumes: authority-tagged telemetry, parcel, regulatory, hydraulic, and model observations.
- Produces: deterministic evidence nodes with parent references, provenance identifiers, validation state, and cryptographic seals.

- [ ] **Step 1: Write tamper-detection tests.**

```python
def test_parent_or_payload_mutation_invalidates_node():
    node = make_test_node()
    assert node.verify_integrity()
    node.payload["value"] = "mutated"
    assert not node.verify_integrity()
```

- [ ] **Step 2: Add RFC 8785-compatible canonical serialization.**

Use a tested canonical JSON implementation or implement the RFC 8785 numeric/string rules explicitly; do not equate key sorting with RFC 8785 compliance.

- [ ] **Step 3: Enforce immutable parent linkage.**

Reject unknown parents, duplicate node identifiers, altered payload hashes, and cycles.

- [ ] **Step 4: Run evidence tests.**

```bash
pytest -q tests/test_canonical_evidence_graph.py tests/test_evidence_graph_binding.py
```

- [ ] **Step 5: Commit the evidence layer.**

```bash
git add engine/evidence_graph_binding.py engine/authority.py src/evidence tests/
git commit -m "feat: harden canonical evidence graph and provenance seals"
```

---

### Task 3: Consolidate hydraulic, groundwater, EnKF, and Bishop analysis

**Files:**
- Modify/Create: `engine/enkf_fusion.py`
- Modify/Create: `engine/bishop_slope.py`
- Modify: `engine/modflow6_runner.py`
- Modify: `engine/regulatory_rules.py`
- Test: `tests/test_enkf_bishop_evidence_graph.py`
- Test: existing hydraulic/groundwater tests

**Interfaces:**
- Consumes: validated observations and model state.
- Produces: typed hydraulic, groundwater, ensemble-fused, and slope-stability states linked to evidence nodes.

- [ ] **Step 1: Add deterministic EnKF tests.**

```python
def test_enkf_update_is_deterministic_for_fixed_seed():
    assert run_update(seed=42) == run_update(seed=42)
```

- [ ] **Step 2: Validate Bishop geometry and numerical boundaries.**

Reject invalid slices, zero denominators, non-finite material parameters, and impossible pore-pressure states.

- [ ] **Step 3: Preserve authority separation.**

Model results remain analytical outputs; regulatory rules consume those outputs but do not rewrite source observations.

- [ ] **Step 4: Run the complete engine test set.**

```bash
pytest -q tests/engine tests/test_enkf_bishop_evidence_graph.py
```

- [ ] **Step 5: Commit the engine consolidation.**

```bash
git add engine tests
 git commit -m "feat: consolidate hydraulic groundwater EnKF and Bishop engines"
```

---

### Task 4: Harden spatial transformation and neural depth processing

**Files:**
- Create: `engine/spatial_transform_bridge.py`
- Create: `engine/neural_depth_optimizer.py`
- Create: `tests/test_spatial_transform_bridge.py`
- Create: `tests/test_neural_depth_optimizer.py`

**Interfaces:**
- Consumes: explicitly typed CRS/datum coordinates and validated float32 depth buffers.
- Produces: WGS84/ECEF/engineering coordinate transforms and deterministic cleaned depth buffers.

- [ ] **Step 1: Test known geodetic conversion invariants.**

```python
def test_ecef_round_trip_preserves_coordinate_within_tolerance():
    ecef = bridge.wgs84_to_ecef(lon, lat, ellipsoid_height_m)
    lon2, lat2, h2 = bridge.ecef_to_wgs84(*ecef)
    assert abs(lon2 - lon) < 1e-9
    assert abs(lat2 - lat) < 1e-9
    assert abs(h2 - ellipsoid_height_m) < 1e-4
```

- [ ] **Step 2: Separate NAVD88 orthometric height from ellipsoidal height.**

Require an explicit geoid transformation/grid when converting NAVD88 heights to EPSG:4978; never multiply NAVD88 feet by `0.3048` and label the result ellipsoidal without correction.

- [ ] **Step 3: Implement Slippy tile boundary clamping.**

Clamp Web Mercator latitude to the valid projection range and validate zoom values.

- [ ] **Step 4: Make neural-buffer invalid input fail closed.**

Reject wrong-length, non-finite, or unsupported buffers rather than generating fabricated production values. Keep fixtures for synthetic 256x256 tests.

- [ ] **Step 5: Run spatial/neural tests.**

```bash
pytest -q tests/test_spatial_transform_bridge.py tests/test_neural_depth_optimizer.py
```

- [ ] **Step 6: Commit the transformation layer.**

```bash
git add engine/spatial_transform_bridge.py engine/neural_depth_optimizer.py tests/
git commit -m "feat: add datum-aware spatial and neural depth pipelines"
```

---

### Task 5: Add production structural-clearance analysis

**Files:**
- Create: `engine/clearance_analyzer.py`
- Create: `tests/test_clearance_analyzer.py`
- Modify: building ingestion/evidence adapters as required

**Interfaces:**
- Consumes: building record plus validated WSE NAVD88.
- Produces: immutable clearance manifest containing FFE, LAG, freeboard, threat classification, calculation provenance, and seal.

- [ ] **Step 1: Test normal and failure scenarios.**

```python
def test_clearance_calculation():
    result = analyzer.evaluate_node_clearance(record, current_wse_navd88=376.40)
    assert result.freeboard_ft == 6.10


def test_first_floor_submersion_is_failure():
    result = analyzer.evaluate_node_clearance(record, current_wse_navd88=383.10)
    assert result.statutory_compliance_pass is False
```

- [ ] **Step 2: Validate all numeric inputs as finite values.**

- [ ] **Step 3: Keep configurable engineering/regulatory thresholds separate from source observations.**

- [ ] **Step 4: Seal the manifest using the canonical evidence serializer.**

- [ ] **Step 5: Run tests.**

```bash
pytest -q tests/test_clearance_analyzer.py
```

- [ ] **Step 6: Commit.**

```bash
git add engine/clearance_analyzer.py tests/test_clearance_analyzer.py
git commit -m "feat: add deterministic structural clearance manifests"
```

---

### Task 6: Implement protobuf contract and secure streaming service

**Files:**
- Create: `proto/spatial_stream.proto`
- Create: `services/grpc_spatial_stream_server.py`
- Create: `services/grpc_spatial_stream_client.py`
- Create: `tests/test_grpc_spatial_stream.py`
- Modify: `requirements.txt` / `pyproject.toml`

**Interfaces:**
- Consumes: validated SceneState/evidence frames.
- Produces: protobuf `VoxelMatrixFrame` streams and ledger verification responses.

- [ ] **Step 1: Test protobuf serialization and schema compatibility.**

```python
def test_voxel_frame_round_trip():
    frame = make_frame()
    assert VoxelMatrixFrame.FromString(frame.SerializeToString()) == frame
```

- [ ] **Step 2: Remove synthetic streaming from production service.**

The server must read from a state provider interface. Test fixtures may provide synthetic frames.

- [ ] **Step 3: Add backpressure, cancellation, maximum message size, and bounded concurrency.**

- [ ] **Step 4: Implement ledger verification against the evidence registry rather than returning unconditional `True`.**

- [ ] **Step 5: Run gRPC tests.**

```bash
pytest -q tests/test_grpc_spatial_stream.py
```

- [ ] **Step 6: Commit.**

```bash
git add proto services tests pyproject.toml requirements.txt
 git commit -m "feat: add production protobuf spatial streaming service"
```

---

### Task 7: Implement certificate authority and mTLS correctly

**Files:**
- Create: `security/cert_provisioner.py`
- Create: `security/mtls_policy.py`
- Create: `tests/test_mtls_policy.py`
- Modify: gRPC server/client configuration
- Modify: `.gitignore`

**Interfaces:**
- Consumes: internal CA material supplied through secure deployment configuration.
- Produces: authenticated gRPC peer identities with certificate-chain validation and authorization policy.

- [ ] **Step 1: Test rejection of absent, expired, wrong-CA, and wrong-SAN client certificates.**

```python
def test_untrusted_client_is_rejected():
    assert authorize_peer(untrusted_peer) is False
```

- [ ] **Step 2: Build a CA hierarchy for test/deployment use.**

Use CA → server/client certificates with SANs. Do not use the server certificate as its own client-trust root.

- [ ] **Step 3: Remove certificate material from source control.**

```gitignore
build/certs/
*.key
*.pem
*.crt
```

- [ ] **Step 4: Configure gRPC client-certificate requirement.**

- [ ] **Step 5: Run security tests.**

```bash
pytest -q tests/test_mtls_policy.py
```

- [ ] **Step 6: Commit.**

```bash
git add security services .gitignore tests
 git commit -m "feat: enforce certificate-authorized gRPC mTLS"
```

---

### Task 8: Harden evidence packaging and controlled cloud archival

**Files:**
- Create: `services/fema_appeal_packager.py`
- Create: `services/s3_upload_trigger.py`
- Create: `tests/test_evidence_packaging.py`
- Modify: dependency configuration

**Interfaces:**
- Consumes: failed clearance manifests.
- Produces: deterministic evidence package containing manifest, report, package manifest, and SHA-256 hashes; optional configured object-storage upload.

- [ ] **Step 1: Test that passing manifests do not generate an appeal package.**

```python
def test_passing_manifest_is_not_packaged():
    assert packager.compile_fema_appeal_package(passing_manifest) is None
```

- [ ] **Step 2: Test failed-manifest package contents and hashes.**

- [ ] **Step 3: Fix ReportLab layout generation and deterministic metadata handling.**

- [ ] **Step 4: Replace filesystem `on_closed` dependence with a robust polling/debounce or explicit post-write handoff mechanism.**

- [ ] **Step 5: Require explicit AWS bucket, region, KMS key, and IAM configuration.**

- [ ] **Step 6: Never label an arbitrary S3 bucket a federal gateway without authoritative configuration.**

- [ ] **Step 7: Run packaging tests.**

```bash
pytest -q tests/test_evidence_packaging.py
```

- [ ] **Step 8: Commit.**

```bash
git add services tests pyproject.toml requirements.txt
 git commit -m "feat: add sealed evidence packaging and controlled archival"
```

---

### Task 9: Integrate canonical SceneState and WebGPU/MapLibre runtime

**Files:**
- Modify: `src/App.tsx`
- Modify: `src/map/*`
- Modify: `src/services/*`
- Modify: WebGPU pipeline modules
- Test: TypeScript/Vitest and WebGPU validation suites

**Interfaces:**
- Consumes: canonical SceneState and streamed hydraulic/depth frames.
- Produces: synchronized 3D MapLibre/Three.js/WebGPU visualization.

- [ ] **Step 1: Preserve the newer `main` parcel/LOMA data gates.**

- [ ] **Step 2: Connect hydraulic WSE and building clearance layers to SceneState.**

- [ ] **Step 3: Validate all WebGPU buffer types and WGSL bindings.**

- [ ] **Step 4: Run frontend tests and type checks.**

```bash
npm test -- --run
npm run typecheck
```

- [ ] **Step 5: Run shader validation.**

```bash
npm run test:webgpu
```

- [ ] **Step 6: Commit.**

```bash
git add src tests package.json package-lock.json
 git commit -m "feat: integrate canonical SceneState with WebGPU MapLibre runtime"
```

---

### Task 10: Integrate OpenUSD and cinematic round-trip validation

**Files:**
- Modify: existing OpenUSD adapters/scripts discovered during branch inventory
- Create/modify: `tests/test_openusd_roundtrip.*`

**Interfaces:**
- Consumes: canonical scene/building/terrain state.
- Produces: deterministic OpenUSD scene representation that round-trips without loss of authoritative identifiers.

- [ ] **Step 1: Test export/import of a minimal authoritative scene.**

```python
def test_openusd_round_trip_preserves_authoritative_ids():
    exported = export_scene(scene)
    restored = import_scene(exported)
    assert restored.authoritative_ids == scene.authoritative_ids
```

- [ ] **Step 2: Validate units, coordinate systems, and metadata.**

- [ ] **Step 3: Run round-trip tests.**

```bash
pytest -q tests/test_openusd_roundtrip.py
```

- [ ] **Step 4: Commit.**

```bash
git add tests scripts src
 git commit -m "test: validate OpenUSD scene round trips"
```

---

### Task 11: Security, dependency, CI, and performance gates

**Files:**
- Modify: `.github/workflows/*`
- Modify: dependency manifests/lockfiles
- Create: `tests/performance/test_stream_benchmark.py`
- Create: security audit configuration as appropriate

**Interfaces:**
- Consumes: the consolidated application.
- Produces: repeatable CI evidence for correctness, security, type safety, shader validation, and measured streaming performance.

- [ ] **Step 1: Run Python test suite.**

```bash
pytest -q
```

- [ ] **Step 2: Run TypeScript checks/tests.**

```bash
npm ci
npm run typecheck
npm test -- --run
```

- [ ] **Step 3: Run dependency/security audit.**

```bash
npm audit --audit-level=high
python -m pip_audit
```

- [ ] **Step 4: Benchmark gRPC frame serialization and end-to-end streaming.**

Record p50/p95/p99 latency, throughput, CPU, and memory. Do not assert `<2 ms` unless the measured p95 satisfies it under a documented benchmark environment.

- [ ] **Step 5: Run all CI workflows.**

- [ ] **Step 6: Commit CI hardening.**

```bash
git add .github tests package.json package-lock.json pyproject.toml requirements*.txt
 git commit -m "ci: add production validation security and performance gates"
```

---

### Task 12: Promote validated integration to `main`

**Files:**
- No new application files; Git ref promotion and verification.

**Interfaces:**
- Consumes: validated integration branch.
- Produces: canonical `main` containing all approved, non-duplicated functionality.

- [ ] **Step 1: Verify integration branch status and CI.**

```text
Expected: all required checks PASS; no unresolved merge conflicts; no secrets detected.
```

- [ ] **Step 2: Compare integration branch with current `main`.**

- [ ] **Step 3: Create a merge commit or fast-forward only when all checks pass.**

```bash
git checkout main
git merge --no-ff integration/ptdt-v35-main-consolidation
```

- [ ] **Step 4: Push the validated result to `main`.**

```bash
git push origin main
```

- [ ] **Step 5: Verify the resulting `main` SHA and combined CI status.**

- [ ] **Step 6: Document exactly which branches were incorporated, already integrated, superseded, or intentionally excluded.**

```bash
git add docs/superpowers
 git commit -m "docs: record PTDT v35 consolidation provenance"
```
