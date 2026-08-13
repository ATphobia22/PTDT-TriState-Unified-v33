export interface SceneEvidenceReference {
  readonly evidenceId: string;
  readonly role: "source" | "derived" | "provenance";
}

export interface SceneStateMetadata {
  readonly engineeringStateId: string;
  readonly simulationTimeUtc: string;
  readonly coordinateReferenceSystem: string;
  readonly verticalDatum: string;
  readonly horizontalUnits: "m" | "ft";
  readonly verticalUnits: "m" | "ft";
  readonly algorithmVersion: string;
  readonly sceneSchemaVersion: string;
  readonly evidence: readonly SceneEvidenceReference[];
  readonly sourceArtifactIds: readonly string[];
}

export interface SceneTerrainState {
  readonly elevationArtifactId: string;
  readonly terrainResolutionMeters: number;
  readonly width: number;
  readonly height: number;
}

export interface SceneWaterState {
  readonly depthArtifactId?: string;
  readonly floodMaskArtifactId?: string;
  readonly waterSurfaceArtifactId?: string;
  readonly thresholdMeters: number;
}

export interface SceneBuildingState {
  readonly buildingId: string;
  readonly footprintArtifactId: string;
  readonly terrainElevationMeters: number;
  readonly heightMeters: number;
  readonly baseElevationMeters: number;
  readonly evidenceId: string;
}

export interface SceneState {
  readonly metadata: SceneStateMetadata;
  readonly terrain: SceneTerrainState;
  readonly water: SceneWaterState;
  readonly buildings: readonly SceneBuildingState[];
}

export function assertSceneState(state: SceneState): void {
  if (!state.metadata.engineeringStateId.trim()) {
    throw new Error("engineeringStateId is required");
  }
  if (!state.metadata.simulationTimeUtc.endsWith("Z")) {
    throw new Error("simulationTimeUtc must be UTC ISO-8601");
  }
  if (!state.metadata.coordinateReferenceSystem.trim()) {
    throw new Error("coordinateReferenceSystem is required");
  }
  if (!state.metadata.verticalDatum.trim()) {
    throw new Error("verticalDatum is required");
  }
  if (!Number.isFinite(state.water.thresholdMeters) || state.water.thresholdMeters < 0) {
    throw new Error("water.thresholdMeters must be finite and non-negative");
  }
  if (!Number.isFinite(state.terrain.terrainResolutionMeters) || state.terrain.terrainResolutionMeters <= 0) {
    throw new Error("terrain resolution must be finite and positive");
  }
  if (!Number.isInteger(state.terrain.width) || !Number.isInteger(state.terrain.height)) {
    throw new Error("terrain dimensions must be integers");
  }
  for (const building of state.buildings) {
    if (!building.buildingId.trim() || !building.evidenceId.trim()) {
      throw new Error("building and evidence identifiers are required");
    }
    if (!Number.isFinite(building.heightMeters) || building.heightMeters < 0) {
      throw new Error("building height must be finite and non-negative");
    }
    if (!Number.isFinite(building.baseElevationMeters)) {
      throw new Error("building base elevation must be finite");
    }
  }
}
