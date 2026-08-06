import hashlib
import json
from typing import Any, Dict
from types import MappingProxyType

from .runtime_execution_composition_snapshot import RuntimeExecutionCompositionSnapshot
from .runtime_execution_composition_descriptor import RuntimeExecutionCompositionDescriptor
from .runtime_execution_composition_metadata import RuntimeExecutionCompositionMetadata
from .runtime_execution_composition_statistics import RuntimeExecutionCompositionStatistics
from .runtime_execution_identity import RuntimeExecutionIdentity
from .runtime_execution_graph import RuntimeExecutionGraph
from .runtime_execution_plan import RuntimeExecutionPlan
from .runtime_execution_context import RuntimeExecutionContext

class ExecutionCompositionSnapshotFactory:
    """
    Performs ONLY structural construction.
    
    NEVER performs:
    - execution
    - lifecycle
    - scheduling
    - provider loading
    - telemetry
    - monitoring
    - optimization
    - planning
    """
    @staticmethod
    def _hash_dict(data: Dict[str, Any]) -> str:
        serialized = json.dumps(data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(serialized.encode('utf-8')).hexdigest()

    @staticmethod
    def create(
        descriptor: RuntimeExecutionCompositionDescriptor,
        metadata: RuntimeExecutionCompositionMetadata,
        statistics: RuntimeExecutionCompositionStatistics,
        execution_identity: RuntimeExecutionIdentity,
        execution_graph: RuntimeExecutionGraph,
        execution_plan: RuntimeExecutionPlan,
        execution_context: RuntimeExecutionContext,
        identity_lookup: MappingProxyType[str, RuntimeExecutionIdentity],
        graph_lookup: MappingProxyType[str, RuntimeExecutionGraph],
        plan_lookup: MappingProxyType[str, RuntimeExecutionPlan],
        context_lookup: MappingProxyType[str, RuntimeExecutionContext],
        descriptor_lookup: MappingProxyType[str, Any],
        composition_lookup: MappingProxyType[str, Any]
    ) -> RuntimeExecutionCompositionSnapshot:
        
        # Sort and hash individually
        descriptor_hash = ExecutionCompositionSnapshotFactory._hash_dict({
            "execution_id": descriptor.execution_id,
            "runtime_id": descriptor.runtime_id,
            "graph_id": descriptor.graph_id,
            "plan_id": descriptor.plan_id,
            "context_id": descriptor.context_id,
            "composition_id": descriptor.composition_id,
            "version": descriptor.version,
            "schema_version": descriptor.schema_version
        })
        
        # These assumes inner artifacts have snapshots, but for simplicity of deterministic composition hash
        # We will hash their identifiers to avoid deep traversal if they don't expose snapshot directly
        # Since this is above metadata boundary, we only hash identifiers for the lookup and ownership hashes
        # Let's ensure deterministic hashing of the composite objects by their identifier or snapshot.hash
        # Assume identity exposes snapshot.hash or similar. For pure architecture batch, let's use their identifier as proxy if needed, or their snapshot string
        # Actually, looking at the previous batches, they have `.identity.snapshot.hash` or `.identity.snapshot.execution_hash`.
        # I'll just hash their identifier to be safe and deterministic, or since they are dataclasses, maybe I can just hash their IDs.
        
        identity_hash = ExecutionCompositionSnapshotFactory._hash_dict({"id": execution_identity.descriptor.execution_id}) if execution_identity and execution_identity.descriptor else ExecutionCompositionSnapshotFactory._hash_dict({})
        graph_hash = ExecutionCompositionSnapshotFactory._hash_dict({"id": execution_graph.identifier}) if execution_graph else ExecutionCompositionSnapshotFactory._hash_dict({})
        plan_hash = ExecutionCompositionSnapshotFactory._hash_dict({"id": execution_plan.identifier}) if execution_plan else ExecutionCompositionSnapshotFactory._hash_dict({})
        context_hash = ExecutionCompositionSnapshotFactory._hash_dict({"id": execution_context.identifier}) if execution_context else ExecutionCompositionSnapshotFactory._hash_dict({})
        
        identity_lookup_hash = ExecutionCompositionSnapshotFactory._hash_dict({k: v.descriptor.execution_id if hasattr(v, 'descriptor') else str(v) for k, v in identity_lookup.items()})
        graph_lookup_hash = ExecutionCompositionSnapshotFactory._hash_dict({k: v.identifier for k, v in graph_lookup.items()})
        plan_lookup_hash = ExecutionCompositionSnapshotFactory._hash_dict({k: v.identifier for k, v in plan_lookup.items()})
        context_lookup_hash = ExecutionCompositionSnapshotFactory._hash_dict({k: v.identifier for k, v in context_lookup.items()})
        
        descriptor_lookup_hash = ExecutionCompositionSnapshotFactory._hash_dict({
            k: v.composition_id if hasattr(v, 'composition_id') else str(v) 
            for k, v in descriptor_lookup.items()
        })
        
        composition_lookup_hash = ExecutionCompositionSnapshotFactory._hash_dict({
            k: v.identifier if hasattr(v, 'identifier') else str(v) 
            for k, v in composition_lookup.items()
        })
        
        metadata_hash = ExecutionCompositionSnapshotFactory._hash_dict({
            "labels": dict(metadata.labels),
            "annotations": dict(metadata.annotations),
            "tags": sorted(list(metadata.tags))
        })
        
        statistics_hash = ExecutionCompositionSnapshotFactory._hash_dict({
            "identity_count": statistics.identity_count,
            "graph_count": statistics.graph_count,
            "plan_count": statistics.plan_count,
            "context_count": statistics.context_count,
            "identity_lookup_count": statistics.identity_lookup_count,
            "graph_lookup_count": statistics.graph_lookup_count,
            "plan_lookup_count": statistics.plan_lookup_count,
            "context_lookup_count": statistics.context_lookup_count,
            "descriptor_lookup_count": statistics.descriptor_lookup_count,
            "composition_lookup_count": statistics.composition_lookup_count
        })
        
        # Composition hash from hierarchy
        hierarchy = {
            "descriptor_hash": descriptor_hash,
            "identity_hash": identity_hash,
            "graph_hash": graph_hash,
            "plan_hash": plan_hash,
            "context_hash": context_hash,
            "identity_lookup_hash": identity_lookup_hash,
            "graph_lookup_hash": graph_lookup_hash,
            "plan_lookup_hash": plan_lookup_hash,
            "context_lookup_hash": context_lookup_hash,
            "descriptor_lookup_hash": descriptor_lookup_hash,
            "composition_lookup_hash": composition_lookup_hash,
            "metadata_hash": metadata_hash,
            "statistics_hash": statistics_hash
        }
        
        composition_hash = ExecutionCompositionSnapshotFactory._hash_dict(hierarchy)
        
        return RuntimeExecutionCompositionSnapshot(
            descriptor_hash=descriptor_hash,
            identity_hash=identity_hash,
            graph_hash=graph_hash,
            plan_hash=plan_hash,
            context_hash=context_hash,
            identity_lookup_hash=identity_lookup_hash,
            graph_lookup_hash=graph_lookup_hash,
            plan_lookup_hash=plan_lookup_hash,
            context_lookup_hash=context_lookup_hash,
            descriptor_lookup_hash=descriptor_lookup_hash,
            composition_lookup_hash=composition_lookup_hash,
            metadata_hash=metadata_hash,
            statistics_hash=statistics_hash,
            composition_hash=composition_hash
        )
