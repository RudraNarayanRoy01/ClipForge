import pytest
from unittest.mock import Mock, ANY

from src.infrastructure.runtime_adapters.runtime_reasoning_adapter import RuntimeReasoningAdapter
from src.runtime.invocation.runtime_invocation_facade import RuntimeInvocationFacade
from src.runtime.execution.execution_result import ExecutionResult, ExecutionOutcome
from src.domain.entities import TimelineContext, TimeRange
from src.intelligence.schemas.ai_models import AIResponse
import uuid

def test_runtime_reasoning_adapter_detect_topics_success():
    facade = Mock(spec=RuntimeInvocationFacade)
    
    # Mock successful facade result
    facade_result = Mock(spec=ExecutionResult)
    facade_result.outcome = ExecutionOutcome.SUCCESS
    facade.invoke.return_value = facade_result
    
    adapter = RuntimeReasoningAdapter(facade=facade)
    
    # The facade will be invoked with an ExecutionIntent containing an LLMExecutionWorkload.
    # The adapter expects the facade invocation to somehow mutate the workload's context.
    # Since we are mocking the facade, we have to side-effect the payload context to contain a response.
    
    def side_effect(intent, planning_context):
        # Mutate the context to inject a fake response
        mock_response = Mock(spec=AIResponse)
        mock_topics = Mock()
        mock_topic1 = Mock()
        mock_topic1.time_range.start_time = 0.0
        mock_topic1.time_range.end_time = 10.0
        mock_topic1.title = "Topic 1"
        mock_topic1.summary = "Summary 1"
        
        mock_topics.topics = [mock_topic1]
        mock_response.structured_output = mock_topics
        
        intent.payload.context.response = mock_response
        return facade_result
        
    facade.invoke.side_effect = side_effect
    
    topics = adapter.detect_topics("Test transcript")
    
    assert len(topics) == 1
    assert topics[0].title == "Topic 1"
    assert topics[0].time_range.start_time == 0.0
    facade.invoke.assert_called_once()

def test_runtime_reasoning_adapter_generate_clips_success():
    facade = Mock(spec=RuntimeInvocationFacade)
    
    facade_result = Mock(spec=ExecutionResult)
    facade_result.outcome = ExecutionOutcome.SUCCESS
    
    adapter = RuntimeReasoningAdapter(facade=facade)
    
    def side_effect(intent, planning_context):
        mock_response = Mock(spec=AIResponse)
        mock_clips = Mock()
        mock_clip1 = Mock()
        mock_clip1.start_time = 0.0
        mock_clip1.end_time = 10.0
        mock_clip1.title = "Clip 1"
        mock_clip1.hook_text = "Hook 1"
        mock_clip1.hashtags = ["#test"]
        mock_clip1.captions = []
        mock_clip1.virality_score = 99
        mock_clip1.ai_rationale = "Rationale"
        
        mock_clips.clips = [mock_clip1]
        mock_response.structured_output = mock_clips
        
        intent.payload.context.response = mock_response
        return facade_result
        
    facade.invoke.side_effect = side_effect
    
    context = TimelineContext(
        video_asset_id=uuid.uuid4(),
        words=[],
        duration=10.0,
        project_id=uuid.uuid4(),
        topic_segments=[]
    )
    clips = adapter.generate_clips(context)
    
    assert len(clips) == 1
    assert clips[0].title == "Clip 1"
    assert clips[0].virality_score == 99
    facade.invoke.assert_called_once()

def test_runtime_reasoning_adapter_failure_propagates_exception():
    facade = Mock(spec=RuntimeInvocationFacade)
    
    facade_result = Mock(spec=ExecutionResult)
    facade_result.outcome = ExecutionOutcome.FAILED
    facade_result.error_message = "Provider error"
    facade.invoke.return_value = facade_result
    
    adapter = RuntimeReasoningAdapter(facade=facade)
    
    with pytest.raises(RuntimeError) as exc:
        adapter.detect_topics("Test")
        
    assert "Runtime execution failed: Provider error" in str(exc.value)

def test_runtime_reasoning_adapter_propagates_context_exception():
    facade = Mock(spec=RuntimeInvocationFacade)
    
    facade_result = Mock(spec=ExecutionResult)
    facade_result.outcome = ExecutionOutcome.SUCCESS
    
    adapter = RuntimeReasoningAdapter(facade=facade)
    
    def side_effect(intent, planning_context):
        intent.payload.context.exception = ValueError("Context error")
        return facade_result
        
    facade.invoke.side_effect = side_effect
    
    with pytest.raises(ValueError) as exc:
        adapter.detect_topics("Test")
        
    assert "Context error" in str(exc.value)
