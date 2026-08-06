from .runtime_execution_scheduler import RuntimeExecutionScheduler
from .runtime_execution_exceptions import ExecutionValidationException

class RuntimeExecutionSchedulerValidator:
    """
    VALIDATES ONLY:

    duplicate identifiers
    missing lifecycle
    lookup consistency
    descriptor consistency
    snapshot consistency
    structural integrity

    NEVER VALIDATES:

    execution
    scheduling
    dispatch
    queues
    workers
    threads
    routing
    monitoring
    telemetry
    optimization
    providers
    hardware
    AI models
    prompt construction
    """
    @staticmethod
    def validate(scheduler: RuntimeExecutionScheduler) -> None:
        if not scheduler:
            raise ExecutionValidationException("Scheduler is missing")
        
        identity = scheduler.identity
        if not identity:
            raise ExecutionValidationException("Identity is missing")
            
        if not identity.runtime_execution_lifecycle:
            raise ExecutionValidationException("Missing lifecycle")
            
        if identity.descriptor.scheduler_id != scheduler.identifier:
            raise ExecutionValidationException("Duplicate identifiers or mismatch in descriptor")
            
        if identity.descriptor.scheduler_id not in identity.scheduler_lookup:
            raise ExecutionValidationException("Scheduler not found in scheduler_lookup")

        if identity.descriptor.lifecycle_id not in identity.lifecycle_lookup:
            raise ExecutionValidationException("Lifecycle not found in lifecycle_lookup")
            
        if identity.descriptor.scheduler_id not in identity.descriptor_lookup:
            raise ExecutionValidationException("Descriptor not found in descriptor_lookup")
            
        if not identity.snapshot.scheduler_hash:
            raise ExecutionValidationException("Snapshot consistency error: missing scheduler_hash")
