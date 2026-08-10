export interface BuildingEvidenceInput {
  provenanceId: string;
  sourceRecordId: string;
  source: string;
  authority: string;
  role: string;
  verticalDatum: string | null;
  units: string | null;
  payload: Record<string, unknown>;
  parentIds: string[];
}

export interface BuildingElevationRelationship {
  buildingProvenanceId: string;
  terrainProvenanceId: string;
  verticalDatum: string;
  buildingElevationFt: number;
  terrainElevationFt: number;
  deltaFt: number;
}

export interface BuildingBFERelationship {
  buildingProvenanceId: string;
  bfeProvenanceId: string;
  verticalDatum: string;
  buildingElevationFt: number;
  bfeFt: number;
  deltaFt: number;
}

function requireSameDatum(left: string | null, right: string | null): string {
  if (!left || !right || left !== right) throw new Error("Building relationship requires matching vertical datums");
  return left;
}

function finite(value: unknown, name: string): number {
  if (typeof value !== "number" || !Number.isFinite(value)) throw new Error(`${name} must be finite`);
  return value;
}

export function buildingToTerrainRelationship(
  building: BuildingEvidenceInput,
  terrain: BuildingEvidenceInput,
): BuildingElevationRelationship {
  const verticalDatum = requireSameDatum(building.verticalDatum, terrain.verticalDatum);
  return {
    buildingProvenanceId: building.provenanceId,
    terrainProvenanceId: terrain.provenanceId,
    verticalDatum,
    buildingElevationFt: finite(building.payload.elevation_ft, "building elevation"),
    terrainElevationFt: finite(terrain.payload.elevation_ft, "terrain elevation"),
    deltaFt: finite(building.payload.elevation_ft, "building elevation") - finite(terrain.payload.elevation_ft, "terrain elevation"),
  };
}

export function buildingToBFERelationship(
  building: BuildingEvidenceInput,
  bfe: BuildingEvidenceInput,
): BuildingBFERelationship {
  const verticalDatum = requireSameDatum(building.verticalDatum, bfe.verticalDatum);
  const buildingElevationFt = finite(building.payload.elevation_ft, "building elevation");
  const bfeFt = finite(bfe.payload.bfe_ft, "BFE");
  return {
    buildingProvenanceId: building.provenanceId,
    bfeProvenanceId: bfe.provenanceId,
    verticalDatum,
    buildingElevationFt,
    bfeFt,
    deltaFt: buildingElevationFt - bfeFt,
  };
}

export function derivedBuildingEvidence(
  source: BuildingEvidenceInput,
  payload: Record<string, unknown>,
  parentIds: string[],
): BuildingEvidenceInput {
  return {
    provenanceId: "",
    sourceRecordId: `derived:${source.sourceRecordId}`,
    source: "PTDT-Layer19",
    authority: "derived",
    role: "building-structural-context",
    verticalDatum: source.verticalDatum,
    units: source.units,
    payload,
    parentIds: [...new Set(parentIds)].sort(),
  };
}
