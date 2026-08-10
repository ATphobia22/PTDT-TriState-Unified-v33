from __future__ import annotations

from typing import Any, Mapping, Optional

from .evidence_graph import ProvenanceRecord


class SourceAdapter:
    source = "unknown"
    role = "context"
    authority = "source"

    def record(
        self,
        source_record_id: str,
        payload: Mapping[str, Any],
        *,
        observed_at: Optional[str] = None,
        spatial_ref: Optional[str] = None,
        vertical_datum: Optional[str] = None,
        units: Optional[str] = None,
    ) -> ProvenanceRecord:
        return ProvenanceRecord.create(
            source=self.source,
            source_record_id=source_record_id,
            role=self.role,
            authority=self.authority,
            payload=payload,
            observed_at=observed_at,
            spatial_ref=spatial_ref,
            vertical_datum=vertical_datum,
            units=units,
        )


class NOAAFootprintAdapter(SourceAdapter):
    source = "NOAA-IOCM-US-Mapping-Coordination"
    role = "contextual-mapping-footprint"
    authority = "NOAA"


class DEMAdapter(SourceAdapter):
    source = "DEM"
    role = "terrain"
    authority = "source-dataset"


class LiDARAdapter(SourceAdapter):
    source = "LiDAR"
    role = "terrain"
    authority = "source-dataset"


class RASAdapter(SourceAdapter):
    source = "HEC-RAS"
    role = "ras"
    authority = "hydraulic-model"


class USGSObservationAdapter(SourceAdapter):
    source = "USGS-NWIS"
    role = "usgs-observation"
    authority = "USGS"


class USGSAssimilationAdapter(SourceAdapter):
    source = "USGS-EnKF"
    role = "derived-assimilation"
    authority = "derived"


class PostGISAdapter(SourceAdapter):
    source = "PostGIS"
    role = "postgis"
    authority = "project-database"
