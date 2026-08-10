# EnKF + Bishop Evidence Graph Binding Design

## Goal

Add EnKF assimilation and Bishop circular-slip stability engines to the repository while binding both to the existing provenance/exchange contracts and explicit model-authority boundaries.

## Architecture

`engine/model_contracts.py` remains the authoritative Evidence Graph contract: `Provenance` carries source model, run/scenario identity, UTC timestamp, datum, and units; `ExchangePayload` carries values, provenance, and status. EnKF is authoritative only for `ASSIMILATION`; Bishop is authoritative for the new `SLOPE_STABILITY` domain. PTDT remains derived/display and does not become a scientific authority.

EnKF uses the scalar analysis equation `K=P/(P+R)` and `x_a=x_f+K(y-x_f)`, with ensemble spread supplying `P`. Bishop uses the iterative Simplified Bishop formulation for circular slip surfaces, with pore pressure represented explicitly per slice.

## Error and promotion semantics

Invalid numerical inputs fail closed with `ValueError`. Only `ModelStatus.VALID` results can be promoted through an authority domain. Provenance source-model mismatches are rejected. Non-converged Bishop results are emitted as `INVALID` and therefore cannot be promoted.

## Testing

Tests cover the EnKF scalar equation, ensemble variance and provenance binding, rejection of non-authoritative provenance, Bishop convergence, Bishop authority registration, and PTDT provenance rejection. Repository-wide JavaScript typecheck/build and existing Python tests remain required CI gates before main integration.

## External accuracy review

USACE documentation confirms that Simplified Bishop assumes a circular slip surface, horizontal interslice forces, vertical force equilibrium, and overall moment equilibrium, with factor of safety requiring iteration. HEC-RAS BSTEM documentation likewise describes iterative Bishop calculations. FHWA guidance confirms circular failure-surface assumptions and use of factor-of-safety calculations for slope stability. EnKF references from NASA confirm ensemble/Kalman filtering as an observation-assimilation approach and highlight covariance/uncertainty handling as material to filter reliability.
