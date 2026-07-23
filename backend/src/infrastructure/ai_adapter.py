import asyncio
import uuid
from typing import List
from pydantic import BaseModel

from src.domain.ports import ILLMReasoningEngine
from src.domain.entities import (
    TopicSegment, ClipSegment, TimelineContext, 
    TimeRange, GeneratedCaption
)
from src.intelligence.providers.capabilities import IAIProvider
from src.intelligence.schemas.ai_models import AIRequest


# --- Pydantic Schemas for Structured Output ---

class TimeRangeSchema(BaseModel):
    start_time: float
    end_time: float

class TopicSegmentSchema(BaseModel):
    time_range: TimeRangeSchema
    title: str
    summary: str

class TopicListSchema(BaseModel):
    topics: List[TopicSegmentSchema]

class GeneratedCaptionSchema(BaseModel):
    time_range: TimeRangeSchema
    text: str

class ClipSegmentSchema(BaseModel):
    start_time: float
    end_time: float
    title: str
    hook_text: str
    hashtags: List[str]
    captions: List[GeneratedCaptionSchema]
    virality_score: int
    ai_rationale: str

class ClipListSchema(BaseModel):
    clips: List[ClipSegmentSchema]


# --- Adapter Implementation ---

class AIProviderLLMEngineAdapter(ILLMReasoningEngine):
    """
    Adapter bridging the legacy ILLMReasoningEngine domain port 
    with the new IAIProvider capability.
    
    This preserves the business contract while allowing adaptive AI runtime selection.
    """
    
    def __init__(self, provider: IAIProvider):
        self._provider = provider

    def detect_topics(self, text_transcript: str) -> List[TopicSegment]:
        prompt = f"Analyze the following transcript and detect logical topics. Format as JSON list.\n\nTranscript: {text_transcript}"
        request = AIRequest(
            prompt=prompt,
            response_schema=TopicListSchema,
            system_prompt="You are an expert video editor capable of identifying topic boundaries."
        )
        
        # We must run this async method synchronously to satisfy the Domain port signature.
        # This is safe because the Application layer executes this within `asyncio.to_thread`.
        response = asyncio.run(self._provider.generate(request))
        
        if not response.structured_output or not hasattr(response.structured_output, 'topics'):
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
        
        response = asyncio.run(self._provider.generate(request))
        
        if not response.structured_output or not hasattr(response.structured_output, 'clips'):
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
