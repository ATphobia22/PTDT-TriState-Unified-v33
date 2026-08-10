from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable, List, Mapping, Optional


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ProvenanceRecord:
    provenance_id: str
    source: str
    source_record_id: str
    role: str
    authority: str
    observed_at: Optional[str]
    retrieved_at: str
    spatial_ref: Optional[str]
    vertical_datum: Optional[str]
    units: Optional[str]
    payload: Mapping[str, Any]
    payload_sha256: str
    parent_ids: tuple[str, ...] = field(default_factory=tuple)

    @classmethod
    def create(
        cls,
        *,
        source: str,
        source_record_id: str,
        role: str,
        authority: str,
        payload: Mapping[str, Any],
        observed_at: Optional[str] = None,
        spatial_ref: Optional[str] = None,
        vertical_datum: Optional[str] = None,
        units: Optional[str] = None,
        parent_ids: Iterable[str] = (),
    ) -> "ProvenanceRecord":
        retrieved_at = datetime.now(timezone.utc).isoformat()
        payload_hash = sha256_json(payload)
        normalized_parents = tuple(sorted(parent_ids))
        seed = {
            "source": source,
            "source_record_id": source_record_id,
            "role": role,
            "authority": authority,
            "observed_at": observed_at,
            "retrieved_at": retrieved_at,
            "spatial_ref": spatial_ref,
            "vertical_datum": vertical_datum,
            "units": units,
            "payload_sha256": payload_hash,
            "parent_ids": normalized_parents,
        }
        provenance_id = "prov-" + hashlib.sha256(canonical_json(seed).encode("utf-8")).hexdigest()
        return cls(
            provenance_id=provenance_id,
            source=source,
            source_record_id=source_record_id,
            role=role,
            authority=authority,
            observed_at=observed_at,
            retrieved_at=retrieved_at,
            spatial_ref=spatial_ref,
            vertical_datum=vertical_datum,
            units=units,
            payload=dict(payload),
            payload_sha256=payload_hash,
            parent_ids=normalized_parents,
        )

    def verify(self) -> bool:
        return self.payload_sha256 == sha256_json(self.payload)


@dataclass(frozen=True)
class EvidenceEdge:
    edge_id: str
    from_id: str
    to_id: str
    relation: str
    semantics: str


class EvidenceGraph:
    """Canonical provenance graph; renderers are read-only consumers."""

    def __init__(self) -> None:
        self._records: dict[str, ProvenanceRecord] = {}
        self._edges: dict[str, EvidenceEdge] = {}

    def add_record(self, record: ProvenanceRecord) -> None:
        if not record.verify():
            raise ValueError(f"Invalid provenance payload hash: {record.provenance_id}")
        existing = self._records.get(record.provenance_id)
        if existing and existing != record:
            raise ValueError(f"Provenance ID collision: {record.provenance_id}")
        for parent_id in record.parent_ids:
            if parent_id not in self._records:
                raise KeyError(f"Missing parent evidence record: {parent_id}")
        self._records[record.provenance_id] = record

    def link(self, from_id: str, to_id: str, relation: str, semantics: str) -> EvidenceEdge:
        if from_id not in self._records or to_id not in self._records:
            raise KeyError("Both evidence nodes must exist before linking")
        edge_seed = {"from": from_id, "to": to_id, "relation": relation, "semantics": semantics}
        edge_id = "edge-" + sha256_json(edge_seed)
        edge = EvidenceEdge(edge_id, from_id, to_id, relation, semantics)
        self._edges[edge_id] = edge
        return edge

    def get(self, provenance_id: str) -> ProvenanceRecord:
        return self._records[provenance_id]

    def neighbors(self, provenance_id: str) -> List[EvidenceEdge]:
        return [e for e in self._edges.values() if e.from_id == provenance_id or e.to_id == provenance_id]

    def selection(self, provenance_id: str) -> dict[str, Any]:
        root = self.get(provenance_id)
        related_ids = {root.provenance_id}
        edges = self.neighbors(provenance_id)
        for edge in edges:
            related_ids.update((edge.from_id, edge.to_id))
        return {
            "root": asdict(root),
            "related": [asdict(self._records[i]) for i in sorted(related_ids) if i != root.provenance_id],
            "edges": [asdict(e) for e in edges],
            "read_only": True,
        }

    def manifest(self) -> dict[str, Any]:
        body = {
            "records": [asdict(r) for r in self._records.values()],
            "edges": [asdict(e) for e in self._edges.values()],
        }
        return {**body, "graph_sha256": sha256_json(body)}
