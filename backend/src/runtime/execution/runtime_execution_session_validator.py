from .runtime_execution_session import RuntimeExecutionSession
from .runtime_execution_exceptions import ExecutionValidationException

class RuntimeExecutionSessionValidator:
    """
    VALIDATES ONLY:
    - duplicate identifiers
    - lookup consistency
    - descriptor consistency
    - session identifier consistency
    - snapshot consistency
    - structural integrity
    
    NEVER VALIDATES:
    - session execution
    - session state
    - execution state
    - execution progress
    - scheduling
    - dispatch
    - workers
    - queues
    - routing
    - monitoring
    - telemetry
    - optimization
    - recovery
    - providers
    - models
    - hardware
    - AI execution
    - prompt construction
    """
    
    @staticmethod
    def validate(session: RuntimeExecutionSession) -> None:
        if session is None:
            raise ExecutionValidationException("Session is missing")
        
        if not hasattr(session, 'identifier') or not session.identifier:
            raise ExecutionValidationException("Session identifier is missing")
            
        if not hasattr(session, 'identity') or session.identity is None:
            raise ExecutionValidationException("Identity is missing")
            
        identity = session.identity
        
        # Check identifier consistency
        if session.identifier != identity.descriptor.session_id:
            raise ExecutionValidationException("Duplicate identifiers: identifier mismatch between wrapper and descriptor")
        
        # Check lookup consistency
            
        if session.identifier not in identity.session_lookup:
            raise ExecutionValidationException("Session not found in session_lookup")
            
        if session.identifier not in identity.descriptor_lookup:
            raise ExecutionValidationException("Descriptor not found in descriptor_lookup")
            
        # Check snapshot consistency
        if not hasattr(identity.snapshot, 'session_hash') or not identity.snapshot.session_hash:
            raise ExecutionValidationException("Snapshot consistency error: session_hash is empty")
