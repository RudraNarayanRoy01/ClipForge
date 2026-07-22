import pytest
import uuid
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from src.application.rendering.models import (
    RenderJob, RenderJobId, RenderJobStatus, RenderJobPriority, RenderJobMetadata
)
from src.application.rendering.exceptions import (
    InvalidRenderJobTransitionError,
    RenderJobValidationError,
)
from src.application.rendering.orchestrator import RenderJobOrchestrator
from src.application.rendering.interfaces import IRenderExecutionService
from src.application.execution_models import (
    RenderExecutionResult,
    RenderExecutionStatus,
    RenderFailureCategory,
    ValidatedRenderPlan,
)
from src.domain.render_plan import (
    RenderPlan, RenderLayer, LayerCategory, RenderMetadata, RenderResolution, FrameRate, AspectRatio
)


@pytest.fixture
def dummy_render_plan():
    metadata = RenderMetadata(
        resolution=RenderResolution(1920, 1080),
        frame_rate=FrameRate(30.0),
        duration_seconds=10.0,
        aspect_ratio=AspectRatio(16, 9)
    )
    layer = RenderLayer(
        id=uuid.uuid4(),
        category=LayerCategory.VIDEO,
        name="Main Video",
        z_index=0,
        tracks=[]
    )
    return RenderPlan(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        metadata=metadata,
        layers=[layer]
    )


@pytest.fixture
def empty_render_plan():
    # RenderPlan raises ValueError if layers is empty, so we must mock or bypass it if we want an empty layers RenderPlan
    # But for our test, we just want to trigger the orchestrator's validation.
    # Let's create an object that looks like RenderPlan but has empty layers.
    plan = MagicMock(spec=RenderPlan)
    plan.layers = []
    return plan


@pytest.fixture
def create_render_job(dummy_render_plan):
    def _create(status=RenderJobStatus.CREATED, plan=None):
        return RenderJob(
            id=RenderJobId.generate(),
            plan=plan or dummy_render_plan,
            status=status,
            priority=RenderJobPriority.NORMAL,
            metadata=RenderJobMetadata(
                project_id=uuid.uuid4(),
                created_at=datetime.utcnow(),
                requester="test_user",
                output_profile="default"
            )
        )
    return _create


@pytest.fixture
def mock_execution_service():
    return AsyncMock(spec=IRenderExecutionService)


@pytest.fixture
def orchestrator(mock_execution_service):
    return RenderJobOrchestrator(execution_service=mock_execution_service)


def test_validate_job_success(orchestrator, create_render_job):
    job = create_render_job(status=RenderJobStatus.CREATED)
    
    validated_job = orchestrator.validate_job(job)
    
    assert validated_job.status == RenderJobStatus.VALIDATED
    assert validated_job.id == job.id
    assert validated_job is not job  # Immutable check


def test_validate_job_invalid_status(orchestrator, create_render_job):
    job = create_render_job(status=RenderJobStatus.VALIDATED)
    
    with pytest.raises(InvalidRenderJobTransitionError):
        orchestrator.validate_job(job)


def test_validate_job_empty_timeline(orchestrator, create_render_job, empty_render_plan):
    job = create_render_job(status=RenderJobStatus.CREATED, plan=empty_render_plan)
    
    with pytest.raises(RenderJobValidationError, match="RenderPlan must contain at least one layer"):
        orchestrator.validate_job(job)


def test_execute_job_success(orchestrator, mock_execution_service, create_render_job):
    job = create_render_job(status=RenderJobStatus.VALIDATED)
    
    success_result = RenderExecutionResult.success(duration_seconds=10.5, output_artifact_path="/tmp/out.mp4")
    mock_execution_service.execute_plan.return_value = success_result
    
    completed_job = asyncio.run(orchestrator.execute_job(job, output_destination="/tmp/out.mp4"))
    
    assert completed_job.status == RenderJobStatus.COMPLETED
    assert completed_job.id == job.id
    mock_execution_service.execute_plan.assert_called_once()
    
    # Check that ValidatedRenderPlan was passed correctly
    call_args = mock_execution_service.execute_plan.call_args[1]
    assert isinstance(call_args["validated_plan"], ValidatedRenderPlan)
    assert call_args["output_destination"] == "/tmp/out.mp4"


def test_execute_job_failure(orchestrator, mock_execution_service, create_render_job):
    job = create_render_job(status=RenderJobStatus.VALIDATED)
    
    failure_result = RenderExecutionResult.failure(
        duration_seconds=5.0,
        category=RenderFailureCategory.INTERNAL_ERROR,
        message="Failed due to testing"
    )
    mock_execution_service.execute_plan.return_value = failure_result
    
    failed_job = asyncio.run(orchestrator.execute_job(job, output_destination="/tmp/out.mp4"))
    
    assert failed_job.status == RenderJobStatus.FAILED


def test_execute_job_invalid_status(orchestrator, create_render_job):
    job = create_render_job(status=RenderJobStatus.CREATED)
    
    with pytest.raises(InvalidRenderJobTransitionError):
        asyncio.run(orchestrator.execute_job(job, output_destination="/tmp/out.mp4"))
