# PTDT Model Authority Boundaries

## Purpose

PTDT separates regulatory constraints, numerical model state, data assimilation, and presentation. A model may publish through an exchange contract without acquiring authority over another subsystem.

| Domain | Authoritative subsystem | Promotion rule |
|---|---|---|
| Regulatory elevation/storage | Archimedes | Deterministic checks only |
| River hydraulics | HEC-RAS | Valid HEC-RAS run/result |
| Groundwater | MODFLOW6 | Valid, fresh, validated output |
| Assimilation | EnKF | Valid observation/model fusion |
| Derived/display state | PTDT | Derived from accepted upstream state |

## MODFLOW6 failure semantics

A MODFLOW6 run is never promoted merely because the process starts or exits with code zero. PTDT rejects missing executables, invalid inputs, timeouts, nonzero exits, solver non-convergence, missing outputs, empty outputs, and stale outputs. A failed run remains `FAILED`; the last valid groundwater state may be retained separately as stale historical state.

## HEC-RAS -> MODFLOW6

The initial exchange is intentionally one-way. HEC-RAS supplies an explicitly declared river stage boundary with NAVD88/feet, timestamp, river ID, run ID, and scenario ID. The exchange adapter produces a contract; it does not mutate MODFLOW internals. A later MODFLOW execution consumes that contract and can publish validated groundwater heads back to PTDT as a separate exchange.

## Archimedes boundary

Archimedes owns regulatory BFE and compensatory-storage checks. It does **not** own river hydraulics, groundwater heads, numerical solver convergence, or EnKF assimilation. Its existing constants and formulas remain unchanged: BFE 375.0 ft NAVD88, site LAG 377.2 ft, and compensatory storage 1.20x.

## Provenance requirements

Every cross-model value carries:

- source model
- run ID
- scenario ID
- UTC timestamp
- datum
- units
- status

No UI component is allowed to infer scientific authority from visualization state.
