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
from src.domain.contracts.render_backend import IRenderBackend
from src.application.render_execution_service import RenderExecutionService


class MockBackend(IRenderBackend):
    def __init__(self):
        self.execute_mock = AsyncMock()

    async def execute(self, request: RenderExecutionRequest) -> RenderExecutionResult:
        return await self.execute_mock(request)


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
async def test_execution_service_success(validated_plan):
    backend = MockBackend()
    backend.execute_mock.return_value = RenderExecutionResult.success(
        duration_seconds=5.0,
        output_artifact_path="/tmp/output.mp4"
    )
    
    service = RenderExecutionService(backend)
    result = await service.execute_plan(
        validated_plan=validated_plan,
        output_destination="/tmp/output.mp4",
        execution_options={"quality": "high"}
    )
    
    # Verify the backend was called with the correct request model
    backend.execute_mock.assert_called_once()
    request = backend.execute_mock.call_args[0][0]
    
    assert isinstance(request, RenderExecutionRequest)
    assert request.validated_plan == validated_plan
    assert request.output_destination == "/tmp/output.mp4"
    assert request.execution_options == {"quality": "high"}
    
    # Verify service passes the result properly
    assert result.status == RenderExecutionStatus.COMPLETED
    assert result.duration_seconds == 5.0
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
