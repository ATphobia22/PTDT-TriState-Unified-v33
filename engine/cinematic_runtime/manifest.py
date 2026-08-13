"""Versioned WebGPU render-manifest ABI."""

from __future__ import annotations

import struct
from typing import Iterable

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .scene_state import AuthoritativeSceneState, EntityStateNode


class WebGPUBufferManifest(BaseModel):
    """JSON control-plane representation of GPU buffer metadata."""

    model_config = ConfigDict(frozen=True)

    schema_version: int = Field(default=1, ge=1)
    scene_state_version: int = Field(ge=0)
    coordinate_space: str
    horizontal_crs: str
    vertical_datum: str
    draw_call_count: int = Field(ge=0)
    transform_stride_f32: int = Field(default=16, frozen=True)
    transform_buffer_flat: tuple[float, ...]
    visibility_bitmask: tuple[int, ...]
    lod_indices: tuple[int, ...]
    state_cryptographic_seal: str = Field(min_length=64, max_length=64)

    @field_validator("visibility_bitmask", "lod_indices")
    @classmethod
    def _validate_integer_buffers(cls, value: tuple[int, ...]) -> tuple[int, ...]:
        if any(item not in (0, 1, 2, 3) for item in value):
            raise ValueError("GPU integer buffers contain an invalid value.")
        return value


class RenderManifestBuilder:
    """Build a deterministic manifest from an authoritative SceneState."""

    @staticmethod
    def build(scene_state: AuthoritativeSceneState) -> WebGPUBufferManifest:
        snapshot = scene_state.snapshot()
        transform_buffer: list[float] = []
        visibility: list[int] = []
        lod_indices: list[int] = []

        for entity in snapshot.entities:
            node = EntityStateNode.model_validate(entity)
            transform_buffer.extend(node.local_transform_matrix)
            visibility.append(1 if node.visibility_status else 0)
            lod_indices.append(node.lod_index)

        return WebGPUBufferManifest(
            schema_version=snapshot.schema_version,
            scene_state_version=snapshot.version,
            coordinate_space=snapshot.coordinate_space,
            horizontal_crs=snapshot.horizontal_crs,
            vertical_datum=snapshot.vertical_datum,
            draw_call_count=len(snapshot.entities),
            transform_stride_f32=16,
            transform_buffer_flat=tuple(transform_buffer),
            visibility_bitmask=tuple(visibility),
            lod_indices=tuple(lod_indices),
            state_cryptographic_seal=snapshot.seal,
        )

    @staticmethod
    def pack_f32(values: Iterable[float]) -> bytes:
        """Pack float32 values using little-endian GPU ABI ordering."""

        values_list = [float(value) for value in values]
        return struct.pack(f"<{len(values_list)}f", *values_list)

    @staticmethod
    def pack_u32(values: Iterable[int]) -> bytes:
        """Pack uint32 values using little-endian GPU ABI ordering."""

        values_list = [int(value) for value in values]
        return struct.pack(f"<{len(values_list)}I", *values_list)
