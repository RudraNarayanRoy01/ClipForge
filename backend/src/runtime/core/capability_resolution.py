from .request import CapabilityRequest
from .capabilities import CapabilityDescriptor, RuntimeCapabilityRegistry

class CapabilityResolutionError(Exception):
    """
    Raised when a requested capability cannot be resolved to a known CapabilityDescriptor.
    This error distinguishes a knowledge/discovery failure from an execution or provider failure.
    """
    pass

class CapabilityResolver:
    """
    Resolves a CapabilityRequest to a known CapabilityDescriptor.
    
    This is a knowledge/discovery mechanism, not an execution mechanism.
    It does not select, instantiate, or execute providers.
    """
    
    def __init__(self, registry: RuntimeCapabilityRegistry):
        self._registry = registry

    def resolve(self, request: CapabilityRequest) -> CapabilityDescriptor:
        """
        Resolve a CapabilityRequest to a registered CapabilityDescriptor.
        
        Args:
            request: The provider-neutral capability request.
            
        Returns:
            The matched CapabilityDescriptor.
            
        Raises:
            CapabilityResolutionError: If the requested capability does not exist in the registry.
        """
        try:
            return self._registry.get_descriptor(request.capability_id)
        except KeyError as e:
            raise CapabilityResolutionError(
                f"Capability '{request.capability_id}' could not be resolved."
            ) from e
