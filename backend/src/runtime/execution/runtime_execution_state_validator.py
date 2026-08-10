from .runtime_execution_state import RuntimeExecutionState
from .runtime_execution_exceptions import ExecutionValidationException

class RuntimeExecutionStateValidator:
    @staticmethod
    def validate(state: RuntimeExecutionState) -> None:
        if state is None:
            raise ExecutionValidationException("State is missing")
            
        if not state.identifier:
            raise ExecutionValidationException("Identifier is missing")
            
        if not state.identity:
            raise ExecutionValidationException("Identity is missing")
            
        identity = state.identity
        if not identity.descriptor:
            raise ExecutionValidationException("Descriptor is missing")
        if not identity.metadata:
            raise ExecutionValidationException("Metadata is missing")
        if not identity.statistics:
            raise ExecutionValidationException("Statistics is missing")
        if not identity.snapshot:
            raise ExecutionValidationException("Snapshot is missing")
            
        if not identity.runtime_execution_session:
            raise ExecutionValidationException("Missing Session")
            
        if state.identifier != identity.descriptor.state_id:
            raise ExecutionValidationException("Duplicate identifiers")
            
        # Lookup checks
        if identity.runtime_execution_session.identifier not in identity.session_lookup:
            raise ExecutionValidationException("Session not found in session_lookup")
            
        if identity.descriptor.state_id not in identity.descriptor_lookup:
            raise ExecutionValidationException("Descriptor not found in descriptor_lookup")
            
        # Snapshot consistency check
        if not identity.snapshot.state_hash:
            raise ExecutionValidationException("Snapshot consistency error: state_hash is missing")
