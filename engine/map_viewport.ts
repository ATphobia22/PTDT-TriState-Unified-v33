import maplibregl from 'maplibre-gl';

/** MapLibre viewport with resize + WebGL context-loss recovery. */
export class EngineViewportManager {
  private map: maplibregl.Map;

  constructor(containerId: string, styleUrl: string) {
    this.map = new maplibregl.Map({
      container: containerId,
      style: styleUrl,
      center: [-87.935, 37.892],
      zoom: 12,
      pitch: 45,
      antialias: true,
    });

    this.initResizeObserver(containerId);
  }

  private initResizeObserver(containerId: string): void {
    const container = document.getElementById(containerId);
    if (!container) return;

    const observer = new ResizeObserver(() => {
      requestAnimationFrame(() => {
        this.map?.resize();
      });
    });

    observer.observe(container);
  }

  public forceContextRestore(): void {
    const canvas = this.map.getCanvas();
    const gl =
      (canvas.getContext('webgl2') as WebGL2RenderingContext | null) ||
      (canvas.getContext('webgl') as WebGLRenderingContext | null);
    if (gl && gl.isContextLost()) {
      console.warn('[EngineViewport] Context loss detected. Triggering map repaint...');
      this.map.triggerRepaint();
    }
  }

  public getMap(): maplibregl.Map {
    return this.map;
  }
}
