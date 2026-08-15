# PMTiles viewer + Tippecanoe optimize

## Libraries

| Tool | Role |
|---|---|
| **pmtiles** (npm, already in package.json) | `Protocol` + `pmtiles://` for MapLibre |
| **pmtiles.io** | Web inspector for any archive URL |
| **go-pmtiles** | CLI convert/upload |
| **@loaders.gl/pmtiles** | deck.gl / loaders path (optional) |

MapLibre registration (once):

```ts
import { Protocol } from "pmtiles";
maplibregl.addProtocol("pmtiles", new Protocol().tile);
// source url: "pmtiles://https://host/file.pmtiles" or local via static server
```

## Tippecanoe (parcels)

```bash
tippecanoe -o out.pmtiles -zg -Z10 -l parcels \
  --drop-densest-as-needed \
  --extend-zooms-if-still-dropping \
  --detect-shared-borders \
  --coalesce-densest-as-needed \
  posey_parcels.geojson
```

| Flag | Effect |
|---|---|
| `-zg` | Auto max zoom from density |
| `--drop-densest-as-needed` | Drop least-visible features when tiles too large |
| `--extend-zooms-if-still-dropping` | Add zooms until features fit |
| `--detect-shared-borders` | Better polygon topology |
| `-l parcels` | Must match MapLibre `source-layer` |

**Caveat:** dropped features cannot be filtered back in at that zoom.

## App wiring

1. `registerPmtilesProtocol()` on mount
2. `tryAddPoseyParcelsPmtiles(map)` else `wireIndianaParcels(map)`
3. Parcel click → `ParcelPopup` → `http://127.0.0.1:8000/api/proxy/xsoft/...`
