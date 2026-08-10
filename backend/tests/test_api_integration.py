import pytest
import uuid
from src.main import app
from src.domain.entities import Project, VideoAsset
from src.infrastructure.database import AsyncSessionLocal
from src.repositories.project_repository import ProjectRepository
from src.repositories.video_repository import VideoRepository
def test_health_endpoint_schema_and_status(client):
    """Verify the health endpoint returns the correct production-grade JSON schema."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    
    data = response.json()
    
    # Regression protection: Check schema keys
    expected_keys = {
        "status", "message", "version", "uptime", 
        "database", "ollama", "gemma", "whisper", 
        "ffmpeg", "queue", "timestamp",
        "schema_version", "expected_version", "migration_pending"
    }
    assert set(data.keys()) == expected_keys
    assert data["status"] in ["ok", "degraded", "error"]

def test_projects_create_schema_and_error(client):
    """Verify that project creation enforces the input schema and currently returns 501."""
    # Valid schema payload, expecting 201
    import uuid
    response = client.post("/api/v1/projects/", json={"name": f"New Project {uuid.uuid4()}"})
    assert response.status_code == 201
    
    # Invalid schema payload, expecting 422 Unprocessable Entity
    response_invalid = client.post("/api/v1/projects/", json={"wrong_field": "value"})
    assert response_invalid.status_code == 422
    
    data = response_invalid.json()
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"

@pytest.mark.asyncio
async def test_videos_analyze_mock_success(client):
    """Verify that video analysis accepts valid parameters and returns a 202 JobAcceptedResponse."""
    # Pre-seed the database using an explicitly scoped async session
    async with AsyncSessionLocal() as session:
        project_repo = ProjectRepository(session)
        video_repo = VideoRepository(session)

        project = Project(name="Test Project", storage_path="/tmp")
        video = VideoAsset(project_id=project.id, file_path="/tmp/video.mp4")

        await project_repo.create(project)
        await video_repo.save_video(video)

    video_id = str(video.id)
    payload = {
        "pipeline_profile": "fast_audio_only",
        "target_length_seconds": 60
    }
    
    response = client.post(f"/api/v1/videos/{video_id}/analyze", json=payload)
    
    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
    assert "message" in data
    assert "Mock AI Pipeline started" in data["message"]

def test_videos_analyze_validation_error(client):
    """Verify that video analysis enforces bounds (e.g. target_length_seconds >= 15)."""
    video_id = str(uuid.uuid4())
    payload = {
        "pipeline_profile": "fast_audio_only",
        "target_length_seconds": 5  # Too low
    }
    response = client.post(f"/api/v1/videos/{video_id}/analyze", json=payload)
    
    assert response.status_code == 422
    assert response.headers["content-type"] == "application/json"

def test_clips_get_not_implemented(client):
    """Verify that the clips endpoint exists but returns 501."""
    clip_id = str(uuid.uuid4())
    response = client.get(f"/api/v1/clips/{clip_id}")
    assert response.status_code == 501
    assert response.json()["detail"] == "Not implemented yet"
