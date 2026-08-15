"""Distributed Redis Pub/Sub and Stream transport for PTDT SceneState."""

from __future__ import annotations

import asyncio
import json
import os
import socket
import time
import uuid
from typing import Any

from .streaming import SceneStreamMessage, SpatialConnectionManager


class DistributedRedisBus:
    """Low-latency Pub/Sub transport backed by an ordered Redis Stream."""

    def __init__(
        self,
        manager: SpatialConnectionManager,
        *,
        redis_url: str,
        channel_name: str = "ptdt:spatial:streams",
        stream_name: str = "ptdt:scene-state",
        stream_max_length: int = 10_000,
        node_id: str | None = None,
    ) -> None:
        if not redis_url:
            raise ValueError("redis_url must not be empty.")
        if stream_max_length < 100:
            raise ValueError("stream_max_length must be at least 100.")

        self.manager = manager
        self.redis_url = redis_url
        self.channel_name = channel_name
        self.stream_name = stream_name
        self.stream_max_length = stream_max_length
        self.node_id = (
            node_id
            or os.getenv("PTDT_NODE_ID")
            or f"{socket.gethostname()}-{uuid.uuid4().hex[:12]}"
        )
        self._redis: Any = None
        self._listener_task: asyncio.Task[None] | None = None
        self._stopped = asyncio.Event()
        self._seen_events: set[str] = set()
        self._seen_order: list[str] = []
        self._seen_limit = 20_000

    async def start(self) -> None:
        """Connect Redis and start the resilient Pub/Sub listener."""

        if self._listener_task is not None and not self._listener_task.done():
            return

        from redis.asyncio import Redis

        self._stopped.clear()
        self._redis = Redis.from_url(self.redis_url, decode_responses=True)
        await self._redis.ping()
        self._listener_task = asyncio.create_task(
            self._listener_loop(),
            name="ptdt-redis-state-listener",
        )

    async def publish_state(
        self,
        *,
        scene_state_version: int,
        frame_index: int,
        payload: dict[str, Any],
        state_cryptographic_seal: str,
    ) -> str:
        """Persist and publish one canonical state event."""

        if self._redis is None:
            raise RuntimeError("DistributedRedisBus.start() must be called first.")

        event_id = uuid.uuid4().hex
        envelope = {
            "event_id": event_id,
            "origin_node_id": self.node_id,
            "schema_version": 1,
            "scene_state_version": scene_state_version,
            "frame_index": frame_index,
            "timestamp_unix_ms": time.time_ns() // 1_000_000,
            "payload": payload,
            "state_cryptographic_seal": state_cryptographic_seal,
        }
        serialized = json.dumps(envelope, sort_keys=True, separators=(",", ":"))

        await self._redis.xadd(
            self.stream_name,
            {"event": serialized},
            maxlen=self.stream_max_length,
            approximate=True,
        )
        await self._redis.publish(self.channel_name, serialized)
        return event_id

    async def replay_from(self, last_stream_id: str = "0-0", *, count: int = 100) -> list[SceneStreamMessage]:
        """Replay persisted events after a Redis Stream ID."""

        if self._redis is None:
            raise RuntimeError("DistributedRedisBus.start() must be called first.")
        if count < 1 or count > 1_000:
            raise ValueError("count must be between 1 and 1000.")

        result = await self._redis.xread(
            {self.stream_name: last_stream_id},
            count=count,
            block=1,
        )
        messages: list[SceneStreamMessage] = []
        for _, entries in result:
            for _, fields in entries:
                message = self._decode_event(fields["event"])
                messages.append(message)
                await self._remember_event(message.event_id)
        return messages

    async def _listener_loop(self) -> None:
        """Continuously consume Pub/Sub with bounded reconnect delay."""

        from redis.asyncio import Redis

        backoff_seconds = 1.0
        while not self._stopped.is_set():
            pubsub = None
            try:
                if self._redis is None:
                    self._redis = Redis.from_url(self.redis_url, decode_responses=True)
                    await self._redis.ping()

                pubsub = self._redis.pubsub()
                await pubsub.subscribe(self.channel_name)
                backoff_seconds = 1.0

                while not self._stopped.is_set():
                    message = await pubsub.get_message(
                        ignore_subscribe_messages=True,
                        timeout=1.0,
                    )
                    if message and message.get("type") == "message":
                        serialized = str(message["data"])
                        envelope = json.loads(serialized)
                        event_id = str(envelope["event_id"])
                        if event_id in self._seen_events:
                            continue
                        decoded = self._decode_event(serialized)
                        await self.manager.broadcast_message(decoded)
                        await self._remember_event(event_id)
            except asyncio.CancelledError:
                raise
            except Exception:
                await asyncio.sleep(backoff_seconds)
                backoff_seconds = min(backoff_seconds * 2.0, 30.0)
            finally:
                if pubsub is not None:
                    try:
                        await pubsub.unsubscribe(self.channel_name)
                    except Exception:
                        pass
                    try:
                        await pubsub.aclose()
                    except Exception:
                        pass

    @staticmethod
    def _decode_event(serialized: str) -> SceneStreamMessage:
        envelope = json.loads(serialized)
        return SceneStreamMessage(
            event_id=str(envelope["event_id"]),
            origin_node_id=str(envelope["origin_node_id"]),
            schema_version=int(envelope["schema_version"]),
            sequence=0,
            scene_state_version=int(envelope["scene_state_version"]),
            frame_index=int(envelope["frame_index"]),
            timestamp_unix_ms=int(envelope["timestamp_unix_ms"]),
            payload=dict(envelope["payload"]),
            state_cryptographic_seal=str(envelope["state_cryptographic_seal"]),
        )

    async def _remember_event(self, event_id: str) -> None:
        if event_id in self._seen_events:
            return
        self._seen_events.add(event_id)
        self._seen_order.append(event_id)
        if len(self._seen_order) > self._seen_limit:
            expired = self._seen_order.pop(0)
            self._seen_events.discard(expired)

    async def stop(self) -> None:
        """Stop listener and close Redis resources."""

        self._stopped.set()
        if self._listener_task is not None:
            self._listener_task.cancel()
            await asyncio.gather(self._listener_task, return_exceptions=True)
            self._listener_task = None
        if self._redis is not None:
            await self._redis.aclose()
            self._redis = None
