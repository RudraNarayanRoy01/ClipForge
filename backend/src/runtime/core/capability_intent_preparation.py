from typing import Any

from .request import CapabilityRequest
from .intent import ExecutionIntent
from .capability_resolution import CapabilityResolver
from .intent_assembly import CapabilityIntentAssembler

class CapabilityIntentPreparationService:
    """
    Coordinates the capability preparation flow from Request to Intent.
    
    It orchestrates:
    1. Resolving a CapabilityRequest to a known CapabilityDescriptor via CapabilityResolver.
    2. Assembling an ExecutionIntent via CapabilityIntentAssembler using the resolved descriptor and payload.
    
    It intentionally does NOT:
    - Execute capabilities
    - Plan execution
    - Select providers
    - Validate schemas
    - Modify the payload
    """
    
    def __init__(
        self,
        resolver: CapabilityResolver,
        assembler: CapabilityIntentAssembler,
    ) -> None:
        """
        Initialize the preparation service with its required dependencies.
        
        Args:
            resolver: The component responsible for capability resolution.
            assembler: The component responsible for intent assembly.
        """
        self._resolver = resolver
        self._assembler = assembler

    def prepare(
        self,
        request: CapabilityRequest,
        payload: Any,
    ) -> ExecutionIntent:
        """
        Prepare an ExecutionIntent from a CapabilityRequest and an opaque payload.
        
        Args:
            request: The consumer's request for a capability.
            payload: The opaque workload data to be passed to the capability.
            
        Returns:
            The prepared, declarative ExecutionIntent.
            
        Raises:
            CapabilityResolutionError: If the requested capability cannot be resolved.
        """
        descriptor = self._resolver.resolve(request)

        return self._assembler.assemble(
            descriptor=descriptor,
            payload=payload,
        )
