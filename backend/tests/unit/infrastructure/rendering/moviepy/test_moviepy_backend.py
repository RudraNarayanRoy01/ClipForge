import pytest
import uuid
import tempfile
import os
from unittest.mock import Mock, patch
from datetime import datetime

from src.infrastructure.rendering.moviepy.backend import MoviePyRenderingBackend
from src.infrastructure.rendering.moviepy.translation import MoviePyRequestTranslator
from src.infrastructure.rendering.moviepy.structures import MoviePyRenderTask, MoviePyResourcePool
from src.application.execution_models import (
    RenderExecutionRequest, 
    ValidatedRenderPlan,
    RenderExecutionResult,
    RenderExecutionStatus,
    RenderFailureCategory
)
from src.domain.render_plan import RenderPlan, RenderMetadata
from src.domain.models.render_profile import RenderProfile
from src.domain.entities import Resolution
from src.editing.domain.models.state import TimelineState, TimelineMetadata
from src.editing.domain.value_objects.time import Time

from src.domain.render_plan import RenderPlan, RenderMetadata, RenderResolution, FrameRate, RenderLayer, LayerCategory, AspectRatio

@pytest.fixture
def dummy_request():
    metadata = RenderMetadata(
        duration_seconds=10.0,
        resolution=RenderResolution(width=1920, height=1080),
        frame_rate=FrameRate(fps=30.0),
        aspect_ratio=AspectRatio(width_ratio=16, height_ratio=9)
    )
    
    layer = RenderLayer(
        id=uuid.uuid4(),
        category=LayerCategory.VIDEO,
        name="Main Video",
        z_index=0
    )
    
    plan = RenderPlan(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        metadata=metadata,
        layers=[layer]
    )
    
    validated_plan = ValidatedRenderPlan(plan=plan, validated_at=datetime.utcnow())
    return RenderExecutionRequest(
        validated_plan=validated_plan,
        output_destination="/tmp/output.mp4"
    )

import asyncio

def test_moviepy_backend_success_execution(dummy_request):
    """
    Test that the backend successfully returns a completed RenderExecutionResult
    without performing actual rendering, maintaining stateless execution.
    """
    translator = MoviePyRequestTranslator()
    backend = MoviePyRenderingBackend(translator=translator)
    
    result = asyncio.run(backend.execute(dummy_request))
    
    assert isinstance(result, RenderExecutionResult)
    assert result.status == RenderExecutionStatus.COMPLETED
    assert result.output_artifact_path == "/tmp/output.mp4"
    assert result.duration_seconds >= 0.0
    assert result.diagnostics is None


def test_moviepy_backend_exception_translation(dummy_request):
    """
    Test that exceptions raised during execution are intercepted and 
    translated into a structured failure result.
    """
    # Mock translator to throw an OS exception
    mock_translator = Mock(spec=MoviePyRequestTranslator)
    mock_translator.translate.side_effect = OSError("Disk full")
    
    backend = MoviePyRenderingBackend(translator=mock_translator)
    result = asyncio.run(backend.execute(dummy_request))
    
    assert isinstance(result, RenderExecutionResult)
    assert result.status == RenderExecutionStatus.FAILED
    assert result.diagnostics is not None
    assert result.diagnostics.category == RenderFailureCategory.RESOURCE_EXHAUSTED
    assert "IO or OS error" in result.diagnostics.message
    assert result.diagnostics.details["error_type"] == "OSError"
    assert result.diagnostics.details["error_message"] == "Disk full"

def test_request_translation(dummy_request):
    """
    Verify the translator successfully translates ValidatedRenderPlan -> MoviePyRenderTask.
    """
    translator = MoviePyRequestTranslator()
    task = translator.translate(dummy_request.validated_plan, dummy_request.output_destination)
    
    assert isinstance(task, MoviePyRenderTask)
    assert task.original_plan_id == dummy_request.validated_plan.plan.id
    assert task.output_destination == dummy_request.output_destination
    assert task.resolution_width == 1920
    assert task.resolution_height == 1080
    assert task.fps == 30.0
    assert isinstance(task.resources, MoviePyResourcePool)

def test_resource_pool_ownership():
    """
    Verify MoviePyResourcePool provides cleanup behavior while deferring
    actual instantiation to future batches.
    """
    pool = MoviePyResourcePool()
    
    pool.video_clips[uuid.uuid4()] = "mock_clip"
    pool.register_temp_file("/tmp/temp1.mp4")
    
    assert len(pool.video_clips) == 1
    assert len(pool.temporary_files) == 1
    
    pool.cleanup()
    
    assert len(pool.video_clips) == 0
    assert len(pool.temporary_files) == 0
