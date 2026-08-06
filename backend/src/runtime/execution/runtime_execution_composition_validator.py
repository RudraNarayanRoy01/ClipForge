class RuntimeExecutionCompositionValidator:
    """
    Validates RuntimeExecutionComposition structurally.
    
    VALIDATES ONLY
    - duplicate identifiers
    - missing artifacts
    - lookup consistency
    - descriptor consistency
    - snapshot consistency
    - structural integrity
    
    NEVER VALIDATES
    - execution
    - scheduling
    - providers
    - lifecycle
    - telemetry
    - monitoring
    - optimization
    - planning
    - prompt construction
    - AI models
    - hardware
    """
    
    @staticmethod
    def validate(composition: 'RuntimeExecutionComposition') -> None:
        if not composition.identifier:
            raise ValueError("Composition identifier cannot be empty")
        if not composition.identity:
            raise ValueError("Composition identity cannot be None")
            
        identity = composition.identity
        if not identity.descriptor:
            raise ValueError("Composition descriptor cannot be None")
        if not identity.metadata:
            raise ValueError("Composition metadata cannot be None")
        if not identity.statistics:
            raise ValueError("Composition statistics cannot be None")
        if not identity.snapshot:
            raise ValueError("Composition snapshot cannot be None")
            
        if not identity.execution_identity:
            raise ValueError("Execution identity cannot be None")
        if not identity.execution_graph:
            raise ValueError("Execution graph cannot be None")
        if not identity.execution_plan:
            raise ValueError("Execution plan cannot be None")
        if not identity.execution_context:
            raise ValueError("Execution context cannot be None")
            
        # Descriptor consistency
        if identity.descriptor.composition_id != composition.identifier:
            raise ValueError("Descriptor composition_id must match composition identifier")
            
        # Check duplicate identifiers across main artifacts if applicable (they should ideally have different IDs but this is structural)
        identifiers = {
            composition.identifier,
            identity.descriptor.execution_id,
            identity.descriptor.runtime_id,
            identity.descriptor.graph_id,
            identity.descriptor.plan_id,
            identity.descriptor.context_id
        }
        if len(identifiers) != 6:
            raise ValueError("Duplicate identifiers detected across execution components")
            
        # Lookup consistency
        if composition.identifier not in identity.composition_lookup:
            raise ValueError("Composition identifier must exist in composition_lookup")
        if identity.descriptor.execution_id not in identity.identity_lookup:
            raise ValueError("Execution identifier must exist in identity_lookup")
        if identity.descriptor.graph_id not in identity.graph_lookup:
            raise ValueError("Graph identifier must exist in graph_lookup")
        if identity.descriptor.plan_id not in identity.plan_lookup:
            raise ValueError("Plan identifier must exist in plan_lookup")
        if identity.descriptor.context_id not in identity.context_lookup:
            raise ValueError("Context identifier must exist in context_lookup")
        
        # Snapshot structural consistency
        if not identity.snapshot.composition_hash:
            raise ValueError("Composition hash cannot be empty")
