from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime

class ModelType(Enum):
    """
    Represents model families and capabilities categorization.
    Categorization only. No behavior.
    """
    LLM = "LLM"
    CHAT = "CHAT"
    VISION = "VISION"
    IMAGE_GENERATION = "IMAGE_GENERATION"
    IMAGE_UNDERSTANDING = "IMAGE_UNDERSTANDING"
    EMBEDDING = "EMBEDDING"
    AUDIO = "AUDIO"
    TRANSCRIPTION = "TRANSCRIPTION"
    TEXT_TO_SPEECH = "TEXT_TO_SPEECH"
    VIDEO = "VIDEO"
    MULTIMODAL = "MULTIMODAL"

class ModelStatus(Enum):
    """
    Represents registration status of a model.
    Registration metadata only. NOT runtime availability or health.
    """
    AVAILABLE = "AVAILABLE"
    EXPERIMENTAL = "EXPERIMENTAL"
    DEPRECATED = "DEPRECATED"
    DISABLED = "DISABLED"

@dataclass(frozen=True)
class ModelInfo:
    """
    Canonical immutable Runtime model metadata.
    
    References the provider by its identity (provider_id).
    Does NOT own or embed ProviderInfo or ProviderCapability.
    
    Metadata only. No runtime behavior. No execution logic.
    """
    model_id: str
    provider_id: str
    display_name: str
    model_type: ModelType
    status: ModelStatus
    version: Optional[str] = None
    description: Optional[str] = None
    
    # Optional metadata boundaries
    release_date: Optional[str] = None
    parameter_count: Optional[int] = None
    context_window: Optional[int] = None
    supports_local: bool = False
    supports_remote: bool = False
    supports_quantization: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class ModelRegistryResult:
    """
    Immutable artifact produced by ModelRegistry.
    
    Contains registered models, operation summary, and validation result.
    No mutable state. No behavior.
    """
    registered_models: List[ModelInfo]
    operation_summary: str
    validation_result: bool
    timestamp: datetime = field(default_factory=datetime.utcnow)
