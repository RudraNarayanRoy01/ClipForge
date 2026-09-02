import pytest
import os
import uuid
import asyncio
from fastapi.testclient import TestClient

from src.repositories.video_repository import VideoRepository
from src.main import app

def create_test_project(client: TestClient) -> str:
    response = client.post("/api/v1/projects/", json={"name": f"Test Project {uuid.uuid4()}"})
    assert response.status_code == 201
    return response.json()["id"]

def test_upload_video_success(client: TestClient, monkeypatch):
    project_id = create_test_project(client)
    
    captured_assets = []
    original_save = VideoRepository.save_video
    
    async def intercept_save(self, video_asset):
        captured_assets.append(video_asset)
        return await original_save(self, video_asset)
        
    monkeypatch.setattr(VideoRepository, "save_video", intercept_save)
    
    files = {"file": ("test.mp4", b"0", "video/mp4")}
    
    storage_path = None
    try:
        response = client.post(f"/api/v1/projects/{project_id}/videos", files=files)
        
        assert response.status_code in (200, 201)
        data = response.json()
        assert "id" in data
        assert data["project_id"] == project_id
        
        # Prove persistence occurred and intercepted
        assert len(captured_assets) == 1
        storage_path = captured_assets[0].storage_path
        
        # Prove physical file actually exists
        assert os.path.exists(storage_path)
        
        # Prove existing read path can recover the asset
        get_resp = client.get(f"/api/v1/projects/{project_id}/videos")
        assert get_resp.status_code == 200
        videos = get_resp.json()
        
        # Could be more than 1 if other tests ran in same project, but we created a new one
        assert len(videos) == 1
        assert videos[0]["id"] == data["id"]
        assert videos[0]["project_id"] == project_id
        
    finally:
        # Test artifact cleanup isolation
        if storage_path and os.path.exists(storage_path):
            os.remove(storage_path)

def test_upload_video_invalid_extension(client: TestClient, monkeypatch):
    project_id = create_test_project(client)
    
    persistence_called = False
    async def mock_save_video(self, video_asset):
        nonlocal persistence_called
        persistence_called = True
        
    monkeypatch.setattr(VideoRepository, "save_video", mock_save_video)
    
    files = {"file": ("test.txt", b"0", "text/plain")}
    response = client.post(f"/api/v1/projects/{project_id}/videos", files=files)
    
    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]
    
    # Prove no VideoAsset persisted because validation precedes it
    assert not persistence_called
    
    # No physical file can be created because file_ext validation occurs before os.makedirs and writing.
    # We verify this by ensuring the specific project directory was never even created for videos.
    # But just in case project_id is shared, we ensure no persistence.
    project_video_dir = os.path.join("backend", "storage", "projects", project_id, "videos")
    # Due to early exit, no file is written in the project_video_dir.
    if os.path.exists(project_video_dir):
        # ensure it's empty
        assert len(os.listdir(project_video_dir)) == 0

def test_upload_video_missing_project(client: TestClient, monkeypatch):
    fake_project_id = str(uuid.uuid4())
    
    persistence_called = False
    async def mock_save_video(self, video_asset):
        nonlocal persistence_called
        persistence_called = True
        
    monkeypatch.setattr(VideoRepository, "save_video", mock_save_video)
    
    files = {"file": ("test.mp4", b"0", "video/mp4")}
    response = client.post(f"/api/v1/projects/{fake_project_id}/videos", files=files)
    
    assert response.status_code == 404
    
    # Prove no persistence reached
    assert not persistence_called
    
    # No physical media artifact created because project validation precedes file writing
    project_video_dir = os.path.join("backend", "storage", "projects", fake_project_id, "videos")
    assert not os.path.exists(project_video_dir)

def test_upload_video_persistence_failure_cleans_up_file(client: TestClient, monkeypatch):
    project_id = create_test_project(client)
    
    captured_paths = []
    
    async def mock_save_video(self, video_asset):
        captured_paths.append(video_asset.storage_path)
        raise Exception("Mock DB Failure")
        
    monkeypatch.setattr(VideoRepository, "save_video", mock_save_video)
    
    files = {"file": ("test.mp4", b"0", "video/mp4")}
    
    with pytest.raises(Exception) as excinfo:
        client.post(f"/api/v1/projects/{project_id}/videos", files=files)
        
    assert "Mock DB Failure" in str(excinfo.value)
    
    assert len(captured_paths) == 1
    storage_path = captured_paths[0]
    
    # Prove atomicity: file was created but then removed by the compensation block
    assert not os.path.exists(storage_path)

def test_upload_video_cleanup_failure_does_not_mask_exception(client: TestClient, monkeypatch):
    project_id = create_test_project(client)
    
    captured_paths = []
    
    async def mock_save_video(self, video_asset):
        captured_paths.append(video_asset.storage_path)
        raise Exception("Original DB Failure")
        
    monkeypatch.setattr(VideoRepository, "save_video", mock_save_video)
    
    original_remove = os.remove
    def mock_remove(path):
        # Only fail our specific captured path to avoid breaking unrelated system cleans
        if captured_paths and path == captured_paths[0]:
            raise Exception("Mock Cleanup Failure")
        return original_remove(path)
        
    monkeypatch.setattr(os, "remove", mock_remove)
    
    files = {"file": ("test.mp4", b"0", "video/mp4")}
    
    storage_path = None
    try:
        with pytest.raises(Exception) as excinfo:
            client.post(f"/api/v1/projects/{project_id}/videos", files=files)
            
        # Prove the original DB exception propagates despite the cleanup failure
        assert "Original DB Failure" in str(excinfo.value)
        assert "Mock Cleanup Failure" not in str(excinfo.value)
        
        assert len(captured_paths) == 1
        storage_path = captured_paths[0]
        
    finally:
        # Restore monkeypatch isn't necessary because pytest does it, but we MUST clean up the orphaned file manually
        monkeypatch.undo()
        if storage_path and os.path.exists(storage_path):
            os.remove(storage_path)
