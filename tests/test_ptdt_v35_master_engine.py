import struct

import pytest

from engine.ptdt_v35_master_engine import (
    EvidenceNode,
    NeuralDepthOptimizer,
    SpatialTransformBridge,
)


def test_rfc8785_seal_is_stable():
    first = EvidenceNode("a", "p", "authority", "validated", {"b": 2, "a": 1})
    first.seal()
    second = EvidenceNode("b", "p", "authority", "validated", {"a": 1, "b": 2})
    second.seal()
    assert first.payload_hash == second.payload_hash


def test_tampering_invalidates_evidence_node():
    node = EvidenceNode("a", "p", "authority", "validated", {"value": 1})
    node.seal()
    assert node.verify_integrity()
    node.payload["value"] = 2
    assert not node.verify_integrity()


def test_slippy_tile_clamps_web_mercator_latitude():
    x, y = SpatialTransformBridge.lonlat_to_slippy_tile(-88.0, 90.0, 15)
    assert 0 <= x < 2**15
    assert 0 <= y < 2**15


def test_depth_processor_rejects_wrong_length():
    processor = NeuralDepthOptimizer(2, 2)
    with pytest.raises(ValueError):
        processor.process(b"bad", 375.0)


def test_depth_processor_hashes_cleaned_buffer():
    processor = NeuralDepthOptimizer(2, 2)
    raw = struct.pack("<4f", 376.0, 374.0, float("nan"), 377.0)
    output, digest, rejected = processor.process(raw, 375.0)
    assert len(output) == 16
    assert len(digest) == 64
    assert rejected == 2
