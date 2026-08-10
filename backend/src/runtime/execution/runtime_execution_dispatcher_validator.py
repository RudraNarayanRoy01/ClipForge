from .runtime_execution_dispatcher import RuntimeExecutionDispatcher
from .runtime_execution_exceptions import ExecutionValidationException

class RuntimeExecutionDispatcherValidator:
    @staticmethod
    def validate(dispatcher: RuntimeExecutionDispatcher) -> None:
        if dispatcher is None:
            raise ExecutionValidationException("Dispatcher is missing")
            
        if not dispatcher.identifier:
            raise ExecutionValidationException("Identifier is missing")
            
        if not dispatcher.identity:
            raise ExecutionValidationException("Identity is missing")
            
        identity = dispatcher.identity
        if not identity.descriptor:
            raise ExecutionValidationException("Descriptor is missing")
        if not identity.metadata:
            raise ExecutionValidationException("Metadata is missing")
        if not identity.statistics:
            raise ExecutionValidationException("Statistics is missing")
        if not identity.snapshot:
            raise ExecutionValidationException("Snapshot is missing")
            
        if not identity.runtime_execution_state:
            raise ExecutionValidationException("Missing State")
            
        if dispatcher.identifier != identity.descriptor.dispatcher_id:
            raise ExecutionValidationException("Duplicate identifiers")
            
        # Lookup checks
        if identity.runtime_execution_state.identifier not in identity.state_lookup:
            raise ExecutionValidationException("State not found in state_lookup")
            
        if identity.descriptor.dispatcher_id not in identity.descriptor_lookup:
            raise ExecutionValidationException("Descriptor not found in descriptor_lookup")
            
        # Snapshot consistency check
        if not identity.snapshot.dispatcher_hash:
            raise ExecutionValidationException("Snapshot consistency error: dispatcher_hash is missing")
