"""Versioned WebGPU render-manifest ABI."""

from __future__ import annotations

import math
import struct
from typing import Iterable

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .scene_state import AuthoritativeSceneState, EntityStateNode


class WebGPUBufferManifest(BaseModel):
    """JSON control-plane representation of GPU buffer metadata."""

    model_config = ConfigDict(frozen=True)

    schema_version: int = Field(default=1, ge=1)
    scene_state_version: int = Field(ge=0)
    coordinate_space: str = Field(min_length=1)
    horizontal_crs: str = Field(min_length=1)
    vertical_datum: str = Field(min_length=1)
    draw_call_count: int = Field(ge=0)
    transform_stride_f32: int = Field(default=16, frozen=True)
    transform_buffer_flat: tuple[float, ...]
    visibility_bitmask: tuple[int, ...]
    lod_indices: tuple[int, ...]
    state_cryptographic_seal: str = Field(min_length=64, max_length=64)

    @field_validator("transform_buffer_flat")
    @classmethod
    def _validate_transform_buffer(cls, value: tuple[float, ...]) -> tuple[float, ...]:
        if not all(math.isfinite(float(item)) for item in value):
            raise ValueError("Transform buffer contains non-finite values.")
        if len(value) % 16 != 0:
            raise ValueError("Transform buffer length must be a multiple of 16.")
        return tuple(float(item) for item in value)

    @field_validator("visibility_bitmask")
    @classmethod
    def _validate_visibility_buffer(cls, value: tuple[int, ...]) -> tuple[int, ...]:
        if any(item not in (0, 1) for item in value):
            raise ValueError("Visibility buffer values must be 0 or 1.")
        return value

    @field_validator("lod_indices")
    @classmethod
    def _validate_lod_buffer(cls, value: tuple[int, ...]) -> tuple[int, ...]:
        if any(item not in (0, 1, 2, 3) for item in value):
            raise ValueError("LoD buffer values must be in the range 0..3.")
        return value

    @field_validator("state_cryptographic_seal")
    @classmethod
    def _validate_seal(cls, value: str) -> str:
        if any(character not in "0123456789abcdef" for character in value.lower()):
            raise ValueError("Cryptographic seal must be a lowercase hexadecimal SHA-256 value.")
        return value.lower()

    @field_validator("draw_call_count")
    @classmethod
    def _validate_draw_count(cls, value: int) -> int:
        if value > 0 and value > 100_000_000:
            raise ValueError("draw_call_count exceeds the supported GPU safety bound.")
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
        if not all(math.isfinite(value) for value in values_list):
            raise ValueError("Cannot pack non-finite GPU float values.")
        return struct.pack(f"<{len(values_list)}f", *values_list)

    @staticmethod
    def pack_u32(values: Iterable[int]) -> bytes:
        """Pack uint32 values using little-endian GPU ABI ordering."""

        values_list = [int(value) for value in values]
        if any(value < 0 or value > 0xFFFFFFFF for value in values_list):
            raise ValueError("Cannot pack a value outside the uint32 range.")
        return struct.pack(f"<{len(values_list)}I", *values_list)
