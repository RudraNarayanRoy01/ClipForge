import pytest
import uuid
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from src.application.rendering.models import (
    RenderJob, RenderJobId, RenderJobStatus, RenderJobPriority, RenderJobMetadata,
    RenderProgress, RenderStage
)
from src.application.rendering.exceptions import (
    InvalidRenderJobTransitionError,
    RenderJobValidationError,
)
from src.application.rendering.orchestrator import RenderJobOrchestrator
from src.application.rendering.interfaces import (
    IRenderExecutionService,
    IRenderProgressObserver,
    IRenderTelemetryObserver
)
from src.application.execution_models import (
    RenderExecutionResult,
    RenderExecutionStatus,
    RenderFailureCategory,
    ValidatedRenderPlan,
)
from src.domain.render_plan import (
    RenderPlan, RenderLayer, LayerCategory, RenderMetadata, RenderResolution, FrameRate, AspectRatio
)
from src.application.rendering.session import RenderExecutionSession
from src.application.rendering.telemetry import RenderExecutionEvent, RenderEventType


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


def test_initialize_session(orchestrator, create_render_job):
    job = create_render_job(status=RenderJobStatus.CREATED)
    session = orchestrator.initialize_session(job)
    
    assert isinstance(session, RenderExecutionSession)
    assert session.job == job
    assert len(session.history.events) == 1
    assert session.history.events[0].event_type == RenderEventType.JOB_CREATED


def test_validate_job_success(orchestrator, create_render_job):
    job = create_render_job(status=RenderJobStatus.CREATED)
    initial_session = orchestrator.initialize_session(job)
    
    validated_session = orchestrator.validate_job(initial_session)
    
    assert validated_session.job.status == RenderJobStatus.VALIDATED
    assert validated_session.job.id == job.id
    assert validated_session is not initial_session  # Immutable check
    
    # Telemetry should be recorded
    assert len(validated_session.history.events) == 2
    assert validated_session.history.events[-1].event_type == RenderEventType.VALIDATED


def test_validate_job_invalid_status(orchestrator, create_render_job):
    job = create_render_job(status=RenderJobStatus.VALIDATED)
    initial_session = orchestrator.initialize_session(job)
    
    with pytest.raises(InvalidRenderJobTransitionError):
        orchestrator.validate_job(initial_session)


def test_validate_job_empty_timeline(orchestrator, create_render_job, empty_render_plan):
    job = create_render_job(status=RenderJobStatus.CREATED, plan=empty_render_plan)
    initial_session = orchestrator.initialize_session(job)
    
    with pytest.raises(RenderJobValidationError, match="RenderPlan must contain at least one layer"):
        orchestrator.validate_job(initial_session)


def test_execute_job_success(orchestrator, mock_execution_service, create_render_job):
    job = create_render_job(status=RenderJobStatus.VALIDATED)
    session = orchestrator.initialize_session(job)
    
    success_result = RenderExecutionResult.success(duration_seconds=10.5, output_artifact_path="/tmp/out.mp4")
    mock_execution_service.execute_plan.return_value = success_result
    
    completed_session = asyncio.run(orchestrator.execute_job(session, output_destination="/tmp/out.mp4"))
    
    assert completed_session.job.status == RenderJobStatus.COMPLETED
    assert completed_session.job.id == job.id
    mock_execution_service.execute_plan.assert_called_once()
    
    # Check that ValidatedRenderPlan was passed correctly
    call_args = mock_execution_service.execute_plan.call_args[1]
    assert isinstance(call_args["validated_plan"], ValidatedRenderPlan)
    assert call_args["output_destination"] == "/tmp/out.mp4"
    
    # Check telemetry
    assert completed_session.history.events[-1].event_type == RenderEventType.COMPLETED
    assert completed_session.history.events[-2].event_type == RenderEventType.STARTED


def test_execute_job_failure(orchestrator, mock_execution_service, create_render_job):
    job = create_render_job(status=RenderJobStatus.VALIDATED)
    session = orchestrator.initialize_session(job)
    
    failure_result = RenderExecutionResult.failure(
        duration_seconds=5.0,
        category=RenderFailureCategory.INTERNAL_ERROR,
        message="Failed due to testing"
    )
    mock_execution_service.execute_plan.return_value = failure_result
    
    failed_session = asyncio.run(orchestrator.execute_job(session, output_destination="/tmp/out.mp4"))
    
    assert failed_session.job.status == RenderJobStatus.FAILED
    assert failed_session.history.events[-1].event_type == RenderEventType.FAILED
    assert failed_session.history.events[-1].message == "Failed due to testing"


def test_execute_job_invalid_status(orchestrator, create_render_job):
    job = create_render_job(status=RenderJobStatus.CREATED)
    session = orchestrator.initialize_session(job)
    
    with pytest.raises(InvalidRenderJobTransitionError):
        asyncio.run(orchestrator.execute_job(session, output_destination="/tmp/out.mp4"))


def test_observers_notified(orchestrator, mock_execution_service, create_render_job):
    job = create_render_job(status=RenderJobStatus.VALIDATED)
    session = orchestrator.initialize_session(job)
    
    progress_observer = MagicMock(spec=IRenderProgressObserver)
    telemetry_observer = MagicMock(spec=IRenderTelemetryObserver)
    
    orchestrator.register_progress_observer(progress_observer)
    orchestrator.register_telemetry_observer(telemetry_observer)
    
    async def side_effect(*args, **kwargs):
        # Fire progress from the executing callback
        cb = kwargs["execution_options"]["progress_callback"]
        prog = RenderProgress(
            job_id=job.id,
            stage=RenderStage.BUILDING_TIMELINE,
            percentage=50.0,
            message="Building..."
        )
        cb(prog)
        return RenderExecutionResult.success(duration_seconds=1.0, output_artifact_path="/out")

    mock_execution_service.execute_plan.side_effect = side_effect
    
    completed_session = asyncio.run(orchestrator.execute_job(session, output_destination="/tmp/out.mp4"))
    
    # Progress observer notified
    assert progress_observer.on_progress.call_count == 1
    progress_arg = progress_observer.on_progress.call_args[0][0]
    assert progress_arg.percentage == 50.0
    
    # Telemetry observer notified for STARTED and COMPLETED events (2 events)
    assert telemetry_observer.on_event.call_count == 2
    event_arg1 = telemetry_observer.on_event.call_args_list[0][0][0]
    assert event_arg1.event_type == RenderEventType.STARTED
    
    event_arg2 = telemetry_observer.on_event.call_args_list[1][0][0]
    assert event_arg2.event_type == RenderEventType.COMPLETED
    
    # Check that progress is in the completed_session
    assert completed_session.progress is not None
    assert completed_session.progress.percentage == 50.0
