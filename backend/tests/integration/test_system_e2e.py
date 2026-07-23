import pytest
import uuid
import datetime
import asyncio
import os
import tempfile
from typing import Dict, Any

from pydantic import BaseModel

from src.bootstrap.startup import initialize_container
from src.infrastructure.di.container import Container
from src.intelligence.interfaces.ai_service import IAIService
from src.intelligence.schemas.ai_models import AIExecutionCommand, AIResponse
from src.intelligence.services.campaign_intelligence import CampaignIntelligenceService
from src.domain.campaign_entities import (
    Campaign, CampaignRules, CampaignSummary, WorthItScore,
    CampaignExecutionPlan, CampaignClipStrategy, CampaignPromptTemplate, CampaignSuitabilityAssessment,
    PlanningValidationError
)
from src.editing.domain.models.state import TimelineState, TimelineMetadata, TimelineTrack
from src.editing.domain.enums.tracks import TimelineTrackType
from src.editing.domain.models.items import Clip, Subtitle, Overlay
from src.editing.domain.enums.items import TimelineItemType, ScalingMode
from src.editing.domain.value_objects.time import Time, TimeRange
from src.editing.domain.value_objects.spatial import BoundingBox, Position, Size
from src.application.render_planning_pipeline import RenderPlanningPipeline
from src.application.render_planner import RenderPlanner
from src.application.render_validator import RenderValidator
from src.application.render_composition_service import RenderCompositionService
from src.domain.render_plan import RenderPlan
from src.domain.models.render_profile import RenderProfile
from src.domain.entities import Resolution
from src.domain.value_objects import AspectRatio
from src.application.execution_models import ValidatedRenderPlan, RenderExecutionStatus, RenderExecutionResult
from src.application.render_execution_service import RenderExecutionService
from src.application.execution_models import RenderExecutionRequest, RenderFailureCategory
from src.domain.ports import IRenderBackend

# Mock AI Service that returns valid schemas for deterministic testing
class MockAIService(IAIService):
    def __init__(self, simulate_failure: bool = False, validation_failure: bool = False):
        self.simulate_failure = simulate_failure
        self.validation_failure = validation_failure
        self.call_count = 0

    async def execute(self, command: AIExecutionCommand) -> AIResponse:
        self.call_count += 1
        
        if self.simulate_failure and self.call_count == 1:
            raise Exception("Simulated transient AI failure")
            
        schema = command.response_schema
        output = None
        
        if schema.__name__ == "ExecutionPlanSchema":
            output = schema(
                target_platform="tiktok",
                recommended_clip_length=30,
                minimum_clip_length=15,
                maximum_clip_length=60,
                preferred_hook_style="high_energy",
                preferred_editing_style="fast_paced",
                caption_style="dynamic",
                call_to_action="subscribe",
                crop_strategy="center",
                subtitle_style="bold",
                required_emotions=["excited"],
                required_topics=["gaming"],
                priority_scene_types=["gameplay"],
                required_audio_style="upbeat",
                brand_voice="casual",
                virality_focus="retention",
                estimated_clip_count=5,
                estimated_editing_time_minutes=120,
                confidence_score=0.1 if self.validation_failure else 0.95
            )
        elif schema.__name__ == "ClipStrategySchema":
            output = schema(
                hook_priorities=["visual", "audio"],
                scene_priorities=["action", "reaction"],
                speech_characteristics=["clear"],
                emotion_targets=["happy"],
                energy_targets=["high"],
                pacing="fast",
                transition_style="zoom",
                camera_motion_preference="stable",
                visual_focus="center",
                audio_focus="dialogue"
            )
        elif schema.__name__ == "PromptTemplateSchema":
            output = schema(
                system_prompt="You are an editor.",
                reasoning_prompt="Analyze this.",
                ranking_prompt="Rank these.",
                render_prompt="Render plan.",
                metadata_prompt="Extract metadata."
            )
        
        return AIResponse(
            text="Mocked output",
            structured_output=output,
            provider="mock",
            model="mock",
            latency_ms=10
        )

# Mock Render Backend for Execution
class MockRenderingBackend(IRenderBackend):
    async def execute(self, request: RenderExecutionRequest) -> RenderExecutionResult:
        return RenderExecutionResult.success(
            duration_seconds=1.0,
            output_artifact_path=request.output_destination
        )


@pytest.fixture
def dummy_render_profile():
    return RenderProfile(
        name="1080p HD",
        profile_type="youtube",
        resolution=Resolution(width=1920, height=1080),
        aspect_ratio=AspectRatio.RATIO_16_9,
        frame_rate=30.0,
        video_codec="libx264",
        audio_codec="aac",
        video_bitrate="5000k",
        audio_bitrate="192k",
        sample_rate=44100,
        output_container=".mp4"
    )

@pytest.fixture
def dummy_timeline_state():
    metadata = TimelineMetadata(fps=30.0, resolution=(1920, 1080), sample_rate=44100)
    total_duration = Time(value=10.0)
    clip = Clip(
        id=uuid.uuid4(),
        item_type=TimelineItemType.CLIP,
        timeline_time_range=TimeRange(start=Time(value=0.0), end=Time(value=10.0)),
        asset_id=uuid.uuid4(),
    )
    video_track = TimelineTrack(
        id=uuid.uuid4(),
        track_type=TimelineTrackType.VIDEO,
        items=(clip,)
    )
    return TimelineState(
        video_tracks=(video_track,),
        audio_tracks=(),
        overlay_tracks=(),
        subtitle_tracks=(),
        metadata=metadata,
        total_duration=total_duration
    )

@pytest.mark.asyncio
async def test_scenario_1_simple_campaign(dummy_timeline_state, dummy_render_profile):
    """Verifies: Simple Campaign -> Single Media Asset -> Transcript -> RenderPlan."""
    # 1. Campaign Intelligence
    ai_service = MockAIService()
    campaign_service = CampaignIntelligenceService(structured_llm=None, ai_service=ai_service)
    
    campaign = Campaign(id=uuid.uuid4(), title="Test Campaign")
    
    plan = await campaign_service.generate_execution_plan(campaign)
    assert plan is not None
    assert plan.confidence_score == 0.95
    
    strategy = await campaign_service.generate_clip_strategy(campaign, plan)
    assert strategy is not None
    
    templates = await campaign_service.generate_prompt_template(campaign, plan, strategy)
    assert templates is not None

    # 2. Render Planning Pipeline
    planning_pipeline = RenderPlanningPipeline(
        planner=RenderPlanner(),
        validator=RenderValidator(),
        composer=RenderCompositionService()
    )
    
    render_plan = planning_pipeline.execute(dummy_timeline_state, dummy_render_profile)
    assert isinstance(render_plan, RenderPlan)
    assert len(render_plan.layers) == 4

@pytest.mark.asyncio
async def test_scenario_2_multiple_assets(dummy_render_profile):
    """Verifies: Campaign -> Multiple assets -> Timeline merge -> RenderPlan."""
    metadata = TimelineMetadata(fps=30.0, resolution=(1920, 1080), sample_rate=44100)
    total_duration = Time(value=20.0)
    
    clip1 = Clip(
        id=uuid.uuid4(), item_type=TimelineItemType.CLIP,
        timeline_time_range=TimeRange(start=Time(value=0.0), end=Time(value=10.0)), asset_id=uuid.uuid4()
    )
    clip2 = Clip(
        id=uuid.uuid4(), item_type=TimelineItemType.CLIP,
        timeline_time_range=TimeRange(start=Time(value=10.0), end=Time(value=20.0)), asset_id=uuid.uuid4()
    )
    subtitle = Subtitle(
        id=uuid.uuid4(), item_type=TimelineItemType.SUBTITLE,
        timeline_time_range=TimeRange(start=Time(value=5.0), end=Time(value=15.0)),
        text="Hello World", position=Position(x=100, y=900)
    )
    
    video_track = TimelineTrack(id=uuid.uuid4(), track_type=TimelineTrackType.VIDEO, items=(clip1, clip2))
    sub_track = TimelineTrack(id=uuid.uuid4(), track_type=TimelineTrackType.SUBTITLE, items=(subtitle,))
    
    complex_timeline = TimelineState(
        video_tracks=(video_track,), audio_tracks=(), overlay_tracks=(), subtitle_tracks=(sub_track,),
        metadata=metadata, total_duration=total_duration
    )
    
    planning_pipeline = RenderPlanningPipeline(
        planner=RenderPlanner(), validator=RenderValidator(), composer=RenderCompositionService()
    )
    
    render_plan = planning_pipeline.execute(complex_timeline, dummy_render_profile)
    assert isinstance(render_plan, RenderPlan)
    assert len(render_plan.layers) == 4 # E.g., Background + Video Tracks/Clips + Subtitles

@pytest.mark.asyncio
async def test_scenario_3_recoverable_ai_failure():
    """Verifies: Recoverable AI failure -> Retry policy -> Pipeline recovery."""
    ai_service = MockAIService(simulate_failure=True)
    campaign_service = CampaignIntelligenceService(structured_llm=None, ai_service=ai_service)
    
    campaign = Campaign(id=uuid.uuid4(), title="Test Campaign")
    
    # Normally a retry policy (like tenacity) wraps the caller or the service method itself.
    # To simulate the orchestrator handling this, we catch the failure on first call and retry.
    plan = None
    try:
        plan = await campaign_service.generate_execution_plan(campaign)
    except Exception as e:
        assert "Simulated transient AI failure" in str(e)
        # Orchestrator retry simulates second call
        plan = await campaign_service.generate_execution_plan(campaign)
        
    assert plan is not None
    assert plan.confidence_score == 0.95
    assert ai_service.call_count == 2

@pytest.mark.asyncio
async def test_scenario_4_invalid_campaign():
    """Verifies: Invalid campaign -> Validation failure -> Expected diagnostics."""
    # The validation failure triggers low confidence score which raises PlanningConfidenceError
    ai_service = MockAIService(validation_failure=True)
    campaign_service = CampaignIntelligenceService(structured_llm=None, ai_service=ai_service)
    
    campaign = Campaign(id=uuid.uuid4(), title="Invalid Campaign")
    
    from src.domain.campaign_entities import PlanningConfidenceError
    with pytest.raises(PlanningConfidenceError) as excinfo:
        await campaign_service.generate_execution_plan(campaign)
    
    assert "Execution plan confidence 0.1 is below threshold" in str(excinfo.value)

def test_scenario_5_application_startup():
    """Verifies: Application startup -> Container initialization -> Pipeline execution."""
    container = initialize_container()
    assert isinstance(container, Container)
    
    # Assert architectural isolation and correct wiring
    # We test that CampaignIntelligenceService can be resolved from the container correctly
    try:
        campaign_svc = container.resolve(CampaignIntelligenceService)
        assert isinstance(campaign_svc, CampaignIntelligenceService)
        # Make sure the container resolved the prompt manager or ai_service dependencies
        assert campaign_svc._ai_service is not None
    except Exception as e:
        pytest.fail(f"Dependency Injection container failed to resolve dependencies: {str(e)}")
