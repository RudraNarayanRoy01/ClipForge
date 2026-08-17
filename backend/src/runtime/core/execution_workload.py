from typing import Protocol, runtime_checkable

@runtime_checkable
class ExecutionWorkload(Protocol):
    """
    Generic provider-neutral, strongly-typed contract for executable work.
    
    This represents the WHAT of execution (the normalized payload) independent of 
    the WHERE (ExecutionTarget) and HOW (ExecutionMechanism).
    
    It MUST remain strictly an immutable data contract and NEVER contain:
    - provider SDK instances
    - API keys or secrets
    - hardware/GPU handles
    - scheduler or telemetry state
    - network clients or event loops
    
    Specific capabilities (e.g. VideoAnalysis, AudioTranscription) will implement 
    concrete frozen dataclasses that satisfy this protocol.
    """
    @property
    def capability_id(self) -> str:
        """The capability identifier this workload is normalized for."""
        ...
