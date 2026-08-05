import pytest
from runtime.services import ServiceSnapshot, ServiceMetadata, ServiceStatistics

def test_service_snapshot_immutability():
    meta = ServiceMetadata(schema_version="1", builder_version="1")
    stats = ServiceStatistics(1,1,0,0,0,1)
    snapshot = ServiceSnapshot(
        composition_id="comp_1",
        services=(),
        metadata=meta,
        statistics=stats
    )
    with pytest.raises(Exception):
        snapshot.composition_id = "comp_2"

def test_service_snapshot_values():
    meta = ServiceMetadata(schema_version="1", builder_version="1")
    stats = ServiceStatistics(1,1,0,0,0,1)
    snapshot = ServiceSnapshot(
        composition_id="comp_1",
        services=(),
        metadata=meta,
        statistics=stats
    )
    assert snapshot.composition_id == "comp_1"
    assert snapshot.services == ()
    assert snapshot.metadata == meta
    assert snapshot.statistics == stats
