"""Regression tests for distributed cluster state routing."""

from __future__ import annotations

import json

from engine.cinematic_runtime.gateway import _authorized_websocket
from engine.cinematic_runtime.redis_bus import DistributedRedisBus
from engine.cinematic_runtime.streaming import SpatialConnectionManager


class FakeHeaders:
    def __init__(self, values: dict[str, str]) -> None:
        self._values = values

    def get(self, key: str, default: str | None = None) -> str | None:
        return self._values.get(key, default)


class FakeWebSocket:
    def __init__(self, values: dict[str, str]) -> None:
        self.headers = FakeHeaders(values)


def test_redis_event_decodes_to_valid_scene_message() -> None:
    manager = SpatialConnectionManager()
    bus = DistributedRedisBus(
        manager,
        redis_url="redis://example.invalid:6379/0",
        node_id="test-node",
    )

    serialized = json.dumps(
        {
            "event_id": "0123456789abcdef0123456789abcdef",
            "origin_node_id": "test-node",
            "schema_version": 1,
            "scene_state_version": 12,
            "frame_index": 99,
            "timestamp_unix_ms": 123456789,
            "payload": {"draw_call_count": 2},
            "state_cryptographic_seal": "a" * 64,
        }
    )

    message = bus._decode_event(serialized)

    assert message.event_id == "0123456789abcdef0123456789abcdef"
    assert message.origin_node_id == "test-node"
    assert message.scene_state_version == 12
    assert message.frame_index == 99
    assert message.timestamp_unix_ms == 123456789


def test_browser_websocket_subprotocol_authentication(monkeypatch) -> None:
    monkeypatch.setenv("PTDT_WS_SHARED_SECRET", "test-secret")

    websocket = FakeWebSocket(
        {"sec-websocket-protocol": "ptdt.v1, ptdt.token.test-secret"}
    )

    authorized, protocol = _authorized_websocket(websocket)

    assert authorized is True
    assert protocol == "ptdt.v1"


def test_browser_websocket_auth_rejects_invalid_token(monkeypatch) -> None:
    monkeypatch.setenv("PTDT_WS_SHARED_SECRET", "test-secret")

    websocket = FakeWebSocket(
        {"sec-websocket-protocol": "ptdt.v1, ptdt.token.wrong-secret"}
    )

    authorized, protocol = _authorized_websocket(websocket)

    assert authorized is False
    assert protocol is None
