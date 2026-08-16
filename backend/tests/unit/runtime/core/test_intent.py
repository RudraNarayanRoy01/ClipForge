from dataclasses import FrozenInstanceError
import pytest
from src.runtime.core.intent import ExecutionIntent

def test_execution_intent_construction():
    """TEST 1 - Construction: ExecutionIntent can be instantiated with valid fields."""
    payload = {"some": "data"}
    intent = ExecutionIntent(
        capability_id="campaign.summary.generate",
        payload=payload,
        output_contract="ExtractionSummarySchema"
    )
    assert intent.capability_id == "campaign.summary.generate"
    assert intent.payload == payload
    assert intent.output_contract == "ExtractionSummarySchema"

def test_execution_intent_capability_identity():
    """TEST 2 - Capability Identity: Verify the field is preserved exactly."""
    intent = ExecutionIntent(
        capability_id="campaign.summary.generate",
        payload=None
    )
    assert intent.capability_id == "campaign.summary.generate"

def test_execution_intent_payload_preservation():
    """TEST 3 - Payload Preservation: Verify payload survives construction without transformation."""
    opaque_payload = {"arbitrary": "content", "nested": {"value": 42}}
    intent = ExecutionIntent(
        capability_id="test.capability",
        payload=opaque_payload
    )
    assert intent.payload is opaque_payload

def test_execution_intent_output_contract():
    """TEST 4 - Output Contract: Verify the value is preserved exactly."""
    intent = ExecutionIntent(
        capability_id="test.capability",
        payload=None,
        output_contract="ExtractionSummarySchema"
    )
    assert intent.output_contract == "ExtractionSummarySchema"

def test_execution_intent_structural_immutability():
    """TEST 5 - Structural Immutability: Verify the frozen dataclass rejects mutation."""
    intent = ExecutionIntent(
        capability_id="campaign.summary.generate",
        payload={"data": 1},
        output_contract="Schema"
    )
    
    with pytest.raises(FrozenInstanceError):
        intent.capability_id = "new.capability"
        
    with pytest.raises(FrozenInstanceError):
        intent.payload = {"new": "data"}
        
    with pytest.raises(FrozenInstanceError):
        intent.output_contract = "NewSchema"

def test_execution_intent_provider_neutrality():
    """
    TEST 6 - Provider Neutrality: Verify construction does not require provider configuration.
    
    This is proven by the successful construction of the object without supplying
    any provider-specific arguments like Ollama, OpenAI, or credentials.
    """
    intent = ExecutionIntent(
        capability_id="provider.neutral.capability",
        payload="test"
    )
    assert not hasattr(intent, "provider")
    assert not hasattr(intent, "model")

def test_execution_intent_hardware_neutrality():
    """
    TEST 7 - Hardware Neutrality: Verify construction does not require hardware configuration.
    
    This is proven by the successful construction of the object without supplying
    any hardware-specific arguments like GPU, CUDA, or RAM.
    """
    intent = ExecutionIntent(
        capability_id="hardware.neutral.capability",
        payload="test"
    )
    assert not hasattr(intent, "gpu")
    assert not hasattr(intent, "cuda")

def test_execution_intent_execution_neutrality():
    """
    TEST 8 - Execution Neutrality: Verify inspecting does not invoke RuntimeExecutor.
    
    This is proven structurally by the lack of any execution methods.
    """
    intent = ExecutionIntent(
        capability_id="test",
        payload=None
    )
    
    # Assert absence of any execution-related methods
    assert not hasattr(intent, "execute")
    assert not hasattr(intent, "run")
    assert not hasattr(intent, "submit")
    assert not hasattr(intent, "schedule")
    assert not hasattr(intent, "retry")
