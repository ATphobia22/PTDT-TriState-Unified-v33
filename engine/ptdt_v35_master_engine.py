from __future__ import annotations

import hashlib
import math
import struct
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Mapping, Sequence

import rfc8785


@dataclass(frozen=True, slots=True)
class SovereignSiteConstants:
    """Configuration values; authoritative source records must override defaults."""

    site_name: str = "PTDT"
    engineering_crs: str = "EPSG:2966"
    vertical_datum: str = "NAVD88"
    bfe_ft: float = 375.0
    lag_ft: float = 377.2
    ffe_ft: float = 382.5
    anchor_lon_lat: tuple[float, float] = (-88.0007, 37.9035)


@dataclass(slots=True)
class EvidenceNode:
    node_id: str
    provenance_id: str
    authority: str
    validation_status: str
    payload: dict[str, Any]
    parent_ids: list[str] = field(default_factory=list)
    payload_hash: str = ""
    timestamp_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def canonical_bytes(self) -> bytes:
        document = {
            "authority": self.authority,
            "parents": sorted(self.parent_ids),
            "payload": self.payload,
            "provenance_id": self.provenance_id,
        }
        return rfc8785.dumps(document)

    def compute_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()

    def seal(self) -> None:
        self.payload_hash = self.compute_hash()

    def verify_integrity(self) -> bool:
        return bool(self.payload_hash) and self.payload_hash == self.compute_hash()


class SpatialTransformBridge:
    """WGS84 geographic -> ECEF conversion for ellipsoidal height.

    NAVD88 orthometric heights must be converted to ellipsoidal height using an
    explicit geoid model before calling ``wgs84_to_ecef``. This class therefore
    intentionally does not pretend that NAVD88 == WGS84 ellipsoidal height.
    """

    _A = 6378137.0
    _F = 1.0 / 298.257223563
    _E2 = _F * (2.0 - _F)
    _WEB_MERCATOR_MAX_LAT = 85.0511287798066

    @classmethod
    def wgs84_to_ecef(cls, lon_deg: float, lat_deg: float, ellipsoid_height_m: float) -> tuple[float, float, float]:
        if not all(math.isfinite(v) for v in (lon_deg, lat_deg, ellipsoid_height_m)):
            raise ValueError("ECEF input coordinates must be finite")
        if not -180.0 <= lon_deg <= 180.0 or not -90.0 <= lat_deg <= 90.0:
            raise ValueError("longitude/latitude outside WGS84 bounds")

        lon = math.radians(lon_deg)
        lat = math.radians(lat_deg)
        sin_lat = math.sin(lat)
        cos_lat = math.cos(lat)
        n = cls._A / math.sqrt(1.0 - cls._E2 * sin_lat * sin_lat)
        x = (n + ellipsoid_height_m) * cos_lat * math.cos(lon)
        y = (n + ellipsoid_height_m) * cos_lat * math.sin(lon)
        z = (n * (1.0 - cls._E2) + ellipsoid_height_m) * sin_lat
        return x, y, z

    @classmethod
    def lonlat_to_slippy_tile(cls, lon_deg: float, lat_deg: float, zoom: int = 15) -> tuple[int, int]:
        if not 0 <= zoom <= 30:
            raise ValueError("zoom must be between 0 and 30")
        if not math.isfinite(lon_deg) or not math.isfinite(lat_deg):
            raise ValueError("tile coordinates must be finite")
        lon = max(-180.0, min(180.0, lon_deg))
        lat = max(-cls._WEB_MERCATOR_MAX_LAT, min(cls._WEB_MERCATOR_MAX_LAT, lat_deg))
        n = 2**zoom
        x = min(n - 1, max(0, int((lon + 180.0) / 360.0 * n)))
        lat_rad = math.radians(lat)
        y = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) * 0.5 * n)
        y = min(n - 1, max(0, y))
        return x, y


class NeuralDepthOptimizer:
    """Validate and transform a packed float32 depth buffer without fabrication."""

    def __init__(self, width: int = 256, height: int = 256) -> None:
        if width <= 0 or height <= 0:
            raise ValueError("depth dimensions must be positive")
        self.width = width
        self.height = height
        self.total_pixels = width * height

    def process(self, raw_binary_stream: bytes, rejection_threshold_ft: float) -> tuple[bytes, str, int]:
        expected_bytes = self.total_pixels * 4
        if len(raw_binary_stream) != expected_bytes:
            raise ValueError(f"expected {expected_bytes} bytes, received {len(raw_binary_stream)}")
        if not math.isfinite(rejection_threshold_ft):
            raise ValueError("rejection threshold must be finite")

        values = struct.iter_unpack("<f", raw_binary_stream)
        output = bytearray(expected_bytes)
        rejected = 0
        offset = 0
        for (value,) in values:
            if not math.isfinite(value) or value <= rejection_threshold_ft:
                value = float("nan")
                rejected += 1
            struct.pack_into("<f", output, offset, value)
            offset += 4
        digest = hashlib.sha256(output).hexdigest()
        return bytes(output), digest, rejected


class MasterSynthesisOrchestrator:
    def __init__(self, constants: SovereignSiteConstants | None = None) -> None:
        self.constants = constants or SovereignSiteConstants()
        self.registry: dict[str, EvidenceNode] = {}
        self.spatial = SpatialTransformBridge()
        self.neural = NeuralDepthOptimizer()

    def register(self, node: EvidenceNode) -> None:
        if not node.verify_integrity():
            raise ValueError("evidence node integrity verification failed")
        for parent_id in node.parent_ids:
            if parent_id not in self.registry:
                raise ValueError(f"unknown evidence parent: {parent_id}")
        if node.node_id in self.registry:
            raise ValueError(f"duplicate evidence node: {node.node_id}")
        node_ids = set(node.parent_ids)
        if node.node_id in node_ids:
            raise ValueError("evidence graph cycle detected")
        self.registry[node.node_id] = node

    def synthesize(self, stage_ft: float, flow_cfs: float, depth_buffer: bytes | None = None) -> dict[str, Any]:
        if not math.isfinite(stage_ft) or not math.isfinite(flow_cfs):
            raise ValueError("telemetry values must be finite")

        observation = EvidenceNode(
            node_id=f"obs-{len(self.registry):08d}",
            provenance_id="telemetry-ingest",
            authority="configured-data-source",
            validation_status="validated",
            payload={"stage_ft": stage_ft, "flow_cfs": flow_cfs},
        )
        observation.seal()
        self.register(observation)

        spatial = {
            "engineering_crs": self.constants.engineering_crs,
            "vertical_datum": self.constants.vertical_datum,
            "anchor_lon_lat": list(self.constants.anchor_lon_lat),
        }
        spatial_node = EvidenceNode(
            node_id=f"spatial-{len(self.registry):08d}",
            provenance_id="spatial-alignment",
            authority="ptdt-geospatial-bridge",
            validation_status="validated",
            payload=spatial,
            parent_ids=[observation.node_id],
        )
        spatial_node.seal()
        self.register(spatial_node)

        neural = None
        if depth_buffer is not None:
            _, digest, rejected = self.neural.process(depth_buffer, self.constants.bfe_ft)
            neural = {"sha256": digest, "rejected_points": rejected}

        return {
            "site": asdict(self.constants),
            "telemetry": observation.payload,
            "spatial": spatial_node.payload,
            "neural": neural,
            "evidence_head": spatial_node.payload_hash,
        }
