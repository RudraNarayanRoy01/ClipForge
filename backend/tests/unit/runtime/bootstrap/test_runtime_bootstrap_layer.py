import pytest
from types import MappingProxyType
from src.runtime.bootstrap.runtime_bootstrap_descriptor import RuntimeBootstrapDescriptor
from src.runtime.bootstrap.runtime_bootstrap_dependency_batch import RuntimeBootstrapDependencyBatch
from src.runtime.bootstrap.runtime_bootstrap_layer import RuntimeBootstrapLayer


def test_dependency_batch_immutability():
    desc = RuntimeBootstrapDescriptor("test_1", "1.0", ())
    batch = RuntimeBootstrapDependencyBatch("batch_1", (desc,), MappingProxyType({"meta": "data"}))
    
    with pytest.raises(AttributeError):
        batch.batch_identifier = "batch_2" # type: ignore
        
    with pytest.raises(AttributeError):
        batch.descriptors = () # type: ignore

def test_layer_immutability():
    desc = RuntimeBootstrapDescriptor("test_1", "1.0", ())
    batch = RuntimeBootstrapDependencyBatch("batch_1", (desc,), MappingProxyType({}))
    layer = RuntimeBootstrapLayer("layer_1", (batch,), MappingProxyType({"l_meta": "data"}))
    
    with pytest.raises(AttributeError):
        layer.layer_identifier = "layer_2" # type: ignore
        
    with pytest.raises(AttributeError):
        layer.dependency_batches = () # type: ignore

def test_layer_equality():
    desc = RuntimeBootstrapDescriptor("test_1", "1.0", ())
    batch1 = RuntimeBootstrapDependencyBatch("batch_1", (desc,), MappingProxyType({}))
    batch2 = RuntimeBootstrapDependencyBatch("batch_1", (desc,), MappingProxyType({}))
    
    layer1 = RuntimeBootstrapLayer("layer_1", (batch1,), MappingProxyType({"a": "b"}))
    layer2 = RuntimeBootstrapLayer("layer_1", (batch2,), MappingProxyType({"a": "b"}))
    layer3 = RuntimeBootstrapLayer("layer_2", (batch1,), MappingProxyType({"a": "b"}))
    
    assert layer1 == layer2
    assert layer1 != layer3
    assert hash(layer1) == hash(layer2)

def test_layer_ordering():
    # Tuples maintain order
    desc1 = RuntimeBootstrapDescriptor("test_1", "1.0", ())
    desc2 = RuntimeBootstrapDescriptor("test_2", "1.0", ())
    
    batch1 = RuntimeBootstrapDependencyBatch("batch_1", (desc1, desc2), MappingProxyType({}))
    batch2 = RuntimeBootstrapDependencyBatch("batch_1", (desc2, desc1), MappingProxyType({}))
    
    assert batch1 != batch2
