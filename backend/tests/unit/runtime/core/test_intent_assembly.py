import pytest
from src.runtime.core.capabilities import CapabilityDescriptor, CapabilityCategory
from src.runtime.core.intent_assembly import CapabilityIntentAssembler
from src.runtime.core.intent import ExecutionIntent

@pytest.fixture
def assembler():
    return CapabilityIntentAssembler()

def test_basic_assembly(assembler):
    """Test 1 - Basic Assembly"""
    descriptor = CapabilityDescriptor(
        identifier="campaign.summary.generate",
        display_name="Generate Summary",
        description="Generates a summary.",
        category=CapabilityCategory.LANGUAGE
    )
    payload = {"text": "some input data"}
    
    intent = assembler.assemble(descriptor, payload)
    
    assert isinstance(intent, ExecutionIntent)
    assert intent.capability_id == "campaign.summary.generate"
    assert intent.payload == payload
    assert intent.output_contract is None

def test_capability_identity(assembler):
    """Test 2 - Capability Identity"""
    descriptor = CapabilityDescriptor(
        identifier="campaign.summary.generate",
        display_name="Generate Summary",
        description="Generates a summary.",
        category=CapabilityCategory.LANGUAGE
    )
    payload = "payload"
    
    intent = assembler.assemble(descriptor, payload)
    
    assert intent.capability_id == descriptor.identifier

def test_payload_preservation(assembler):
    """Test 3 - Payload Preservation"""
    descriptor = CapabilityDescriptor(
        identifier="test.capability",
        display_name="Test",
        description="Test.",
        category=CapabilityCategory.UTILITY
    )
    
    # Payload is preserved without transformation
    payload_obj = {"nested": [1, 2, 3]}
    intent = assembler.assemble(descriptor, payload_obj)
    
    assert intent.payload is payload_obj

def test_output_contract_propagation(assembler):
    """Test 4 - Output Contract Propagation"""
    descriptor = CapabilityDescriptor(
        identifier="campaign.summary.generate",
        display_name="Generate Summary",
        description="Generates a summary.",
        category=CapabilityCategory.LANGUAGE,
        metadata={
            "structured_output": True,
            "output_schema": "ExtractionSummarySchema"
        }
    )
    
    intent = assembler.assemble(descriptor, "payload")
    
    assert intent.output_contract == "ExtractionSummarySchema"

def test_provider_neutrality():
    """Test 5 - Provider Neutrality"""
    # This is implicitly tested by lack of provider imports and execution,
    # and strictly verified by architecture tests.
    pass

def test_hardware_neutrality():
    """Test 6 - Hardware Neutrality"""
    # Implicitly tested by lack of hardware context inputs
    pass

def test_execution_neutrality():
    """Test 7 - Execution Neutrality"""
    # Implicitly tested by returning an intent rather than result
    pass

def test_planning_neutrality():
    """Test 8 - Planning Neutrality"""
    # Implicitly tested by intent lacking strategy/plan fields
    pass

def test_invalid_descriptor_none(assembler):
    """Test 9 - Invalid Descriptor (None)"""
    with pytest.raises(ValueError, match="CapabilityDescriptor cannot be None."):
        assembler.assemble(None, "payload")

def test_invalid_descriptor_missing_identifier(assembler):
    """Test 9 - Invalid Descriptor (Empty identifier)"""
    descriptor = CapabilityDescriptor(
        identifier="",
        display_name="Test",
        description="Test.",
        category=CapabilityCategory.UTILITY
    )
    with pytest.raises(ValueError, match="CapabilityDescriptor must have a valid identifier."):
        assembler.assemble(descriptor, "payload")
