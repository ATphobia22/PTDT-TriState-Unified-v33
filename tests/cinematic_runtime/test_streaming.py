"""Streaming regression tests for bounded state delivery."""

from __future__ import annotations

import asyncio
from typing import Any

from engine.cinematic_runtime.streaming import SceneStreamMessage, SpatialConnectionManager


class FakeWebSocket:
    def __init__(self) -> None:
        self.accepted = False
        self.messages: list[dict] = []
        self.closed = False
        self.subprotocol: str | None = None

    async def accept(self, *args: Any, subprotocol: str | None = None, **kwargs: Any) -> None:
        self.accepted = True
        self.subprotocol = subprotocol

    async def send_json(self, payload: dict) -> None:
        self.messages.append(payload)

    async def close(self) -> None:
        self.closed = True


def test_broadcast_uses_versioned_envelope() -> None:
    async def run() -> None:
        manager = SpatialConnectionManager(queue_size=2)
        websocket = FakeWebSocket()
        await manager.connect(websocket)

        message = await manager.broadcast_state(
            scene_state_version=3,
            frame_index=17,
            payload={"draw_call_count": 1},
            state_cryptographic_seal="a" * 64,
        )

        await asyncio.sleep(0)

        assert isinstance(message, SceneStreamMessage)
        assert message.sequence == 1
        assert message.scene_state_version == 3
        assert websocket.messages[0]["frame_index"] == 17

        await manager.disconnect(websocket)
        assert websocket.closed is True

    asyncio.run(run())


def test_client_protocol_queue_is_bounded_and_latest_state_wins() -> None:
    async def run() -> None:
        manager = SpatialConnectionManager(queue_size=1)
        websocket = FakeWebSocket()
        await manager.connect(websocket)

        for frame in range(10):
            await manager.broadcast_state(
                scene_state_version=frame,
                frame_index=frame,
                payload={"frame": frame},
                state_cryptographic_seal="b" * 64,
            )

        await asyncio.sleep(0)

        assert websocket.messages[-1]["frame_index"] == 9
        await manager.disconnect(websocket)

    asyncio.run(run())
