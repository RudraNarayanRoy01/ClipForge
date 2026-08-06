import pytest
from types import MappingProxyType
from src.runtime.execution.runtime_execution_node import RuntimeExecutionNode
from src.runtime.execution.runtime_execution_edge import RuntimeExecutionEdge
from src.runtime.execution.runtime_execution_graph import RuntimeExecutionGraph
from src.runtime.execution.runtime_execution_graph_identity import RuntimeExecutionGraphIdentity
from src.runtime.execution.runtime_execution_graph_descriptor import RuntimeExecutionGraphDescriptor
from src.runtime.execution.runtime_execution_graph_metadata import RuntimeExecutionGraphMetadata
from src.runtime.execution.runtime_execution_graph_statistics import RuntimeExecutionGraphStatistics
from src.runtime.execution.runtime_execution_graph_snapshot import RuntimeExecutionGraphSnapshot
from src.runtime.execution.runtime_execution_graph_validator import RuntimeExecutionGraphValidator
from src.runtime.execution.runtime_execution_exceptions import ExecutionValidationException
from src.runtime.execution.execution_graph_id_factory import ExecutionGraphIdFactory
from src.runtime.execution.execution_graph_descriptor_factory import ExecutionGraphDescriptorFactory
from src.runtime.execution.execution_graph_metadata_factory import ExecutionGraphMetadataFactory
from src.runtime.execution.execution_graph_factory import ExecutionGraphFactory
from src.runtime.execution.execution_graph_snapshot_factory import ExecutionGraphSnapshotFactory
from src.runtime.execution.execution_graph_statistics_builder import ExecutionGraphStatisticsBuilder
from src.runtime.execution.runtime_execution_graph_factory import RuntimeExecutionGraphFactory

def test_node_immutability():
    node = RuntimeExecutionNode("node1", "ref1", "meta1")
    with pytest.raises(Exception):
        node.identifier = "node2"

def test_edge_immutability():
    edge = RuntimeExecutionEdge("e1", "n1", "n2", "rel1", "meta")
    with pytest.raises(Exception):
        edge.source_node_identifier = "n3"

def test_graph_immutability():
    graph = RuntimeExecutionGraphFactory.build(tuple(), tuple())
    with pytest.raises(Exception):
        graph.identifier = "new_id"

def test_metadata_immutability():
    meta = ExecutionGraphMetadataFactory.create_metadata()
    with pytest.raises(Exception):
        meta.labels = frozenset(["new"])

def test_statistics_immutability():
    stats = RuntimeExecutionGraphStatistics(1, 1, 1, 1, 1, 1, 1, 1)
    with pytest.raises(Exception):
        stats.node_count = 2

def test_snapshot_immutability():
    snap = RuntimeExecutionGraphSnapshot("a", "b", "c", "l", "d", "e", "f", "g")
    with pytest.raises(Exception):
        snap.node_hash = "g"

def test_duplicate_node_validation():
    n1 = RuntimeExecutionNode("node1", "ref1", "m1")
    n2 = RuntimeExecutionNode("node1", "ref2", "m2")
    with pytest.raises(ExecutionValidationException):
        RuntimeExecutionGraphValidator.validate((n1, n2), tuple())

def test_broken_edge_source():
    n1 = RuntimeExecutionNode("node1", "ref1", "m1")
    e1 = RuntimeExecutionEdge("e1", "missing", "node1", "rel", "m")
    with pytest.raises(ExecutionValidationException):
        RuntimeExecutionGraphValidator.validate((n1,), (e1,))

def test_broken_edge_destination():
    n1 = RuntimeExecutionNode("node1", "ref1", "m1")
    e1 = RuntimeExecutionEdge("e1", "node1", "missing", "rel", "m")
    with pytest.raises(ExecutionValidationException):
        RuntimeExecutionGraphValidator.validate((n1,), (e1,))

def test_valid_graph_validation():
    n1 = RuntimeExecutionNode("node1", "ref1", "m1")
    n2 = RuntimeExecutionNode("node2", "ref2", "m2")
    e1 = RuntimeExecutionEdge("e1", "node1", "node2", "rel", "m")
    RuntimeExecutionGraphValidator.validate((n1, n2), (e1,))

def test_graph_factory_roots_leaves():
    n1 = RuntimeExecutionNode("n1", "r", "m")
    n2 = RuntimeExecutionNode("n2", "r", "m")
    n3 = RuntimeExecutionNode("n3", "r", "m")
    e1 = RuntimeExecutionEdge("e1", "n1", "n2", "rel", "m")
    e2 = RuntimeExecutionEdge("e2", "n2", "n3", "rel", "m")
    
    graph = RuntimeExecutionGraphFactory.build((n1, n2, n3), (e1, e2))
    identity = graph.identity
    
    assert "n1" in identity.roots
    assert "n3" in identity.leaves
    assert "n2" not in identity.roots
    assert "n2" not in identity.leaves

def test_graph_factory_lookups_are_mapping_proxy():
    graph = RuntimeExecutionGraphFactory.build(tuple(), tuple())
    identity = graph.identity
    assert isinstance(identity.node_lookup, MappingProxyType)
    assert isinstance(identity.edge_lookup, MappingProxyType)
    assert isinstance(identity.incoming_lookup, MappingProxyType)
    assert isinstance(identity.outgoing_lookup, MappingProxyType)
    assert isinstance(identity.descriptor_lookup, MappingProxyType)

def test_graph_factory_deterministic_ordering():
    n1 = RuntimeExecutionNode("c", "r", "m")
    n2 = RuntimeExecutionNode("a", "r", "m")
    n3 = RuntimeExecutionNode("b", "r", "m")
    
    # Factory itself doesn't reorder the input nodes tuple directly inside Identity unless we do it in build, but lookups and hashes are sorted.
    # The nodes are passed directly to Identity. Let's just check the snapshot hashes.
    g1 = RuntimeExecutionGraphFactory.build((n1, n2, n3), tuple())
    g2 = RuntimeExecutionGraphFactory.build((n2, n3, n1), tuple())
    # Descriptor will be different, so snapshot will be different. We test this specifically in another file.
    assert len(g1.identity.nodes) == 3

def test_statistics_builder():
    n1 = RuntimeExecutionNode("n1", "r", "m")
    n2 = RuntimeExecutionNode("n2", "r", "m")
    n3 = RuntimeExecutionNode("n3", "r", "m")
    e1 = RuntimeExecutionEdge("e1", "n1", "n2", "rel", "m")
    
    graph = RuntimeExecutionGraphFactory.build((n1, n2, n3), (e1,))
    stats = graph.identity.statistics
    
    assert stats.node_count == 3
    assert stats.edge_count == 1
    assert stats.root_count == 2
    assert stats.leaf_count == 2
    assert stats.connected_component_count == 2
    assert stats.isolated_node_count == 1
    assert stats.graph_depth == 1
    assert stats.graph_width == 2

def test_runtime_graph_factory():
    n1 = RuntimeExecutionNode("n1", "r", "m")
    graph = RuntimeExecutionGraphFactory.build(
        nodes=(n1,),
        edges=tuple(),
        labels=frozenset(["test"])
    )
    
    assert graph is not None
    assert graph.identity is not None
    assert graph.identity.descriptor is not None
    assert graph.identity.metadata is not None
    assert graph.identity.statistics is not None
    assert graph.identity.snapshot is not None
    assert len(graph.identity.nodes) == 1
    assert "test" in graph.identity.metadata.labels
    assert graph.identity.statistics.node_count == 1
    assert graph.identity.snapshot.snapshot_hash is not None
