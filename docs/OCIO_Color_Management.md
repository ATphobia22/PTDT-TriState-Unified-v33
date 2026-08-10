# OpenColorIO Color Management

## Core concepts
- **Config** (.ocio): colorspaces, roles, displays, views, looks
- **Reference space**: hub connecting all colorspaces
- **Roles** (task aliases → actual spaces):
  - `scene_linear` / `rendering` / `compositing_linear` → ACEScg
  - `color_timing` → ACEScc / ACEScct
  - `compositing_log` → ADX10 or log working space
  - `color_picking` → display-referred (sRGB)
  - `data` → Raw (non-color)
  - `aces_interchange` → ACES2065-1 (config interchange)

## ACES typical roles
```yaml
roles:
  scene_linear: ACES - ACEScg
  rendering: ACES - ACEScg
  compositing_linear: ACES - ACEScg
  color_timing: ACES - ACEScc
  color_picking: Output - sRGB
  data: Utility - Raw
  default: ACES - ACES2065-1
```

## Pipeline
Input IDT → scene_linear (ACEScg) → grade/looks → Display View (RRT+ODT)

Natron: OCIOColorSpace for transforms; Viewer = Linear; never double sRGB.
Twin runtime: approximate with `src/cgi/CinematicGrade.ts` (linear exposure/contrast/sat).
