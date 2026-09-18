# AI Agent / Multimodal Evaluation / Media Generation Federation Map

**Status:** Forensic federation analysis for `feature/ai-eval-agent-media-federation`.

## Executive disposition

The supplied repositories are useful primarily as **capability references, adapters, benchmarks, and local-AI orchestration patterns**. They must not become competing PTDT engineering authorities.

| Repository | Capability | Disposition | PTDT integration |
|---|---|---|---|
| `ATphobia22/operateGPT` | One-request multi-agent operations; LLM + image/video orchestration; embeddings | WRAP / REIMPLEMENT PATTERNS | Agent orchestration and content-production workflow patterns |
| `ATphobia22/lmms-eval` | Multimodal model evaluation; reproducibility; statistical evaluation; agentic tasks; video/audio I/O | RETAIN / ADAPT | AI Governance Plane, evaluation ledger, model regression gates |
| `ATphobia22/sdnext` | Image/video generation; quantization; balanced CPU/GPU offload; heterogeneous GPU backends | WRAP / OPTIONAL MEDIA WORKER | Cinematic asset generation only; isolated from engineering truth |
| `ATphobia22/locally-uncensored` | Local AI studio; coding agent; MCP; multi-backend routing; local RAG; image/video; permissions | REFERENCE / ADAPT | Local AI runtime architecture, permission model, offline media worker patterns |
| `ATphobia22/HiFox` | Repository contains only a minimal README title in the available source snapshot | AUDIT FIRST | No capability promoted without source evidence |

## Source-grounded findings

### OperateGPT

The supplied repository describes a multi-agent system that turns a single request into marketing copy, images, and videos, with support for local and proxied LLMs plus embedding models. fileciteturn74file0L2-L2

**Retain conceptually:** task decomposition, model/provider abstraction, multimodal artifact orchestration, embedding-backed retrieval, and one-request-to-multi-artifact workflows.

**Do not import directly:** historical provider configuration or credential patterns. The README uses an environment variable for an OpenAI key; PTDT must use its existing secret-management and least-privilege policy. fileciteturn74file0L2-L2

### LMMs-Eval

The supplied repository is the strongest addition to the PTDT AI Governance architecture. Its documented goals include reproducible evaluation, efficient large-scale evaluation, confidence intervals, clustered standard errors, paired comparisons, agentic task evaluation, video I/O optimization, safety/red-team baselines, token/throughput metrics, and structured multimodal chat messages. fileciteturn75file0L2-L2

**Promote these patterns into PTDT:**

1. Deterministic evaluation records
2. Benchmark manifests
3. Model/version/task identifiers
4. Confidence intervals and paired comparisons where statistically appropriate
5. Per-sample and run-level efficiency metrics
6. Multimodal evaluation contracts for text/image/video/audio
7. Agentic evaluation as a first-class test mode
8. Evaluation results linked to Evidence Graph records

The repository recommends `uv` and lockfile-based reproducible environments; PTDT should adopt the principle of locked reproducible environments without importing a second Python package-management authority into an existing runtime. fileciteturn75file0L2-L2

### SD.Next

The supplied SD.Next source describes an all-in-one image/video generation server and WebUI supporting many diffusion models and workflows, including text/image/video generation, image editing, enhancement, LoRA, ControlNet, upscaling and related media processing. It also documents SDNQ quantization, balanced CPU/GPU offload, multi-platform acceleration, and Docker deployment recipes. fileciteturn76file0L2-L2

**Useful PTDT capabilities:** quantized media-worker profiles, VRAM-aware model scheduling, CPU/GPU offload policy, heterogeneous GPU backend benchmarking, deterministic seed/model metadata for cinematic assets, and isolated image/video post-processing workers.

**Boundary:** generated imagery/video is a **presentation artifact**. It cannot alter hydraulic, groundwater, geotechnical, regulatory, or evidence state.

### Locally Uncensored

The supplied repository documents a local desktop AI studio combining chat, coding agents, image/video generation, local RAG, voice, MCP, multiple local backends, granular tool permissions, A/B model comparison, benchmarking, and remote access. fileciteturn77file0L2-L2

**Useful architecture patterns:** backend capability detection, OpenAI-compatible adapter boundaries, local/offline execution, explicit agent tool permissions, approval gates before mutation, coding-agent review-before-apply flow, per-project policy files, A/B model comparison, cost/correctness benchmark reporting, and model load/unload with VRAM-aware scheduling.

**Do not import the repository's “uncensored” policy as a PTDT policy.** PTDT agents remain subject to explicit safety, security, governance, authorization, and scientific-integrity controls.

### HiFox

The available `README.md` contains only the title `HiFox.ai`; the repository snapshot therefore does not support a substantive capability promotion. fileciteturn78file0L2-L2

**Disposition:** audit only.

## PTDT AI Governance integration

```text
                   AI / AGENT REQUEST
                           │
                    Policy + Identity
                           │
                    Capability Router
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
      Local LLM         Multimodal       Tool Agent
      backend           evaluator         runtime
          │                │                │
          └────────────────┼────────────────┘
                           ▼
                    Evaluation Harness
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
      Correctness       Safety          Efficiency
          │                │                │
          └────────────────┼────────────────┘
                           ▼
                    Evidence Ledger
                           │
                           ▼
                  Approved AI Artifact
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
       Engineering use             Cinematic use
       (strictly gated)            (media artifact)
```

## Canonical contracts to implement

### AI evaluation record

Every production AI evaluation should identify:

- `evaluation_id`
- `model_id`
- `model_revision`
- `provider/backend`
- `task_id`
- `dataset_id`
- `dataset_revision`
- `prompt/template_revision`
- `seed`
- `software_environment_digest`
- `hardware_profile`
- `metric_set`
- `confidence_interval`
- `paired_comparison_id` when applicable
- `input_artifact_ids[]`
- `output_artifact_ids[]`
- `evidence_ids[]`
- `status`

### Agent execution record

Every privileged agent run should identify:

- `agent_run_id`
- `agent_policy_version`
- `model_id`
- `workspace_id`
- `requested_tools[]`
- `approved_tools[]`
- `approval_events[]`
- `input_evidence_ids[]`
- `mutated_artifact_ids[]`
- `test_results[]`
- `git_revision`
- `output_evidence_ids[]`
- `status`

## Security boundary

AI-generated content and agent actions are **untrusted derived outputs until validated**.

1. No arbitrary agent write access to authoritative engineering databases.
2. No direct modification of Evidence Graph records by generated content.
3. Tool permissions must be explicit and least-privilege.
4. Repository mutation requires review/test gates.
5. Secrets remain outside prompts, model context, logs, and generated artifacts.
6. Media workers execute in isolated workspaces with resource quotas.
7. External model downloads require provenance and integrity verification.
8. Evaluation datasets are immutable/versioned evidence inputs.
9. Agent-generated engineering recommendations require validation before promotion.

## Cinematic integration

The strongest media-generation capabilities belong downstream of SceneState:

`EngineeringState -> SceneState -> OpenUSD -> Media/Render Worker -> Cinematic Artifact`

Every generated cinematic frame, image, video, caption, or narration must retain the SceneState/evidence lineage that produced it.

## Recommended implementation sequence

1. Add an `AIEvaluationRecord` schema and Evidence Graph adapter.
2. Add deterministic model/evaluation manifests.
3. Build multimodal evaluation runners for text/image/video/audio.
4. Add agentic evaluation mode and tool-permission tests.
5. Add local-backend capability discovery behind an adapter interface.
6. Add VRAM-aware media-worker scheduling and quantized-model benchmarking.
7. Add cinematic artifact provenance linking generated media to SceneState.
8. Audit `HiFox` source before assigning any runtime role.

## Non-goals

- Do not vendor entire AI studios into PTDT.
- Do not make a media-generation UI a scientific subsystem.
- Do not allow an LLM or image/video model to become an engineering authority.
- Do not copy provider secrets or unsafe credential patterns from source repositories.
- Do not replace the canonical Evidence Graph with an AI-specific provenance database.
