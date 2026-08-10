# Expanded Repository Inventory — 2026-08-10

## Purpose

Track additional ATphobia22 repositories for the PTDT consolidation, storage-reduction, toolset, and quantum/AI research audit. These repositories are **source candidates**, not automatic merge targets.

## Repositories

| Repository | GitHub size metadata (KB) | Default branch | Initial role |
|---|---:|---|---|
| ATphobia22/cligit | 78,877 | trunk | CLI/tooling candidate; inspect for repository automation and Git workflows |
| ATphobia22/Qwen3.5-TurboQuant-MLX-LM | 134 | main | Quantization/MLX research candidate |
| ATphobia22/CopilotKit | 696,560 | main | Agent/copilot UI and orchestration candidate; high-priority size audit |
| ATphobia22/Imagina-AI | 101,520 | main | AI/media/model tooling candidate |
| ATphobia22/ml-bokeh | 83,057 | main | ML/visualization candidate |
| ATphobia22/Gravity | 4,180 | main | Specialized utility candidate |
| ATphobia22/cgru | 55,562 | master | Graphics/rendering pipeline candidate |
| ATphobia22/SwiftLM | 34,113 | main | Swift/LLM implementation candidate |
| ATphobia22/swift-package-manager | 40,983 | main | Swift build/package infrastructure candidate |
| ATphobia22/3D-Machine-Learning | 41,974 | master | 3D/ML candidate; high relevance to digital twin |
| ATphobia22/epsg.io | 122,502 | master | CRS/EPSG geospatial authority candidate |
| ATphobia22/context7 | 33,462 | master | Context/documentation tooling candidate |
| ATphobia22/ToolJet | 1,631,247 | develop | App/platform tooling candidate; **highest new repository size** |
| ATphobia22/awesome-copilot | 101,626 | main | Agent skill/prompt knowledge source |
| ATphobia22/awesome-seedance-2-prompts | 239,450 | main | Generative media prompt corpus; audit for large assets and duplication |
| ATphobia22/awesome-digital-twins | 46 | main | Digital-twin knowledge/reference corpus |
| ATphobia22/antigravity-awesome-skills | 57,656 | main | Agent skills/tooling candidate |
| ATphobia22/awesome-arcgis-developers | 385 | main | GIS developer reference corpus |

## Integration policy

1. Do not recursively merge these repositories into the canonical PTDT source tree.
2. Inventory source, Git history, generated artifacts, dependencies, binaries, models, datasets, and duplicated content first.
3. Assign each repository one of: `AUTHORITATIVE`, `IMPORT`, `ADAPTER`, `REFERENCE`, `EXPERIMENTAL`, `EXTERNAL`, or `EXCLUDE`.
4. Preserve licenses and upstream attribution.
5. Prefer adapters/submodules/content-addressed artifacts over vendoring large upstream trees.
6. Measure Git object storage separately from working-tree size.
7. Never delete authoritative engineering observations or source evidence solely to reduce size.

## Storage optimization priorities

The first targets for forensic inspection are `ToolJet`, `CopilotKit`, `awesome-seedance-2-prompts`, `epsg.io`, `cligit`, and `Imagina-AI` because their current GitHub size metadata is comparatively large.

For each repository, inspect:

- Git object database and historical blobs
- tracked binaries and archives
- generated/build/cache directories
- dependency/vendor trees
- model weights
- GIS datasets and tiles
- duplicate files and repeated datasets
- large historical blobs no longer present in HEAD

## PTDT relevance

- `epsg.io` can supply CRS/EPSG reference data and validation logic, but should not replace PROJ/GDAL authority without validation.
- `3D-Machine-Learning` can be evaluated for point-cloud/mesh/scene-learning workflows.
- `Qwen3.5-TurboQuant-MLX-LM` is relevant to model quantization and local inference experiments.
- `awesome-digital-twins` and `awesome-arcgis-developers` are reference corpora rather than production dependencies.
- `antigravity-awesome-skills` and `awesome-copilot` should be mined for reusable workflows/skills, not copied wholesale.
- `ToolJet` and `CopilotKit` should be evaluated primarily as optional UI/agent integration components.

## Quantum/optimization research

`Qwen3.5-TurboQuant-MLX-LM` and numerical/ML repositories are candidates for a separate experimental benchmark layer covering:

- quantization of derived ML state
- PCA/SVD and low-rank representations
- quantum-inspired clustering/chunking optimization
- QAOA-style combinatorial optimization experiments
- quantum-autoencoder research simulations

Quantum methods must remain experimental until they demonstrate exact reconstruction where lossless behavior is required and measurable improvement against strong classical baselines.

## Important size note

GitHub's repository `size` field is metadata expressed in KB and is not equivalent to the size of the complete Git object database or a local clone. A true 88-GB forensic result requires access to the complete repositories and Git object histories. This inventory therefore records GitHub-reported size metadata only and does not claim that the listed values represent total recoverable storage.
