class RuntimeExecutionBuilderValidator:
    """
    Validates RuntimeExecutionBuilder structurally.
    
    VALIDATES ONLY
    - duplicate identifiers
    - missing composition
    - lookup consistency
    - descriptor consistency
    - snapshot consistency
    - structural integrity
    
    NEVER VALIDATES
    - execution
    - lifecycle
    - scheduling
    - providers
    - monitoring
    - telemetry
    - optimization
    - routing
    - AI models
    - hardware
    - prompt construction
    """
    
    @staticmethod
    def validate(builder: 'RuntimeExecutionBuilder') -> None:
        if not builder.identifier:
            raise ValueError("Builder identifier cannot be empty")
        if not builder.identity:
            raise ValueError("Builder identity cannot be None")
            
        identity = builder.identity
        if not identity.descriptor:
            raise ValueError("Builder descriptor cannot be None")
        if not identity.metadata:
            raise ValueError("Builder metadata cannot be None")
        if not identity.statistics:
            raise ValueError("Builder statistics cannot be None")
        if not identity.snapshot:
            raise ValueError("Builder snapshot cannot be None")
            
        if not identity.composition:
            raise ValueError("Execution composition cannot be None")
            
        # Descriptor consistency
        if identity.descriptor.builder_id != builder.identifier:
            raise ValueError("Descriptor builder_id must match builder identifier")
            
        # Check duplicate identifiers across main artifacts
        identifiers = {
            builder.identifier,
            identity.descriptor.execution_id,
            identity.descriptor.runtime_id,
            identity.descriptor.graph_id,
            identity.descriptor.plan_id,
            identity.descriptor.context_id,
            identity.descriptor.composition_id
        }
        if len(identifiers) != 7:
            raise ValueError("Duplicate identifiers detected across execution components")
            
        # Lookup consistency
        if builder.identifier not in identity.builder_lookup:
            raise ValueError("Builder identifier must exist in builder_lookup")
        if identity.descriptor.composition_id not in identity.composition_lookup:
            raise ValueError("Composition identifier must exist in composition_lookup")
        if identity.descriptor.builder_id not in identity.descriptor_lookup:
            raise ValueError("Builder descriptor identifier must exist in descriptor_lookup")
            
        # Snapshot structural consistency
        if not identity.snapshot.builder_hash:
            raise ValueError("Builder hash cannot be empty")
