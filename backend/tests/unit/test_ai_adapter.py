import pytest
from unittest.mock import AsyncMock, MagicMock
from pydantic import BaseModel

from src.infrastructure.ai_adapter import (
    AIProviderLLMEngineAdapter, 
    TopicListSchema, 
    TopicSegmentSchema, 
    TimeRangeSchema,
    ClipListSchema,
    ClipSegmentSchema,
    GeneratedCaptionSchema
)
from src.domain.entities import TimelineContext, TimeRange
from src.intelligence.schemas.ai_models import AIResponse


@pytest.fixture
def mock_provider():
    provider = AsyncMock()
    return provider

@pytest.fixture
def adapter(mock_provider):
    return AIProviderLLMEngineAdapter(mock_provider)

def test_detect_topics(adapter, mock_provider):
    # Arrange
    transcript = "Welcome to the podcast. Today we talk about AI."
    
    mock_response = AIResponse(
        provider="mock",
        model="mock",
        latency_ms=100,
        structured_output=TopicListSchema(
            topics=[
                TopicSegmentSchema(
                    time_range=TimeRangeSchema(start_time=0.0, end_time=1.5),
                    title="Intro",
                    summary="Podcast intro"
                )
            ]
        )
    )
    mock_provider.generate.return_value = mock_response

    # Act
    topics = adapter.detect_topics(transcript)

    # Assert
    assert len(topics) == 1
    assert topics[0].title == "Intro"
    assert topics[0].summary == "Podcast intro"
    assert topics[0].time_range.start_time == 0.0
    assert topics[0].time_range.end_time == 1.5
    
    mock_provider.generate.assert_called_once()
    request_arg = mock_provider.generate.call_args[0][0]
    assert transcript in request_arg.prompt
    assert request_arg.response_schema == TopicListSchema

def test_generate_clips(adapter, mock_provider):
    # Arrange
    context = TimelineContext(video_asset_id=MagicMock())
    context.words = [MagicMock()] * 10 # 10 words
    
    mock_response = AIResponse(
        provider="mock",
        model="mock",
        latency_ms=100,
        structured_output=ClipListSchema(
            clips=[
                ClipSegmentSchema(
                    start_time=0.0,
                    end_time=5.0,
                    title="Awesome Clip",
                    hook_text="Watch this!",
                    hashtags=["#ai"],
                    captions=[
                        GeneratedCaptionSchema(
                            time_range=TimeRangeSchema(start_time=0.0, end_time=5.0),
                            text="Watch this!"
                        )
                    ],
                    virality_score=90,
                    ai_rationale="Very engaging"
                )
            ]
        )
    )
    mock_provider.generate.return_value = mock_response

    # Act
    clips = adapter.generate_clips(context)

    # Assert
    assert len(clips) == 1
    assert clips[0].title == "Awesome Clip"
    assert clips[0].virality_score == 90
    assert clips[0].boundaries.start_time == 0.0
    assert clips[0].boundaries.end_time == 5.0
    assert len(clips[0].captions) == 1
    
    mock_provider.generate.assert_called_once()

def test_rank_clips(adapter):
    # Arrange
    clip1 = MagicMock()
    clip1.virality_score = 50
    clip2 = MagicMock()
    clip2.virality_score = 90
    
    # Act
    ranked = adapter.rank_clips([clip1, clip2], MagicMock())
    
    # Assert
    assert ranked[0] == clip2
    assert ranked[1] == clip1
