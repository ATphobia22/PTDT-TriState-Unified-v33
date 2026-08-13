"""FastAPI gateway for the PTDT cinematic runtime."""

from __future__ import annotations

import json
import os

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, status
from pydantic import BaseModel, ConfigDict, Field

from .manifest import RenderManifestBuilder, WebGPUBufferManifest
from .scene_state import AuthoritativeSceneState, EntityStateNode
from .streaming import ClientProtocolMessage, SpatialConnectionManager

MAX_WEBSOCKET_MESSAGE_BYTES = 32 * 1024


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


def _authorized_websocket(websocket: WebSocket) -> bool:
    """Validate a shared secret when one is configured.

    Production deployments should replace this boundary with the platform's
    identity provider/JWT middleware. When no secret is configured, the
    endpoint is intentionally unavailable rather than implicitly public.
    """

    expected = os.getenv("PTDT_WS_SHARED_SECRET")
    supplied = websocket.headers.get("x-ptdt-ws-secret")
    return bool(expected) and supplied == expected


app = FastAPI(
    title="PTDT Cinematic Runtime",
    version="34.0.0",
)

scene_state = AuthoritativeSceneState()
broadcaster = SpatialConnectionManager()


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
    """Commit entities atomically and enqueue the resulting state envelope."""

    scene_state.upsert_many(payload.entities)
    snapshot = scene_state.snapshot()
    manifest = RenderManifestBuilder.build(scene_state)

    message = await broadcaster.broadcast_state(
        scene_state_version=snapshot.version,
        frame_index=payload.frame_index,
        payload=manifest.model_dump(mode="json"),
        state_cryptographic_seal=snapshot.seal,
    )

    return BroadcastResponse(
        status="FRAME_PROCESSED",
        sequence=message.sequence,
        scene_state_version=snapshot.version,
        state_cryptographic_seal=snapshot.seal,
    )


@app.websocket("/api/v1/stream/scene-state")
async def websocket_scene_state_stream(websocket: WebSocket) -> None:
    """Authenticate and stream versioned SceneState envelopes."""

    if not _authorized_websocket(websocket):
        await websocket.close(code=1008, reason="Unauthorized")
        return

    await broadcaster.connect(websocket)
    try:
        while True:
            raw_message = await websocket.receive_json()
            if len(json.dumps(raw_message, separators=(",", ":"))) > MAX_WEBSOCKET_MESSAGE_BYTES:
                await websocket.close(code=1009, reason="Message too large")
                break

            message = ClientProtocolMessage.model_validate(raw_message)

            if message.type in {"PING", "PONG", "ACK"}:
                await broadcaster.touch(websocket)
                await websocket.send_json(
                    {"type": "PONG", "sequence": message.sequence}
                )
                continue

            if message.type == "SUBSCRIBE":
                await broadcaster.touch(websocket)
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
