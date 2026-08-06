import hashlib
import json
from dataclasses import asdict
from typing import Any
from .runtime_execution_engine_snapshot import RuntimeExecutionEngineSnapshot
from .runtime_execution_engine_descriptor import RuntimeExecutionEngineDescriptor
from .runtime_execution_engine_metadata import RuntimeExecutionEngineMetadata
from .runtime_execution_engine_statistics import RuntimeExecutionEngineStatistics
from .runtime_execution_scheduler import RuntimeExecutionScheduler

class ExecutionEngineSnapshotFactory:
    """
    ONLY performs structural construction.

    Performs NO:

    Execution
    Scheduling
    Providers
    Monitoring
    Telemetry
    Optimization
    Routing
    Planning
    Hardware
    Dependency Injection
    """
    
    @staticmethod
    def _hash_dict(data: dict) -> str:
        serialized = json.dumps(data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(serialized.encode('utf-8')).hexdigest()

    @staticmethod
    def create(
        descriptor: RuntimeExecutionEngineDescriptor,
        metadata: RuntimeExecutionEngineMetadata,
        statistics: RuntimeExecutionEngineStatistics,
        runtime_execution_scheduler: RuntimeExecutionScheduler,
        scheduler_lookup: Any,
        descriptor_lookup: Any,
        engine_lookup: Any
    ) -> RuntimeExecutionEngineSnapshot:
        
        descriptor_hash = ExecutionEngineSnapshotFactory._hash_dict(asdict(descriptor))
        
        # Consistent with identity hash construction
        scheduler_hash = hashlib.sha256(
            (runtime_execution_scheduler.identifier if runtime_execution_scheduler else "").encode('utf-8')
        ).hexdigest()
        
        scheduler_lookup_keys = sorted(list(scheduler_lookup.keys()))
        scheduler_lookup_hash = ExecutionEngineSnapshotFactory._hash_dict({"keys": scheduler_lookup_keys})
        
        descriptor_lookup_keys = sorted(list(descriptor_lookup.keys()))
        descriptor_lookup_hash = ExecutionEngineSnapshotFactory._hash_dict({"keys": descriptor_lookup_keys})
        
        engine_lookup_keys = sorted(list(engine_lookup.keys()))
        engine_lookup_hash = ExecutionEngineSnapshotFactory._hash_dict({"keys": engine_lookup_keys})
        
        metadata_dict = {
            "labels": dict(metadata.labels),
            "annotations": dict(metadata.annotations),
            "tags": sorted(list(metadata.tags))
        }
        metadata_hash = ExecutionEngineSnapshotFactory._hash_dict(metadata_dict)
        
        statistics_hash = ExecutionEngineSnapshotFactory._hash_dict(asdict(statistics))
        
        combined = "".join([
            descriptor_hash,
            scheduler_hash,
            scheduler_lookup_hash,
            descriptor_lookup_hash,
            engine_lookup_hash,
            metadata_hash,
            statistics_hash
        ])
        engine_hash = hashlib.sha256(combined.encode('utf-8')).hexdigest()
        
        return RuntimeExecutionEngineSnapshot(
            descriptor_hash=descriptor_hash,
            scheduler_hash=scheduler_hash,
            scheduler_lookup_hash=scheduler_lookup_hash,
            descriptor_lookup_hash=descriptor_lookup_hash,
            engine_lookup_hash=engine_lookup_hash,
            metadata_hash=metadata_hash,
            statistics_hash=statistics_hash,
            engine_hash=engine_hash
        )
