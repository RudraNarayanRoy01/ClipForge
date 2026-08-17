import pytest
from unittest.mock import Mock, MagicMock

from src.runtime.core.request import CapabilityRequest
from src.runtime.core.capabilities import CapabilityDescriptor, CapabilityCategory
from src.runtime.core.intent import ExecutionIntent
from src.runtime.core.capability_resolution import CapabilityResolver, CapabilityResolutionError
from src.runtime.core.intent_assembly import CapabilityIntentAssembler
from src.runtime.core.capability_intent_preparation import CapabilityIntentPreparationService

@pytest.fixture
def mock_resolver():
    return Mock(spec=CapabilityResolver)

@pytest.fixture
def mock_assembler():
    return Mock(spec=CapabilityIntentAssembler)

@pytest.fixture
def preparation_service(mock_resolver, mock_assembler):
    return CapabilityIntentPreparationService(
        resolver=mock_resolver,
        assembler=mock_assembler
    )

def test_valid_preparation(preparation_service, mock_resolver, mock_assembler):
    """TEST 1 - VALID PREPARATION"""
    request = CapabilityRequest(capability_id="campaign.summary.generate")
    payload = {"campaign_text": "data"}
    
    descriptor = CapabilityDescriptor(
        identifier="campaign.summary.generate",
        display_name="Summary Gen",
        description="Gen",
        category=CapabilityCategory.LANGUAGE
    )
    
    intent = ExecutionIntent(
        capability_id="campaign.summary.generate",
        payload=payload
    )
    
    mock_resolver.resolve.return_value = descriptor
    mock_assembler.assemble.return_value = intent
    
    result = preparation_service.prepare(request, payload)
    
    assert result is intent
    assert isinstance(result, ExecutionIntent)

def test_capability_identity(preparation_service, mock_resolver, mock_assembler):
    """TEST 2 - CAPABILITY IDENTITY"""
    request = CapabilityRequest(capability_id="requested.capability.id")
    payload = {}
    
    # The resolver returns a descriptor with a specific identifier
    resolved_identifier = "resolved.capability.id"
    descriptor = CapabilityDescriptor(
        identifier=resolved_identifier,
        display_name="Resolved",
        description="Resolved Cap",
        category=CapabilityCategory.UTILITY
    )
    
    # The assembler should correctly use the resolved_identifier if operating correctly.
    # The test verifies the intent returned by preparation service uses the one from assembler.
    intent = ExecutionIntent(
        capability_id=resolved_identifier,
        payload=payload
    )
    
    mock_resolver.resolve.return_value = descriptor
    mock_assembler.assemble.return_value = intent
    
    result = preparation_service.prepare(request, payload)
    
    assert result.capability_id == resolved_identifier
    # Further ensure that it just delegates
    mock_assembler.assemble.assert_called_once_with(descriptor=descriptor, payload=payload)

def test_payload_preservation(preparation_service, mock_resolver, mock_assembler):
    """TEST 3 - PAYLOAD PRESERVATION"""
    request = CapabilityRequest(capability_id="test.cap")
    
    # Create an opaque object to test identity
    class OpaquePayload:
        pass
        
    payload = OpaquePayload()
    
    descriptor = CapabilityDescriptor(
        identifier="test.cap",
        display_name="Test",
        description="Test Cap",
        category=CapabilityCategory.UTILITY
    )
    
    intent = ExecutionIntent(
        capability_id="test.cap",
        payload=payload
    )
    
    mock_resolver.resolve.return_value = descriptor
    mock_assembler.assemble.return_value = intent
    
    result = preparation_service.prepare(request, payload)
    
    # Verify the EXACT payload identity is preserved in the resulting intent
    assert result.payload is payload
    
    # Verify the EXACT payload identity was passed to the assembler
    _, kwargs = mock_assembler.assemble.call_args
    assert kwargs["payload"] is payload

def test_output_contract_propagation(preparation_service, mock_resolver, mock_assembler):
    """TEST 4 - OUTPUT CONTRACT"""
    request = CapabilityRequest(capability_id="test.cap")
    payload = {}
    
    descriptor = CapabilityDescriptor(
        identifier="test.cap",
        display_name="Test",
        description="Test Cap",
        category=CapabilityCategory.UTILITY,
        metadata={"output_schema": "ExtractionSummarySchema"}
    )
    
    intent = ExecutionIntent(
        capability_id="test.cap",
        payload=payload,
        output_contract="ExtractionSummarySchema"
    )
    
    mock_resolver.resolve.return_value = descriptor
    mock_assembler.assemble.return_value = intent
    
    result = preparation_service.prepare(request, payload)
    
    assert result.output_contract == "ExtractionSummarySchema"

def test_unknown_capability_resolution_error(preparation_service, mock_resolver, mock_assembler):
    """TEST 5 - UNKNOWN CAPABILITY"""
    request = CapabilityRequest(capability_id="unknown.capability")
    payload = {}
    
    mock_resolver.resolve.side_effect = CapabilityResolutionError("Capability not found")
    
    with pytest.raises(CapabilityResolutionError):
        preparation_service.prepare(request, payload)
        
    # Assembler must not be called
    mock_assembler.assemble.assert_not_called()

def test_resolver_called_exactly_once(preparation_service, mock_resolver, mock_assembler):
    """TEST 6 - RESOLVER CALLED ONCE"""
    request = CapabilityRequest(capability_id="test.cap")
    payload = {}
    
    descriptor = CapabilityDescriptor(
        identifier="test.cap",
        display_name="Test",
        description="Test Cap",
        category=CapabilityCategory.UTILITY
    )
    intent = ExecutionIntent(capability_id="test.cap", payload=payload)
    
    mock_resolver.resolve.return_value = descriptor
    mock_assembler.assemble.return_value = intent
    
    preparation_service.prepare(request, payload)
    
    mock_resolver.resolve.assert_called_once_with(request)

def test_assembler_called_exactly_once(preparation_service, mock_resolver, mock_assembler):
    """TEST 7 - ASSEMBLER CALLED ONCE"""
    request = CapabilityRequest(capability_id="test.cap")
    payload = {"data": 123}
    
    descriptor = CapabilityDescriptor(
        identifier="test.cap",
        display_name="Test",
        description="Test Cap",
        category=CapabilityCategory.UTILITY
    )
    intent = ExecutionIntent(capability_id="test.cap", payload=payload)
    
    mock_resolver.resolve.return_value = descriptor
    mock_assembler.assemble.return_value = intent
    
    preparation_service.prepare(request, payload)
    
    mock_assembler.assemble.assert_called_once_with(descriptor=descriptor, payload=payload)

def test_execution_neutrality():
    """TEST 8 - EXECUTION NEUTRALITY"""
    import ast
    import inspect
    from pathlib import Path
    from src.runtime.core.capability_intent_preparation import CapabilityIntentPreparationService
    
    # 1. Structural evidence: constructor does not require an executor
    sig = inspect.signature(CapabilityIntentPreparationService.__init__)
    assert "executor" not in sig.parameters, "Constructor must not require an executor"
    assert "runtime_executor" not in sig.parameters, "Constructor must not require an executor"
    
    # 2. AST evidence: module does not import executor
    module_path = Path("backend/src/runtime/core/capability_intent_preparation.py")
    source_code = module_path.read_text(encoding="utf-8")
    tree = ast.parse(source_code)
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert "executor" not in alias.name.lower(), f"Prohibited execution import: {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                assert "executor" not in node.module.lower(), f"Prohibited execution from-import: {node.module}"
            for alias in node.names:
                assert "executor" not in alias.name.lower(), f"Prohibited execution alias: {alias.name}"

def test_provider_hardware_neutrality():
    """TEST 9 - PROVIDER/HARDWARE NEUTRALITY"""
    import ast
    from pathlib import Path
    
    module_path = Path("backend/src/runtime/core/capability_intent_preparation.py")
    source_code = module_path.read_text(encoding="utf-8")
    tree = ast.parse(source_code)
    
    prohibited_terms = [
        "ollama", "openai", "gemini", "provider", "hardware", "cuda", "gpu", "vram", "device"
    ]
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                for term in prohibited_terms:
                    assert term not in alias.name.lower(), f"Prohibited hardware/provider import: {alias.name}"
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                for term in prohibited_terms:
                    assert term not in node.module.lower(), f"Prohibited hardware/provider from-import: {node.module}"
            for alias in node.names:
                for term in prohibited_terms:
                    assert term not in alias.name.lower(), f"Prohibited hardware/provider alias: {alias.name}"
