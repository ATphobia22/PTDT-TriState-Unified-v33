"""CRS and render-space semantics for the PTDT cinematic runtime."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final

import pyproj
from pydantic import BaseModel, ConfigDict, Field, field_validator


class VerticalReference(BaseModel):
    """Explicit vertical coordinate semantics."""

    model_config = ConfigDict(frozen=True)

    datum: str = Field(default="NAVD88", min_length=1)
    unit: str = Field(default="ftUS", min_length=1)
    realization: str | None = None

    @field_validator("datum", "unit")
    @classmethod
    def _non_empty(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Vertical reference values must not be empty.")
        return value


class RenderCoordinate(BaseModel):
    """A coordinate carrying authoritative and render-space semantics."""

    model_config = ConfigDict(frozen=True)

    x_project_ftus: float
    y_project_ftus: float
    z_navd88_ftus: float
    local_x_ftus: float
    local_y_ftus: float
    local_z_ftus: float
    horizontal_crs: str = "EPSG:2966"
    vertical_reference: VerticalReference = Field(default_factory=VerticalReference)

    @field_validator(
        "x_project_ftus",
        "y_project_ftus",
        "z_navd88_ftus",
        "local_x_ftus",
        "local_y_ftus",
        "local_z_ftus",
    )
    @classmethod
    def _finite(cls, value: float) -> float:
        if not math.isfinite(value):
            raise ValueError("Coordinate values must be finite.")
        return float(value)


@dataclass(frozen=True)
class CRSRenderSemantics:
    """Transform WGS84 coordinates into EPSG:2966 and then local render space.

    EPSG:2966 remains the authoritative projected CRS. The render origin is
    an application-level translation applied after CRS projection so that
    WebGPU single-precision arithmetic remains numerically stable.
    """

    target_epsg: str = "EPSG:2966"
    origin_x_ftus: float = 2_770_000.0
    origin_y_ftus: float = 400_000.0

    _SOURCE_EPSG: Final[str] = "EPSG:4326"

    def __post_init__(self) -> None:
        if not math.isfinite(self.origin_x_ftus) or not math.isfinite(
            self.origin_y_ftus
        ):
            raise ValueError("Render origin values must be finite.")

        source = pyproj.CRS(self._SOURCE_EPSG)
        target = pyproj.CRS(self.target_epsg)
        object.__setattr__(self, "_source_crs", source)
        object.__setattr__(self, "_target_crs", target)
        object.__setattr__(
            self,
            "_transformer",
            pyproj.Transformer.from_crs(source, target, always_xy=True),
        )

    @property
    def horizontal_crs(self) -> str:
        """Return the authoritative projected CRS identifier."""
        return self._target_crs.to_string()

    def forward_transform(
        self,
        lon: float,
        lat: float,
        alt_navd88_ftus: float,
        vertical_reference: VerticalReference | None = None,
    ) -> RenderCoordinate:
        """Transform WGS84 longitude/latitude plus an already-NAVD88 height."""

        if not math.isfinite(lon) or not math.isfinite(lat):
            raise ValueError("Longitude and latitude must be finite.")
        if not -180.0 <= lon <= 180.0:
            raise ValueError("Longitude must be within [-180, 180].")
        if not -90.0 <= lat <= 90.0:
            raise ValueError("Latitude must be within [-90, 90].")
        if not math.isfinite(alt_navd88_ftus):
            raise ValueError("NAVD88 elevation must be finite.")

        x_ftus, y_ftus = self._transformer.transform(lon, lat)
        if not math.isfinite(x_ftus) or not math.isfinite(y_ftus):
            raise RuntimeError("CRS transformation returned a non-finite result.")

        vertical = vertical_reference or VerticalReference()
        local_x = float(x_ftus - self.origin_x_ftus)
        local_y = float(y_ftus - self.origin_y_ftus)
        local_z = float(alt_navd88_ftus)

        return RenderCoordinate(
            x_project_ftus=float(x_ftus),
            y_project_ftus=float(y_ftus),
            z_navd88_ftus=float(alt_navd88_ftus),
            local_x_ftus=local_x,
            local_y_ftus=local_y,
            local_z_ftus=local_z,
            horizontal_crs=self.horizontal_crs,
            vertical_reference=vertical,
        )

    def inverse_transform(
        self,
        coordinate: RenderCoordinate,
    ) -> tuple[float, float, float]:
        """Return WGS84 longitude/latitude plus the unchanged NAVD88 height."""

        if coordinate.horizontal_crs != self.horizontal_crs:
            raise ValueError(
                "Coordinate horizontal CRS does not match this transformer."
            )

        lon, lat = self._transformer.transform(
            coordinate.x_project_ftus,
            coordinate.y_project_ftus,
            direction=pyproj.enums.TransformDirection.INVERSE,
        )
        return float(lon), float(lat), float(coordinate.z_navd88_ftus)
