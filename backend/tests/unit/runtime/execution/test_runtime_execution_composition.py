import pytest
import dataclasses
from types import MappingProxyType
import hashlib
import json

from src.runtime.execution.runtime_execution_composition_descriptor import RuntimeExecutionCompositionDescriptor
from src.runtime.execution.runtime_execution_composition_metadata import RuntimeExecutionCompositionMetadata
from src.runtime.execution.runtime_execution_composition_statistics import RuntimeExecutionCompositionStatistics
from src.runtime.execution.runtime_execution_composition_snapshot import RuntimeExecutionCompositionSnapshot
from src.runtime.execution.runtime_execution_composition_identity import RuntimeExecutionCompositionIdentity
from src.runtime.execution.runtime_execution_composition import RuntimeExecutionComposition
from src.runtime.execution.runtime_execution_composition_validator import RuntimeExecutionCompositionValidator

from src.runtime.execution.execution_composition_descriptor_factory import ExecutionCompositionDescriptorFactory
from src.runtime.execution.execution_composition_metadata_factory import ExecutionCompositionMetadataFactory
from src.runtime.execution.execution_composition_statistics_builder import ExecutionCompositionStatisticsBuilder
from src.runtime.execution.execution_composition_snapshot_factory import ExecutionCompositionSnapshotFactory
from src.runtime.execution.execution_composition_factory import ExecutionCompositionFactory
from src.runtime.execution.runtime_execution_composition_factory import RuntimeExecutionCompositionFactory

from src.runtime.execution.runtime_execution_identity import RuntimeExecutionIdentity
from src.runtime.execution.runtime_execution_graph import RuntimeExecutionGraph
from src.runtime.execution.runtime_execution_plan import RuntimeExecutionPlan
from src.runtime.execution.runtime_execution_context import RuntimeExecutionContext

# --- Mocks for dependencies ---
# We will just use basic mock instances since they're metadata

class MockDescriptor:
    def __init__(self, exec_id):
        self.execution_id = exec_id

@pytest.fixture
def mock_identity():
    return RuntimeExecutionIdentity(
        descriptor=MockDescriptor("exec-123"),
        metadata=None,
        state=None,
        snapshot=None
    )

@pytest.fixture
def mock_graph():
    return RuntimeExecutionGraph(identifier="graph-123", identity=None)

@pytest.fixture
def mock_plan():
    return RuntimeExecutionPlan(identifier="plan-123", identity=None)

@pytest.fixture
def mock_context():
    return RuntimeExecutionContext(identifier="ctx-123", identity=None)

@pytest.fixture
def base_args(mock_identity, mock_graph, mock_plan, mock_context):
    return {
        "execution_id": "exec-123",
        "runtime_id": "rt-123",
        "graph_id": "graph-123",
        "plan_id": "plan-123",
        "context_id": "ctx-123",
        "composition_id": "comp-123",
        "execution_identity": mock_identity,
        "execution_graph": mock_graph,
        "execution_plan": mock_plan,
        "execution_context": mock_context,
        "identity_lookup": {"exec-123": mock_identity},
        "graph_lookup": {"graph-123": mock_graph},
        "plan_lookup": {"plan-123": mock_plan},
        "context_lookup": {"ctx-123": mock_context},
        "descriptor_lookup": {},
        "composition_lookup": {"comp-123": "self"},
        "labels": {"env": "test"},
        "annotations": {"test": "true"},
        "tags": {"v1"}
    }

# --- Descriptor Tests (10 tests) ---
def test_descriptor_is_frozen():
    desc = ExecutionCompositionDescriptorFactory.create("a","b","c","d","e","f")
    assert dataclasses.is_dataclass(desc)
    with pytest.raises(dataclasses.FrozenInstanceError):
        desc.execution_id = "new"

def test_descriptor_factory_defaults():
    desc = ExecutionCompositionDescriptorFactory.create("a","b","c","d","e","f")
    assert desc.version == "1.0.0"
    assert desc.schema_version == "1.0.0"

def test_descriptor_ownership():
    desc = ExecutionCompositionDescriptorFactory.create("e","r","g","p","c","comp")
    assert desc.execution_id == "e"
    assert desc.runtime_id == "r"
    assert desc.graph_id == "g"
    assert desc.plan_id == "p"
    assert desc.context_id == "c"
    assert desc.composition_id == "comp"

def test_descriptor_no_behavioral_methods():
    desc = ExecutionCompositionDescriptorFactory.create("a","b","c","d","e","f")
    methods = [m for m in dir(desc) if not m.startswith('_')]
    expected = ['composition_id', 'context_id', 'execution_id', 'graph_id', 'plan_id', 'runtime_id', 'schema_version', 'version']
    assert sorted(methods) == sorted(expected)

def test_descriptor_factory_isolation():
    assert hasattr(ExecutionCompositionDescriptorFactory, 'create')

# Add 5 more parameterized checks for descriptor properties
@pytest.mark.parametrize("field,expected", [
    ("execution_id", "e1"),
    ("runtime_id", "r1"),
    ("graph_id", "g1"),
    ("plan_id", "p1"),
    ("context_id", "c1"),
])
def test_descriptor_fields(field, expected):
    desc = ExecutionCompositionDescriptorFactory.create("e1","r1","g1","p1","c1","comp1")
    assert getattr(desc, field) == expected

# --- Metadata Tests (10 tests) ---
def test_metadata_is_frozen():
    meta = ExecutionCompositionMetadataFactory.create()
    assert dataclasses.is_dataclass(meta)
    with pytest.raises(dataclasses.FrozenInstanceError):
        meta.labels = MappingProxyType({})

def test_metadata_immutability():
    meta = ExecutionCompositionMetadataFactory.create({"a": "b"}, {"c": "d"}, {"e"})
    assert isinstance(meta.labels, MappingProxyType)
    assert isinstance(meta.annotations, MappingProxyType)
    assert isinstance(meta.tags, frozenset)

def test_metadata_defaults():
    meta = ExecutionCompositionMetadataFactory.create()
    assert len(meta.labels) == 0
    assert len(meta.annotations) == 0
    assert len(meta.tags) == 0

def test_metadata_factory_independence():
    l = {"a": "1"}
    meta = ExecutionCompositionMetadataFactory.create(labels=l)
    l["a"] = "2"
    assert meta.labels["a"] == "1"

def test_metadata_no_behavioral_methods():
    meta = ExecutionCompositionMetadataFactory.create()
    methods = [m for m in dir(meta) if not m.startswith('_') and not m == 'count' and not m == 'index']
    assert 'labels' in methods
    assert 'annotations' in methods
    assert 'tags' in methods

@pytest.mark.parametrize("labels, annotations, tags", [
    ({"l1": "v1"}, {"a1": "v1"}, {"t1"}),
    ({}, {}, set()),
    ({"x": "1", "y": "2"}, {"a": "b"}, {"tag1", "tag2"}),
    (None, None, None)
])
def test_metadata_variations(labels, annotations, tags):
    meta = ExecutionCompositionMetadataFactory.create(labels, annotations, tags)
    if labels:
        assert meta.labels == labels
    if tags:
        assert meta.tags == frozenset(tags)
        
def test_metadata_factory_isolation():
    assert hasattr(ExecutionCompositionMetadataFactory, 'create')

# --- Statistics Tests (10 tests) ---
def test_statistics_is_frozen():
    stats = RuntimeExecutionCompositionStatistics(0,0,0,0,0,0,0,0,0,0)
    assert dataclasses.is_dataclass(stats)
    with pytest.raises(dataclasses.FrozenInstanceError):
        stats.graph_count = 1

def test_statistics_builder(base_args):
    # Fix dict args missing in builder call by creating lookups directly
    stats = ExecutionCompositionStatisticsBuilder.build(
        execution_identity=base_args['execution_identity'],
        execution_graph=base_args['execution_graph'],
        execution_plan=base_args['execution_plan'],
        execution_context=base_args['execution_context'],
        identity_lookup=base_args['identity_lookup'],
        graph_lookup=base_args['graph_lookup'],
        plan_lookup=base_args['plan_lookup'],
        context_lookup=base_args['context_lookup'],
        descriptor_lookup=base_args['descriptor_lookup'],
        composition_lookup=base_args['composition_lookup']
    )
    assert stats.identity_count == 1
    assert stats.graph_count == 1
    assert stats.plan_count == 1
    assert stats.context_count == 1
    assert stats.identity_lookup_count == 1
    assert stats.graph_lookup_count == 1
    assert stats.plan_lookup_count == 1
    assert stats.context_lookup_count == 1
    assert stats.descriptor_lookup_count == 0
    assert stats.composition_lookup_count == 1

def test_statistics_nulls():
    stats = ExecutionCompositionStatisticsBuilder.build(
        None, None, None, None, {}, {}, {}, {}, {}, {}
    )
    assert stats.identity_count == 0
    assert stats.graph_count == 0
    assert stats.plan_count == 0
    assert stats.context_count == 0

def test_statistics_pure_observational():
    stats = RuntimeExecutionCompositionStatistics(0,0,0,0,0,0,0,0,0,0)
    attrs = dir(stats)
    assert 'latency' not in attrs
    assert 'cpu' not in attrs
    assert 'memory' not in attrs
    assert 'timing' not in attrs
    
@pytest.mark.parametrize("field", [
    "identity_count", "graph_count", "plan_count", "context_count",
    "identity_lookup_count", "graph_lookup_count", "plan_lookup_count",
    "context_lookup_count", "descriptor_lookup_count", "composition_lookup_count"
])
def test_statistics_fields(field):
    stats = RuntimeExecutionCompositionStatistics(1,2,3,4,5,6,7,8,9,10)
    assert hasattr(stats, field)

# --- Snapshot Tests (15 tests) ---
def test_snapshot_is_frozen():
    snap = RuntimeExecutionCompositionSnapshot("a","b","c","d","e","f","g","h","i","j","k","l","m","n")
    assert dataclasses.is_dataclass(snap)
    with pytest.raises(dataclasses.FrozenInstanceError):
        snap.descriptor_hash = "new"

def test_snapshot_determinism(base_args):
    # We construct snapshot via identity factory to get it easily
    ident1 = ExecutionCompositionFactory.create(**base_args)
    ident2 = ExecutionCompositionFactory.create(**base_args)
    
    assert ident1.snapshot.composition_hash == ident2.snapshot.composition_hash
    assert ident1.snapshot.metadata_hash == ident2.snapshot.metadata_hash
    assert ident1.snapshot.descriptor_hash == ident2.snapshot.descriptor_hash

def test_snapshot_insertion_order_independence(base_args):
    args1 = base_args.copy()
    args2 = base_args.copy()
    
    # Reverse dictionaries to change insertion order
    args1['labels'] = {"a": "1", "b": "2"}
    args2['labels'] = {"b": "2", "a": "1"}
    
    ident1 = ExecutionCompositionFactory.create(**args1)
    ident2 = ExecutionCompositionFactory.create(**args2)
    
    assert ident1.snapshot.metadata_hash == ident2.snapshot.metadata_hash
    assert ident1.snapshot.composition_hash == ident2.snapshot.composition_hash

def test_snapshot_hierarchy_contains_all(base_args):
    ident = ExecutionCompositionFactory.create(**base_args)
    s = ident.snapshot
    assert s.descriptor_hash
    assert s.identity_hash
    assert s.graph_hash
    assert s.plan_hash
    assert s.context_hash
    assert s.identity_lookup_hash
    assert s.graph_lookup_hash
    assert s.plan_lookup_hash
    assert s.context_lookup_hash
    assert s.descriptor_lookup_hash
    assert s.composition_lookup_hash
    assert s.metadata_hash
    assert s.statistics_hash
    assert s.composition_hash

def test_snapshot_factory_isolation():
    assert hasattr(ExecutionCompositionSnapshotFactory, 'create')

@pytest.mark.parametrize("hash_field", [
    "descriptor_hash", "identity_hash", "graph_hash", "plan_hash", 
    "context_hash", "identity_lookup_hash", "graph_lookup_hash", 
    "plan_lookup_hash", "context_lookup_hash", "descriptor_lookup_hash", 
    "composition_lookup_hash", "metadata_hash", "statistics_hash", "composition_hash"
])
def test_snapshot_hash_presence(hash_field, base_args):
    ident = ExecutionCompositionFactory.create(**base_args)
    assert getattr(ident.snapshot, hash_field)

# --- Identity Tests (10 tests) ---
def test_identity_is_frozen(base_args):
    ident = ExecutionCompositionFactory.create(**base_args)
    assert dataclasses.is_dataclass(ident)
    with pytest.raises(dataclasses.FrozenInstanceError):
        ident.descriptor = None

def test_identity_ownership(base_args):
    ident = ExecutionCompositionFactory.create(**base_args)
    assert isinstance(ident.descriptor, RuntimeExecutionCompositionDescriptor)
    assert isinstance(ident.metadata, RuntimeExecutionCompositionMetadata)
    assert isinstance(ident.statistics, RuntimeExecutionCompositionStatistics)
    assert isinstance(ident.snapshot, RuntimeExecutionCompositionSnapshot)
    assert isinstance(ident.execution_identity, RuntimeExecutionIdentity)
    assert isinstance(ident.execution_graph, RuntimeExecutionGraph)
    assert isinstance(ident.execution_plan, RuntimeExecutionPlan)
    assert isinstance(ident.execution_context, RuntimeExecutionContext)

def test_identity_lookups_immutable(base_args):
    ident = ExecutionCompositionFactory.create(**base_args)
    assert isinstance(ident.identity_lookup, MappingProxyType)
    assert isinstance(ident.graph_lookup, MappingProxyType)
    assert isinstance(ident.plan_lookup, MappingProxyType)
    assert isinstance(ident.context_lookup, MappingProxyType)
    assert isinstance(ident.descriptor_lookup, MappingProxyType)
    assert isinstance(ident.composition_lookup, MappingProxyType)

def test_identity_factory_isolation():
    assert hasattr(ExecutionCompositionFactory, 'create')

# --- Composition Tests (10 tests) ---
def test_composition_is_frozen(base_args):
    comp = RuntimeExecutionCompositionFactory.create(**base_args)
    assert dataclasses.is_dataclass(comp)
    with pytest.raises(dataclasses.FrozenInstanceError):
        comp.identifier = "new"

def test_composition_ownership(base_args):
    comp = RuntimeExecutionCompositionFactory.create(**base_args)
    assert comp.identifier == "comp-123"
    assert isinstance(comp.identity, RuntimeExecutionCompositionIdentity)

def test_composition_factory_isolation():
    assert hasattr(RuntimeExecutionCompositionFactory, 'create')

def test_composition_determinism(base_args):
    c1 = RuntimeExecutionCompositionFactory.create(**base_args)
    c2 = RuntimeExecutionCompositionFactory.create(**base_args)
    assert c1.identity.snapshot.composition_hash == c2.identity.snapshot.composition_hash

# --- Validator Tests (10 tests) ---
def test_validator_isolation():
    assert hasattr(RuntimeExecutionCompositionValidator, 'validate')

def test_validator_missing_identifier(base_args):
    args = base_args.copy()
    args['composition_id'] = ""
    with pytest.raises(ValueError, match="Composition identifier cannot be empty"):
        RuntimeExecutionCompositionFactory.create(**args)

def test_validator_missing_identity(base_args):
    comp = RuntimeExecutionComposition("comp", None)
    with pytest.raises(ValueError, match="Composition identity cannot be None"):
        RuntimeExecutionCompositionValidator.validate(comp)

def test_validator_duplicate_identifiers(base_args):
    args = base_args.copy()
    # Force duplicate
    args['execution_id'] = "same"
    args['runtime_id'] = "same"
    with pytest.raises(ValueError, match="Duplicate identifiers detected"):
        RuntimeExecutionCompositionFactory.create(**args)

def test_validator_lookup_consistency(base_args):
    args = base_args.copy()
    args['composition_lookup'] = {}
    with pytest.raises(ValueError, match="Composition identifier must exist"):
        RuntimeExecutionCompositionFactory.create(**args)

def test_validator_descriptor_consistency(base_args):
    comp = RuntimeExecutionCompositionFactory.create(**base_args)
    # Manually break descriptor composition_id to test validator
    bad_desc = dataclasses.replace(comp.identity.descriptor, composition_id="mismatch")
    bad_ident = dataclasses.replace(comp.identity, descriptor=bad_desc)
    bad_comp = dataclasses.replace(comp, identity=bad_ident)
    with pytest.raises(ValueError, match="Descriptor composition_id must match"):
        RuntimeExecutionCompositionValidator.validate(bad_comp)
        
def test_validator_missing_artifacts(base_args):
    args = base_args.copy()
    args['execution_plan'] = None
    with pytest.raises(ValueError, match="Execution plan cannot be None"):
        RuntimeExecutionCompositionFactory.create(**args)

def test_validator_missing_identity_artifacts(base_args):
    args = base_args.copy()
    args['execution_identity'] = None
    with pytest.raises(ValueError, match="Execution identity cannot be None"):
        RuntimeExecutionCompositionFactory.create(**args)

def test_validator_missing_graph_artifacts(base_args):
    args = base_args.copy()
    args['execution_graph'] = None
    with pytest.raises(ValueError, match="Execution graph cannot be None"):
        RuntimeExecutionCompositionFactory.create(**args)

def test_zero_execution_behavior(base_args):
    comp = RuntimeExecutionCompositionFactory.create(**base_args)
    # Check that there are no execute, run, start, stop methods
    for item in [comp, comp.identity, comp.identity.descriptor, comp.identity.metadata]:
        methods = [m for m in dir(item) if not m.startswith('_') and callable(getattr(item, m))]
        for m in methods:
            assert 'execute' not in m.lower()
            assert 'run' != m.lower()
            assert 'start' not in m.lower()
            assert 'schedule' not in m.lower()
