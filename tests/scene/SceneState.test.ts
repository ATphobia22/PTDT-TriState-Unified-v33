import assert from "node:assert/strict";
import test from "node:test";
import { assertSceneState, type SceneState } from "../../src/scene/SceneState.ts";

function createValidSceneState(): SceneState {
  return {
    metadata: {
      engineeringStateId: "eng-001",
      simulationTimeUtc: "2026-08-13T00:00:00Z",
      coordinateReferenceSystem: "EPSG:26916",
      verticalDatum: "NAVD88",
      horizontalUnits: "m",
      verticalUnits: "m",
      algorithmVersion: "ptdt-test-1",
      sceneSchemaVersion: "1.0.0",
      evidence: [{ evidenceId: "ev-001", role: "source" }],
      sourceArtifactIds: ["terrain-001"],
    },
    terrain: {
      elevationArtifactId: "dem-001",
      terrainResolutionMeters: 1,
      width: 128,
      height: 128,
    },
    water: {
      depthArtifactId: "depth-001",
      floodMaskArtifactId: "mask-001",
      thresholdMeters: 0.1,
    },
    buildings: [
      {
        buildingId: "bldg-001",
        footprintArtifactId: "footprint-001",
        terrainElevationMeters: 300,
        heightMeters: 8,
        baseElevationMeters: 300,
        evidenceId: "ev-bldg-001",
      },
    ],
  };
}

test("SceneState accepts a valid engineering-to-scene contract", () => {
  assert.doesNotThrow(() => assertSceneState(createValidSceneState()));
});

test("SceneState rejects non-UTC simulation timestamps", () => {
  const state = createValidSceneState();
  const invalidState: SceneState = {
    ...state,
    metadata: { ...state.metadata, simulationTimeUtc: "2026-08-13T00:00:00" },
  };
  assert.throws(() => assertSceneState(invalidState), /UTC ISO-8601/);
});

test("SceneState rejects invalid terrain dimensions", () => {
  const state = createValidSceneState();
  const invalidState: SceneState = {
    ...state,
    terrain: { ...state.terrain, width: 0 },
  };
  assert.throws(() => assertSceneState(invalidState), /dimensions must be integers/);
});

test("SceneState rejects negative water thresholds", () => {
  const state = createValidSceneState();
  const invalidState: SceneState = {
    ...state,
    water: { ...state.water, thresholdMeters: -0.01 },
  };
  assert.throws(() => assertSceneState(invalidState), /non-negative/);
});

test("SceneState preserves terrain-relative building base semantics", () => {
  const state = createValidSceneState();
  assert.equal(
    state.buildings[0].baseElevationMeters,
    state.buildings[0].terrainElevationMeters,
  );
  assert.doesNotThrow(() => assertSceneState(state));
});
