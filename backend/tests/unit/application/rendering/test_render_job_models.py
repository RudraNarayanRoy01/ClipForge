import uuid
import pytest
from datetime import datetime, timezone
from dataclasses import FrozenInstanceError

from src.application.rendering.models import (
    RenderJob,
    RenderJobId,
    RenderJobStatus,
    RenderJobPriority,
    RenderJobMetadata,
)
from src.domain.render_plan import (
    RenderPlan,
    RenderMetadata,
    RenderResolution,
    FrameRate,
    AspectRatio,
    RenderLayer,
    LayerCategory,
)


@pytest.fixture
def dummy_render_plan() -> RenderPlan:
    metadata = RenderMetadata(
        resolution=RenderResolution(1920, 1080),
        frame_rate=FrameRate(30.0),
        duration_seconds=10.0,
        aspect_ratio=AspectRatio(16, 9),
    )
    layer = RenderLayer(
        id=uuid.uuid4(),
        category=LayerCategory.VIDEO,
        name="Main Video",
        z_index=0,
    )
    return RenderPlan(
        id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        metadata=metadata,
        layers=[layer],
    )


@pytest.fixture
def dummy_metadata() -> RenderJobMetadata:
    return RenderJobMetadata(
        project_id=uuid.uuid4(),
        created_at=datetime.now(timezone.utc),
        requester="test_user",
        output_profile="high_quality_mp4",
        tags=["test", "urgent"],
        notes="Please prioritize this.",
    )


@pytest.fixture
def dummy_render_job(dummy_render_plan, dummy_metadata) -> RenderJob:
    return RenderJob(
        id=RenderJobId.generate(),
        plan=dummy_render_plan,
        status=RenderJobStatus.CREATED,
        priority=RenderJobPriority.NORMAL,
        metadata=dummy_metadata,
    )


def test_render_job_id_generation():
    job_id = RenderJobId.generate()
    assert isinstance(job_id.value, uuid.UUID)
    assert str(job_id) == str(job_id.value)


def test_render_job_id_is_immutable():
    job_id = RenderJobId.generate()
    with pytest.raises(FrozenInstanceError):
        job_id.value = uuid.uuid4()


def test_render_job_metadata_is_immutable(dummy_metadata):
    with pytest.raises(FrozenInstanceError):
        dummy_metadata.requester = "new_user"


def test_render_job_is_immutable(dummy_render_job):
    with pytest.raises(FrozenInstanceError):
        dummy_render_job.status = RenderJobStatus.RUNNING


def test_render_job_update_status(dummy_render_job):
    updated_job = dummy_render_job.update_status(RenderJobStatus.QUEUED)
    
    assert updated_job is not dummy_render_job
    assert updated_job.status == RenderJobStatus.QUEUED
    # Ensure other attributes remained exactly the same
    assert updated_job.id == dummy_render_job.id
    assert updated_job.plan == dummy_render_job.plan
    assert updated_job.priority == dummy_render_job.priority
    assert updated_job.metadata == dummy_render_job.metadata
    assert updated_job.schema_version == dummy_render_job.schema_version


def test_render_job_update_priority(dummy_render_job):
    updated_job = dummy_render_job.update_priority(RenderJobPriority.HIGH)
    
    assert updated_job is not dummy_render_job
    assert updated_job.priority == RenderJobPriority.HIGH
    # Ensure other attributes remained exactly the same
    assert updated_job.id == dummy_render_job.id
    assert updated_job.plan == dummy_render_job.plan
    assert updated_job.status == dummy_render_job.status
    assert updated_job.metadata == dummy_render_job.metadata


def test_render_job_status_enum_completeness():
    expected_statuses = {
        "CREATED", "VALIDATED", "QUEUED", "RUNNING", 
        "COMPLETED", "FAILED", "CANCELLED"
    }
    actual_statuses = {status.name for status in RenderJobStatus}
    assert expected_statuses == actual_statuses


def test_render_job_priority_enum_completeness():
    expected_priorities = {"LOW", "NORMAL", "HIGH", "CRITICAL"}
    actual_priorities = {priority.name for priority in RenderJobPriority}
    assert expected_priorities == actual_priorities

def test_schema_version_default(dummy_render_job):
    assert dummy_render_job.schema_version == "1.0"
