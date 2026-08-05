import pytest
from backend.src.runtime.composition.composition_statistics_builder import CompositionStatisticsBuilder
from backend.src.runtime.registry.component_registry import RuntimeComponentRegistry
from backend.src.runtime.dependency.dependency_graph import RuntimeDependencyGraph
from backend.src.runtime.registry.runtime_component import RuntimeComponent
from backend.src.runtime.registry.component_types import RuntimeComponentType
from backend.src.runtime.registry.component_status import RuntimeComponentStatus
from backend.src.runtime.dependency.dependency_type import DependencyType

def test_statistics_builder_empty():
    stats = CompositionStatisticsBuilder.build(None, None)
    assert stats.component_count == 0
    assert stats.dependency_count == 0
    assert stats.root_count == 0
    assert stats.leaf_count == 0
    assert stats.disconnected_count == 0

def test_statistics_builder_populated():
    registry = RuntimeComponentRegistry()
    registry.register(RuntimeComponent("c1", "Comp1", RuntimeComponentType.CORE, "1.0", RuntimeComponentStatus.REGISTERED))
    registry.register(RuntimeComponent("c2", "Comp2", RuntimeComponentType.CORE, "1.0", RuntimeComponentStatus.REGISTERED))
    
    graph = RuntimeDependencyGraph()
    graph.register_node("c1")
    graph.register_node("c2")
    graph.register_dependency("c1", "c2", DependencyType.REQUIRED)
    
    registry_snapshot = registry.get_snapshot()
    graph_snapshot = graph.create_snapshot()
    
    stats = CompositionStatisticsBuilder.build(registry_snapshot, graph_snapshot)
    
    assert stats.component_count == 2
    assert stats.dependency_count == 1
    assert stats.root_count == 1 # c1 is a root
    assert stats.leaf_count == 1 # c2 is a leaf
    assert stats.disconnected_count == 0
