# Storage Optimization and Quantum Toolset Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Reduce the PTDT ecosystem's storage footprint without sacrificing authoritative engineering data, provenance, reproducibility, or recoverability, while adding experimentally isolated quantum/quantum-inspired optimization benchmarks.

**Architecture:** The canonical repository remains `PTDT-TriState-Unified-v33`. A local forensic scanner inventories Git objects, working-tree artifacts, generated outputs, large files, archives, datasets, dependencies, and duplicates across the seven supplied repositories. A content-addressed artifact layer uses hashing, safe archive inspection, deterministic manifests, and configurable compression/externalization policies. Quantum components remain research-only and are evaluated against classical baselines before they can influence production decisions.

**Tech Stack:** Python 3.11+, Git plumbing, libarchive adapter, SHA-256/BLAKE3 where available, content-defined chunking, Zstandard where available, NumPy/SciPy optional numerical backend, FreeCAD/FreeMat adapters, Qiskit/Cirq-compatible optional research adapters, pytest.

## Global Constraints

- Never delete authoritative source data automatically.
- Never use lossy compression for authoritative observations or regulatory evidence.
- Every transformed artifact receives a content hash and provenance manifest.
- Quantum/quantum-inspired code is experimental and cannot mutate authoritative data.
- Large generated/build artifacts must be externalizable and reproducible.
- Repository history rewriting is a separately gated operation after measured inventory.
- Existing PTDT application behavior must remain unchanged until integration tests pass.

---

### Task 1: Add storage-forensics data model

**Files:**
- Create: `tools/storage_forensics/models.py`
- Create: `tests/storage_forensics/test_models.py`

**Interfaces:**
- Produces `ArtifactRecord`, `RepositoryInventory`, and `Classification` types consumed by scanner and reduction planning tasks.

- [ ] **Step 1: Write the failing test**

```python
from tools.storage_forensics.models import ArtifactRecord, Classification


def test_artifact_record_round_trip():
    record = ArtifactRecord(
        path="data/a.tif",
        size_bytes=123,
        sha256="abc",
        classification=Classification.AUTHORITATIVE,
    )
    assert record.path == "data/a.tif"
    assert record.classification.value == "authoritative"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/storage_forensics/test_models.py -v`
Expected: FAIL because the models do not yet exist.

- [ ] **Step 3: Implement the minimal typed dataclasses/enums**

Use frozen dataclasses, string-valued classifications (`authoritative`, `reconstructable`, `derived`, `dependency`, `generated`, `unknown`), and JSON-serializable fields for hashes, sizes, media types, source repository, CRS, vertical datum, and provenance references.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/storage_forensics/test_models.py -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/storage_forensics/models.py tests/storage_forensics/test_models.py
git commit -m "feat: add storage forensic data model"
```

### Task 2: Build repository and artifact scanner

**Files:**
- Create: `tools/storage_forensics/scanner.py`
- Create: `tests/storage_forensics/test_scanner.py`

**Interfaces:**
- `scan_repository(root: Path) -> RepositoryInventory`
- `classify_path(path: Path) -> Classification`
- `hash_file(path: Path) -> str`

- [ ] **Step 1: Write failing tests** for deterministic classification of `.git`, build directories, dependency directories, archives, GIS rasters, point clouds, source code, and unknown binaries.
- [ ] **Step 2: Run `pytest tests/storage_forensics/test_scanner.py -v` and confirm failure.**
- [ ] **Step 3: Implement streaming file hashing and directory classification without loading large files into memory.**
- [ ] **Step 4: Run the scanner tests and confirm PASS.**
- [ ] **Step 5: Commit `feat: add repository storage forensic scanner`.**

### Task 3: Add duplicate and content-defined chunk analysis

**Files:**
- Create: `tools/storage_forensics/dedup.py`
- Create: `tests/storage_forensics/test_dedup.py`

**Interfaces:**
- `find_duplicate_files(records) -> list[list[ArtifactRecord]]`
- `chunk_fingerprint(path, chunk_size=...) -> list[str]`
- `estimate_dedup_savings(records) -> int`

- [ ] **Step 1: Write tests using repeated files and repeated byte ranges.**
- [ ] **Step 2: Verify tests fail.**
- [ ] **Step 3: Implement exact-file hashing first; add optional content-defined chunking for large files.**
- [ ] **Step 4: Verify duplicate groups and savings calculations.**
- [ ] **Step 5: Commit `feat: add content-addressed dedup analysis`.**

### Task 4: Add archive inspection and deterministic packaging

**Files:**
- Create: `tools/archive/artifact_store.py`
- Create: `tools/archive/manifest.py`
- Create: `tests/archive/test_artifact_store.py`

**Interfaces:**
- `register_artifact(path, store_root) -> ArtifactRecord`
- `create_manifest(records) -> dict`
- `safe_extract(archive, destination) -> list[ArtifactRecord]`

- [ ] **Step 1: Write tests for hash-addressed storage, manifest generation, and path traversal rejection.**
- [ ] **Step 2: Verify failure.**
- [ ] **Step 3: Implement standard-library archive support and an optional libarchive backend when installed.**
- [ ] **Step 4: Verify exact byte-for-byte reconstruction from stored artifacts.**
- [ ] **Step 5: Commit `feat: add safe artifact archive layer`.**

### Task 5: Add compression benchmark and policy engine

**Files:**
- Create: `tools/storage_forensics/compression.py`
- Create: `tools/storage_forensics/policy.py`
- Create: `tests/storage_forensics/test_compression.py`
- Create: `tests/storage_forensics/test_policy.py`

**Interfaces:**
- `benchmark_compression(path) -> CompressionBenchmark`
- `compression_policy(record) -> CompressionPolicy`
- `verify_round_trip(original, compressed) -> bool`

- [ ] **Step 1: Test that authoritative data rejects lossy policies and reconstructable data permits configured lossless compression.**
- [ ] **Step 2: Verify failure.**
- [ ] **Step 3: Implement Zstandard as an optional backend with gzip fallback; record compression ratio and elapsed time.**
- [ ] **Step 4: Verify round trips and policy enforcement.**
- [ ] **Step 5: Commit `feat: add measured compression policies`.**

### Task 6: Add repository-wide storage report

**Files:**
- Create: `tools/storage_forensics/report.py`
- Create: `tools/storage_forensics/cli.py`
- Create: `tests/storage_forensics/test_report.py`

**Interfaces:**
- `build_report(inventories) -> dict`
- CLI commands: `scan`, `duplicates`, `compress-benchmark`, `report`

- [ ] **Step 1: Write report tests using synthetic repositories.**
- [ ] **Step 2: Verify failure.**
- [ ] **Step 3: Implement machine-readable JSON plus concise Markdown output.**
- [ ] **Step 4: Verify report contains top files, duplicate groups, category totals, estimated savings, and unsafe-to-delete warnings.**
- [ ] **Step 5: Commit `feat: add storage forensic reporting CLI`.**

### Task 7: Add scientific-state reduction interfaces

**Files:**
- Create: `tools/scientific_reduction/pca.py`
- Create: `tools/scientific_reduction/enkf_state.py`
- Create: `tests/scientific_reduction/test_pca.py`
- Create: `tests/scientific_reduction/test_enkf_state.py`

**Interfaces:**
- `fit_pca(matrix, variance_target=0.999) -> PCAResult`
- `compress_ensemble(state, variance_target=0.999) -> CompressedState`
- `reconstruct_state(compressed) -> ndarray`

- [ ] **Step 1: Write tests requiring reconstruction error below the configured threshold and preserving metadata.**
- [ ] **Step 2: Verify failure.**
- [ ] **Step 3: Implement classical NumPy/SciPy PCA/SVD as the production baseline.**
- [ ] **Step 4: Verify reconstruction and metadata preservation.**
- [ ] **Step 5: Commit `feat: add loss-bounded scientific state reduction`.**

### Task 8: Add quantum-inspired optimization research harness

**Files:**
- Create: `research/quantum_optimization/benchmark.py`
- Create: `research/quantum_optimization/chunking.py`
- Create: `tests/quantum_optimization/test_benchmark.py`
- Create: `docs/quantum/README.md`

**Interfaces:**
- `run_classical_baseline(problem) -> BenchmarkResult`
- `run_quantum_inspired(problem, seed) -> BenchmarkResult`
- `compare_results(baseline, candidate) -> ComparisonResult`

- [ ] **Step 1: Write tests proving deterministic seeded behavior and that a candidate cannot be marked production without matching exact reconstruction requirements.**
- [ ] **Step 2: Verify failure.**
- [ ] **Step 3: Implement a classical simulated-annealing/heuristic baseline and a quantum-inspired optimization interface with optional external quantum SDKs.**
- [ ] **Step 4: Verify benchmark output includes runtime, objective value, memory estimate, reconstruction correctness, and seed.**
- [ ] **Step 5: Commit `feat: add quantum-inspired optimization research harness`.**

### Task 9: Add optional quantum algorithm adapters

**Files:**
- Create: `research/quantum_optimization/qaoa_adapter.py`
- Create: `research/quantum_optimization/qae_adapter.py`
- Create: `tests/quantum_optimization/test_adapters.py`

**Interfaces:**
- `qaoa_optimize(problem, backend="simulator", seed=0) -> BenchmarkResult`
- `quantum_autoencoder_probe(matrix, backend="simulator", seed=0) -> BenchmarkResult`

- [ ] **Step 1: Write tests that skip cleanly when quantum SDKs are absent and never modify production artifacts.**
- [ ] **Step 2: Verify skip behavior.**
- [ ] **Step 3: Implement optional adapters only; keep all quantum dependencies out of the production dependency set.**
- [ ] **Step 4: Verify adapter isolation.**
- [ ] **Step 5: Commit `feat: isolate optional quantum algorithm adapters`.**

### Task 10: Add five-repository inventory configuration

**Files:**
- Create: `config/storage_repositories.json`
- Create: `docs/storage/REDUCTION_POLICY.md`
- Create: `docs/storage/REPOSITORY_INVENTORY.md`

Repositories:
- `ATphobia22/PTDT-TriState-Unified-v33`
- `ATphobia22/Tri-State-River-Valley-Engineering-System`
- `ATphobia22/Tri-County-River-Valley-Digital-Twin`
- `ATphobia22/PTDT-v33`
- `ATphobia22/Point-Township-Digital-Twin`
- `ATphobia22/libarchive`
- `ATphobia22/turbovec`

- [ ] **Step 1: Add canonical repository roles and non-destructive scan defaults.**
- [ ] **Step 2: Document authoritative/reconstructable/derived storage classes.**
- [ ] **Step 3: Document that no Git history rewrite occurs automatically.**
- [ ] **Step 4: Validate JSON and documentation links locally.**
- [ ] **Step 5: Commit `docs: define seven-repository storage reduction policy`.**

### Task 11: Add CI verification

**Files:**
- Create: `.github/workflows/storage-forensics.yml`

- [ ] **Step 1: Configure Python test execution and scanner unit tests.**
- [ ] **Step 2: Add a non-destructive repository-size report job.**
- [ ] **Step 3: Ensure CI does not upload raw engineering datasets or secrets.**
- [ ] **Step 4: Validate workflow YAML and test command locally where possible.**
- [ ] **Step 5: Commit `ci: add storage forensic verification`.**

### Task 12: Perform measured repository scan and generate reduction manifest

**Files:**
- Generated: `docs/storage/REDUCTION_MANIFEST.json`
- Generated: `docs/storage/REDUCTION_REPORT.md`

- [ ] **Step 1: Run the scanner against local clones of all seven repositories.**
- [ ] **Step 2: Compare exact duplicate hashes and chunk fingerprints.**
- [ ] **Step 3: Identify generated/build/dependency artifacts that are safe to regenerate.**
- [ ] **Step 4: Benchmark lossless compression on representative artifact classes.**
- [ ] **Step 5: Generate a proposed deletion/externalization manifest; do not delete anything automatically.**
- [ ] **Step 6: Run full tests and verify all retained artifact hashes.**
- [ ] **Step 7: Commit the measured manifest and report.**

### Task 13: Git-history compaction gate

**Files:**
- Create: `docs/storage/GIT_HISTORY_COMPACTION.md`

- [ ] **Step 1: Use Git object statistics to identify historical large blobs.**
- [ ] **Step 2: Map every candidate blob to current and historical references.**
- [ ] **Step 3: Exclude authoritative evidence and required reproducibility artifacts.**
- [ ] **Step 4: Produce a `git-filter-repo`/BFG migration script only after the inventory proves the candidates are disposable.**
- [ ] **Step 5: Require a separate explicit approval before force-updating any public branch.**

### Task 14: Benchmark turbovec as an optional acceleration backend

**Files:**
- Create: `tools/vector_backend/adapter.py`
- Create: `tests/vector_backend/test_adapter.py`
- Create: `docs/vector_backend/TURBOVEC_BENCHMARK.md`

- [ ] **Step 1: Define a backend-neutral vector interface.**
- [ ] **Step 2: Add NumPy reference implementation tests.**
- [ ] **Step 3: Add optional turbovec adapter with exact numerical comparison.**
- [ ] **Step 4: Benchmark only workloads where numerical equivalence is established.**
- [ ] **Step 5: Commit `feat: add optional turbovec vector backend`.**

### Task 15: Integrate provenance and evidence controls

**Files:**
- Create: `tools/provenance/artifact_provenance.py`
- Create: `tests/provenance/test_artifact_provenance.py`

- [ ] **Step 1: Test that transformed artifacts retain source hash, transformation, tool version, parameters, timestamp, CRS, vertical datum, and output hash.**
- [ ] **Step 2: Verify failure.**
- [ ] **Step 3: Implement signed/hashed manifest support without embedding secrets.**
- [ ] **Step 4: Verify provenance survives archive/compression/reconstruction workflows.**
- [ ] **Step 5: Commit `feat: preserve provenance across storage transformations`.**

### Task 16: Final validation and PR

**Files:**
- Modify: generated documentation only if validation discovers inconsistencies.

- [ ] **Step 1: Run all storage, scientific reduction, provenance, and quantum adapter tests.**
- [ ] **Step 2: Run static import/compile checks.**
- [ ] **Step 3: Run the complete non-destructive seven-repository scan.**
- [ ] **Step 4: Confirm no production code imports optional quantum SDKs unconditionally.**
- [ ] **Step 5: Confirm no authoritative artifact has been deleted or altered.**
- [ ] **Step 6: Open a draft PR from `feat/storage-optimization-quantum-toolset` into `main`.**
- [ ] **Step 7: Report measured savings only; never claim an 88-GB reduction until the scan provides the measured baseline.**
