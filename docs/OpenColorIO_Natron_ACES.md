# OpenColorIO / Natron ACES Pipeline (TSDES)

## Natron OCIO nodes
1. Preferences → Color Management → set config to `aces_1.3` (or OpenColorIO-Config-ACES).
2. **Read node**: Input/Output = ACEScg (or Linear/raw). Natron Read has built-in OCIO.
3. Composite in **ACEScg** (scene-linear).
4. **OCIOColorSpace** node (not OCIODisplay) after grade:
   - Input: ACEScg
   - Output: sRGB / Rec.709 (ODT)
5. Viewer LUT = **Linear (None)** to avoid double sRGB.
6. **Write**: Input + File colorspace = linear/raw if OCIOColorSpace already applied ODT.

## Working spaces
- Scene-linear: ACEScg
- Display: sRGB (D60 sim) or P3-D65 after RRT+ODT
- Avoid OCIODisplay for pipeline transforms — use OCIOColorSpace only.

## Twin integration
Our Electron/Three path approximates ACES with linear grade + exposure/contrast/sat in `src/cgi/CinematicGrade.ts`.
For offline Natron masters: export EXR linear → OCIOColorSpace ACEScg→sRGB.
