import * as THREE from 'three';

export interface CameraTrack {
  name: string;
  positions: THREE.Vector3[];
  lookAt: THREE.Vector3;
  focalLength: number; // mm
  duration: number;    // seconds
}

export const BONEBANK_TRACKS: CameraTrack[] = [
  {
    name: 'Wide Establishing Aerial',
    positions: [
      new THREE.Vector3(40, 35, 40),
      new THREE.Vector3(20, 28, 50),
      new THREE.Vector3(-10, 30, 45),
    ],
    lookAt: new THREE.Vector3(0, 0, 0),
    focalLength: 28,
    duration: 12,
  },
  {
    name: 'Bonebank Homestead Track',
    positions: [
      new THREE.Vector3(8, 6, 14),
      new THREE.Vector3(4, 5, 10),
      new THREE.Vector3(0, 4.5, 8),
    ],
    lookAt: new THREE.Vector3(0, 1.5, 0),
    focalLength: 65,
    duration: 10,
  },
  {
    name: 'Ohio-Wabash Confluence',
    positions: [
      new THREE.Vector3(-30, 22, -25),
      new THREE.Vector3(-15, 18, -35),
      new THREE.Vector3(5, 20, -40),
    ],
    lookAt: new THREE.Vector3(0, 0, -10),
    focalLength: 35,
    duration: 14,
  },
];

export class CinematicCameraController {
  camera: THREE.PerspectiveCamera;
  private track: CameraTrack | null = null;
  private t = 0;
  private active = false;

  constructor(camera: THREE.PerspectiveCamera) {
    this.camera = camera;
  }

  play(track: CameraTrack) {
    this.track = track;
    this.t = 0;
    this.active = true;
    // approximate FOV from focal length (full-frame 36mm)
    this.camera.fov = 2 * Math.atan(18 / track.focalLength) * (180 / Math.PI);
    this.camera.updateProjectionMatrix();
  }

  update(dt: number) {
    if (!this.active || !this.track) return;
    this.t += dt;
    const u = Math.min(1, this.t / this.track.duration);
    const ease = u * u * (3 - 2 * u); // smoothstep

    const pts = this.track.positions;
    if (pts.length < 2) return;

    const seg = Math.min(pts.length - 2, Math.floor(ease * (pts.length - 1)));
    const localT = (ease * (pts.length - 1)) - seg;
    const pos = new THREE.Vector3().lerpVectors(pts[seg], pts[seg + 1], localT);

    this.camera.position.copy(pos);
    this.camera.lookAt(this.track.lookAt);

    if (u >= 1) this.active = false;
  }
}
