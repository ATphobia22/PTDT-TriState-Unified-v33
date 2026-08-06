# PTDT-TriState-Unified-v33

Unified digital twin + Capacitor iOS app.

## Web
```bash
npm install
npm run dev
```

## iPhone (Capacitor)
```bash
npm install
npm run build
npx cap add ios
npx cap sync ios
npx cap open ios
```
Requires Xcode on macOS. App ID: `com.ptdt.unified.v33`

## Components
- GeoTIFF worker
- MapLibre depth filters + WebGL2 flood shaders
- rasFloodBridge
- PostGIS docker-compose
