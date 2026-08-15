"""FastAPI gateway for the PTDT cinematic runtime and cluster stream."""

from __future__ import annotations

import asyncio
import json
import os
import time

from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, status
from pydantic import BaseModel, ConfigDict, Field

from .manifest import RenderManifestBuilder, WebGPUBufferManifest
from .redis_bus import DistributedRedisBus
from .scene_state import AuthoritativeSceneState, EntityStateNode
from .streaming import ClientProtocolMessage, SceneStreamMessage, SpatialConnectionManager

MAX_WEBSOCKET_MESSAGE_BYTES = 32 * 1024
DEFAULT_REDIS_URL = "redis://atphobia-redis-mesh:6379/0"
SUPPORTED_WS_PROTOCOL = "ptdt.v1"


class SceneEntityPayload(EntityStateNode):
    """HTTP representation of an authoritative render entity."""


class BroadcastFramePayload(BaseModel):
    """Frame state accepted by the runtime broadcast endpoint."""

    model_config = ConfigDict(extra="forbid")

    frame_index: int = Field(ge=0)
    entities: list[SceneEntityPayload] = Field(max_length=100_000)


class BroadcastResponse(BaseModel):
    """Deterministic HTTP response for a broadcast tick."""

    status: str
    sequence: int
    scene_state_version: int
    state_cryptographic_seal: str
    distribution_event_id: str | None = None


def _websocket_protocols(websocket: WebSocket) -> list[str]:
    """Return browser-provided WebSocket subprotocol tokens."""

    header = websocket.headers.get("sec-websocket-protocol", "")
    return [item.strip() for item in header.split(",") if item.strip()]


def _authorized_websocket(websocket: WebSocket) -> tuple[bool, str | None]:
    """Validate shared-secret auth for browser and non-browser clients."""

    expected = os.getenv("PTDT_WS_SHARED_SECRET")
    if not expected:
        return False, None

    supplied_header = websocket.headers.get("x-ptdt-ws-secret")
    if supplied_header == expected:
        return True, SUPPORTED_WS_PROTOCOL

    protocols = _websocket_protocols(websocket)
    token_protocol = next(
        (item for item in protocols if item.startswith("ptdt.token.")),
        None,
    )
    if token_protocol is not None and token_protocol.removeprefix("ptdt.token.") == expected:
        return True, SUPPORTED_WS_PROTOCOL

    return False, None


broadcaster = SpatialConnectionManager()
scene_state = AuthoritativeSceneState()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Start optional distributed transport and heartbeat maintenance."""

    redis_url = os.getenv("PTDT_REDIS_URL")
    require_redis = os.getenv("PTDT_REQUIRE_REDIS", "false").strip().lower() == "true"
    redis_bus: DistributedRedisBus | None = None
    app.state.last_frame_index = 0

    if redis_url or require_redis:
        redis_bus = DistributedRedisBus(
            broadcaster,
            redis_url=redis_url or DEFAULT_REDIS_URL,
        )
        try:
            await redis_bus.start()
        except Exception:
            await redis_bus.stop()
            if require_redis:
                raise
            redis_bus = None

    prune_stop = asyncio.Event()

    async def prune_loop() -> None:
        while not prune_stop.is_set():
            try:
                await asyncio.wait_for(prune_stop.wait(), timeout=5.0)
            except asyncio.TimeoutError:
                await broadcaster.prune_stale()

    prune_task = asyncio.create_task(prune_loop(), name="ptdt-websocket-pruner")
    app.state.redis_bus = redis_bus

    try:
        yield
    finally:
        prune_stop.set()
        prune_task.cancel()
        await asyncio.gather(prune_task, return_exceptions=True)
        if redis_bus is not None:
            await redis_bus.stop()


app = FastAPI(
    title="PTDT Cinematic Runtime",
    version="34.2.0",
    lifespan=lifespan,
)


@app.get(
    "/api/v1/render/webgpu-manifest",
    response_model=WebGPUBufferManifest,
    status_code=status.HTTP_200_OK,
)
async def generate_webgpu_manifest() -> WebGPUBufferManifest:
    """Return the validated WebGPU control-plane manifest."""

    return RenderManifestBuilder.build(scene_state)


@app.post(
    "/api/v1/pipeline/execute-and-broadcast",
    response_model=BroadcastResponse,
    status_code=status.HTTP_200_OK,
)
async def execute_and_broadcast(
    payload: BroadcastFramePayload,
) -> BroadcastResponse:
    """Commit state and distribute it locally or through Redis."""

    scene_state.upsert_many(payload.entities)
    snapshot = scene_state.snapshot()
    manifest = RenderManifestBuilder.build(scene_state)
    app.state.last_frame_index = payload.frame_index
    redis_bus: DistributedRedisBus | None = app.state.redis_bus

    if redis_bus is not None:
        event_id = await redis_bus.publish_state(
            scene_state_version=snapshot.version,
            frame_index=payload.frame_index,
            payload=manifest.model_dump(mode="json"),
            state_cryptographic_seal=snapshot.seal,
        )
        return BroadcastResponse(
            status="FRAME_PROCESSED_CLUSTER_QUEUED",
            sequence=0,
            scene_state_version=snapshot.version,
            state_cryptographic_seal=snapshot.seal,
            distribution_event_id=event_id,
        )

    message = await broadcaster.broadcast_state(
        scene_state_version=snapshot.version,
        frame_index=payload.frame_index,
        payload=manifest.model_dump(mode="json"),
        state_cryptographic_seal=snapshot.seal,
    )

    return BroadcastResponse(
        status="FRAME_PROCESSED_LOCAL",
        sequence=message.sequence,
        scene_state_version=snapshot.version,
        state_cryptographic_seal=snapshot.seal,
        distribution_event_id=message.event_id,
    )


@app.websocket("/api/v1/stream/scene-state")
async def websocket_scene_state_stream(websocket: WebSocket) -> None:
    """Authenticate and stream versioned SceneState envelopes."""

    authorized, selected_protocol = _authorized_websocket(websocket)
    if not authorized:
        await websocket.close(code=1008, reason="Unauthorized")
        return

    await websocket.accept(subprotocol=selected_protocol)
    await broadcaster.register_accepted(websocket)
    try:
        while True:
            raw_message = await websocket.receive_json()
            if len(json.dumps(raw_message, separators=(",", ":"))) > MAX_WEBSOCKET_MESSAGE_BYTES:
                await websocket.close(code=1009, reason="Message too large")
                break

            message = ClientProtocolMessage.model_validate(raw_message)
            await broadcaster.touch(websocket)

            if message.type in {"PING", "PONG", "ACK"}:
                await websocket.send_json(
                    {"type": "PONG", "sequence": message.sequence}
                )
                continue

            if message.type == "RESYNC":
                snapshot = scene_state.snapshot()
                manifest = RenderManifestBuilder.build(scene_state)
                resync_message = SceneStreamMessage(
                    origin_node_id=os.getenv("PTDT_NODE_ID", "local"),
                    schema_version=manifest.schema_version,
                    sequence=0,
                    scene_state_version=snapshot.version,
                    frame_index=int(app.state.last_frame_index),
                    timestamp_unix_ms=time.time_ns() // 1_000_000,
                    payload=manifest.model_dump(mode="json"),
                    state_cryptographic_seal=snapshot.seal,
                )
                await broadcaster.send_to(websocket, resync_message)
                continue

            if message.type == "SUBSCRIBE":
                await websocket.send_json(
                    {
                        "type": "SUBSCRIBED",
                        "scene_id": message.scene_id,
                        "viewport_id": message.viewport_id,
                        "max_fps": message.max_fps or 30,
                    }
                )
                continue

            if message.type in {"UNSUBSCRIBE", "CLOSE"}:
                break

            await websocket.send_json(
                {
                    "type": "ERROR",
                    "code": "UNSUPPORTED_MESSAGE_TYPE",
                    "message": message.type,
                }
            )
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        await broadcaster.disconnect(websocket)
