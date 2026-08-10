# ACES Pipeline Node Graph (Natron)

```
[Read EXR/Plate]
  FileColorspace: Linear / ACEScg
  Output: ACEScg
        |
        v
[Grade / ColorCorrect]     ← linear ops only (gain, sat, contrast)
        |
        v
[Glow] + [LensDistortion]  ← atmospheric mist / anamorphic
        |
        v
[OCIOColorSpace]           ← NOT OCIODisplay
  Input:  ACEScg
  Output: sRGB  (or P3-D65)
        |
        v
[Write]
  Input colorspace: sRGB (or match OCIO output)
  File colorspace:  sRGB

Viewer LUT = Linear (None)
```

## Config
- Natron Preferences → Color Management → `aces_1.3` or OpenColorIO-Config-ACES
- Working space: ACEScg
- Never double-apply sRGB (Viewer + Write)
