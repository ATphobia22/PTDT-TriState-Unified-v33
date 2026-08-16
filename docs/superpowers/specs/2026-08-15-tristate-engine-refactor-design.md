# TriStateUnifiedEngine Refactor Design

**Date:** 2026-08-15  
**Repository:** `ATphobia22/PTDT-TriState-Unified-v33`  
**Branch:** `fix/tristate-engine-refactor`

## Goal

Refactor the TriState engineering engine so that numerical inputs, evidence semantics, regulatory findings, coordinate handling, and tests are deterministic and explicit. The refactor must distinguish physical exceedance from regulatory noncompliance and from operational fail-closed states.

## Source and authority boundaries

The implementation will preserve PTDT source terminology and provenance concepts while avoiding unsupported legal conclusions. FEMA/LOMA output will identify evidence-supported candidacy rather than claiming FEMA approval. Regulatory logic will encode threshold tests separately from BFE observations.

Primary spatial reference: EPSG:2966, NAD83 / Indiana West (ftUS). Vertical reference is NAVD88, with GEOID18 documented separately as the geoid model. Mapping coordinates use `[longitude, latitude]`; the existing `latLon` representation remains temporarily for compatibility and is deprecated.

## Architecture

### 1. Input and normalization layer

- Validate required numeric inputs with `Number.isFinite`.
- Reject invalid stage, flow, and supplied floodway delta values with explicit `TypeError`s.
- Safely coerce numeric-string building heights while rejecting non-numeric values.
- Preserve deterministic building-height precedence: explicit meters, explicit feet conversion, levels heuristic, primary fallback.
- Export fallback constants used by tests and downstream deterministic consumers.

Constants:

- `FALLBACK_BUILDING_HEIGHT_M = 7.2`
- `LEVEL_HEIGHT_M = 3.2`

### 2. Evidence model

Use the existing four-state PTDT evidence vocabulary:

- `OBSERVED`
- `DERIVED`
- `MODELED`
- `ADJUDICATED`

Hashes and provenance identifiers remain separate from regulatory conclusions. Coordinates are represented as `[lon, lat]` for mapping consumers.

### 3. Regulatory governor

The governor returns a structured finding rather than collapsing every condition into `compliant=false`.

```ts
interface JurisdictionalComplianceResult {
  jurisdiction: Jurisdiction;
  compliant: boolean | null;
  finding: ComplianceFinding;
  stageFt: number;
  bfeFt: number;
  stageAboveBfeFt: number;
  floodwayDeltaFt: number | null;
  regulatoryThresholdFt: number | null;
  notes: string[];
}
```

Findings:

- `BASELINE`
- `BFE_EXCEEDED`
- `LAG_EXCEEDED`
- `ADVERSE_EFFECT`
- `FLOODWAY_IMPACT`
- `NO_IMPACT_REQUIRED`
- `CRITICAL_EXCEEDED`
- `NOT_EVALUATED`

#### Indiana

BFE exceedance is recorded as a physical/hydrologic condition and does not by itself establish regulatory noncompliance. The Indiana floodway adverse-effect test is evaluated separately using the applicable regulatory flood-elevation increase criterion. LAG exceedance can drive the PTDT critical finding, but it must not suppress other supplied floodway-delta notes.

#### Illinois

The applicable floodway impact test uses the 0.1-ft threshold. A supplied floodway delta greater than 0.1 ft produces a `FLOODWAY_IMPACT` failure and a retained explanatory note. BFE exceedance remains a separate observation.

#### Kentucky

Floodway encroachment no-impact logic is kept separate from the floodway-boundary definition. A supplied encroachment delta greater than zero fails the no-impact test. The engine must not encode a universal zero-rise rule for every Kentucky floodway calculation.

### 4. Operational state machine

Operational state is distinct from regulatory compliance:

- `LIVE_TELEMETRY`
- `DEGRADED_STALE`
- `CRITICAL_INUNDATION`
- `FAIL_CLOSED`

A critical physical condition may cause an operational alarm without asserting that a permitting authority has made a legal determination.

### 5. Coordinate migration

Add:

```ts
coordinates: [number, number]
```

Document ordering explicitly as `[lon, lat]`.

Retain `latLon` as a deprecated compatibility field with a runtime warning when accessed/used, without breaking existing consumers in this release.

### 6. Documentation

Create `src/lib/README-TriStateUnifiedEngine.md` covering:

- purpose and architecture;
- primary CRS and vertical datum terminology;
- coordinate ordering and `latLon` migration;
- building-height normalization precedence and constants;
- jurisdiction-specific compliance semantics;
- examples and error behavior.

## Testing

Use Vitest when a test framework is absent or compatible with the repository. Add/update `package.json` only as necessary to provide a deterministic `test` script and Vitest development dependency.

Required tests:

### Building-height normalization

- explicit meters;
- feet conversion;
- levels heuristic;
- deterministic primary fallback;
- numeric-string inputs;
- invalid values.

### Regulatory evaluation

- Indiana stage just above BFE records BFE exceedance without falsely converting it into universal regulatory failure;
- Illinois delta > 0.1 ft fails floodway criterion and records a note;
- Illinois stage > BFE records warning/observation separately;
- Kentucky delta > 0 fails encroachment no-impact criterion;
- LAG exceedance produces `CRITICAL_EXCEEDED` while preserving floodway notes;
- non-finite stage throws `TypeError`;
- supplied non-finite floodway delta throws `TypeError`.

### Coordinate compatibility

- `coordinates` is `[lon, lat]`;
- legacy `latLon` remains available;
- migration behavior is documented and tested where runtime warning infrastructure permits.

## Error handling

Errors are explicit and deterministic. Invalid numeric inputs fail fast. Regulatory applicability must not be inferred when required data is absent; return `null`/`NOT_EVALUATED` where appropriate. No code path may silently convert missing source evidence into observed evidence.

## Non-goals

- No claim that FEMA, IDNR, Illinois, or Kentucky has approved a project.
- No replacement of certified survey, hydraulic modeling, or agency review with dashboard calculations.
- No unrelated UI rewrite.
- No silent CRS transformation.

## Acceptance criteria

1. TypeScript compiles under the repository's existing strictness settings.
2. Vitest suite covers the specified branches and semantic distinctions.
3. Regulatory findings no longer conflate BFE exceedance with regulatory noncompliance.
4. Coordinate migration is non-breaking and documented.
5. Building-height normalization is deterministic and validated.
6. The design and implementation preserve provenance/evidence-state distinctions.
7. README documents all changed public behavior.
