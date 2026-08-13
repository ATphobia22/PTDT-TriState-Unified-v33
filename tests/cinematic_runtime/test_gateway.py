"""FastAPI gateway regression tests for SceneState streaming."""

from __future__ import annotations

from fastapi.testclient import TestClient

from engine.cinematic_runtime.gateway import app


def _entity(uuid: str) -> dict:
    return {
        "uuid": uuid,
        "asset_class": "building",
        "local_transform_matrix": [
            1.0,
            0.0,
            0.0,
            0.0,
            0.0,
            1.0,
            0.0,
            0.0,
            0.0,
            0.0,
            1.0,
            0.0,
            0.0,
            0.0,
            0.0,
            1.0,
        ],
    }


def test_authenticated_websocket_receives_scene_state(monkeypatch) -> None:
    monkeypatch.setenv("PTDT_WS_SHARED_SECRET", "test-secret")
    monkeypatch.delenv("PTDT_REDIS_URL", raising=False)
    monkeypatch.delenv("PTDT_REQUIRE_REDIS", raising=False)

    with TestClient(app) as client:
        with client.websocket_connect(
            "/api/v1/stream/scene-state",
            subprotocols=["ptdt.v1", "ptdt.token.test-secret"],
        ) as websocket:
            websocket.send_json(
                {
                    "type": "SUBSCRIBE",
                    "scene_id": "ptdt",
                    "viewport_id": "test",
                    "max_fps": 30,
                }
            )
            assert websocket.receive_json()["type"] == "SUBSCRIBED"

            response = client.post(
                "/api/v1/pipeline/execute-and-broadcast",
                json={"frame_index": 7, "entities": [_entity("gateway-test-1")]},
            )
            assert response.status_code == 200

            streamed = websocket.receive_json()
            assert streamed["type"] == "SCENE_STATE"
            assert streamed["frame_index"] == 7
            assert streamed["scene_state_version"] >= 1
            assert len(streamed["state_cryptographic_seal"]) == 64


def test_authenticated_websocket_can_request_targeted_resync(monkeypatch) -> None:
    monkeypatch.setenv("PTDT_WS_SHARED_SECRET", "test-secret")
    monkeypatch.delenv("PTDT_REDIS_URL", raising=False)
    monkeypatch.delenv("PTDT_REQUIRE_REDIS", raising=False)

    with TestClient(app) as client:
        with client.websocket_connect(
            "/api/v1/stream/scene-state",
            subprotocols=["ptdt.v1", "ptdt.token.test-secret"],
        ) as websocket:
            response = client.post(
                "/api/v1/pipeline/execute-and-broadcast",
                json={"frame_index": 8, "entities": [_entity("gateway-test-2")]},
            )
            assert response.status_code == 200

            websocket.send_json({"type": "RESYNC", "sequence": 0})
            resync = websocket.receive_json()

            assert resync["type"] == "SCENE_STATE"
            assert resync["scene_state_version"] >= response.json()["scene_state_version"]
            assert resync["frame_index"] == 8
