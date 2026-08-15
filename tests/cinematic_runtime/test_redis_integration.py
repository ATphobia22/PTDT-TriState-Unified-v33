"""Optional live Redis integration test for the cinematic cluster bus."""

from __future__ import annotations

import asyncio
import os

import pytest

from engine.cinematic_runtime.redis_bus import DistributedRedisBus
from engine.cinematic_runtime.streaming import SpatialConnectionManager


class FakeWebSocket:
    def __init__(self) -> None:
        self.messages: list[dict] = []
        self.closed = False

    async def accept(self, subprotocol: str | None = None) -> None:
        return None

    async def send_json(self, payload: dict) -> None:
        self.messages.append(payload)

    async def close(self) -> None:
        self.closed = True


def test_live_redis_bus_round_trip() -> None:
    redis_url = os.getenv("PTDT_REDIS_URL")
    if not redis_url:
        pytest.skip("PTDT_REDIS_URL is not configured for live Redis integration tests.")

    async def run() -> None:
        manager = SpatialConnectionManager(queue_size=2)
        websocket = FakeWebSocket()
        await manager.connect(websocket)
        bus = DistributedRedisBus(
            manager,
            redis_url=redis_url,
            channel_name="ptdt:test:spatial:streams",
            stream_name="ptdt:test:scene-state",
            node_id="pytest-node",
        )

        try:
            await bus.start()
            event_id = await bus.publish_state(
                scene_state_version=41,
                frame_index=9001,
                payload={"draw_call_count": 1},
                state_cryptographic_seal="c" * 64,
            )

            for _ in range(40):
                if websocket.messages:
                    break
                await asyncio.sleep(0.025)

            assert event_id
            assert websocket.messages
            assert websocket.messages[-1]["scene_state_version"] == 41
            assert websocket.messages[-1]["frame_index"] == 9001
            assert websocket.messages[-1]["state_cryptographic_seal"] == "c" * 64
        finally:
            await bus.stop()
            await manager.disconnect(websocket)

    asyncio.run(run())
