from typing import Any
from .capabilities import CapabilityDescriptor
from .intent import ExecutionIntent

class CapabilityIntentAssembler:
    """
    Converts a successfully resolved CapabilityDescriptor and an opaque payload
    into an immutable ExecutionIntent.
    
    This is purely an assembly mechanism. It does not resolve capabilities,
    plan execution, select providers, or execute work.
    """
    
    def assemble(
        self,
        descriptor: CapabilityDescriptor,
        payload: Any,
    ) -> ExecutionIntent:
        """
        Assemble an ExecutionIntent.
        
        Args:
            descriptor: The resolved capability describing what work is requested.
            payload: Opaque caller-provided workload data to be preserved without transformation.
            
        Returns:
            An ExecutionIntent representing the immutable declarative requested work.
            
        Raises:
            ValueError: If the descriptor is None or lacks a valid identifier.
        """
        if descriptor is None:
            raise ValueError("CapabilityDescriptor cannot be None.")
        
        if not descriptor.identifier:
            raise ValueError("CapabilityDescriptor must have a valid identifier.")
            
        # Extract output contract descriptive identifier if available in metadata
        output_contract = descriptor.metadata.get("output_schema")
        
        return ExecutionIntent(
            capability_id=descriptor.identifier,
            payload=payload,
            output_contract=output_contract
        )
