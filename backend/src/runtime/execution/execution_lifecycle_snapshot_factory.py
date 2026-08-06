import hashlib
from .runtime_execution_lifecycle_descriptor import RuntimeExecutionLifecycleDescriptor
from .runtime_execution_lifecycle_metadata import RuntimeExecutionLifecycleMetadata
from .runtime_execution_lifecycle_statistics import RuntimeExecutionLifecycleStatistics
from .runtime_execution_lifecycle_snapshot import RuntimeExecutionLifecycleSnapshot
from .runtime_execution_builder import RuntimeExecutionBuilder

class ExecutionLifecycleSnapshotFactory:
    """
    ONLY performs structural construction.
    Performs NO:
    - Execution
    - Scheduling
    - Lifecycle Behaviour
    - Monitoring
    - Telemetry
    - Optimization
    - Provider Loading
    - Hardware Management
    - Routing
    - Planning
    """

    @staticmethod
    def _hash_string(value: str) -> str:
        return hashlib.sha256(value.encode('utf-8')).hexdigest()

    @staticmethod
    def create(
        descriptor: RuntimeExecutionLifecycleDescriptor,
        builder: RuntimeExecutionBuilder,
        builder_lookup: dict,
        descriptor_lookup: dict,
        lifecycle_lookup: dict,
        metadata: RuntimeExecutionLifecycleMetadata,
        statistics: RuntimeExecutionLifecycleStatistics
    ) -> RuntimeExecutionLifecycleSnapshot:
        
        # Sorted traversal to ensure deterministic hashes
        descriptor_hash = ExecutionLifecycleSnapshotFactory._hash_string(descriptor.lifecycle_id)
        builder_hash = ExecutionLifecycleSnapshotFactory._hash_string(f"{descriptor_hash}:{builder.identifier}")
        
        builder_keys = "".join(sorted(builder_lookup.keys()))
        builder_lookup_hash = ExecutionLifecycleSnapshotFactory._hash_string(f"{builder_hash}:{builder_keys}")
        
        desc_keys = "".join(sorted(descriptor_lookup.keys()))
        descriptor_lookup_hash = ExecutionLifecycleSnapshotFactory._hash_string(f"{builder_lookup_hash}:{desc_keys}")
        
        lifecycle_keys = "".join(sorted(lifecycle_lookup.keys()))
        lifecycle_lookup_hash = ExecutionLifecycleSnapshotFactory._hash_string(f"{descriptor_lookup_hash}:{lifecycle_keys}")
        
        meta_str = "".join(sorted(metadata.tags))
        metadata_hash = ExecutionLifecycleSnapshotFactory._hash_string(f"{lifecycle_lookup_hash}:{meta_str}")
        
        stat_str = f"{statistics.builder_count}:{statistics.builder_lookup_count}:{statistics.descriptor_lookup_count}:{statistics.lifecycle_lookup_count}"
        statistics_hash = ExecutionLifecycleSnapshotFactory._hash_string(f"{metadata_hash}:{stat_str}")
        
        lifecycle_hash = ExecutionLifecycleSnapshotFactory._hash_string(f"{statistics_hash}:lifecycle")

        return RuntimeExecutionLifecycleSnapshot(
            descriptor_hash=descriptor_hash,
            builder_hash=builder_hash,
            builder_lookup_hash=builder_lookup_hash,
            descriptor_lookup_hash=descriptor_lookup_hash,
            lifecycle_lookup_hash=lifecycle_lookup_hash,
            metadata_hash=metadata_hash,
            statistics_hash=statistics_hash,
            lifecycle_hash=lifecycle_hash
        )
