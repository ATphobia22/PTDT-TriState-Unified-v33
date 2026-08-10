/** ACES-inspired linear grade + atmospheric modulation for Tri-State Twin */
export interface GradeParams {
  exposure: number;
  contrast: number;
  saturation: number;
  grain: number;
  fogDensity: number;
  flareIntensity: number;
}

export function gradeFromFloodDepth(depth_m: number): GradeParams {
  // quadratic ease as torrent peaks
  const t = Math.min(1, depth_m / 5);
  const ease = t * t;
  return {
    exposure: 1.05 - ease * 0.35,
    contrast: 1.1 + ease * 0.2,
    saturation: 1.0 - ease * 0.45,
    grain: 0.04 + ease * 0.08,
    fogDensity: 0.006 + ease * 0.02,
    flareIntensity: 0.15 + ease * 0.35,
  };
}

export function applyCanvasGrade(
  ctx: CanvasRenderingContext2D,
  w: number,
  h: number,
  params: GradeParams
) {
  const img = ctx.getImageData(0, 0, w, h);
  const d = img.data;
  for (let i = 0; i < d.length; i += 4) {
    let r = d[i] / 255;
    let g = d[i + 1] / 255;
    let b = d[i + 2] / 255;
    // exposure
    r *= params.exposure;
    g *= params.exposure;
    b *= params.exposure;
    // contrast around mid-gray
    r = (r - 0.5) * params.contrast + 0.5;
    g = (g - 0.5) * params.contrast + 0.5;
    b = (b - 0.5) * params.contrast + 0.5;
    // saturation
    const l = 0.2126 * r + 0.7152 * g + 0.0722 * b;
    r = l + (r - l) * params.saturation;
    g = l + (g - l) * params.saturation;
    b = l + (b - l) * params.saturation;
    // film grain
    const n = (Math.random() - 0.5) * params.grain;
    r += n;
    g += n;
    b += n;
    d[i] = Math.max(0, Math.min(255, r * 255));
    d[i + 1] = Math.max(0, Math.min(255, g * 255));
    d[i + 2] = Math.max(0, Math.min(255, b * 255));
  }
  ctx.putImageData(img, 0, 0);
}
