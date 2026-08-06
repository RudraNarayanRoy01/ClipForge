import pytest
from types import MappingProxyType
import hashlib
import json

from src.runtime.execution import (
    RuntimeExecutionDependencyBatch,
    RuntimeExecutionLayer,
    RuntimeExecutionPlanDescriptor,
    RuntimeExecutionPlanMetadata,
    RuntimeExecutionPlanStatistics,
    RuntimeExecutionPlanSnapshot,
    RuntimeExecutionPlanIdentity,
    RuntimeExecutionPlan,
    RuntimeExecutionPlanValidator,
    ExecutionPlanDescriptorFactory,
    ExecutionPlanMetadataFactory,
    ExecutionPlanSnapshotFactory,
    ExecutionPlanStatisticsBuilder,
    ExecutionPlanFactory,
    RuntimeExecutionPlanFactory,
    ExecutionValidationException
)

def create_valid_descriptor(pid="plan-101"):
    return ExecutionPlanDescriptorFactory.create(
        execution_id="exec-123",
        runtime_id="rt-456",
        graph_id="graph-789",
        plan_id=pid,
        version="1.0.0",
        schema_version="1.0.0"
    )

def create_valid_metadata():
    return ExecutionPlanMetadataFactory.create(
        labels={"env": "test"},
        annotations={"author": "AI"},
        tags={"critical": "true"}
    )

def create_valid_layers():
    batch1 = RuntimeExecutionDependencyBatch(
        batch_identifier="batch-1",
        ordered_node_identifiers=("node-1", "node-2"),
        dependency_identifiers=frozenset()
    )
    batch2 = RuntimeExecutionDependencyBatch(
        batch_identifier="batch-2",
        ordered_node_identifiers=("node-3",),
        dependency_identifiers=frozenset(["batch-1"])
    )
    layer1 = RuntimeExecutionLayer(
        layer_identifier="layer-1",
        batches=(batch1,)
    )
    layer2 = RuntimeExecutionLayer(
        layer_identifier="layer-2",
        batches=(batch2,)
    )
    return (layer1, layer2)


class TestRuntimeExecutionPlanImmutability:
    def test_dependency_batch_frozen_id(self):
        batch = create_valid_layers()[0].batches[0]
        with pytest.raises(Exception):
            batch.batch_identifier = "mutated"
            
    def test_dependency_batch_frozen_nodes(self):
        batch = create_valid_layers()[0].batches[0]
        with pytest.raises(Exception):
            batch.ordered_node_identifiers = ()
            
    def test_dependency_batch_frozen_deps(self):
        batch = create_valid_layers()[0].batches[0]
        with pytest.raises(Exception):
            batch.dependency_identifiers = frozenset()

    def test_layer_frozen_id(self):
        layer = create_valid_layers()[0]
        with pytest.raises(Exception):
            layer.layer_identifier = "mutated"
            
    def test_layer_frozen_batches(self):
        layer = create_valid_layers()[0]
        with pytest.raises(Exception):
            layer.batches = ()

    def test_descriptor_frozen_exec_id(self):
        desc = create_valid_descriptor()
        with pytest.raises(Exception):
            desc.execution_id = "mutated"
            
    def test_descriptor_frozen_plan_id(self):
        desc = create_valid_descriptor()
        with pytest.raises(Exception):
            desc.plan_id = "mutated"

    def test_metadata_frozen_labels(self):
        meta = create_valid_metadata()
        with pytest.raises(Exception):
            meta.labels = MappingProxyType({})
            
    def test_metadata_frozen_tags(self):
        meta = create_valid_metadata()
        with pytest.raises(Exception):
            meta.tags = MappingProxyType({})

    def test_statistics_frozen_layer_count(self):
        stats = ExecutionPlanStatisticsBuilder.build(create_valid_layers())
        with pytest.raises(Exception):
            stats.layer_count = 99
            
    def test_statistics_frozen_node_count(self):
        stats = ExecutionPlanStatisticsBuilder.build(create_valid_layers())
        with pytest.raises(Exception):
            stats.node_count = 99

    def test_snapshot_frozen_plan_hash(self):
        desc = create_valid_descriptor()
        meta = create_valid_metadata()
        layers = create_valid_layers()
        identity = ExecutionPlanFactory.create_identity(desc, meta, layers)
        with pytest.raises(Exception):
            identity.snapshot.plan_hash = "mutated"
            
    def test_snapshot_frozen_layer_hash(self):
        desc = create_valid_descriptor()
        meta = create_valid_metadata()
        layers = create_valid_layers()
        identity = ExecutionPlanFactory.create_identity(desc, meta, layers)
        with pytest.raises(Exception):
            identity.snapshot.layer_hash = "mutated"

    def test_identity_frozen_descriptor(self):
        desc = create_valid_descriptor()
        meta = create_valid_metadata()
        layers = create_valid_layers()
        identity = ExecutionPlanFactory.create_identity(desc, meta, layers)
        with pytest.raises(Exception):
            identity.descriptor = desc
            
    def test_identity_frozen_layers(self):
        desc = create_valid_descriptor()
        meta = create_valid_metadata()
        layers = create_valid_layers()
        identity = ExecutionPlanFactory.create_identity(desc, meta, layers)
        with pytest.raises(Exception):
            identity.layers = ()

    def test_plan_frozen_identifier(self):
        desc = create_valid_descriptor()
        meta = create_valid_metadata()
        layers = create_valid_layers()
        plan = RuntimeExecutionPlanFactory.create(desc, meta, layers)
        with pytest.raises(Exception):
            plan.identifier = "mutated"
            
    def test_plan_frozen_identity(self):
        desc = create_valid_descriptor()
        meta = create_valid_metadata()
        layers = create_valid_layers()
        plan = RuntimeExecutionPlanFactory.create(desc, meta, layers)
        with pytest.raises(Exception):
            plan.identity = plan.identity


class TestRuntimeExecutionPlanCollections:
    def test_metadata_labels_proxy(self):
        meta = create_valid_metadata()
        assert isinstance(meta.labels, MappingProxyType)
        with pytest.raises(Exception):
            meta.labels["new"] = "value"
            
    def test_metadata_tags_proxy(self):
        meta = create_valid_metadata()
        assert isinstance(meta.tags, MappingProxyType)

    def test_layer_lookup_proxy(self):
        identity = ExecutionPlanFactory.create_identity(create_valid_descriptor(), create_valid_metadata(), create_valid_layers())
        assert isinstance(identity.layer_lookup, MappingProxyType)
        with pytest.raises(Exception):
            identity.layer_lookup["new"] = None

    def test_batch_lookup_proxy(self):
        identity = ExecutionPlanFactory.create_identity(create_valid_descriptor(), create_valid_metadata(), create_valid_layers())
        assert isinstance(identity.batch_lookup, MappingProxyType)
        with pytest.raises(Exception):
            identity.batch_lookup["new"] = None

    def test_descriptor_lookup_proxy(self):
        identity = ExecutionPlanFactory.create_identity(create_valid_descriptor(), create_valid_metadata(), create_valid_layers())
        assert isinstance(identity.descriptor_lookup, MappingProxyType)
        with pytest.raises(Exception):
            identity.descriptor_lookup["new"] = None

    def test_plan_lookup_proxy(self):
        identity = ExecutionPlanFactory.create_identity(create_valid_descriptor(), create_valid_metadata(), create_valid_layers())
        assert isinstance(identity.plan_lookup, MappingProxyType)
        with pytest.raises(Exception):
            identity.plan_lookup["new"] = None
            
    def test_layer_batches_is_tuple(self):
        layer = create_valid_layers()[0]
        assert isinstance(layer.batches, tuple)
        
    def test_batch_nodes_is_tuple(self):
        batch = create_valid_layers()[0].batches[0]
        assert isinstance(batch.ordered_node_identifiers, tuple)
        
    def test_batch_dependencies_is_frozenset(self):
        batch = create_valid_layers()[0].batches[0]
        assert isinstance(batch.dependency_identifiers, frozenset)


class TestRuntimeExecutionPlanValidation:
    def test_valid_plan_passes(self):
        identity = ExecutionPlanFactory.create_identity(create_valid_descriptor(), create_valid_metadata(), create_valid_layers())
        assert identity is not None

    def test_duplicate_layer_fails(self):
        layers = create_valid_layers()
        duplicate_layers = (layers[0], layers[0])
        with pytest.raises(ExecutionValidationException, match="Duplicate layer"):
            ExecutionPlanFactory.create_identity(create_valid_descriptor(), create_valid_metadata(), duplicate_layers)

    def test_empty_layer_fails(self):
        empty_layer = RuntimeExecutionLayer("layer-1", batches=())
        with pytest.raises(ExecutionValidationException, match="Empty layer"):
            ExecutionPlanFactory.create_identity(create_valid_descriptor(), create_valid_metadata(), (empty_layer,))

    def test_duplicate_batch_fails(self):
        batch1 = RuntimeExecutionDependencyBatch("batch-1", ("node-1",), frozenset())
        layer1 = RuntimeExecutionLayer("layer-1", (batch1, batch1))
        with pytest.raises(ExecutionValidationException, match="Duplicate batch"):
            ExecutionPlanFactory.create_identity(create_valid_descriptor(), create_valid_metadata(), (layer1,))
            
    def test_duplicate_batch_across_layers_fails(self):
        batch1 = RuntimeExecutionDependencyBatch("batch-1", ("node-1",), frozenset())
        layer1 = RuntimeExecutionLayer("layer-1", (batch1,))
        layer2 = RuntimeExecutionLayer("layer-2", (batch1,))
        with pytest.raises(ExecutionValidationException, match="Duplicate batch"):
            ExecutionPlanFactory.create_identity(create_valid_descriptor(), create_valid_metadata(), (layer1, layer2))

    def test_empty_batch_fails(self):
        batch1 = RuntimeExecutionDependencyBatch("batch-1", (), frozenset())
        layer1 = RuntimeExecutionLayer("layer-1", (batch1,))
        with pytest.raises(ExecutionValidationException, match="Empty batch"):
            ExecutionPlanFactory.create_identity(create_valid_descriptor(), create_valid_metadata(), (layer1,))

    def test_missing_plan_id_fails(self):
        desc = ExecutionPlanDescriptorFactory.create("e", "r", "g", "", "v", "sv")
        with pytest.raises(ExecutionValidationException, match="Invalid plan_id"):
            ExecutionPlanFactory.create_identity(desc, create_valid_metadata(), create_valid_layers())


class TestRuntimeExecutionPlanLookups:
    def test_layer_lookup_consistency(self):
        layers = create_valid_layers()
        identity = ExecutionPlanFactory.create_identity(create_valid_descriptor(), create_valid_metadata(), layers)
        for layer in layers:
            assert identity.layer_lookup[layer.layer_identifier] is layer

    def test_batch_lookup_consistency(self):
        layers = create_valid_layers()
        identity = ExecutionPlanFactory.create_identity(create_valid_descriptor(), create_valid_metadata(), layers)
        for layer in layers:
            for batch in layer.batches:
                assert identity.batch_lookup[batch.batch_identifier] is batch

    def test_descriptor_lookup_consistency(self):
        desc = create_valid_descriptor()
        identity = ExecutionPlanFactory.create_identity(desc, create_valid_metadata(), create_valid_layers())
        assert identity.descriptor_lookup[desc.plan_id] is desc
        
    def test_descriptor_lookup_single_element(self):
        desc = create_valid_descriptor()
        identity = ExecutionPlanFactory.create_identity(desc, create_valid_metadata(), create_valid_layers())
        assert len(identity.descriptor_lookup) == 1

    def test_plan_lookup_consistency(self):
        desc = create_valid_descriptor()
        identity = ExecutionPlanFactory.create_identity(desc, create_valid_metadata(), create_valid_layers())
        assert desc.plan_id in identity.plan_lookup
        
    def test_plan_lookup_single_element(self):
        desc = create_valid_descriptor()
        identity = ExecutionPlanFactory.create_identity(desc, create_valid_metadata(), create_valid_layers())
        assert len(identity.plan_lookup) == 1


class TestRuntimeExecutionPlanStatistics:
    def test_layer_count_correct(self):
        stats = ExecutionPlanStatisticsBuilder.build(create_valid_layers())
        assert stats.layer_count == 2
        
    def test_layer_count_single(self):
        stats = ExecutionPlanStatisticsBuilder.build((create_valid_layers()[0],))
        assert stats.layer_count == 1

    def test_dependency_batch_count_correct(self):
        stats = ExecutionPlanStatisticsBuilder.build(create_valid_layers())
        assert stats.dependency_batch_count == 2
        
    def test_dependency_batch_count_multiple_in_layer(self):
        batch1 = RuntimeExecutionDependencyBatch("b1", ("n1",), frozenset())
        batch2 = RuntimeExecutionDependencyBatch("b2", ("n2",), frozenset())
        layer = RuntimeExecutionLayer("l1", (batch1, batch2))
        stats = ExecutionPlanStatisticsBuilder.build((layer,))
        assert stats.dependency_batch_count == 2

    def test_planned_step_count_correct(self):
        stats = ExecutionPlanStatisticsBuilder.build(create_valid_layers())
        assert stats.planned_step_count == 3  # node-1, node-2, node-3

    def test_graph_depth_correct(self):
        stats = ExecutionPlanStatisticsBuilder.build(create_valid_layers())
        assert stats.graph_depth == 2

    def test_maximum_parallel_groups_correct(self):
        stats = ExecutionPlanStatisticsBuilder.build(create_valid_layers())
        assert stats.maximum_parallel_groups == 1
        
    def test_maximum_parallel_groups_large(self):
        batch1 = RuntimeExecutionDependencyBatch("b1", ("n1",), frozenset())
        batch2 = RuntimeExecutionDependencyBatch("b2", ("n2",), frozenset())
        batch3 = RuntimeExecutionDependencyBatch("b3", ("n3",), frozenset())
        layer = RuntimeExecutionLayer("l1", (batch1, batch2, batch3))
        stats = ExecutionPlanStatisticsBuilder.build((layer,))
        assert stats.maximum_parallel_groups == 3
        
    def test_node_count_correct(self):
        stats = ExecutionPlanStatisticsBuilder.build(create_valid_layers())
        assert stats.node_count == 3


class TestRuntimeExecutionPlanSnapshot:
    def test_snapshot_is_deterministic(self):
        desc1 = create_valid_descriptor()
        meta1 = create_valid_metadata()
        layers1 = create_valid_layers()
        identity1 = ExecutionPlanFactory.create_identity(desc1, meta1, layers1)

        desc2 = create_valid_descriptor()
        meta2 = create_valid_metadata()
        layers2 = create_valid_layers()
        identity2 = ExecutionPlanFactory.create_identity(desc2, meta2, layers2)

        assert identity1.snapshot.plan_hash == identity2.snapshot.plan_hash
        
    def test_layer_hash_deterministic(self):
        desc = create_valid_descriptor()
        meta = create_valid_metadata()
        identity1 = ExecutionPlanFactory.create_identity(desc, meta, create_valid_layers())
        identity2 = ExecutionPlanFactory.create_identity(desc, meta, create_valid_layers())
        assert identity1.snapshot.layer_hash == identity2.snapshot.layer_hash
        
    def test_batch_hash_deterministic(self):
        desc = create_valid_descriptor()
        meta = create_valid_metadata()
        identity1 = ExecutionPlanFactory.create_identity(desc, meta, create_valid_layers())
        identity2 = ExecutionPlanFactory.create_identity(desc, meta, create_valid_layers())
        assert identity1.snapshot.batch_hash == identity2.snapshot.batch_hash

    def test_snapshot_hashes_change_on_mutation_desc(self):
        identity1 = ExecutionPlanFactory.create_identity(create_valid_descriptor(), create_valid_metadata(), create_valid_layers())
        identity2 = ExecutionPlanFactory.create_identity(create_valid_descriptor("plan-999"), create_valid_metadata(), create_valid_layers())
        assert identity1.snapshot.plan_hash != identity2.snapshot.plan_hash
        assert identity1.snapshot.descriptor_hash != identity2.snapshot.descriptor_hash
        
    def test_snapshot_hashes_change_on_mutation_meta(self):
        identity1 = ExecutionPlanFactory.create_identity(create_valid_descriptor(), create_valid_metadata(), create_valid_layers())
        meta2 = ExecutionPlanMetadataFactory.create({"env": "prod"}, {}, {})
        identity2 = ExecutionPlanFactory.create_identity(create_valid_descriptor(), meta2, create_valid_layers())
        assert identity1.snapshot.plan_hash != identity2.snapshot.plan_hash
        assert identity1.snapshot.metadata_hash != identity2.snapshot.metadata_hash
        
    def test_snapshot_hashes_change_on_mutation_layers(self):
        identity1 = ExecutionPlanFactory.create_identity(create_valid_descriptor(), create_valid_metadata(), create_valid_layers())
        layers2 = (create_valid_layers()[0],)
        identity2 = ExecutionPlanFactory.create_identity(create_valid_descriptor(), create_valid_metadata(), layers2)
        assert identity1.snapshot.plan_hash != identity2.snapshot.plan_hash
        assert identity1.snapshot.layer_hash != identity2.snapshot.layer_hash
        assert identity1.snapshot.statistics_hash != identity2.snapshot.statistics_hash
        
    def test_snapshot_plan_lookup_hash_deterministic(self):
        identity1 = ExecutionPlanFactory.create_identity(create_valid_descriptor(), create_valid_metadata(), create_valid_layers())
        identity2 = ExecutionPlanFactory.create_identity(create_valid_descriptor(), create_valid_metadata(), create_valid_layers())
        assert identity1.snapshot.plan_lookup_hash == identity2.snapshot.plan_lookup_hash
        
    def test_snapshot_lookup_hash_deterministic(self):
        identity1 = ExecutionPlanFactory.create_identity(create_valid_descriptor(), create_valid_metadata(), create_valid_layers())
        identity2 = ExecutionPlanFactory.create_identity(create_valid_descriptor(), create_valid_metadata(), create_valid_layers())
        assert identity1.snapshot.lookup_hash == identity2.snapshot.lookup_hash
        
    def test_metadata_hashing_ignores_order(self):
        desc = create_valid_descriptor()
        layers = create_valid_layers()
        meta1 = ExecutionPlanMetadataFactory.create({"a": "1", "b": "2"}, {}, {})
        meta2 = ExecutionPlanMetadataFactory.create({"b": "2", "a": "1"}, {}, {})
        identity1 = ExecutionPlanFactory.create_identity(desc, meta1, layers)
        identity2 = ExecutionPlanFactory.create_identity(desc, meta2, layers)
        assert identity1.snapshot.metadata_hash == identity2.snapshot.metadata_hash


class TestRuntimeExecutionPlanFactory:
    def test_plan_factory_creates_wrapper(self):
        desc = create_valid_descriptor()
        plan = RuntimeExecutionPlanFactory.create(desc, create_valid_metadata(), create_valid_layers())
        assert plan.identifier == desc.plan_id
        assert isinstance(plan.identity, RuntimeExecutionPlanIdentity)
        
    def test_plan_factory_maintains_descriptor(self):
        desc = create_valid_descriptor()
        plan = RuntimeExecutionPlanFactory.create(desc, create_valid_metadata(), create_valid_layers())
        assert plan.identity.descriptor is desc
        
    def test_plan_factory_maintains_layers(self):
        layers = create_valid_layers()
        plan = RuntimeExecutionPlanFactory.create(create_valid_descriptor(), create_valid_metadata(), layers)
        assert plan.identity.layers is layers

    def test_plan_factory_maintains_metadata(self):
        meta = create_valid_metadata()
        plan = RuntimeExecutionPlanFactory.create(create_valid_descriptor(), meta, create_valid_layers())
        assert plan.identity.metadata is meta
        
    def test_factory_isolation_metadata(self):
        meta1 = create_valid_metadata()
        meta2 = create_valid_metadata()
        assert meta1 is not meta2
        
    def test_factory_isolation_descriptor(self):
        desc1 = create_valid_descriptor()
        desc2 = create_valid_descriptor()
        assert desc1 is not desc2
        
    def test_factory_isolation_snapshot(self):
        desc = create_valid_descriptor()
        meta = create_valid_metadata()
        layers = create_valid_layers()
        id1 = ExecutionPlanFactory.create_identity(desc, meta, layers)
        id2 = ExecutionPlanFactory.create_identity(desc, meta, layers)
        assert id1.snapshot is not id2.snapshot
        
    def test_factory_isolation_statistics(self):
        layers = create_valid_layers()
        stats1 = ExecutionPlanStatisticsBuilder.build(layers)
        stats2 = ExecutionPlanStatisticsBuilder.build(layers)
        assert stats1 is not stats2
        
    def test_factory_plan_wrapper_isolation(self):
        desc = create_valid_descriptor()
        meta = create_valid_metadata()
        layers = create_valid_layers()
        plan1 = RuntimeExecutionPlanFactory.create(desc, meta, layers)
        plan2 = RuntimeExecutionPlanFactory.create(desc, meta, layers)
        assert plan1 is not plan2
        assert plan1.identity is not plan2.identity

