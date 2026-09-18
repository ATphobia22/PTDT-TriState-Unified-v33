# Full-Stack AI Agent Template — PTDT Forensic Federation Map

**Source:** `ATphobia22/full-stack-ai-agent-template`
**Disposition:** WRAP / ADAPT — do not vendor the generator into PTDT.

## Why it matters

The repository is a production-oriented FastAPI + Next.js project generator with multiple AI-agent frameworks, RAG backends, WebSocket streaming, authentication, observability, Docker/Kubernetes deployment, and enterprise integrations. The source README documents PydanticAI, PydanticDeep, LangChain, LangGraph, DeepAgents, Milvus, Qdrant, pgvector, ChromaDB, JWT/OAuth, Celery, Docker, and Kubernetes. fileciteturn87file0L2-L2

## Capability disposition

| Capability | PTDT decision | Integration boundary |
|---|---|---|
| FastAPI layered backend | ADAPT | AI Governance / control-plane APIs |
| Next.js / React frontend patterns | ADAPT | Operator/admin UI; keep PTDT spatial visualization stack authoritative |
| PydanticAI | RETAIN | Preferred typed agent adapter |
| LangGraph | WRAP | Complex workflow/graph agent adapter |
| DeepAgents | WRAP | Delegated-agent adapter with strict tool permissions |
| PydanticDeep | WRAP | Coding/file-operation sandbox only |
| RAG | ADAPT | Evidence/document retrieval; retrieval is evidence input, not authority |
| WebSocket streaming | ADAPT | Agent execution/status streaming |
| JWT/OAuth/API-key patterns | ADAPT | Identity/access control under PTDT security architecture |
| Redis/Celery/background workers | ADAPT | Non-authoritative asynchronous jobs and media/evaluation workers |
| PostgreSQL | ADAPT | Control-plane metadata; scientific evidence remains governed by PTDT contracts |
| Observability | RETAIN | Logs, metrics, traces, agent-run diagnostics |
| Docker/Kubernetes | ADAPT | Isolated runtime deployment |
| Generator/CLI | DO NOT VENDOR | PTDT is an application/system, not a generic scaffold generator |

## Canonical PTDT agent architecture

```text
PTDT OPERATOR / API
        │
 Identity + Policy
        │
 Capability Router
        │
 ┌──────┼──────────┐
 ▼      ▼          ▼
PydanticAI LangGraph DeepAgents
 │      │          │
 └──────┼──────────┘
        ▼
 Tool Permission
        │
 Sandbox / Worker
        │
 ┌──────┼──────────┐
 ▼      ▼          ▼
RAG  Engineering  Media
     Tools         Tools
 │      │          │
 ▼      ▼          ▼
Evidence Validation SceneState
        │          │
        └────┬─────┘
             ▼
       Evidence Ledger
             │
       Promotion Gate
```

## Critical authority rule

The template's agent infrastructure is **control-plane technology**. It cannot become an engineering authority.

Agents may retrieve evidence, inspect results, propose changes, execute sandboxed tools, generate reports/media, and run tests. They may not directly promote unvalidated output into HEC-RAS, MODFLOW6, Bishop, EnKF, regulatory, Evidence Graph, or canonical SceneState authority.

## RAG integration

RAG should map into the existing Evidence Graph rather than create a parallel provenance universe. Retrieved material should carry source artifact ID, revision/hash, ingestion timestamp, document/chunk ID, retrieval query ID, embedding/model revision, retrieval score, access policy, and evidence status.

A retrieval result is an **evidence reference**, not automatically a validated fact.

## Agent execution contract

Adapt the stack to produce a PTDT `AgentExecutionRecord` containing:

- `agent_run_id`
- `agent_policy_version`
- `model_id` / `model_revision`
- `workspace_id`
- `requested_tools[]` / `approved_tools[]`
- `approval_events[]`
- `retrieved_evidence_ids[]`
- `input_artifact_ids[]`
- `mutated_artifact_ids[]`
- `test_results[]`
- `git_revision`
- `output_artifact_ids[]`
- `evidence_ids[]`
- `status`

## Security and reproducibility

The upstream project's recent changelog demonstrates the need for strict dependency compatibility gates: it records a `fastapi-pagination`/FastAPI incompatibility and a DeepAgents 0.7 API change that required a dependency cap. citeturn0search0

PTDT should therefore pin/lock agent frameworks, test supported configuration matrices, treat upgrades as compatibility events, scan generated code for secrets/unsafe defaults, keep sandbox permissions explicit, and prevent credentials from entering model context.

The template also documents MCP connections with encrypted tokens, OAuth 2.1/PKCE, multiple transports, per-server tool selection, and SSRF policy. These are useful patterns for PTDT's MCP boundary, but must be reimplemented under PTDT identity and authorization controls. citeturn0search0

Its secret-stripped generator manifest containing version, context hash, and generated configuration is a useful reproducibility pattern. Adapt this as an `AI_RUNTIME_MANIFEST.json` containing runtime schema, framework/version, model/backend revision, tools, policy, RAG/evaluation configuration, environment digest, timestamp, and context hash — never secrets. citeturn0search1

## Testing strategy

```text
Python compile → unit tests → agent contracts → tool permissions
→ RAG provenance → AI regression/evaluation → typecheck → build
→ security/dependency audit → Evidence integrity
```

## Cinematic integration

`Agent → SceneState proposal → validation → OpenUSD → WebGPU/Hydra → media worker`

Agents may orchestrate cinematic production, but generated imagery/video remains a derived artifact and cannot alter engineering truth.

## Final disposition

**WRAP / ADAPT.** Import architectural patterns and selected implementation ideas. Do not merge the upstream scaffold, dependency graph, generated project tree, or framework-specific application code into PTDT. Preserve PTDT's canonical Evidence Graph, Engineering State, SceneState, WebGPU, OpenUSD, and scientific-model authorities.
