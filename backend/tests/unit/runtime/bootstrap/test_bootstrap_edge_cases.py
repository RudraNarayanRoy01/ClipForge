import pytest
from types import MappingProxyType
from src.runtime.bootstrap.runtime_bootstrap_descriptor import RuntimeBootstrapDescriptor
from src.runtime.bootstrap.runtime_bootstrap_dependency_batch import RuntimeBootstrapDependencyBatch
from src.runtime.bootstrap.runtime_bootstrap_layer import RuntimeBootstrapLayer
from src.runtime.bootstrap.runtime_bootstrap_plan import RuntimeBootstrapPlan
from src.runtime.bootstrap.runtime_bootstrap_metadata import RuntimeBootstrapMetadata
from src.runtime.bootstrap.bootstrap_graph_statistics import BootstrapGraphStatistics
from src.runtime.bootstrap.runtime_bootstrap_statistics import RuntimeBootstrapStatistics


def test_metadata_immutability():
    meta = RuntimeBootstrapMetadata(1.0, "1", "1", MappingProxyType({}), MappingProxyType({}), None)
    with pytest.raises(AttributeError):
        meta.version = "2" # type: ignore
    with pytest.raises(AttributeError):
        meta.labels = MappingProxyType({}) # type: ignore

def test_graph_statistics_immutability():
    stats = BootstrapGraphStatistics(1, 1, 1, 1, 1, 1, 1)
    with pytest.raises(AttributeError):
        stats.node_count = 2 # type: ignore

def test_statistics_immutability():
    stats = RuntimeBootstrapStatistics(1, 1, 1, 1, 1, 1)
    with pytest.raises(AttributeError):
        stats.layer_count = 2 # type: ignore

def test_descriptor_empty_dependencies():
    desc = RuntimeBootstrapDescriptor("test", "1", ())
    assert len(desc.dependency_identifiers) == 0

def test_batch_empty_descriptors():
    batch = RuntimeBootstrapDependencyBatch("b", (), MappingProxyType({}))
    assert len(batch.descriptors) == 0

def test_layer_empty_batches():
    layer = RuntimeBootstrapLayer("l", (), MappingProxyType({}))
    assert len(layer.dependency_batches) == 0

def test_plan_empty_layers():
    plan = RuntimeBootstrapPlan(())
    assert len(plan.layers) == 0
