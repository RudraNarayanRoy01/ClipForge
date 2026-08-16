import pytest

from src.runtime.core.capabilities import (
    CapabilityDescriptor,
    CapabilityCategory,
    RuntimeCapabilityRegistry
)
from src.runtime.core.bootstrap import RuntimeBootstrap

def test_generate_summary_descriptor_semantics():
    """TEST 1 — Descriptor semantics: verify identity, category, and metadata."""
    descriptor = CapabilityDescriptor(
        identifier="campaign.summary.generate",
        display_name="Generate Campaign Summary",
        description="Generates a structured campaign summary from extracted or provided rules text.",
        category=CapabilityCategory.LANGUAGE,
        metadata={
            "structured_output": True,
            "output_schema": "ExtractionSummarySchema"
        },
        version="1.0"
    )
    
    assert descriptor.identifier == "campaign.summary.generate"
    assert descriptor.category == CapabilityCategory.LANGUAGE
    assert descriptor.metadata.get("structured_output") is True
    assert descriptor.metadata.get("output_schema") == "ExtractionSummarySchema"
    
    # Prove provider neutrality - no Ollama references
    assert "ollama" not in descriptor.identifier.lower()
    assert "ollama" not in descriptor.display_name.lower()
    assert "ollama" not in descriptor.description.lower()

def test_bootstrap_registers_capabilities():
    """TEST 2 — Bootstrap registration & TEST 3 — Descriptor discovery"""
    bootstrap = RuntimeBootstrap()
    bootstrap.startup()
    
    registry = bootstrap.context.capability_registry
    
    # Verify discovery via the actual registry API
    descriptor = registry.get_descriptor("campaign.summary.generate")
    assert descriptor is not None
    assert descriptor.identifier == "campaign.summary.generate"
    assert descriptor.category == CapabilityCategory.LANGUAGE
    assert descriptor.metadata["structured_output"] is True
    assert descriptor.metadata["output_schema"] == "ExtractionSummarySchema"

def test_registry_duplicate_protection():
    """TEST 4 — Duplicate protection: verify existing registry duplicate contract."""
    registry = RuntimeCapabilityRegistry()
    
    descriptor = CapabilityDescriptor(
        identifier="test.capability",
        display_name="Test",
        description="Test description",
        category=CapabilityCategory.UTILITY
    )
    
    # First registration succeeds
    registry.register_descriptor(descriptor)
    
    # Second registration raises ValueError
    with pytest.raises(ValueError) as exc_info:
        registry.register_descriptor(descriptor)
    
    assert "is already registered" in str(exc_info.value)

def test_repeated_startup_behavior():
    """TEST 5 — Repeated startup: verify idempotency guard works."""
    bootstrap = RuntimeBootstrap()
    
    # First startup
    bootstrap.startup()
    
    registry = bootstrap.context.capability_registry
    
    # Verify it was registered exactly once
    descriptors_after_first = registry.enumerate_descriptors()
    assert len([d for d in descriptors_after_first if d.identifier == "campaign.summary.generate"]) == 1
    
    # Second startup
    bootstrap.startup()
    
    # Verify it is still there and no errors were raised
    descriptors_after_second = registry.enumerate_descriptors()
    assert len([d for d in descriptors_after_second if d.identifier == "campaign.summary.generate"]) == 1
    
    # Registry count should remain unchanged
    assert len(descriptors_after_first) == len(descriptors_after_second)

def test_provider_neutrality():
    """TEST 6 — Provider neutrality: ensure Ollama is not coupled to the bootstrap integration."""
    bootstrap = RuntimeBootstrap()
    bootstrap.startup()
    
    descriptor = bootstrap.context.capability_registry.get_descriptor("campaign.summary.generate")
    
    # Deep check of the metadata and object
    for value in descriptor.metadata.values():
        if isinstance(value, str):
            assert "ollama" not in value.lower()
            assert "gemini" not in value.lower()
            assert "openai" not in value.lower()
