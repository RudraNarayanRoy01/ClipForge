import pytest
import uuid
import asyncio
from src.domain.entities import Project, VideoAsset
from src.domain.ports import IProjectRepository, IVideoRepository

def test_videos_analyze_mock_success(client):
    """Verify that video analysis accepts valid parameters and returns a 202 JobAcceptedResponse."""
    container = client.app.state.container
    project_repo = container.resolve(IProjectRepository)
    video_repo = container.resolve(IVideoRepository)

    project = Project(name="Test Project", storage_path="/tmp")
    video = VideoAsset(project_id=project.id, file_path="/tmp/video.mp4")

    async def setup_db():
        await project_repo.create(project) # wait, project_repo has create() and save()
        await video_repo.save_video(video)

    asyncio.run(setup_db())

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
