export const depthColorExpression = [
  "interpolate", ["linear"], ["get", "depth_m"],
  0, "#38bdf8",
  1, "#0ea5e9",
  2, "#1e40af",
  3, "#1e3a8a",
  5, "#0f172a",
] as const;

export const particleDensity = [
  "interpolate", ["linear"], ["get", "depth_m"],
  0, 0.15,
  1, 0.45,
  2, 0.9,
  3, 1.4,
  5, 2.0,
] as const;

export const wetRoadOpacity = [
  "interpolate", ["linear"], ["get", "depth_m"],
  0, 0.08,
  0.3, 0.25,
  0.8, 0.55,
  1.5, 0.8,
] as const;

export const depthFilter = (minDepth = 0.05) =>
  [">", ["get", "depth_m"], minDepth] as const;
