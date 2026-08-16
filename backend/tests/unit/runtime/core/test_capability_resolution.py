import pytest
from src.runtime.core.capabilities import CapabilityDescriptor, CapabilityCategory, RuntimeCapabilityRegistry
from src.runtime.core.request import CapabilityRequest
from src.runtime.core.capability_resolution import CapabilityResolver, CapabilityResolutionError

def test_capability_request_construction():
    """Test A — Request construction"""
    request = CapabilityRequest(capability_id="campaign.summary.generate")
    assert request.capability_id == "campaign.summary.generate"
    # Ensure it's frozen and has no unnecessary fields
    with pytest.raises(Exception):
        request.capability_id = "other"

def test_successful_capability_resolution():
    """Test B — Successful resolution"""
    registry = RuntimeCapabilityRegistry()
    descriptor = CapabilityDescriptor(
        identifier="campaign.summary.generate",
        display_name="Generate Summary",
        description="Generates summary",
        category=CapabilityCategory.LANGUAGE
    )
    registry.register_descriptor(descriptor)
    
    resolver = CapabilityResolver(registry)
    request = CapabilityRequest(capability_id="campaign.summary.generate")
    
    resolved_descriptor = resolver.resolve(request)
    
    assert resolved_descriptor is not None
    assert resolved_descriptor.identifier == "campaign.summary.generate"
    assert resolved_descriptor.category == CapabilityCategory.LANGUAGE

def test_unknown_capability_resolution():
    """Test C — Unknown capability"""
    registry = RuntimeCapabilityRegistry()
    resolver = CapabilityResolver(registry)
    request = CapabilityRequest(capability_id="campaign.unknown.operation")
    
    with pytest.raises(CapabilityResolutionError) as exc_info:
        resolver.resolve(request)
        
    assert "campaign.unknown.operation" in str(exc_info.value)
    assert "could not be resolved" in str(exc_info.value)

def test_provider_neutrality():
    """Test D — Provider neutrality"""
    # Verify that CapabilityRequest and CapabilityResolver have no concrete provider references
    import inspect
    from src.runtime.core import request, capability_resolution
    
    request_source = inspect.getsource(request)
    resolver_source = inspect.getsource(capability_resolution)
    
    for source in [request_source, resolver_source]:
        assert "Ollama" not in source
        assert "OpenAI" not in source
        assert "Gemini" not in source
        assert "Provider" not in source # Except maybe conceptually, but we didn't add it

def test_registry_integrity():
    """Test E — Registry integrity"""
    registry = RuntimeCapabilityRegistry()
    descriptor = CapabilityDescriptor(
        identifier="campaign.summary.generate",
        display_name="Generate Summary",
        description="Generates summary",
        category=CapabilityCategory.LANGUAGE
    )
    registry.register_descriptor(descriptor)
    
    with pytest.raises(ValueError) as exc_info:
        registry.register_descriptor(descriptor)
        
    assert "already registered" in str(exc_info.value)

def test_resolution_is_not_execution():
    """Test F — Resolution is not execution"""
    registry = RuntimeCapabilityRegistry()
    descriptor = CapabilityDescriptor(
        identifier="campaign.summary.generate",
        display_name="Generate Summary",
        description="Generates summary",
        category=CapabilityCategory.LANGUAGE
    )
    registry.register_descriptor(descriptor)
    
    resolver = CapabilityResolver(registry)
    request = CapabilityRequest(capability_id="campaign.summary.generate")
    
    result = resolver.resolve(request)
    
    # Verify it returns a descriptor, not an execution result
    assert isinstance(result, CapabilityDescriptor)
    # Ensure there is no executor involved (by structural inspection)
    import inspect
    source = inspect.getsource(CapabilityResolver.resolve)
    assert "executor" not in source.lower()
    assert "execute" not in source.lower()
