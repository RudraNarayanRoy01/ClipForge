import pytest
import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock

from src.domain.render_plan import (
    RenderPlan, 
    RenderMetadata, 
    RenderResolution, 
    FrameRate, 
    AspectRatio, 
    RenderLayer,
    LayerCategory
)
from src.application.execution_models import (
    ValidatedRenderPlan,
    RenderExecutionRequest,
    RenderExecutionResult,
    RenderExecutionStatus,
    RenderFailureCategory,
)
from src.domain.models.render_result import RenderResult, RenderStatus
from src.domain.ports import IRenderBackend
from src.application.render_execution_service import RenderExecutionService


class MockBackend(IRenderBackend):
    def __init__(self):
        self.execute_mock = AsyncMock()

    async def execute(self, plan: RenderPlan, output_path: str) -> RenderResult:
        return await self.execute_mock(plan, output_path)


@pytest.fixture
def dummy_render_plan():
    metadata = RenderMetadata(
        resolution=RenderResolution(width=1920, height=1080),
        frame_rate=FrameRate(fps=30.0),
        duration_seconds=10.0,
        aspect_ratio=AspectRatio(width_ratio=16, height_ratio=9)
    )
    layer = RenderLayer(
        id=uuid.uuid4(),
        category=LayerCategory.VIDEO,
        name="Main Video",
        z_index=0
    )
    return RenderPlan(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        metadata=metadata,
        layers=[layer]
    )


@pytest.fixture
def validated_plan(dummy_render_plan):
    return ValidatedRenderPlan(
        plan=dummy_render_plan,
        validated_at=datetime.now(timezone.utc)
    )


@pytest.mark.asyncio
async def test_execution_service_success(validated_plan, dummy_render_plan):
    backend = MockBackend()
    backend.execute_mock.return_value = RenderResult(
        status=RenderStatus.COMPLETED,
        rendered_output_location="/tmp/output.mp4",
        rendered_duration=5.0
    )
    
    service = RenderExecutionService(backend)
    result = await service.execute_plan(
        validated_plan=validated_plan,
        output_destination="/tmp/output.mp4",
        execution_options={"quality": "high"}
    )
    
    # Verify the backend was called with the correct domain primitives
    backend.execute_mock.assert_called_once()
    plan, output_path = backend.execute_mock.call_args[0]
    
    assert isinstance(plan, RenderPlan)
    assert plan == dummy_render_plan
    assert output_path == "/tmp/output.mp4"
    
    # Verify service passes the result properly
    assert result.status == RenderExecutionStatus.COMPLETED
    assert result.duration_seconds >= 0.0
    assert result.output_artifact_path == "/tmp/output.mp4"


@pytest.mark.asyncio
async def test_execution_service_backend_exception_handling(validated_plan):
    backend = MockBackend()
    backend.execute_mock.side_effect = RuntimeError("FFmpeg crashed unexpectedly")
    
    service = RenderExecutionService(backend)
    result = await service.execute_plan(
        validated_plan=validated_plan,
        output_destination="/tmp/output.mp4"
    )
    
    # Service should catch the exception and return a structured failure result
    assert result.status == RenderExecutionStatus.FAILED
    assert result.diagnostics is not None
    assert result.diagnostics.category == RenderFailureCategory.INTERNAL_ERROR
    assert result.diagnostics.message == "An unexpected error occurred during backend execution."
    assert result.diagnostics.details["error_type"] == "RuntimeError"
    assert result.diagnostics.details["error_message"] == "FFmpeg crashed unexpectedly"


@pytest.mark.asyncio
@pytest.mark.parametrize("error_reason, expected_category", [
    ("resource_exhausted", RenderFailureCategory.RESOURCE_EXHAUSTED),
    ("validation", RenderFailureCategory.VALIDATION_REQUIRED),
    ("backend_failure", RenderFailureCategory.BACKEND_FAILURE),
    (None, RenderFailureCategory.BACKEND_FAILURE),
    ("unknown_reason", RenderFailureCategory.BACKEND_FAILURE),
])
async def test_execution_service_maps_error_reasons(
    validated_plan, error_reason, expected_category
):
    backend = MockBackend()
    metadata = {}
    if error_reason is not None:
        metadata["error_reason"] = error_reason

    backend.execute_mock.return_value = RenderResult(
        status=RenderStatus.FAILED,
        message="Simulated failure",
        rendering_metadata=metadata
    )
    
    service = RenderExecutionService(backend)
    result = await service.execute_plan(
        validated_plan=validated_plan,
        output_destination="/tmp/output.mp4"
    )
    
    assert result.status == RenderExecutionStatus.FAILED
    assert result.diagnostics is not None
    assert result.diagnostics.category == expected_category
    assert result.diagnostics.message == "Simulated failure"
