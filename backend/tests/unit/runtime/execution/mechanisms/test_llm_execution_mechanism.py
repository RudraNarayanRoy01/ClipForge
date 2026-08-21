import pytest
from unittest.mock import Mock, AsyncMock
import asyncio

from src.runtime.execution.mechanisms.llm_execution_mechanism import (
    LLMExecutionMechanism, LLMExecutionWorkload, LLMCapabilityContext
)
from src.runtime.execution.execution_result import ExecutionOutcome
from src.runtime.core.execution_target import ExecutionTarget
from src.intelligence.providers.capabilities import IAIProvider
from src.intelligence.schemas.ai_models import AIRequest, AIResponse

def test_llm_execution_mechanism_success():
    mock_provider = Mock(spec=IAIProvider)
    mock_response = Mock(spec=AIResponse)
    
    # Provider generate is async
    async def mock_generate(request):
        return mock_response
    mock_provider.generate = mock_generate
    
    mechanism = LLMExecutionMechanism(provider=mock_provider)
    
    request = Mock(spec=AIRequest)
    context = LLMCapabilityContext(request=request)
    workload = LLMExecutionWorkload(context=context)
    
    target = Mock(spec=ExecutionTarget)
    
    outcome, error = mechanism.execute(target, workload)
    
    assert outcome == ExecutionOutcome.SUCCESS
    assert error is None
    assert context.response is mock_response
    assert context.exception is None

def test_llm_execution_mechanism_failure():
    mock_provider = Mock(spec=IAIProvider)
    
    async def mock_generate(request):
        raise ValueError("Provider error")
    mock_provider.generate = mock_generate
    
    mechanism = LLMExecutionMechanism(provider=mock_provider)
    
    request = Mock(spec=AIRequest)
    context = LLMCapabilityContext(request=request)
    workload = LLMExecutionWorkload(context=context)
    
    target = Mock(spec=ExecutionTarget)
    
    outcome, error = mechanism.execute(target, workload)
    
    assert outcome == ExecutionOutcome.FAILED
    assert "Provider error" in error
    assert context.response is None
    assert isinstance(context.exception, ValueError)
