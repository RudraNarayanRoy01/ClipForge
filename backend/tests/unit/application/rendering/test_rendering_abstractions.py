import pytest
from dataclasses import asdict
from datetime import datetime

from src.application.rendering.models import (
    RenderJobId,
    RenderStage,
    RenderProgress,
    RenderCancellationToken,
    CancellationResult,
)

def test_render_progress_validation_valid():
    job_id = RenderJobId.generate()
    progress = RenderProgress(
        job_id=job_id,
        stage=RenderStage.COMPOSITING,
        percentage=50.0,
        message="Halfway there"
    )
    assert progress.percentage == 50.0
    assert progress.stage == RenderStage.COMPOSITING

def test_render_progress_validation_percentage_bounds():
    job_id = RenderJobId.generate()
    
    with pytest.raises(ValueError, match="Percentage must be between 0.0 and 100.0"):
        RenderProgress(job_id=job_id, stage=RenderStage.INITIALIZING, percentage=-1.0, message="")
        
    with pytest.raises(ValueError, match="Percentage must be between 0.0 and 100.0"):
        RenderProgress(job_id=job_id, stage=RenderStage.COMPLETED, percentage=101.0, message="")

def test_render_progress_validation_completed_implies_100_percent():
    job_id = RenderJobId.generate()
    
    # Should raise because stage is COMPLETED but percentage is not 100
    with pytest.raises(ValueError, match="COMPLETED stage implies 100.0% percentage"):
        RenderProgress(job_id=job_id, stage=RenderStage.COMPLETED, percentage=99.9, message="")
        
    # Should not raise
    progress = RenderProgress(job_id=job_id, stage=RenderStage.COMPLETED, percentage=100.0, message="Done")
    assert progress.percentage == 100.0

def test_render_progress_is_immutable():
    job_id = RenderJobId.generate()
    progress = RenderProgress(job_id=job_id, stage=RenderStage.ENCODING, percentage=10.0, message="")
    
    with pytest.raises(Exception):
        progress.percentage = 20.0

def test_render_cancellation_token_immutability_and_identity():
    job_id = RenderJobId.generate()
    token = RenderCancellationToken(job_id=job_id)
    
    assert token.job_id == job_id
    assert not token.is_cancelled
    
    with pytest.raises(Exception):
        token.is_cancelled = True
        
    with pytest.raises(Exception):
        token.job_id = RenderJobId.generate()

def test_render_cancellation_token_request_cancellation():
    job_id = RenderJobId.generate()
    token = RenderCancellationToken(job_id=job_id)
    
    assert not token.is_cancelled
    
    # request_cancellation should return a new token
    new_token = token.request_cancellation()
    
    assert new_token is not token
    assert new_token.job_id == token.job_id
    assert new_token.is_cancelled
    # Original token remains unmutated
    assert not token.is_cancelled

def test_render_stage_canonical_values():
    # Verify all required stages exist
    stages = [s.name for s in RenderStage]
    assert "INITIALIZING" in stages
    assert "LOADING_ASSETS" in stages
    assert "BUILDING_TIMELINE" in stages
    assert "COMPOSITING" in stages
    assert "ENCODING" in stages
    assert "FINALIZING" in stages
    assert "COMPLETED" in stages

def test_cancellation_result_canonical_values():
    results = [r.name for r in CancellationResult]
    assert "NOT_REQUESTED" in results
    assert "REQUESTED" in results
    assert "CANCELLED" in results
    assert "CANCELLATION_REJECTED" in results

def test_render_progress_serialization():
    job_id = RenderJobId.generate()
    now = datetime.utcnow()
    progress = RenderProgress(
        job_id=job_id,
        stage=RenderStage.COMPOSITING,
        percentage=45.5,
        message="Processing",
        timestamp=now
    )
    
    serialized = asdict(progress)
    assert serialized["job_id"] == asdict(job_id)
    assert serialized["stage"] == RenderStage.COMPOSITING
    assert serialized["percentage"] == 45.5
    assert serialized["message"] == "Processing"
    assert serialized["timestamp"] == now
