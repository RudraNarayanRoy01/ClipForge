import hashlib
import json
from typing import Any
from types import MappingProxyType

from .runtime_execution_builder_snapshot import RuntimeExecutionBuilderSnapshot
from .runtime_execution_builder_descriptor import RuntimeExecutionBuilderDescriptor
from .runtime_execution_builder_metadata import RuntimeExecutionBuilderMetadata
from .runtime_execution_builder_statistics import RuntimeExecutionBuilderStatistics
from .runtime_execution_composition import RuntimeExecutionComposition

class ExecutionBuilderSnapshotFactory:
    """
    ONLY performs structural construction.
    Performs NO Execution, Scheduling, Lifecycle, Telemetry, Monitoring, Optimization, Provider Loading, Hardware Management, Routing, Planning.
    """
    
    @staticmethod
    def create(
        descriptor: RuntimeExecutionBuilderDescriptor,
        composition: RuntimeExecutionComposition,
        composition_lookup: MappingProxyType[str, RuntimeExecutionComposition],
        descriptor_lookup: MappingProxyType[str, Any],
        builder_lookup: MappingProxyType[str, Any],
        metadata: RuntimeExecutionBuilderMetadata,
        statistics: RuntimeExecutionBuilderStatistics
    ) -> RuntimeExecutionBuilderSnapshot:
        
        def compute_hash(data: dict) -> str:
            # Deterministic SHA-256 only, sorted traversal, insertion-order independent
            json_str = json.dumps(data, sort_keys=True, separators=(',', ':'))
            return hashlib.sha256(json_str.encode('utf-8')).hexdigest()
            
        descriptor_hash = compute_hash({
            "execution_id": descriptor.execution_id,
            "runtime_id": descriptor.runtime_id,
            "graph_id": descriptor.graph_id,
            "plan_id": descriptor.plan_id,
            "context_id": descriptor.context_id,
            "composition_id": descriptor.composition_id,
            "builder_id": descriptor.builder_id,
            "version": descriptor.version,
            "schema_version": descriptor.schema_version
        })
        
        composition_hash = compute_hash({
            "composition_id": composition.identifier,
            "composition_hash": composition.identity.snapshot.composition_hash
        })
        
        composition_lookup_hash = compute_hash({
            k: v.identifier for k, v in sorted(composition_lookup.items())
        })
        
        descriptor_lookup_hash = compute_hash({
            k: v.builder_id for k, v in sorted(descriptor_lookup.items())
        })
        
        builder_lookup_hash = compute_hash({
            k: str(v) for k, v in sorted(builder_lookup.items())
        })
        
        metadata_hash = compute_hash({
            "labels": dict(metadata.labels),
            "annotations": dict(metadata.annotations),
            "tags": sorted(list(metadata.tags))
        })
        
        statistics_hash = compute_hash({
            "composition_count": statistics.composition_count,
            "composition_lookup_count": statistics.composition_lookup_count,
            "descriptor_lookup_count": statistics.descriptor_lookup_count,
            "builder_lookup_count": statistics.builder_lookup_count
        })
        
        builder_hash = compute_hash({
            "descriptor": descriptor_hash,
            "composition": composition_hash,
            "composition_lookup": composition_lookup_hash,
            "descriptor_lookup": descriptor_lookup_hash,
            "builder_lookup": builder_lookup_hash,
            "metadata": metadata_hash,
            "statistics": statistics_hash
        })
        
        return RuntimeExecutionBuilderSnapshot(
            descriptor_hash=descriptor_hash,
            composition_hash=composition_hash,
            composition_lookup_hash=composition_lookup_hash,
            descriptor_lookup_hash=descriptor_lookup_hash,
            builder_lookup_hash=builder_lookup_hash,
            metadata_hash=metadata_hash,
            statistics_hash=statistics_hash,
            builder_hash=builder_hash
        )
