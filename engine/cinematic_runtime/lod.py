"""Camera-aware frustum and screen-space Level-of-Detail controller."""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from pydantic import BaseModel, ConfigDict, Field, field_validator


class RenderAsset(BaseModel):
    """Render-space asset bounding sphere."""

    model_config = ConfigDict(frozen=True)

    uuid: str = Field(min_length=1)
    position_ft: tuple[float, float, float]
    radius_ft: float = Field(gt=0.0)

    @field_validator("position_ft")
    @classmethod
    def _validate_position(
        cls,
        value: tuple[float, float, float],
    ) -> tuple[float, float, float]:
        if len(value) != 3 or not all(math.isfinite(float(v)) for v in value):
            raise ValueError("Asset position must be a finite 3-vector.")
        return tuple(float(v) for v in value)


@dataclass(frozen=True)
class CameraFrustum:
    """Camera pose and viewport parameters used by the LoD controller."""

    position_ft: tuple[float, float, float]
    forward: tuple[float, float, float]
    up: tuple[float, float, float]
    vertical_fov_radians: float
    horizontal_fov_radians: float
    near_clip_ft: float
    far_clip_ft: float
    viewport_width_px: int
    viewport_height_px: int

    def __post_init__(self) -> None:
        if self.viewport_width_px <= 0 or self.viewport_height_px <= 0:
            raise ValueError("Viewport dimensions must be positive.")
        if self.near_clip_ft <= 0 or self.far_clip_ft <= self.near_clip_ft:
            raise ValueError("Invalid camera clip range.")

        forward = np.asarray(self.forward, dtype=np.float64)
        up = np.asarray(self.up, dtype=np.float64)
        if not np.all(np.isfinite(forward)) or not np.all(np.isfinite(up)):
            raise ValueError("Camera vectors must be finite.")
        if np.linalg.norm(forward) == 0 or np.linalg.norm(up) == 0:
            raise ValueError("Camera vectors must be non-zero.")

    def _basis(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        forward = np.asarray(self.forward, dtype=np.float64)
        forward /= np.linalg.norm(forward)

        up = np.asarray(self.up, dtype=np.float64)
        up -= forward * np.dot(up, forward)
        up /= np.linalg.norm(up)

        right = np.cross(forward, up)
        right /= np.linalg.norm(right)
        return right, up, forward

    def sphere_visibility(
        self,
        position_ft: tuple[float, float, float],
        radius_ft: float,
    ) -> tuple[bool, float, float]:
        """Return visibility, camera-space forward distance, and projected diameter."""

        right, up, forward = self._basis()
        delta = np.asarray(position_ft, dtype=np.float64) - np.asarray(
            self.position_ft,
            dtype=np.float64,
        )

        x = float(np.dot(delta, right))
        y = float(np.dot(delta, up))
        z = float(np.dot(delta, forward))

        if z + radius_ft < self.near_clip_ft:
            return False, z, 0.0
        if z - radius_ft > self.far_clip_ft:
            return False, z, 0.0

        tan_h = math.tan(self.horizontal_fov_radians / 2.0)
        tan_v = math.tan(self.vertical_fov_radians / 2.0)

        if abs(x) > z * tan_h + radius_ft:
            return False, z, 0.0
        if abs(y) > z * tan_v + radius_ft:
            return False, z, 0.0

        depth = max(z, self.near_clip_ft)
        projected_radius_px = (
            radius_ft
            / depth
            * self.viewport_height_px
            / (2.0 * tan_v)
        )
        return True, z, float(projected_radius_px * 2.0)


@dataclass(frozen=True)
class LoDDecision:
    """Deterministic visibility and LoD result."""

    visible: bool
    lod_index: int
    distance_ft: float
    projected_diameter_px: float


class LoDPolicy(BaseModel):
    """Screen-space-error LoD policy.

    Thresholds are expressed as projected diameter in pixels. The first
    threshold is the minimum diameter for LoD 3, the second for LoD 2, and the
    third for LoD 1. Values below the third threshold use LoD 0.
    """

    model_config = ConfigDict(frozen=True)

    lod3_min_px: float = Field(default=120.0, gt=0.0)
    lod2_min_px: float = Field(default=48.0, gt=0.0)
    lod1_min_px: float = Field(default=12.0, gt=0.0)

    @field_validator("lod2_min_px", "lod1_min_px")
    @classmethod
    def _positive(cls, value: float) -> float:
        return value

    def model_post_init(self, __context) -> None:
        if not self.lod3_min_px > self.lod2_min_px > self.lod1_min_px:
            raise ValueError(
                "LoD pixel thresholds must satisfy LoD3 > LoD2 > LoD1."
            )

    def compute(
        self,
        frustum: CameraFrustum,
        asset: RenderAsset,
    ) -> LoDDecision:
        visible, distance_ft, diameter_px = frustum.sphere_visibility(
            asset.position_ft,
            asset.radius_ft,
        )
        if not visible:
            return LoDDecision(
                visible=False,
                lod_index=0,
                distance_ft=float(distance_ft),
                projected_diameter_px=0.0,
            )

        if diameter_px >= self.lod3_min_px:
            lod_index = 3
        elif diameter_px >= self.lod2_min_px:
            lod_index = 2
        elif diameter_px >= self.lod1_min_px:
            lod_index = 1
        else:
            lod_index = 0

        return LoDDecision(
            visible=True,
            lod_index=lod_index,
            distance_ft=float(distance_ft),
            projected_diameter_px=float(diameter_px),
        )
