from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime

class ProviderType(Enum):
    """
    Represents provider classification.
    Only categorization.
    """
    LOCAL = "LOCAL"
    CLOUD = "CLOUD"
    HYBRID = "HYBRID"

class ProviderStatus(Enum):
    """
    Represents provider registration state.
    No health information, no runtime state.
    """
    REGISTERED = "REGISTERED"
    DISABLED = "DISABLED"
    DEPRECATED = "DEPRECATED"

@dataclass(frozen=True)
class ProviderInfo:
    """
    Represents immutable provider metadata.
    
    Metadata only. No behavior.
    """
    provider_id: str
    display_name: str
    provider_type: ProviderType
    registration_status: ProviderStatus
    endpoint_type: str
    provider_version: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class ProviderRegistryResult:
    """
    Immutable artifact produced by ProviderRegistry.
    
    Contains registered providers, operation summary, and registration result.
    No mutable state. No execution behavior.
    """
    registered_providers: List[ProviderInfo]
    operation_summary: str
    registration_result: bool
    timestamp: datetime = field(default_factory=datetime.utcnow)
