import pytest
from types import MappingProxyType
from src.runtime.bootstrap.runtime_bootstrap_validator import RuntimeBootstrapValidator
from src.runtime.bootstrap.runtime_bootstrap_descriptor import RuntimeBootstrapDescriptor
from src.runtime.bootstrap.runtime_bootstrap_dependency_batch import RuntimeBootstrapDependencyBatch
from src.runtime.bootstrap.runtime_bootstrap_layer import RuntimeBootstrapLayer
from src.runtime.bootstrap.bootstrap_exceptions import BootstrapValidationException


def test_validator_detects_cycles():
    validator = RuntimeBootstrapValidator()
    
    desc_a = RuntimeBootstrapDescriptor("a", "1.0", ("b",))
    desc_b = RuntimeBootstrapDescriptor("b", "1.0", ("a",))
    
    batch_a = RuntimeBootstrapDependencyBatch("ba", (desc_a,), MappingProxyType({}))
    batch_b = RuntimeBootstrapDependencyBatch("bb", (desc_b,), MappingProxyType({}))
    
    layer_a = RuntimeBootstrapLayer("la", (batch_a,), MappingProxyType({}))
    layer_b = RuntimeBootstrapLayer("lb", (batch_b,), MappingProxyType({}))
    
    adjacency = {
        "a": {"b"},
        "b": {"a"}
    }
    
    with pytest.raises(BootstrapValidationException) as exc:
        validator.validate_inputs(
            descriptor=desc_a,
            descriptors={"a": desc_a, "b": desc_b},
            layers=[layer_a, layer_b],
            adjacency=adjacency
        )
    
    assert "Cycle detected" in str(exc.value)

def test_validator_missing_descriptors():
    validator = RuntimeBootstrapValidator()
    
    desc_a = RuntimeBootstrapDescriptor("a", "1.0", ("c",))
    batch_a = RuntimeBootstrapDependencyBatch("ba", (desc_a,), MappingProxyType({}))
    layer_a = RuntimeBootstrapLayer("la", (batch_a,), MappingProxyType({}))
    
    adjacency = {
        "a": {"c"}
    }
    
    with pytest.raises(BootstrapValidationException) as exc:
        validator.validate_inputs(
            descriptor=desc_a,
            descriptors={"a": desc_a},
            layers=[layer_a],
            adjacency=adjacency
        )
        
    assert "Dependency 'c' of node 'a' not found in descriptors." in str(exc.value)
