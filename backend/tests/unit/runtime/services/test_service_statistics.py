import pytest
from runtime.services import ServiceStatistics

def test_service_statistics_immutability():
    stats = ServiceStatistics(
        total_services=5,
        singleton_services=2,
        transient_services=2,
        scoped_services=1,
        dependency_count=10,
        grouped_services=3
    )
    with pytest.raises(Exception):
        stats.total_services = 6

def test_service_statistics_values():
    stats = ServiceStatistics(
        total_services=5,
        singleton_services=2,
        transient_services=2,
        scoped_services=1,
        dependency_count=10,
        grouped_services=3
    )
    assert stats.total_services == 5
    assert stats.singleton_services == 2
    assert stats.transient_services == 2
    assert stats.scoped_services == 1
    assert stats.dependency_count == 10
    assert stats.grouped_services == 3
