"""Validated physical camera model with WebGPU-compatible projection."""

from __future__ import annotations

import math

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, field_validator


class PhysicalCameraProfile(BaseModel):
    """Physical camera parameters expressed in engineering units."""

    model_config = ConfigDict(frozen=True)

    sensor_width_mm: float = Field(default=27.99, gt=0.0)
    sensor_height_mm: float = Field(default=19.22, gt=0.0)
    focal_length_mm: float = Field(default=50.0, gt=0.0)
    anamorphic_squeeze: float = Field(default=1.0, gt=0.0)
    near_clip_ft: float = Field(default=1.0, gt=0.0)
    far_clip_ft: float = Field(default=10_000.0, gt=0.0)

    @field_validator("far_clip_ft")
    @classmethod
    def _far_must_exceed_near(cls, value: float, info) -> float:
        near = info.data.get("near_clip_ft")
        if near is not None and value <= near:
            raise ValueError("far_clip_ft must be greater than near_clip_ft.")
        return value


class ValidatedCameraModel:
    """Deterministic camera projection generator.

    The returned matrix maps a right-handed camera space where visible points
    have negative Z into WebGPU's NDC depth interval [0, 1].
    """

    def __init__(self, profile: PhysicalCameraProfile) -> None:
        self.profile = profile

    @property
    def aspect_ratio(self) -> float:
        return (
            self.profile.sensor_width_mm
            / self.profile.sensor_height_mm
        ) * self.profile.anamorphic_squeeze

    @property
    def horizontal_fov_radians(self) -> float:
        effective_width = (
            self.profile.sensor_width_mm
            * self.profile.anamorphic_squeeze
        )
        return 2.0 * math.atan(
            effective_width / (2.0 * self.profile.focal_length_mm)
        )

    @property
    def vertical_fov_radians(self) -> float:
        return 2.0 * math.atan(
            self.profile.sensor_height_mm
            / (2.0 * self.profile.focal_length_mm)
        )

    def compute_projection_matrix(self) -> np.ndarray:
        """Return a WebGPU-compatible 4x4 perspective matrix."""

        tan_half_fov_v = math.tan(self.vertical_fov_radians / 2.0)
        near = self.profile.near_clip_ft
        far = self.profile.far_clip_ft

        matrix = np.zeros((4, 4), dtype=np.float32)
        matrix[0, 0] = 1.0 / (self.aspect_ratio * tan_half_fov_v)
        matrix[1, 1] = 1.0 / tan_half_fov_v
        matrix[2, 2] = far / (near - far)
        matrix[2, 3] = (far * near) / (near - far)
        matrix[3, 2] = -1.0
        return matrix

    def validate_projection(self) -> None:
        """Validate key projection invariants used by WebGPU."""

        matrix = self.compute_projection_matrix()
        if matrix.shape != (4, 4):
            raise AssertionError("Projection matrix must be 4x4.")
        if not np.all(np.isfinite(matrix)):
            raise AssertionError("Projection matrix contains non-finite values.")
        if matrix[3, 2] != -1.0:
            raise AssertionError("Projection matrix must use w=-z.")
