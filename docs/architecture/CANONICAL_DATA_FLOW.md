# Canonical data flow

```text
source observations / terrain / footprints / regulatory text
                         |
                         v
                 Authoritative Evidence Graph
                         |
              +----------+-----------+
              |                      |
              v                      v
        validated model inputs   building context
              |                      |
       +------+------+               |
       |      |     |               |
     HEC-RAS MODFLOW EnKF          Layer 19
       |      |     |               |
       +------+------+               |
              v                      |
        derived model evidence <-----+
              |
       +------+------+
       |             |
     Bishop      Archimedes
       |             |
       +------+------+
              v
       regulatory evaluation
              |
              v
      derived compliance evidence
              |
              v
      PTDT read-only projection
              |
      +-------+--------+
      |                |
   MapLibre          WebGPU/HUD
```

## Prohibited path

`MapLibre geometry -> engineering calculation -> regulatory conclusion` is not an allowed data path.

## Building/BFE relationship

Building elevation and BFE must be provenance-bearing evidence records with matching vertical datum. The relationship result is derived evidence and is not inferred from rendered extrusion height.

## Regulatory evaluation

The governor consumes the hydraulic model result identified by provenance and a versioned rule record. Missing evidence, mismatched jurisdiction, stale model status, or wrong scope yields `NOT_EVALUATED` rather than a guessed certification.
