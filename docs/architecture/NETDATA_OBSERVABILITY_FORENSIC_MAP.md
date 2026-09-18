# Netdata Observability — PTDT Federation Map

**Source:** `ATphobia22/netdata`
**Disposition:** **WRAP / ADAPT** — do not vendor Netdata as the canonical PTDT telemetry authority.

## Source-grounded capability assessment

The supplied repository describes Netdata as an open-source, real-time infrastructure monitoring platform with per-second collection/visualization, ML-powered anomaly detection, low-resource operation, distributed/edge processing, local data retention, alerts, streaming, and broad infrastructure/application collectors. fileciteturn89file0L2-L2

The README documents monitoring of system resources, storage, networking, hardware/sensors including GPUs, processes, logs, containers, VMs, synthetic checks, packaged applications, cloud infrastructure, and custom applications. It also documents parent-child centralization, alerts, long-term retention, and local/edge operation. fileciteturn89file0L2-L2

## PTDT disposition matrix

| Capability | Decision | PTDT role |
|---|---|---|
| Per-second infrastructure metrics | **RETAIN / WRAP** | Runtime telemetry for compute, storage, network and service health |
| GPU/CPU/memory monitoring | **RETAIN / WRAP** | WebGPU/native GPU/AI worker capacity and performance telemetry |
| Hardware/sensor monitoring | **RETAIN / WRAP** | Node health and operational diagnostics |
| Container/Kubernetes monitoring | **RETAIN / WRAP** | Runtime fleet observability |
| Application/database monitoring | **RETAIN / WRAP** | API, GIS, simulation, agent and worker health |
| Synthetic checks | **RETAIN / ADAPT** | Endpoint/service health probes |
| ML anomaly detection | **ADAPT** | Operational anomaly signal; never scientific truth |
| Alerts | **RETAIN / ADAPT** | SRE/operations alerting and escalation |
| Parent/child streaming | **ADAPT** | Distributed node telemetry aggregation |
| Long-term metrics retention | **ADAPT** | Operational history; separate from immutable Evidence Ledger |
| Netdata UI | **REFERENCE / OPTIONAL** | Operational dashboard only; PTDT visualization remains canonical |
| Netdata Cloud | **OPTIONAL / EXTERNAL** | Do not make it a required dependency for sovereign/offline PTDT deployments |
| Netdata Agent | **WRAP** | Node-level collector/monitoring worker |

## Critical authority separation

Netdata telemetry is **operational evidence**, not engineering-model authority.

```text
Infrastructure / Runtime
        │
        ▼
   Netdata telemetry
        │
   ┌────┴─────────────┐
   │                  │
Operational        Engineering
observability      evidence
   │                  │
   ▼                  ▼
SRE alerts       Evidence Graph
   │                  │
   └────────┬─────────┘
            ▼
      PTDT Operations
```

A Netdata anomaly or metric may indicate that a node, GPU, service, worker, storage subsystem, or network path is unhealthy. It **must not** directly modify HEC-RAS, MODFLOW6, Bishop, EnKF, regulatory, or authoritative geospatial state.

## Engineering integration

### 1. Simulation runtime

Instrument:

- HEC-RAS worker CPU/memory/runtime
- MODFLOW6 process lifecycle and runtime
- Bishop calculation workers
- EnKF assimilation cycles
- I/O throughput
- solver queue latency
- failed/retried jobs
- artifact publication latency

### 2. GPU/WebGPU pipeline

Instrument:

- GPU utilization
- GPU memory pressure
- compute worker queue depth
- shader/dispatch timing
- frame latency
- upload/download bandwidth
- resource creation failures
- device-loss events
- WebGPU worker health

**Important:** browser WebGPU metrics and host-level GPU metrics are complementary. Netdata cannot substitute for GPU timestamp instrumentation inside the rendering/compute pipeline.

### 3. AI Agent Plane

Instrument:

- model worker utilization
- inference latency
- tokens/sec where available
- queue depth
- VRAM utilization
- model load/unload time
- RAG latency
- vector database latency
- tool execution latency
- failed tool calls
- agent-run duration
- evaluation worker resource consumption

These metrics feed the AI Governance operational layer but do not determine model correctness. Correctness remains governed by the evaluation framework and Evidence Ledger.

### 4. Cinematic/OpenUSD pipeline

Instrument:

- OpenUSD conversion latency
- scene generation queue depth
- asset loading latency
- texture processing time
- render-worker utilization
- media encoding throughput
- failed artifact generation
- storage pressure
- GPU memory pressure

## Telemetry-to-Evidence boundary

Operational metrics should be bridged into the Evidence Graph only when they materially support a reproducibility or audit claim.

Recommended record lineage:

```text
Netdata metric sample
       ↓
telemetry snapshot ID
       ↓
runtime event / execution record
       ↓
artifact or model run
       ↓
Evidence Graph reference
```

Do **not** copy every per-second operational sample into the immutable Evidence Ledger. Maintain high-frequency telemetry in the observability system and create evidence-bearing snapshots/aggregates when required.

## New operational contract

Recommended `RuntimeTelemetrySnapshot`:

- `snapshot_id`
- `node_id`
- `service_id`
- `component`
- `timestamp`
- `metric_set`
- `collector_version`
- `telemetry_source`
- `aggregation_window`
- `software_revision`
- `hardware_profile`
- `environment_digest`
- `anomaly_flags[]`
- `evidence_id` when promoted into Evidence Graph

Recommended `RuntimeExecutionRecord` linkage:

- simulation/job ID
- agent run ID where applicable
- SceneState ID where applicable
- Git revision
- input artifact IDs
- output artifact IDs
- telemetry snapshot IDs
- status
- failure classification

## Observability architecture

```text
                     PTDT SYSTEM
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
   Simulation         AI/Agents       Cinematic
    Workers            Workers          Workers
        │                │                │
        └────────────────┼────────────────┘
                         ▼
                  Runtime Telemetry
                         │
                     Netdata
                         │
       ┌─────────────────┼─────────────────┐
       ▼                 ▼                 ▼
    Metrics           Alerts          Anomalies
       │                 │                 │
       └─────────────────┼─────────────────┘
                         ▼
                 Operations Plane
                         │
              selected audit snapshots
                         ▼
                   Evidence Graph
```

## Security requirements

1. Netdata credentials/tokens must remain outside model prompts and generated artifacts.
2. Monitoring endpoints must not expose control-plane mutation APIs.
3. Remote telemetry access must use least privilege and authenticated transport.
4. Operational dashboards must not be treated as authorization surfaces for engineering-state mutation.
5. Telemetry ingestion must validate timestamps, node identity, metric names and units.
6. Anomaly detection is advisory unless an independently validated rule promotes it to an operational event.
7. External/cloud telemetry is optional; the PTDT sovereign/offline mode must remain functional without it.
8. Retention policies must distinguish ephemeral operational metrics from immutable engineering evidence.

## Performance strategy

Netdata is especially valuable because the source describes low-resource, per-second, edge-based monitoring and high-scale distributed collection. fileciteturn89file0L2-L2

Use it for **observability**, not as another high-frequency data plane inside scientific simulation.

Recommended separation:

- Netdata → operational metrics
- OpenTelemetry/structured traces → distributed execution traces where required
- Evidence Graph → immutable provenance/evidence
- Simulation stores → scientific state
- SceneState/OpenUSD → derived visual state

This avoids duplicating every metric into every subsystem.

## Final disposition

**WRAP / ADAPT.** Netdata is a high-value addition to the PTDT **Operations + Observability Plane**. Its collectors, real-time metrics, alerts, anomaly detection, distributed streaming, and infrastructure visibility should be integrated through adapters and telemetry contracts.

The canonical engineering state, Evidence Graph, SceneState, WebGPU renderer, OpenUSD artifacts, and AI evaluation authority remain independent of Netdata.
