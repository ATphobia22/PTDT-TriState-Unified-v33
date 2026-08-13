"""Bounded WebSocket streaming and optional Redis Streams transport."""

from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ClientProtocolMessage(BaseModel):
    """Validated client-to-server control message."""

    model_config = ConfigDict(extra="forbid")

    type: str = Field(min_length=1, max_length=32)
    sequence: int | None = Field(default=None, ge=0)
    scene_id: str | None = Field(default=None, max_length=128)
    viewport_id: str | None = Field(default=None, max_length=128)
    max_fps: int | None = Field(default=None, ge=1, le=120)

    @field_validator("type")
    @classmethod
    def _normalize_type(cls, value: str) -> str:
        return value.strip().upper()


class SceneStreamMessage(BaseModel):
    """Server-to-client state envelope."""

    model_config = ConfigDict(extra="forbid")

    type: str = "SCENE_STATE"
    schema_version: int = Field(ge=1)
    sequence: int = Field(ge=0)
    scene_state_version: int = Field(ge=0)
    frame_index: int = Field(ge=0)
    timestamp_unix_ms: int = Field(ge=0)
    payload: dict[str, Any]
    state_cryptographic_seal: str = Field(min_length=64, max_length=64)


@dataclass
class _ClientSession:
    websocket: Any
    queue: asyncio.Queue[SceneStreamMessage]
    sender_task: asyncio.Task[None]
    last_seen_monotonic: float
    dropped_frames: int = 0


class SpatialConnectionManager:
    """Connection manager with bounded latest-state-wins queues."""

    def __init__(
        self,
        *,
        queue_size: int = 2,
        heartbeat_timeout_seconds: float = 45.0,
    ) -> None:
        if queue_size < 1:
            raise ValueError("queue_size must be positive.")
        if heartbeat_timeout_seconds <= 0:
            raise ValueError("heartbeat_timeout_seconds must be positive.")

        self._queue_size = queue_size
        self._heartbeat_timeout = heartbeat_timeout_seconds
        self._sessions: dict[int, _ClientSession] = {}
        self._lock = asyncio.Lock()
        self._sequence = 0

    async def connect(self, websocket: Any) -> None:
        """Accept and register a WebSocket client with a dedicated sender."""

        await websocket.accept()
        queue: asyncio.Queue[SceneStreamMessage] = asyncio.Queue(maxsize=self._queue_size)
        sender_task = asyncio.create_task(
            self._sender_loop(websocket, queue),
            name="ptdt-websocket-sender",
        )
        session = _ClientSession(
            websocket=websocket,
            queue=queue,
            sender_task=sender_task,
            last_seen_monotonic=time.monotonic(),
        )
        async with self._lock:
            self._sessions[id(websocket)] = session

    async def disconnect(self, websocket: Any) -> None:
        """Remove a client and cancel its sender task."""

        async with self._lock:
            session = self._sessions.pop(id(websocket), None)

        if session is None:
            return

        if not session.sender_task.done():
            session.sender_task.cancel()
            await asyncio.gather(session.sender_task, return_exceptions=True)

        try:
            await websocket.close()
        except Exception:
            pass

    async def touch(self, websocket: Any) -> None:
        """Refresh the client's heartbeat timestamp."""

        async with self._lock:
            session = self._sessions.get(id(websocket))
            if session is not None:
                session.last_seen_monotonic = time.monotonic()

    async def broadcast_state(
        self,
        *,
        scene_state_version: int,
        frame_index: int,
        payload: dict[str, Any],
        state_cryptographic_seal: str,
    ) -> SceneStreamMessage:
        """Enqueue one state message without waiting on socket writes."""

        async with self._lock:
            self._sequence += 1
            sequence = self._sequence
            sessions = list(self._sessions.values())

        message = SceneStreamMessage(
            schema_version=1,
            sequence=sequence,
            scene_state_version=scene_state_version,
            frame_index=frame_index,
            timestamp_unix_ms=int(time.time() * 1000),
            payload=payload,
            state_cryptographic_seal=state_cryptographic_seal,
        )

        for session in sessions:
            try:
                session.queue.put_nowait(message)
            except asyncio.QueueFull:
                try:
                    session.queue.get_nowait()
                    session.queue.task_done()
                except asyncio.QueueEmpty:
                    pass
                try:
                    session.queue.put_nowait(message)
                    session.dropped_frames += 1
                except asyncio.QueueFull:
                    session.dropped_frames += 1

        return message

    async def prune_stale(self) -> int:
        """Disconnect clients that missed the heartbeat deadline."""

        cutoff = time.monotonic() - self._heartbeat_timeout
        async with self._lock:
            stale = [
                session.websocket
                for session in self._sessions.values()
                if session.last_seen_monotonic < cutoff
            ]

        for websocket in stale:
            await self.disconnect(websocket)

        return len(stale)

    async def _sender_loop(
        self,
        websocket: Any,
        queue: asyncio.Queue[SceneStreamMessage],
    ) -> None:
        while True:
            message = await queue.get()
            try:
                await websocket.send_json(message.model_dump(mode="json"))
            except Exception:
                return
            finally:
                queue.task_done()


class RedisStateStream:
    """Redis Streams adapter for ordered cross-node state distribution."""

    def __init__(
        self,
        redis_url: str,
        *,
        stream_key: str = "ptdt:scene-state",
    ) -> None:
        self.redis_url = redis_url
        self.stream_key = stream_key
        self._redis = None

    async def connect(self) -> None:
        """Create the asyncio Redis client."""

        try:
            from redis.asyncio import Redis
        except ImportError as exc:
            raise RuntimeError("redis is required for RedisStateStream.") from exc

        self._redis = Redis.from_url(self.redis_url, decode_responses=True)
        await self._redis.ping()

    async def append(self, message: SceneStreamMessage) -> str:
        """Append a state envelope to the ordered Redis Stream."""

        if self._redis is None:
            raise RuntimeError("RedisStateStream.connect() must be called first.")

        fields = {
            "message": json.dumps(
                message.model_dump(mode="json"),
                sort_keys=True,
                separators=(",", ":"),
            )
        }
        result = await self._redis.xadd(
            self.stream_key,
            fields,
            maxlen=10_000,
            approximate=True,
        )
        return str(result)

    async def read(
        self,
        *,
        last_id: str = "0-0",
        block_ms: int = 1000,
        count: int = 100,
    ) -> list[SceneStreamMessage]:
        """Read ordered stream entries after the supplied Redis ID."""

        if self._redis is None:
            raise RuntimeError("RedisStateStream.connect() must be called first.")

        result = await self._redis.xread(
            {self.stream_key: last_id},
            count=count,
            block=block_ms,
        )
        messages: list[SceneStreamMessage] = []
        for _, entries in result:
            for _, fields in entries:
                messages.append(
                    SceneStreamMessage.model_validate(json.loads(fields["message"]))
                )
        return messages

    async def close(self) -> None:
        """Close the Redis connection."""

        if self._redis is not None:
            await self._redis.aclose()
            self._redis = None
