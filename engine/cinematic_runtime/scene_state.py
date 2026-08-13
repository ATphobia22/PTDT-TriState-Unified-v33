"""Versioned authoritative SceneState repository."""

from __future__ import annotations

import hashlib
import json
import math
import threading
from dataclasses import dataclass
from typing import Any, Iterable

from pydantic import BaseModel, ConfigDict, Field, field_validator


class EntityStateNode(BaseModel):
    """Validated render entity state."""

    model_config = ConfigDict(frozen=True)

    uuid: str = Field(min_length=1)
    asset_class: str = Field(min_length=1)
    local_transform_matrix: tuple[float, ...]
    visibility_status: bool = True
    lod_index: int = Field(default=0, ge=0, le=3)

    @field_validator("local_transform_matrix")
    @classmethod
    def _validate_matrix(cls, value: tuple[float, ...]) -> tuple[float, ...]:
        if len(value) != 16:
            raise ValueError("local_transform_matrix must contain exactly 16 values.")
        if not all(isinstance(item, (int, float)) and math.isfinite(float(item)) for item in value):
            raise ValueError("local_transform_matrix values must be finite numbers.")
        return tuple(float(item) for item in value)


@dataclass(frozen=True)
class SceneStateSnapshot:
    """Immutable serialized SceneState snapshot."""

    version: int
    entities: tuple[dict[str, Any], ...]
    coordinate_space: str
    horizontal_crs: str
    vertical_datum: str
    schema_version: int
    seal: str


class AuthoritativeSceneState:
    """Thread-safe, process-local repository with explicit state versions.

    The repository deliberately does not pretend to be a distributed database.
    A deployment can persist these immutable snapshots externally and use Redis
    Streams for cross-process distribution.
    """

    def __init__(
        self,
        *,
        coordinate_space: str = "PTDT_LOCAL_RENDER_FTUS",
        horizontal_crs: str = "EPSG:2966",
        vertical_datum: str = "NAVD88",
        schema_version: int = 1,
    ) -> None:
        self.coordinate_space = coordinate_space
        self.horizontal_crs = horizontal_crs
        self.vertical_datum = vertical_datum
        self.schema_version = schema_version
        self._registry: dict[str, EntityStateNode] = {}
        self._version = 0
        self._lock = threading.RLock()

    def upsert(self, node: EntityStateNode) -> int:
        """Atomically update one entity and advance the state version."""

        return self.upsert_many((node,))

    def upsert_many(self, nodes: Iterable[EntityStateNode]) -> int:
        """Atomically apply a batch and advance the state version once."""

        validated_nodes = tuple(nodes)
        with self._lock:
            for node in validated_nodes:
                self._registry[node.uuid] = node
            if validated_nodes:
                self._version += 1
            return self._version

    def remove(self, uuid: str) -> int:
        """Atomically remove one entity and advance the state version."""

        with self._lock:
            if uuid in self._registry:
                del self._registry[uuid]
                self._version += 1
            return self._version

    def get(self, uuid: str) -> EntityStateNode | None:
        """Read one entity from an atomic snapshot boundary."""

        with self._lock:
            return self._registry.get(uuid)

    def snapshot(self) -> SceneStateSnapshot:
        """Create a canonical immutable snapshot and cryptographic seal."""

        with self._lock:
            entities = tuple(
                node.model_dump(mode="json")
                for node in sorted(
                    self._registry.values(),
                    key=lambda item: item.uuid,
                )
            )
            body = {
                "schema_version": self.schema_version,
                "scene_state_version": self._version,
                "coordinate_space": self.coordinate_space,
                "horizontal_crs": self.horizontal_crs,
                "vertical_datum": self.vertical_datum,
                "entities": entities,
            }

        seal = self.compute_seal(body)
        return SceneStateSnapshot(
            version=self._version,
            entities=entities,
            coordinate_space=self.coordinate_space,
            horizontal_crs=self.horizontal_crs,
            vertical_datum=self.vertical_datum,
            schema_version=self.schema_version,
            seal=seal,
        )

    @staticmethod
    def compute_seal(payload: dict[str, Any]) -> str:
        """Hash canonical JSON bytes so serialization order is deterministic."""

        canonical = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        return hashlib.sha256(canonical).hexdigest()
