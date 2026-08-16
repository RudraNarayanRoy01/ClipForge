from dataclasses import dataclass

@dataclass(frozen=True)
class CapabilityRequest:
    """
    An immutable request for a Runtime Capability.
    
    This represents a consumer's request for a specific capability (e.g., 'campaign.summary.generate')
    without specifying how it should be executed, which provider to use, or any execution-specific
    state.
    """
    capability_id: str
