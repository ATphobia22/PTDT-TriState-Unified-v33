export const depthColorExpression = [
  "interpolate", ["linear"], ["get", "depth_m"],
  0, "#38bdf8", 1, "#0ea5e9", 2, "#1e40af", 3, "#1e3a8a"
];
export const particleDensity = [
  "interpolate", ["linear"], ["get", "depth_m"],
  0, 0.2, 1, 0.5, 2, 1.0, 3, 1.5
];
export const wetRoadOpacity = [
  "interpolate", ["linear"], ["get", "depth_m"],
  0, 0.1, 0.5, 0.4, 1.0, 0.7
];
