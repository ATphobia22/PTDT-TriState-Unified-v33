/** Simplified Bishop circular-slip FoS — federal threshold FoS >= 1.40 */
export function simplifiedBishopFoS(params: {
  cohesionKpa: number;
  frictionDeg: number;
  unitWeightKnM3: number;
  slopeHeightM: number;
  slopeAngleDeg: number;
  waterHeightM?: number;
}): number {
  const {
    cohesionKpa,
    frictionDeg,
    unitWeightKnM3,
    slopeHeightM,
    slopeAngleDeg,
    waterHeightM = 0,
  } = params;

  const phi = (frictionDeg * Math.PI) / 180;
  const alpha = (slopeAngleDeg * Math.PI) / 180;
  const c = cohesionKpa;
  const gamma = unitWeightKnM3;
  const H = slopeHeightM;
  const hw = waterHeightM;

  // simplified single-slice approximation
  const W = gamma * H * H * 0.5;
  const u = hw > 0 ? 9.81 * hw * 0.5 : 0;
  const N = W * Math.cos(alpha) - u;
  const resisting = c * H + N * Math.tan(phi);
  const driving = W * Math.sin(alpha);
  if (driving <= 0) return 99;
  return resisting / driving;
}

export const FEDERAL_FOS_THRESHOLD = 1.4;
