# Low-Code / No-Code Front-to-Back Deployment Federation

**Status:** Architecture reference and controlled adapter strategy
**Branch:** `feature/low-code-platform-federation`

## Executive decision

The supplied low-code blueprint is useful as a **delivery-plane capability map**, but PTDT should **not replace its canonical engineering architecture with a unified no-code platform**.

PTDT is a scientific/engineering digital-twin system with WebGPU, GIS, HEC-RAS, MODFLOW 6, EnKF, Bishop stability, OpenUSD, evidence/provenance, AI governance, and high-throughput compute requirements. A low-code platform is therefore best used for **control-plane, administrative, workflow, community, grant, operations, and rapid-prototype surfaces**.

### Recommended strategy

```text
                 PTDT CANONICAL CORE
 ┌──────────────────────────────────────────────────┐
 │ Engineering State │ Evidence │ SceneState │ GPU │
 │ HEC-RAS │ MODFLOW6 │ EnKF │ Bishop │ OpenUSD │
 └──────────────────────────┬───────────────────────┘
                            │ APIs/events
                            ▼
                 PTDT APPLICATION PLANE
                            │
       ┌────────────────────┼────────────────────┐
       ▼                    ▼                    ▼
  Custom React/       Low-Code Admin       Mobile/Web
  WebGPU/MapLibre       /Operations          Apps
       │                    │                    │
       └────────────────────┼────────────────────┘
                            ▼
                     Canonical APIs
                            │
                         Supabase
                      PostgreSQL/Auth
```

## Source blueprint disposition

| Platform | Primary strength from supplied blueprint | PTDT disposition | Recommended scope |
|---|---|---|---|
| FlutterFlow | Cross-platform visual application builder, Firebase/Supabase integration, GitHub/code export and deployment workflows | **ADOPT SELECTIVELY** | Mobile/community/field applications and operational companion apps |
| Bubble | Full-stack visual web application with built-in database/workflows/hosting | **REFERENCE / PROTOTYPE ONLY** | Rapid business/admin prototypes; not engineering core |
| Wappler | Developer-centric low-code with standard web assets and self-hosted deployment model | **HIGH-VALUE ADAPTER CANDIDATE** | Self-hosted administrative/control-plane applications where code/data sovereignty matters |
| OutSystems | Enterprise full-stack low-code, governance, integration, DevOps | **REFERENCE / ENTERPRISE OPTION** | Enterprise workflow/application surfaces if organizational requirements justify platform adoption |
| Mendix | Enterprise low-code and multi-cloud/private-cloud deployment | **REFERENCE / ENTERPRISE OPTION** | Governed enterprise workflow surfaces |
| Retool | Internal operations/data administration | **ADOPT SELECTIVELY** | SRE, evidence review, grant operations, data administration, support tooling |
| WeWeb | Visual frontend in a decoupled stack | **ADAPTER CANDIDATE** | Public/community/admin web interfaces over canonical APIs |
| Toddle | Visual frontend alternative | **ADAPTER CANDIDATE** | Prototype/public workflow interfaces |
| Xano | Visual backend/API layer | **REFERENCE / OPTIONAL** | Rapid prototypes only unless a specific bounded service justifies it |
| Supabase | PostgreSQL/Auth/API/storage/realtime platform already compatible with PTDT | **CANONICAL SUPPORTING SERVICE** | Auth, control-plane metadata, bounded application data, realtime UI state |
| Vercel | Frontend/serverless deployment | **CANONICAL DEPLOYMENT OPTION** | Public web/control-plane deployment; not the scientific compute authority |
| Render | Managed deployment alternative | **OPTIONAL** | Bounded API/worker services |
| Docker | Portable runtime packaging | **CANONICAL** | Engineering, agent, GIS, simulation, and low-code-adjacent services |

## Important source verification corrections

The supplied blueprint should be treated as a starting architecture, not an authoritative current product specification.

### FlutterFlow

Current official documentation confirms that FlutterFlow can export project source code through its CLI, supports branch/environment selection, and can deploy from a connected GitHub repository. citeturn0search2turn0search5

FlutterFlow also documents Firebase and Supabase integrations. Its current documentation specifically notes Supabase API-key setup for self-hosted Supabase databases. citeturn0search12turn0search14

**PTDT decision:** strong candidate for field/mobile/community apps, but exported Flutter code remains a separate application surface and must communicate with PTDT through versioned APIs.

### Bubble

Bubble's current official material confirms a built-in database, visual workflows, external API connectivity, hosting, and one-click deployment. citeturn0search3turn0search8turn0search11

**PTDT decision:** useful for rapidly proving administrative/business workflows. Do not put authoritative engineering state inside a Bubble-native database.

### OutSystems

Current official material describes visual full-stack application development, governance/security capabilities, integrations, DevOps tooling, CI/CD, monitoring, dependency analysis, rollback, and cloud-native deployment. citeturn0search38

**PTDT decision:** credible enterprise workflow platform, but adoption would create a substantial platform boundary and should be justified by deployment/governance requirements rather than technical necessity.

### Mendix

The supplied official material confirms public-cloud and private-cloud deployment options, including Kubernetes-based private-cloud deployment and multi-cloud portability. citeturn0search36

**PTDT decision:** enterprise reference option; no core dependency.

## Canonical PTDT low-code planes

### 1. Operations Plane

Use low-code interfaces for:

- service health
- incident management
- node inventory
- simulation job queues
- worker status
- Netdata telemetry views
- maintenance workflows
- deployment approvals

### 2. Evidence Administration Plane

Use controlled UI tooling for:

- evidence review
- provenance inspection
- source registration
- evidence approval/rejection
- lineage visualization
- dataset status
- audit workflows

**Never permit a generic low-code CRUD interface to bypass Evidence Graph invariants.**

### 3. Community Benefit / Human Needs Plane

Low-code is well suited to:

- community intake
- needs assessments
- grant-program workflows
- service directories
- case routing
- accessibility workflows
- public dashboards
- notifications

### 4. Grant / Economic Development Plane

Candidate functions:

- opportunity tracking
- eligibility questionnaires
- application workflows
- document collection
- deadlines
- reporting
- award tracking
- partner coordination

### 5. Field / Mobile Plane

FlutterFlow is the strongest candidate from the supplied set for field/mobile interfaces because its documented workflow supports exported Flutter source and GitHub-connected deployment. citeturn0search2turn0search5

Potential applications:

- field inspection
- sensor registration
- infrastructure inspection
- flood observations
- photo/video evidence capture
- offline-first field collection where the selected application architecture supports it

## Control-plane security model

Low-code interfaces must never receive broad database privileges.

```text
User
  ↓
Identity / RBAC / ABAC
  ↓
Application API
  ↓
Policy Enforcement
  ↓
Validated Command
  ↓
Canonical Service
  ↓
Evidence / Engineering State
```

Required controls:

- server-side authorization
- row-level security where supported
- least-privilege service identities
- immutable audit events
- explicit approval for privileged mutations
- schema validation
- API versioning
- rate limiting
- tenant/community isolation where applicable
- secret isolation
- no direct browser access to privileged simulation databases

## Data architecture

The supplied decoupled pattern is preferred for PTDT:

```text
Visual Frontend
     │
 HTTPS/WebSocket
     ▼
API Gateway / BFF
     │
 ┌───┼───────────────────┐
 ▼   ▼                   ▼
Auth Control DB       Domain Services
       │                   │
       ▼                   ▼
   Supabase/Postgres   Python/Go/TS
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
          HEC-RAS       MODFLOW6      Evidence
             │             │             │
             └─────────────┼─────────────┘
                           ▼
                       SceneState
                           ▼
                     OpenUSD/WebGPU
```

This preserves the distinction between **application data** and **scientific state**.

## Deployment federation

### Public application

`WeWeb / custom React / FlutterFlow → Vercel or equivalent → PTDT API`

### Internal operations

`Retool / custom admin → authenticated API → Supabase + domain services`

### Self-hosted sovereign environment

`Wappler/custom frontend → Docker/Kubernetes → PTDT services → PostgreSQL/Supabase-compatible infrastructure`

### Enterprise environment

`OutSystems/Mendix → governed enterprise APIs → PTDT domain services`

## One-click deployment does not mean one-runtime architecture

PTDT must retain independent deployment units for:

- GIS services
- simulation services
- Evidence Graph
- AI agents
- AI evaluation
- Netdata/observability
- WebGPU frontend
- OpenUSD/asset workers
- media generation
- public/community applications

A unified low-code surface may orchestrate these services but must not collapse their trust boundaries.

## Recommended canonical stack

### Core engineering

- Python/Go/TypeScript
- HEC-RAS
- MODFLOW 6
- EnKF
- Bishop
- WebGPU/WGSL
- MapLibre
- OpenUSD
- PostgreSQL/Supabase-compatible services
- Docker/Kubernetes

### Application/control plane

- React/TypeScript for the authoritative engineering UI
- MapLibre/WebGPU for spatial/cinematic interfaces
- Supabase for bounded application services/Auth/realtime where appropriate
- Retool for internal operational administration
- FlutterFlow for selected mobile/field applications
- Wappler as a self-hosted low-code candidate
- WeWeb as a public/admin frontend candidate

### Deployment

- GitHub as source-control authority
- CI/CD with signed/verified artifacts
- Vercel or equivalent for selected public frontends
- Docker/Kubernetes for backend and scientific services
- sovereign/self-hosted deployment profile maintained separately

## Decision rule

**Do not select a low-code platform because it can build everything. Select it because it safely accelerates one bounded plane without becoming a new system authority.**

### Highest-value adoption order

1. **Supabase** — supporting application/auth/realtime plane
2. **Retool** — operations/evidence administration
3. **FlutterFlow** — field/mobile/community applications
4. **Wappler** — self-hosted low-code applications requiring greater code/data control
5. **WeWeb** — public/admin visual frontend candidate
6. **OutSystems/Mendix** — enterprise organizational option
7. **Bubble** — rapid prototype/business workflow option
8. **Xano** — bounded prototype/API option

## Final architecture principle

The low-code federation is an **application acceleration layer above the PTDT core**:

`Low-Code UI → API/Policy → Canonical Domain Services → Engineering State/Evidence/SceneState`

Never:

`Low-Code UI → direct mutation of scientific database`

This preserves scientific reproducibility, security, provenance, portability, and the existing PTDT authority model while still exploiting visual application-development ecosystems where they provide measurable delivery advantages.
