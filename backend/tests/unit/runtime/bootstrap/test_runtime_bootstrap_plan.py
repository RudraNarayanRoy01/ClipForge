import pytest
from types import MappingProxyType
from src.runtime.bootstrap.runtime_bootstrap_plan import RuntimeBootstrapPlan
from src.runtime.bootstrap.runtime_bootstrap_layer import RuntimeBootstrapLayer
from src.runtime.bootstrap.runtime_bootstrap_dependency_batch import RuntimeBootstrapDependencyBatch


def test_plan_immutability():
    batch = RuntimeBootstrapDependencyBatch("b1", (), MappingProxyType({}))
    layer = RuntimeBootstrapLayer("l1", (batch,), MappingProxyType({}))
    plan = RuntimeBootstrapPlan((layer,))
    
    with pytest.raises(AttributeError):
        plan.layers = () # type: ignore

def test_plan_equality():
    batch = RuntimeBootstrapDependencyBatch("b1", (), MappingProxyType({}))
    layer1 = RuntimeBootstrapLayer("l1", (batch,), MappingProxyType({}))
    layer2 = RuntimeBootstrapLayer("l2", (batch,), MappingProxyType({}))
    
    plan1 = RuntimeBootstrapPlan((layer1, layer2))
    plan2 = RuntimeBootstrapPlan((layer1, layer2))
    plan3 = RuntimeBootstrapPlan((layer2, layer1))
    
    assert plan1 == plan2
    assert plan1 != plan3
    assert hash(plan1) == hash(plan2)

def test_plan_ordering_determinism():
    batch = RuntimeBootstrapDependencyBatch("b1", (), MappingProxyType({}))
    layer1 = RuntimeBootstrapLayer("l1", (batch,), MappingProxyType({}))
    layer2 = RuntimeBootstrapLayer("l2", (batch,), MappingProxyType({}))
    
    plan = RuntimeBootstrapPlan((layer1, layer2))
    
    # Layers should strictly preserve tuple order
    assert plan.layers[0].layer_identifier == "l1"
    assert plan.layers[1].layer_identifier == "l2"
