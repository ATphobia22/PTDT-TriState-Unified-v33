# PTDT Cinematic Runtime Core

## Authority

The cinematic runtime is a consumer of authoritative PTDT evidence, hydraulic,
terrain, regulatory, and building state. It does not invent BFE, lowest
adjacent grade, floodway impact, or regulatory compliance.

## Coordinate pipeline

```text
EPSG:4326 WGS84
        |
        v
EPSG:2966 NAD83 / Indiana West (ftUS)
        |
        v
project coordinates
        |
        v
application render-origin subtraction
        |
        v
PTDT_LOCAL_RENDER_FTUS
```

Horizontal CRS and vertical datum are carried independently.

NAVD88 elevations are accepted as already-referenced heights. No silent
vertical datum transformation is performed.

## Camera pipeline

Physical sensor/lens parameters are validated before projection. The
projection matrix uses a right-handed camera convention and WebGPU NDC depth
range [0, 1].

## SceneState

SceneState is versioned and validated at ingestion. Every transform is exactly
16 finite float values. Frame batches advance the state version once. Snapshots
are sorted by UUID and sealed using canonical SHA-256 serialization.

The process-local repository is a concurrency boundary, not a distributed
database. Cross-node distribution uses Redis Streams.

## LoD

LoD is camera-aware and based on:

- frustum visibility
- camera-space depth
- projected bounding-sphere diameter
- viewport height
- vertical/horizontal field of view

LoD 3/2/1/0 thresholds are measured in projected pixels rather than arbitrary
world-space distance.

## Streaming

Each WebSocket receives a bounded queue. The queue implements latest-state-wins
coalescing so a slow client cannot create an unbounded historical backlog.

State envelopes contain:

- schema version
- sequence
- SceneState version
- frame index
- timestamp
- payload
- cryptographic seal

Redis Streams provide ordered cross-node transport. Pub/Sub remains suitable
for ephemeral notifications but is not the authoritative state transport.

## Security

The streaming gateway requires `PTDT_WS_SHARED_SECRET` and the matching
`x-ptdt-ws-secret` header. The protocol rejects oversized control messages and
validates all client messages with strict Pydantic schemas.

A production deployment should replace the shared-secret boundary with the
platform identity provider/JWT middleware and enforce TLS, origin policy,
connection limits, rate limits, and secret rotation.

## Regulatory boundary

Rendering/elevation relationships are not regulatory determinations. Any
regulatory result must originate from the PTDT evidence/rules subsystem and
carry source/version/provenance metadata.
