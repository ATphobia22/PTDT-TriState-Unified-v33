"""Deterministic tests for the PTDT cinematic runtime core."""

from __future__ import annotations

import math

import numpy as np
import pytest

from engine.cinematic_runtime.camera import PhysicalCameraProfile, ValidatedCameraModel
from engine.cinematic_runtime.crs import CRSRenderSemantics
from engine.cinematic_runtime.lod import CameraFrustum, LoDPolicy, RenderAsset
from engine.cinematic_runtime.manifest import RenderManifestBuilder
from engine.cinematic_runtime.scene_state import AuthoritativeSceneState, EntityStateNode


def test_crs_round_trip_is_deterministic() -> None:
    engine = CRSRenderSemantics()
    first = engine.forward_transform(-88.0135, 37.8935, 377.2)
    second = engine.forward_transform(-88.0135, 37.8935, 377.2)

    assert first == second

    lon, lat, elevation = engine.inverse_transform(first)
    assert math.isclose(lon, -88.0135, abs_tol=1e-8)
    assert math.isclose(lat, 37.8935, abs_tol=1e-8)
    assert elevation == 377.2


def test_crs_rejects_non_finite_input() -> None:
    engine = CRSRenderSemantics()

    with pytest.raises(ValueError):
        engine.forward_transform(float("nan"), 37.8935, 377.2)


def test_camera_projection_uses_webgpu_depth_range() -> None:
    model = ValidatedCameraModel(PhysicalCameraProfile())
    matrix = model.compute_projection_matrix()

    near = -model.profile.near_clip_ft
    far = -model.profile.far_clip_ft
    near_clip = matrix @ np.array([0.0, 0.0, near, 1.0])
    far_clip = matrix @ np.array([0.0, 0.0, far, 1.0])

    assert matrix.shape == (4, 4)
    assert matrix[3, 2] == -1.0
    assert math.isclose(float(near_clip[2] / near_clip[3]), 0.0, abs_tol=1e-5)
    assert math.isclose(float(far_clip[2] / far_clip[3]), 1.0, abs_tol=1e-5)


def test_scene_state_validates_matrix_and_seals_deterministically() -> None:
    state = AuthoritativeSceneState()
    entity = EntityStateNode(
        uuid="building-1",
        asset_class="building",
        local_transform_matrix=(
            1.0, 0.0, 0.0, 0.0,
            0.0, 1.0, 0.0, 0.0,
            0.0, 0.0, 1.0, 0.0,
            10.0, 20.0, 30.0, 1.0,
        ),
    )

    version = state.upsert(entity)
    snapshot_a = state.snapshot()
    snapshot_b = state.snapshot()

    assert version == 1
    assert snapshot_a.seal == snapshot_b.seal
    assert snapshot_a.version == 1

    with pytest.raises(ValueError):
        EntityStateNode(uuid="bad", asset_class="building", local_transform_matrix=(1.0, 2.0))


def test_scene_state_batch_update_increments_version_once() -> None:
    state = AuthoritativeSceneState()
    nodes = [
        EntityStateNode(
            uuid=f"asset-{index}",
            asset_class="building",
            local_transform_matrix=(
                1.0, 0.0, 0.0, 0.0,
                0.0, 1.0, 0.0, 0.0,
                0.0, 0.0, 1.0, 0.0,
                0.0, 0.0, 0.0, 1.0,
            ),
        )
        for index in range(3)
    ]

    assert state.upsert_many(nodes) == 1
    assert len(state.snapshot().entities) == 3


def test_screen_space_lod_uses_visibility_and_projected_size() -> None:
    camera = CameraFrustum(
        position_ft=(0.0, 0.0, 0.0),
        forward=(0.0, 0.0, -1.0),
        up=(0.0, 1.0, 0.0),
        vertical_fov_radians=math.radians(40.0),
        horizontal_fov_radians=math.radians(60.0),
        near_clip_ft=1.0,
        far_clip_ft=10_000.0,
        viewport_width_px=1920,
        viewport_height_px=1080,
    )
    policy = LoDPolicy()

    near_asset = RenderAsset(uuid="near", position_ft=(0.0, 0.0, -50.0), radius_ft=10.0)
    far_asset = RenderAsset(uuid="far", position_ft=(0.0, 0.0, -2000.0), radius_ft=1.0)
    side_asset = RenderAsset(uuid="side", position_ft=(100_000.0, 0.0, -50.0), radius_ft=1.0)

    assert policy.compute(camera, near_asset).lod_index == 3
    assert policy.compute(camera, far_asset).lod_index == 0
    assert policy.compute(camera, side_asset).visible is False


def test_webgpu_manifest_has_fixed_matrix_stride() -> None:
    state = AuthoritativeSceneState()
    state.upsert(
        EntityStateNode(
            uuid="asset-1",
            asset_class="building",
            local_transform_matrix=(
                1.0, 0.0, 0.0, 0.0,
                0.0, 1.0, 0.0, 0.0,
                0.0, 0.0, 1.0, 0.0,
                0.0, 0.0, 0.0, 1.0,
            ),
        )
    )

    manifest = RenderManifestBuilder.build(state)

    assert manifest.draw_call_count == 1
    assert manifest.transform_stride_f32 == 16
    assert len(manifest.transform_buffer_flat) == 16
    assert len(manifest.visibility_bitmask) == 1
    assert len(manifest.lod_indices) == 1
