import pytest
import uuid
from unittest.mock import Mock

from src.infrastructure.runtime_adapters.runtime_transcription_adapter import RuntimeTranscriptionAdapter
from src.runtime.invocation.runtime_invocation_facade import RuntimeInvocationFacade
from src.runtime.execution.execution_result import ExecutionResult, ExecutionOutcome
from src.transcription.dtos import TranscriptionRequest, Transcript
from src.transcription.exceptions import TranscriptionProcessingError


@pytest.mark.asyncio
async def test_runtime_transcription_adapter_success():
    facade = Mock(spec=RuntimeInvocationFacade)
    
    facade_result = Mock(spec=ExecutionResult)
    facade_result.outcome = ExecutionOutcome.SUCCESS
    
    adapter = RuntimeTranscriptionAdapter(facade=facade)
    
    expected_transcript = Mock(spec=Transcript)
    
    def side_effect(intent, planning_context):
        intent.payload.context.result = expected_transcript
        return facade_result
        
    facade.invoke.side_effect = side_effect
    
    request = TranscriptionRequest(video_asset_id=uuid.uuid4(), storage_path="s3://test")
    
    transcript = await adapter.transcribe(request)
    
    assert transcript is expected_transcript
    facade.invoke.assert_called_once()

@pytest.mark.asyncio
async def test_runtime_transcription_adapter_failure():
    facade = Mock(spec=RuntimeInvocationFacade)
    
    facade_result = Mock(spec=ExecutionResult)
    facade_result.outcome = ExecutionOutcome.FAILED
    facade_result.error_message = "Runtime failed"
    facade.invoke.return_value = facade_result
    
    adapter = RuntimeTranscriptionAdapter(facade=facade)
    request = TranscriptionRequest(video_asset_id=uuid.uuid4(), storage_path="s3://test")
    
    with pytest.raises(TranscriptionProcessingError) as exc:
        await adapter.transcribe(request)
        
    assert "Runtime transcription failed: Runtime failed" in str(exc.value)

@pytest.mark.asyncio
async def test_runtime_transcription_adapter_context_exception():
    facade = Mock(spec=RuntimeInvocationFacade)
    
    facade_result = Mock(spec=ExecutionResult)
    facade_result.outcome = ExecutionOutcome.SUCCESS
    
    adapter = RuntimeTranscriptionAdapter(facade=facade)
    
    def side_effect(intent, planning_context):
        intent.payload.context.exception = ValueError("Context failed")
        return facade_result
        
    facade.invoke.side_effect = side_effect
    
    request = TranscriptionRequest(video_asset_id=uuid.uuid4(), storage_path="s3://test")
    
    with pytest.raises(ValueError) as exc:
        await adapter.transcribe(request)
        
    assert "Context failed" in str(exc.value)
