import pytest
from runtime.services import (
    RuntimeServiceBuilder, ServiceDescriptor, ServiceValidator
)
from runtime.services.service_exceptions import ServiceBuildException

def test_large_service_graph_performance():
    builder = RuntimeServiceBuilder()
    descriptors = []
    for i in range(1000):
        descriptors.append(
            ServiceDescriptor(
                service_id=f"s_{i}",
                component_id=f"c_{i}",
                service_name=f"Service {i}",
                service_type="CORE",
                lifetime="TRANSIENT",
                dependencies=(f"s_{i-1}",) if i > 0 else ()
            )
        )
    result = builder.build(descriptors)
    assert result.success is True
    assert result.service_composition.statistics.total_services == 1000
    assert result.service_composition.statistics.dependency_count == 999

def test_builder_independent_snapshots():
    builder = RuntimeServiceBuilder()
    desc = ServiceDescriptor("s1", "c1", "N", "T", "SINGLETON")
    result1 = builder.build([desc])
    result2 = builder.build([desc])
    assert result1.service_composition.composition_id != result2.service_composition.composition_id
    assert result1.service_composition.snapshot is not result2.service_composition.snapshot
