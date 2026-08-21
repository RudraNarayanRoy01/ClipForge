import uuid
from typing import List

from src.domain.ports import ILLMReasoningEngine
from src.domain.entities import (
    TopicSegment, ClipSegment, TimelineContext, 
    TimeRange, GeneratedCaption
)
from src.intelligence.schemas.ai_models import AIRequest
from src.infrastructure.ai_adapter import (
    TopicListSchema, ClipListSchema
)
from src.runtime.invocation.runtime_invocation_facade import RuntimeInvocationFacade
from src.runtime.core.intent import ExecutionIntent
from src.runtime.core.planning_context import PlanningContext
from src.runtime.execution.execution_result import ExecutionOutcome
from src.runtime.execution.mechanisms.llm_execution_mechanism import (
    LLMCapabilityContext, LLMExecutionWorkload
)


class RuntimeReasoningAdapter(ILLMReasoningEngine):
    """
    Adapter bridging the ILLMReasoningEngine domain port with the new Runtime boundary.
    
    This replaces the legacy AIProviderLLMEngineAdapter by delegating execution
    to the RuntimeInvocationFacade instead of directly executing via a provider.
    """
    
    def __init__(self, facade: RuntimeInvocationFacade):
        self._facade = facade

    def _invoke_runtime(self, request: AIRequest) -> LLMCapabilityContext:
        """Helper to invoke the Runtime facade and extract the context."""
        context = LLMCapabilityContext(request=request)
        workload = LLMExecutionWorkload(context=context)
        intent = ExecutionIntent(
            capability_id="LLM_REASONING",
            payload=workload
        )
        planning_context = PlanningContext()

        result = self._facade.invoke(intent, planning_context)

        if result.outcome != ExecutionOutcome.SUCCESS:
            error_msg = result.error_message or "Unknown execution error"
            raise RuntimeError(f"Runtime execution failed: {error_msg}")
            
        if context.exception:
            raise context.exception
            
        return context

    def detect_topics(self, text_transcript: str) -> List[TopicSegment]:
        prompt = f"Analyze the following transcript and detect logical topics. Format as JSON list.\n\nTranscript: {text_transcript}"
        request = AIRequest(
            prompt=prompt,
            response_schema=TopicListSchema,
            system_prompt="You are an expert video editor capable of identifying topic boundaries."
        )
        
        context = self._invoke_runtime(request)
        response = context.response
        
        if not response or not response.structured_output or not hasattr(response.structured_output, 'topics'):
            return []
            
        topics = []
        for topic_schema in response.structured_output.topics:
            topics.append(
                TopicSegment(
                    time_range=TimeRange(topic_schema.time_range.start_time, topic_schema.time_range.end_time),
                    title=topic_schema.title,
                    summary=topic_schema.summary
                )
            )
        return topics

    def generate_clips(self, context: TimelineContext) -> List[ClipSegment]:
        prompt = f"Generate viral short-form clips based on this timeline context. Context words: {len(context.words)}."
        request = AIRequest(
            prompt=prompt,
            response_schema=ClipListSchema,
            system_prompt="You are an expert viral content creator."
        )
        
        runtime_context = self._invoke_runtime(request)
        response = runtime_context.response
        
        if not response or not response.structured_output or not hasattr(response.structured_output, 'clips'):
            return []
            
        clips = []
        for clip_schema in response.structured_output.clips:
            clip = ClipSegment(
                id=uuid.uuid4(),
                project_id=uuid.uuid4(),
                video_asset_id=context.video_asset_id,
                boundaries=TimeRange(clip_schema.start_time, clip_schema.end_time),
                title=clip_schema.title,
                hook_text=clip_schema.hook_text,
                hashtags=clip_schema.hashtags,
                captions=[
                    GeneratedCaption(
                        TimeRange(cap.time_range.start_time, cap.time_range.end_time),
                        cap.text
                    )
                    for cap in clip_schema.captions
                ],
                thumbnail_timestamp=clip_schema.start_time,
                virality_score=clip_schema.virality_score,
                ai_rationale=clip_schema.ai_rationale,
                user_approved=False
            )
            clips.append(clip)
        return clips

    def rank_clips(self, clips: List[ClipSegment], context: TimelineContext) -> List[ClipSegment]:
        """Rank clips based on virality score."""
        return sorted(clips, key=lambda c: c.virality_score, reverse=True)
