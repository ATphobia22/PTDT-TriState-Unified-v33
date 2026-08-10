# Natron Plugin Development (OpenFX)

## Stack
- Host: Natron (OpenFX)
- API: devernay/openfx Support layer (C++)
- Official plugin repos: openfx-io, openfx-misc, openfx-arena

## Minimal plugin layout
```
MyPlugin/
  MyPlugin.cpp      # factory + plugin class
  Makefile
  Info.plist        # (macOS bundle)
```

## Build (Linux/macOS pattern)
```bash
git clone https://github.com/devernay/openfx.git
git clone https://github.com/NatronGitHub/openfx-arena.git
cd openfx-arena && git submodule update -i --recursive
make CONFIG=release
# install to /usr/OFX/Plugins or ~/OFX/Plugins
```

Windows: use nmake + OFX headers; install to
`C:\Program Files\Common Files\OFX\Plugins`

## TSDES use
Custom OFX for flood-depth-driven grade (depth→exposure/fog) can wrap the same math as `src/cgi/CinematicGrade.ts`.
