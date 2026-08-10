# OpenFX Plugin Architecture (Natron)

## Layers
1. **C API** — raw OFX (ofxCore, ofxImageEffect)
2. **Support layer** (C++) — Natron/devernay fork: factory + plugin class + params

## Plugin objects
- **Factory** — describes plugin, creates instances on host load
- **Plugin instance** — render(), parameter change, clips
- **Bundle** — `MyPlugin.ofx.bundle` (Windows: under `Common Files\OFX\Plugins`)

## Build sources
- https://github.com/devernay/openfx (headers + Support)
- https://github.com/NatronGitHub/openfx-arena (extra plugins)
- https://github.com/NatronGitHub/openfx-io (I/O + OCIO/OIIO)

```bash
git clone --recursive https://github.com/NatronGitHub/openfx-arena
cd openfx-arena && make CONFIG=release
# install *.ofx.bundle → OFX Plugins path
```

## TSDES custom plugin idea
OFX that reads depth float channel → modulates exposure/fog (same math as CinematicGrade).
