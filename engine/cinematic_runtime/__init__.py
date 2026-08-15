"""PTDT cinematic runtime core.

Deterministic geospatial, camera, SceneState, LoD, manifest, and streaming
primitives for the PTDT render/synchronization plane.
"""

from .camera import PhysicalCameraProfile, ValidatedCameraModel
from .crs import CRSRenderSemantics, RenderCoordinate, VerticalReference
from .lod import CameraFrustum, LoDDecision, LoDPolicy, RenderAsset
from .manifest import RenderManifestBuilder, WebGPUBufferManifest
from .scene_state import AuthoritativeSceneState, EntityStateNode
from .streaming import (
    ClientProtocolMessage,
    SceneStreamMessage,
    SpatialConnectionManager,
)

__all__ = [
    "AuthoritativeSceneState",
    "CRSRenderSemantics",
    "CameraFrustum",
    "ClientProtocolMessage",
    "EntityStateNode",
    "LoDDecision",
    "LoDPolicy",
    "PhysicalCameraProfile",
    "RenderAsset",
    "RenderCoordinate",
    "RenderManifestBuilder",
    "SceneStreamMessage",
    "SpatialConnectionManager",
    "ValidatedCameraModel",
    "VerticalReference",
    "WebGPUBufferManifest",
]
