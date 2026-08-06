export type WeatherMode = 'clear' | 'mist' | 'heavyRain';

export interface WeatherParams {
  mode: WeatherMode;
  fogDensity: number;
  particleMultiplier: number;
  rainIntensity: number;
  waterOpacity: number;
}

export function resolveWeather(depth_m: number): WeatherParams {
  if (depth_m < 0.5) {
    return { mode: 'clear', fogDensity: 0.006, particleMultiplier: 0.8, rainIntensity: 0, waterOpacity: 0.45 };
  }
  if (depth_m < 3.0) {
    return { mode: 'mist', fogDensity: 0.014, particleMultiplier: 1.1, rainIntensity: 0.4, waterOpacity: 0.65 };
  }
  return { mode: 'heavyRain', fogDensity: 0.022, particleMultiplier: 1.5, rainIntensity: 1.0, waterOpacity: 0.82 };
}
