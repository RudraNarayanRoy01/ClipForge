from typing import Any
from .runtime_execution_exceptions import ExecutionValidationException
from .runtime_execution_lifecycle import RuntimeExecutionLifecycle
from .runtime_execution_builder import RuntimeExecutionBuilder

class RuntimeExecutionLifecycleValidator:
    """
    VALIDATES ONLY
    - duplicate identifiers
    - missing builder
    - lookup consistency
    - descriptor consistency
    - snapshot consistency
    - structural integrity
    
    NEVER VALIDATES
    - execution
    - scheduling
    - lifecycle behaviour
    - routing
    - monitoring
    - telemetry
    - optimization
    - provider loading
    - hardware
    - AI models
    - prompt construction
    
    The validator remains purely structural.
    """

    @staticmethod
    def validate(lifecycle: RuntimeExecutionLifecycle) -> None:
        if not lifecycle.identifier:
            raise ExecutionValidationException("Missing identifier")
            
        identity = lifecycle.identity
        if not identity.descriptor:
            raise ExecutionValidationException("Missing descriptor")
            
        if not identity.runtime_execution_builder:
            raise ExecutionValidationException("Missing builder")
            
        if identity.descriptor.lifecycle_id != lifecycle.identifier:
            raise ExecutionValidationException("Identifier mismatch between descriptor and lifecycle")
            
        if lifecycle.identifier not in identity.lifecycle_lookup:
            raise ExecutionValidationException("Missing lifecycle in lookup")
            
        if identity.runtime_execution_builder.identifier not in identity.builder_lookup:
            raise ExecutionValidationException("Missing builder in lookup")
