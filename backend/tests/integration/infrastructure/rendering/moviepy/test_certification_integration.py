import pytest
import uuid
import asyncio
from pathlib import Path

from src.infrastructure.rendering.moviepy.backend import MoviePyRenderingBackend
from src.infrastructure.rendering.moviepy.translation import MoviePyRequestTranslator
from src.domain.contracts.render_backend import IRenderBackend
from src.application.execution_models import (
    RenderExecutionRequest,
    RenderExecutionResult,
    RenderExecutionStatus,
    ValidatedRenderPlan,
    RenderFailureCategory
)
from src.domain.render_plan import RenderPlan, RenderMetadata, RenderResolution, FrameRate, AspectRatio, RenderLayer, LayerCategory

try:
    from moviepy.editor import ColorClip
except ImportError:
    ColorClip = None

@pytest.fixture
def temp_output_dir(tmp_path):
    output_dir = tmp_path / "certification_output"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

def create_valid_dummy_request(output_dest: str) -> RenderExecutionRequest:
    import datetime
    metadata = RenderMetadata(
        duration_seconds=1.0,
        resolution=RenderResolution(width=640, height=360),
        frame_rate=FrameRate(fps=10.0),
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
    
    validated_plan = ValidatedRenderPlan(plan=plan, validated_at=datetime.datetime.utcnow())
    return RenderExecutionRequest(
        validated_plan=validated_plan,
        output_destination=output_dest,
        execution_options={}
    )


def test_interface_compliance():
    """Verify that MoviePyRenderingBackend fully satisfies the IRenderBackend contract."""
    backend = MoviePyRenderingBackend()
    assert isinstance(backend, IRenderBackend)


@pytest.mark.integration
def test_infrastructure_boundary_enforcement(temp_output_dir):
    """
    Verify that MoviePy-specific types never escape into the Application or Domain layers,
    even during a failure scenario.
    """
    if ColorClip is None:
        pytest.skip("MoviePy is not installed.")
        
    backend = MoviePyRenderingBackend()
    
    # Send a request that will fail because no media is provided
    output_dest = str(temp_output_dir / "failed.mp4")
    request = create_valid_dummy_request(output_dest)
    
    result = asyncio.run(backend.execute(request))
    
    # Result must be a domain/application model
    assert isinstance(result, RenderExecutionResult)
    assert result.status == RenderExecutionStatus.FAILED
    
    # Ensure no MoviePy classes leak in the diagnostics or details
    assert "MoviePy" in result.diagnostics.details.get("backend", "")
    assert isinstance(result.diagnostics.category, RenderFailureCategory)


@pytest.mark.integration
def test_immutable_contracts_and_determinism(temp_output_dir):
    """
    Verify determinism and immutability. 
    Running the same request multiple times should not mutate the original RenderPlan,
    and should yield deterministic results.
    """
    if ColorClip is None:
        pytest.skip("MoviePy is not installed.")
        
    backend = MoviePyRenderingBackend()
    
    output_dest = str(temp_output_dir / "deterministic.mp4")
    request = create_valid_dummy_request(output_dest)
    
    # Snapshot original plan state
    original_plan_id = request.validated_plan.plan.id
    original_layer_count = len(request.validated_plan.plan.layers)
    
    # Execute first time
    result1 = asyncio.run(backend.execute(request))
    
    # Execute second time
    result2 = asyncio.run(backend.execute(request))
    
    # Assert immutability
    assert request.validated_plan.plan.id == original_plan_id
    assert len(request.validated_plan.plan.layers) == original_layer_count
    
    # Assert determinism (results should have same failure category and status)
    assert result1.status == result2.status
    assert result1.diagnostics.category == result2.diagnostics.category
