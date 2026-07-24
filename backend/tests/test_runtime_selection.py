import pytest
from src.runtime.core import (
    RuntimeContext,
    CapabilityCategory,
    CapabilityDescriptor,
    ProviderCategory,
    ProviderIdentity,
    ProviderDescriptor,
    HardwareCategory,
    HardwareIdentity,
    HardwareDescriptor,
    ProviderSelectionRequest,
    ProviderSelectionStatus
)

def test_provider_selection_request_is_immutable():
    request = ProviderSelectionRequest(requested_capability_id="vision.analysis")
    with pytest.raises(Exception):
        # dataclass frozen=True should prevent assignment
        request.requested_capability_id = "audio.transcription"

def test_provider_selection_success_path():
    context = RuntimeContext()
    
    # 1. Register a capability
    context.capability_registry.register_descriptor(
        CapabilityDescriptor(
            identifier="vision.analysis",
            display_name="Vision Analysis",
            description="Analyzes images",
            category=CapabilityCategory.VISION
        )
    )
    
    # 2. Register hardware
    context.hardware_discovery.register_hardware(
        HardwareDescriptor(
            identity=HardwareIdentity("gpu.cuda0"),
            display_name="NVIDIA GPU",
            description="CUDA device",
            category=HardwareCategory.GPU,
            vendor="NVIDIA",
            architecture="Ampere"
        )
    )
    
    # 3. Register a provider that supports the capability and requires the hardware
    context.provider_registry.register_provider(
        ProviderDescriptor(
            identity=ProviderIdentity("openai.vision"),
            display_name="OpenAI Vision",
            description="Cloud Vision Provider",
            category=ProviderCategory.VISION,
            supported_capability_ids=["vision.analysis"],
            supported_resource_ids=["gpu.cuda0"]
        )
    )
    
    # 4. Request Selection without constraints
    request = ProviderSelectionRequest(requested_capability_id="vision.analysis")
    result = context.provider_selection.select_provider(request)
    
    assert result.status == ProviderSelectionStatus.SUCCESS
    assert result.selected_provider_identity.identifier == "openai.vision"

def test_provider_selection_capability_not_supported():
    context = RuntimeContext()
    # Missing capability registration
    request = ProviderSelectionRequest(requested_capability_id="vision.analysis")
    result = context.provider_selection.select_provider(request)
    
    assert result.status == ProviderSelectionStatus.CAPABILITY_NOT_SUPPORTED
    assert result.selected_provider_identity is None

def test_provider_selection_no_provider_found():
    context = RuntimeContext()
    context.capability_registry.register_descriptor(
        CapabilityDescriptor(
            identifier="vision.analysis",
            display_name="Vision Analysis",
            description="Analyzes images",
            category=CapabilityCategory.VISION
        )
    )
    
    # Capability exists, but no provider registered
    request = ProviderSelectionRequest(requested_capability_id="vision.analysis")
    result = context.provider_selection.select_provider(request)
    
    assert result.status == ProviderSelectionStatus.NO_PROVIDER_FOUND
    assert result.selected_provider_identity is None

def test_provider_selection_constraints_not_satisfied():
    context = RuntimeContext()
    context.capability_registry.register_descriptor(
        CapabilityDescriptor(
            identifier="vision.analysis",
            display_name="Vision Analysis",
            description="Analyzes images",
            category=CapabilityCategory.VISION
        )
    )
    
    context.provider_registry.register_provider(
        ProviderDescriptor(
            identity=ProviderIdentity("openai.vision"),
            display_name="OpenAI Vision",
            description="Cloud Vision Provider",
            category=ProviderCategory.VISION,
            supported_capability_ids=["vision.analysis"],
            supported_resource_ids=[]
        )
    )
    
    # Request a constraint that the provider doesn't support
    request = ProviderSelectionRequest(
        requested_capability_id="vision.analysis",
        hardware_constraints=["gpu.cuda0"]
    )
    result = context.provider_selection.select_provider(request)
    
    assert result.status == ProviderSelectionStatus.CONSTRAINTS_NOT_SATISFIED
    assert result.selected_provider_identity is None
