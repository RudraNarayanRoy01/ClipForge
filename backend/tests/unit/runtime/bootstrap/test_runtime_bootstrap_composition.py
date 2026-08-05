import pytest
from types import MappingProxyType
from src.runtime.bootstrap.runtime_bootstrap_composition import RuntimeBootstrapComposition
from src.runtime.bootstrap.runtime_bootstrap_graph import RuntimeBootstrapGraph
from src.runtime.bootstrap.runtime_bootstrap_plan import RuntimeBootstrapPlan
from src.runtime.bootstrap.runtime_bootstrap_metadata import RuntimeBootstrapMetadata
from src.runtime.bootstrap.bootstrap_graph_statistics import BootstrapGraphStatistics
from src.runtime.bootstrap.runtime_bootstrap_statistics import RuntimeBootstrapStatistics
from src.runtime.bootstrap.runtime_bootstrap_snapshot import RuntimeBootstrapSnapshot


def test_composition_immutability():
    graph = RuntimeBootstrapGraph(
        roots=frozenset(),
        leaves=frozenset(),
        descriptor_lookup=MappingProxyType({}),
        dependency_lookup=MappingProxyType({}),
        layer_lookup=MappingProxyType({}),
        adjacency_lookup=MappingProxyType({}),
        reverse_adjacency_lookup=MappingProxyType({})
    )
    plan = RuntimeBootstrapPlan(())
    metadata = RuntimeBootstrapMetadata(123.4, "1.0", "1.0", MappingProxyType({}), MappingProxyType({}), None)
    graph_stats = BootstrapGraphStatistics(0, 0, 0, 0, 0, 0, 0)
    stats = RuntimeBootstrapStatistics(0, 0, 0, 0, 0, 0)
    snapshot = RuntimeBootstrapSnapshot("h", "h", "h", "h", "h", "h", "h")
    
    comp = RuntimeBootstrapComposition(
        composition_id="comp_1",
        graph=graph,
        plan=plan,
        metadata=metadata,
        graph_statistics=graph_stats,
        statistics=stats,
        snapshot=snapshot
    )
    
    with pytest.raises(AttributeError):
        comp.composition_id = "comp_2" # type: ignore
        
    assert comp.graph == graph
    assert comp.plan == plan
    assert comp.metadata == metadata
    assert comp.graph_statistics == graph_stats
    assert comp.statistics == stats
    assert comp.snapshot == snapshot
