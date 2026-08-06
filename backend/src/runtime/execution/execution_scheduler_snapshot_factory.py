import hashlib
import json
from dataclasses import asdict
from typing import Any
from .runtime_execution_scheduler_snapshot import RuntimeExecutionSchedulerSnapshot
from .runtime_execution_scheduler_descriptor import RuntimeExecutionSchedulerDescriptor
from .runtime_execution_scheduler_metadata import RuntimeExecutionSchedulerMetadata
from .runtime_execution_scheduler_statistics import RuntimeExecutionSchedulerStatistics
from .runtime_execution_lifecycle import RuntimeExecutionLifecycle

class ExecutionSchedulerSnapshotFactory:
    """
    ONLY performs structural construction.

    Performs NO:

    Execution
    Scheduling
    Monitoring
    Telemetry
    Optimization
    Provider Loading
    Hardware Management
    Routing
    Planning
    """
    
    @staticmethod
    def _hash_dict(data: dict) -> str:
        serialized = json.dumps(data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(serialized.encode('utf-8')).hexdigest()

    @staticmethod
    def create(
        descriptor: RuntimeExecutionSchedulerDescriptor,
        metadata: RuntimeExecutionSchedulerMetadata,
        statistics: RuntimeExecutionSchedulerStatistics,
        runtime_execution_lifecycle: RuntimeExecutionLifecycle,
        lifecycle_lookup: Any,
        descriptor_lookup: Any,
        scheduler_lookup: Any
    ) -> RuntimeExecutionSchedulerSnapshot:
        
        descriptor_hash = ExecutionSchedulerSnapshotFactory._hash_dict(asdict(descriptor))
        
        lifecycle_hash = hashlib.sha256(runtime_execution_lifecycle.identifier.encode('utf-8')).hexdigest()
        
        lifecycle_lookup_keys = sorted(list(lifecycle_lookup.keys()))
        lifecycle_lookup_hash = ExecutionSchedulerSnapshotFactory._hash_dict({"keys": lifecycle_lookup_keys})
        
        descriptor_lookup_keys = sorted(list(descriptor_lookup.keys()))
        descriptor_lookup_hash = ExecutionSchedulerSnapshotFactory._hash_dict({"keys": descriptor_lookup_keys})
        
        scheduler_lookup_keys = sorted(list(scheduler_lookup.keys()))
        scheduler_lookup_hash = ExecutionSchedulerSnapshotFactory._hash_dict({"keys": scheduler_lookup_keys})
        
        metadata_dict = {
            "labels": dict(metadata.labels),
            "annotations": dict(metadata.annotations),
            "tags": sorted(list(metadata.tags))
        }
        metadata_hash = ExecutionSchedulerSnapshotFactory._hash_dict(metadata_dict)
        
        statistics_hash = ExecutionSchedulerSnapshotFactory._hash_dict(asdict(statistics))
        
        combined = "".join([
            descriptor_hash,
            lifecycle_hash,
            lifecycle_lookup_hash,
            descriptor_lookup_hash,
            scheduler_lookup_hash,
            metadata_hash,
            statistics_hash
        ])
        scheduler_hash = hashlib.sha256(combined.encode('utf-8')).hexdigest()
        
        return RuntimeExecutionSchedulerSnapshot(
            descriptor_hash=descriptor_hash,
            lifecycle_hash=lifecycle_hash,
            lifecycle_lookup_hash=lifecycle_lookup_hash,
            descriptor_lookup_hash=descriptor_lookup_hash,
            scheduler_lookup_hash=scheduler_lookup_hash,
            metadata_hash=metadata_hash,
            statistics_hash=statistics_hash,
            scheduler_hash=scheduler_hash
        )
