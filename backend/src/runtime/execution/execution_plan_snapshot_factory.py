import hashlib
import json
from typing import Tuple, Any
from types import MappingProxyType
from .runtime_execution_plan_snapshot import RuntimeExecutionPlanSnapshot
from .runtime_execution_plan_descriptor import RuntimeExecutionPlanDescriptor
from .runtime_execution_plan_metadata import RuntimeExecutionPlanMetadata
from .runtime_execution_plan_statistics import RuntimeExecutionPlanStatistics
from .runtime_execution_layer import RuntimeExecutionLayer
from .runtime_execution_dependency_batch import RuntimeExecutionDependencyBatch

class ExecutionPlanSnapshotFactory:
    
    @classmethod
    def create(cls,
               descriptor: RuntimeExecutionPlanDescriptor,
               layers: Tuple[RuntimeExecutionLayer, ...],
               layer_lookup: MappingProxyType[str, RuntimeExecutionLayer],
               batch_lookup: MappingProxyType[str, RuntimeExecutionDependencyBatch],
               plan_lookup: MappingProxyType[str, Any],
               metadata: RuntimeExecutionPlanMetadata,
               statistics: RuntimeExecutionPlanStatistics) -> RuntimeExecutionPlanSnapshot:
        
        descriptor_hash = cls._hash_dict(descriptor.__dict__)
        
        # layer_hash and batch_hash
        layer_list = []
        batch_list = []
        for layer in layers:
            layer_list.append(layer.layer_identifier)
            for batch in layer.batches:
                batch_dict = {
                    "batch_identifier": batch.batch_identifier,
                    "ordered_node_identifiers": list(batch.ordered_node_identifiers),
                    "dependency_identifiers": sorted(list(batch.dependency_identifiers))
                }
                batch_list.append(cls._hash_dict(batch_dict))
        
        layer_hash = cls._hash_list(layer_list)
        batch_hash = cls._hash_list(batch_list)
        
        lookup_hash = cls._hash_dict({
            "layers": sorted(list(layer_lookup.keys())),
            "batches": sorted(list(batch_lookup.keys()))
        })
        
        plan_lookup_hash = cls._hash_list(sorted(list(plan_lookup.keys())))
        
        metadata_hash = cls._hash_dict({
            "labels": dict(metadata.labels),
            "annotations": dict(metadata.annotations),
            "tags": dict(metadata.tags)
        })
        
        statistics_hash = cls._hash_dict(statistics.__dict__)
        
        plan_hash = cls._hash_list([
            descriptor_hash,
            layer_hash,
            batch_hash,
            lookup_hash,
            plan_lookup_hash,
            metadata_hash,
            statistics_hash
        ])
        
        return RuntimeExecutionPlanSnapshot(
            descriptor_hash=descriptor_hash,
            layer_hash=layer_hash,
            batch_hash=batch_hash,
            lookup_hash=lookup_hash,
            plan_lookup_hash=plan_lookup_hash,
            metadata_hash=metadata_hash,
            statistics_hash=statistics_hash,
            plan_hash=plan_hash
        )

    @classmethod
    def _hash_dict(cls, data: dict) -> str:
        serialized = json.dumps(data, sort_keys=True)
        return hashlib.sha256(serialized.encode('utf-8')).hexdigest()
        
    @classmethod
    def _hash_list(cls, data: list) -> str:
        serialized = json.dumps(data, sort_keys=True)
        return hashlib.sha256(serialized.encode('utf-8')).hexdigest()
