from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

class CapabilityType(Enum):
    """
    Represents capability categories supported by a provider.
    Pure categorization only. No behavior.
    """
    TEXT_GENERATION = "TEXT_GENERATION"
    CHAT = "CHAT"
    VISION = "VISION"
    IMAGE_GENERATION = "IMAGE_GENERATION"
    IMAGE_UNDERSTANDING = "IMAGE_UNDERSTANDING"
    AUDIO_TRANSCRIPTION = "AUDIO_TRANSCRIPTION"
    AUDIO_GENERATION = "AUDIO_GENERATION"
    VIDEO_ANALYSIS = "VIDEO_ANALYSIS"
    VIDEO_GENERATION = "VIDEO_GENERATION"
    EMBEDDINGS = "EMBEDDINGS"
    FUNCTION_CALLING = "FUNCTION_CALLING"
    STRUCTURED_OUTPUT = "STRUCTURED_OUTPUT"
    STREAMING = "STREAMING"


@dataclass(frozen=True)
class CapabilityLimits:
    """
    Represents provider limitations.
    Metadata only. No runtime configuration. No execution settings.
    """
    maximum_context_window: Optional[int] = None
    maximum_input_tokens: Optional[int] = None
    maximum_output_tokens: Optional[int] = None
    maximum_images: Optional[int] = None
    maximum_audio_duration_sec: Optional[int] = None
    maximum_video_duration_sec: Optional[int] = None
    supports_batching: bool = False
    supports_streaming: bool = False
    supports_json_mode: bool = False
    supports_multimodal: bool = False


@dataclass(frozen=True)
class ProviderCapability:
    """
    Represents immutable provider capability metadata.
    
    References the provider by its identity (provider_id). 
    It does NOT own or embed ProviderInfo.
    
    No behavior. No runtime logic. No execution or scheduling details.
    """
    provider_id: str
    supported_capabilities: List[CapabilityType] = field(default_factory=list)
    capability_limits: CapabilityLimits = field(default_factory=CapabilityLimits)
    supports_local_execution: bool = False
    supports_remote_execution: bool = False
    supports_gpu: bool = False
    supports_cpu: bool = False


@dataclass(frozen=True)
class ProviderCapabilityResult:
    """
    Immutable artifact produced by ProviderCapabilityRegistry.
    
    Contains provider capability, operation summary, and validation result.
    No mutable state. No behavior.
    """
    provider_capability: ProviderCapability
    operation_summary: str
    validation_result: bool
    timestamp: datetime = field(default_factory=datetime.utcnow)
