from .runtime_execution_engine import RuntimeExecutionEngine
from .runtime_execution_exceptions import ExecutionValidationException

class RuntimeExecutionEngineValidator:
    """
    VALIDATES ONLY:

    duplicate identifiers
    missing scheduler
    lookup consistency
    descriptor consistency
    snapshot consistency
    structural integrity

    NEVER VALIDATES:

    execution
    AI
    providers
    models
    routing
    dispatch
    monitoring
    telemetry
    optimization
    worker execution
    queue execution
    GPU
    CPU
    hardware
    prompt construction
    LLM outputs
    """
    @staticmethod
    def validate(engine: RuntimeExecutionEngine) -> None:
        if not engine:
            raise ExecutionValidationException("Engine is missing")
        
        identity = engine.identity
        if not identity:
            raise ExecutionValidationException("Identity is missing")
            
        if not identity.runtime_execution_scheduler:
            raise ExecutionValidationException("Missing scheduler")
            
        if identity.descriptor.engine_id != engine.identifier:
            raise ExecutionValidationException("Duplicate identifiers or mismatch in descriptor")
            
        if identity.descriptor.engine_id not in identity.engine_lookup:
            raise ExecutionValidationException("Engine not found in engine_lookup")

        if identity.descriptor.scheduler_id not in identity.scheduler_lookup:
            raise ExecutionValidationException("Scheduler not found in scheduler_lookup")
            
        if identity.descriptor.engine_id not in identity.descriptor_lookup:
            raise ExecutionValidationException("Descriptor not found in descriptor_lookup")
            
        if not identity.snapshot.engine_hash:
            raise ExecutionValidationException("Snapshot consistency error: missing engine_hash")
